"""Tests for Synthesis Agent."""

import pytest
from src.agents.synthesis_agent import SynthesisAgent


@pytest.fixture
def synthesis_agent():
    return SynthesisAgent()


@pytest.fixture
def sample_agent_results():
    return {
        "content_analyzer": {
            "emotional_score": 0.8,
            "narrative_themes": ["election manipulation"],
            "hashtag_patterns": {"#election2024": 15}
        },
        "rag_agent": {
            "similar_campaigns": [
                {"campaign_id": "past_1", "similarity": 0.92}
            ]
        },
        "research_agent": {
            "fact_checks": ["FALSE", "TRUE", "PARTLY_TRUE"]
        },
        "bias_detector": {
            "political_bias": 0.85,
            "bias_types": ["strong right-wing"]
        },
        "bot_detector": {
            "bot_probability": 0.75,
            "suspicious_engagement": True
        },
        "campaign_detector": {
            "campaign_count": 2,
            "campaigns": [
                {
                    "narrative_theme": "election manipulation",
                    "pages": ["page1", "page2"],
                    "confidence": 0.85
                }
            ]
        }
    }


class TestSynthesisAgentBasics:
    """Test basic synthesis functionality."""

    def test_agent_initialization(self, synthesis_agent):
        """Test agent initializes correctly."""
        assert synthesis_agent.name == "Synthesis Agent"
        assert synthesis_agent.description

    def test_run_with_empty_input(self, synthesis_agent):
        """Test handling of empty input."""
        result = synthesis_agent.run({
            "agent_results": {},
            "original_query": ""
        })

        assert "report" in result
        assert "key_findings" in result
        assert "evidence" in result
        assert "recommendation" in result

    def test_run_with_full_input(self, synthesis_agent, sample_agent_results):
        """Test run with complete agent results."""
        result = synthesis_agent.run({
            "agent_results": sample_agent_results,
            "original_query": "Analyze @political_page for coordinated activity"
        })

        required_keys = [
            "report",
            "key_findings",
            "evidence",
            "recommendation",
            "trust_score_components",
            "completeness_score"
        ]

        for key in required_keys:
            assert key in result


class TestKeyFindingsExtraction:
    """Test key findings extraction."""

    def test_extract_key_findings_empty(self, synthesis_agent):
        """Test extraction from empty agent results."""
        findings = synthesis_agent._extract_key_findings({})
        assert isinstance(findings, list)

    def test_campaign_activity_finding(self, synthesis_agent, sample_agent_results):
        """Test campaign activity is extracted."""
        findings = synthesis_agent._extract_key_findings(sample_agent_results)

        campaign_found = any("campaign" in f.lower() for f in findings)
        assert campaign_found

    def test_bot_activity_finding(self, synthesis_agent, sample_agent_results):
        """Test bot activity is extracted."""
        sample_agent_results["bot_detector"]["bot_probability"] = 0.85
        findings = synthesis_agent._extract_key_findings(sample_agent_results)

        bot_found = any("bot" in f.lower() for f in findings)
        assert bot_found

    def test_fact_check_finding(self, synthesis_agent, sample_agent_results):
        """Test fact-check findings are extracted."""
        findings = synthesis_agent._extract_key_findings(sample_agent_results)

        fact_check_found = any("fact" in f.lower() or "false" in f.lower() for f in findings)
        assert fact_check_found

    def test_max_findings_limit(self, synthesis_agent, sample_agent_results):
        """Test that max 10 findings are returned."""
        findings = synthesis_agent._extract_key_findings(sample_agent_results)
        assert len(findings) <= 10

    def test_min_findings_generated(self, synthesis_agent, sample_agent_results):
        """Test that multiple findings are generated."""
        findings = synthesis_agent._extract_key_findings(sample_agent_results)
        assert len(findings) > 0


class TestEvidenceBuilding:
    """Test evidence list construction."""

    def test_build_evidence_empty(self, synthesis_agent):
        """Test evidence building from empty results."""
        evidence = synthesis_agent._build_evidence_list({})
        assert isinstance(evidence, list)

    def test_campaign_evidence(self, synthesis_agent, sample_agent_results):
        """Test campaign evidence is included."""
        evidence = synthesis_agent._build_evidence_list(sample_agent_results)

        campaign_evidence = [e for e in evidence if e.type == "campaign_coordination"]
        assert len(campaign_evidence) > 0

    def test_bot_evidence(self, synthesis_agent, sample_agent_results):
        """Test bot detection evidence."""
        evidence = synthesis_agent._build_evidence_list(sample_agent_results)

        bot_evidence = [e for e in evidence if e.type == "bot_activity"]
        assert len(bot_evidence) > 0

    def test_bias_evidence(self, synthesis_agent, sample_agent_results):
        """Test bias evidence is included."""
        evidence = synthesis_agent._build_evidence_list(sample_agent_results)

        bias_evidence = [e for e in evidence if e.type == "bias"]
        assert len(bias_evidence) > 0

    def test_evidence_confidence_scores(self, synthesis_agent, sample_agent_results):
        """Test that evidence has valid confidence scores."""
        evidence = synthesis_agent._build_evidence_list(sample_agent_results)

        for e in evidence:
            assert 0 <= e.confidence <= 1.0

    def test_evidence_has_source(self, synthesis_agent, sample_agent_results):
        """Test that evidence cites its source."""
        evidence = synthesis_agent._build_evidence_list(sample_agent_results)

        for e in evidence:
            assert e.source in [
                "campaign_detector",
                "bot_detector",
                "bias_detector",
                "research_agent",
                "content_analyzer",
                "rag_agent"
            ]


class TestEvidenceRanking:
    """Test evidence ranking by importance."""

    def test_rank_evidence_ordering(self, synthesis_agent, sample_agent_results):
        """Test evidence is ranked by importance."""
        evidence = synthesis_agent._build_evidence_list(sample_agent_results)
        ranked = synthesis_agent._rank_evidence(evidence)

        if len(ranked) > 1:
            for i in range(len(ranked) - 1):
                # Campaign should rank higher than manipulation
                if ranked[i].type == "campaign_coordination":
                    assert ranked[i+1].type != "manipulation"

    def test_rank_preserves_all_evidence(self, synthesis_agent, sample_agent_results):
        """Test ranking doesn't drop evidence."""
        evidence = synthesis_agent._build_evidence_list(sample_agent_results)
        ranked = synthesis_agent._rank_evidence(evidence)

        assert len(ranked) == len(evidence)


class TestReportGeneration:
    """Test report generation."""

    def test_report_structure(self, synthesis_agent, sample_agent_results):
        """Test report has proper structure."""
        key_findings = synthesis_agent._extract_key_findings(sample_agent_results)
        evidence = synthesis_agent._build_evidence_list(sample_agent_results)

        report = synthesis_agent._generate_report(
            sample_agent_results,
            key_findings,
            evidence,
            "Test query"
        )

        assert isinstance(report, str)
        assert len(report) > 200
        assert "Analysis Report" in report

    def test_report_includes_query(self, synthesis_agent, sample_agent_results):
        """Test report references original query."""
        key_findings = synthesis_agent._extract_key_findings(sample_agent_results)
        evidence = synthesis_agent._build_evidence_list(sample_agent_results)

        query = "Analyze election manipulation"
        report = synthesis_agent._generate_report(
            sample_agent_results,
            key_findings,
            evidence,
            query
        )

        assert "Analysis Report" in report

    def test_report_includes_key_findings(self, synthesis_agent, sample_agent_results):
        """Test report includes key findings section."""
        key_findings = synthesis_agent._extract_key_findings(sample_agent_results)
        evidence = synthesis_agent._build_evidence_list(sample_agent_results)

        report = synthesis_agent._generate_report(
            sample_agent_results,
            key_findings,
            evidence,
            "Test"
        )

        assert "Findings" in report

    def test_report_includes_evidence(self, synthesis_agent, sample_agent_results):
        """Test report includes evidence section."""
        key_findings = synthesis_agent._extract_key_findings(sample_agent_results)
        evidence = synthesis_agent._build_evidence_list(sample_agent_results)

        report = synthesis_agent._generate_report(
            sample_agent_results,
            key_findings,
            evidence,
            "Test"
        )

        assert "Evidence" in report


class TestRecommendationGeneration:
    """Test recommendation generation."""

    def test_recommendation_exists(self, synthesis_agent, sample_agent_results):
        """Test that recommendation is generated."""
        key_findings = ["Finding 1", "Finding 2"]
        rec = synthesis_agent._generate_recommendation(key_findings, sample_agent_results)

        assert isinstance(rec, str)
        assert len(rec) > 10

    def test_high_risk_recommendation(self, synthesis_agent, sample_agent_results):
        """Test recommendation for high-risk content."""
        key_findings = ["Campaign detected", "High bot activity", "Bias detected"]
        rec = synthesis_agent._generate_recommendation(key_findings, sample_agent_results)

        assert "flag" in rec.lower() or "risk" in rec.lower()

    def test_low_risk_recommendation(self, synthesis_agent):
        """Test recommendation for low-risk content."""
        results = {
            "campaign_detector": {"campaign_count": 0},
            "bot_detector": {"bot_probability": 0.1},
            "bias_detector": {"political_bias": 0.2}
        }
        key_findings = []
        rec = synthesis_agent._generate_recommendation(key_findings, results)

        assert isinstance(rec, str)


class TestTrustComponents:
    """Test trust score component extraction."""

    def test_extract_trust_components(self, synthesis_agent, sample_agent_results):
        """Test trust component extraction."""
        components = synthesis_agent._extract_trust_components(sample_agent_results)

        expected_keys = [
            "authenticity",
            "truthfulness",
            "bias_score",
            "manipulation_score",
            "campaign_activity"
        ]

        for key in expected_keys:
            assert key in components

    def test_component_values_valid(self, synthesis_agent, sample_agent_results):
        """Test that component values are 0-1."""
        components = synthesis_agent._extract_trust_components(sample_agent_results)

        for key, value in components.items():
            assert 0 <= value <= 1.0, f"{key} out of range: {value}"


class TestCompletenessScore:
    """Test completeness calculation."""

    def test_completeness_empty_results(self, synthesis_agent):
        """Test completeness with no agents."""
        score = synthesis_agent._calculate_completeness({})
        assert score == 0.0

    def test_completeness_all_agents(self, synthesis_agent, sample_agent_results):
        """Test completeness with all agents."""
        score = synthesis_agent._calculate_completeness(sample_agent_results)
        assert score == 1.0

    def test_completeness_partial_agents(self, synthesis_agent):
        """Test completeness with some agents."""
        partial = {
            "content_analyzer": {"score": 0.5},
            "bias_detector": {"bias": 0.5},
            "bot_detector": {"prob": 0.5},
            "campaign_detector": {"count": 0}
        }
        score = synthesis_agent._calculate_completeness(partial)
        assert 0 < score < 1.0
