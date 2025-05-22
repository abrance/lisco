import pytest

from pkg.client.llm.api_tool import HttpAPIManager
from pkg.client.llm.schema_util import create_model_from_schema


@pytest.fixture
def mock_http_manager():
    return HttpAPIManager()


def test_http_manager(mock_http_manager):
    mock_http_manager.load_openapi_json("/opt/test/openapi.json", "/", "http://localhost:18000/metric")
    print("apis: ", mock_http_manager.apis)
    for api in mock_http_manager.apis:
        print("api.to_structured_tool(): ", api.to_structured_tool())

@pytest.fixture
def mock_json_schema():
    return {'properties': {'size': {'anyOf': [{'type': 'integer'}, {'type': 'null'}], 'default': 3, 'description': '一个可选的整数参数，用于演示如何处理查询参数', 'title': 'Size'}}, 'required': ['size'], 'title': 'GetMetrics__postArgsSchema', 'type': 'object'}


def test_create_model_from_schema(mock_json_schema):
    arg_schema_class = create_model_from_schema(mock_json_schema)
    args = arg_schema_class(size=3)
    print("args: ", args.model_dump_json())
