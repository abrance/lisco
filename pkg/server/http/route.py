from starlette.middleware.cors import CORSMiddleware


class Route:
    """
    web server 的 路由, 在这里管理路由
    中间件管理, 分为 global 和局部中间件, 局部中间件这里先不管
    """

    def __init__(self, server_app):
        """

        :param server_app: 类似 fastapp 和 flask app 概念
        """
        self.app = server_app

    def add_global_middleware(self):
        """
        添加默认的中间件
        :return:
        """
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def add_route(self):
        """
        添加路由
        :return:
        """
        self.app.include_router(
            # 添加路由
        )
