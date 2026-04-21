from backend.rules.symbolic_engine import SymbolicEngine

def test_rule_r1_override():
    cfg = {"rule_thresholds": {"pedestrian_distance_m": 2.0, "ego_speed_brake_kmh": 10}}
    eng = SymbolicEngine(cfg)
    ctx = {"ego_speed_kmh": 20, "nearest_pedestrian_distance_m": 1.0}
    res = eng.evaluate(ctx)
    assert res["override"] == "Brake"
    assert "R1_pedestrian_distance_threshold" in res["flags"]

