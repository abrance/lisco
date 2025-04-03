from enum import Enum

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from pkg.util.config.config import config_manager


class ModelEnum(str, Enum):
    qwen_turbo = "qwen-turbo"
    qwen_plus = "qwen-plus"



# 定义工具（使用 Tool 类显式定义）
def magic_function(input: int) -> int:
    """Applies a magic function to an input.
    input : int
    """
    return input + 2

class MagicFunctionInput(BaseModel):
    input: int = Field(..., description="输入整数")


tools = [
    Tool(
        name="magic_function",
        func=magic_function,
        description="对输入整数执行魔法函数（+2）, input: int",
        args_schema=MagicFunctionInput,
        return_direct=False
    )
]

chatLLM = ChatOpenAI(
    api_key=config_manager.get_config().llm.api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model=ModelEnum.qwen_turbo.value,
)

# 定义提示模板（结构需符合 LangChain 0.3 的要求）
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个会调用工具的智能助手，按需执行任务。"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")  # 用于记录代理的中间思考
    ]
)

# 创建 Tool Calling Agent
agent = create_tool_calling_agent(
    llm=chatLLM,
    tools=tools,
    prompt=prompt,
)

# 初始化 AgentExecutor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

