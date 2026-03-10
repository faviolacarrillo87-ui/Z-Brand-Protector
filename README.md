# 🛡️ Z-BRAND PROTECTOR | Enterprise Identity Security

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Sherlock](https://img.shields.io/badge/sherlock-integrated-brightgreen)](https://github.com/sherlock-project/sherlock)
[![Holehe](https://img.shields.io/badge/holehe-integrated-blue)](https://github.com/megadose/holehe)

**Z-BRAND PROTECTOR** es un framework avanzado de monitorización y auditoría de identidad digital, diseñado para la protección proactiva de marcas, figuras públicas e influencers. Unifica las herramientas más potentes del ecosistema OSINT en una sola interfaz de línea de comandos, generando reportes estructurados para la toma de decisiones y la trazabilidad forense.

---

## 📑 Tabla de Contenidos

- [🚀 Capacidades Operativas (Motores Integrados)](#-capacidades-operativas-motores-integrados)
- [📊 Salida de Datos y Reportes](#-salida-de-datos-y-reportes)
- [⚙️ Instalación](#️-instalación)
  - [Requisitos Previos](#requisitos-previos)
  - [Instalación Rápida](#instalación-rápida)
  - [Configuración](#configuración)
- [🖥️ Uso](#️-uso)
  - [Sintaxis Básica](#sintaxis-básica)
  - [Ejemplos Prácticos](#ejemplos-prácticos)
  - [Modo Simulación (Dry Run)](#modo-simulación-dry-run)
  - [Procesamiento por Lotes](#procesamiento-por-lotes)
- [📂 Estructura de Salida](#-estructura-de-salida)
- [🧪 Ejemplo de Reporte JSON](#-ejemplo-de-reporte-json)
- [🛠️ Personalización](#️-personalización)
- [🤝 Contribuciones](#-contribuciones)
- [📄 Licencia](#-licencia)
- [📬 Contacto](#-contacto)

---

## 🚀 Capacidades Operativas (Motores Integrados)

Este framework integra tres motores OSINT de referencia, permitiendo ejecutar múltiples técnicas de reconocimiento con un solo comando:

| Motor | Función |
|-------|---------|
| **🔍 Sherlock Engine** | Rastreo masivo de nombres de usuario en más de 350 plataformas sociales (Instagram, Twitter, TikTok, GitHub, etc.) para detectar suplantaciones o perfiles no autorizados. |
| **🌐 WhatsMyName Deep Scan** | Búsqueda profunda de nicks y alias en registros globales de la web, ampliando el alcance más allá de las redes sociales principales. |
| **📧 Holehe Email Intelligence** | Verificación de brechas de seguridad y existencia de cuentas vinculadas a correos electrónicos corporativos o personales. Ideal para auditar la exposición de un email. |

---

## 📊 Salida de Datos y Reportes

El sistema no solo ejecuta búsquedas, sino que organiza la inteligencia obtenida para facilitar su análisis y posterior uso:

- **📄 JSON Manifest:** Generación automática de reportes estructurados en formato JSON, listos para integrarse con bases de datos, herramientas de visualización o pipelines de datos.
- **📈 CSV Export:** Opción de exportar los resultados a CSV para su análisis en hojas de cálculo.
- **📝 Logging Auditor:** Registro detallado de cada operación en `brand_protector.log`, incluyendo marcas procesadas, errores, tiempos y resultados. Fundamental para trazabilidad forense y auditorías de cumplimiento.
- **📁 Directorio Organizado:** Todos los reportes se guardan en una carpeta `reports/` (personalizable), con nombres que incluyen timestamp para evitar colisiones.

---

## ⚙️ Instalación

### Requisitos Previos

- **Python 3.8 o superior**
- **pip** (gestor de paquetes de Python)
- **Git** (para clonar repositorios)
- **Sherlock, Holehe y WhatsMyName** (se instalan automáticamente con las instrucciones siguientes)

### Instalación Rápida

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tuusuario/z-brand-protector.git
   cd z-brand-protector
