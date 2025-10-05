#!/bin/bash

# Einstellungen.command - Einstellungen für die Arbeitsblatt-Personalisierung ändern
# Dieses Script aktiviert die virtuelle Umgebung und startet das Einstellungs-Menü

# Wechsle zum Script-Verzeichnis
cd "$(dirname "$0")" || exit 1

echo "================================================"
echo "  Einstellungen - Arbeitsblatt-Personalisierung"
echo "================================================"
echo ""

# Prüfe, ob virtuelle Umgebung existiert
if [ ! -d "venv" ]; then
    echo "❌ Fehler: Virtuelle Umgebung nicht gefunden!"
    echo ""
    echo "Bitte führen Sie zuerst 'Ersteinrichtung.command' aus."
    echo ""
    echo "Drücken Sie Enter zum Beenden..."
    read
    exit 1
fi

# Aktiviere virtuelle Umgebung
echo "🔧 Aktiviere virtuelle Umgebung..."
source venv/bin/activate

# Prüfe, ob Aktivierung erfolgreich war
if [ $? -ne 0 ]; then
    echo "❌ Fehler beim Aktivieren der virtuellen Umgebung!"
    echo ""
    echo "Drücken Sie Enter zum Beenden..."
    read
    exit 1
fi

echo "✓ Virtuelle Umgebung aktiviert"
echo ""

# Starte Einstellungs-Menü
python -c "from worksheet_personalizer.settings_manager import interactive_settings_update; interactive_settings_update()"

# Prüfe Exit-Code
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Fehler beim Ändern der Einstellungen!"
    echo ""
    echo "Drücken Sie Enter zum Beenden..."
    read
    exit 1
fi

# Deaktiviere virtuelle Umgebung
deactivate

exit 0
