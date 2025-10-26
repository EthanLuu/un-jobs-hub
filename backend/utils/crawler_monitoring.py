"""
Crawler monitoring and health check utilities.

Provides:
- Crawler status tracking
- Health checks
- Performance metrics
- Alert generation
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CrawlerHealth(Enum):
    """Crawler health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class CrawlerMonitor:
    """Monitor crawler health and performance."""

    def __init__(self):
        self.crawler_stats: Dict[str, Dict] = {}
        self.last_check: Optional[datetime] = None

    def update_crawler_stats(self, organization: str, metrics: Dict):
        """
        Update crawler statistics.

        Args:
            organization: Organization name
            metrics: Crawler metrics dictionary
        """
        if organization not in self.crawler_stats:
            self.crawler_stats[organization] = {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "last_run": None,
                "last_success": None,
                "total_jobs_found": 0,
                "total_jobs_saved": 0,
                "average_duration": 0.0,
                "recent_errors": []
            }

        stats = self.crawler_stats[organization]
        stats["total_runs"] += 1
        stats["last_run"] = metrics.get("end_time")

        if metrics.get("status") == "success":
            stats["successful_runs"] += 1
            stats["last_success"] = metrics.get("end_time")
        elif metrics.get("status") == "failed":
            stats["failed_runs"] += 1

        stats["total_jobs_found"] += metrics.get("jobs_found", 0)
        stats["total_jobs_saved"] += metrics.get("jobs_saved", 0)

        # Update average duration
        current_avg = stats["average_duration"]
        new_duration = metrics.get("duration_seconds", 0)
        total_runs = stats["total_runs"]
        stats["average_duration"] = (current_avg * (total_runs - 1) + new_duration) / total_runs

        # Track recent errors
        if metrics.get("errors"):
            stats["recent_errors"].extend(metrics.get("errors", []))
            stats["recent_errors"] = stats["recent_errors"][-20:]  # Keep last 20 errors

        self.last_check = datetime.utcnow()

    def get_crawler_health(self, organization: str) -> Dict:
        """
        Get health status for a specific crawler.

        Args:
            organization: Organization name

        Returns:
            Health status dictionary
        """
        if organization not in self.crawler_stats:
            return {
                "organization": organization,
                "health": CrawlerHealth.UNKNOWN.value,
                "message": "No data available",
                "checks": []
            }

        stats = self.crawler_stats[organization]
        health_checks = []
        health_status = CrawlerHealth.HEALTHY

        # Check 1: Recent run check
        last_run = stats.get("last_run")
        if last_run:
            last_run_dt = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
            hours_since_last_run = (datetime.utcnow() - last_run_dt.replace(tzinfo=None)).total_seconds() / 3600

            if hours_since_last_run > 48:  # No run in 48 hours
                health_checks.append({
                    "check": "last_run",
                    "status": "critical",
                    "message": f"No run in {hours_since_last_run:.1f} hours"
                })
                health_status = CrawlerHealth.CRITICAL
            elif hours_since_last_run > 24:  # No run in 24 hours
                health_checks.append({
                    "check": "last_run",
                    "status": "warning",
                    "message": f"No run in {hours_since_last_run:.1f} hours"
                })
                if health_status == CrawlerHealth.HEALTHY:
                    health_status = CrawlerHealth.WARNING
            else:
                health_checks.append({
                    "check": "last_run",
                    "status": "healthy",
                    "message": f"Last run {hours_since_last_run:.1f} hours ago"
                })
        else:
            health_checks.append({
                "check": "last_run",
                "status": "unknown",
                "message": "Never run"
            })
            health_status = CrawlerHealth.UNKNOWN

        # Check 2: Success rate
        total_runs = stats.get("total_runs", 0)
        if total_runs > 0:
            success_rate = (stats.get("successful_runs", 0) / total_runs) * 100

            if success_rate < 50:
                health_checks.append({
                    "check": "success_rate",
                    "status": "critical",
                    "message": f"Success rate: {success_rate:.1f}%"
                })
                health_status = CrawlerHealth.CRITICAL
            elif success_rate < 80:
                health_checks.append({
                    "check": "success_rate",
                    "status": "warning",
                    "message": f"Success rate: {success_rate:.1f}%"
                })
                if health_status == CrawlerHealth.HEALTHY:
                    health_status = CrawlerHealth.WARNING
            else:
                health_checks.append({
                    "check": "success_rate",
                    "status": "healthy",
                    "message": f"Success rate: {success_rate:.1f}%"
                })

        # Check 3: Recent errors
        recent_errors = stats.get("recent_errors", [])
        if len(recent_errors) > 10:
            health_checks.append({
                "check": "errors",
                "status": "warning",
                "message": f"{len(recent_errors)} recent errors"
            })
            if health_status == CrawlerHealth.HEALTHY:
                health_status = CrawlerHealth.WARNING
        elif len(recent_errors) > 0:
            health_checks.append({
                "check": "errors",
                "status": "info",
                "message": f"{len(recent_errors)} recent errors"
            })
        else:
            health_checks.append({
                "check": "errors",
                "status": "healthy",
                "message": "No recent errors"
            })

        return {
            "organization": organization,
            "health": health_status.value,
            "checks": health_checks,
            "stats": {
                "total_runs": stats.get("total_runs", 0),
                "successful_runs": stats.get("successful_runs", 0),
                "failed_runs": stats.get("failed_runs", 0),
                "success_rate": (stats.get("successful_runs", 0) / max(stats.get("total_runs", 1), 1)) * 100,
                "last_run": stats.get("last_run"),
                "last_success": stats.get("last_success"),
                "average_duration": stats.get("average_duration", 0),
                "total_jobs_found": stats.get("total_jobs_found", 0),
                "total_jobs_saved": stats.get("total_jobs_saved", 0)
            }
        }

    def get_all_health(self) -> List[Dict]:
        """
        Get health status for all crawlers.

        Returns:
            List of health status dictionaries
        """
        return [
            self.get_crawler_health(org)
            for org in self.crawler_stats.keys()
        ]

    def get_overall_health(self) -> Dict:
        """
        Get overall system health status.

        Returns:
            Overall health dictionary
        """
        all_health = self.get_all_health()

        if not all_health:
            return {
                "status": CrawlerHealth.UNKNOWN.value,
                "message": "No crawler data available",
                "crawler_count": 0,
                "healthy_count": 0,
                "warning_count": 0,
                "critical_count": 0
            }

        health_counts = {
            "healthy": 0,
            "warning": 0,
            "critical": 0,
            "unknown": 0
        }

        for crawler in all_health:
            health_counts[crawler["health"]] += 1

        # Determine overall status
        if health_counts["critical"] > 0:
            overall_status = CrawlerHealth.CRITICAL
        elif health_counts["warning"] > 0:
            overall_status = CrawlerHealth.WARNING
        elif health_counts["healthy"] > 0:
            overall_status = CrawlerHealth.HEALTHY
        else:
            overall_status = CrawlerHealth.UNKNOWN

        return {
            "status": overall_status.value,
            "message": f"{len(all_health)} crawlers monitored",
            "crawler_count": len(all_health),
            "healthy_count": health_counts["healthy"],
            "warning_count": health_counts["warning"],
            "critical_count": health_counts["critical"],
            "unknown_count": health_counts["unknown"],
            "last_check": self.last_check.isoformat() if self.last_check else None
        }


# Global monitor instance
crawler_monitor = CrawlerMonitor()
