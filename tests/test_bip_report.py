#!/usr/bin/env python3
"""
Test script to verify BIP report template generation works correctly.
"""

import datetime
from pathlib import Path

from src.html_generator import HTMLGenerator
from src.models import ContentItem


def test_bip_report_generation():
    """Test BIP report template generation with sample data."""

    # Create sample content items with realistic BIP data
    items = [
        # Organizacje pozarządowe
        ContentItem(
            url="https://bip.nadarzyn.pl/34,organizacje?nobreakup#akapit_562",
            main_title="Lista organizacji pozarządowych",
            title='Stowarzyszenie na Rzecz Dzieci i Osób Niepełnosprawnych „SZLAKIEM TĘCZY"',
            description=(
                '1. Stowarzyszenie na Rzecz Dzieci i Osób Niepełnosprawnych „SZLAKIEM TĘCZY" '
                "Kajetany, ul. Karola Łoniewskiego 11, 05-830 Nadarzyn tel. 793 003 898 "
                "e-mail: szlakiemteczy@nadarzyn.pl"
            ),
            created_at=datetime.date(2025, 8, 26),
            published_at=datetime.date(2025, 8, 26),
            last_modified_at=datetime.date(2025, 8, 26),
        ),
        # Obwieszczenia
        ContentItem(
            url="https://bip.nadarzyn.pl/73,komunikaty-i-ogloszenia?nobreakup#plik_21282",
            main_title="Obwieszczenie Wójta Gminy Nadarzyn z dnia 26.08.2025",
            title="Obwieszczenie Wójta Gminy Nadarzyn",
            description=(
                "Wójt Gminy Nadarzyn Nadarzyn dnia 26 08 2025 r ul Mszczonowska 24 05 830 Nadarzyn "
                "ROŚ 6220 12 2025 DSZ 1 OBWIESZCZENIE Na podstawie art 10 I art 61 1 oraz 4 ustawy "
                "z dnia 14 czerwca 1960 r Kodeks"
            ),
            created_at=datetime.date(2025, 8, 20),
            published_at=datetime.date(2025, 8, 20),
            last_modified_at=datetime.date(2025, 8, 26),
        ),
        # Protokoły z sesji
        ContentItem(
            url="https://bip.nadarzyn.pl/1071,rok-2025?tresc=18160",
            main_title="Protokół z XIII Sesji Rady Gminy Nadarzyn",
            title="Protokół z XIII Sesji",
            description="Protokół z XIII Sesji Rady Gminy Nadarzyn z dnia 25 lipca 2025 roku",
            created_at=datetime.date(2025, 7, 25),
            published_at=datetime.date(2025, 7, 25),
            last_modified_at=datetime.date(2025, 7, 25),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/1071,rok-2025?tresc=18161",
            main_title="Protokół z XIV Sesji Rady Gminy Nadarzyn",
            title="Protokół z XIV Sesji",
            description="Protokół z XIV Sesji Rady Gminy Nadarzyn z dnia 22 sierpnia 2025 roku",
            created_at=datetime.date(2025, 8, 22),
            published_at=datetime.date(2025, 8, 22),
            last_modified_at=datetime.date(2025, 8, 23),
        ),
        # Uchwały
        ContentItem(
            url="https://bip.nadarzyn.pl/1053,rok-2025?tresc=18157#akapit_7469",
            main_title="Uchwały Rady Gminy Nadarzyn podjęte na XV Sesji",
            title="Uchwała Nr XV.293.2025",
            description=(
                "Wykaz uchwał z XV sesji z dnia 27 sierpnia 2025 r. Uchwała Nr XV.293.2025 "
                "w sprawie szczegółowych warunków i trybu przyznawania nagród za osiągnięcia "
                "w dziedzinie twórczości artystycznej, upowszechniania i ochrony kultury"
            ),
            created_at=datetime.date(2025, 8, 27),
            published_at=datetime.date(2025, 8, 27),
            last_modified_at=datetime.date(2025, 8, 27),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/1053,rok-2025?tresc=18157#plik_21336",
            main_title="Uchwały Rady Gminy Nadarzyn podjęte na XV Sesji",
            title="Uchwała Nr XV.320.2025",
            description=(
                "Uchwała Nr XV 320 2025 Rady Gminy Nadarzyn z dnia 27 sierpnia 2025 r "
                "w sprawie wyrażenia zgody na zawarcie w trybie bezprzetargowym umowy "
                "dzierżawy nieruchomości stanowiących własność Gminy"
            ),
            created_at=datetime.date(2025, 8, 27),
            published_at=datetime.date(2025, 8, 27),
            last_modified_at=datetime.date(2025, 8, 28),
        ),
        # Zawiadomienia
        ContentItem(
            url="https://bip.nadarzyn.pl/88,zawiadomienia-o-zwolaniu-sesji?tresc=18194",
            main_title="Zawiadomienie o zwołaniu Sesji Rady Gminy Nadarzyn",
            title="zawiadomienie_o_sesji_(18)_zal_nr_3.pdf(PDF)",
            description=(
                "Zawiadomienie o zwołaniu XVI Sesji Rady Gminy Nadarzyn na dzień 26 września 2025 roku. "
                "Załącznik nr 3 do Uchwały Nr Rady Gminy Nadarzyn z dnia Zmiana Tabeli nr 3"
            ),
            created_at=datetime.date(2025, 9, 1),
            published_at=datetime.date(2025, 9, 1),
            last_modified_at=datetime.date(2025, 9, 1),
        ),
        # Starsze wpisy dla testowania grouping
        ContentItem(
            url="https://bip.nadarzyn.pl/old-announcement",
            main_title="Stare ogłoszenie",
            title="Historyczne ogłoszenie",
            description="To jest starsze ogłoszenie do testowania grupowania według dat",
            created_at=datetime.date(2025, 6, 15),
            published_at=datetime.date(2025, 6, 15),
            last_modified_at=datetime.date(2025, 6, 20),
        ),
    ]

    print("=== BIP Report Template Generation Test ===\n")

    # Generate BIP report
    generator = HTMLGenerator()
    output_path = generator.generate_report(
        items=items,
        output_path="tests/test_bip_report_output.html",
        template_name="bip_report.html",
        custom_context={
            "page_title": "Test BIP Nadarzyn - Raport",
            "subtitle": "Raport testowy wygenerowany automatycznie",
            "new_items_count": 3,
            "last_updated": "22 września 2025",
        },
    )

    print("✅ BIP report generated successfully!")
    print(f"📄 Report contains {len(items)} items")
    print(f"💾 Saved to: {Path(output_path).absolute()}")

    # Show basic statistics
    grouped_count = {}
    date_count = {}
    entry_types = {"new": 0, "update": 0}

    for item in items:
        # Group by main_title
        main_title = item.main_title or "Różne"
        grouped_count[main_title] = grouped_count.get(main_title, 0) + 1

        # Group by date
        item_date = item.last_modified_at or item.created_at or item.published_at
        if item_date:
            date_str = item_date.strftime("%Y-%m-%d")
            date_count[date_str] = date_count.get(date_str, 0) + 1

        # Count entry types
        entry_type = generator._get_entry_type(item)
        entry_types[entry_type] = entry_types.get(entry_type, 0) + 1

    print("\n📊 Content breakdown by category:")
    for title, count in sorted(grouped_count.items()):
        print(f"  • {title}: {count} item(s)")

    print("\n📅 Content breakdown by date:")
    for date_str, count in sorted(date_count.items(), reverse=True):
        print(f"  • {date_str}: {count} item(s)")

    print("\n🏷️  Entry types:")
    print(f"  • Nowe wpisy: {entry_types.get('new', 0)}")
    print(f"  • Aktualizacje: {entry_types.get('update', 0)}")

    print("\n🌐 Open in browser:")
    print(f"  file://{Path(output_path).absolute()}")

    return output_path


if __name__ == "__main__":
    test_bip_report_generation()
