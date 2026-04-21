from backend.rules.symbolic_engine import SymbolicEngine

def test_rule_r2_red_light_override():
    cfg = {"rule_thresholds": {"pedestrian_distance_m": 2.0, "ego_speed_brake_kmh": 10}}
    eng = SymbolicEngine(cfg)
    ctx = {"ego_speed_kmh": 5, "red_light_detected": True}
    res = eng.evaluate(ctx)
    assert res["override"] == "Stop"
    assert "R2_red_light_detected" in res["flags"]


def test_rule_r3_veto_swerve_flag():
    cfg = {"rule_thresholds": {}}
    eng = SymbolicEngine(cfg)
    ctx = {
        "ego_speed_kmh": 30,
        "steering_maneuver_would_hit_oncoming_lane": True,
        "oncoming_traffic_close": True,
    }
    res = eng.evaluate(ctx)
    assert res["override"] in (None, "Brake", "Stop")  # R3 is a veto flag, not explicit override
    assert "R3_veto_swerve" in res["flags"]

