from pkg.client.llm.llm import agent_executor


def test_llm():
    # 执行工具调用
    result = agent_executor.invoke(
        {"input": "请计算 magic_function(3) 的结果"}
    )
    assert result["output"] == 5 or "5" in result["output"]

    # # 测试带聊天历史的场景
    # from langchain_core.messages import HumanMessage, AIMessage
    # result_with_history = agent_executor.invoke({
    #     "input": "我的名字是什么？",
    #     "chat_history": [
    #         HumanMessage(content="你好，我的名字是 Alice"),
    #         AIMessage(content="你好 Alice！有什么可以帮助你的吗？")
    #     ]
    # })
    # assert "Alice" in str(result_with_history["output"])