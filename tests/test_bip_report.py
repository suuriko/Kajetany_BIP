#!/usr/bin/env python3
"""
Test script to verify BIP report template generation works correctly.
"""

from pathlib import Path

from fixture_items import get_sample_items
from src.html_generator import HTMLGenerator


def test_bip_report_generation():
    """Test BIP report template generation with extensive sample data."""

    # Get sample items from fixtures
    items = get_sample_items()

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
