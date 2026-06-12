"""Integration tests for ML/NLP agents."""

import pytest
from src.agents.content_analyzer import ContentAnalyzerAgent
from src.agents.bias_detector import BiasDetectorAgent
from src.agents.bot_detector import BotDetectorAgent


class TestAgentIntegration:
    """Test integration of all ML/NLP agents."""

    @pytest.fixture
    def agents(self):
        """Create all agent instances."""
        return {
            "content_analyzer": ContentAnalyzerAgent(),
            "bias_detector": BiasDetectorAgent(),
            "bot_detector": BotDetectorAgent(),
        }

    @pytest.fixture
    def complete_instagram_data(self):
        """Create complete Instagram data with all required fields."""
        return {
            "post_id": "12345",
            "caption": "Check out this amazing new political perspective! #trending #politics",
            "hashtags": ["#trending", "#politics", "#trending"],
            "comments": [
                {"text": "Great post!", "author": "user1", "timestamp": "2024-06-12T10:15:00"},
                {"text": "I agree totally", "author": "user2", "timestamp": "2024-06-12T10:20:00"},
                {"text": "Great post!", "author": "user3", "timestamp": "2024-06-12T10:25:00"},
            ],
            "posting_time": "2024-06-12T14:30:00",
            "engagement": {
                "likes": 1500,
                "comments": 45,
                "shares": 120,
                "engagement_rate": 0.08,
            },
            "likes_history": [
                {"timestamp": "2024-06-12T14:30:00", "count": 100},
                {"timestamp": "2024-06-12T15:30:00", "count": 300},
                {"timestamp": "2024-06-12T16:30:00", "count": 800},
                {"timestamp": "2024-06-12T17:30:00", "count": 1500},
            ],
            "follower_data": {
                "daily_growth": [10, 15, 12, 18, 14, 16, 13]
            },
            "engagement_timing": [
                {"timestamp": "2024-06-12T14:45:00"},
                {"timestamp": "2024-06-12T15:15:00"},
                {"timestamp": "2024-06-12T15:50:00"},
                {"timestamp": "2024-06-12T16:30:00"},
            ]
        }

    def test_all_agents_run_successfully(self, agents, complete_instagram_data):
        """Test that all agents can run successfully."""
        # Content Analyzer
        content_result = agents["content_analyzer"].run({
            "caption": complete_instagram_data["caption"],
            "hashtags": complete_instagram_data["hashtags"],
            "comments": [c["text"] for c in complete_instagram_data["comments"]],
            "posting_time": complete_instagram_data["posting_time"],
            "engagement": complete_instagram_data["engagement"],
        })
        assert content_result["status"] == "success"

        # Bias Detector
        bias_result = agents["bias_detector"].run({
            "text": complete_instagram_data["caption"],
            "comments": [c["text"] for c in complete_instagram_data["comments"]],
        })
        assert bias_result["status"] == "success"

        # Bot Detector
        bot_result = agents["bot_detector"].run({
            "comments": complete_instagram_data["comments"],
            "likes_history": complete_instagram_data["likes_history"],
            "follower_data": complete_instagram_data["follower_data"],
            "engagement_timing": complete_instagram_data["engagement_timing"],
        })
        assert bot_result["status"] == "success"

    def test_output_format_compatibility(self, agents, complete_instagram_data):
        """Test that outputs are compatible for downstream processing."""
        # Content Analyzer output
        content_result = agents["content_analyzer"].run({
            "caption": complete_instagram_data["caption"],
            "hashtags": complete_instagram_data["hashtags"],
            "comments": [c["text"] for c in complete_instagram_data["comments"]],
            "posting_time": complete_instagram_data["posting_time"],
            "engagement": complete_instagram_data["engagement"],
        })

        # Verify structure
        assert isinstance(content_result["analysis"], dict)
        analysis = content_result["analysis"]
        assert "emotional_language" in analysis
        assert "narrative_themes" in analysis
        assert "hashtag_patterns" in analysis
        assert "engagement_metrics" in analysis

        # Bias Detector output
        bias_result = agents["bias_detector"].run({
            "text": complete_instagram_data["caption"],
            "comments": [c["text"] for c in complete_instagram_data["comments"]],
        })
        assert isinstance(bias_result["analysis"], dict)
        analysis = bias_result["analysis"]
        assert "political_bias" in analysis
        assert "gender_bias" in analysis
        assert "toxicity_score" in analysis
        assert "overall_bias_score" in analysis

        # Bot Detector output
        bot_result = agents["bot_detector"].run({
            "comments": complete_instagram_data["comments"],
            "likes_history": complete_instagram_data["likes_history"],
            "follower_data": complete_instagram_data["follower_data"],
            "engagement_timing": complete_instagram_data["engagement_timing"],
        })
        assert isinstance(bot_result["analysis"], dict)
        analysis = bot_result["analysis"]
        assert "bot_activity_score" in analysis
        assert "engagement_velocity" in analysis
        assert "comment_authenticity" in analysis

    def test_agents_with_suspicious_content(self, agents):
        """Test agents with suspicious content."""
        suspicious_data = {
            "caption": "Fake news alert! Don't believe liberals! #conspiracy",
            "hashtags": ["#conspiracy", "#fakenews"],
            "comments": [
                {"text": "Follow me!", "author": "bot1", "timestamp": "2024-06-12T10:00:00"},
                {"text": "Follow me!", "author": "bot2", "timestamp": "2024-06-12T10:05:00"},
                {"text": "Follow me!", "author": "bot3", "timestamp": "2024-06-12T10:10:00"},
            ],
            "posting_time": "2024-06-12T14:30:00",
            "engagement": {"likes": 5000, "comments": 500, "shares": 200, "engagement_rate": 0.25},
            "likes_history": [
                {"count": 100},
                {"count": 500},
                {"count": 1000},
                {"count": 5000},
            ],
            "follower_data": {"daily_growth": [10, 500, 1000, 500, 10]},
            "engagement_timing": [
                {"timestamp": "2024-06-12T14:30:00"},
                {"timestamp": "2024-06-12T14:31:00"},
                {"timestamp": "2024-06-12T14:32:00"},
            ]
        }

        # Content Analyzer should detect conspiracy theme
        content_result = agents["content_analyzer"].run({
            "caption": suspicious_data["caption"],
            "hashtags": suspicious_data["hashtags"],
            "comments": [c["text"] for c in suspicious_data["comments"]],
            "posting_time": suspicious_data["posting_time"],
            "engagement": suspicious_data["engagement"],
        })
        assert "conspiracy" in content_result["analysis"]["narrative_themes"]

        # Bias Detector should detect political bias
        bias_result = agents["bias_detector"].run({
            "text": suspicious_data["caption"],
            "comments": [c["text"] for c in suspicious_data["comments"]],
        })
        assert bias_result["analysis"]["overall_bias_score"] > 0

        # Bot Detector should flag bot activity
        bot_result = agents["bot_detector"].run({
            "comments": suspicious_data["comments"],
            "likes_history": suspicious_data["likes_history"],
            "follower_data": suspicious_data["follower_data"],
            "engagement_timing": suspicious_data["engagement_timing"],
        })
        assert bot_result["analysis"]["bot_activity_score"] > 0.3

    def test_agents_with_legitimate_content(self, agents):
        """Test agents with legitimate content."""
        legitimate_data = {
            "caption": "Beautiful sunset at the beach today! Nature is amazing.",
            "hashtags": ["#sunset", "#nature", "#photography"],
            "comments": [
                {"text": "Beautiful photo!", "author": "user1", "timestamp": "2024-06-12T10:00:00"},
                {"text": "Love this!", "author": "user2", "timestamp": "2024-06-12T10:30:00"},
                {"text": "Great shot!", "author": "user3", "timestamp": "2024-06-12T11:00:00"},
            ],
            "posting_time": "2024-06-12T19:00:00",
            "engagement": {"likes": 500, "comments": 30, "shares": 10, "engagement_rate": 0.04},
            "likes_history": [
                {"count": 50},
                {"count": 150},
                {"count": 300},
                {"count": 500},
            ],
            "follower_data": {"daily_growth": [5, 8, 10, 12, 15, 18, 20]},
            "engagement_timing": [
                {"timestamp": "2024-06-12T19:15:00"},
                {"timestamp": "2024-06-12T19:45:00"},
                {"timestamp": "2024-06-12T20:30:00"},
                {"timestamp": "2024-06-12T21:00:00"},
            ]
        }

        # Content Analyzer should find lifestyle theme
        content_result = agents["content_analyzer"].run({
            "caption": legitimate_data["caption"],
            "hashtags": legitimate_data["hashtags"],
            "comments": [c["text"] for c in legitimate_data["comments"]],
            "posting_time": legitimate_data["posting_time"],
            "engagement": legitimate_data["engagement"],
        })
        assert "lifestyle" in content_result["analysis"]["narrative_themes"] or \
               content_result["analysis"]["emotional_language"]["sentiment"]["polarity"] > 0

        # Bias Detector should find lower bias than suspicious content
        bias_result = agents["bias_detector"].run({
            "text": legitimate_data["caption"],
            "comments": [c["text"] for c in legitimate_data["comments"]],
        })
        assert bias_result["analysis"]["overall_bias_score"] < 0.6

        # Bot Detector should find lower bot activity than suspicious content
        bot_result = agents["bot_detector"].run({
            "comments": legitimate_data["comments"],
            "likes_history": legitimate_data["likes_history"],
            "follower_data": legitimate_data["follower_data"],
            "engagement_timing": legitimate_data["engagement_timing"],
        })
        # Legitimate content should have lower bot score than high engagement content
        assert bot_result["analysis"]["bot_activity_score"] < 0.5

    def test_agents_error_recovery(self, agents):
        """Test that agents handle errors gracefully."""
        # Test with minimal/empty data
        minimal_data = {
            "caption": "",
            "hashtags": [],
            "comments": [],
            "posting_time": None,
            "engagement": {},
        }

        content_result = agents["content_analyzer"].run(minimal_data)
        assert content_result["status"] == "success"

        # Test with invalid input
        invalid_bias_data = {"text": ""}
        bias_result = agents["bias_detector"].run(invalid_bias_data)
        assert bias_result["status"] == "success"

        # Test with no engagement data
        empty_bot_data = {
            "comments": [],
            "likes_history": [],
            "follower_data": {},
            "engagement_timing": [],
        }
        bot_result = agents["bot_detector"].run(empty_bot_data)
        # Should still return valid result even with empty data
        assert "status" in bot_result


class TestAgentDataPipeline:
    """Test data flowing through agent pipeline."""

    def test_end_to_end_pipeline(self):
        """Test complete pipeline from Instagram data to analysis."""
        # Simulate data coming from Instagram API
        raw_data = {
            "post_id": "instagram_12345",
            "caption": "Breaking: New climate policy announced! #environment #politics",
            "hashtags": ["#environment", "#politics", "#news"],
            "comments": [
                {"text": "Finally!", "author": "user1", "timestamp": "2024-06-12T10:00:00"},
                {"text": "About time", "author": "user2", "timestamp": "2024-06-12T10:15:00"},
            ],
            "posting_time": "2024-06-12T14:30:00",
            "likes": 2000,
            "comments_count": 45,
            "shares": 150,
        }

        # Process through Content Analyzer
        content_agent = ContentAnalyzerAgent()
        content_analysis = content_agent.run({
            "caption": raw_data["caption"],
            "hashtags": raw_data["hashtags"],
            "comments": [c["text"] for c in raw_data["comments"]],
            "posting_time": raw_data["posting_time"],
            "engagement": {
                "likes": raw_data["likes"],
                "comments": raw_data["comments_count"],
                "shares": raw_data["shares"],
                "engagement_rate": (raw_data["likes"] + raw_data["comments_count"]) / 10000,
            }
        })

        # Process through Bias Detector
        bias_agent = BiasDetectorAgent()
        bias_analysis = bias_agent.run({
            "text": raw_data["caption"],
            "comments": [c["text"] for c in raw_data["comments"]],
        })

        # Process through Bot Detector (would need engagement timing in real scenario)
        bot_agent = BotDetectorAgent()
        bot_analysis = bot_agent.run({
            "comments": raw_data["comments"],
            "likes_history": [{"count": raw_data["likes"]}],
        })

        # Verify all analyses completed
        assert content_analysis["status"] == "success"
        assert bias_analysis["status"] == "success"
        assert bot_analysis["status"] == "success"

        # Combine results (as Synthesis Agent would)
        combined_analysis = {
            "post_id": raw_data["post_id"],
            "content_analysis": content_analysis["analysis"],
            "bias_analysis": bias_analysis["analysis"],
            "bot_analysis": bot_analysis["analysis"],
        }

        # Verify combined structure
        assert "narrative_themes" in combined_analysis["content_analysis"]
        assert "overall_bias_score" in combined_analysis["bias_analysis"]
        assert "bot_activity_score" in combined_analysis["bot_analysis"]
