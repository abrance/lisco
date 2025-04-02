import os
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# 设置阿里云环境变量（需替换为你的凭证）
apikey = os.getenv("DASHSCOPE_API_KEY", "sk-e1b527930ae64adcbffba20d07bdd83e")

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
    api_key=apikey,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
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
    verbose=True  # 显示详细执行过程
)

