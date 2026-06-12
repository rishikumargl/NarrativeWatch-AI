"""Campaign Detector Agent - Detects coordinated influence campaigns."""

from typing import Any, Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import math


@dataclass
class Campaign:
    campaign_id: str
    pages: List[str]
    confidence: float
    narrative_theme: str
    hashtag_overlap: float
    timing_correlation: float
    narrative_similarity: float
    evidence: Dict[str, Any]


class CampaignDetectorAgent:
    """Detects coordinated influence campaigns across multiple pages."""

    def __init__(self, name: str = "Campaign Detector"):
        self.name = name
        self.description = "Identifies coordinated influence campaigns across Instagram pages"

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect campaigns from page data.

        Args:
            input_data: Dict with 'pages' (List), 'posts' (List), 'query_context' (str)

        Returns:
            Dict with 'campaigns', 'campaign_count', 'evidence', etc.
        """
        pages = input_data.get("pages", [])
        posts = input_data.get("posts", [])
        query_context = input_data.get("query_context", "")

        if not pages:
            return {
                "campaigns": [],
                "campaign_count": 0,
                "coordinated_pages": [],
                "message": "No pages provided"
            }

        campaigns = self.detect_campaigns(pages, posts)

        return {
            "campaigns": [asdict(c) for c in campaigns],
            "campaign_count": len(campaigns),
            "total_pages_analyzed": len(pages),
            "coordinated_pages": self._get_coordinated_pages(campaigns),
            "evidence": self._aggregate_evidence(campaigns),
            "message": f"Detected {len(campaigns)} potential campaign(s)"
        }

    def detect_campaigns(self, pages: List[Dict], posts: List[Dict] = None) -> List[Campaign]:
        """Detect campaigns using graph clustering."""
        if posts is None:
            posts = []

        page_graph = self._build_page_graph(pages, posts)
        clusters = self._cluster_pages(page_graph)

        campaigns = []
        for cluster in clusters:
            if len(cluster) >= 2:
                campaign = self._analyze_cluster(cluster, pages, posts, page_graph)
                if campaign.confidence > 0.5:
                    campaigns.append(campaign)

        return sorted(campaigns, key=lambda c: c.confidence, reverse=True)

    def _build_page_graph(self, pages: List[Dict], posts: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Build graph of page relationships."""
        graph = defaultdict(lambda: defaultdict(float))

        for i, page1 in enumerate(pages):
            page1_id = page1.get("id") or page1.get("username")

            for j, page2 in enumerate(pages):
                if i >= j:
                    continue

                page2_id = page2.get("id") or page2.get("username")

                similarity = self._calculate_page_similarity(page1, page2, posts)
                if similarity > 0:
                    graph[page1_id][page2_id] = similarity
                    graph[page2_id][page1_id] = similarity

        return graph

    def _calculate_page_similarity(self, page1: Dict, page2: Dict, posts: List[Dict]) -> float:
        """Calculate similarity between two pages."""
        hashtag_sim = self._hashtag_similarity(page1, page2)
        timing_sim = self._timing_similarity(page1, page2, posts)
        narrative_sim = self._narrative_similarity(page1, page2)

        return (hashtag_sim * 0.4) + (timing_sim * 0.3) + (narrative_sim * 0.3)

    def _hashtag_similarity(self, page1: Dict, page2: Dict) -> float:
        """Calculate hashtag overlap between pages."""
        tags1 = set(page1.get("hashtags", []))
        tags2 = set(page2.get("hashtags", []))

        if not tags1 or not tags2:
            return 0.0

        intersection = len(tags1 & tags2)
        union = len(tags1 | tags2)

        return intersection / union if union > 0 else 0.0

    def _timing_similarity(self, page1: Dict, page2: Dict, posts: List[Dict]) -> float:
        """Calculate engagement timing correlation."""
        posts1 = [p for p in posts if p.get("page_id") == page1.get("id")]
        posts2 = [p for p in posts if p.get("page_id") == page2.get("id")]

        if not posts1 or not posts2:
            return 0.0

        timestamps1 = [p.get("timestamp", "") for p in posts1]
        timestamps2 = [p.get("timestamp", "") for p in posts2]

        if not timestamps1 or not timestamps2:
            return 0.0

        common_hours = 0
        for t1 in timestamps1:
            hour1 = self._extract_hour(t1)
            for t2 in timestamps2:
                hour2 = self._extract_hour(t2)
                if hour1 and hour2 and abs(hour1 - hour2) <= 2:
                    common_hours += 1

        max_possible = min(len(timestamps1), len(timestamps2))
        return (common_hours / max_possible) if max_possible > 0 else 0.0

    def _narrative_similarity(self, page1: Dict, page2: Dict) -> float:
        """Calculate narrative/theme similarity."""
        desc1 = str(page1.get("description", "")).lower()
        desc2 = str(page2.get("description", "")).lower()

        if not desc1 or not desc2:
            return 0.0

        words1 = set(desc1.split())
        words2 = set(desc2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _cluster_pages(self, graph: Dict[str, Dict[str, float]]) -> List[Set[str]]:
        """Simple clustering based on similarity threshold."""
        threshold = 0.6
        visited = set()
        clusters = []

        for page in graph.keys():
            if page in visited:
                continue

            cluster = {page}
            visited.add(page)
            queue = [page]

            while queue:
                current = queue.pop(0)
                for neighbor, similarity in graph[current].items():
                    if neighbor not in visited and similarity > threshold:
                        cluster.add(neighbor)
                        visited.add(neighbor)
                        queue.append(neighbor)

            if len(cluster) >= 2:
                clusters.append(cluster)

        return clusters

    def _analyze_cluster(
        self,
        cluster: Set[str],
        pages: List[Dict],
        posts: List[Dict],
        graph: Dict[str, Dict[str, float]]
    ) -> Campaign:
        """Analyze a cluster of coordinated pages."""
        cluster_list = list(cluster)
        cluster_pages = [p for p in pages if (p.get("id") or p.get("username")) in cluster]

        hashtag_overlap = self._calculate_cluster_hashtag_overlap(cluster_pages)
        timing_correlation = self._calculate_cluster_timing(cluster_pages, posts)
        narrative_similarity = self._calculate_cluster_narrative(cluster_pages)

        confidence = (hashtag_overlap * 0.4) + (timing_correlation * 0.3) + (narrative_similarity * 0.3)

        narrative_theme = self._infer_narrative_theme(cluster_pages)

        return Campaign(
            campaign_id=f"campaign_{hash(frozenset(cluster)) % 10000:04d}",
            pages=cluster_list,
            confidence=confidence,
            narrative_theme=narrative_theme,
            hashtag_overlap=hashtag_overlap,
            timing_correlation=timing_correlation,
            narrative_similarity=narrative_similarity,
            evidence={
                "page_count": len(cluster_list),
                "shared_hashtags": self._get_shared_hashtags(cluster_pages),
                "temporal_correlation": timing_correlation,
                "similar_narratives": narrative_similarity
            }
        )

    def _calculate_cluster_hashtag_overlap(self, pages: List[Dict]) -> float:
        """Calculate hashtag overlap within cluster."""
        all_hashtags = [set(p.get("hashtags", [])) for p in pages]

        if not all_hashtags:
            return 0.0

        intersection = set.intersection(*all_hashtags) if all_hashtags else set()
        union = set.union(*all_hashtags) if all_hashtags else set()

        return len(intersection) / len(union) if union else 0.0

    def _calculate_cluster_timing(self, pages: List[Dict], posts: List[Dict]) -> float:
        """Calculate timing correlation within cluster."""
        page_ids = set(p.get("id") for p in pages)
        cluster_posts = [p for p in posts if p.get("page_id") in page_ids]

        if len(cluster_posts) < 2:
            return 0.0

        timestamps = [self._extract_hour(p.get("timestamp", "")) for p in cluster_posts]
        timestamps = [t for t in timestamps if t is not None]

        if not timestamps:
            return 0.0

        variance = sum((t - sum(timestamps) / len(timestamps)) ** 2 for t in timestamps) / len(timestamps)
        std_dev = math.sqrt(variance)

        return 1 / (1 + std_dev / 24)

    def _calculate_cluster_narrative(self, pages: List[Dict]) -> float:
        """Calculate narrative similarity within cluster."""
        if not pages:
            return 0.0

        descriptions = [str(p.get("description", "")).lower() for p in pages]
        word_sets = [set(d.split()) for d in descriptions if d]

        if not word_sets:
            return 0.0

        intersection = set.intersection(*word_sets) if word_sets else set()
        union = set.union(*word_sets) if word_sets else set()

        return len(intersection) / len(union) if union else 0.0

    def _infer_narrative_theme(self, pages: List[Dict]) -> str:
        """Infer dominant narrative theme."""
        descriptions = [str(p.get("description", "")).lower() for p in pages]
        text = " ".join(descriptions)

        keywords = {
            "election": "election manipulation",
            "vote": "electoral influence",
            "political": "political campaign",
            "climate": "climate denial",
            "health": "health misinformation",
            "vaccine": "vaccine hesitancy",
            "covid": "covid misinformation"
        }

        for keyword, theme in keywords.items():
            if keyword in text:
                return theme

        return "coordinated influence campaign"

    def _get_shared_hashtags(self, pages: List[Dict]) -> List[str]:
        """Get hashtags shared across pages."""
        if not pages:
            return []

        all_tags = [set(p.get("hashtags", [])) for p in pages]
        if not all_tags:
            return []

        shared = set.intersection(*all_tags) if all_tags else set()
        return list(shared)[:10]

    def _get_coordinated_pages(self, campaigns: List[Campaign]) -> List[str]:
        """Get all pages in coordinated campaigns."""
        pages = set()
        for campaign in campaigns:
            pages.update(campaign.pages)
        return list(pages)

    def _aggregate_evidence(self, campaigns: List[Campaign]) -> Dict[str, Any]:
        """Aggregate evidence across all campaigns."""
        return {
            "total_campaigns": len(campaigns),
            "avg_confidence": sum(c.confidence for c in campaigns) / len(campaigns) if campaigns else 0,
            "highest_confidence": max(c.confidence for c in campaigns) if campaigns else 0,
            "coordination_types": list(set(c.narrative_theme for c in campaigns))
        }

    @staticmethod
    def _extract_hour(timestamp: str) -> int:
        """Extract hour from timestamp."""
        if not timestamp:
            return None
        try:
            if "T" in timestamp:
                time_part = timestamp.split("T")[1]
                hour = int(time_part.split(":")[0])
                return hour
            return None
        except (ValueError, IndexError):
            return None
