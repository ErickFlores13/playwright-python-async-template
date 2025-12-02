"""
Metrics tracker for AI selector healing operations.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class MetricsTracker:
    """
    Tracks metrics and generates reports for AI healing operations.

    Monitors success rates, costs, cache effectiveness, and detailed healing logs.
    """

    def __init__(self):
        """Initialize metrics tracker."""
        self.metrics = {
            "total_attempts": 0,
            "successful_healings": 0,
            "failed_healings": 0,
            "cache_hits": 0,
            "ai_calls": 0,
            "total_cost": 0.0,
        }
        self.healing_log: List[Dict[str, Any]] = []
        self.strategy_usage: Dict[str, int] = {}

    def record_attempt(self):
        """Record a healing attempt."""
        self.metrics["total_attempts"] += 1

    def record_cache_hit(self):
        """Record a cache hit."""
        self.metrics["cache_hits"] += 1

    def record_success(self):
        """Record a successful healing."""
        self.metrics["successful_healings"] += 1

    def record_failure(self):
        """Record a failed healing."""
        self.metrics["failed_healings"] += 1

    def record_ai_call(self, cost: float = 0.0003):
        """
        Record an AI API call and its cost.

        Args:
            cost: Estimated cost of the API call (default: $0.0003 for gpt-4o-mini)
        """
        self.metrics["ai_calls"] += 1
        self.metrics["total_cost"] += cost

    def record_strategy_usage(self, strategy_name: str):
        """
        Record which extraction strategy was used.

        Args:
            strategy_name: Name of the strategy used
        """
        self.strategy_usage[strategy_name] = self.strategy_usage.get(strategy_name, 0) + 1

    def log_healing(
        self,
        original: str,
        healed: str,
        confidence: float,
        page_url: str,
        auto_applied: bool,
        strategy_used: str = "unknown",
    ):
        """
        Log a healing event for detailed review.

        Args:
            original: Original failed selector
            healed: Healed working selector
            confidence: AI confidence score (0-1)
            page_url: URL where healing occurred
            auto_applied: Whether healing was automatically applied
            strategy_used: Name of extraction strategy used
        """
        self.healing_log.append(
            {
                "original_selector": original,
                "healed_selector": healed,
                "confidence": confidence,
                "auto_applied": auto_applied,
                "page_url": page_url,
                "strategy_used": strategy_used,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_summary(self) -> Dict[str, Any]:
        """
        Get current metrics summary.

        Returns:
            Dictionary with metrics and calculated rates
        """
        total = max(self.metrics["total_attempts"], 1)  # Avoid division by zero

        return {
            "total_attempts": self.metrics["total_attempts"],
            "successful_healings": self.metrics["successful_healings"],
            "failed_healings": self.metrics["failed_healings"],
            "cache_hits": self.metrics["cache_hits"],
            "ai_calls": self.metrics["ai_calls"],
            "total_cost": self.metrics["total_cost"],
            "success_rate": self.metrics["successful_healings"] / total if total > 0 else 0,
            "cache_hit_rate": self.metrics["cache_hits"] / total if total > 0 else 0,
            "strategy_usage": self.strategy_usage.copy(),
        }

    def print_summary(self):
        """Print a beautiful summary of healing metrics to console."""
        if self.metrics["total_attempts"] == 0:
            return

        summary = self.get_summary()

        print("\n" + "=" * 50)
        print("AI Selector Healing Summary")
        print("=" * 50)
        print(f"   Total healing attempts: {summary['total_attempts']}")
        print(f"   [OK] Successful: {summary['successful_healings']}")
        print(f"   [FAIL] Failed: {summary['failed_healings']}")
        print(f"   [CACHE] Cache hits: {summary['cache_hits']}")
        print(f"   [AI] AI API calls: {summary['ai_calls']}")
        print(f"   [COST] Estimated cost: ${summary['total_cost']:.4f}")
        print(f"   [RATE] Success rate: {summary['success_rate']:.0%}")
        print(f"   [RATE] Cache hit rate: {summary['cache_hit_rate']:.0%}")

        if summary["strategy_usage"]:
            print(f"\n   [STATS] Extraction strategies used:")
            for strategy, count in summary["strategy_usage"].items():
                print(f"      • {strategy}: {count} times")

        if self.healing_log:
            print(f"\n   [REPORT] Detailed report: ai_healing_report.json")

        print("=" * 50 + "\n")

    def generate_report(self, output_path: str = "ai_healing_report.json"):
        """
        Generate detailed healing report after test run.

        Args:
            output_path: Path to save the report

        Raises:
            PermissionError: If cannot write to report file
            OSError: If file system error occurs
            TypeError: If report data is not JSON serializable
        """
        if not self.healing_log:
            logger.debug("No healing events to report")
            return

        try:
            summary = self.get_summary()

            report = {
                "summary": {
                    "total_attempts": summary["total_attempts"],
                    "successful_healings": summary["successful_healings"],
                    "failed_healings": summary["failed_healings"],
                    "cache_hits": summary["cache_hits"],
                    "ai_calls": summary["ai_calls"],
                    "total_cost": summary["total_cost"],
                    "success_rate": f"{summary['success_rate']:.0%}",
                    "cache_hit_rate": f"{summary['cache_hit_rate']:.0%}",
                    "auto_applied": len([h for h in self.healing_log if h["auto_applied"]]),
                    "needs_review": len([h for h in self.healing_log if not h["auto_applied"]]),
                    "strategy_usage": summary["strategy_usage"],
                },
                "healings": self.healing_log,
            }

            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"📊 Detailed healing report saved: {output_path}")

        except PermissionError as e:
            raise PermissionError(f"Permission denied writing report to: {output_path}") from e
        except OSError as e:
            raise OSError(f"OS error writing report: {e}") from e
        except TypeError as e:
            raise TypeError(f"Invalid report data (not JSON serializable): {e}") from e
