from pkg.app.metric import metric_app_server
from pkg.server.http.server import WebServerLoader
from pkg.util.config.config import config_manager


def init_webserver():
    config = config_manager.get_config()
    webserver = WebServerLoader(host=config.server.host, port=config.server.port)
    webserver.register_server([metric_app_server])
    webserver.start()


def main():
    init_webserver()

if __name__ == '__main__':
    main()