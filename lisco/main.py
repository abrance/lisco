from pkg.app.ai_agent import ai_agent_app_server
from pkg.app.image_generate import image_generate_app_server
from pkg.app.metric import metric_app_server
from pkg.app.resource import resource_app_server
from pkg.db.db import DBManager
from pkg.server.http.server import WebServerLoader
from pkg.util.config.config import config_manager


def init_webserver():
    config = config_manager.get_config()
    db_manager = DBManager(db_name=config.db.db_name, db_host=config.db.host, db_port=config.db.port, db_user=config.db.user, db_password=config.db.password)
    db_manager.connect()
    db_manager.init_db()
    webserver = WebServerLoader(host=config.server.host, port=config.server.port)
    webserver.register_server([metric_app_server, ai_agent_app_server, image_generate_app_server, resource_app_server])
    webserver.start()


def main():
    init_webserver()

if __name__ == '__main__':
    main()