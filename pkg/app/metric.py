from pkg.server.http.server import AppServer


class MetricAppServer(AppServer):
    def __init__(self):
        super().__init__("/metric")


metric_app_server = MetricAppServer()
metric_app = metric_app_server.get_app()


@metric_app.get("/")
def read_root():
    return {"Hello": "World, metric"}