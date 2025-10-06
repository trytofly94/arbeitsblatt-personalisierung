# Norddruck Font

## Font-Datei

`NORDDRUC_REBUILT.TTF` - Norddruck-Schriftart mit korrigiertem Unicode-Mapping

## Hintergrund

Die originale Norddruck TTF-Datei aus dem Jahr 1997 hatte ein Problem mit der Character Map (CMap):
- Alle Zeichen waren im **Private Use Area** (U+F000 - U+F0FF) kodiert
- Standard ASCII/Unicode-Zeichen (z.B. 'A' bei U+0041) waren nicht verfügbar
- Dies führte zu Darstellungsproblemen in ReportLab

## Lösung

Die Font wurde mit `fontTools` neu aufgebaut:

1. **Analyse**: Zeichen befanden sich bei U+F020 - U+F0FF statt U+0020 - U+00FF
2. **Remapping**: Alle Zeichen wurden um 0xF000 nach unten verschoben
   - `U+F041 ('A') → U+0041 ('A')`
   - `U+F061 ('a') → U+0061 ('a')`
   - etc.
3. **CMap Rebuild**: Neue Format 4 + Format 12 CMap Tables erstellt
4. **Verifikation**: Alle Standard-Zeichen (A-Z, a-z, 0-9, Satzzeichen) funktionieren

## Verwendung

Die Font wird automatisch vom `PDFProcessor` geladen und registriert:

```python
from worksheet_personalizer.core.pdf_processor import PDFProcessor

# Font wird automatisch als 'Norddruck' registriert
processor = PDFProcessor(worksheet_path, add_name=True)
# processor.font_name == 'Norddruck'
```

## Fallback

Falls die Font nicht geladen werden kann, wird automatisch auf **Helvetica-Bold** zurückgegriffen.

## Technische Details

- **Original Encoding**: Private Use Area (U+F000+)
- **Neues Encoding**: Standard Unicode (U+0000+)
- **CMap Format**: Format 4 (Windows Unicode BMP) + Format 12 (Unicode full)
- **Zeichen**: 141 Glyphs (Buchstaben, Zahlen, Satzzeichen, Sonderzeichen)
