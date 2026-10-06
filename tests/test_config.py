from pathlib import Path

from vmar_ps.config import experiment_id, resolve_agents, load_config


def test_resolve_agents_cycles_profiles():
    config = {
        "num_agents": 6,
        "cycle_agent_pool": True,
        "agents": [{"agent_id": "a1"}, {"agent_id": "a2"}],
    }
    agents = resolve_agents(config)
    assert len(agents) == 6
    assert len({a["agent_id"] for a in agents}) == 6


def test_experiment_id_is_deterministic():
    config = {"seed": 7, "method": "single_pass"}
    assert experiment_id(config, "abc") == experiment_id(config, "abc")


def test_load_config_expands_yaml(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "secret")
    path = tmp_path / "config.yaml"
    placeholder = "$" + "{GEMINI_API_KEY}"
    path.write_text(
        "api_key: " + placeholder + "\n"
        "num_agents: 1\n"
        "agents:\n  - agent_id: a1\n",
        encoding="utf-8",
    )
    loaded = load_config(path)
    assert loaded["api_key"] == "secret"
