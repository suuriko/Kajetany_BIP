#!/usr/bin/env python3
"""
Test script to verify email template generation works correctly.
"""

import datetime
from pathlib import Path

from src.html_generator import HTMLGenerator
from src.models.elements import ContentItem


def test_email_generation():
    """Test email template generation with sample data."""

    # Create sample content items - mix of new entries and updates
    items = [
        # Nowy wpis (created_at = last_modified_at)
        ContentItem(
            url="https://bip.nadarzyn.pl/34,organizacje?nobreakup#akapit_562",
            main_title="Lista organizacji pozarządowych",
            title='Stowarzyszenie na Rzecz Dzieci i Osób Niepełnosprawnych „SZLAKIEM TĘCZY"',
            description=(
                '1. Stowarzyszenie na Rzecz Dzieci i Osób Niepełnosprawnych „SZLAKIEM TĘCZY" '
                "Kajetany, ul. Karola Łoniewskiego 11, 05-830 Nadarzyn tel. 793 003 898"
            ),
            created_at=datetime.date(2025, 8, 26),
            published_at=datetime.date(2025, 8, 26),
            last_modified_at=datetime.date(2025, 8, 26),
        ),
        # Aktualizacja (last_modified_at > created_at)
        ContentItem(
            url="https://bip.nadarzyn.pl/73,komunikaty-i-ogloszenia?nobreakup#plik_21282",
            main_title="Obwieszczenie Wójta Gminy Nadarzyn z dnia 26.08.2025",
            title="Obwieszczenie Wójta Gminy Nadarzyn",
            description=(
                "Wójt Gminy Nadarzyn Nadarzyn dnia 26 08 2025 r ul Mszczonowska 24 05 830 Nadarzyn "
                "ROŚ 6220 12 2025 DSZ 1 OBWIESZCZENIE Na podstawie art 10 I art 61 1"
            ),
            created_at=datetime.date(2025, 8, 20),
            published_at=datetime.date(2025, 8, 20),
            last_modified_at=datetime.date(2025, 8, 26),  # Zaktualizowane później
        ),
        # Nowy wpis bez description
        ContentItem(
            url="https://bip.nadarzyn.pl/1071,rok-2025?tresc=18160",
            main_title="Protokół z XIII Sesji Rady Gminy Nadarzyn",
            title="Protokół z XIII Sesji",
            description=None,
            created_at=datetime.date(2025, 8, 26),
            published_at=datetime.date(2025, 8, 26),
            last_modified_at=datetime.date(2025, 8, 26),
        ),
        # Dodajmy więcej różnorodnych wpisów
        ContentItem(
            url="https://bip.nadarzyn.pl/1053,rok-2025?tresc=18157#akapit_7469",
            main_title="Uchwały Rady Gminy Nadarzyn podjęte na XV Sesji",
            title="Uchwała Nr XV.293.2025",
            description=(
                "Wykaz uchwał z XV sesji z dnia 27 sierpnia 2025 r. Uchwała Nr XV.293.2025 "
                "w sprawie szczegółowych warunków i trybu przyznawania nagród za osiągnięcia "
                "w dziedzinie twórczości artystycznej"
            ),
            created_at=datetime.date(2025, 8, 27),
            published_at=datetime.date(2025, 8, 27),
            last_modified_at=datetime.date(2025, 8, 28),  # Aktualizacja
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/88,zawiadomienia-o-zwolaniu-sesji?tresc=18194",
            main_title="Zawiadomienie o zwołaniu Sesji Rady Gminy Nadarzyn",
            title="Zawiadomienie o XVI Sesji",
            description="Załącznik nr 3 do Uchwały Nr Rady Gminy Nadarzyn z dnia Zmiana Tabeli nr 3",
            created_at=datetime.date(2025, 9, 1),
            published_at=datetime.date(2025, 9, 1),
            last_modified_at=datetime.date(2025, 9, 1),  # Nowy
        ),
    ]

    print("=== Email Template Generation Test ===\n")

    # Generate email content
    generator = HTMLGenerator()
    email_content = generator.generate_email_content(items)

    # Save to file for inspection
    output_path = Path("tests/test_email_output.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(email_content)

    print("✅ Email content generated successfully!")
    print(f"📧 Email contains {len(items)} items grouped by main_title")
    print(f"💾 Saved to: {output_path.absolute()}")

    # Show basic statistics
    grouped_count = {}
    entry_types = {"nowy": 0, "aktualizacja": 0}

    for item in items:
        main_title = item.main_title or "Różne"
        grouped_count[main_title] = grouped_count.get(main_title, 0) + 1

        # Test entry type logic
        entry_type = generator._get_entry_type(item)
        entry_types[entry_type] = entry_types.get(entry_type, 0) + 1

    print("\n📊 Content breakdown:")
    for title, count in grouped_count.items():
        print(f"  • {title}: {count} item(s)")

    print("\n🏷️  Entry types:")
    print(f"  • Nowe wpisy: {entry_types.get('nowy', 0)}")
    print(f"  • Aktualizacje: {entry_types.get('aktualizacja', 0)}")

    print("\n📄 First 200 characters of generated email:")
    print(email_content[:200] + "...")

    return output_path


if __name__ == "__main__":
    test_email_generation()
