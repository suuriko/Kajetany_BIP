#!/usr/bin/env python3
"""
Unit tests for datetime_extractor module.

Tests the datetime extraction functionality that parses various date formats
from text strings commonly found in web content.
"""

from datetime import datetime

from src.crawler.datetime_extractor import DATETIME_PATTERNS, extract_datetime


class TestDatetimeExtractor:
    """Test the extract_datetime function and related functionality."""

    def test_extract_datetime_with_polish_date_format(self):
        """Test extraction of Polish date format (DD.MM.YYYY)."""
        result = extract_datetime("Data publikacji: 15.03.2025")
        expected = datetime(2025, 3, 15)
        assert result == expected

    def test_extract_datetime_with_iso_date_format(self):
        """Test extraction of ISO date format (YYYY-MM-DD)."""
        result = extract_datetime("Updated on 2025-03-15")
        expected = datetime(2025, 3, 15)
        assert result == expected

    def test_extract_datetime_with_iso_datetime_format(self):
        """Test extraction of ISO datetime format (YYYY-MM-DD HH:MM)."""
        # Due to pattern priority, date pattern matches first, so time is ignored
        result = extract_datetime("At 2025-03-15 14:30 exactly")
        expected = datetime(2025, 3, 15)  # Time ignored due to pattern priority
        assert result == expected

    def test_extract_datetime_pattern_priority_behavior(self):
        """Test that patterns are matched in priority order."""
        # Due to pattern priority, "2025-03-15" matches before "2025-03-15 14:30"
        result = extract_datetime("Published: 2025-03-15 14:30")
        expected = datetime(2025, 3, 15)  # Time part not captured due to pattern priority
        assert result == expected

    def test_extract_datetime_with_multiple_dates_returns_first(self):
        """Test that when multiple dates are present, the first one is returned."""
        text = "Created: 15.03.2025, Modified: 16.03.2025"
        result = extract_datetime(text)
        expected = datetime(2025, 3, 15)
        assert result == expected

    def test_extract_datetime_with_no_date_returns_none(self):
        """Test that text without dates returns None."""
        result = extract_datetime("This text has no dates in it")
        assert result is None

    def test_extract_datetime_with_empty_string_returns_none(self):
        """Test that empty string returns None."""
        result = extract_datetime("")
        assert result is None

    def test_extract_datetime_with_none_returns_none(self):
        """Test that None input returns None."""
        result = extract_datetime(None)
        assert result is None

    def test_extract_datetime_with_whitespace_only_returns_none(self):
        """Test that whitespace-only string returns None."""
        result = extract_datetime("   \n\t  ")
        assert result is None

    def test_extract_datetime_with_invalid_polish_date(self):
        """Test that invalid Polish date format returns None."""
        result = extract_datetime("Invalid date: 32.13.2025")
        assert result is None

    def test_extract_datetime_with_invalid_iso_date(self):
        """Test that invalid ISO date format returns None."""
        result = extract_datetime("Invalid date: 2025-13-32")
        assert result is None

    def test_extract_datetime_with_partial_date_formats(self):
        """Test that partial date formats don't match."""
        test_cases = [
            "1.3.25",  # Too short
            "2025-3-15",  # Missing zero padding
            "15/03/2025",  # Wrong separator
            "15-03-2025",  # Wrong format
        ]
        for case in test_cases:
            result = extract_datetime(case)
            assert result is None, f"Expected None for '{case}' but got {result}"

    def test_extract_datetime_patterns_have_correct_format(self):
        """Test that all patterns in DATETIME_PATTERNS are properly structured."""
        assert len(DATETIME_PATTERNS) == 3

        # Check that each pattern is a tuple with regex and format string
        for pattern, date_format in DATETIME_PATTERNS:
            assert hasattr(pattern, "search"), "Pattern should be a compiled regex"
            assert isinstance(date_format, str), "Date format should be a string"
            assert "%" in date_format, "Date format should contain format specifiers"

    def test_extract_datetime_with_surrounding_text(self):
        """Test extraction works with various surrounding text."""
        test_cases = [
            ("Dokument z dnia 25.12.2024 został opublikowany", datetime(2024, 12, 25)),
            ("Ostatnia aktualizacja: 2024-12-25", datetime(2024, 12, 25)),
            # Due to pattern priority, date pattern matches before datetime pattern
            ("Timestamp: 2024-12-25 09:30 - please review", datetime(2024, 12, 25)),
            ("25.12.2024", datetime(2024, 12, 25)),  # Date only
            ("2024-12-25", datetime(2024, 12, 25)),  # Date only
        ]

        for text, expected in test_cases:
            result = extract_datetime(text)
            assert result == expected, f"Failed for text: '{text}'"

    def test_extract_datetime_with_edge_date_values(self):
        """Test extraction with edge date values."""
        test_cases = [
            ("01.01.2000", datetime(2000, 1, 1)),  # Y2K
            ("31.12.2099", datetime(2099, 12, 31)),  # Far future
            ("29.02.2024", datetime(2024, 2, 29)),  # Leap year
        ]

        for text, expected in test_cases:
            result = extract_datetime(text)
            assert result == expected, f"Failed for text: '{text}'"

    def test_extract_datetime_with_leap_year_validation(self):
        """Test that invalid leap year dates return None."""
        # 2023 is not a leap year
        result = extract_datetime("29.02.2023")
        assert result is None

    def test_extract_datetime_priority_order(self):
        """Test that patterns are matched in priority order."""
        # This text contains both Polish and ISO formats
        # Should match the first pattern (Polish format)
        text = "Date: 15.03.2025 (ISO: 2025-03-16)"
        result = extract_datetime(text)
        expected = datetime(2025, 3, 15)  # Should get the Polish date, not ISO
        assert result == expected
