from pkg.client.llm.llm import QwenAgent, LiscoAgent
import pytest

from pkg.util.config.config import config_manager


@pytest.fixture
def mock_qwen_agent():
    return QwenAgent()


@pytest.fixture
def mock_lisco_agent():
    return LiscoAgent()

@pytest.fixture
def mock_simple_list():
    return "[1, 2, 3]"

@pytest.fixture
def mock_python_object():
    return """
{
	"id": "0eb62fb6-418c-4066-bb0d-4f886b18feb6",
	"enable": True,
	"name": None,
	"description": None,
	"proto_version": "v1",
	"data_sources": [{
		"id": "0cb15287-bc2a-4b16-a521-52081768132c",
		"type": "preview",
		"name": None
	}],
	"transforms": [{
		"id": "6a362914-cb64-4f67-a8e1-ef45faa8887c",
		"name": "CCCCCC",
		"type": "transform",
		"operate": {
			"meta_name": "delimiter_parse"
		},
		"source_id": None
	}],
	"bindings": [{
		"id": "b6cbef20-83d3-486d-bdad-b55bafea217d",
		"source_id": "0cb15287-bc2a-4b16-a521-52081768132c",
		"target_id": "6a362914-cb64-4f67-a8e1-ef45faa8887c",
		"fields": [],
		"is_all_in": True
	}],
	"data_sinks": [{
		"id": "09e43208-bc6f-445f-bcce-39f0740e3511",
		"type": "preview",
		"name": None
	}],
	"created_at": 1734418115,
	"updated_at": 1734418115
}    
"""

@pytest.mark.skipif(config_manager.get_config().llm.model == "qwen-plus", reason="qwen-plus 暂时不参与测试")
def test_mock_qwen_agent(mock_qwen_agent):
    result = mock_qwen_agent.invoke(
        {"input": "请计算 magic_function(3) 的结果"}
    )
    assert result["output"] == 5 or "5" in result["output"]


@pytest.mark.skipif(config_manager.get_config().llm.model == "qwen-plus", reason="qwen-plus 暂时不参与测试")
@pytest.mark.parametrize("input_obj", [mock_simple_list, mock_python_object])
def test_pretty_print_python_object_tool_invoke(mock_lisco_agent, input_obj):
    result = mock_lisco_agent.invoke({"input": f"帮我解析下面的python对象，并用 json 友好输出，只输出结果，避免解释。\n\nobj = {input_obj}"})
    assert result["output"]


@pytest.mark.skipif(config_manager.get_config().llm.model == "qwen-plus", reason="qwen-plus 暂时不参与测试")
@pytest.mark.parametrize("input_obj", [mock_simple_list, mock_python_object])
def test_pretty_print_python_object_tool_stream(mock_lisco_agent, input_obj):
    result = mock_lisco_agent.stream({"input": f"帮我解析下面的python对象，并用 json 友好输出，只输出结果，避免解释。\n\nobj = {input_obj}"})
    for chunk in result:
        print("output: ", chunk.get("output", ""))


@pytest.mark.skipif(config_manager.get_config().llm.model == "qwen-plus", reason="qwen-plus 暂时不参与测试")
@pytest.mark.asyncio
async def test_astream_various_inputs(mock_lisco_agent, mock_simple_list, mock_python_object):
    chunks = []
    query = {"input": f"帮我解析下面的python dict 对象，并用 json 友好输出，只输出结果，避免解释。\n\nobj = {mock_python_object}"}
    async for chunk in mock_lisco_agent.astream(query):
        chunks.append(chunk)
    final_output = "".join([c.get("output", "") for c in chunks])
    print("final_output: ", final_output)
    for c in chunks:
        print("output: ", c.get("output", ""))
