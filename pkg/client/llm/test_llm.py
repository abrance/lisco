from pkg.client.llm.llm import QwenTurboAgent

def test_llm():
    # 执行工具调用
    agent = QwenTurboAgent()

    result = agent.invoke(
        {"input": "请计算 magic_function(3) 的结果"}
    )
    assert result["output"] == 5 or "5" in result["output"]