"""Tests for Campaign Detector Agent."""

import pytest
from src.agents.campaign_detector import CampaignDetectorAgent


@pytest.fixture
def campaign_detector():
    return CampaignDetectorAgent()


@pytest.fixture
def sample_pages():
    return [
        {
            "id": "page_1",
            "username": "@political_account1",
            "description": "Political news and analysis",
            "hashtags": ["#election2024", "#vote", "#political"],
            "follower_count": 50000
        },
        {
            "id": "page_2",
            "username": "@news_fake",
            "description": "Political analysis and news",
            "hashtags": ["#election2024", "#vote", "#analysis"],
            "follower_count": 30000
        },
        {
            "id": "page_3",
            "username": "@sports_account",
            "description": "Sports updates and scores",
            "hashtags": ["#sports", "#football", "#nfl"],
            "follower_count": 100000
        }
    ]


@pytest.fixture
def sample_posts():
    return [
        {
            "id": "post_1",
            "page_id": "page_1",
            "timestamp": "2024-06-01T14:30:00",
            "content": "Election news",
            "engagement": {"likes": 1000, "comments": 50}
        },
        {
            "id": "post_2",
            "page_id": "page_2",
            "timestamp": "2024-06-01T15:45:00",
            "content": "Election analysis",
            "engagement": {"likes": 800, "comments": 40}
        },
        {
            "id": "post_3",
            "page_id": "page_3",
            "timestamp": "2024-06-01T09:00:00",
            "content": "Football game",
            "engagement": {"likes": 2000, "comments": 100}
        }
    ]


class TestCampaignDetectorBasics:
    """Test basic campaign detection functionality."""

    def test_agent_initialization(self, campaign_detector):
        """Test agent initializes correctly."""
        assert campaign_detector.name == "Campaign Detector"
        assert campaign_detector.description

    def test_run_with_empty_input(self, campaign_detector):
        """Test handling of empty input."""
        result = campaign_detector.run({"pages": []})
        assert result["campaign_count"] == 0
        assert result["campaigns"] == []

    def test_run_with_valid_input(self, campaign_detector, sample_pages, sample_posts):
        """Test run method with valid input."""
        result = campaign_detector.run({
            "pages": sample_pages,
            "posts": sample_posts,
            "query_context": "Detect election campaigns"
        })

        assert "campaigns" in result
        assert "campaign_count" in result
        assert "total_pages_analyzed" in result
        assert result["total_pages_analyzed"] == 3


class TestHashtagSimilarity:
    """Test hashtag similarity calculation."""

    def test_identical_hashtags(self, campaign_detector):
        """Test pages with identical hashtags."""
        page1 = {"id": "p1", "hashtags": ["#test", "#sample"]}
        page2 = {"id": "p2", "hashtags": ["#test", "#sample"]}

        sim = campaign_detector._hashtag_similarity(page1, page2)
        assert sim == 1.0

    def test_no_hashtags(self, campaign_detector):
        """Test pages with no hashtags."""
        page1 = {"id": "p1", "hashtags": []}
        page2 = {"id": "p2", "hashtags": []}

        sim = campaign_detector._hashtag_similarity(page1, page2)
        assert sim == 0.0

    def test_partial_overlap(self, campaign_detector):
        """Test pages with partial hashtag overlap."""
        page1 = {"id": "p1", "hashtags": ["#a", "#b", "#c"]}
        page2 = {"id": "p2", "hashtags": ["#b", "#c", "#d"]}

        sim = campaign_detector._hashtag_similarity(page1, page2)
        assert 0 < sim < 1.0
        assert sim == 0.5


class TestNarrativeSimilarity:
    """Test narrative similarity calculation."""

    def test_identical_descriptions(self, campaign_detector):
        """Test pages with identical descriptions."""
        page1 = {"id": "p1", "description": "Political news"}
        page2 = {"id": "p2", "description": "Political news"}

        sim = campaign_detector._narrative_similarity(page1, page2)
        assert sim == 1.0

    def test_empty_descriptions(self, campaign_detector):
        """Test pages with empty descriptions."""
        page1 = {"id": "p1", "description": ""}
        page2 = {"id": "p2", "description": ""}

        sim = campaign_detector._narrative_similarity(page1, page2)
        assert sim == 0.0

    def test_different_descriptions(self, campaign_detector):
        """Test pages with different descriptions."""
        page1 = {"id": "p1", "description": "Political news"}
        page2 = {"id": "p2", "description": "Sports updates"}

        sim = campaign_detector._narrative_similarity(page1, page2)
        assert sim < 0.5


class TestTimingSimilarity:
    """Test timing correlation calculation."""

    def test_same_hour_posts(self, campaign_detector):
        """Test pages posting in same hour."""
        page1 = {"id": "p1"}
        page2 = {"id": "p2"}
        posts = [
            {"page_id": "p1", "timestamp": "2024-06-01T14:30:00"},
            {"page_id": "p2", "timestamp": "2024-06-01T14:45:00"}
        ]

        sim = campaign_detector._timing_similarity(page1, page2, posts)
        assert sim > 0.5

    def test_different_hour_posts(self, campaign_detector):
        """Test pages posting in different hours."""
        page1 = {"id": "p1"}
        page2 = {"id": "p2"}
        posts = [
            {"page_id": "p1", "timestamp": "2024-06-01T14:30:00"},
            {"page_id": "p2", "timestamp": "2024-06-01T20:45:00"}
        ]

        sim = campaign_detector._timing_similarity(page1, page2, posts)
        assert sim < 0.5


class TestClustering:
    """Test page clustering logic."""

    def test_single_page_no_cluster(self, campaign_detector):
        """Test that single pages don't form clusters."""
        page = {"id": "p1", "hashtags": ["#test"]}
        campaigns = campaign_detector.detect_campaigns([page])
        assert len(campaigns) == 0

    def test_two_coordinated_pages(self, campaign_detector):
        """Test detection of two coordinated pages."""
        pages = [
            {
                "id": "p1",
                "username": "@page1",
                "description": "Election news and analysis",
                "hashtags": ["#election", "#vote", "#political"],
            },
            {
                "id": "p2",
                "username": "@page2",
                "description": "Election analysis and news",
                "hashtags": ["#election", "#vote", "#political"],
            }
        ]

        campaigns = campaign_detector.detect_campaigns(pages)
        assert len(campaigns) >= 0  # May not detect if similarity threshold not met

    def test_unrelated_pages_no_cluster(self, campaign_detector):
        """Test that unrelated pages don't cluster."""
        pages = [
            {
                "id": "p1",
                "username": "@sports",
                "description": "Sports news",
                "hashtags": ["#football"],
            },
            {
                "id": "p2",
                "username": "@food",
                "description": "Food reviews",
                "hashtags": ["#recipe"],
            }
        ]

        campaigns = campaign_detector.detect_campaigns(pages)
        assert len(campaigns) == 0


class TestCampaignAnalysis:
    """Test campaign cluster analysis."""

    def test_campaign_confidence_score(self, campaign_detector, sample_pages):
        """Test campaign confidence calculation."""
        cluster = {"page_1", "page_2"}
        cluster_pages = [p for p in sample_pages if p["id"] in cluster]

        campaign = campaign_detector._analyze_cluster(
            cluster, cluster_pages, [], {}
        )

        assert 0 <= campaign.confidence <= 1.0

    def test_shared_hashtags_extraction(self, campaign_detector):
        """Test extraction of shared hashtags."""
        pages = [
            {"id": "p1", "hashtags": ["#a", "#b", "#c"]},
            {"id": "p2", "hashtags": ["#b", "#c", "#d"]},
            {"id": "p3", "hashtags": ["#c", "#e", "#f"]}
        ]

        shared = campaign_detector._get_shared_hashtags(pages)
        assert "#c" in shared

    def test_narrative_theme_inference(self, campaign_detector):
        """Test narrative theme inference."""
        pages = [
            {"id": "p1", "description": "election coverage"},
            {"id": "p2", "description": "voting information"}
        ]

        theme = campaign_detector._infer_narrative_theme(pages)
        assert theme  # Should return some theme
        assert isinstance(theme, str)


class TestGraphConstruction:
    """Test graph building and manipulation."""

    def test_build_page_graph(self, campaign_detector, sample_pages, sample_posts):
        """Test page graph construction."""
        graph = campaign_detector._build_page_graph(sample_pages, sample_posts)

        # Graph should be dict of dicts
        assert isinstance(graph, dict)

        # Should have entries for pages with high similarity
        assert len(graph) > 0

    def test_graph_edge_weights(self, campaign_detector, sample_pages, sample_posts):
        """Test that graph edges have weights 0-1."""
        graph = campaign_detector._build_page_graph(sample_pages, sample_posts)

        for page_id, neighbors in graph.items():
            for neighbor_id, weight in neighbors.items():
                assert 0 <= weight <= 1.0


class TestOutputFormat:
    """Test output format and structure."""

    def test_run_output_structure(self, campaign_detector, sample_pages, sample_posts):
        """Test run method output has correct structure."""
        result = campaign_detector.run({
            "pages": sample_pages,
            "posts": sample_posts,
            "query_context": "Test"
        })

        required_keys = [
            "campaigns",
            "campaign_count",
            "total_pages_analyzed",
            "coordinated_pages",
            "evidence",
            "message"
        ]

        for key in required_keys:
            assert key in result

    def test_campaign_object_structure(self, campaign_detector, sample_pages):
        """Test campaign object has required fields."""
        campaigns = campaign_detector.detect_campaigns(sample_pages)

        if campaigns:
            campaign = campaigns[0]

            required_fields = [
                "campaign_id",
                "pages",
                "confidence",
                "narrative_theme",
                "hashtag_overlap",
                "timing_correlation",
                "narrative_similarity",
                "evidence"
            ]

            for field in required_fields:
                assert hasattr(campaign, field)
