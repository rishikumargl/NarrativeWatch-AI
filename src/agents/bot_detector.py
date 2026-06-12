"""Bot Detector Agent for NarrativeWatch AI."""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from statistics import mean, stdev
import numpy as np

try:
    from src.agents.base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

logger = logging.getLogger(__name__)


class BotDetectorAgent(BaseAgent):
    """Detect bot activity and coordinated engagement patterns."""

    def __init__(self):
        """Initialize Bot Detector Agent."""
        super().__init__(
            name="Bot Detector",
            description="Analyze engagement patterns for bot activity and "
                       "coordinated influence campaigns"
        )

    def run(self, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze engagement data for bot activity.

        Args:
            engagement_data: Dict with comments, likes, followers, timing data

        Returns:
            Dict with bot detection analysis
        """
        try:
            if not self.validate_input(engagement_data):
                return {"status": "error", "message": "Invalid input data"}

            comments = engagement_data.get("comments", [])
            likes_history = engagement_data.get("likes_history", [])
            follower_data = engagement_data.get("follower_data", {})
            engagement_timing = engagement_data.get("engagement_timing", [])

            analysis = {
                "bot_activity_score": 0.0,  # Calculated below
                "engagement_velocity": self._analyze_engagement_velocity(likes_history),
                "comment_authenticity": self._analyze_comment_patterns(comments),
                "follower_anomalies": self._detect_follower_anomalies(follower_data),
                "timing_patterns": self._analyze_timing_patterns(engagement_timing),
                "bot_indicators": self._extract_bot_indicators(engagement_data),
                "risk_level": "low",  # Determined below
            }

            # Calculate overall bot activity score
            scores = [
                analysis["engagement_velocity"].get("anomaly_score", 0),
                analysis["comment_authenticity"].get("bot_likelihood", 0),
                analysis["follower_anomalies"].get("anomaly_score", 0),
                min(analysis["timing_patterns"].get("pattern_score", 0), 1.0),
            ]

            bot_score = mean(scores) if scores else 0.0
            analysis["bot_activity_score"] = float(bot_score)

            # Determine risk level
            if bot_score > 0.7:
                analysis["risk_level"] = "critical"
            elif bot_score > 0.5:
                analysis["risk_level"] = "high"
            elif bot_score > 0.3:
                analysis["risk_level"] = "medium"
            else:
                analysis["risk_level"] = "low"

            return {
                "status": "success",
                "agent": "Bot Detector",
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Bot Detector error: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def validate_input(self, input_data: Any) -> bool:
        """Validate input data."""
        if not isinstance(input_data, dict):
            return False
        # At least one of these should exist
        return bool(
            input_data.get("comments") or
            input_data.get("likes_history") or
            input_data.get("follower_data") or
            input_data.get("engagement_timing")
        )

    def _analyze_engagement_velocity(self, likes_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement velocity for anomalies."""
        if not likes_history or len(likes_history) < 2:
            return {
                "anomaly_detected": False,
                "z_score": 0.0,
                "anomaly_score": 0.0,
                "description": "Insufficient data",
            }

        try:
            # Extract like counts over time
            like_counts = [item.get("count", 0) for item in likes_history]

            # Calculate velocity (rate of change)
            velocities = []
            for i in range(1, len(like_counts)):
                velocity = like_counts[i] - like_counts[i-1]
                velocities.append(velocity)

            if not velocities or len(velocities) < 2:
                return {
                    "anomaly_detected": False,
                    "z_score": 0.0,
                    "anomaly_score": 0.0,
                    "description": "Insufficient velocity data",
                }

            # Calculate statistics
            mean_velocity = mean(velocities)
            std_velocity = stdev(velocities) if len(velocities) > 1 else 0

            # Z-score for latest velocity
            if std_velocity > 0:
                z_score = abs((velocities[-1] - mean_velocity) / std_velocity)
            else:
                z_score = 0.0

            # Anomaly detection (z-score > 2 is anomalous)
            anomaly_detected = z_score > 2.0
            anomaly_score = min(z_score / 5, 1.0)  # Normalize to 0-1

            return {
                "anomaly_detected": anomaly_detected,
                "z_score": float(z_score),
                "anomaly_score": float(anomaly_score),
                "velocity_mean": float(mean_velocity),
                "velocity_std": float(std_velocity),
                "description": "Engagement spike detected" if anomaly_detected else "Normal velocity",
            }

        except Exception as e:
            logger.warning(f"Could not analyze engagement velocity: {e}")
            return {
                "anomaly_detected": False,
                "z_score": 0.0,
                "anomaly_score": 0.0,
                "description": f"Error: {str(e)}",
            }

    def _analyze_comment_patterns(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze comment patterns for bot-like behavior."""
        if not comments:
            return {
                "bot_likelihood": 0.0,
                "repetition_percentage": 0.0,
                "suspicion_level": "none",
                "indicators": [],
            }

        try:
            comment_texts = [c.get("text", "") for c in comments if c.get("text")]

            if not comment_texts:
                return {
                    "bot_likelihood": 0.0,
                    "repetition_percentage": 0.0,
                    "suspicion_level": "none",
                    "indicators": [],
                }

            # Calculate text similarity and repetition
            unique_comments = len(set(comment_texts))
            total_comments = len(comment_texts)
            repetition_percentage = 1 - (unique_comments / total_comments) if total_comments > 0 else 0

            # Find repeated comments
            from collections import Counter
            comment_counts = Counter(comment_texts)
            repeated_comments = {text: count for text, count in comment_counts.items() if count > 1}

            # Check for common bot patterns
            bot_indicators = []
            for comment in comment_texts:
                if self._is_bot_like_comment(comment):
                    bot_indicators.append(comment)

            # Calculate bot likelihood
            bot_likelihood = (repetition_percentage * 0.4 +
                            (len(bot_indicators) / len(comment_texts)) * 0.6 if comment_texts else 0)
            bot_likelihood = min(bot_likelihood, 1.0)

            # Determine suspicion level
            if repetition_percentage > 0.5:
                suspicion = "critical"
            elif repetition_percentage > 0.3:
                suspicion = "high"
            elif repetition_percentage > 0.1:
                suspicion = "medium"
            else:
                suspicion = "low"

            return {
                "bot_likelihood": float(bot_likelihood),
                "repetition_percentage": float(repetition_percentage),
                "total_comments": total_comments,
                "unique_comments": unique_comments,
                "suspicion_level": suspicion,
                "repeated_comments_count": len(repeated_comments),
                "bot_pattern_count": len(bot_indicators),
                "indicators": list(set(bot_indicators))[:5],  # Top 5
            }

        except Exception as e:
            logger.warning(f"Could not analyze comment patterns: {e}")
            return {
                "bot_likelihood": 0.0,
                "repetition_percentage": 0.0,
                "suspicion_level": "error",
                "indicators": [],
            }

    def _detect_follower_anomalies(self, follower_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in follower growth."""
        if not follower_data:
            return {
                "growth_anomaly": False,
                "anomaly_score": 0.0,
                "avg_daily_growth": 0.0,
                "description": "No follower data",
            }

        try:
            daily_growth = follower_data.get("daily_growth", [])

            if not daily_growth or len(daily_growth) < 2:
                return {
                    "growth_anomaly": False,
                    "anomaly_score": 0.0,
                    "avg_daily_growth": 0.0,
                    "description": "Insufficient growth data",
                }

            # Calculate statistics
            growth_values = [float(g) for g in daily_growth if isinstance(g, (int, float))]
            avg_growth = mean(growth_values)
            std_growth = stdev(growth_values) if len(growth_values) > 1 else 0

            # Check for anomalies (sudden spikes)
            latest_growth = growth_values[-1] if growth_values else 0
            if std_growth > 0:
                z_score = abs((latest_growth - avg_growth) / std_growth)
            else:
                z_score = 0.0

            anomaly_detected = z_score > 2.5
            anomaly_score = min(z_score / 5, 1.0)

            # Check for suspicious growth patterns
            suspicious_patterns = []
            if avg_growth > 1000:  # Unusual growth rate
                suspicious_patterns.append("unusually_high_growth")
            if std_growth > avg_growth * 2:  # High volatility
                suspicious_patterns.append("volatile_growth")

            return {
                "growth_anomaly": anomaly_detected,
                "anomaly_score": float(anomaly_score),
                "avg_daily_growth": float(avg_growth),
                "std_daily_growth": float(std_growth),
                "latest_daily_growth": float(latest_growth),
                "suspicious_patterns": suspicious_patterns,
                "description": "Anomalous growth pattern detected" if anomaly_detected else "Normal growth",
            }

        except Exception as e:
            logger.warning(f"Could not detect follower anomalies: {e}")
            return {
                "growth_anomaly": False,
                "anomaly_score": 0.0,
                "avg_daily_growth": 0.0,
                "description": f"Error: {str(e)}",
            }

    def _analyze_timing_patterns(self, engagement_timing: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze timing patterns for coordinated engagement."""
        if not engagement_timing:
            return {
                "pattern_score": 0.0,
                "coordination_detected": False,
                "timing_regularity": 0.0,
                "description": "No timing data",
            }

        try:
            timestamps = [item.get("timestamp") for item in engagement_timing if item.get("timestamp")]

            if not timestamps or len(timestamps) < 3:
                return {
                    "pattern_score": 0.0,
                    "coordination_detected": False,
                    "timing_regularity": 0.0,
                    "description": "Insufficient timing data",
                }

            # Calculate inter-event times
            inter_event_times = []
            for i in range(1, len(timestamps)):
                try:
                    t1 = datetime.fromisoformat(str(timestamps[i-1]))
                    t2 = datetime.fromisoformat(str(timestamps[i]))
                    delta = (t2 - t1).total_seconds()
                    inter_event_times.append(delta)
                except Exception:
                    continue

            if not inter_event_times or len(inter_event_times) < 2:
                return {
                    "pattern_score": 0.0,
                    "coordination_detected": False,
                    "timing_regularity": 0.0,
                    "description": "Could not parse timestamps",
                }

            # Calculate coefficient of variation (regularity metric)
            times_array = np.array(inter_event_times, dtype=np.float32)
            mean_time = np.mean(times_array)
            std_time = np.std(times_array)

            if mean_time > 0:
                cv = std_time / mean_time  # Coefficient of variation
            else:
                cv = 0.0

            # Very low CV means very regular (bot-like) timing
            timing_regularity = 1 - min(cv, 1.0)  # Invert so high regularity = high bot likelihood

            # Check for suspicious patterns (e.g., regular intervals)
            coordination_detected = timing_regularity > 0.8

            return {
                "pattern_score": float(timing_regularity),
                "coordination_detected": coordination_detected,
                "timing_regularity": float(timing_regularity),
                "mean_interval": float(mean_time),
                "std_interval": float(std_time),
                "description": "Coordinated timing pattern detected" if coordination_detected else "Random timing",
            }

        except Exception as e:
            logger.warning(f"Could not analyze timing patterns: {e}")
            return {
                "pattern_score": 0.0,
                "coordination_detected": False,
                "timing_regularity": 0.0,
                "description": f"Error: {str(e)}",
            }

    def _extract_bot_indicators(self, engagement_data: Dict[str, Any]) -> List[str]:
        """Extract specific indicators of bot activity."""
        indicators = []

        # Check various indicators
        if engagement_data.get("engagement_velocity", {}).get("anomaly_detected"):
            indicators.append("engagement_spike")

        if engagement_data.get("comment_authenticity", {}).get("repetition_percentage", 0) > 0.3:
            indicators.append("repeated_comments")

        if engagement_data.get("follower_data", {}).get("daily_growth"):
            daily_growth = engagement_data["follower_data"]["daily_growth"]
            if any(g > 1000 for g in daily_growth if isinstance(g, (int, float))):
                indicators.append("unusual_follower_growth")

        if engagement_data.get("engagement_timing"):
            if len(engagement_data["engagement_timing"]) > 10:
                indicators.append("high_engagement_frequency")

        return indicators

    def _is_bot_like_comment(self, comment: str) -> bool:
        """Check if a comment exhibits bot-like characteristics."""
        if not comment:
            return False

        # Bot patterns
        bot_patterns = [
            r"^[a-z]{1,3}$",  # Very short comments (a, b, c, etc.)
            r"^[0-9]+$",  # Only numbers
            r"^[!?]{2,}$",  # Multiple punctuation
            r"check out|link in bio|click here|follow me|dm for",  # Promotional
            r"([a-z])\1{2,}",  # Repeated characters (aaaa, bbbb)
        ]

        import re
        for pattern in bot_patterns:
            try:
                if re.search(pattern, comment, re.IGNORECASE):
                    return True
            except Exception:
                continue

        return False
