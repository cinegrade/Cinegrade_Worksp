import json
from pathlib import Path

class HookFeedbackEngine:
    def __init__(self, metrics_path: str = "config/hook_weights.json"):
        self.metrics_path = Path(metrics_path)
        self.metrics_path.parent.mkdir(exist_ok=True)
        self.weights = self._load_weights()

    def _load_weights(self) -> dict:
        if self.metrics_path.exists():
            with open(self.metrics_path, "r") as f:
                return json.load(f)
        return {
            "fast_zoom": 1.0,
            "cinematic_pan": 1.0,
            "glitch_intro": 1.0,
            "minimal_fade": 1.0
        }

    def update_weights(self, performance_data: dict):
        """
        performance_data format: {"fast_zoom": {"views": 12000, "retention": 0.65}, ...}
        """
        for hook, stats in performance_data.items():
            score = (stats["views"] * 0.4) + (stats["retention"] * 10000 * 0.6)
            current = self.weights.get(hook, 1.0)
            # Exponential moving average adjustment
            self.weights[hook] = round(current * 0.8 + (score / 10000) * 0.2, 3)

        with open(self.metrics_path, "w") as f:
            json.dump(self.weights, f, indent=4)

    def get_optimal_hook(self) -> str:
        return max(self.weights, key=self.weights.get)