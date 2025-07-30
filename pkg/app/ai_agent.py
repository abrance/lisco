from pydantic import BaseModel, Field

from pkg.client.llm.llm import LiscoAgent
from pkg.server.http.server import AppServer


class AIAgentAppServer(AppServer):
    def __init__(self):
        super().__init__("/ai-agent")


ai_agent_app_server = AIAgentAppServer()
ai_agent_app = ai_agent_app_server.get_app()


@ai_agent_app.get("/")
def read_root():
    return {"Hello": "World, ai agent"}


class BaseChatBody(BaseModel):
    query: str = Field(description="用户提示词")
    prompt: str = Field(
        """
    你是一个智能助手，回答用户的问题。
    """,
        description="系统提示词",
    )


class PrettyPrintPythonObjectBody(BaseChatBody):
    prompt: str = Field(
        """
    你是字符串处理专家，使用 pretty_print_python_object 工具并按照下面规则处理用户请求字符串，并返回处理结果。
    参数解析规则：
        input_format：
            python_object: python 对象，如 dict, list, set
            json_text: json 文本，能直接被 json 解析
            like_json_text: 类似 json 文本，但是因为有一点格式问题，如缺少了一个引号、括号会导致 json 解析错误的文本
        output_format：
            输出格式，可选值：json, yaml, toml, ini, xml, html, markdown, latex, text， 默认为 text
    """,
        description="系统提示词",
    )


class ChatBody(BaseChatBody):
    prompt: str = Field(
        """
    你是一个软件领域的专家，回答用户问题。
    """,
        description="系统提示词",
    )


@ai_agent_app.post("/pretty-print-python-object")
def pretty_print_python_object(body: PrettyPrintPythonObjectBody) -> str:
    agent = LiscoAgent()
    result = agent.invoke({"input": "{}\n {}".format(body.prompt, body.query)})
    return result["output"]


@ai_agent_app.post("/chat")
def chat(body: ChatBody) -> str:
    agent = LiscoAgent()
    result = agent.invoke({"input": "{}\n {}".format(body.prompt, body.query)})
    return result["output"]
