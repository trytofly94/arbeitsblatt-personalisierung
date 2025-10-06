# Arbeitsblatt-Personalisierung 📚✨

Ein benutzerfreundliches Tool zur automatischen Personalisierung von Arbeitsblättern durch Hinzufügen von Schülerfotos und Namen - **ohne Kommandozeile!**

## 🎯 Übersicht

Dieses Tool ermöglicht es Lehrern, schnell und effizient personalisierte Arbeitsblätter für bis zu drei Klassen zu erstellen. Es fügt automatisch Schülerfotos ein und kann optional den Namen des Schülers hinzufügen.

### ✨ Features

- **🖱️ Ein-Klick-Bedienung**: Keine Kommandozeilen-Kenntnisse nötig
- **👥 Multi-Klassen**: Unterstützt 3 Klassengruppen gleichzeitig (A, B, C)
- **📄 Flexibles Format**: Unterstützt PDF und Bildformate (PNG, JPG)
- **⚙️ Anpassbar**: Fotogröße und Name-Anzeige einfach konfigurierbar
- **🎨 Professionell**: Norddruck-Schrift und dynamische Größenanpassung
- **📏 Intelligent**: Automatische Skalierung für jede PDF-Größe
- **🔄 Auto-Update**: Einfaches Update-System
- **💾 Datenschutz**: Schülerfotos bleiben beim Update erhalten
- **🇩🇪 Auf Deutsch**: Alle Meldungen in deutscher Sprache

## 🚀 Schnellstart (macOS)

### 1️⃣ Projekt herunterladen

```bash
git clone https://github.com/trytofly94/arbeitsblatt-personalisierung.git
cd arbeitsblatt-personalisierung
```

### 2️⃣ Ersteinrichtung (einmalig)

**Doppelklick auf:** `Ersteinrichtung.command`

Das war's! Die Installation läuft automatisch.

### 3️⃣ Arbeitsblätter personalisieren

1. **Schülerfotos** in `Schüler-A/` (oder B, C) legen
   - Dateiname = Name des Schülers (z.B. `Max_Mustermann.jpg`)

2. **PDF-Arbeitsblatt** in `Input-A/` (oder B, C) legen

3. **Doppelklick auf:** `Start.command`

4. **Fertig!** → Personalisierte Arbeitsblätter finden Sie in `Ausgabe-A/`

### 4️⃣ Einstellungen ändern (optional)

**Doppelklick auf:** `Einstellungen.command`

Hier können Sie anpassen:
- 📏 **Fotogröße** (Standard: 2.5 cm)
  - Wählen Sie aus 6 vordefinierten Größen (1.5 - 4.0 cm)
  - Oder geben Sie eine eigene Größe ein
- ✏️ **Name hinzufügen** (Ja/Nein)
  - Format: "Name: Max Mustermann" neben dem Foto
  - Verwendet Norddruck-Schrift für einheitliches Aussehen

**Automatische Anpassungen:**
- 🔤 Schriftgröße passt sich dynamisch an PDF-Größe an (2.25% der Höhe)
- 📐 Abstände und Ränder skalieren automatisch mit dem Arbeitsblatt
- 📝 Name erscheint immer links vom Foto in optimaler Position

### 5️⃣ Programm aktualisieren

**Doppelklick auf:** `Update.command`

Ihre Schülerfotos und Einstellungen bleiben dabei erhalten!

## 📁 Ordnerstruktur

```
arbeitsblatt-personalisierung/
├── 🛠️ Maschinenraum/              # Technische Dateien (nicht anfassen)
│   ├── src/                       # Python-Code
│   ├── fonts/NORDDRUC.TTF         # Norddruck-Schriftart
│   └── settings.json              # Einstellungen (automatisch verwaltet)
├── 👥 Schüler-A/                   # Fotos Klasse A
├── 👥 Schüler-B/                   # Fotos Klasse B
├── 👥 Schüler-C/                   # Fotos Klasse C
├── 📥 Input-A/                     # PDFs für Klasse A
├── 📥 Input-B/                     # PDFs für Klasse B
├── 📥 Input-C/                     # PDFs für Klasse C
├── 📤 Ausgabe-A/                   # Fertige Arbeitsblätter A
├── 📤 Ausgabe-B/                   # Fertige Arbeitsblätter B
├── 📤 Ausgabe-C/                   # Fertige Arbeitsblätter C
├── ▶️ Start.command                # HIER KLICKEN zum Starten
├── ⚙️ Einstellungen.command        # Einstellungen ändern
├── 🔄 Update.command               # Programm aktualisieren
└── 🏁 Ersteinrichtung.command      # Ersteinrichtung (einmalig)
```

## 💡 Tipps

### Schülerfotos vorbereiten

- **Format**: JPG, JPEG, PNG
- **Benennung**: `Vorname_Nachname.jpg` oder `Vorname Nachname.jpg`
- **Qualität**: Mindestens 300x400 Pixel empfohlen
- **Hintergrund**: Am besten einfarbig oder neutral

### Mehrere Klassen verwalten

Sie können bis zu 3 Klassen gleichzeitig verwalten:
- **Klasse A**: `Schüler-A/` + `Input-A/` → `Ausgabe-A/`
- **Klasse B**: `Schüler-B/` + `Input-B/` → `Ausgabe-B/`
- **Klasse C**: `Schüler-C/` + `Input-C/` → `Ausgabe-C/`

### Was passiert beim Start?

1. Alle PDFs aus `Input-A/B/C` werden verarbeitet
2. Für jeden Schüler wird ein personalisiertes Arbeitsblatt erstellt
   - **Foto**: Erscheint oben rechts in der gewählten Größe
   - **Name**: Optional "Name: Vorname Nachname" links vom Foto
   - **Schrift**: Norddruck-Schriftart, automatisch skaliert
3. Original-PDF wird nach `Ausgabe-X/Arbeitsblattname/` verschoben
4. Alle personalisierten PDFs landen im gleichen Ordner
5. Große "FERTIG!"-Meldung bestätigt den Abschluss

### Sicherheit Ihrer Daten

- ✅ Schülerfotos werden **niemals** ins Internet hochgeladen
- ✅ Alle Daten bleiben **lokal** auf Ihrem Computer
- ✅ Bei Updates bleiben Ihre Fotos **erhalten**
- ✅ Das Programm ist **Open Source** und überprüfbar

## 🔧 Erweiterte Nutzung (für Entwickler)

### CLI-Verwendung

```bash
python -m worksheet_personalizer \
  --worksheet pfad/zum/arbeitsblatt.pdf \
  --students-folder pfad/zu/schuelerfotos/ \
  --output-folder ./personalisiert/
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

# Standard-Fotogröße in cm (Standard: 2.5 für A4-Druck)
export WORKSHEET_PHOTO_SIZE=2.5

# Log-Level
export LOG_LEVEL=INFO
```

### Einstellungsdatei

Die Einstellungen werden in `Maschinenraum/settings.json` gespeichert:

```json
{
  "photo_size_cm": 2.5,          // Fotogröße in cm
  "add_name": true,              // Name hinzufügen (Ja/Nein)
  "add_name_default": true       // Standard für neue Arbeitsblätter
}
```

**Hinweis:** Verwenden Sie `Einstellungen.command` statt diese Datei manuell zu bearbeiten!

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

### Problem: Einstellungen werden nicht gespeichert

**Lösung**: Stellen Sie sicher, dass `Maschinenraum/settings.json` existiert und beschreibbar ist. Die Datei wird automatisch erstellt beim ersten Start von `Einstellungen.command`.

### Problem: Schriftgröße ist zu klein/groß

**Lösung**: Die Schriftgröße wird automatisch als 2.25% der PDF-Höhe berechnet. Dies funktioniert für Standard-Arbeitsblätter optimal. Bei sehr großen oder kleinen PDFs passt sich die Schrift automatisch an.

### Problem: PDF-Generierung schlägt fehl

**Lösung**: Führen Sie `Ersteinrichtung.command` erneut aus. Dies installiert alle benötigten Abhängigkeiten neu.

### Problem: Bilder werden nicht korrekt skaliert

**Lösung**: Überprüfen Sie, dass die Eingabebilder eine ausreichende Auflösung haben (mindestens 300x400 Pixel empfohlen).

### Problem: "Module not found" Fehler

**Lösung**: Führen Sie `Ersteinrichtung.command` erneut aus, um die virtuelle Umgebung und alle Dependencies neu zu installieren.

### Problem: Terminal-Fenster schließt sich nicht

**Lösung**: Dies ist ein Sicherheitsfeature bei Fehlern. Lesen Sie die Fehlermeldung und beheben Sie das Problem. Bei erfolgreicher Ausführung schließt sich das Fenster automatisch.

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
