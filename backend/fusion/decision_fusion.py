from typing import Dict, Any, List

ACTIONS = ["Brake","SwerveLeft","SwerveRight","SlowDown","Continue","Stop"]

class DecisionFusion:
    def __init__(self, config: Dict[str, Any]):
        self.cfg = config

    def score_risk(self, detections: List[Dict[str, Any]]) -> float:
        close_objs = 0
        for d in detections:
            x1,y1,x2,y2 = d["bbox"]
            height = max(y2 - y1, 1.0)
            dist_m = 100.0/height
            if dist_m < 5.0:
                close_objs += 1
        return close_objs * float(self.cfg.get("fusion", {}).get("risk_penalty_per_close_obj", 0.1))

    def fuse(self, rule_result: Dict[str, Any], llm_json: Dict[str, Any], detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        if rule_result.get("override"):
            return {"final_decision": rule_result["override"], "source": "symbolic_override"}
        risk_pen = self.score_risk(detections)
        ranked = llm_json.get("ranked_actions", [])
        if ranked:
            # Adjust top score by risk penalty for non-braking actions
            top = ranked[0]
            if top.get("action") not in ("Brake", "Stop"):
                top["score"] = max(0.0, top.get("score", 0) - risk_pen)
            return {"final_decision": top.get("action", "SlowDown"), "source": "llm_fusion"}
        return {"final_decision": llm_json.get("recommended_action", "SlowDown"), "source": "llm_fallback"}

