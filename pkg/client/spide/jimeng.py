import time
from typing import List

import requests
from pydantic import BaseModel, Field

from pkg.client.spide.images import (
    get_model,
    get_credit,
    receive_credit,
    build_abilities,
)
from pkg.client.spide.jimeng_core import (
    generate_cookie,
    request,
    DEFAULT_ASSISTANT_ID,
    API_IMAGE_GENERATION_FAILED,
    API_CONTENT_FILTERED,
    DRAFT_VERSION,
    json_encode,
    generate_uuid,
    url_encode,
)

import hmac
import zlib
import logging
import random
import hashlib

logging.basicConfig(
    format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
    level=logging.INFO,
)

day_n = 1


def hash256(msg):
    return hashlib.sha256(msg.encode("utf-8")).hexdigest()


def hmac_hash256(key, msg):
    if isinstance(key, str):
        return hmac.new(key.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256)
    elif isinstance(key, hmac.HMAC):
        return hmac.new(key.digest(), msg.encode("utf-8"), hashlib.sha256)


def fileCRC32(file_buffer):
    return hex(zlib.crc32(file_buffer) & 0xFFFFFFFF)[2:]


def u(params):
    new_params = sorted(params.items(), key=lambda x: x[0])
    new_params = [f"{k}={v}" for k, v in new_params]
    return "&".join(new_params)


class ImageRequestBuilder:
    def __init__(self, e, t, api, method="GET", params=None, data=None):
        self.t = t
        self.e = e
        self.api = api
        self.method = method
        self.params = params
        self.data = data

    def getAuthorization(self):
        return (
            f"AWS4-HMAC-SHA256 Credential={self.e['access_key_id']}/{self.t[0:8]}/cn-north-1/imagex/aws4_request, "
            f"SignedHeaders=x-amz-date;x-amz-security-token, Signature={self.signature()}"
        )

    def signature(self):
        r = self.getSigningKey()
        return hmac_hash256(r, self.stringToSign()).hexdigest()

    def getSigningKey(self, r="cn-north-1", n="imagex"):
        o = hmac_hash256("AWS4" + self.e["secret_access_key"], str(self.t[0:8]))
        i = hmac_hash256(o, str(r))
        s = hmac_hash256(i, str(n))
        return hmac_hash256(s, "aws4_request")

    def stringToSign(self):
        t = []
        t.append("AWS4-HMAC-SHA256")
        t.append(self.t)
        t.append(self.credentialString())
        t.append(hash256(self.canonicalString()))
        return "\n".join(t)

    def credentialString(self, region="cn-north-1", serviceName="imagex"):
        return "/".join([self.t[0:8], region, serviceName, "aws4_request"])

    def canonicalString(self):
        e = []
        e.append(self.method)
        e.append("/")
        e.append(u(self.params))
        e.append(self.canonicalHeaders())
        e.append(self.signedHeaders())
        e.append(self.hexEncodedBodyHash())
        return "\n".join(e)

    def canonicalHeaders(self):
        return f"x-amz-date:{self.t}\nx-amz-security-token:{self.e['session_token']}\n"

    def signedHeaders(self):
        return "x-amz-date;x-amz-security-token"

    def hexEncodedBodyHash(self):
        return hash256("")


def get_upload_token(cookie):
    api = "https://jimeng.jianying.com/mweb/v1/get_upload_token?aid=513695&da_version=3.1.5"
    headers = {
        "cookie": cookie.strip(),
    }
    r = requests.post(api, headers=headers)
    print(r.json())
    if r.status_code == 200 and r.json()["errmsg"] == "success":
        return r.json()["data"]
    else:
        logging.error("获取token失败", r.text)
        return None


def random_str(n):
    return "".join(random.sample("zyxwvutsrqponmlkjihgfedcba0123456789", n))


def get_as_pic(image_path):
    try:
        with open(image_path, "rb") as file:
            image_data = file.read()
            return image_data
    except Exception as e:
        logging.error(e)
        return None


class UploadImageInfo(BaseModel):
    host: str = Field(..., title="上传图片的host", description="上传图片的host")
    uri: str = Field(..., title="上传图片的uri", description="上传图片的uri")
    auth: str = Field(..., title="上传图片的auth", description="上传图片的auth")

    def get_upload_url(self):
        return f"https://{self.host}/{self.uri}"


class ImageInfo(BaseModel):
    path: str = Field(..., title="图片路径", description="图片路径")
    content_type: str = Field(
        "application/octet-stream", title="图片类型", description="图片类型"
    )
    content: bytes = Field(..., title="图片内容", description="图片内容")
    checksum: str = Field(..., title="校验和", description="校验和")
    length: int = Field(..., title="图片长度", description="图片长度")

    @classmethod
    def build(cls, path):
        try:
            with open(path, "rb") as file:
                image_data = file.read()
                if image_data:
                    return cls(
                        path=path,
                        content=image_data,
                        checksum=fileCRC32(image_data),
                        length=len(image_data),
                    )
                else:
                    return None

        except Exception as e:
            logging.error(e)
            return None


class JMImageUploader:
    def __init__(self, session_id, image_path):
        self.session_id = session_id
        self.image_info = ImageInfo.build(image_path)

    def get_upload_address(self):
        cookie = generate_cookie(self.session_id)
        upload_token = get_upload_token(cookie)
        time_now_str = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        params = {
            "Action": "ApplyImageUpload",
            "Version": "2018-08-01",
            "ServiceId": "tb4s082cfz",
            "s": random_str(11),
        }
        r = ImageRequestBuilder(
            upload_token,
            time_now_str,
            "https://imagex.bytedanceapi.com/",
            method="GET",
            params=params,
        )
        headers = {
            "authorization": r.getAuthorization(),
            "x-amz-date": time_now_str,
            "x-amz-security-token": upload_token["session_token"],
        }
        resp = requests.get(r.api, params=params, headers=headers).json()
        if "Result" not in resp:
            raise Exception("获取上传地址失败")

        upload_image_info = UploadImageInfo(
            host=resp["Result"]["UploadAddress"]["UploadHosts"][0],
            uri=resp["Result"]["UploadAddress"]["StoreInfos"][0]["StoreUri"],
            auth=resp["Result"]["UploadAddress"]["StoreInfos"][0]["Auth"],
        )
        return upload_image_info

    def upload(self):
        upload_image_info = self.get_upload_address()
        resp_upload = requests.put(
            upload_image_info.get_upload_url(),
            data=self.image_info.content,
            headers={
                "authorization": upload_image_info.auth,
                "content-length": str(self.image_info.length),
                "content-Type": self.image_info.content_type,
                "content-crc32": self.image_info.checksum,
            },
        )
        assert resp_upload.status_code == 200
        return upload_image_info


class JMImageToImageWorker:
    def __init__(self, session_id):
        self.session_id = session_id

    @classmethod
    def generate_images(
        cls,
        model: str,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        sample_strength: float = 0.5,
        negative_prompt: str = "",
        refresh_token: str = None,
        image_uri: str = None,
    ) -> List[str]:
        """生成图像

        Args:
            model: 模型名称
            prompt: 提示词
            width: 图像宽度
            height: 图像高度
            sample_strength: 精细度
            negative_prompt: 反向提示词
            refresh_token: 刷新token
            image_uri: 原始图像URL

        Returns:
            List[str]: 图像URL列表

        Raises:
            API_IMAGE_GENERATION_FAILED: 图像生成失败
            API_CONTENT_FILTERED: 内容被过滤
        """
        # 参数验证
        if not prompt or not isinstance(prompt, str):
            raise ValueError("prompt must be a non-empty string")
        if not refresh_token:
            raise ValueError("refresh_token is required")

        # 获取实际模型
        _model = get_model(model)

        # 检查积分
        credit_info = get_credit(refresh_token)
        if credit_info.get("totalCredit", 0) <= 0:
            receive_credit(refresh_token)

        # 生成组件ID
        component_id = generate_uuid()
        generate_type = "blend" if image_uri else "generate"
        # 发送生成请求
        result = request(
            "post",
            "/mweb/v1/aigc_draft/generate",
            refresh_token,
            params={
                "babi_param": url_encode(
                    json_encode(
                        {
                            "scenario": "image_video_generation",
                            "feature_key": "to_image_referenceimage_generate",
                            "feature_entrance": "to_image",
                            "feature_entrance_detail": f"to_image-{_model}",
                        }
                    )
                )
            },
            data={
                "extend": {
                    "root_model": _model,
                    "template_id": "",
                },
                "submit_id": generate_uuid(),
                "metrics_extra": json_encode(
                    {
                        "templateId": "",
                        "generateCount": 1,
                        "promptSource": "custom",
                        "templateSource": "",
                        "lastRequestId": "",
                        "originRequestId": "",
                    }
                ),
                "draft_content": json_encode(
                    {
                        "type": "draft",
                        "id": generate_uuid(),
                        "min_version": DRAFT_VERSION,
                        "is_from_tsn": True,
                        "version": DRAFT_VERSION,
                        "main_component_id": component_id,
                        "component_list": [
                            {
                                "type": "image_base_component",
                                "id": component_id,
                                "min_version": DRAFT_VERSION,
                                "generate_type": generate_type,  # blend  generate  后面 abilities 需要填入不同的结构
                                "aigc_mode": "workbench",
                                "abilities": build_abilities(
                                    prompt,
                                    image_uri,
                                    _model,
                                    sample_strength,
                                    height,
                                    width,
                                    negative_prompt,
                                ),
                            }
                        ],
                    }
                ),
                "http_common_info": {"aid": int(DEFAULT_ASSISTANT_ID)},
            },
        )

        # 获取历史记录ID
        history_id = result.get("aigc_data", {}).get("history_record_id")
        if not history_id:
            raise API_IMAGE_GENERATION_FAILED("记录ID不存在")

        # 轮询获取结果
        status = 20
        fail_code = None
        item_list = []

        while status == 20:
            time.sleep(1)
            result = request(
                "post",
                "/mweb/v1/get_history_by_ids",
                refresh_token,
                data={
                    "history_ids": [history_id],
                    "image_info": {
                        "width": 2048,
                        "height": 2048,
                        "format": "webp",
                        "image_scene_list": [
                            {
                                "scene": "smart_crop",
                                "width": 360,
                                "height": 360,
                                "uniq_key": "smart_crop-w:360-h:360",
                                "format": "webp",
                            },
                            {
                                "scene": "smart_crop",
                                "width": 480,
                                "height": 480,
                                "uniq_key": "smart_crop-w:480-h:480",
                                "format": "webp",
                            },
                            {
                                "scene": "smart_crop",
                                "width": 720,
                                "height": 720,
                                "uniq_key": "smart_crop-w:720-h:720",
                                "format": "webp",
                            },
                            {
                                "scene": "smart_crop",
                                "width": 720,
                                "height": 480,
                                "uniq_key": "smart_crop-w:720-h:480",
                                "format": "webp",
                            },
                            {
                                "scene": "smart_crop",
                                "width": 360,
                                "height": 240,
                                "uniq_key": "smart_crop-w:360-h:240",
                                "format": "webp",
                            },
                            {
                                "scene": "smart_crop",
                                "width": 240,
                                "height": 320,
                                "uniq_key": "smart_crop-w:240-h:320",
                                "format": "webp",
                            },
                            {
                                "scene": "smart_crop",
                                "width": 480,
                                "height": 640,
                                "uniq_key": "smart_crop-w:480-h:640",
                                "format": "webp",
                            },
                            {
                                "scene": "normal",
                                "width": 2400,
                                "height": 2400,
                                "uniq_key": "2400",
                                "format": "webp",
                            },
                            {
                                "scene": "normal",
                                "width": 1080,
                                "height": 1080,
                                "uniq_key": "1080",
                                "format": "webp",
                            },
                            {
                                "scene": "normal",
                                "width": 720,
                                "height": 720,
                                "uniq_key": "720",
                                "format": "webp",
                            },
                            {
                                "scene": "normal",
                                "width": 480,
                                "height": 480,
                                "uniq_key": "480",
                                "format": "webp",
                            },
                            {
                                "scene": "normal",
                                "width": 360,
                                "height": 360,
                                "uniq_key": "360",
                                "format": "webp",
                            },
                        ],
                    },
                    "http_common_info": {"aid": int(DEFAULT_ASSISTANT_ID)},
                },
            )

            record = result.get(history_id)
            if not record:
                raise API_IMAGE_GENERATION_FAILED("记录不存在")

            status = record.get("status")
            fail_code = record.get("fail_code")
            item_list = record.get("item_list", [])

        if status == 30:
            if fail_code == "2038":
                raise API_CONTENT_FILTERED()
            raise API_IMAGE_GENERATION_FAILED()

        # 提取图片URL
        return [
            item.get("image", {}).get("large_images", [{}])[0].get("image_url")
            or item.get("common_attr", {}).get("cover_url")
            for item in item_list
            if item
        ]

    def single_image_to_images(
        self, image_path, prompt, negative_prompt, width, height, sample_strength
    ):
        uploader = JMImageUploader(self.session_id, image_path)
        upload_image_info = uploader.upload()
        urls = self.generate_images(
            model="jimeng-2.0-pro",
            prompt=prompt,
            width=width,
            height=height,
            sample_strength=sample_strength,
            negative_prompt=negative_prompt,
            refresh_token=self.session_id,
            image_uri=upload_image_info.uri,
        )
        return urls
