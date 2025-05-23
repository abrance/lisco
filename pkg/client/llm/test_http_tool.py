import pytest

from pkg.client.llm.llm import HttpApiAgent


@pytest.fixture
def mock_k_agent():
    return HttpApiAgent()


def test_k_agent_invoke(mock_k_agent):
    result = mock_k_agent.invoke({"input": "查询监控指标，条目为 5，分析监控出来的指标数据"})
    print("result: ", result, result['output'])


