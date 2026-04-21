from backend.summarizer.context_generator import ContextGenerator
from backend.fusion.decision_fusion import DecisionFusion
from backend.rules.symbolic_engine import SymbolicEngine


def test_context_summarizer_format():
    cg = ContextGenerator()
    dets = [
        {"label": "pedestrian", "confidence": 0.95, "bbox": [100, 200, 130, 300], "centroid": [115, 250], "estimated_speed": 0.0},
        {"label": "vehicle", "confidence": 0.80, "bbox": [300, 220, 380, 300], "centroid": [340, 260], "estimated_speed": 0.0},
    ]
    s = cg.summarize(12, 40.0, dets)
    assert "Frame 12" in s and "speed 40.0 km/h" in s


def test_decision_fusion_prefers_override():
    fusion = DecisionFusion({"fusion": {"risk_penalty_per_close_obj": 0.2}})
    rule_result = {"override": "Brake", "flags": ["R1_pedestrian_distance_threshold"]}
    llm_json = {"recommended_action": "Continue", "ranked_actions": [{"action": "Continue", "score": 0.9}]}
    out = fusion.fuse(rule_result, llm_json, [])
    assert out["final_decision"] == "Brake" and out["source"] == "symbolic_override"

