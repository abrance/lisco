from pkg.client.spide.jimeng import JMImageToImageWorker
from pkg.util.config.config import config_manager


def test_upload_image_and_generate():
    session_id = config_manager.get_config().spider.jm_session_id
    worker = JMImageToImageWorker(session_id)
    image_urls = worker.single_image_to_images(
        "/opt/ggdownload/34b38060-9170-4671-8697-429c96813dc6-1-1.png",
        "##将这个女孩的头发改成充满科技感的蓝色",
        "",
        1024,
        1024,
        0.5,
    )
    print(image_urls)
