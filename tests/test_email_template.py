#!/usr/bin/env python3
"""
Test script to verify email template generation works correctly.
"""

from pathlib import Path

from fixture_items import get_sample_items
from src.html_generator import HTMLGenerator


def test_email_generation():
    """Test email template generation with extensive sample data."""

    # Create sample content items with realistic BIP data
    # Mix of articles and file attachments across multiple dates and categories
    items = get_sample_items()

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
    print(f"  • New entries: {entry_types.get('nowy', 0)}")
    print(f"  • Updates: {entry_types.get('aktualizacja', 0)}")

    print("\n📄 First 200 characters of generated email:")
    print(email_content[:200] + "...")

    return output_path


if __name__ == "__main__":
    test_email_generation()
