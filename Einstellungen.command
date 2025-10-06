#!/bin/bash

# Einstellungen.command - Einstellungen für die Arbeitsblatt-Personalisierung ändern
# Dieses Script bietet ein interaktives Menü zum Ändern der Einstellungen

# Wechsle zum Script-Verzeichnis
cd "$(dirname "$0")" || exit 1

clear

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
source venv/bin/activate > /dev/null 2>&1

# Lade aktuelle Einstellungen aus Maschinenraum
SETTINGS_FILE="Maschinenraum/settings.json"

# Funktion zum Lesen einer Einstellung
get_setting() {
    local key=$1
    local default=$2
    if [ -f "$SETTINGS_FILE" ]; then
        python3 -c "import json; print(json.load(open('$SETTINGS_FILE')).get('$key', '$default'))" 2>/dev/null || echo "$default"
    else
        echo "$default"
    fi
}

# Funktion zum Setzen einer Einstellung
set_setting() {
    local key=$1
    local value=$2
    python3 << EOF
import json
import os

settings = {}
if os.path.exists('$SETTINGS_FILE'):
    with open('$SETTINGS_FILE', 'r') as f:
        settings = json.load(f)

settings['$key'] = $value

with open('$SETTINGS_FILE', 'w') as f:
    json.dump(settings, f, indent=2)
EOF
}

# Hauptmenü-Schleife
while true; do
    # Lade aktuelle Werte neu bei jedem Schleifendurchlauf
    PHOTO_SIZE=$(get_setting "photo_size_cm" "2.5")
    # Versuche add_name_default, falls nicht vorhanden nutze add_name
    ADD_NAME=$(get_setting "add_name_default" "$(get_setting 'add_name' 'true')")

    clear
    echo "================================================"
    echo "  Einstellungen"
    echo "================================================"
    echo ""
    echo "Aktuelle Einstellungen:"
    echo ""
    echo "  1) Fotogröße: ${PHOTO_SIZE} cm"
    echo "  2) Name hinzufügen: $([ "$ADD_NAME" = "true" ] && echo "Ja" || echo "Nein")"
    echo ""
    echo "  0) Speichern und Beenden"
    echo ""
    echo -n "Welche Einstellung möchten Sie ändern? (0-2): "
    read -r CHOICE

    case $CHOICE in
        1)
            # Fotogröße ändern
            clear
            echo "================================================"
            echo "  Fotogröße ändern"
            echo "================================================"
            echo ""
            echo "Aktuelle Größe: ${PHOTO_SIZE} cm"
            echo ""
            echo "Wählen Sie eine Fotogröße:"
            echo ""
            echo "  1) 1.5 cm (Klein)"
            echo "  2) 2.0 cm (Mittel-Klein)"
            echo "  3) 2.5 cm (Standard)"
            echo "  4) 3.0 cm (Mittel-Groß)"
            echo "  5) 3.5 cm (Groß)"
            echo "  6) 4.0 cm (Sehr Groß)"
            echo "  7) Benutzerdefiniert"
            echo ""
            echo -n "Ihre Wahl (1-7): "
            read -r SIZE_CHOICE

            case $SIZE_CHOICE in
                1) PHOTO_SIZE="1.5" ;;
                2) PHOTO_SIZE="2.0" ;;
                3) PHOTO_SIZE="2.5" ;;
                4) PHOTO_SIZE="3.0" ;;
                5) PHOTO_SIZE="3.5" ;;
                6) PHOTO_SIZE="4.0" ;;
                7)
                    echo ""
                    echo -n "Geben Sie die Fotogröße in cm ein (0.5 - 10.0): "
                    read -r CUSTOM_SIZE
                    PHOTO_SIZE="$CUSTOM_SIZE"
                    ;;
                *)
                    echo ""
                    echo "❌ Ungültige Eingabe!"
                    sleep 2
                    continue
                    ;;
            esac
            echo ""
            echo "✓ Fotogröße auf ${PHOTO_SIZE} cm gesetzt"
            sleep 1
            ;;

        2)
            # Name hinzufügen ändern
            clear
            echo "================================================"
            echo "  Name auf Arbeitsblatt hinzufügen"
            echo "================================================"
            echo ""
            echo "Aktuell: $([ "$ADD_NAME" = "true" ] && echo "Ja" || echo "Nein")"
            echo ""
            echo "Soll der Name des Schülers auf dem Arbeitsblatt"
            echo "angezeigt werden?"
            echo ""
            echo "  1) Ja - Name wird hinzugefügt"
            echo "  2) Nein - Nur Foto"
            echo ""
            echo -n "Ihre Wahl (1-2): "
            read -r NAME_CHOICE

            case $NAME_CHOICE in
                1)
                    ADD_NAME="true"
                    echo ""
                    echo "✓ Name wird künftig hinzugefügt"
                    ;;
                2)
                    ADD_NAME="false"
                    echo ""
                    echo "✓ Nur Foto wird verwendet"
                    ;;
                *)
                    echo ""
                    echo "❌ Ungültige Eingabe!"
                    sleep 2
                    continue
                    ;;
            esac
            sleep 1
            ;;

        0)
            # Speichern und Beenden
            clear
            echo "================================================"
            echo "  Einstellungen speichern"
            echo "================================================"
            echo ""
            echo "Folgende Einstellungen werden gespeichert:"
            echo ""
            echo "  • Fotogröße: ${PHOTO_SIZE} cm"
            echo "  • Name hinzufügen: $([ "$ADD_NAME" = "true" ] && echo "Ja" || echo "Nein")"
            echo ""

            # Speichere Einstellungen (beide Keys für Kompatibilität)
            set_setting "photo_size_cm" "$PHOTO_SIZE"
            set_setting "add_name_default" "$ADD_NAME"
            set_setting "add_name" "$ADD_NAME"

            echo "✓ Einstellungen wurden gespeichert!"
            echo ""
            echo "Fenster schließt sich in 2 Sekunden..."
            sleep 2

            deactivate
            osascript -e 'tell application "Terminal" to close first window' &
            exit 0
            ;;

        *)
            echo ""
            echo "❌ Ungültige Eingabe! Bitte wählen Sie 0-2."
            sleep 2
            ;;
    esac
done
