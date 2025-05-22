from enum import Enum

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from pydantic import BaseModel, Field

from pkg.client.llm.api_tool import HttpAPI, HttpFunction, Function, Parameters, ArgProperty, HttpAPIManager
from pkg.client.llm.tool import pretty_print_python_object_tool
from pkg.util.config.config import config_manager


class ModelEnum(str, Enum):
    GPT4oMINI = "gpt-4o-mini"

    QWEN_TURBO = "qwen-turbo"
    QWEN_PLUS = "qwen-plus"


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
            model=ModelEnum.GPT4oMINI.value,
        )
        self.init_tools()
        self.init_prompt_template()
        self.init_agent()
        self.init_agent_executor()

    def init_llm(self, api_key, base_url, model, app_code=None):
        query = None
        if app_code:
            query = dict(bk_app_code=app_code, bk_app_secret=api_key)
        self.llm = ChatOpenAI(
            api_key=api_key, base_url=base_url, model=model, default_query=query
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
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

    def init_agent_executor(self):
        self.agent_executor = AgentExecutor(
            agent=self.agent, tools=self.tools, verbose=True
        )


class QwenAgent(BaseAIAgent):
    def init(self):
        self.init_llm(
            api_key=config_manager.get_config().llm.api_key,
            base_url=config_manager.get_config().llm.base_url,
            model=config_manager.get_config().llm.model,
            app_code=config_manager.get_config().llm.app_code,
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
            return_direct=False,
        )

        self.tools = [s]

    def invoke(self, query):
        return self.agent_executor.invoke(query)

    def stream(self, query):
        return self.agent_executor.stream(query)

    async def astream(self, query):
        async for chunk in self.agent_executor.astream(query):
            yield chunk


class LiscoAgent(QwenAgent):
    def init_tools(self):
        self.tools = [pretty_print_python_object_tool]


class HttpApiAgent(QwenAgent):
    def init_tools(self):
        manager = HttpAPIManager()
        manager.load_openapi_json("/opt/test/openapi.json", "/", "http://localhost:18000/metric")
        for api in manager.apis:
            self.tools.append(api.to_structured_tool())
