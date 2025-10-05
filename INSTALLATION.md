# 🚀 Installation auf einem neuen Mac

Diese Anleitung zeigt, wie Sie alle benötigten Programme auf einem frischen Mac installieren.

## Schritt 1: Terminal öffnen

1. Drücken Sie **`Cmd + Leertaste`** (öffnet Spotlight)
2. Tippen Sie **`Terminal`**
3. Drücken Sie **Enter**

## Schritt 2: Xcode Command Line Tools installieren

Die Xcode Command Line Tools enthalten wichtige Entwickler-Werkzeuge (inklusive Git).

**Kopieren Sie diesen Befehl ins Terminal und drücken Enter:**

```bash
xcode-select --install
```

- Ein Fenster öffnet sich → Klicken Sie auf **"Installieren"**
- Warten Sie, bis die Installation abgeschlossen ist (kann 5-15 Minuten dauern)
- Das Terminal zeigt eine Erfolgsmeldung

## Schritt 3: Homebrew installieren (Paketmanager)

Homebrew ist ein Paketmanager für macOS, der die Installation von Software vereinfacht.

**Kopieren Sie diesen Befehl ins Terminal:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

- Drücken Sie **Enter**, wenn Sie dazu aufgefordert werden
- Geben Sie Ihr **Mac-Passwort** ein (es wird nicht angezeigt - das ist normal!)
- Warten Sie, bis die Installation fertig ist

**Wichtig für M1/M2/M3 Macs:** Nach der Installation werden zwei Befehle angezeigt, die Sie ausführen müssen. Sie sehen etwa so aus:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**→ Kopieren Sie diese beiden Zeilen und führen Sie sie aus!**

## Schritt 4: Python 3 installieren

```bash
brew install python@3.11
```

Warten Sie, bis die Installation abgeschlossen ist.

## Schritt 5: Git installieren (falls noch nicht vorhanden)

```bash
brew install git
```

## Schritt 6: Installation überprüfen

Überprüfen Sie, ob alles korrekt installiert wurde:

```bash
git --version
python3 --version
```

Sie sollten Versionsnummern sehen, z.B.:
- `git version 2.39.0`
- `Python 3.11.x`

## Schritt 7: Arbeitsblatt-Personalisierung herunterladen

**Wechseln Sie in den Ordner, wo Sie das Projekt speichern möchten:**

```bash
cd ~/Desktop
```

**Laden Sie das Projekt herunter:**

```bash
git clone https://github.com/trytofly94/arbeitsblatt-personalisierung.git
```

**Wechseln Sie in das Projekt-Verzeichnis:**

```bash
cd arbeitsblatt-personalisierung
```

## Schritt 8: Ersteinrichtung durchführen

**Im Finder:**
1. Öffnen Sie den Ordner `arbeitsblatt-personalisierung` auf Ihrem Desktop
2. **Doppelklick** auf `Ersteinrichtung.command`
3. Falls eine Sicherheitswarnung erscheint:
   - **Rechtsklick** auf `Ersteinrichtung.command`
   - Wählen Sie **"Öffnen"**
   - Bestätigen Sie mit **"Öffnen"**

Die Installation läuft automatisch!

## ✅ Fertig!

Sie können jetzt das Tool verwenden:

1. **Schülerfotos** in `Schüler-A/` legen
2. **PDF-Arbeitsblatt** in `Input-A/` legen
3. **Doppelklick** auf `Start.command`

---

## 🔄 Später: Programm aktualisieren

**Im Terminal:**

```bash
cd ~/Desktop/arbeitsblatt-personalisierung
git pull
```

**Oder einfacher: Doppelklick auf `Update.command`**

---

## ❓ Probleme?

### "command not found: brew"

→ Homebrew wurde nicht korrekt installiert. Wiederholen Sie Schritt 3.

Für M1/M2/M3 Macs führen Sie zusätzlich aus:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Schließen Sie das Terminal und öffnen Sie es neu.

### "command not found: git"

→ Xcode Command Line Tools fehlen. Wiederholen Sie Schritt 2.

### "Permission denied"

→ Sie haben keine Berechtigung. Versuchen Sie:

```bash
sudo xcode-select --install
```

Geben Sie Ihr Mac-Passwort ein.

### Python-Fehler beim Start

→ Virtuelle Umgebung neu erstellen:

```bash
cd ~/Desktop/arbeitsblatt-personalisierung
rm -rf venv
```

Dann Doppelklick auf `Ersteinrichtung.command`

---

## 📧 Kontakt

Bei Problemen erstellen Sie ein Issue auf GitHub:
https://github.com/trytofly94/arbeitsblatt-personalisierung/issues
