import configparser
from typing import Optional

from pydantic import BaseModel, Field

from pkg.constant.config import DEFAULT_CONFIG_PATH


class Server(BaseModel):
    host: str = Field(..., description="服务器地址")
    port: int = Field(..., description="服务器端口")


class LLM(BaseModel):
    base_url: str = Field(..., description="LLM 服务器地址")
    model: str = Field(..., description="LLM 模型")
    api_key: str = Field(..., description="LLM API Key")
    app_code: Optional[str] = Field(description="LLM 应用编码")


class Spider(BaseModel):
    jm_session_id: Optional[str] = Field(description="JM Session ID")


class DB(BaseModel):
    host: str = Field(..., description="数据库地址")
    port: int = Field(..., description="数据库端口")
    user: str = Field(..., description="数据库用户名")
    password: str = Field(..., description="数据库密码")
    db_name: str = Field(..., description="数据库名称")


class Storage(BaseModel):
    image_storage_path: str = Field(..., description="图片存储路径")


class LiscoConfig(BaseModel):
    server: Server = Field(..., description="服务器配置")
    llm: LLM = Field(..., description="LLM 配置")
    spider: Spider = Field(..., description="爬虫配置")
    db: DB = Field(..., description="数据库配置")
    storage: Storage = Field(..., description="存储配置")


class ConfigManager:
    def __init__(self):
        self.config = None
        self.config_parser = None
        self.init_config()

    def init_config(self):
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(DEFAULT_CONFIG_PATH)
        self.config_parser.read(DEFAULT_CONFIG_PATH)

        try:
            server_host = self.config_parser.get("server", "host")
            server_port = self.config_parser.getint("server", "port")
            api_key = self.config_parser.get("llm", "api_key")
            base_url = self.config_parser.get("llm", "base_url")
            model = self.config_parser.get("llm", "model")
            app_code = self.config_parser.get("llm", "app_code", fallback=None)
            jm_session_id = self.config_parser.get("spider", "jm_session_id", fallback=None)
            db_host = self.config_parser.get("db", "host")
            db_port = self.config_parser.getint("db", "port")
            db_user = self.config_parser.get("db", "user")
            db_password = self.config_parser.get("db", "password")
            db_name = self.config_parser.get("db", "db_name")
            image_storage_path = self.config_parser.get("storage", "image_storage_path")
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            raise RuntimeError(f"Missing config section or key: {e}")

        self.config = LiscoConfig(
            server=Server(host=server_host, port=server_port),
            llm=LLM(
                api_key=api_key,
                base_url=base_url,
                model=model,
                app_code=app_code,
            ),
            spider=Spider(
                jm_session_id=jm_session_id
            ),
            db=DB(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                db_name=db_name,
            ),
            storage=Storage(
                image_storage_path=image_storage_path
            ),
        )

    def get_config(self) -> LiscoConfig:
        if not self.config:
            raise RuntimeError("Config not initialized")
        return self.config


config_manager = ConfigManager()
