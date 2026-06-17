"""Text processing utilities for NarrativeWatch AI."""

import re
from typing import List, Dict, Tuple, Optional, Any
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
import logging

try:
    import spacy
except ImportError:
    spacy = None

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Load spaCy model
nlp = None
if spacy:
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
        nlp = None
else:
    logger.warning("spaCy not installed. Run: pip install spacy")


class TextProcessor:
    """Text processing utilities."""

    def __init__(self):
        """Initialize text processor."""
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.nlp = nlp

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        if not text:
            return []
        tokens = word_tokenize(text.lower())
        return tokens

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from token list."""
        return [token for token in tokens if token.lower() not in self.stop_words and token.isalpha()]

    def lemmatize(self, tokens: List[str]) -> List[str]:
        """Lemmatize tokens."""
        return [self.lemmatizer.lemmatize(token) for token in tokens]

    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        hashtags = re.findall(r'#\w+', text)
        return [tag.lower() for tag in hashtags]

    def extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text."""
        mentions = re.findall(r'@\w+', text)
        return [mention.lower() for mention in mentions]

    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)

    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy."""
        if not self.nlp:
            logger.warning("spaCy not loaded. Returning empty entities.")
            return {}

        doc = self.nlp(text)
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)

        return entities

    def calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment polarity using TextBlob (range: -1.0 to 1.0)."""
        if not text:
            return 0.0
        blob = TextBlob(text)
        return float(blob.sentiment.polarity)

    def calculate_subjectivity(self, text: str) -> float:
        """Calculate subjectivity using TextBlob (range: 0.0 to 1.0)."""
        if not text:
            return 0.0
        blob = TextBlob(text)
        return float(blob.sentiment.subjectivity)

    def analyze_emotional_intensity(self, text: str) -> Dict[str, float]:
        """Analyze emotional intensity markers in text."""
        emotional_markers = {
            'excitement': len(re.findall(r'[!]{2,}|very|amazing|incredible', text, re.IGNORECASE)),
            'anger': len(re.findall(r'[!]+|hate|angry|furious', text, re.IGNORECASE)),
            'sadness': len(re.findall(r'[:/]{1,}|sad|depressed|heartbroken', text, re.IGNORECASE)),
            'fear': len(re.findall(r'scared|afraid|terrified|panic', text, re.IGNORECASE)),
        }

        # Normalize by text length
        text_length = len(text.split())
        if text_length > 0:
            return {k: min(v / text_length, 1.0) for k, v in emotional_markers.items()}
        return {k: 0.0 for k in emotional_markers.keys()}

    def count_language_features(self, text: str) -> Dict[str, int]:
        """Count various language features."""
        sentences = sent_tokenize(text)
        tokens = self.tokenize(text)

        return {
            'sentences': len(sentences),
            'words': len(tokens),
            'characters': len(text),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            'punctuation_count': sum(1 for c in text if c in '!?.,;:'),
            'unique_words': len(set(tokens)),
        }

    def extract_patterns(self, text: str) -> Dict[str, Any]:
        """Extract various text patterns."""
        return {
            'hashtags': self.extract_hashtags(text),
            'mentions': self.extract_mentions(text),
            'urls': self.extract_urls(text),
            'named_entities': self.extract_named_entities(text),
            'language_features': self.count_language_features(text),
            'sentiment': self.calculate_sentiment(text),
            'subjectivity': self.calculate_subjectivity(text),
            'emotional_intensity': self.analyze_emotional_intensity(text),
        }

    def clean_text(self, text: str, lowercase: bool = True, remove_urls: bool = True) -> str:
        """Clean text by removing unwanted characters."""
        if remove_urls:
            text = re.sub(r'http[s]?://\S+', '', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        if lowercase:
            text = text.lower()

        return text

    def detect_language(self, text: str) -> str:
        """Detect language of text (uses TextBlob - returns 'en' for English)."""
        try:
            blob = TextBlob(text)
            return blob.detect_language()
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "en"

    def get_word_frequency(self, text: str, top_n: int = 10) -> Dict[str, int]:
        """Get most frequent words in text."""
        tokens = self.tokenize(text)
        tokens = self.remove_stopwords(tokens)
        tokens = self.lemmatize(tokens)

        from collections import Counter
        freq = Counter(tokens)
        return dict(freq.most_common(top_n))

    def analyze_readability(self, text: str) -> Dict[str, float]:
        """Analyze text readability metrics."""
        sentences = sent_tokenize(text)
        words = self.tokenize(text)

        if len(sentences) == 0 or len(words) == 0:
            return {'avg_word_length': 0, 'avg_sentence_length': 0, 'complexity': 0}

        avg_word_length = sum(len(w) for w in words) / len(words)
        avg_sentence_length = len(words) / len(sentences)

        # Simple complexity metric (0-1)
        complexity = min(avg_sentence_length / 20, 1.0)

        return {
            'avg_word_length': float(avg_word_length),
            'avg_sentence_length': float(avg_sentence_length),
            'complexity': float(complexity),
        }
