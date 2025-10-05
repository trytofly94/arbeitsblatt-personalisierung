# Projekt-Konfiguration für Arbeitsblatt-Personalisierung

## 1. Projektbeschreibung

Ein CLI-Tool zur automatischen Personalisierung von Arbeitsblättern (PDF oder Bilder) durch Hinzufügen von Schülerfotos und optional deren Namen. Das Tool ermöglicht es Lehrern, schnell und effizient personalisierte Arbeitsblätter für eine ganze Klasse zu erstellen.

### Hauptfunktionen
- Verarbeitung von Arbeitsblättern im PDF- oder Bildformat (PNG, JPG)
- Einfügen von Schülerfotos in der oberen rechten Ecke (1,5 cm Größe)
- Optional: Hinzufügen des Schülernamens
- Batch-Verarbeitung für gesamte Klassenordner
- Ausgabe personalisierter Arbeitsblätter pro Schüler

## 2. Technologie-Stack

### Sprache & Runtime
- **Python**: 3.9+
- **Paketmanager**: pip (mit pyproject.toml für moderne Paketverwaltung)

### Kern-Abhängigkeiten

#### PDF-Verarbeitung
- **PyPDF2** (4.0+): PDF-Manipulation und -Zusammenführung
- **reportlab** (4.0+): PDF-Generierung für Overlays
- **pdf2image** (1.16+): Konvertierung PDF → Bild (falls nötig)

#### Bild-Verarbeitung
- **Pillow** (PIL) (10.0+): Bildmanipulation, Größenanpassung, Compositing

#### CLI & Utilities
- **click** (8.1+): Moderne, benutzerfreundliche CLI-Entwicklung
- **rich** (13.0+): Schöne Terminal-Ausgaben und Progress-Bars
- **pydantic** (2.0+): Datenvalidierung und Settings-Management

#### Testing & Qualität
- **pytest** (7.4+): Test-Framework
- **pytest-cov** (4.1+): Code-Coverage
- **black** (23.0+): Code-Formatter
- **ruff** (0.1+): Schneller Linter (ersetzt flake8, isort, etc.)
- **mypy** (1.5+): Type-Checking

#### Build & Distribution
- **build** (1.0+): PEP 517 kompatibles Build-Tool
- **wheel**: Wheel-Distribution

## 3. Projektstruktur

```
arbeitsblatt-personalisierung/
├── src/
│   └── worksheet_personalizer/
│       ├── __init__.py
│       ├── __main__.py              # Entry point für python -m worksheet_personalizer
│       ├── cli.py                   # Click CLI-Definitionen
│       ├── config.py                # Pydantic Settings & Konfiguration
│       ├── core/
│       │   ├── __init__.py
│       │   ├── pdf_processor.py    # PDF-spezifische Logik
│       │   ├── image_processor.py  # Bild-spezifische Logik
│       │   └── personalizer.py     # Haupt-Personalisierungs-Engine
│       ├── models/
│       │   ├── __init__.py
│       │   └── student.py          # Pydantic-Modelle für Schülerdaten
│       └── utils/
│           ├── __init__.py
│           ├── file_handler.py     # Datei-I/O-Helpers
│           └── image_utils.py      # Bild-Transformationen
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest-Fixtures
│   ├── test_pdf_processor.py
│   ├── test_image_processor.py
│   ├── test_personalizer.py
│   ├── test_cli.py
│   └── fixtures/                   # Test-Daten (Beispiel-PDFs, Bilder)
│       ├── sample_worksheet.pdf
│       ├── sample_worksheet.png
│       └── students/
│           ├── max_mustermann.jpg
│           └── anna_schmidt.jpg
├── docs/
│   ├── usage.md                    # Nutzungsanleitung
│   └── examples.md                 # Beispiele
├── scripts/
│   └── setup_dev.sh                # Entwicklungsumgebung einrichten
├── pyproject.toml                  # Projekt-Metadaten & Dependencies
├── README.md
├── .gitignore
├── .python-version                 # pyenv-Kompatibilität
└── CLAUDE.md                       # Diese Datei

```

## 4. Wichtige Befehle

### Entwicklungsumgebung einrichten

```bash
# Virtuelle Umgebung erstellen
python -m venv venv

# Aktivieren (Linux/macOS)
source venv/bin/activate

# Aktivieren (Windows)
venv\Scripts\activate

# Dependencies installieren (Development-Mode)
pip install -e ".[dev]"
```

### Anwendung ausführen

```bash
# Als Modul (empfohlen)
python -m worksheet_personalizer --help

# Nach Installation
worksheet-personalizer --help

# Beispiel-Aufruf
python -m worksheet_personalizer \
  --worksheet arbeitsblatt.pdf \
  --students-folder ./schueler/ \
  --output-folder ./personalisiert/ \
  --add-name
```

### Tests & Qualitätssicherung

```bash
# Alle Tests ausführen
pytest

# Mit Coverage-Report
pytest --cov=worksheet_personalizer --cov-report=html

# Nur spezifische Tests
pytest tests/test_pdf_processor.py

# Tests mit Ausgabe
pytest -v -s

# Code formatieren (automatisch)
black src/ tests/

# Linting
ruff check src/ tests/

# Linting mit Auto-Fix
ruff check --fix src/ tests/

# Type-Checking
mypy src/
```

### Build & Distribution

```bash
# Paket bauen
python -m build

# Lokal installieren
pip install dist/worksheet_personalizer-*.whl

# Entwicklungs-Installation (editierbar)
pip install -e .
```

## 5. Architektur-Übersicht

### Kern-Komponenten

#### 1. CLI Layer (`cli.py`)
- Click-basierte Kommandozeilen-Schnittstelle
- Argument-Parsing und Validierung
- Rich-basierte Progress-Anzeige

#### 2. Processing Layer (`core/`)
- **PDFProcessor**: Handhabt PDF-spezifische Operationen
  - PDF laden und analysieren
  - Overlays mit reportlab erstellen
  - PDFs zusammenführen
- **ImageProcessor**: Handhabt Bild-Operationen
  - Bilder laden (PNG, JPG, etc.)
  - Schülerfotos verarbeiten und skalieren
  - Composite-Operationen
- **Personalizer**: Orchestriert den Gesamtprozess
  - Erkennt Eingabeformat (PDF vs. Bild)
  - Delegiert an entsprechenden Processor
  - Batch-Verarbeitung

#### 3. Data Layer (`models/`)
- Pydantic-Modelle für Typsicherheit
- Datenvalidierung
- Settings-Management

#### 4. Utilities (`utils/`)
- Wiederverwendbare Helper-Funktionen
- Datei-I/O-Abstraktionen
- Bild-Transformationen (Resize, Crop, etc.)

### Datenfluss

```
1. CLI Input (Arbeitsblatt + Schüler-Ordner)
   ↓
2. Personalizer erkennt Format
   ↓
3a. PDFProcessor              3b. ImageProcessor
    - PDF laden                   - Bild laden
    - Overlay erstellen           - Foto einfügen
    - Zusammenführen              - Speichern
   ↓
4. Ausgabe (personalisierte Dateien)
```

## 6. Coding-Standards & Konventionen

### Code-Stil
- **Formatter**: Black (Line length: 88)
- **Linter**: Ruff (mit allen empfohlenen Regeln)
- **Type Hints**: Vollständig für alle öffentlichen Funktionen
- **Docstrings**: Google-Style für Klassen und öffentliche Methoden

### Namenskonventionen
- **Dateien/Module**: snake_case (z.B. `pdf_processor.py`)
- **Klassen**: PascalCase (z.B. `PDFProcessor`)
- **Funktionen/Variablen**: snake_case (z.B. `process_worksheet`)
- **Konstanten**: UPPER_SNAKE_CASE (z.B. `DEFAULT_PHOTO_SIZE`)

### Testing
- Mindestens 80% Code-Coverage
- Unit-Tests für alle Core-Komponenten
- Integration-Tests für CLI
- Fixture-basierte Tests mit pytest

### Git-Workflow
- Feature-Branches: `feature/beschreibung`
- Bugfix-Branches: `fix/beschreibung`
- Commit-Messages: Conventional Commits Format
  - `feat: neue Funktion`
  - `fix: Bugfix`
  - `docs: Dokumentation`
  - `test: Tests`
  - `refactor: Code-Refactoring`

## 7. Konfiguration

### Umgebungsvariablen
```bash
# Optional: Standard-Ausgabe-Ordner
WORKSHEET_OUTPUT_DIR=./output

# Optional: Standard-Fotogröße in cm
WORKSHEET_PHOTO_SIZE=1.5

# Optional: Log-Level
LOG_LEVEL=INFO
```

### Config-Datei (Optional)
Unterstützung für `config.yaml` im Projekt-Root:
```yaml
photo_size_cm: 1.5
photo_position: top-right
add_name_default: false
output_format: pdf
```

## 8. Hinweise für die Agenten

### Für den Planner
- Berücksichtige die modulare Architektur (PDF vs. Image Processing getrennt)
- Plane Tests parallel zur Implementierung
- Beachte die Abhängigkeiten zwischen Komponenten

### Für den Creator
- **Wichtig**: Vollständige Type-Hints verwenden
- Black und Ruff vor jedem Commit ausführen
- Pydantic-Modelle für alle Datenstrukturen nutzen
- Logging mit Python's `logging`-Modul (nicht print)
- Fehlerbehandlung: Spezifische Exceptions, keine generischen `except`-Blöcke

### Für den Tester
- Test-Framework: **pytest**
- Test-Befehl: `pytest --cov=worksheet_personalizer`
- Fixtures für Test-Daten unter `tests/fixtures/` verwenden
- Mocken externer Dependencies (z.B. Dateisystem mit `tmp_path`)
- Coverage-Ziel: Minimum 80%

### Für den Deployer
- Vor PR-Erstellung: Alle Tests müssen grün sein
- Dokumentation aktualisieren (README.md, docs/)
- CHANGELOG.md pflegen
- Version in `pyproject.toml` erhöhen (SemVer)

## 9. Bekannte Limitierungen & Zukünftige Erweiterungen

### Aktuelle Limitierungen
- Nur einzelne Arbeitsblatt-Datei pro Durchlauf
- Fotogröße und -position sind fix (1,5 cm, oben rechts)

### Geplante Features
- [ ] Konfigurierbare Foto-Position und -Größe
- [ ] Unterstützung für mehrere Arbeitsblätter gleichzeitig
- [ ] GUI-Version für nicht-technische Nutzer
- [ ] CSV-Import für Schülerdaten (Name, Foto-Pfad, etc.)
- [ ] Template-System für verschiedene Arbeitsblatt-Layouts
- [ ] OCR-Integration für automatische Namens-Platzierung

## 10. Troubleshooting

### Häufige Probleme

#### PDF-Generierung schlägt fehl
- Prüfe, ob `reportlab` korrekt installiert ist
- Stelle sicher, dass das Eingabe-PDF nicht korrupt ist

#### Bilder werden nicht korrekt skaliert
- Überprüfe DPI-Einstellungen (Standard: 300 DPI)
- Verifiziere Eingabeformat der Schülerfotos

#### Tests schlagen fehl
- Stelle sicher, dass Test-Fixtures vorhanden sind
- Prüfe virtuelle Umgebung und Dependencies

### Logs & Debugging
- Log-Dateien: `~/.worksheet_personalizer/logs/`
- Debug-Modus: `--verbose` Flag bei CLI
- Ausführliche Logs: `LOG_LEVEL=DEBUG python -m worksheet_personalizer ...`
