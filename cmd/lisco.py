from pkg.app.metric import metric_app_server
from pkg.server.http.server import WebServerLoader


def init_webserver():
    webserver = WebServerLoader(host='127.0.0.1', port=18000)
    webserver.register_server([metric_app_server])
    webserver.start()


def main():
    init_webserver()

if __name__ == '__main__':
    main()