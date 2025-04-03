from pkg.client.llm.llm import QwenAgent, LiscoAgent
import pytest


@pytest.fixture
def mock_qwen_agent():
    return QwenAgent()


@pytest.fixture
def mock_lisco_agent():
    return LiscoAgent()

@pytest.mark.skip
def test_mock_qwen_agent(mock_qwen_agent):
    result = mock_qwen_agent.invoke(
        {"input": "请计算 magic_function(3) 的结果"}
    )
    assert result["output"] == 5 or "5" in result["output"]


# @pytest.mark.skip
def test_pretty_print_python_object_tool(mock_lisco_agent):
    obj = '[1, 2, 3]'
    result = mock_lisco_agent.invoke({"input": f"帮我解析下面的python对象，并用 json 友好输出，只输出结果，避免解释。\n\nobj = {obj}"})
    assert obj in result["output"]

    obj = """
{
	'id': '0eb62fb6-418c-4066-bb0d-4f886b18feb6',
	'enable': True,
	'name': None,
	'description': None,
	'proto_version': 'v1',
	'data_sources': [{
		'id': '0cb15287-bc2a-4b16-a521-52081768132c',
		'type': 'preview',
		'name': None
	}],
	'transforms': [{
		'id': '6a362914-cb64-4f67-a8e1-ef45faa8887c',
		'name': 'CCCCCC',
		'type': 'transform',
		'operate': {
			'meta_name': 'delimiter_parse'
		},
		'source_id': None
	}],
	'bindings': [{
		'id': 'b6cbef20-83d3-486d-bdad-b55bafea217d',
		'source_id': '0cb15287-bc2a-4b16-a521-52081768132c',
		'target_id': '6a362914-cb64-4f67-a8e1-ef45faa8887c',
		'fields': [],
		'is_all_in': True
	}],
	'data_sinks': [{
		'id': '09e43208-bc6f-445f-bcce-39f0740e3511',
		'type': 'preview',
		'name': None
	}],
	'created_at': 1734418115,
	'updated_at': 1734418115
}    
    """
    result = mock_lisco_agent.invoke({"input": f"帮我解析下面的python对象，并用 json 友好输出，只输出结果，避免解释。\n\nobj = {obj}"})
    print(result["output"])
    assert result["output"]
