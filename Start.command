#!/bin/bash

# Start.command - Startet die Arbeitsblatt-Personalisierung
# Dieses Script aktiviert die virtuelle Umgebung und führt die Batch-Verarbeitung aus

# Wechsle zum Script-Verzeichnis
cd "$(dirname "$0")" || exit 1

echo "================================================"
echo "  Arbeitsblatt-Personalisierung"
echo "================================================"
echo ""

# Prüfe, ob virtuelle Umgebung existiert
if [ ! -d "venv" ]; then
    echo "❌ Fehler: Virtuelle Umgebung nicht gefunden!"
    echo ""
    echo "Bitte führen Sie zuerst 'Ersteinrichtung.command' aus."
    echo ""
    sleep 3
    osascript -e 'tell application "Terminal" to close first window' &
    exit 1
fi

# Aktiviere virtuelle Umgebung
echo "🔧 Aktiviere virtuelle Umgebung..."
source venv/bin/activate

# Prüfe, ob Aktivierung erfolgreich war
if [ $? -ne 0 ]; then
    echo "❌ Fehler beim Aktivieren der virtuellen Umgebung!"
    echo ""
    sleep 3
    osascript -e 'tell application "Terminal" to close first window' &
    exit 1
fi

echo "✓ Virtuelle Umgebung aktiviert"
echo ""

# Starte Batch-Verarbeitung
echo "🚀 Starte Batch-Verarbeitung..."
echo ""

python -m worksheet_personalizer.batch_processor

# Prüfe Exit-Code
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Fehler bei der Verarbeitung!"
    echo ""
    sleep 3
    osascript -e 'tell application "Terminal" to close first window' &
    exit 1
fi

# Deaktiviere virtuelle Umgebung
deactivate

echo ""
echo "================================================"
echo "  Verarbeitung abgeschlossen!"
echo "================================================"
echo ""
echo "Fenster schließt sich in 3 Sekunden..."
sleep 3

# Schließe Terminal-Fenster
osascript -e 'tell application "Terminal" to close first window' &
exit 0
