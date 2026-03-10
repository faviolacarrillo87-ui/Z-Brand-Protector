#!/usr/bin/env python3
"""
Z-BRAND PROTECTOR | ANTI-FAKE (Versión Élite)
Módulo de seguridad para monitorización de marcas/influencers usando Sherlock.
"""

import os
import sys
import json
import csv
import argparse
import logging
import subprocess
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Intentar importar tqdm para barra de progreso (opcional)
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# ----------------------------------------------------------------------
# Configuración global
# ----------------------------------------------------------------------
DEFAULT_CONFIG = {
    'sherlock': {
        'timeout': 1,
        'platforms': None,  # None = todas
        'output_format': 'txt'  # txt, json, csv
    },
    'logging': {
        'level': 'INFO',
        'file': 'auditoria.log'
    },
    'reports_dir': 'reports'
}

def load_config(config_path='config.yaml'):
    """Carga configuración desde archivo YAML o usa valores por defecto."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
            # Mezclar con defaults (simple merge)
            config = DEFAULT_CONFIG.copy()
            if user_config:
                for k, v in user_config.items():
                    if k in config and isinstance(config[k], dict) and isinstance(v, dict):
                        config[k].update(v)
                    else:
                        config[k] = v
            return config
    return DEFAULT_CONFIG.copy()

# ----------------------------------------------------------------------
# Funciones auxiliares
# ----------------------------------------------------------------------
def setup_logging(log_file, log_level=logging.INFO):
    """Configura el sistema de logging."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_sherlock():
    """Verifica que Sherlock esté instalado y accesible."""
    try:
        subprocess.run(['sherlock', '--help'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def sanitize_brand_name(name: str) -> str:
    """Elimina caracteres peligrosos para evitar inyección de comandos."""
    # Permitimos letras, números, guiones y guiones bajos (como en nombres de usuario)
    import re
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name)
    if not sanitized:
        raise ValueError("El nombre de la marca no es válido después de sanitizar.")
    return sanitized

def run_sherlock(brand: str, timeout: int, platforms: Optional[List[str]], output_file: str) -> bool:
    """
    Ejecuta Sherlock para una marca y redirige la salida al archivo indicado.
    Retorna True si tuvo éxito (código de retorno 0), False en caso contrario.
    """
    cmd = ['sherlock', brand, '--timeout', str(timeout), '--output', output_file]
    if platforms:
        cmd.extend(['--site', *platforms])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logging.error(f"Sherlock falló para {brand}. Código: {result.returncode}")
            logging.debug(f"stderr: {result.stderr}")
            return False
        return True
    except Exception as e:
        logging.exception(f"Excepción ejecutando Sherlock para {brand}: {e}")
        return False

def convert_to_json(txt_file: str, json_file: str):
    """Convierte el reporte de texto de Sherlock a JSON (formato simple)."""
    # El reporte de Sherlock tiene líneas como: [+] Usuario encontrado en: Instagram
    # Podemos parsear las plataformas encontradas
    found = []
    if os.path.exists(txt_file):
        with open(txt_file, 'r') as f:
            for line in f:
                if '[+]' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        platform = parts[1].strip()
                        found.append(platform)
    with open(json_file, 'w') as f:
        json.dump({'plataformas_encontradas': found}, f, indent=2)

def convert_to_csv(txt_file: str, csv_file: str):
    """Convierte el reporte a CSV (una plataforma por fila)."""
    found = []
    if os.path.exists(txt_file):
        with open(txt_file, 'r') as f:
            for line in f:
                if '[+]' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        platform = parts[1].strip()
                        found.append([platform])
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Plataforma'])
        writer.writerows([[p] for p in found])

def process_brand(brand: str, config: dict, output_dir: Path, dry_run: bool = False) -> dict:
    """
    Procesa una marca individual: ejecuta Sherlock (si no es dry-run) y genera reportes.
    Retorna un diccionario con estadísticas de esta marca.
    """
    brand_safe = sanitize_brand_name(brand)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{brand_safe}_{timestamp}"
    txt_file = output_dir / f"{base_filename}.txt"
    json_file = output_dir / f"{base_filename}.json"
    csv_file = output_dir / f"{base_filename}.csv"

    logging.info(f"Procesando: {brand} (sanitized: {brand_safe})")

    if dry_run:
        logging.info(f"[DRY RUN] Se ejecutaría: sherlock {brand_safe} --timeout {config['sherlock']['timeout']} --output {txt_file}")
        # Simulamos éxito
        return {
            'marca': brand,
            'estado': 'simulado',
            'archivos': [str(txt_file), str(json_file), str(csv_file)],
            'timestamp': timestamp
        }

    # Ejecutar Sherlock
    success = run_sherlock(
        brand_safe,
        config['sherlock']['timeout'],
        config['sherlock']['platforms'],
        str(txt_file)
    )

    if not success:
        logging.error(f"Error procesando {brand}. No se generaron reportes.")
        return {
            'marca': brand,
            'estado': 'error',
            'archivos': [],
            'timestamp': timestamp
        }

    # Convertir a otros formatos si se solicita
    if config['sherlock']['output_format'] in ('json', 'all') and os.path.exists(txt_file):
        convert_to_json(txt_file, json_file)
        logging.info(f"JSON generado: {json_file}")
    if config['sherlock']['output_format'] in ('csv', 'all') and os.path.exists(txt_file):
        convert_to_csv(txt_file, csv_file)
        logging.info(f"CSV generado: {csv_file}")

    return {
        'marca': brand,
        'estado': 'éxito',
        'archivos': [str(txt_file)] + ([str(json_file)] if config['sherlock']['output_format'] in ('json', 'all') else []) + ([str(csv_file)] if config['sherlock']['output_format'] in ('csv', 'all') else []),
        'timestamp': timestamp
    }

# ----------------------------------------------------------------------
# Función principal
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Z-BRAND PROTECTOR | Anti-Fake (Sherlock wrapper profesional)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Ejemplos:\n  python brand_protector.py "ElonMusk"\n  python brand_protector.py --file marcas.txt --output-dir ./resultados --format json\n  python brand_protector.py --dry-run "Nike""
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('marca', nargs='?', help='Nombre de la marca/influencer a analizar')
    group.add_argument('-f', '--file', help='Archivo con lista de marcas (una por línea)')

    parser.add_argument('-o', '--output-dir', default='reports', help='Directorio donde guardar los reportes (default: reports)')
    parser.add_argument('--format', choices=['txt', 'json', 'csv', 'all'], default='txt', help='Formato de salida (default: txt)')
    parser.add_argument('--timeout', type=int, help='Timeout en segundos para Sherlock (default: de config)')
    parser.add_argument('--platforms', nargs='+', help='Plataformas específicas a escanear (ej. instagram twitter)')
    parser.add_argument('--dry-run', action='store_true', help='Simular ejecución sin llamar a Sherlock')
    parser.add_argument('-v', '--verbose', action='store_true', help='Activar modo verbose (logging DEBUG)')
    parser.add_argument('--config', default='config.yaml', help='Archivo de configuración YAML (default: config.yaml)')
    parser.add_argument('--log-file', default='auditoria.log', help='Archivo de log (default: auditoria.log)')

    args = parser.parse_args()

    # Cargar configuración
    config = load_config(args.config)
    # Sobrescribir con argumentos de línea de comandos
    if args.timeout:
        config['sherlock']['timeout'] = args.timeout
    if args.platforms:
        config['sherlock']['platforms'] = args.platforms
    if args.format:
        config['sherlock']['output_format'] = args.format
    if args.output_dir:
        config['reports_dir'] = args.output_dir

    # Configurar logging
    log_level = logging.DEBUG if args.verbose else getattr(logging, config['logging']['level'].upper(), logging.INFO)
    setup_logging(args.log_file, log_level)

    # Verificar Sherlock instalado (a menos que sea dry-run)
    if not args.dry_run and not check_sherlock():
        logging.error("Sherlock no está instalado o no está en el PATH.")
        print("\n[!] Sherlock no encontrado. Por favor, instálalo desde:")
        print("    https://github.com/sherlock-project/sherlock")
        print("    O usa 'pip install sherlock' (si está disponible).")
        sys.exit(1)

    # Crear directorio de reportes
    output_dir = Path(config['reports_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)

    # Obtener lista de marcas a procesar
    marcas = []
    if args.marca:
        marcas = [args.marca]
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                marcas = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logging.error(f"No se pudo leer el archivo {args.file}: {e}")
            sys.exit(1)

    if not marcas:
        logging.error("No se proporcionaron marcas para analizar.")
        sys.exit(1)

    logging.info(f"Iniciando procesamiento de {len(marcas)} marca(s). Modo dry-run: {args.dry_run}")

    # Procesar cada marca
    resultados = []
    iterator = tqdm(marcas, desc="Procesando") if TQDM_AVAILABLE else marcas
    for marca in iterator:
        try:
            res = process_brand(marca, config, output_dir, args.dry_run)
            resultados.append(res)
        except ValueError as e:
            logging.error(f"Error con la marca '{marca}': {e}")
        except Exception as e:
            logging.exception(f"Error inesperado con '{marca}': {e}")

    # Generar reporte global
    resumen = {
        'fecha': datetime.now().isoformat(),
        'total_marcas': len(marcas),
        'procesadas': len(resultados),
        'exitosas': sum(1 for r in resultados if r['estado'] == 'éxito'),
        'simuladas': sum(1 for r in resultados if r['estado'] == 'simulado'),
        'errores': sum(1 for r in resultados if r['estado'] == 'error'),
        'detalles': resultados
    }

    resumen_file = output_dir / f"resumen_global_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(resumen_file, 'w') as f:
        json.dump(resumen, f, indent=2)

    logging.info(f"Proceso completado. Resumen guardado en {resumen_file}")
    print(f"\n[OK] Todos los reportes se encuentran en: {output_dir}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupción por usuario. Saliendo...")
        sys.exit(0)
