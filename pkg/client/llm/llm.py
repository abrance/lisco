from enum import Enum

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from pkg.util.config.config import config_manager


class ModelEnum(str, Enum):
    gpt4o_mini = "gpt-4o-mini"

    qwen_turbo = "qwen-turbo"
    qwen_plus = "qwen-plus"



class BaseAIAgent:
    def __init__(self):
        self.llm = None
        self.agent_executor = None
        self.agent = None
        self.model = None
        self.tools = []
        self.prompt_template = None
        self.init()

    def init(self):
        self.init_llm(
            api_key=config_manager.get_config().llm.api_key,
            base_url="https://api.openai.com/v1",
            model=ModelEnum.gpt4o_mini.value
        )
        self.init_tools()
        self.init_prompt_template()
        self.init_agent()
        self.init_agent_executor()

    def init_llm(self, api_key, base_url, model):
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

    def init_agent(self):
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt_template,
        )

    def init_tools(self):
        self.tools = []

    def init_prompt_template(self):
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个会调用工具的智能助手，按需执行任务。"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ]
        )

    def init_agent_executor(self):
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )


class QwenTurboAgent(BaseAIAgent):
    def init(self):
        self.init_llm(
            api_key=config_manager.get_config().llm.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model=ModelEnum.qwen_turbo.value
        )
        self.init_prompt_template()
        self.init_tools()
        self.init_agent()
        self.init_agent_executor()

    def init_tools(self):
        def magic_function(input: int) -> int:
            """Applies a magic function to an input.
            input : int
            """
            return input + 2

        class MagicFunctionInput(BaseModel):
            input: int = Field(..., description="输入整数")

        s = StructuredTool.from_function(
                func=magic_function,
                name="magic_function",
                description="对输入整数执行魔法函数（+2）, input: int",
                args_schema=MagicFunctionInput,
                return_direct=False
            )

        self.tools = [
            s
        ]

    def invoke(self, query):
        return self.agent_executor.invoke(query)
