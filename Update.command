#!/bin/bash

# Wechsel zum Projektverzeichnis (das Verzeichnis, in dem dieses Skript liegt)
cd "$(dirname "$0")"

clear

echo "================================================"
echo "  Update - Arbeitsblatt-Personalisierung"
echo "================================================"
echo ""

# Prüfe ob Git installiert ist
if ! command -v git &> /dev/null; then
    echo "❌ Git ist nicht installiert!"
    echo ""
    echo "Bitte installieren Sie Git von: https://git-scm.com/download/mac"
    echo ""
    sleep 5
    osascript -e 'tell application "Terminal" to close first window' &
    exit 1
fi

echo "🔄 Prüfe auf Updates..."
echo ""

# Fetch neueste Änderungen
git fetch origin 2>&1 | while IFS= read -r line; do
    echo "  $line"
done

# Prüfe ob Updates verfügbar sind
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u} 2>/dev/null)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo ""
    echo "✓ Bereits auf dem neuesten Stand!"
    echo ""
    echo "Keine Updates verfügbar."
    echo ""
    echo "Fenster schließt sich in 3 Sekunden..."
    sleep 3
    osascript -e 'tell application "Terminal" to close first window' &
    exit 0
fi

echo ""
echo "📥 Updates verfügbar!"
echo ""

# Zeige was sich geändert hat
echo "Änderungen:"
git log --oneline HEAD..@{u} | head -5 | while IFS= read -r line; do
    echo "  • $line"
done

echo ""
echo "⚠️  WICHTIG: Ihre Schülerfotos und Arbeitsblätter bleiben erhalten!"
echo ""
echo "Möchten Sie das Update durchführen? (j/N)"
read -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Jj]$ ]]; then
    echo ""
    echo "❌ Update abgebrochen."
    echo ""
    echo "Fenster schließt sich in 3 Sekunden..."
    sleep 3
    osascript -e 'tell application "Terminal" to close first window' &
    exit 0
fi

echo ""
echo "📦 Führe Update durch..."
echo ""

# Stelle sicher, dass Schüler-Ordner und andere User-Ordner nicht überschrieben werden
# Stash lokale Änderungen (falls vorhanden), aber behalte untracked files
git stash push -m "Auto-stash before update" --include-untracked 2>&1 | while IFS= read -r line; do
    echo "  $line"
done

# Pull neueste Änderungen
echo ""
git pull origin $(git rev-parse --abbrev-ref HEAD) 2>&1 | while IFS= read -r line; do
    echo "  $line"
done

PULL_RESULT=$?

if [ $PULL_RESULT -eq 0 ]; then
    # Stelle lokale Änderungen wieder her (Schülerfotos etc.)
    STASH_LIST=$(git stash list)
    if [[ $STASH_LIST == *"Auto-stash before update"* ]]; then
        echo ""
        echo "🔄 Stelle lokale Dateien wieder her..."
        git stash pop 2>&1 | while IFS= read -r line; do
            echo "  $line"
        done
    fi

    echo ""
    echo "================================================"
    echo "  Update erfolgreich abgeschlossen!"
    echo "================================================"
    echo ""
    echo "✓ Das Programm wurde aktualisiert"
    echo "✓ Ihre Schülerfotos bleiben erhalten"
    echo ""
    echo "Möchten Sie die Abhängigkeiten aktualisieren? (empfohlen)"
    echo "(j/N)"
    read -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Jj]$ ]]; then
        echo ""
        echo "📦 Aktualisiere Abhängigkeiten..."

        # Aktiviere virtuelle Umgebung und aktualisiere
        if [ -d "venv" ]; then
            source venv/bin/activate
            pip install -e "Maschinenraum/.[dev]" --upgrade --quiet
            echo ""
            echo "✓ Abhängigkeiten aktualisiert"
        else
            echo ""
            echo "⚠️  Virtuelle Umgebung nicht gefunden."
            echo "   Führen Sie 'Ersteinrichtung.command' aus."
        fi
    fi
else
    echo ""
    echo "❌ Fehler beim Update!"
    echo ""
    echo "Bitte wenden Sie sich an den Support oder versuchen Sie:"
    echo "  1. Das Projekt neu zu klonen"
    echo "  2. Ihre Schülerfotos vorher zu sichern"
    echo ""
    sleep 5
    osascript -e 'tell application "Terminal" to close first window' &
    exit 1
fi

echo ""
echo "Fenster schließt sich in 5 Sekunden..."
sleep 5
osascript -e 'tell application "Terminal" to close first window' &
exit 0
