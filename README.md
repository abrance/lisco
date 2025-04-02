## what

lisco 是一个提供各种 kingeye 开发服务的工具箱:
目前主要支持软件开发, 填补一些开发工具箱空白 

## why

1. 减少重复开发
2. 用界面 UI 的方式协助开发者

## how

1. 使用 AI 辅助, 这样有一定的容错性, 如 json 序列化, 普通产品只会告诉不符合规范, AI 会给出提示和修改方案, 甚至尝试修复
2. 使用 MCP SERVER 辅助, 这样可以减少重复开发, 减少维护成本

### 产品设计

1. 功能实现尽量简单, 不需要花里胡哨的展示, 颜色主要使用蓝色
2. 尽量不存储用户数据
3. 不需登录
4. 界面信息不多

### 技术设计

**分层**
1. http server (组装 app 逻辑, 实现 http 接口)
2. app  (应用层, 组合提供 client 能力) 
3. any  client (客户端, 为应用层提供底层能力)

**前后端分离**
- python
- js

### 技术栈

1. python
2. fastapi (http server) 82w star > flask

## when

| status    | 
|-----------|
| **✓**     |  
| **⚠**     |  
| **✗**     |
| **?**     |
| **1%**    |
| **doing** |


**plan**

| id | status | time       | title          | content                         |
|----|--------|------------|----------------|---------------------------------|
| 0  | **✓**  | 2025-03-25 | 创建项目           | 初始化项目                           |
| 1  | **?**  | x          | init framework | 搭建框架                            |
| 2  | **?**  | x          | 业务开发           | 开发 python object pretty printer |
| 3  | **?**  | x          | 跑通一个测试接口       |                                 |


**AI使用**

| id | status | title                        | content               |
|----|--------|------------------------------|-----------------------|
| 0  | **?**  | 完成 chat                      | 与 llm 聊天              |
| 1  | **?**  | ai 整合本地 tool                 | xxx                   |
| 2  | **?**  | 实现单个 agent                   | xxx                   |
| 3  | **?**  | agent 整合 tools               | xxx                   |
| 4  | **?**  | 单个 agent 封装单个 app agent      | xxx                   |
| 5  | **?**  | app 整合 app agent             | app agent 是 app 的一种类型 |
| 6  | **?**  | MCP client 和 MCP server 能力整合 | xxx                   |


## 问题


### 技术问题

1. 用什么大模型框架, langchain ? 


