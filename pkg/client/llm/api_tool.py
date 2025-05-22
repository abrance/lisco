import json
from typing import Dict, Type, Any

import requests
from langchain_core.tools import StructuredTool

from pydantic import BaseModel, Field, field_validator

from pkg.client.llm.schema_util import create_model_from_schema


class AnyOfOption(BaseModel):
    type: str


class ArgProperty(BaseModel):
    """
    参数属性
    anyOf: Optional[List[AnyOfOption]] = Field(None, description="The anyOf of the property")
    type: Optional[str] = Field("string", description="The type of the property")
    default: Optional[Any] = Field(None, description="The default value of the property")
    description: str = Field("", description="The description of the property")
    """
    schema_: Dict[str, Any] = Field(..., alias='schema')
    required: bool = True

    @field_validator('schema_')
    def check_any_of_or_type(cls, v):
        if 'anyOf' not in v and 'type' not in v:
            raise ValueError('Either "anyOf" or "type" must be provided.')
        if 'anyOf' in v and 'type' in v:
            raise ValueError('Only one of "anyOf" or "type" can be provided, not both.')
        return v


class Parameters(BaseModel):
    type: str = "object"
    properties: Dict[str, ArgProperty]

    def get_json_schema_properties(self) -> Dict[str, Any]:
        properties = {}
        for param_name, arg_property in self.properties.items():
            properties[param_name] = arg_property.schema_
        return properties


class Function(BaseModel):
    name: str = Field(..., description="The name of the function")
    description: str = Field(..., description="The description of the function")
    parameters: Parameters = Field(..., description="The parameters of the function")
    output: str = Field(..., description="The description of the function output")

    @field_validator("name")
    def validate_name(cls, v):
        # name 为全部英文字符串 形如 AlarmSearch 或 AlarmSearch_v2 或 alarm_search
        assert isinstance(v, str)
        _v = v.replace("_", "")
        assert _v.isalnum() and len(_v) > 0
        return v

    def create_parameter_model(self) -> Type[BaseModel]:
        properties = self.parameters.properties

        required_list = []
        for param_name, arg_property in properties.items():
            if not arg_property.required:
                required_list.append(param_name)

        json_schema_dict = {
            "title": f"{self.name}ArgsSchema",
            "type": "object",
            "properties": self.parameters.get_json_schema_properties(),
            "required": required_list,
        }
        model_class = create_model_from_schema(json_schema_dict)

        return model_class


class HttpFunction(BaseModel):
    """
    KingEye Function Call Model ，包含了一个 Function Call 的所需的所有结构
    """
    type: str = "function"
    function: Function = Field(..., description="The function to call")


class HttpAPI(BaseModel):
    url: str = Field(..., description="The URL of the API")
    method: str = "POST"
    function: HttpFunction = Field(..., description="The HTTP of the API")

    # 写一个 validator ， 验证 url 是否正确， 验证 method 是否正确
    @field_validator("url")
    def validate_url(cls, v):
        try:
            if isinstance(v, str) and v.startswith(("http://", "https://")):
                return v
            else:
                raise ValueError("Invalid URL")
        except requests.exceptions.MissingSchema:
            raise ValueError("Invalid URL")

    def request(self, **kwargs) -> Any:
        # 请求 url method， 目前只支持 POST 请求， 将 function 中的 parameters 转换为 json body 参数，返回响应的 data 数据。
        # 强调， 接入的 KingEye API 需要在请求、响应上保持协议一致，即， 请求方法 POST ，请求参数为 json 格式， 响应为 json 格式， code mes data 组成。
        try:
            response = requests.post(self.url, json=kwargs)
            response.raise_for_status()
            resp = response.json()
            print("resp: ", resp)
            return resp.get('data')
        except Exception as e:
            raise ValueError(f"HTTP error occurred: {e}")

    def wrap_result(self, **kwargs):
        # return self.request(**kwargs)
        result = {
            "content": self.function.function.output,
            "artifact": self.request(**kwargs)
        }
        return result

    def to_structured_tool(self):
        function_schema: Function = self.function.function
        return StructuredTool.from_function(
            self.wrap_result,
            name=function_schema.name,
            description=function_schema.description,
            args_schema=function_schema.create_parameter_model(),
            # response_format="content_and_artifact",  # 加了以后，artifacts 会被忽略， 只传入了 content 给 LLM
            return_direct=False,
            verbose=True,
        )

    def to_mcp_tool(self):
        # todo
        pass


class HttpAPIManager:
    def __init__(self):
        self.apis: list[HttpAPI] = []

    def load_openapi_json(self, json_file_path, api_path, server_location, method="post"):
        """
        通过导入 openapi.json 文件和 url 的 path ， 定位到一个接口
        :param json_file_path:
        :param api_path:
        :param method:
        :return:
        """
        openapi_json = json.load(open(json_file_path, "r"))
        api_info = openapi_json.get("paths").get(api_path, {})
        api_info = api_info.get(method, {})
        if not api_info:
            raise ValueError("Invalid url_path")

        json_schema_properties_dict = {}

        api_name = api_info.get("operationId")
        api_description = api_info.get("description")
        output_ref = api_info.get("responses", {}).get("200", {}).get("content").get("application/json", {}).get("schema").get("$ref").split("/")[-1]
        output = json.dumps(openapi_json.get("components").get("schemas", {}).get(output_ref))
        params = api_info.get("parameters", [])
        for param in params:
            param_name = param.get("name")

            # param_type = param.get("schema").get("type")
            # param_description = param.get("description")

            arg = ArgProperty.model_validate({
                "schema": param.get("schema"),
                "required": param.get("required", True)
            })
            json_schema_properties_dict[param_name] = arg
            # arg.required = param.get("required")
            # args[param_name] = arg

        url = f"{server_location}{api_path}"
        self.load_schema(url, method, api_name, api_description, output, json_schema_properties_dict)
        return True

    def get_openapi_schema(self):
        pass

    def load_schema(self, url, method, api_name: str, api_description: str, output: str, args: Dict[str, ArgProperty]):
        fc = HttpFunction(
            function=Function(
                name=api_name,
                description=api_description,
                parameters=Parameters(
                    type="object",
                    properties=args
                ),
                output=output
            ),
        )
        api = HttpAPI(
            url=url,
            function=fc
        )
        self.apis.append(api)
        return api

    def dumps(self, to_proto: str):
        if to_proto == 'openai':
            pass
        elif to_proto == 'mcp':
            pass
        else:
            return None
