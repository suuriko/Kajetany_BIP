"""
HTML Generator Module for BIP Reports

This module provides functionality to generate static HTML reports from scraped BIP data
using Jinja2 templates. It offers flexibility in formatting and styling while maintaining
a clean separation between data and presentation.

Usage:
    generator = HTMLGenerator()
    generator.generate_report(items_data, output_path="report.html")
"""

import datetime
import locale
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.models.elements import ContentItem


class HTMLGenerator:
    """
    A flexible HTML generator that uses Jinja2 templates to create static HTML files
    from BIP content data.
    """

    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the HTML generator with a templates directory.

        Args:
            templates_dir: Path to the directory containing Jinja2 templates
        """
        self.templates_dir = Path(templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir), autoescape=select_autoescape(["html", "xml"])
        )

        # Add custom filters
        self.env.filters["datetime_format"] = self._datetime_format
        self.env.filters["date_format"] = self._date_format
        self.env.filters["polish_date_format"] = self._polish_date_format
        self.env.filters["truncate"] = self._truncate_text
        self.env.filters["entry_type"] = self._get_entry_type

    @staticmethod
    def _datetime_format(value: datetime.datetime, format_str: str = "%d.%m.%Y %H:%M") -> str:
        """Custom filter for datetime formatting."""
        if value is None:
            return "Nieznana"
        return value.strftime(format_str)

    @staticmethod
    def _date_format(value: datetime.date, format_str: str = "%d.%m.%Y") -> str:
        """Custom filter for date formatting."""
        if value is None:
            return "Nieznana"
        return value.strftime(format_str)

    @staticmethod
    def _polish_date_format(value: datetime.date, format_str: str = "%-d %B %Y") -> str:
        """Format date to Polish format using locale."""
        if value is None:
            return "Nieznana"

        # Save current locale
        original_locale = locale.getlocale(locale.LC_TIME)
        try:
            # Try to set Polish locale
            locale.setlocale(locale.LC_TIME, "pl_PL.UTF-8")
            return value.strftime(format_str)
        except locale.Error:
            # Fallback to original locale if Polish is not available
            try:
                locale.setlocale(locale.LC_TIME, original_locale)
            except (locale.Error, TypeError):
                pass
            return value.strftime(format_str)
        finally:
            # Always restore original locale
            try:
                locale.setlocale(locale.LC_TIME, original_locale)
            except (locale.Error, TypeError):
                pass

    @staticmethod
    def _truncate_text(value: str, length: int = 200, end: str = "...") -> str:
        """Truncate text to specified length."""
        if value is None:
            return ""
        if len(value) <= length:
            return value
        return value[:length].rstrip() + end

    @staticmethod
    def _get_entry_type(item) -> str:
        """Determine if entry is new or updated based on dates."""
        # If we don't have enough date information, assume it's new
        if not hasattr(item, "last_modified_at") or not item.last_modified_at:
            return "nowy"

        # Get reference dates (when the item was first created/published)
        reference_dates = []
        if hasattr(item, "created_at") and item.created_at:
            reference_dates.append(item.created_at)
        if hasattr(item, "published_at") and item.published_at:
            reference_dates.append(item.published_at)

        # If no reference dates, assume it's new
        if not reference_dates:
            return "nowy"

        # Find the earliest reference date
        earliest_date = min(reference_dates)

        # If last_modified_at is later than the earliest reference date, it's an update
        if item.last_modified_at > earliest_date:
            return "aktualizacja"
        else:
            return "nowy"

    def _prepare_items_data(self, items: List[ContentItem]) -> List[Dict[str, Any]]:
        """
        Convert ContentItem objects to dictionaries suitable for template rendering.

        Args:
            items: List of ContentItem objects

        Returns:
            List of dictionaries with item data
        """
        return [
            {
                "url": item.url,
                "main_title": item.main_title,
                "title": item.title,
                "description": item.description,
                "published_at": item.published_at,
                "created_at": item.created_at,
                "last_modified_at": item.last_modified_at,
            }
            for item in items
        ]

    def generate_report(
        self,
        items: List[ContentItem],
        output_path: str = "gh-pages/index.html",
        template_name: str = "bip_report.html",
        custom_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate an HTML report from BIP content items.

        Args:
            items: List of ContentItem objects to include in the report
            output_path: Path where the generated HTML file will be saved
            template_name: Name of the Jinja2 template to use
            custom_context: Additional context variables for the template

        Returns:
            Path to the generated HTML file
        """
        template = self.env.get_template(template_name)

        # Prepare template context
        context = {
            "page_title": "Biuletyn Informacji Publicznej - Nadarzyn",
            "subtitle": "Automatyczny monitoring komunikatów i ogłoszeń dla Kajetan",
            "items": self._prepare_items_data(items),
            "last_updated": datetime.datetime.now().strftime("%d.%m.%Y"),
            "generation_time": datetime.datetime.now(),
        }

        # Add custom context if provided
        if custom_context:
            context.update(custom_context)

        # Render template
        html_content = template.render(**context)

        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write HTML file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        return str(output_file)

    def generate_from_csv(
        self,
        csv_path: str,
        output_path: str = "gh-pages/index.html",
        template_name: str = "bip_report.html",
        custom_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate an HTML report directly from a CSV file containing BIP data.

        Args:
            csv_path: Path to the CSV file with BIP data
            output_path: Path where the generated HTML file will be saved
            template_name: Name of the Jinja2 template to use
            custom_context: Additional context variables for the template

        Returns:
            Path to the generated HTML file
        """
        # Read CSV data
        df = pd.read_csv(csv_path)

        # Convert DataFrame rows to ContentItem objects
        items = []
        for _, row in df.iterrows():
            item_data = row.to_dict()

            # Handle date parsing
            for date_field in ["published_at", "created_at", "last_modified_at"]:
                if date_field in item_data and pd.notna(item_data[date_field]):
                    try:
                        item_data[date_field] = pd.to_datetime(item_data[date_field]).date()
                    except Exception:
                        item_data[date_field] = None
                else:
                    item_data[date_field] = None

            # Create ContentItem, handling missing fields gracefully
            try:
                item = ContentItem(**item_data)
                items.append(item)
            except Exception as e:
                print(f"Warning: Could not create ContentItem from row: {e}")
                continue

        return self.generate_report(
            items=items, output_path=output_path, template_name=template_name, custom_context=custom_context
        )

    def generate_email_content(
        self,
        items: List[ContentItem],
        template_name: str = "email_template.html",
        custom_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate an HTML email content from BIP content items.

        Args:
            items: List of ContentItem objects to include in the email
            template_name: Name of the Jinja2 template to use
            custom_context: Additional context variables for the template

        Returns:
            HTML email content as string
        """
        template = self.env.get_template(template_name)

        # Group items by main_title
        items_grouped = {}
        for item in items:
            main_title = item.main_title or "Różne"
            if main_title not in items_grouped:
                items_grouped[main_title] = []
            items_grouped[main_title].append(item)

        # Prepare context for email template
        context = {
            "items_grouped": items_grouped,
            "total_count": len(items),
            "subject": "[BIP Bot] Nowe wpisy i aktualizacje dla Kajetan w BIP Nadarzyn",
            "generation_time": datetime.datetime.now(),
        }

        # Add custom context if provided
        if custom_context:
            context.update(custom_context)

        return template.render(**context)

    def list_templates(self) -> List[str]:
        """
        List all available templates in the templates directory.

        Returns:
            List of template file names
        """
        return list(self.env.list_templates())


def quick_generate(csv_path: str = "items.csv", output_path: str = "gh-pages/index.html") -> str:
    """
    Quick utility function to generate an HTML report from the default CSV file.

    Args:
        csv_path: Path to the CSV file with BIP data
        output_path: Path where the generated HTML file will be saved

    Returns:
        Path to the generated HTML file
    """
    generator = HTMLGenerator()
    return generator.generate_from_csv(csv_path, output_path)


if __name__ == "__main__":
    # Example usage
    result = quick_generate()
    print(f"HTML report generated: {result}")
