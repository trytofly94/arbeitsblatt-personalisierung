# Arbeitsblatt-Personalisierung

Ein CLI-Tool zur automatischen Personalisierung von Arbeitsblättern durch Hinzufügen von Schülerfotos und Namen.

## Übersicht

Dieses Tool ermöglicht es Lehrern, schnell und effizient personalisierte Arbeitsblätter für eine ganze Klasse zu erstellen. Es fügt automatisch Schülerfotos in der oberen rechten Ecke ein und kann optional den Namen des Schülers hinzufügen.

### Features

- **Flexibles Eingabeformat**: Unterstützt PDF und Bildformate (PNG, JPG)
- **Batch-Verarbeitung**: Verarbeitet alle Schüler in einem Ordner automatisch
- **Anpassbare Ausgabe**: Optionales Hinzufügen von Schülernamen
- **Hochwertige Ausgabe**: Behält Qualität und Layout des Original-Arbeitsblatts bei
- **Einfache Bedienung**: Intuitive Kommandozeilen-Schnittstelle

## Voraussetzungen

- **Python** 3.9 oder höher
- **pip** (Python-Paketmanager)

### System-Abhängigkeiten

Für PDF-zu-Bild-Konvertierung (optional):
- **Linux**: `sudo apt-get install poppler-utils`
- **macOS**: `brew install poppler`
- **Windows**: [Poppler für Windows herunterladen](http://blog.alivate.com.au/poppler-windows/)

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/IhrBenutzername/arbeitsblatt-personalisierung.git
cd arbeitsblatt-personalisierung
```

### 2. Virtuelle Umgebung erstellen und aktivieren

```bash
# Virtuelle Umgebung erstellen
python -m venv venv

# Aktivieren (Linux/macOS)
source venv/bin/activate

# Aktivieren (Windows)
venv\Scripts\activate
```

### 3. Dependencies installieren

```bash
# Für normale Nutzung
pip install -e .

# Für Entwicklung (inkl. Test-Tools)
pip install -e ".[dev]"
```

## Nutzung

### Grundlegende Verwendung

```bash
python -m worksheet_personalizer \
  --worksheet pfad/zum/arbeitsblatt.pdf \
  --students-folder pfad/zu/schuelerfotos/ \
  --output-folder ./personalisiert/
```

### Mit Schülernamen

```bash
python -m worksheet_personalizer \
  --worksheet arbeitsblatt.pdf \
  --students-folder ./schueler/ \
  --output-folder ./ausgabe/ \
  --add-name
```

### Alle verfügbaren Optionen anzeigen

```bash
python -m worksheet_personalizer --help
```

## Ordnerstruktur für Schülerfotos

Die Schülerfotos sollten wie folgt organisiert sein:

```
schueler/
├── max_mustermann.jpg
├── anna_schmidt.png
├── tom_mueller.jpg
└── ...
```

**Hinweis**: Der Dateiname (ohne Erweiterung) wird als Schülername verwendet, wenn `--add-name` aktiviert ist.

## Beispiel-Workflow

1. **Arbeitsblatt vorbereiten**: Ihr normales Arbeitsblatt als PDF oder Bild
2. **Schülerfotos sammeln**: Alle Fotos in einem Ordner (JPG oder PNG empfohlen)
3. **Tool ausführen**:
   ```bash
   python -m worksheet_personalizer \
     --worksheet mathe_uebung.pdf \
     --students-folder ./klasse_7a/ \
     --output-folder ./ausgabe/ \
     --add-name
   ```
4. **Ergebnis**: Im Ausgabe-Ordner findet sich für jeden Schüler ein personalisiertes Arbeitsblatt

## Konfiguration

### Umgebungsvariablen (Optional)

```bash
# Standard-Ausgabe-Ordner
export WORKSHEET_OUTPUT_DIR=./output

# Standard-Fotogröße in cm
export WORKSHEET_PHOTO_SIZE=1.5

# Log-Level
export LOG_LEVEL=INFO
```

### Config-Datei (Optional)

Erstellen Sie eine `config.yaml` im Projekt-Verzeichnis:

```yaml
photo_size_cm: 1.5
photo_position: top-right
add_name_default: false
output_format: pdf
```

## Entwicklung

### Tests ausführen

```bash
# Alle Tests
pytest

# Mit Coverage-Report
pytest --cov=worksheet_personalizer --cov-report=html

# Nur spezifische Tests
pytest tests/test_pdf_processor.py -v
```

### Code-Qualität prüfen

```bash
# Code formatieren
black src/ tests/

# Linting
ruff check src/ tests/

# Type-Checking
mypy src/
```

### Build erstellen

```bash
python -m build
```

## Projektstruktur

```
arbeitsblatt-personalisierung/
├── src/worksheet_personalizer/  # Hauptcode
│   ├── cli.py                   # CLI-Interface
│   ├── core/                    # Kern-Logik
│   ├── models/                  # Datenmodelle
│   └── utils/                   # Hilfsfunktionen
├── tests/                       # Tests
├── docs/                        # Dokumentation
├── pyproject.toml              # Projekt-Konfiguration
└── README.md                   # Diese Datei
```

## Troubleshooting

### Problem: PDF-Generierung schlägt fehl

**Lösung**: Stellen Sie sicher, dass `reportlab` korrekt installiert ist:
```bash
pip install --upgrade reportlab
```

### Problem: Bilder werden nicht korrekt skaliert

**Lösung**: Überprüfen Sie, dass die Eingabebilder eine ausreichende Auflösung haben (mindestens 300 DPI empfohlen)

### Problem: "Module not found" Fehler

**Lösung**: Aktivieren Sie die virtuelle Umgebung und installieren Sie die Dependencies erneut:
```bash
source venv/bin/activate  # oder venv\Scripts\activate auf Windows
pip install -e .
```

## Unterstützung

- **Dokumentation**: Siehe `docs/` Ordner
- **Issues**: [GitHub Issues](https://github.com/IhrBenutzername/arbeitsblatt-personalisierung/issues)
- **Beitragen**: Pull Requests sind willkommen!

## Lizenz

[Bitte Lizenz hinzufügen]

## Autoren

- [Ihr Name]

## Danksagungen

- Entwickelt mit Python, PyPDF2, Pillow und Click
- Inspiriert durch die Bedürfnisse von Lehrern für personalisierte Lernmaterialien
