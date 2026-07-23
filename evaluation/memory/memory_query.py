"""
Query interface for evaluation memory records.
Enables retrieval and analysis of past evaluation runs.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class MemoryQuery:
    """
    Query past evaluation records for continuous learning.
    """

    def __init__(self, records_dir: Optional[str] = None):
        if records_dir is None:
            records_dir = Path(__file__).parent / "records"
        else:
            records_dir = Path(records_dir)
        self.records_dir = records_dir

    def _load_records(self, target_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load all records, optionally filtered by target."""
        records = []
        targets = [target_name] if target_name else [d.name for d in self.records_dir.iterdir() if d.is_dir()]

        for target in targets:
            target_path = self.records_dir / target
            if not target_path.exists():
                continue
            for record_file in sorted(target_path.glob("*.json")):
                try:
                    with open(record_file) as f:
                        records.append(json.load(f))
                except (json.JSONDecodeError, IOError):
                    continue

        return records

    def get_records_for_target(self, target_name: str) -> List[Dict[str, Any]]:
        """Get all records for a specific target system."""
        return self._load_records(target_name)

    def get_latest_record(self, target_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent record for a target."""
        records = self.get_records_for_target(target_name)
        if not records:
            return None
        return max(records, key=lambda r: r.get("started_at", ""))

    def find_bypasses(
        self,
        target_name: Optional[str] = None,
        bypass_type: Optional[str] = None,
        min_severity: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find all test cases that resulted in bypasses.

        Args:
            target_name: Filter by target system
            bypass_type: Filter by specific bypass technique
            min_severity: Minimum severity ("low", "medium", "high", "critical")

        Returns:
            List of failed test cases with full context
        """
        severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        min_level = severity_order.get(min_severity, 0)

        bypasses = []
        records = self._load_records(target_name)

        for record in records:
            for tc in record.get("test_cases", []):
                if tc.get("passed"):
                    continue
                if bypass_type and tc.get("bypass_type") != bypass_type:
                    continue
                if min_severity:
                    tc_level = severity_order.get(tc.get("severity", "low"), 0)
                    if tc_level < min_level:
                        continue

                # Enrich with run context
                enriched = {
                    **tc,
                    "run_id": record.get("run_id"),
                    "target_name": record.get("target_name"),
                    "run_started_at": record.get("started_at"),
                    "run_config": record.get("config"),
                }
                bypasses.append(enriched)

        return bypasses

    def get_metric_trend(
        self, target_name: str, metric: str = "pass_rate"
    ) -> List[Dict[str, Any]]:
        """
        Get trend of a metric over time for a target.

        Args:
            target_name: Target system to analyze
            metric: Metric key from summary ("pass_rate", "block_rate", etc.)

        Returns:
            List of {timestamp, value} dicts, sorted by time
        """
        records = self.get_records_for_target(target_name)
        trend = []

        for record in records:
            value = record.get("summary", {}).get(metric)
            if value is not None:
                trend.append({
                    "timestamp": record.get("started_at"),
                    "run_id": record.get("run_id"),
                    "value": value,
                })

        return sorted(trend, key=lambda x: x["timestamp"])

    def get_bypass_type_distribution(self, target_name: Optional[str] = None) -> Dict[str, int]:
        """Count bypass types across all records."""
        bypasses = self.find_bypasses(target_name)
        distribution = {}
        for bp in bypasses:
            bt = bp.get("bypass_type", "unknown")
            distribution[bt] = distribution.get(bt, 0) + 1
        return distribution

    def get_unique_commands_with_bypasses(self, target_name: str) -> List[str]:
        """Get unique commands that have bypassed detection at least once."""
        bypasses = self.find_bypasses(target_name)
        seen = set()
        commands = []
        for bp in bypasses:
            cmd = bp.get("input_data", "")
            if cmd and cmd not in seen:
                seen.add(cmd)
                commands.append(cmd)
        return commands

    def compare_runs(self, run_id_1: str, run_id_2: str) -> Dict[str, Any]:
        """
        Compare two evaluation runs and identify regressions/improvements.

        Returns:
            Dict with: new_passes, new_failures, unchanged, regression_count, improvement_count
        """
        all_records = self._load_records()
        r1 = next((r for r in all_records if r.get("run_id") == run_id_1), None)
        r2 = next((r for r in all_records if r.get("run_id") == run_id_2), None)

        if not r1 or not r2:
            return {"error": "One or both run IDs not found"}

        tc1 = {tc["test_id"]: tc for tc in r1.get("test_cases", [])}
        tc2 = {tc["test_id"]: tc for tc in r2.get("test_cases", [])}

        new_failures = []
        new_passes = []
        unchanged = []

        for test_id, tc in tc2.items():
            old = tc1.get(test_id)
            if not old:
                # New test in run 2
                if not tc["passed"]:
                    new_failures.append(tc)
                continue

            if old["passed"] and not tc["passed"]:
                new_failures.append({"test_id": test_id, "was": "pass", "now": "fail", "details": tc})
            elif not old["passed"] and tc["passed"]:
                new_passes.append({"test_id": test_id, "was": "fail", "now": "pass", "details": tc})
            else:
                unchanged.append(test_id)

        return {
            "run_1": run_id_1,
            "run_2": run_id_2,
            "target": r1.get("target_name"),
            "new_failures": new_failures,
            "new_passes": new_passes,
            "unchanged_count": len(unchanged),
            "regression_count": len(new_failures),
            "improvement_count": len(new_passes),
        }

    def generate_next_run_recommendations(self, target_name: str) -> List[str]:
        """
        Based on past evaluations, generate recommendations for the next run.

        Returns:
            List of actionable recommendation strings
        """
        recommendations = []
        latest = self.get_latest_record(target_name)
        if not latest:
            return ["No previous records found. Run baseline evaluation first."]

        summary = latest.get("summary", {})
        bypass_types = summary.get("bypass_type_counts", {})

        # Rule-based recommendations
        if summary.get("pass_rate", 1.0) < 0.5:
            recommendations.append(
                f"Pass rate is {summary.get('pass_rate', 0):.1%}. "
                "System is highly vulnerable. Prioritize fixing before expanding tests."
            )

        if "base64" in bypass_types or "base64_encoded" in bypass_types:
            recommendations.append(
                "Base64 encoding bypasses detected. Add hex, urlencode, and mixed-encoding variants."
            )

        if "roleplay" in str(bypass_types).lower() or "roleplay_assistant" in bypass_types:
            recommendations.append(
                "Roleplay bypasses detected. Test developer-mode, hypothetical framing, and creative-writing variants."
            )

        if summary.get("false_positive_rate", 0) > 0.1:
            recommendations.append(
                f"False positive rate is {summary.get('false_positive_rate', 0):.1%}. "
                "Review benign test cases for overly aggressive blocking."
            )

        if summary.get("generated_variant_count", 0) == 0 and summary.get("failed", 0) > 0:
            recommendations.append(
                f"{summary.get('failed', 0)} failures with no variants generated. "
                "Run variant generator to expand test coverage."
            )

        if not recommendations:
            recommendations.append(
                f"Latest run shows pass rate of {summary.get('pass_rate', 0):.1%}. "
                "Consider expanding to new attack categories or increasing test diversity."
            )

        return recommendations
