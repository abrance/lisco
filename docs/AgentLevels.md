## 构建智能体的 5 个等级

## 大家都知道，奥特曼对于 AGI 做了 5 级规划，其中 Agent 属于第三级别，现在，我们也把 Agent 的等级水平分为 5
级，看看你能实现哪一个层级。

## 我把智能体分成以下五级：

> Level 1：具备工具调用能力的智能体
>
> Level 2：拥有知识检索和记忆功能的智能体
>
> Level 3：具备长期记忆和推理能力的智能体
>
> Level 4：多智能体团队协作
>
> Level 5：智能体系统化部署


## **Level 1：工具 + 指令驱动的智能体**

这是最基础的版本——一个能执行指令并循环调用工具的 LLM。人们说的“Agent 就是 LLM +
工具调用”，指的就是这个层级（也侧面说明他们探索得不深）。

**指令** 告诉 Agent 要干嘛，**工具** 让它能动手做事：抓数据、调用 API、触发流程等。虽然简单，但已经可以实现不少自动化任务了。



    from agno.agent import Agent   
    from agno.models.openai import OpenAIChat   
    from agno.tools.duckduckgo import DuckDuckGoTools  
      
    agno_assist = Agent(  
      name="Agno AGI",  
      model=0penAIChat(id="gpt-4.1"),  
      description=dedent("""\  
      You are "Agno AGI, an autonomous AI Agent that can build agents using the Agno)  
      framework. Your goal is to help developers understand and use Agno by providing   
      explanations, working code examples, and optional visual and audio explanations  
      of key concepts."""),  
      instructions="Search the web for information about Agno.",  
      tools=[DuckDuckGoTools()],  
      add_datetime_to_instructions=True,   
      markdown=True,  
    )  
      agno_assist.print_response("What is Agno?", stream=True)  



## **Level 2：有知识 + 记忆能力的智能体**

现实中大多数任务，LLM 本身的知识都不够用。不能把所有内容都塞进 prompt，所以 Agent 需要能**在运行时调用外部知识库**
——这就涉及**agentic RAG**  或 **动态 few-shot 提示** 。

最理想的方式是**混合检索（全文 + 语义）+ rerank 重排** ，这是目前 agent 检索的最佳方案。

此外，**持久化存储** 让 Agent 拥有记忆。LLM 本身是无状态的，但通过记录历史对话和行为，它就能变成“有记忆”的状态智能体。



    ... imports  
    # You can also use https://docs.agno.com/llms-full.txt for the full documentation  
    knowledge_base = UrlKnowledge(  
      urls=["https://docs.agno.com/introduction.md"],  
      vector_db=LanceDb(  
        uri="tmp/lancedb",  
        table_name="agno_docs",  
        search_type=SearchType.hybrid,  
        embedder=0penAIEmbedder(id="text-embedding-3-small"),  
        reranker=CohereReranker(model="rerank-multilingual-v3.0"),  
      ),  
    )  
    storage = SqliteStorage(table_name="agent_sessions", db_file="tmp/agent.db")  
      
    agno_assist = Agent(  
      name="Agno AGI",  
      model=OpenAIChat(id="gpt-4.1"),  
      description=...,   
      instructions=...,  
      tools=[PythonTools(), DuckDuckGoTools()],  
      add_datetime_to_instructions=True,  
    # Agentic RAG is enabled by default when 'knowledge' is provided to the Agent.  
      knowledge=knowledge_base,  
    # Store Agent sessions in a sqlite database  
      storage=storage,  
    # Add the chat history to the messages  
      add_history_to_messages=True,  
    # Number of history runs  
      num_history_runs=3,   
      markdown=True,  
    )  
      
    if __name_ == "__main__":  
    # Load the knowledge base, comment after first run  
    # agno_assist.knovledge.load(recreate=True)  
      agno _assist.print_response("What is Agno?", stream=True)  




## **Level 3：长期记忆 + 推理能力的智能体**

**长期记忆** 意味着 Agent 能记住跨会话的信息，比如用户偏好、过去执行失败的任务，从而逐渐**适应**
用户和上下文。这就开启了个性化和持续改进的可能性。

**推理能力** 则是进一步升级——让 Agent 更擅长拆解任务、做决策、处理多步骤任务。不仅能“理解”，还能**提升任务完成率** 。



    ... imports  
      
    knowledge_base = ...  
      
    memory = Memory(  
    # Use any model for creating nemories  
      model=0penAIChat(id="gpt-4.1"),  
      db=SqliteMemoryDb(table_name="user_menories", db_file="tmp/agent.db"),  
      delete_memories=True,   
      clear_memories=True,  
    )  
      
      storage =  
      
    agno_assist = Agent(  
      name="Agno AGI",  
      model=Claude (id="claude-3-7-sonnet-latest"),  
    # User for the memories  
      user_id="ava",   
      description=...,   
      instructions=...,  
    # Give the Agent the ability to reason  
      tools=[PythonTools(), DuckDuckGoTools(),   
      ReasoningTools(add_instructions=True)],  
      ...  
    # Store memories in a sqlite database  
      memory=memory,  
    # Let the Agent manage its menories  
      enable_agentic_memory=True,  
    )  
      
    if __name__ == "__main__":  
    # You can comment this out after the first run and the agent will remember  
      agno_assist.print_response("Always start your messages with 'hi ava'", stream=True)  
      agno_assist.print_response("What is Agno?", stream=True)  


![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg
width='1px' height='1px' viewBox='0 0 1 1' version='1.1'
xmlns='http://www.w3.org/2000/svg'
xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg
stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-
opacity='0'%3E%3Cg transform='translate\(-249.000000, -126.000000\)'
fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1'
height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

## **Level 4：多智能体团队**

最有效的 Agent 往往是专注的：在某一垂类擅长任务，配有有限（<10 个）的专用工具。

如果任务更复杂，就需要多个 Agent 协作。每个智能体负责一块子任务，团队一起解决更大的问题。

但问题是：**缺乏推理能力的“团队领导”会在复杂问题上一团乱** 。目前大多数自主多智能体系统仍然不稳定，成功率不到一半。

框架层面的支持可以缓解这点，例如 Agno 提供的三种执行模式：**协调（coordinate）、路由（route）、协作（collaborate）**
，搭配内建记忆和上下文管理，能大大提高可行性。



    ... imports  
      
    web agent = Agent(  
      name="Web Search Agent",    
      role="Handle web search requests",   
      model= OpenAIChat(id="gpt-4o-mini"),  
      tools=[DuckDuckGoTools()],  
      instructions="Always include sources",  
    )  
      
    finance_agent= Agent(  
      name="Finance Agent",  
      role="Handle financial data requests",  
      model=OpenAIChat(id="gpt-4o-mini"),  
      tools=[YFinanceTools()],  
      instructions=[  
        "You are a financial data specialist. Provide concise and accurate data.",  
        "Use tables to display stock prices, fundamentals (P/E, Market Cap)",  
      ],  
    )  
      
      
    team_leader = Team (  
      name="Reasoning Finance Team Leader",   
      mode="coordinate",  
      model=Claude(id="claude-3-7-sonnet-latest"),  
      members=[web_agent, finance_agent],  
      tools=[ReasoningTools(add_instructions=True)],  
      instructions=[  
        "Use tables to display data",  
        "Only output the final answer, no other text.",  
      ],  
      show_members_responses=True,   
      enable_agentic_context=True,   
      add_datetime_to_instructions=True,  
      success_criteria="The team has successfully completed the task.",  
    )  
      
      
    if __name__ == "__main__":  
      team_leader.print_response(  
        """\  
        Analyze the impact of recent US tariffs on market performance across  
    these key sectors:  
    - Steel & Aluminum: (X, NUE, AA)  
    - Technology Hardware: (AAPL, DELL, HPQ)  
      
    For each sector:  
    1. Compare stock performance before and after tariff implementation  
    2. Identify supply chain disruptions and cost impact percentages  
    3. Analyze companies' strategic responses (reshoring, price adjustments, supplier  
    diversification)""",  
      stream=True,   
      stream_intermediate_steps=True,   
      show_full_reasoning=True,  
    )  



到了这个级别，Agent 不再是“功能”或“助手”，而是**整个系统的核心基础设施** 。

Agentic Systems 就是全栈 API 系统——用户发起请求，系统异步启动任务，并在中途持续返回结果。

听起来很酷，做起来很难。

你得做这些事：

* 请求一来就持久化状态

* 启动后台任务并跟踪进度

* 实时推送输出结果

* 建立 websocket 或等效机制来流式更新

很多团队都低估了后端系统的复杂性。