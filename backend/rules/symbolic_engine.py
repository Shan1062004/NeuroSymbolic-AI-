from typing import Dict, Any, List

class SymbolicEngine:
    def __init__(self, config: Dict[str, Any]):
        self.cfg = config

    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        flags: List[str] = []
        override = None
        thr = self.cfg.get("rule_thresholds", {})
        ped_thr = float(thr.get("pedestrian_distance_m", 2.0))
        brake_speed = float(thr.get("ego_speed_brake_kmh", 10.0))

        # Extract from context
        ego_speed = float(context.get("ego_speed_kmh", 0))
        red_light = bool(context.get("red_light_detected", False))
        oncoming_close = bool(context.get("oncoming_traffic_close", False))
        steer_would_hit_oncoming = bool(context.get("steering_maneuver_would_hit_oncoming_lane", False))
        nearest_ped_dist = context.get("nearest_pedestrian_distance_m")

        if nearest_ped_dist is not None and nearest_ped_dist < ped_thr and ego_speed > brake_speed:
            flags.append("R1_pedestrian_distance_threshold")
            override = "Brake"
        if red_light:
            flags.append("R2_red_light_detected")
            override = "Stop"
        if steer_would_hit_oncoming and oncoming_close:
            flags.append("R3_veto_swerve")

        return {"override": override, "flags": flags}

