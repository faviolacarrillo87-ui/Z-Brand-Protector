#!/usr/bin/env python3
import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Configuración de Logging Profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('brand_protector.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

BANNER = """
╔══════════════════════════════════════════════════════════╗
║         Z-BRAND PROTECTOR | ANTI-FAKE (Final)           ║
║              Identity Security Solutions                 ║
╚══════════════════════════════════════════════════════════╝
"""

class BrandMonitor:
    def __init__(self, brand_name: str, dry_run: bool = False):
        self.brand_name = brand_name
        self.dry_run = dry_run
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)
        self.results = {}

    def run_sherlock(self):
        """Ejecuta Sherlock para búsqueda de perfiles."""
        output_file = self.output_dir / f"sherlock_{self.brand_name}.txt"
        cmd = f"sherlock {self.brand_name} --timeout 1 --output {output_file}"
        if not self.dry_run:
            logger.info(f"Lanzando Sherlock para: {self.brand_name}")
            os.system(cmd)
            self.results['sherlock'] = str(output_file)

    def run_whatsmyname(self):
        """Ejecuta WhatsMyName para rastreo profundo."""
        output_file = self.output_dir / f"wmn_{self.brand_name}.txt"
        cmd = f"whatsmyname -u {self.brand_name} > {output_file}"
        if not self.dry_run:
            logger.info(f"Lanzando WhatsMyName para: {self.brand_name}")
            os.system(cmd)
            self.results['whatsmyname'] = str(output_file)

    def run_holehe(self):
        """Verifica correos electrónicos asociados."""
        email = f"{self.brand_name}@gmail.com"
        cmd = f"holehe {email} --only-used"
        if not self.dry_run:
            logger.info(f"Lanzando Holehe para: {email}")
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            self.results['holehe'] = res.stdout

    def export_json(self):
        """Genera el manifiesto final en JSON."""
        report_path = self.output_dir / f"final_report_{self.brand_name}.json"
        with open(report_path, 'w') as f:
            json.dump({
                "brand": self.brand_name,
                "timestamp": self.timestamp,
                "findings": self.results
            }, f, indent=4)
        logger.info(f"Manifiesto JSON generado en: {report_path}")

    def execute_all(self):
        print(BANNER)
        self.run_sherlock()
        self.run_whatsmyname()
        self.run_holehe()
        self.export_json()
        print(f"\n[OK] Auditoría completada para {self.brand_name}")

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else input("[?] Marca a monitorear: ")
    monitor = BrandMonitor(name)
    monitor.execute_all()

