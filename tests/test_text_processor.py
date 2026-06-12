"""Unit tests for TextProcessor utility."""

import pytest
from src.utils.text_processor import TextProcessor


class TestTextProcessor:
    """Test TextProcessor class."""

    @pytest.fixture
    def processor(self):
        """Create TextProcessor instance."""
        return TextProcessor()

    def test_tokenize_basic(self, processor):
        """Test basic tokenization."""
        text = "Hello world! This is a test."
        tokens = processor.tokenize(text)
        assert len(tokens) > 0
        assert "hello" in tokens
        assert "world" in tokens

    def test_tokenize_empty(self, processor):
        """Test tokenization of empty string."""
        tokens = processor.tokenize("")
        assert tokens == []

    def test_remove_stopwords(self, processor):
        """Test stopword removal."""
        tokens = ["the", "quick", "brown", "fox", "is", "jumping"]
        filtered = processor.remove_stopwords(tokens)
        assert "quick" in filtered
        assert "the" not in filtered
        assert "is" not in filtered

    def test_lemmatize(self, processor):
        """Test lemmatization."""
        tokens = ["running", "walked", "plays"]
        lemmatized = processor.lemmatize(tokens)
        assert len(lemmatized) == 3
        assert all(isinstance(token, str) for token in lemmatized)

    def test_extract_hashtags(self, processor):
        """Test hashtag extraction."""
        text = "Check out #trending #politics and #climate"
        hashtags = processor.extract_hashtags(text)
        assert "#trending" in hashtags
        assert "#politics" in hashtags
        assert "#climate" in hashtags
        assert len(hashtags) == 3

    def test_extract_hashtags_no_hashtags(self, processor):
        """Test hashtag extraction with no hashtags."""
        text = "This text has no hashtags"
        hashtags = processor.extract_hashtags(text)
        assert hashtags == []

    def test_extract_mentions(self, processor):
        """Test mention extraction."""
        text = "Hi @john and @jane, check this out"
        mentions = processor.extract_mentions(text)
        assert "@john" in mentions
        assert "@jane" in mentions
        assert len(mentions) == 2

    def test_extract_urls(self, processor):
        """Test URL extraction."""
        text = "Visit https://example.com and http://test.org for more info"
        urls = processor.extract_urls(text)
        assert len(urls) == 2
        assert any("example.com" in url for url in urls)

    def test_calculate_sentiment_positive(self, processor):
        """Test sentiment calculation for positive text."""
        text = "This is amazing! I love it so much!"
        sentiment = processor.calculate_sentiment(text)
        assert sentiment > 0

    def test_calculate_sentiment_negative(self, processor):
        """Test sentiment calculation for negative text."""
        text = "This is terrible and awful. I hate it."
        sentiment = processor.calculate_sentiment(text)
        assert sentiment < 0

    def test_calculate_sentiment_neutral(self, processor):
        """Test sentiment calculation for neutral text."""
        text = "The sky is blue."
        sentiment = processor.calculate_sentiment(text)
        assert abs(sentiment) < 0.3

    def test_calculate_subjectivity(self, processor):
        """Test subjectivity calculation."""
        text = "I think this is the best thing ever"
        subjectivity = processor.calculate_subjectivity(text)
        assert 0 <= subjectivity <= 1

    def test_analyze_emotional_intensity(self, processor):
        """Test emotional intensity analysis."""
        text = "This is amazing!! I love this incredible stuff!!!"
        intensity = processor.analyze_emotional_intensity(text)
        assert "excitement" in intensity
        assert "anger" in intensity
        assert "sadness" in intensity
        assert all(0 <= v <= 1 for v in intensity.values())

    def test_count_language_features(self, processor):
        """Test language feature counting."""
        text = "This is a sentence. This is another. And a third!"
        features = processor.count_language_features(text)
        assert features["sentences"] == 3
        assert features["words"] > 0
        assert "characters" in features

    def test_extract_patterns(self, processor):
        """Test pattern extraction."""
        text = "Check #trending @john https://example.com"
        patterns = processor.extract_patterns(text)
        assert "hashtags" in patterns
        assert "mentions" in patterns
        assert "urls" in patterns
        assert "language_features" in patterns
        assert "sentiment" in patterns

    def test_clean_text(self, processor):
        """Test text cleaning."""
        text = "Hello   WORLD  https://example.com  !!"
        cleaned = processor.clean_text(text, lowercase=True, remove_urls=True)
        assert "hello" in cleaned
        assert "example.com" not in cleaned
        assert "  " not in cleaned

    def test_detect_language(self, processor):
        """Test language detection."""
        text = "This is English text"
        lang = processor.detect_language(text)
        assert lang == "en"

    def test_get_word_frequency(self, processor):
        """Test word frequency calculation."""
        text = "the cat sat on the mat and the cat was happy"
        freq = processor.get_word_frequency(text, top_n=5)
        assert isinstance(freq, dict)
        assert len(freq) <= 5

    def test_analyze_readability(self, processor):
        """Test readability analysis."""
        text = "This is a test. Another sentence. And a third."
        readability = processor.analyze_readability(text)
        assert "avg_word_length" in readability
        assert "avg_sentence_length" in readability
        assert "complexity" in readability
        assert 0 <= readability["complexity"] <= 1


class TestTextProcessorEdgeCases:
    """Test edge cases for TextProcessor."""

    @pytest.fixture
    def processor(self):
        """Create TextProcessor instance."""
        return TextProcessor()

    def test_empty_input(self, processor):
        """Test with empty inputs."""
        assert processor.tokenize("") == []
        assert processor.extract_hashtags("") == []
        assert processor.calculate_sentiment("") == 0.0

    def test_special_characters(self, processor):
        """Test with special characters."""
        text = "Hello!@#$%^&*()"
        tokens = processor.tokenize(text)
        assert len(tokens) > 0

    def test_mixed_case(self, processor):
        """Test with mixed case text."""
        text = "HeLLo WoRLd"
        tokens = processor.tokenize(text)
        assert "hello" in tokens
        assert "world" in tokens

    def test_very_long_text(self, processor):
        """Test with very long text."""
        text = "word " * 10000
        tokens = processor.tokenize(text)
        assert len(tokens) > 0
        sentiment = processor.calculate_sentiment(text)
        assert isinstance(sentiment, float)

    def test_unicode_text(self, processor):
        """Test with unicode text."""
        text = "Hello 世界 مرحبا мир"
        hashtags = processor.extract_hashtags(text)
        assert isinstance(hashtags, list)

    def test_consecutive_special_chars(self, processor):
        """Test with consecutive special characters."""
        text = "This is!!! amazing?? wonderful!!!"
        sentiment = processor.calculate_sentiment(text)
        assert isinstance(sentiment, float)
