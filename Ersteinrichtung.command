#!/bin/bash

# Ersteinrichtung.command - Einrichtung der Arbeitsblatt-Personalisierung
# Dieses Script prüft Python, erstellt die virtuelle Umgebung und installiert alle Abhängigkeiten

# Wechsle zum Script-Verzeichnis
cd "$(dirname "$0")" || exit 1

echo "================================================"
echo "  Ersteinrichtung - Arbeitsblatt-Personalisierung"
echo "================================================"
echo ""

# Prüfe Python-Version
echo "🔍 Prüfe Python-Installation..."

# Versuche python3 zu finden
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Fehler: Python ist nicht installiert!"
    echo ""
    echo "Bitte installieren Sie Python 3.9 oder höher von:"
    echo "https://www.python.org/downloads/"
    echo ""
    sleep 5
    osascript -e 'tell application "Terminal" to close first window' &
    exit 1
fi

# Prüfe Python-Version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

echo "✓ Python gefunden: Version $PYTHON_VERSION"

# Prüfe, ob Version >= 3.9
if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]; }; then
    echo "❌ Fehler: Python 3.9 oder höher wird benötigt!"
    echo "   Ihre Version: $PYTHON_VERSION"
    echo ""
    echo "Bitte installieren Sie eine neuere Python-Version von:"
    echo "https://www.python.org/downloads/"
    echo ""
    sleep 5
    osascript -e 'tell application "Terminal" to close first window' &
    exit 1
fi

echo ""

# Prüfe, ob virtuelle Umgebung bereits existiert
if [ -d "venv" ]; then
    echo "⚠️  Virtuelle Umgebung existiert bereits!"
    echo ""
    echo "ℹ️  Verwende bestehende virtuelle Umgebung und aktualisiere Abhängigkeiten..."
    echo ""

    # Aktiviere existierende Umgebung
    source venv/bin/activate

    # Aktualisiere Dependencies
    echo "📦 Aktualisiere Abhängigkeiten..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -e "Maschinenraum[dev]" > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        echo "✓ Abhängigkeiten aktualisiert"
    else
        echo "❌ Fehler beim Aktualisieren der Abhängigkeiten!"
        deactivate
        echo ""
        sleep 3
        osascript -e 'tell application "Terminal" to close first window' &
        exit 1
    fi

    deactivate

    echo ""
    echo "================================================"
    echo "  Aktualisierung abgeschlossen!"
    echo "================================================"
    echo ""
    echo "Sie können nun 'Start.command' ausführen."
    echo ""
    echo "Fenster schließt sich in 3 Sekunden..."
    sleep 3
    osascript -e 'tell application "Terminal" to close first window' &
    exit 0
fi

# Erstelle virtuelle Umgebung
echo "🔧 Erstelle virtuelle Umgebung..."
$PYTHON_CMD -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Fehler beim Erstellen der virtuellen Umgebung!"
    echo ""
    sleep 3
    osascript -e 'tell application "Terminal" to close first window' &
    exit 1
fi

echo "✓ Virtuelle Umgebung erstellt"
echo ""

# Aktiviere virtuelle Umgebung
echo "🔧 Aktiviere virtuelle Umgebung..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Fehler beim Aktivieren der virtuellen Umgebung!"
    echo ""
    sleep 3
    osascript -e 'tell application "Terminal" to close first window' &
    exit 1
fi

echo "✓ Virtuelle Umgebung aktiviert"
echo ""

# Aktualisiere pip
echo "📦 Aktualisiere pip..."
pip install --upgrade pip --quiet

if [ $? -ne 0 ]; then
    echo "❌ Fehler beim Aktualisieren von pip!"
    deactivate
    echo ""
    sleep 3
    osascript -e 'tell application "Terminal" to close first window' &
    exit 1
fi

echo "✓ pip aktualisiert"
echo ""

# Installiere Abhängigkeiten
echo "📦 Installiere Abhängigkeiten..."
echo "   (Dies kann einige Minuten dauern...)"
echo ""

pip install -e "Maschinenraum[dev]" --quiet

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Fehler beim Installieren der Abhängigkeiten!"
    echo ""
    echo "Versuchen Sie es erneut mit:"
    echo "  source venv/bin/activate"
    echo "  pip install -e 'Maschinenraum[dev]'"
    echo ""
    deactivate
    sleep 5
    osascript -e 'tell application "Terminal" to close first window' &
    exit 1
fi

echo "✓ Alle Abhängigkeiten installiert"
echo ""

# Deaktiviere virtuelle Umgebung
deactivate

echo "================================================"
echo "  ✅ Einrichtung erfolgreich abgeschlossen!"
echo "================================================"
echo ""
echo "Sie können nun folgende Scripte ausführen:"
echo ""
echo "  • Start.command         - Arbeitsblätter verarbeiten"
echo "  • Einstellungen.command - Einstellungen ändern"
echo ""
echo "Fenster schließt sich in 5 Sekunden..."
sleep 5

# Schließe Terminal-Fenster
osascript -e 'tell application "Terminal" to close first window' &
exit 0
