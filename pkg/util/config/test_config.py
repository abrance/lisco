from pkg.util.config.config import config_manager


def test_config():
    config = config_manager.get_config()
    assert config.llm.api_key