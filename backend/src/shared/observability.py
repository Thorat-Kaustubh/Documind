import time
import logging
from typing import Dict, Any, Optional
from backend.src.shared.performance import PerformanceOptimizer

try:
    from prometheus_client import Counter, Histogram
    
    QUERY_LATENCY = Histogram('documind_query_latency_seconds', 'Time spent processing queries', ['model', 'intent'])
    QUERY_COST = Counter('documind_query_cost_dollars', 'Estimated cost of LLM queries', ['model'])
    QUERY_ERRORS = Counter('documind_query_errors_total', 'Number of failed queries', ['model'])
    QUERY_COUNT = Counter('documind_query_total', 'Total number of queries', ['model'])
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

logger = logging.getLogger("documind.observability")

class ObservabilityManager:
    """
    SECTION 11: OBSERVABILITY LAYER
    Tracks Latency, Cost, Model Usage, and Error Rates.
    Future: Export to OpenTelemetry/Prometheus.
    """
    def __init__(self):
        self.optimizer = PerformanceOptimizer()
        self.metrics_log = []

    def start_trace(self, query: str) -> Dict[str, Any]:
        return {
            "query": query,
            "start_time": time.time(),
            "steps": []
        }

    def record_step(self, trace: Dict[str, Any], step_name: str, duration: float, metadata: Optional[Dict[str, Any]] = None):
        trace["steps"].append({
            "name": step_name,
            "duration": duration,
            "metadata": metadata or {}
        })

    def complete_trace(self, trace: Dict[str, Any], response: Dict[str, Any], model: str):
        end_time = time.time()
        total_latency = end_time - trace["start_time"]
        
        # Estimate cost (Simple token count heuristic)
        # Using context length from response if available
        input_tokens = len(str(trace.get("query", ""))) // 4
        output_tokens = len(str(response.get("summary", ""))) // 4
        
        cost = self.optimizer.calculate_cost(model, input_tokens, output_tokens)
        has_error = 1 if "error" in response else 0
        intent = response.get("intent", "UNKNOWN")
        
        if HAS_PROMETHEUS:
            QUERY_COUNT.labels(model=model).inc()
            QUERY_LATENCY.labels(model=model, intent=intent).observe(total_latency)
            QUERY_COST.labels(model=model).inc(cost)
            if has_error:
                QUERY_ERRORS.labels(model=model).inc()
        
        report = {
            "query": trace["query"],
            "latency": total_latency,
            "cost": cost,
            "model": model,
            "error_rate": has_error,
            "steps_count": len(trace["steps"])
        }
        
        # LOG FOR PRODUCTION AUDIT
        logger.info(f"OBSERVABILITY REPORT: Latency: {total_latency:.2f}s | Cost: ${cost:.6f} | Model: {model}")
        self.metrics_log.append(report)
        return report
