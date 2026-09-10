#!/usr/bin/env python3
"""
Beispiele für die Verwendung des Wayback Machine Scrapers als Library
"""

from scraper import WaybackMachineScraper


def example_1_basic_search():
    """Beispiel 1: Einfache Keyword-Suche"""
    print("\n" + "="*60)
    print("BEISPIEL 1: Einfache Keyword-Suche")
    print("="*60)
    
    scraper = WaybackMachineScraper()
    urls = scraper.search_urls(keyword="newsletter", limit=1000)
    urls = scraper.deduplicate_by_domain(urls)
    urls = scraper.sort_by_date(urls)
    
    scraper.print_results(urls, limit=10)
    scraper.save_results(urls, "newsletter")


def example_2_search_with_title():
    """Beispiel 2: Suche mit Titel-Filter"""
    print("\n" + "="*60)
    print("BEISPIEL 2: Suche mit Titel-Filter")
    print("="*60)
    
    scraper = WaybackMachineScraper()
    urls = scraper.search_urls(keyword="newsletter", limit=500)
    urls = scraper.filter_by_title_wayback(urls, "sign up")
    urls = scraper.deduplicate_by_domain(urls)
    urls = scraper.sort_by_date(urls)
    
    scraper.print_results(urls, limit=10)
    scraper.save_results(urls, "newsletter_signup")


def example_3_subscribe_urls():
    """Beispiel 3: Subscribe-URLs finden"""
    print("\n" + "="*60)
    print("BEISPIEL 3: Subscribe URLs finden")
    print("="*60)
    
    scraper = WaybackMachineScraper()
    urls = scraper.search_urls(keyword="subscribe", limit=2000)
    urls = scraper.deduplicate_by_domain(urls)
    urls = scraper.sort_by_date(urls, newest_first=True)
    
    scraper.print_results(urls, limit=15)
    scraper.save_results(urls, "subscribe_urls")


def example_4_contact_forms():
    """Beispiel 4: Contact-Form URLs"""
    print("\n" + "="*60)
    print("BEISPIEL 4: Contact Form URLs")
    print("="*60)
    
    scraper = WaybackMachineScraper()
    urls = scraper.search_urls(keyword="/contact", limit=1500)
    urls = scraper.filter_by_title_wayback(urls, "contact")
    urls = scraper.deduplicate_by_domain(urls)
    urls = scraper.sort_by_date(urls)
    
    scraper.print_results(urls, limit=10)
    scraper.save_results(urls, "contact_urls")


def example_5_custom_processing():
    """Beispiel 5: Benutzerdefinierte Verarbeitung"""
    print("\n" + "="*60)
    print("BEISPIEL 5: Benutzerdefinierte Verarbeitung")
    print("="*60)
    
    scraper = WaybackMachineScraper()
    
    # Suche durchführen
    urls = scraper.search_urls(keyword="newsletter", limit=800)
    print(f"Ursprünglich: {len(urls)} URLs")
    
    # Deduplizierung
    urls = scraper.deduplicate_by_domain(urls)
    print(f"Nach Deduplizierung: {len(urls)} URLs")
    
    # Nur URLs von bestimmten TLDs behalten
    tld_filter = ['.de', '.com', '.org']
    urls = [u for u in urls if any(u['url'].endswith(tld) for tld in tld_filter)]
    print(f"Nach TLD-Filter (.de, .com, .org): {len(urls)} URLs")
    
    # Sortierung
    urls = scraper.sort_by_date(urls, newest_first=True)
    
    scraper.print_results(urls, limit=10)
    scraper.save_results(urls, "newsletter_filtered")


if __name__ == "__main__":
    print("\n🚀 Wayback Machine Scraper - Beispiele\n")
    print("Wähle ein Beispiel zum Ausführen:")
    print("1. Einfache Keyword-Suche")
    print("2. Suche mit Titel-Filter")
    print("3. Subscribe URLs finden")
    print("4. Contact Form URLs")
    print("5. Benutzerdefinierte Verarbeitung")
    
    choice = input("\nEingabe (1-5): ").strip()
    
    if choice == "1":
        example_1_basic_search()
    elif choice == "2":
        example_2_search_with_title()
    elif choice == "3":
        example_3_subscribe_urls()
    elif choice == "4":
        example_4_contact_forms()
    elif choice == "5":
        example_5_custom_processing()
    else:
        print("Ungültige Eingabe")
