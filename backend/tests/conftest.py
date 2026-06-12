"""Pytest configuration for NarrativeWatch AI tests."""

import sys
import os

# Add src to path so tests can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest


@pytest.fixture(scope="session")
def test_data():
    """Provide test data fixtures."""
    return {
        "sample_caption": "Check out this amazing new product! #trending #innovation",
        "sample_hashtags": ["#trending", "#innovation", "#future"],
        "sample_comments": [
            "This looks great!",
            "I love this",
            "Amazing product",
        ],
        "positive_text": "This is amazing! I love it so much!",
        "negative_text": "This is terrible and awful. I hate it.",
        "neutral_text": "The sky is blue.",
        "conservative_text": "We must protect our borders and traditional values",
        "liberal_text": "We need more social justice and equality for all",
    }


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
