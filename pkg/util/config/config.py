import configparser

from pydantic import BaseModel, Field

from pkg.constant.config import DEFAULT_CONFIG_PATH


class ConfigManager:
    def __init__(self):
        self.config = None
        self.config_parser = None
        self.init_config()

    def init_config(self):
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(DEFAULT_CONFIG_PATH)
        self.config_parser.read(DEFAULT_CONFIG_PATH)

        server_host = self.config_parser.get('server', 'host')
        server_port = self.config_parser.getint('server', 'port')
        api_key = self.config_parser.get('llm', 'api_key')
        self.config = LiscoConfig(
            server=Server(host=server_host, port=server_port),
            llm=LLM(api_key=api_key)
        )

    def get_config(self):
        return self.config


class Server(BaseModel):
    host: str = Field(..., description="服务器地址")
    port: int = Field(..., description="服务器端口")

class LLM(BaseModel):
    api_key: str = Field(..., description="LLM API Key")

class LiscoConfig(BaseModel):
    server: Server = Field(..., description="服务器配置")
    llm: LLM = Field(..., description="LLM 配置")


config_manager = ConfigManager()