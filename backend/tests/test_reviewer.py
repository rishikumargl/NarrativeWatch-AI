"""Tests for Reviewer Agent and Reflection Loop."""

import pytest
from src.agents.reviewer_agent import ReviewerAgent
from src.workflow.reflection_loop import ReflectionLoop


@pytest.fixture
def reviewer_agent():
    return ReviewerAgent()


@pytest.fixture
def synthesis_result():
    return {
        "report": "This account shows coordinated activity. The content demonstrates political bias, high bot engagement, and emotional manipulation across multiple related pages. Historical patterns match known campaign strategies.",
        "key_findings": [
            "Coordinated campaign detected across 2 pages",
            "75% bot activity",
            "Multiple false claims in content",
            "Strong political bias",
            "Emotional manipulation tactics"
        ],
        "evidence": [
            {
                "type": "campaign_coordination",
                "description": "Campaign with confidence 0.85",
                "confidence": 0.85,
                "source": "campaign_detector"
            },
            {
                "type": "bot_activity",
                "description": "Inauthentic engagement",
                "confidence": 0.75,
                "source": "bot_detector"
            }
        ],
        "recommendation": "Flag account for review",
        "original_query": "Analyze @political_account",
        "completeness_score": 0.9
    }


@pytest.fixture
def agent_results():
    return {
        "content_analyzer": {"emotional_score": 0.8},
        "rag_agent": {"similar_campaigns": [{}]},
        "research_agent": {"fact_checks": ["FALSE", "TRUE"]},
        "bias_detector": {"political_bias": 0.85},
        "bot_detector": {"bot_probability": 0.75},
        "campaign_detector": {"campaigns": [{}]}
    }


class TestReviewerAgentBasics:
    """Test basic reviewer functionality."""

    def test_agent_initialization(self, reviewer_agent):
        """Test agent initializes correctly."""
        assert reviewer_agent.name == "Reviewer Agent"
        assert reviewer_agent.description

    def test_run_with_valid_input(self, reviewer_agent, synthesis_result, agent_results):
        """Test run with valid synthesis result."""
        result = reviewer_agent.run({
            "synthesis_result": synthesis_result,
            "agent_results": agent_results
        })

        assert "status" in result
        assert "completeness_score" in result
        assert "accuracy_score" in result
        assert "clarity_score" in result
        assert "relevance_score" in result
        assert "approved" in result

    def test_status_approved_or_needs_revision(self, reviewer_agent, synthesis_result, agent_results):
        """Test that status is either APPROVED or NEEDS_REVISION."""
        result = reviewer_agent.run({
            "synthesis_result": synthesis_result,
            "agent_results": agent_results
        })

        assert result["status"] in ["APPROVED", "NEEDS_REVISION"]


class TestCompletenessCheck:
    """Test completeness evaluation."""

    def test_complete_synthesis_passes(self, reviewer_agent, synthesis_result, agent_results):
        """Test that complete synthesis passes completeness check."""
        feedback = reviewer_agent.evaluate_synthesis(synthesis_result, agent_results)
        assert feedback.completeness_score > 0.5

    def test_missing_fields_fails(self, reviewer_agent, agent_results):
        """Test that missing fields fail completeness."""
        incomplete = {"report": "Short"}
        feedback = reviewer_agent.evaluate_synthesis(incomplete, agent_results)
        assert feedback.completeness_score < 0.9

    def test_missing_key_findings(self, reviewer_agent, synthesis_result, agent_results):
        """Test that missing key findings lower score."""
        incomplete = synthesis_result.copy()
        incomplete["key_findings"] = ["Only one"]
        feedback = reviewer_agent.evaluate_synthesis(incomplete, agent_results)
        assert feedback.completeness_score < 0.9

    def test_minimal_evidence(self, reviewer_agent, synthesis_result, agent_results):
        """Test that minimal evidence lowers score."""
        incomplete = synthesis_result.copy()
        incomplete["evidence"] = []
        feedback = reviewer_agent.evaluate_synthesis(incomplete, agent_results)
        assert feedback.completeness_score < 0.8


class TestAccuracyCheck:
    """Test accuracy evaluation."""

    def test_accurate_synthesis_passes(self, reviewer_agent, synthesis_result, agent_results):
        """Test that accurate synthesis passes."""
        feedback = reviewer_agent.evaluate_synthesis(synthesis_result, agent_results)
        assert feedback.accuracy_score > 0.5

    def test_short_report_fails_accuracy(self, reviewer_agent, agent_results):
        """Test that short report fails accuracy check."""
        short_synthesis = {
            "report": "Short",
            "key_findings": ["Test"],
            "evidence": [],
            "recommendation": ""
        }
        feedback = reviewer_agent.evaluate_synthesis(short_synthesis, agent_results)
        assert feedback.accuracy_score < 0.7

    def test_missing_campaign_mention(self, reviewer_agent, agent_results):
        """Test that missing campaign findings in report lowers accuracy."""
        synthesis = {
            "report": "This is a test report",
            "key_findings": ["Finding 1"],
            "evidence": [],
            "recommendation": "Test",
            "original_query": ""
        }
        feedback = reviewer_agent.evaluate_synthesis(synthesis, agent_results)
        assert feedback.accuracy_score < 0.9


class TestClarityCheck:
    """Test clarity evaluation."""

    def test_clear_report_passes(self, reviewer_agent, synthesis_result, agent_results):
        """Test that clear, structured report passes."""
        feedback = reviewer_agent.evaluate_synthesis(synthesis_result, agent_results)
        assert feedback.clarity_score > 0.5

    def test_unstructured_report_fails(self, reviewer_agent, agent_results):
        """Test that unstructured report fails clarity."""
        poor_clarity = {
            "report": "Some random text without structure",
            "key_findings": [],
            "evidence": [],
            "recommendation": ""
        }
        feedback = reviewer_agent.evaluate_synthesis(poor_clarity, agent_results)
        assert feedback.clarity_score < 0.8

    def test_missing_recommendation_fails(self, reviewer_agent, synthesis_result, agent_results):
        """Test that missing recommendation lowers clarity."""
        no_rec = synthesis_result.copy()
        no_rec["recommendation"] = ""
        feedback = reviewer_agent.evaluate_synthesis(no_rec, agent_results)
        assert feedback.clarity_score < 0.9


class TestRelevanceCheck:
    """Test relevance evaluation."""

    def test_relevant_report_passes(self, reviewer_agent, synthesis_result, agent_results):
        """Test that relevant report passes."""
        feedback = reviewer_agent.evaluate_synthesis(synthesis_result, agent_results)
        assert feedback.relevance_score > 0.5

    def test_irrelevant_report_fails(self, reviewer_agent, agent_results):
        """Test that irrelevant report fails relevance check."""
        irrelevant = {
            "report": "This is about sports and games",
            "key_findings": [],
            "evidence": [],
            "recommendation": "Test",
            "original_query": "Analyze election campaigns"
        }
        feedback = reviewer_agent.evaluate_synthesis(irrelevant, agent_results)
        assert feedback.relevance_score < 0.7


class TestFeedbackGeneration:
    """Test feedback generation."""

    def test_feedback_has_issues(self, reviewer_agent, synthesis_result, agent_results):
        """Test that feedback identifies issues."""
        feedback = reviewer_agent.evaluate_synthesis(synthesis_result, agent_results)

        if feedback.status == "NEEDS_REVISION":
            assert len(feedback.issues) > 0

    def test_feedback_has_suggestions(self, reviewer_agent, synthesis_result, agent_results):
        """Test that feedback provides suggestions."""
        feedback = reviewer_agent.evaluate_synthesis(synthesis_result, agent_results)

        if feedback.status == "NEEDS_REVISION":
            assert len(feedback.suggestions) > 0

    def test_feedback_prompt_format(self, reviewer_agent, synthesis_result, agent_results):
        """Test that feedback prompt is well-formatted."""
        feedback = reviewer_agent.evaluate_synthesis(synthesis_result, agent_results)
        prompt = reviewer_agent.generate_feedback_prompt(feedback)

        assert isinstance(prompt, str)
        assert "Status" in prompt or "status" in prompt.lower()


class TestReflectionLoop:
    """Test reflection loop functionality."""

    @pytest.fixture
    def mock_agents(self):
        """Create mock synthesis and reviewer agents."""
        class MockSynthesisAgent:
            def run(self, input_data):
                return {
                    "report": "Test report",
                    "key_findings": ["Finding 1", "Finding 2"],
                    "evidence": [{"type": "test", "confidence": 0.8}],
                    "recommendation": "Test recommendation",
                    "original_query": input_data.get("original_query")
                }

        class MockReviewerAgent:
            def __init__(self, approval_iter=1):
                self.approval_iter = approval_iter
                self.call_count = 0

            def run(self, input_data):
                self.call_count += 1
                status = "APPROVED" if self.call_count >= self.approval_iter else "NEEDS_REVISION"
                return {
                    "status": status,
                    "completeness_score": 0.8,
                    "accuracy_score": 0.8,
                    "clarity_score": 0.8,
                    "relevance_score": 0.8,
                    "issues": ["Issue 1"] if status == "NEEDS_REVISION" else [],
                    "suggestions": ["Suggestion 1"] if status == "NEEDS_REVISION" else [],
                    "confidence": 0.8
                }

        return MockSynthesisAgent(), MockReviewerAgent()

    def test_loop_initialization(self, mock_agents):
        """Test loop initializes correctly."""
        synthesis_agent, reviewer_agent = mock_agents
        loop = ReflectionLoop(synthesis_agent, reviewer_agent, max_retries=3)

        assert loop.max_retries == 3

    def test_loop_approves_on_first_pass(self, mock_agents):
        """Test loop approves result on first pass."""
        synthesis_agent, reviewer_agent = mock_agents
        reviewer_agent.approval_iter = 1

        loop = ReflectionLoop(synthesis_agent, reviewer_agent, max_retries=3)
        result = loop.execute_with_review({}, {"report": "Test"})

        assert result.approved
        assert result.iterations == 1

    def test_loop_retries_on_rejection(self, mock_agents):
        """Test loop retries when rejected."""
        synthesis_agent, reviewer_agent = mock_agents
        reviewer_agent.approval_iter = 2

        loop = ReflectionLoop(synthesis_agent, reviewer_agent, max_retries=3)
        result = loop.execute_with_review({}, {"report": "Test"})

        assert result.approved
        assert result.iterations == 2

    def test_loop_escalates_on_max_retries(self, mock_agents):
        """Test loop escalates after max retries."""
        synthesis_agent, reviewer_agent = mock_agents
        reviewer_agent.approval_iter = 10  # Never approve

        loop = ReflectionLoop(synthesis_agent, reviewer_agent, max_retries=2)
        result = loop.execute_with_review({}, {"report": "Test"})

        assert not result.approved
        assert result.iterations == 2
        assert result.status == "ESCALATED"

    def test_loop_tracks_feedback(self, mock_agents):
        """Test loop tracks feedback history."""
        synthesis_agent, reviewer_agent = mock_agents
        reviewer_agent.approval_iter = 2

        loop = ReflectionLoop(synthesis_agent, reviewer_agent, max_retries=3)
        result = loop.execute_with_review({}, {"report": "Test"})

        assert len(result.feedback_history) == 2
        for feedback in result.feedback_history:
            assert "iteration" in feedback
            assert "status" in feedback
            assert "scores" in feedback

    def test_loop_statistics(self, mock_agents):
        """Test loop statistics calculation."""
        synthesis_agent, reviewer_agent = mock_agents
        reviewer_agent.approval_iter = 2

        loop = ReflectionLoop(synthesis_agent, reviewer_agent, max_retries=3)
        result = loop.execute_with_review({}, {"report": "Test"})

        stats = loop.get_loop_statistics(result)
        assert "total_iterations" in stats
        assert "approved" in stats
        assert "average_completeness" in stats
        assert "average_accuracy" in stats
