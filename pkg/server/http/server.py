from typing import List

from fastapi import FastAPI
import uvicorn


class AppServer:
    """
    对应技术设计的 server , 组装 app

    api:
        - get_app
            期望外层拿到 app 去注册路由
            期望 app 被 mount 到父 app
    """
    def __init__(self, base_url):
        self.base_url = base_url
        self.name = base_url
        self.fastapi_app = FastAPI()

    def get_app(self):
        return self.fastapi_app



class WebServerLoader:
    """
    相当于 server listener 所在, 加载 host port
    api:
        - 主 app 在此定义, 获取此 app 去注册路由, 加载 子 app 都行
        - start 启动 http server
        - stop 停止 http server
    """
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.fastapi_app = FastAPI()
        self.uvicorn_server = None
        self.app_servers = {}

    def start(self):
        # 启动 Uvicorn 服务器
        config = uvicorn.Config(self.fastapi_app, host=self.host, port=self.port)
        self.uvicorn_server = uvicorn.Server(config)
        self.uvicorn_server.run()

    def stop(self):
        if self.uvicorn_server:
            self.uvicorn_server.should_exit = True
            self.uvicorn_server.force_exit = True

    def get_app(self):
        """
        获取 fastapp , 具体路由不再 WebServer 中管理
        :return:
        """
        return self.fastapi_app

    def register_server(self, app_server_list: List[AppServer]):
        """
        注册 app_server
        :param app_server_list:
        :return:
        """
        app_server_dc = {app.base_url: app for app in app_server_list}
        self.app_servers.update(app_server_dc)


