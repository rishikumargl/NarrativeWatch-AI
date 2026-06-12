"""Unit tests for BotDetectorAgent."""

import pytest
from datetime import datetime, timedelta
from src.agents.bot_detector import BotDetectorAgent


class TestBotDetectorAgent:
    """Test BotDetectorAgent class."""

    @pytest.fixture
    def agent(self):
        """Create BotDetectorAgent instance."""
        return BotDetectorAgent()

    @pytest.fixture
    def sample_engagement_data(self):
        """Create sample engagement data."""
        return {
            "comments": [
                {"text": "Great post!", "author": "user1"},
                {"text": "Amazing content", "author": "user2"},
                {"text": "Great post!", "author": "user3"},  # Repeated
                {"text": "Love this", "author": "user4"},
            ],
            "likes_history": [
                {"timestamp": "2024-06-12T10:00:00", "count": 100},
                {"timestamp": "2024-06-12T11:00:00", "count": 200},
                {"timestamp": "2024-06-12T12:00:00", "count": 250},
                {"timestamp": "2024-06-12T13:00:00", "count": 260},
            ],
            "follower_data": {
                "daily_growth": [10, 15, 12, 18, 14, 16, 13]
            },
            "engagement_timing": [
                {"timestamp": "2024-06-12T10:15:00"},
                {"timestamp": "2024-06-12T11:20:00"},
                {"timestamp": "2024-06-12T12:25:00"},
                {"timestamp": "2024-06-12T13:30:00"},
            ]
        }

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "Bot Detector"

    def test_validate_input_valid_comments(self, agent):
        """Test input validation with comments."""
        data = {"comments": [{"text": "test"}]}
        assert agent.validate_input(data) is True

    def test_validate_input_valid_likes(self, agent):
        """Test input validation with likes_history."""
        data = {"likes_history": [{"count": 100}]}
        assert agent.validate_input(data) is True

    def test_validate_input_valid_followers(self, agent):
        """Test input validation with follower_data."""
        data = {"follower_data": {"daily_growth": [10, 20]}}
        assert agent.validate_input(data) is True

    def test_validate_input_invalid(self, agent):
        """Test input validation with invalid data."""
        assert agent.validate_input({}) is False
        assert agent.validate_input("invalid") is False
        assert agent.validate_input(None) is False

    def test_run_success(self, agent, sample_engagement_data):
        """Test successful analysis run."""
        result = agent.run(sample_engagement_data)
        assert result["status"] == "success"
        assert "analysis" in result
        assert "timestamp" in result

    def test_bot_activity_score(self, agent, sample_engagement_data):
        """Test bot activity score calculation."""
        result = agent.run(sample_engagement_data)
        analysis = result["analysis"]
        assert "bot_activity_score" in analysis
        assert 0 <= analysis["bot_activity_score"] <= 1

    def test_risk_level_determination(self, agent, sample_engagement_data):
        """Test risk level determination."""
        result = agent.run(sample_engagement_data)
        risk_level = result["analysis"]["risk_level"]
        assert risk_level in ["low", "medium", "high", "critical"]

    def test_engagement_velocity_analysis(self, agent, sample_engagement_data):
        """Test engagement velocity analysis."""
        result = agent.run(sample_engagement_data)
        velocity = result["analysis"]["engagement_velocity"]

        assert "anomaly_detected" in velocity
        assert "z_score" in velocity
        assert "anomaly_score" in velocity
        assert "description" in velocity

    def test_velocity_normal_pattern(self, agent):
        """Test velocity analysis with normal pattern."""
        data = {
            "likes_history": [
                {"count": 100},
                {"count": 110},
                {"count": 120},
                {"count": 130},
            ]
        }
        result = agent.run(data)
        velocity = result["analysis"]["engagement_velocity"]
        # Normal linear growth should have low anomaly score
        assert velocity["anomaly_score"] < 0.5

    def test_velocity_spike_detection(self, agent):
        """Test velocity analysis with spike."""
        data = {
            "likes_history": [
                {"count": 100},
                {"count": 110},
                {"count": 120},
                {"count": 500},  # Spike
            ]
        }
        result = agent.run(data)
        velocity = result["analysis"]["engagement_velocity"]
        # Spike should be detected with reasonable anomaly score
        assert velocity["anomaly_score"] > 0.2

    def test_comment_authenticity_analysis(self, agent, sample_engagement_data):
        """Test comment authenticity analysis."""
        result = agent.run(sample_engagement_data)
        comments = result["analysis"]["comment_authenticity"]

        assert "bot_likelihood" in comments
        assert "repetition_percentage" in comments
        assert "suspicion_level" in comments
        assert "indicators" in comments
        assert 0 <= comments["bot_likelihood"] <= 1

    def test_comment_repetition_detection(self, agent):
        """Test detection of repeated comments."""
        data = {
            "comments": [
                {"text": "Great post!"},
                {"text": "Great post!"},
                {"text": "Great post!"},
                {"text": "Great post!"},
                {"text": "Different comment"},
            ]
        }
        result = agent.run(data)
        comments = result["analysis"]["comment_authenticity"]
        assert comments["repetition_percentage"] > 0.5
        assert comments["suspicion_level"] == "critical"

    def test_follower_anomalies_detection(self, agent, sample_engagement_data):
        """Test follower anomaly detection."""
        result = agent.run(sample_engagement_data)
        followers = result["analysis"]["follower_anomalies"]

        assert "growth_anomaly" in followers
        assert "anomaly_score" in followers
        assert "avg_daily_growth" in followers

    def test_unusual_follower_growth(self, agent):
        """Test detection of unusual follower growth."""
        data = {
            "follower_data": {
                "daily_growth": [10, 15, 5000, 12, 10]  # Spike
            }
        }
        result = agent.run(data)
        followers = result["analysis"]["follower_anomalies"]
        assert "suspicious_patterns" in followers
        assert len(followers["suspicious_patterns"]) > 0

    def test_timing_patterns_analysis(self, agent, sample_engagement_data):
        """Test timing pattern analysis."""
        result = agent.run(sample_engagement_data)
        timing = result["analysis"]["timing_patterns"]

        assert "pattern_score" in timing
        assert "coordination_detected" in timing
        assert "timing_regularity" in timing
        assert 0 <= timing["pattern_score"] <= 1

    def test_regular_timing_detection(self, agent):
        """Test detection of regular timing patterns."""
        base_time = datetime(2024, 6, 12, 10, 0, 0)
        timing_data = {
            "engagement_timing": [
                {"timestamp": (base_time + timedelta(hours=i)).isoformat()}
                for i in range(10)
            ]
        }
        result = agent.run(timing_data)
        timing = result["analysis"]["timing_patterns"]
        # Regular hourly pattern should have high regularity
        assert timing["timing_regularity"] > 0.5

    def test_bot_indicators_extraction(self, agent):
        """Test bot indicator extraction."""
        data = {
            "comments": [
                {"text": "Follow me!"},
                {"text": "Check link in bio"},
            ],
            "likes_history": [
                {"count": 100},
                {"count": 500},
                {"count": 100},
                {"count": 900},
            ],
            "follower_data": {
                "daily_growth": [10, 5000, 20, 10]
            },
            "engagement_timing": [
                {"timestamp": "2024-06-12T10:00:00"},
            ] * 20
        }
        result = agent.run(data)
        indicators = result["analysis"]["bot_indicators"]
        assert len(indicators) > 0
        assert all(isinstance(ind, str) for ind in indicators)


class TestBotDetectorEdgeCases:
    """Test edge cases for BotDetectorAgent."""

    @pytest.fixture
    def agent(self):
        """Create BotDetectorAgent instance."""
        return BotDetectorAgent()

    def test_empty_comments(self, agent):
        """Test with empty comments list."""
        data = {
            "comments": [],
            "likes_history": [{"count": 100}, {"count": 120}],
        }
        result = agent.run(data)
        assert result["status"] == "success"

    def test_single_engagement_point(self, agent):
        """Test with single engagement data point."""
        data = {
            "likes_history": [{"count": 100}],
        }
        result = agent.run(data)
        assert result["status"] == "success"

    def test_empty_follower_data(self, agent):
        """Test with empty follower data but other data present."""
        data = {
            "comments": [{"text": "test"}],
            "likes_history": [{"count": 100}],
            "follower_data": {},
        }
        result = agent.run(data)
        assert result["status"] == "success"

    def test_invalid_timestamps(self, agent):
        """Test with invalid timestamps."""
        data = {
            "engagement_timing": [
                {"timestamp": "invalid-date"},
                {"timestamp": "also-invalid"},
            ]
        }
        result = agent.run(data)
        # Should handle gracefully
        assert result["status"] == "success"

    def test_very_large_engagement(self, agent):
        """Test with very large engagement numbers."""
        data = {
            "likes_history": [
                {"count": 1000000},
                {"count": 2000000},
                {"count": 3000000},
            ]
        }
        result = agent.run(data)
        assert result["status"] == "success"

    def test_many_comments(self, agent):
        """Test with many comments."""
        data = {
            "comments": [
                {"text": f"Comment {i}"}
                for i in range(10000)
            ]
        }
        result = agent.run(data)
        assert result["status"] == "success"

    def test_unicode_comments(self, agent):
        """Test with unicode in comments."""
        data = {
            "comments": [
                {"text": "Hello 世界"},
                {"text": "مرحبا العالم"},
                {"text": "Привет мир"},
            ]
        }
        result = agent.run(data)
        assert result["status"] == "success"
