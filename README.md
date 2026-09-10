# Wayback Machine Link Scraper

Ein Python-Tool zum Scrapen von URLs aus der Wayback Machine mit erweiterten Filter- und Deduplicationsfunktionen.

## Features

✨ **Keyword-Filterung**: Suche nach URLs die bestimmte Wörter enthalten (z.B. "newsletter")

🎯 **Titel-Filterung**: Filtere URLs nach Website-Titeln (z.B. "sign up")

🔄 **Automatische Deduplizierung**: Nur der aktuellste Link pro Domain

📊 **Mehrere Export-Formate**: JSON und CSV Output

⚡ **Schnelle Verarbeitung**: Nutzt die Wayback Machine CDX API

## Installation

```bash
git clone https://github.com/strategytest88/wayback-machine-scraper.git
cd wayback-machine-scraper
pip install -r requirements.txt
```

## Verwendung

### Einfache Keywordsuche

```bash
python scraper.py newsletter
```

Dies sucht alle URLs in der Wayback Machine die "newsletter" enthalten und:
- Entfernt Duplikate (nur aktuellste pro Domain)
- Sortiert nach Datum (neueste zuerst)
- Speichert in `results.json` und `results.csv`

### Mit Titel-Filter

```bash
python scraper.py newsletter --title "sign up"
```

Sucht URLs mit "newsletter" UND filtert nach Website-Titel "sign up"

### Benutzerdefinierten Output-Dateinamen setzen

```bash
python scraper.py newsletter --output meine_ergebnisse
```

Speichert Ergebnisse in `meine_ergebnisse.json` und `meine_ergebnisse.csv`

### Alle Optionen kombinieren

```bash
python scraper.py newsletter --title "sign up" --output newsletter_results
```

## Output-Format

### JSON Format (`results.json`)

```json
[
  {
    "url": "https://example.com/newsletter",
    "timestamp": "20230615120000",
    "wayback_url": "https://web.archive.org/web/20230615120000/https://example.com/newsletter",
    "date": "15.06.2023 12:00:00"
  },
  ...
]
```

### CSV Format (`results.csv`)

```csv
Domain,Original URL,Wayback URL,Timestamp,Date
example.com,https://example.com/newsletter,https://web.archive.org/web/20230615120000/https://example.com/newsletter,20230615120000,15.06.2023 12:00:00
```

## Wie es funktioniert

1. **Keyword-Suche**: Nutzt die [Wayback Machine CDX Search API](https://github.com/webrecorder/pywb/wiki/CDX-API) um URLs zu finden
2. **Titel-Filterung**: Lädt jeden Wayback-Snapshot und prüft auf den gesuchten Titel
3. **Deduplizierung**: Vergleicht Domains und behält nur den Snapshot mit dem neuesten Timestamp
4. **Export**: Speichert gefilterte Ergebnisse in strukturierten Formaten

## Tipps & Tricks

### Mehrere Keywords kombinieren

Wen du nach verschiedenen Keywords suchen möchtest, führe den Scraper mehrfach aus:

```bash
python scraper.py newsletter --output newsletter_urls
python scraper.py subscribe --output subscribe_urls
python scraper.py "sign up" --output signup_urls
```

### Performance-Optimierung

Bei vielen Ergebnissen (z.B. mit Titel-Filter) kann die Verarbeitung lange dauern, da jede URL abgerufen werden muss.

**Tipp**: Starte mit Keywordsuche ohne Titel-Filter, um schnell einen Überblick zu bekommen.

## Fehlerbehebung

### Timeout-Fehler

Wenn die Suche abbricht, erhöhe den Timeout:
```python
response = requests.get(self.search_api, params=params, timeout=60)
```

### Zu viele Ergebnisse

Reduziere das `limit` in der `search_urls()` Methode:
```python
urls = scraper.search_urls(keyword=keyword, limit=1000)
```

### Rate-Limiting

Wenn viele Requests abgelehnt werden, füge Pausen ein:
```python
import time
time.sleep(0.5)  # 500ms Pause zwischen Requests
```

## API-Quellen

- [Wayback Machine CDX Search API](https://github.com/webrecorder/pywb/wiki/CDX-API)
- [Archive.org Developer Documentation](https://archive.org/developers/)

## Lizenz

MIT License

## Kontakt

Bei Fragen oder Bugs: [GitHub Issues](https://github.com/strategytest88/wayback-machine-scraper/issues)
