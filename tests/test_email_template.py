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

    # Create sample content items - kilka pozycji w jednej grupie
    items = [
        # Nowy wpis (tylko published_at, bez last_modified_at)
        ContentItem(
            url="https://bip.nadarzyn.pl/1053,rok-2025?tresc=18157#uchwala_120",
            main_title="Uchwały Rady Gminy Nadarzyn podjęte na XV Sesji",
            title="Uchwała Nr XV/120/2025 w sprawie wyrażenia zgody na przekształcenie zakładu budżetowego",
            description=(
                "Uchwała dotyczy przekształcenia Zakładu Budżetowego Gospodarki Komunalnej i Mieszkaniowej "
                "w Nadarzynie w spółkę z ograniczoną odpowiedzialnością."
            ),
            created_at=datetime.date(2025, 8, 26),
            published_at=datetime.date(2025, 8, 26),
            last_modified_at=None,  # Brak aktualizacji - nowy wpis
        ),
        # Aktualizacja (last_modified_at > created_at)
        ContentItem(
            url="https://bip.nadarzyn.pl/1053,rok-2025?tresc=18157#uchwala_121",
            main_title="Uchwały Rady Gminy Nadarzyn podjęte na XV Sesji",
            title="Uchwała Nr XV/121/2025 w sprawie zmian w budżecie gminy na rok 2025",
            description=(
                "Uchwała wprowadza zmiany w budżecie gminy Nadarzyn na rok 2025 - zwiększenie "
                "dochodów i wydatków o kwotę 250.000 zł na inwestycje infrastrukturalne."
            ),
            created_at=datetime.date(2025, 8, 20),
            published_at=datetime.date(2025, 8, 20),
            last_modified_at=datetime.date(2025, 8, 26),  # Zaktualizowane później
        ),
        # Nowy wpis (tylko published_at, bez last_modified_at)
        ContentItem(
            url="https://bip.nadarzyn.pl/1053,rok-2025?tresc=18157#uchwala_122",
            main_title="Uchwały Rady Gminy Nadarzyn podjęte na XV Sesji",
            title="Uchwała Nr XV/122/2025 w sprawie nadania nazwy ulicy",
            description=None,
            created_at=datetime.date(2025, 8, 26),
            published_at=datetime.date(2025, 8, 26),
            last_modified_at=None,  # Brak aktualizacji - nowy wpis
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
    print(f"📧 Email contains {len(items)} items in one group")
    print(f"💾 Saved to: {output_path}")

    # Group statistics
    grouped_count = {}
    entry_types = {}

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
