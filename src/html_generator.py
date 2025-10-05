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
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.item_repository import ItemRepository
from src.models import ContentItem


class HTMLGenerator:
    """
    A flexible HTML generator that uses Jinja2 templates to create static HTML files
    from BIP content data.
    """

    logger = logging.getLogger("html_generator")

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
    def _polish_date_format(value: datetime.date) -> str:
        """Format date to Polish format using locale."""
        if value is None:
            return "Nieznana"

        # Save current locale
        original_locale = locale.getlocale(locale.LC_TIME)
        try:
            # Try to set Polish locale
            locale.setlocale(locale.LC_TIME, "pl_PL.UTF-8")
            return value.strftime("%-d %B %Y")
        except locale.Error:
            HTMLGenerator.logger.warning("Polish locale 'pl_PL.UTF-8' not available. The string mapping method.")
            # Fallback: manual month mapping
            months_pl = [
                "stycznia",
                "lutego",
                "marca",
                "kwietnia",
                "maja",
                "czerwca",
                "lipca",
                "sierpnia",
                "września",
                "października",
                "listopada",
                "grudnia",
            ]
            month = months_pl[value.month - 1]
            return f"{value.day} {month} {value.year}"
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
    def _get_entry_type(item: ContentItem) -> str:
        """Determine if entry is new or updated based on dates."""
        return "aktualizacja" if item.last_modified_at else "nowy"

    @staticmethod
    def _group_items_by_date_and_main_title(items: List[ContentItem]) -> List[tuple[str, str, List[ContentItem]]]:
        """
        Group items by date and main_title, then sort them in descending order.

        Args:
            items: List of ContentItem objects to group

        Returns:
            List of tuples (date_string, main_title, items_list) sorted by date descending
        """
        # First group by date
        items_by_date = defaultdict(list)

        for item in items:
            # Get the most relevant date for grouping
            item_date = item.last_modified_at or item.created_at or item.published_at
            if item_date:
                date_str = item_date.strftime("%Y-%m-%d")
                items_by_date[date_str].append(item)

        # Now group by main_title within each date and flatten the structure
        result = []
        for date_str in sorted(items_by_date.keys(), reverse=True):
            items_for_date = items_by_date[date_str]

            # Group by main_title
            items_by_title = defaultdict(list)
            for item in items_for_date:
                main_title = item.main_title or "Różne"
                items_by_title[main_title].append(item)

            # Add each group as a separate tuple
            for main_title in sorted(items_by_title.keys()):
                result.append((date_str, main_title, items_by_title[main_title]))

        return result

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

        # Group items by date for timeline display
        items_by_date = self._group_items_by_date_and_main_title(items)
        print(items_by_date)

        # Prepare template context
        context = {
            "page_title": "Biuletyn Informacji Publicznej - Nadarzyn",
            "subtitle": "Automatyczny monitoring komunikatów i ogłoszeń dla Kajetan",
            "items": items,
            "items_by_date": items_by_date,
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

        item_repository = ItemRepository.from_dataframe(df)

        return self.generate_report(
            items=item_repository.items,
            output_path=output_path,
            template_name=template_name,
            custom_context=custom_context,
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

        # Group items by date and main_title for timeline display
        items_by_date = self._group_items_by_date_and_main_title(items)

        # Prepare context for email template
        context = {
            "items": items,
            "items_by_date": items_by_date,
            "total_count": len(items),
            "subject": "[BIP Bot] Nowe wpisy i aktualizacje dla Kajetan w BIP Nadarzyn",
            "generation_time": datetime.datetime.now(),
        }

        # Add custom context if provided
        if custom_context:
            context.update(custom_context)

        return template.render(**context)
