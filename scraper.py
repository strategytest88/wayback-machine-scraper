#!/usr/bin/env python3
"""
Wayback Machine Link Scraper
Filtiert URLs nach Keywords und Website-Titeln
Gibt den aktuellsten Link pro Domain ohne Duplikate
"""

import requests
import json
from urllib.parse import urlparse
from datetime import datetime
from typing import List, Dict, Set
import sys
import os
import signal
import time

class WaybackMachineScraper:
    def __init__(self):
        self.base_url = "https://archive.org/wayback/available"
        self.search_api = "http://web.archive.org/cdx/search/cdx?url=archive.org"
        self.cache_dir = ".cache"
        self.interrupted = False
        
        # Interrupt-Handler (Ctrl+C)
        signal.signal(signal.SIGINT, self._handle_interrupt)
        
        # Cache-Verzeichnis erstellen
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _handle_interrupt(self, signum, frame):
        """Handler für Ctrl+C - speichert bisherige Ergebnisse"""
        print("\n\n⚠️  Verarbeitung unterbrochen (Ctrl+C)")
        self.interrupted = True
    
    def search_urls(self, keyword: str = None, title: str = None, limit: int = 10000) -> List[Dict]:
        """
        Sucht URLs in der Wayback Machine nach Keyword oder Website-Titel
        OHNE den Content zu laden - nur Metadaten!
        
        Args:
            keyword: Suchbegriff der in der URL vorkommen soll
            title: Website-Titel nach dem gefiltert werden soll
            limit: Maximale Anzahl von Ergebnissen
            
        Returns:
            Liste von URLs mit Metadaten
        """
        try:
            # Suche in CDX API
            params = {
                'url': '*',
                'matchType': 'prefix',
                'output': 'json',
                'fl': 'timestamp,original,statuscode,mimetype',
                'filter': 'statuscode:200',
                'collapse': 'urlkey',
                'limit': limit,
            }
            
            if keyword:
                params['url'] = f"*{keyword}*"
            
            print(f"\n🔍 Suche nach Keyword: {keyword or 'alle URLs'}")
            print(f"📝 Filter nach Titel: {title or 'keine'}")
            print("⏳ Dies kann eine Weile dauern...\n")
            
            response = requests.get(self.search_api, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) < 2:
                print("❌ Keine Ergebnisse gefunden")
                return []
            
            results = []
            for row in data[1:]:  # Header überspringen
                timestamp, original, statuscode, mimetype = row
                
                # Filter nach HTML/Text Seiten
                if mimetype and 'text' not in mimetype.lower():
                    continue
                    
                results.append({
                    'url': original,
                    'timestamp': timestamp,
                    'wayback_url': f"https://web.archive.org/web/{timestamp}/{original}",
                    'date': self._parse_timestamp(timestamp)
                })
            
            print(f"�� {len(results)} URLs gefunden (nur Metadaten, kein Content geladen!)\n")
            return results
            
        except Exception as e:
            print(f"❌ Fehler bei der Suche: {str(e)}")
            return []
    
    def preview_results(self, urls: List[Dict], title: str = None) -> int:
        """
        Zeigt Preview der Ergebnisse und fragt Nutzer wie viele verarbeitet werden sollen
        
        Args:
            urls: Alle gefundenen URLs
            title: Titel-Filter (für Info-Text)
            
        Returns:
            Anzahl der URLs die verarbeitet werden sollen
        """
        print("\n" + "="*80)
        print("PREVIEW - GEFUNDENE ERGEBNISSE")
        print("="*80 + "\n")
        
        # Deduplizierung für Preview
        domains = set()
        unique_urls = []
        for item in urls:
            domain = urlparse(item['url']).netloc
            if domain not in domains:
                domains.add(domain)
                unique_urls.append(item)
                
                if len(unique_urls) <= 10:  # Zeige erste 10
                    print(f"{len(unique_urls)}. {domain}")
                    print(f"   URL: {item['url']}")
                    print(f"   Datum: {item['date']}")
                    print()
        
        print(f"\n📊 ZUSAMMENFASSUNG:")
        print(f"   • Gesamt gefundene URLs: {len(urls)}")
        print(f"   • Einzigartige Domains: {len(unique_urls)}")
        
        if title:
            print(f"   • Noch zu prüfen: {len(urls)} URLs auf Titel '{title}'")
            print(f"   ⚠️  WARNUNG: Dies kann lange dauern (10+ Sekunden pro URL)!")
        
        print(f"\n💾 Speichergröße (Metadaten only): ~{len(urls) * 0.3:.1f} KB")
        
        # Nutzer fragen
        print("\n" + "-"*80)
        
        if title:
            print(f"\n❓ Möchtest du diese {len(urls)} URLs nach Titel '{title}' filtern?")
            print("   ⚠️  Dies wird LANGE dauern! (~10 Sekunden pro URL)")
            choice = input("\n(j/n): ").strip().lower()
            
            if choice != 'j':
                print("\n⏭️  Überspringe Titel-Filterung")
                return 0
            return len(urls)
        else:
            try:
                amount = input(f"\n📥 Wieviele URLs möchtest du verarbeiten? (1-{len(urls)}): ").strip()
                amount = int(amount)
                
                if 1 <= amount <= len(urls):
                    return amount
                else:
                    print(f"❌ Ungültig. Verwende Maximum: {len(urls)}")
                    return len(urls)
            except ValueError:
                print(f"❌ Ungültig. Verwende Maximum: {len(urls)}")
                return len(urls)
    
    def filter_by_title_wayback(self, urls: List[Dict], title: str, max_urls: int = None) -> List[Dict]:
        """
        Filtert URLs nach Website-Titel durch Abruf des Wayback-Snapshots
        
        Args:
            urls: Liste von URLs zum Filtern
            title: Gesuchter Website-Titel
            max_urls: Maximale Anzahl zu verarbeiten
            
        Returns:
            Gefilterte Liste
        """
        print(f"\n🔎 Filtere nach Titel: '{title}'")
        print(f"⚠️  Dies ist LANGSAM - lädt jede URL-Kopie!")
        print(f"💡 Tipp: Drücke Ctrl+C um unterbrechen und Ergebnisse zu speichern\n")
        
        filtered = []
        to_process = urls[:max_urls] if max_urls else urls
        
        start_time = time.time()
        
        for i, item in enumerate(to_process, 1):
            if self.interrupted:
                print(f"\n\n⏹️  Bei URL {i}/{len(to_process)} unterbrochen!")
                break
            
            if i % 10 == 0 or i == 1:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = len(to_process) - i
                est_total = avg_time * remaining
                print(f"   ✓ Verarbeitet: {i}/{len(to_process)}... (⏱️  ~{est_total:.0f}s übrig)", end='\r')
            
            try:
                response = requests.get(item['wayback_url'], timeout=10)
                response.encoding = 'utf-8'
                
                if title.lower() in response.text.lower():
                    filtered.append(item)
                time.sleep(0.05)  # Kleine Pause, um Server nicht zu überlasten
                    
            except Exception as e:
                # Fehler ignorieren und weitermachen
                pass
        
        print(f"\n✅ {len(filtered)} URLs mit Titel '{title}' gefunden\n")
        return filtered
    
    def deduplicate_by_domain(self, urls: List[Dict]) -> List[Dict]:
        """
        Entfernt Duplikate und behält nur den aktuellsten Link pro Domain
        
        Args:
            urls: Liste von URLs
            
        Returns:
            Deduplizierte Liste mit aktuellsten Links pro Domain
        """
        print("🔄 Dedupliziere URLs nach Domain...")
        
        domain_map = {}  # domain -> neuester link
        
        for item in urls:
            # Extrahiere Domain
            parsed = urlparse(item['url'])
            domain = parsed.netloc.lower()
            
            # Behalte nur den neuesten Timestamp pro Domain
            if domain not in domain_map or item['timestamp'] > domain_map[domain]['timestamp']:
                domain_map[domain] = item
        
        result = list(domain_map.values())
        print(f"✅ {len(result)} einzigartige Domains\n")
        
        return result
    
    def sort_by_date(self, urls: List[Dict], newest_first: bool = True) -> List[Dict]:
        """
        Sortiert URLs nach Datum
        
        Args:
            urls: Liste von URLs
            newest_first: True für neueste zuerst
            
        Returns:
            Sortierte Liste
        """
        return sorted(urls, key=lambda x: x['timestamp'], reverse=newest_first)
    
    def save_results(self, urls: List[Dict], filename: str = "results"):
        """
        Speichert Ergebnisse als JSON und CSV
        
        Args:
            urls: Liste von URLs
            filename: Basis-Dateiname (ohne Erweiterung)
        """
        # JSON speichern
        json_file = f"{filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(urls, f, indent=2, ensure_ascii=False)
        
        # CSV speichern
        csv_file = f"{filename}.csv"
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("Domain,Original URL,Wayback URL,Timestamp,Date\n")
            for item in urls:
                domain = urlparse(item['url']).netloc
                # Escaping für CSV
                csv_line = f'"{domain}","{item["url"]}","{item["wayback_url"]}",{item["timestamp"]},{item["date"]}'
                f.write(csv_line + "\n")
        
        print(f"\n💾 Ergebnisse gespeichert:")
        print(f"   📄 {json_file} ({len(urls)} Einträge)")
        print(f"   📊 {csv_file}")
        print(f"   💾 Größe: ~{os.path.getsize(json_file) / 1024:.1f} KB")
    
    def print_results(self, urls: List[Dict], limit: int = 20):
        """
        Gibt Ergebnisse formatiert aus
        
        Args:
            urls: Liste von URLs
            limit: Maximale Anzahl zum Anzeigen
        """
        print("\n" + "="*80)
        print(f"ERGEBNISSE ({len(urls)} gesamt)")
        print("="*80 + "\n")
        
        for i, item in enumerate(urls[:limit], 1):
            domain = urlparse(item['url']).netloc
            print(f"{i}. {domain}")
            print(f"   URL: {item['url']}")
            print(f"   Wayback: {item['wayback_url']}")
            print(f"   Datum: {item['date']}")
            print()
        
        if len(urls) > limit:
            print(f"... und {len(urls) - limit} weitere URLs\n")
    
    @staticmethod
    def _parse_timestamp(timestamp: str) -> str:
        """
        Konvertiert Timestamp im Format YYYYMMDDHHMMSS zu lesbarem Format
        """
        try:
            dt = datetime.strptime(timestamp, '%Y%m%d%H%M%S')
            return dt.strftime('%d.%m.%Y %H:%M:%S')
        except:
            return timestamp


def main():
    if len(sys.argv) < 2:
        print("Verwendung: python scraper.py <keyword> [--title <titel>] [--output <dateiname>]")
        print("\nBeispiele:")
        print("  python scraper.py newsletter")
        print("  python scraper.py newsletter --title 'sign up'")
        print("  python scraper.py newsletter --title 'sign up' --output results")
        sys.exit(1)
    
    # Argumente parsen
    keyword = sys.argv[1]
    title = None
    output_file = "results"
    
    if '--title' in sys.argv:
        idx = sys.argv.index('--title')
        if idx + 1 < len(sys.argv):
            title = sys.argv[idx + 1]
    
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    # Scraper ausführen
    scraper = WaybackMachineScraper()
    
    print("🚀 Wayback Machine Link Scraper")
    print("="*80)
    
    # URLs suchen (NUR METADATEN!)
    urls = scraper.search_urls(keyword=keyword, limit=5000)
    
    if not urls:
        print("❌ Keine URLs gefunden.")
        return
    
    # Preview und Nutzer-Entscheidung
    to_process = scraper.preview_results(urls, title)
    
    if to_process == 0:
        print("\n⏭️  Überspringe zur Deduplizierung...")
        urls = scraper.deduplicate_by_domain(urls)
        urls = scraper.sort_by_date(urls, newest_first=True)
    else:
        # Nach Titel filtern
        if title:
            urls = scraper.filter_by_title_wayback(urls, title, max_urls=to_process)
            if not urls and not scraper.interrupted:
                print("❌ Keine URLs mit dem Titel gefunden.")
                return
        else:
            urls = urls[:to_process]
        
        # Deduplizieren
        urls = scraper.deduplicate_by_domain(urls)
        
        # Nach Datum sortieren (neueste zuerst)
        urls = scraper.sort_by_date(urls, newest_first=True)
    
    # Ergebnisse anzeigen
    if urls:
        scraper.print_results(urls)
        
        # Speichern
        scraper.save_results(urls, output_file)
        print("\n✅ Fertig!")
    else:
        print("\n⚠️  Keine Ergebnisse zu speichern.")


if __name__ == "__main__":
    main()
