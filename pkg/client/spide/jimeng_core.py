import uuid
import time
import hashlib
import random
from urllib.parse import quote
from typing import List, Any, Dict, Optional
import requests
import logging

import gzip
import brotli
import json
from io import BytesIO


class JMException(Exception):
    """即梦API异常基类"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


EXCEPTIONS = {
    "API_REQUEST_PARAMS_INVALID": [-2000, '请求参数非法'],
    "API_REQUEST_FAILED": [-2001, '请求失败'],
    "API_TOKEN_EXPIRES": [-2002, 'Token已失效'],
    "API_FILE_URL_INVALID": [-2003, '远程文件URL非法'],
    "API_FILE_EXECEEDS_SIZE": [-2004, '远程文件超出大小'],
    "API_CHAT_STREAM_PUSHING": [-2005, '已有对话流正在输出'],
    "API_CONTENT_FILTERED": [-2006, '内容由于合规问题已被阻止生成'],
    "API_IMAGE_GENERATION_FAILED": [-2007, '图像生成失败'],
    "API_VIDEO_GENERATION_FAILED": [-2008, '视频生成失败'],
    "API_IMAGE_GENERATION_INSUFFICIENT_POINTS": [-2009, '即梦积分不足']
}

class API_REQUEST_PARAMS_INVALID(JMException):
    """请求参数非法"""
    def __init__(self, message: str):
        super().__init__(-2000, "请求参数非法")

class API_REQUEST_FAILED(JMException):
    """请求失败"""
    def __init__(self, message: str):
        super().__init__(-2001, "请求失败")

class API_TOKEN_EXPIRES(JMException):
    """Token已失效"""
    def __init__(self, message: str):
        super().__init__(-2002, "Token已失效")

class API_FILE_URL_INVALID(JMException):
    """远程文件URL非法"""
    def __init__(self, message: str):
        super().__init__(-2003, "远程文件URL非法")

class API_FILE_EXECEEDS_SIZE(JMException):
    """远程文件超出大小"""
    def __init__(self, message: str):
        super().__init__(-2004, "远程文件超出大小")

class API_CHAT_STREAM_PUSHING(JMException):
    """已有对话流正在输出"""
    def __init__(self, message: str):
        super().__init__(-2005, "已有对话流正在输出")

class API_CONTENT_FILTERED(JMException):
    """内容由于合规问题已被阻止生成"""
    def __init__(self, message: str):
        super().__init__(-2006, "内容由于合规问题已被阻止生成")

class API_VIDEO_GENERATION_FAILED(JMException):
    """视频生成失败"""
    def __init__(self, message: str):
        super().__init__(-2008, "视频生成失败")

class API_IMAGE_GENERATION_FAILED(JMException):
    """图像生成失败"""
    def __init__(self, message: str):
        super().__init__(-2007, "图像生成失败")

class API_IMAGE_GENERATION_INSUFFICIENT_POINTS(JMException):
    """积分不足"""
    def __init__(self, message: str):
        super().__init__(-2009, "即梦积分不足")


def is_string(value: Any) -> bool:
    """判断是否为字符串"""
    return isinstance(value, str)

def is_array(value: Any) -> bool:
    """判断是否为数组"""
    return isinstance(value, (list, tuple))

def is_finite(value: Any) -> bool:
    """判断是否为有限数字"""
    try:
        float_val = float(value)
        return not (float_val == float('inf') or float_val == float('-inf') or float_val != float_val)
    except (TypeError, ValueError):
        return False

def default_to(value: Any, default_value: Any) -> Any:
    """设置默认值"""
    return default_value if value is None else value

def get_timestamp() -> int:
    """获取当前时间戳

    Returns:
        int: 时间戳(秒)
    """
    return int(time.time())

def generate_uuid(with_hyphen: bool = True) -> str:
    """生成UUID

    Args:
        with_hyphen: 是否包含连字符

    Returns:
        str: UUID字符串
    """
    _uuid = str(uuid.uuid4())
    return _uuid if with_hyphen else _uuid.replace('-', '')

def md5(text: str) -> str:
    """计算MD5

    Args:
        text: 文本

    Returns:
        str: MD5字符串
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def generate_device_id() -> int:
    """生成设备ID

    Returns:
        int: 设备ID
    """
    return int(random.random() * 999999999999999999 + 7000000000000000000)

def generate_web_id() -> int:
    """生成网页ID

    Returns:
        int: 网页ID
    """
    return int(random.random() * 999999999999999999 + 7000000000000000000)

def token_split(auth: str) -> List[str]:
    """分割token

    Args:
        auth: Authorization头部值

    Returns:
        List[str]: token列表
    """
    if not auth:
        return []
    auth = auth.replace('Bearer', '').strip()
    return [t.strip() for t in auth.split(',') if t.strip()]

def json_encode(obj: object) -> str:
    """JSON编码

    Args:
        obj: 对象

    Returns:
        str: JSON字符串
    """
    return json.dumps(obj, separators=(',', ':'))

def url_encode(text: str) -> str:
    """URL编码

    Args:
        text: 文本

    Returns:
        str: URL编码字符串
    """
    return quote(text)



# 常量定义
MODEL_NAME = "jimeng"
DEFAULT_ASSISTANT_ID = "513695"
VERSION_CODE = "5.8.0"
PLATFORM_CODE = "7"
DEVICE_ID = generate_device_id()
WEB_ID = generate_web_id()
USER_ID = generate_uuid(False)
MAX_RETRY_COUNT = 3
RETRY_DELAY = 5000
FILE_MAX_SIZE = 100 * 1024 * 1024

# 请求头
FAKE_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-language": "zh-CN,zh;q=0.9",
    "Cache-control": "no-cache",
    "Last-event-id": "undefined",
    "Appid": DEFAULT_ASSISTANT_ID,
    "Appvr": VERSION_CODE,
    "Origin": "https://jimeng.jianying.com",
    "Pragma": "no-cache",
    "Priority": "u=1, i",
    "Referer": "https://jimeng.jianying.com",
    "Pf": PLATFORM_CODE,
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

def acquire_token(refresh_token: str) -> str:
    """获取访问token

    目前jimeng的access_token是固定的，暂无刷新功能

    Args:
        refresh_token: 用于刷新access_token的refresh_token

    Returns:
        str: access_token
    """
    return refresh_token


def generate_cookie(token: str) -> str:
    """生成Cookie

    Args:
        token: 访问token

    Returns:
        str: Cookie字符串
    """
    return f"sessionid={token}; sessionid_ss={token}; sid_tt={token}; uid_tt={token}; uid_tt_ss={token}"


def check_result(response: requests.Response) -> Dict[str, Any]:
    """检查请求结果

    Args:
        response: 请求响应

    Returns:
        Dict: 响应数据

    Raises:
        API_IMAGE_GENERATION_INSUFFICIENT_POINTS: 积分不足
        API_REQUEST_FAILED: 请求失败
    """
    result = response.json()
    ret, errmsg, data = result.get('ret'), result.get('errmsg'), result.get('data')

    if not is_finite(ret):
        return result

    if ret == '0':
        return data

    if ret == '5000':
        raise API_IMAGE_GENERATION_INSUFFICIENT_POINTS(f"即梦积分可能不足，{errmsg}")

    raise API_REQUEST_FAILED(f"请求jimeng失败: {errmsg}")


def request(
        method: str,
        uri: str,
        refresh_token: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
) -> Dict[str, Any]:
    """请求即梦API

    Args:
        method: 请求方法
        uri: 请求路径
        refresh_token: 刷新token
        params: URL参数
        data: 请求数据
        headers: 请求头
        **kwargs: 其他参数

    Returns:
        Dict: 响应数据
    """
    token = acquire_token(refresh_token)
    device_time = get_timestamp()
    sign = md5(f"9e2c|{uri[-7:]}|{PLATFORM_CODE}|{VERSION_CODE}|{device_time}||11ac")

    _headers = {
        **FAKE_HEADERS,
        "Cookie": generate_cookie(token),
        "Device-Time": str(device_time),
        "Sign": sign,
        "Sign-Ver": "1"
    }
    if headers:
        _headers.update(headers)

    _params = {
        "aid": DEFAULT_ASSISTANT_ID,
        "device_platform": "web",
        "region": "CN",
        "web_id": WEB_ID
    }
    if params:
        _params.update(params)

    response = requests.request(
        method=method.lower(),
        url=f"https://jimeng.jianying.com{uri}",
        params=_params,
        json=data,
        headers=_headers,
        timeout=15,
        verify=True,
        **kwargs
    )

    # 检查响应
    try:
        logging.debug(f'请求uri:{uri},响应状态:{response.status_code}')
        # 检查Content-Encoding
        logging.debug(f'请求uri:{uri},响应状态:{response.status_code}')
        # 检查Content-Encoding并解压
        try:
            content = decompress_response(response)
            logging.debug(f'响应结果:{content}')
        except Exception as e:
            logging.debug(f'解压失败,使用原始响应: {str(e)}')
            content = response.text
            logging.debug(f'响应结果:{content}')
        # result = response.json()
        result = json.loads(content)
    except:
        raise API_REQUEST_FAILED("响应格式错误")

    ret = result.get('ret')
    if ret is None:
        return result

    if str(ret) == '0':
        return result.get('data', {})

    if str(ret) == '5000':
        raise API_IMAGE_GENERATION_INSUFFICIENT_POINTS(f"[无法生成图像]: 即梦积分可能不足，{result.get('errmsg')}")

    raise API_REQUEST_FAILED(f"[请求jimeng失败]: {result.get('errmsg')}")


def decompress_response(response: requests.Response) -> str:
    """解压响应内容

    Args:
        response: 请求响应

    Returns:
        str: 解压后的内容
    """
    content = response.content
    encoding = response.headers.get('Content-Encoding', '').lower()

    if encoding == 'gzip':
        buffer = BytesIO(content)
        with gzip.GzipFile(fileobj=buffer) as f:
            content = f.read()
    elif encoding == 'br':
        content = brotli.decompress(content)
    # 如果之后需要支持其他压缩格式(如zstd),可以在这里添加

    return content.decode('utf-8')


# 默认模型
# 草稿版本
# 模型映射
DEFAULT_MODEL = "jimeng-2.1"
DRAFT_VERSION = "3.0.2"
MODEL_MAP = {
    "jimeng-2.1": "high_aes_general_v21_L:general_v2.1_L",
    "jimeng-2.0-pro": "high_aes_general_v20_L:general_v2.0_L",
    "jimeng-2.0": "high_aes_general_v20:general_v2.0",
    "jimeng-1.4": "high_aes_general_v14:general_v1.4",
    "jimeng-xl-pro": "text2img_xl_sft",
}
