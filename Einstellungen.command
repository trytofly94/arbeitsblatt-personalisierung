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
        python3 -c "import json; val = json.load(open('$SETTINGS_FILE')).get('$key', '$default'); print(str(val).lower())" 2>/dev/null || echo "$default"
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

# Konvertiere String-Werte zu korrekten Typen
value = '$value'
if value.lower() == 'true':
    value = True
elif value.lower() == 'false':
    value = False
elif value.replace('.', '', 1).isdigit():
    # Zahlen (int oder float)
    value = float(value) if '.' in value else int(value)

settings['$key'] = value

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
    NAME_TOP_MARGIN=$(get_setting "name_top_margin_percent" "2.5")
    PHOTO_TOP_MARGIN=$(get_setting "photo_top_margin_percent" "2.5")
    PHOTO_RIGHT_MARGIN=$(get_setting "photo_right_margin_percent" "3.5")

    clear
    echo "================================================"
    echo "  Einstellungen"
    echo "================================================"
    echo ""
    # Funktion zur Beschreibung der Abstände
    get_margin_description() {
        local value=$1
        case $value in
            0.0) echo "Kein Abstand" ;;
            0.5) echo "Minimal" ;;
            1.0) echo "Sehr schmal" ;;
            1.5) echo "Schmal" ;;
            2.5) echo "Normal" ;;
            3.5) echo "Mittel" ;;
            5.0) echo "Breit" ;;
            7.0) echo "Sehr breit" ;;
            10.0) echo "Maximal" ;;
            *) echo "${value}%" ;;
        esac
    }

    echo "Aktuelle Einstellungen:"
    echo ""
    echo "  1) Fotogröße: ${PHOTO_SIZE} cm"
    echo "  2) Name hinzufügen: $([ "$ADD_NAME" = "true" ] && echo "Ja" || echo "Nein")"
    echo "  3) Name-Abstand von oben: $(get_margin_description "$NAME_TOP_MARGIN")"
    echo "  4) Foto-Abstand von oben: $(get_margin_description "$PHOTO_TOP_MARGIN")"
    echo "  5) Foto-Abstand von rechts: $(get_margin_description "$PHOTO_RIGHT_MARGIN")"
    echo ""
    echo "  0) Speichern und Beenden"
    echo ""
    echo -n "Welche Einstellung möchten Sie ändern? (0-5): "
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

            # Speichere Einstellung sofort
            set_setting "photo_size_cm" "$PHOTO_SIZE"

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
                    # Speichere Einstellung sofort (beide Keys für Kompatibilität)
                    set_setting "add_name_default" "$ADD_NAME"
                    set_setting "add_name" "$ADD_NAME"
                    echo ""
                    echo "✓ Name wird künftig hinzugefügt"
                    ;;
                2)
                    ADD_NAME="false"
                    # Speichere Einstellung sofort (beide Keys für Kompatibilität)
                    set_setting "add_name_default" "$ADD_NAME"
                    set_setting "add_name" "$ADD_NAME"
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

        3)
            # Name-Abstand von oben ändern
            clear
            echo "================================================"
            echo "  Name-Abstand von oben ändern"
            echo "================================================"
            echo ""
            echo "Aktuell: $(get_margin_description "$NAME_TOP_MARGIN")"
            echo ""
            echo "Wählen Sie einen Abstand vom oberen Blattrand:"
            echo ""
            echo "  1) Kein Abstand (0.0%)"
            echo "  2) Minimal (0.5%)"
            echo "  3) Sehr schmal (1.0%)"
            echo "  4) Schmal (1.5%)"
            echo "  5) Normal (2.5%)"
            echo "  6) Mittel (3.5%)"
            echo "  7) Breit (5.0%)"
            echo "  8) Sehr breit (7.0%)"
            echo "  9) Maximal (10.0%)"
            echo ""
            echo -n "Ihre Wahl (1-9): "
            read -r MARGIN_CHOICE

            case $MARGIN_CHOICE in
                1) NAME_TOP_MARGIN="0.0" ;;
                2) NAME_TOP_MARGIN="0.5" ;;
                3) NAME_TOP_MARGIN="1.0" ;;
                4) NAME_TOP_MARGIN="1.5" ;;
                5) NAME_TOP_MARGIN="2.5" ;;
                6) NAME_TOP_MARGIN="3.5" ;;
                7) NAME_TOP_MARGIN="5.0" ;;
                8) NAME_TOP_MARGIN="7.0" ;;
                9) NAME_TOP_MARGIN="10.0" ;;
                *)
                    echo ""
                    echo "❌ Ungültige Eingabe!"
                    sleep 2
                    continue
                    ;;
            esac

            # Speichere Einstellung sofort
            set_setting "name_top_margin_percent" "$NAME_TOP_MARGIN"

            echo ""
            echo "✓ Name-Abstand auf $(get_margin_description "$NAME_TOP_MARGIN") gesetzt"
            sleep 1
            ;;

        4)
            # Foto-Abstand von oben ändern
            clear
            echo "================================================"
            echo "  Foto-Abstand von oben ändern"
            echo "================================================"
            echo ""
            echo "Aktuell: $(get_margin_description "$PHOTO_TOP_MARGIN")"
            echo ""
            echo "Wählen Sie einen Abstand vom oberen Blattrand:"
            echo ""
            echo "  1) Kein Abstand (0.0%)"
            echo "  2) Minimal (0.5%)"
            echo "  3) Sehr schmal (1.0%)"
            echo "  4) Schmal (1.5%)"
            echo "  5) Normal (2.5%)"
            echo "  6) Mittel (3.5%)"
            echo "  7) Breit (5.0%)"
            echo "  8) Sehr breit (7.0%)"
            echo "  9) Maximal (10.0%)"
            echo ""
            echo -n "Ihre Wahl (1-9): "
            read -r SUB_CHOICE

            case $SUB_CHOICE in
                1) PHOTO_TOP_MARGIN="0.0" ;;
                2) PHOTO_TOP_MARGIN="0.5" ;;
                3) PHOTO_TOP_MARGIN="1.0" ;;
                4) PHOTO_TOP_MARGIN="1.5" ;;
                5) PHOTO_TOP_MARGIN="2.5" ;;
                6) PHOTO_TOP_MARGIN="3.5" ;;
                7) PHOTO_TOP_MARGIN="5.0" ;;
                8) PHOTO_TOP_MARGIN="7.0" ;;
                9) PHOTO_TOP_MARGIN="10.0" ;;
                *)
                    echo "Ungültige Eingabe."
                    sleep 1
                    continue
                    ;;
            esac

            # Speichere Einstellung sofort
            set_setting "photo_top_margin_percent" "$PHOTO_TOP_MARGIN"

            echo ""
            echo "✓ Foto-Abstand von oben auf $(get_margin_description "$PHOTO_TOP_MARGIN") gesetzt"
            sleep 1
            ;;

        5)
            # Foto-Abstand von rechts ändern
            clear
            echo "================================================"
            echo "  Foto-Abstand von rechts ändern"
            echo "================================================"
            echo ""
            echo "Aktuell: $(get_margin_description "$PHOTO_RIGHT_MARGIN")"
            echo ""
            echo "Wählen Sie einen Abstand vom rechten Blattrand:"
            echo ""
            echo "  1) Kein Abstand (0.0%)"
            echo "  2) Minimal (0.5%)"
            echo "  3) Sehr schmal (1.0%)"
            echo "  4) Schmal (1.5%)"
            echo "  5) Normal (2.5%)"
            echo "  6) Mittel (3.5%)"
            echo "  7) Breit (5.0%)"
            echo "  8) Sehr breit (7.0%)"
            echo "  9) Maximal (10.0%)"
            echo ""
            echo -n "Ihre Wahl (1-9): "
            read -r SUB_CHOICE

            case $SUB_CHOICE in
                1) PHOTO_RIGHT_MARGIN="0.0" ;;
                2) PHOTO_RIGHT_MARGIN="0.5" ;;
                3) PHOTO_RIGHT_MARGIN="1.0" ;;
                4) PHOTO_RIGHT_MARGIN="1.5" ;;
                5) PHOTO_RIGHT_MARGIN="2.5" ;;
                6) PHOTO_RIGHT_MARGIN="3.5" ;;
                7) PHOTO_RIGHT_MARGIN="5.0" ;;
                8) PHOTO_RIGHT_MARGIN="7.0" ;;
                9) PHOTO_RIGHT_MARGIN="10.0" ;;
                *)
                    echo "Ungültige Eingabe."
                    sleep 1
                    continue
                    ;;
            esac

            # Speichere Einstellung sofort
            set_setting "photo_right_margin_percent" "$PHOTO_RIGHT_MARGIN"

            echo ""
            echo "✓ Foto-Abstand von rechts auf $(get_margin_description "$PHOTO_RIGHT_MARGIN") gesetzt"
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
            echo "  • Name-Abstand von oben: $(get_margin_description "$NAME_TOP_MARGIN")"
            echo "  • Foto-Abstand von oben: $(get_margin_description "$PHOTO_TOP_MARGIN")"
            echo "  • Foto-Abstand von rechts: $(get_margin_description "$PHOTO_RIGHT_MARGIN")"
            echo ""

            # Speichere Einstellungen
            set_setting "photo_size_cm" "$PHOTO_SIZE"
            set_setting "add_name_default" "$ADD_NAME"
            set_setting "add_name" "$ADD_NAME"
            set_setting "name_top_margin_percent" "$NAME_TOP_MARGIN"
            set_setting "photo_top_margin_percent" "$PHOTO_TOP_MARGIN"
            set_setting "photo_right_margin_percent" "$PHOTO_RIGHT_MARGIN"

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
            echo "❌ Ungültige Eingabe! Bitte wählen Sie 0-3."
            sleep 2
            ;;
    esac
done
