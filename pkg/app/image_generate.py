from fastapi import Form, UploadFile, File
from pydantic import BaseModel, Field

from pkg.client.spide.jimeng import JMImageToImageWorker
from pkg.server.http.server import AppServer
from pkg.util.config.config import config_manager

APP_NAME = "image_generate"


class ImageGenerateAppServer(AppServer):
    def __init__(self):
        super().__init__("/" + APP_NAME)


image_generate_app_server = ImageGenerateAppServer()
image_generate_app = image_generate_app_server.get_app()


@image_generate_app.get("/")
def read_root():
    return {"Hello": "World, image generate"}


class CreateImageBody(BaseModel):
    prompt: str = Field(..., description="用户请求字符串")
    height: int = Field(1024, description="图片高度")
    width: int = Field(1024, description="图片宽度")
    negative_prompt: str = Field("", description="反向提示词")
    sample_strength: float = Field(0.5, description="采样强度")


@image_generate_app.post("/create")
def create_image(
    prompt: str = Form(..., description="用户请求字符串"),
    height: int = Form(1024, description="图片高度"),
    width: int = Form(1024, description="图片宽度"),
    negative_prompt: str = Form("", description="反向提示词"),
    sample_strength: float = Form(0.5, description="采样强度"),
    image_file: UploadFile = File(..., description="要上传的参考图片文件"),
):
    # 在这里处理接收到的数据和文件
    # 例如，可以读取文件内容：
    session_id = config_manager.get_config().spider.jm_session_id
    image_storage_path = config_manager.get_config().storage.image_storage_path
    file_location = f"{image_storage_path}/{image_file.filename}"
    # 读取并保存上传的文件
    with open(file_location, "wb") as file_object:
        contents = image_file.read()
        file_object.write(contents)
    worker = JMImageToImageWorker(session_id)
    image_urls = worker.single_image_to_images(
        file_location,
        prompt,
        negative_prompt,
        width,
        height,
        sample_strength,
    )

    return {"filename": image_file.filename, "content_type": image_file.content_type}
