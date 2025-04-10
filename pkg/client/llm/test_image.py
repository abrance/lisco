import pytest

from pkg.util.config.config import config_manager


@pytest.mark.skip
def test_image_2_image():
    from pkg.client.llm.image import ImageEditor
    image_editor = ImageEditor(config_manager.get_config().llm.api_key)
    resp = image_editor.image_2_image("将这个图片变为像素风格", "http://st1i24ia5.hn-bkt.clouddn.com/%E4%B8%89%E5%A7%A8.png?e=1744103103&token=0ctWTmjbTeXtGKwEjV6XOzQhnx8KwcpXyou-7UCF:I4p-ocnmGflR3LUDnnC_F1rinxE=")
    output = resp.get("output", {})
    if output:
        task_id = output.get("task_id")
        data = image_editor.check_task_status(task_id)
        print(data)