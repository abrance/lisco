import functools
import json
from enum import Enum
from typing import Dict, Any

from langchain_core.tools import ToolException
from pydantic import BaseModel, Field


def exception_to_tool_exception(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            raise ToolException(str(err))

    return inner


class InnerMagicPrompt(str, Enum):
    INVALID_PARAMS_ERROR = "终止流程: 参数错误, 请求用户重新输入修正参数. "
    TOOL_HANDLE_ERROR = "终止流程: 工具执行出错. "


class ToolHandleError(BaseModel):
    tool_name: str = Field(description="The name of the tool.")
    error_msg: str = Field(description="The error message.")

    def err_msg(self):
        return  "{} {} 执行出错, 错误信息为 {}".format(InnerMagicPrompt.TOOL_HANDLE_ERROR, self.tool_name, self.error_msg)


class ToolInputValidationError(BaseModel):
    tool_name: str = Field(description="The name of the tool.")
    recognized_inputs: Dict[str, Any] = Field(description="The recognized inputs.")
    invalid_inputs: Dict[str, Any] = Field(description="The invalid inputs.")

    def err_msg(self):
        return  "{} {} 识别到输入参数有误, 已识别的参数有 {}, 识别到校验不通过的参数有 {}".format(InnerMagicPrompt.INVALID_PARAMS_ERROR, self.tool_name, self.recognized_inputs, self.invalid_inputs)


class ToolUtils:
    @classmethod
    def tool_result_wrap(cls, tool_output):
        """
        简单的输出使用这种形式更方便, 可以通过 content 内容做到:
        1. 告诉模型参数错误, 请求重新输入
        2. 告诉模型 tool 输出结果
        """
        result = {"content": tool_output}
        return result

    @classmethod
    def tool_exception_wrap(cls, tool_error):
        if isinstance(tool_error, ToolInputValidationError) or isinstance(tool_error, ToolHandleError):
            return cls.tool_result_wrap(tool_error.err_msg())
        else:
            return cls.tool_result_wrap(tool_error)

    @classmethod
    def tool_result_with_artifact(cls, content, artifact):
        """
        带有查询结果的 tool 使用带有 artifact(工件) 的返回, 这种形式更有利于 LLM tool 之间的信息传递
        """
        return content, artifact

    @staticmethod
    def parse_json_response(response_text: str) -> dict:
        """
        解析并清理 JSON 响应文本
        :param response_text: 返回的原始文本
        :return: 解析后的 JSON 对象
        """
        try:
            # 尝试直接解析 JSON
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试去除多余的空格、换行符以及代码块标记后再解析
            cleaned_response = (
                response_text.strip()
                .replace("\n", "")
                .replace("```json", "")
                .replace("```", "")
            )
            return json.loads(cleaned_response)
