import ast
import json
from enum import Enum
from pprint import pformat
from random import randint

from langchain_core.tools import StructuredTool, ToolException
from pydantic import BaseModel, Field, ValidationError

from pkg.client.llm.util import ToolUtils, exception_to_tool_exception


class OutputFormatEnum(Enum):
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    INI = "ini"
    XML = "xml"
    HTML = "html"
    MARKDOWN = "markdown"
    TEXT = "text"

class InputFormatEnum(Enum):
    PYTHON_OBJECT = "python_object"
    JSON_TEXT = "json_text"
    LIKE_JSON_TEXT = "like_json_text"


@exception_to_tool_exception
def pretty_print_python_object(obj: str, input_format: str = InputFormatEnum.JSON_TEXT.value, output_format: str = OutputFormatEnum.JSON.value) -> str:
    if input_format == InputFormatEnum.PYTHON_OBJECT.value:
        parsed_obj = ast.literal_eval(obj)
    elif input_format == InputFormatEnum.JSON_TEXT.value:
        parsed_obj = json.loads(obj)
    elif input_format == InputFormatEnum.LIKE_JSON_TEXT.value:
        return ToolUtils.tool_result_with_artifact("这是一个有些许错误的json文本，将数据展开每行一条数据，为错误的格式的行做注释", obj)
    else:
        raise ValueError(f"Invalid input_format: {input_format}")

    if output_format == OutputFormatEnum.JSON.value:
        result = json.dumps(parsed_obj, indent=4)
    elif output_format == OutputFormatEnum.TEXT.value:
        result = pformat(parsed_obj)
    else:
        raise ValueError(f"Invalid output_format: {output_format}")

    return ToolUtils.tool_result_with_artifact("处理完成", result)



class PrettyPrintPythonObjectInput(BaseModel):
    obj: str = Field(..., description="要打印的Python对象字符串")
    input_format: str = Field(
        description="""输入格式，根据输入数据的形式判断，可选值：
        python_object: python 对象，如 dict, list, set
        json_text: json 文本，能直接被 json 解析
        like_json_text: 类似 json 文本，但是因为有一点格式问题，如缺少了一个引号、括号会导致 json 解析错误的文本
        """,
        default="text",
    )
    output_format: str = Field(
        description="输出格式，可选值：json, yaml, toml, ini, xml, html, markdown, latex, text， 默认为 text",
        default="text",
    )


class BaseAgentErrorHandler:
    """
    处理 Agent Tool 生命周期异常
    """
    max_retry: int = 3

    def __init__(self, tool_name: str = ""):
        self._id = str(randint(1, 9999)) if not tool_name else tool_name


class ToolErrorHandler(BaseAgentErrorHandler):
    """用于处理工具调用失败的情况
    当工具调用失败太多,抛出调用失败的异常;
    针对同一个线程
    """
    def __call__(self, exc: ToolException) -> str:
        return f"exception when calling tool, exception: {exc}, 请告诉用户这个信息，并提醒用户修改输入"


class ValidationErrorHandler(BaseAgentErrorHandler):
    """用于处理参数验证失败的情况
    """
    def __call__(self, tool_name: str):
        def validate_error_handler(error: ValidationError):
            return f"exception when {tool_name} validating input, exception: {error}, 请告诉用户这个信息，并提醒用户修改输入"
        return validate_error_handler


pretty_print_python_object_tool = StructuredTool.from_function(
    pretty_print_python_object,
    name="pretty_print_python_object",
    description="""智能解析字符串工具， 能解析python对象，json文本，有点问题的json文本
    输入示例： 
        帮我解析下面的python对象，并友好输出。
        帮我解析下面的字符串，并用以 json 形式输出。
        这是一段有点毛病的json文本，帮我用智能解析字符串工具处理为 json 文本
    参数解析规则：
        input_format：
            python_object: python 对象，如 dict, list, set
            json_text: json 文本，能直接被 json 解析
            like_json_text: 类似 json 文本，但是因为有一点格式问题，如缺少了一个引号、括号会导致 json 解析错误的文本
        output_format：
            输出格式，可选值：json, yaml, toml, ini, xml, html, markdown, latex, text， 默认为 text                
    """,
    args_schema=PrettyPrintPythonObjectInput,
    response_format="content_and_artifact",
    return_direct=False,
    verbose=True,
    handle_tool_error=ToolErrorHandler("pretty_print_python_object"),
    handle_validation_error=ValidationErrorHandler("pretty_print_python_object"),
)