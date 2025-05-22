# import json
#
# import requests
#
# from pkg.client.llm.api_tool import ArgProperty, Parameters, Function
#
#
# def get_api_info(swagger_url, api_path, method):
#     # 获取Swagger文档
#     response = requests.get(swagger_url)
#     swagger_doc = response.json()
#     # 初始化一个空字典用于存储结果
#     api_info = {}
#     for path, methods in swagger_doc['paths'].items():
#         if path == api_path:
#             # 检查请求方法是否匹配
#             if method.lower() in methods:
#                 endpoint = methods[method.lower()]
#                 # 提取API名称（通常是操作ID）
#                 api_info['name'] = endpoint.get('operationId', 'No operation ID provided')
#                 api_info['description'] = endpoint.get('summary', 'No summary provided')
#                 # 提取参数描述
#                 parameters = endpoint.get('parameters', [])
#                 args_dict = {}
#                 for param in parameters:
#                     schema = param.get('schema', {})
#                     #schema {'anyOf': [{'type': 'integer'}, {'type': 'null'}], 'description': '一个可选的整数参数，用于演示如何处理查询参数', 'title': 'Size'}
#                     # todo
#                     """default 也要拉进来"""
#                     schema['required'] = param.get('required', False)
#                     # args_info.append(arg_info)
#                     args_dict[param.get('name')] = schema
#                 api_info['parameters'] = {
#                     "type": "object",
#                     "properties": args_dict
#                 }
#
#                 responses = endpoint.get('responses', {})
#                 response_info = {}
#                 for status_code, details in responses.items():
#                     response_description = details.get('description', 'No description provided')
#                     response_info[status_code] = response_description
#                 api_info['output'] = response_info.get('200', 'No response description provided')
#
#                 break
#
#     return api_info
#
#
# def test_requests_openapi():
#     # 使用示例
#     swagger_url = "http://localhost:18000/metric/openapi.json"  # 替换为你的Swagger文档URL
#     api_path = "/"  # 替换为目标API的路径
#     method = "GET"  # 替换为目标API的方法
#
#     api_details = get_api_info(swagger_url, api_path, method)
#     print(api_details)
#     print(json.dumps(api_details, indent=4))
#
#
# def test_create_parameter_model_with_string_field():
#     api = Function(
#         name="GetUser",
#         description="Get user information",
#         parameters=Parameters(
#             type="object",
#             properties={
#                 "name": ArgProperty(type="string", description="The name of the user"),
#                 "age": ArgProperty(type="integer", description="The age of the user"),
#                 "is_active": ArgProperty(type="boolean", description="Whether the user is active or not", required=True)
#             }
#         ),
#         output="user_info"
#     )
#
#     model_class = api.create_parameter_model()
#     instance = model_class(name="Alice", age=25, is_active=True)
#
#     assert instance.name == "Alice"
#     assert instance.age == 25
#     assert instance.is_active is True
#     assert model_class.__annotations__["name"] == str
#     assert model_class.__annotations__["age"] == int
#     assert model_class.__annotations__["is_active"] == bool
#     print("model_class:", model_class)
#
# # def test_create_parameter_model_with_required_integer_field():
# #     api = MyAPIClass()
# #     api.parameters.properties = {
# #         "age": {"type": "integer", "required": True}
# #     }
# #
# #     model_class = api.create_parameter_model()
# #     instance = model_class(age=30)
# #
# #     assert instance.age == 30
# #     assert model_class.__annotations__["age"] == (int, ...)
# #
# # def test_create_parameter_model_with_default_value():
# #     api = MyAPIClass()
# #     api.parameters.properties = {
# #         "is_active": {"type": "boolean", "default": True}
# #     }
# #
# #     model_class = api.create_parameter_model()
# #     instance = model_class()
# #
# #     assert instance.is_active is True
# #     assert model_class.__annotations__["is_active"] == (bool, True)
# #
# # def test_create_parameter_model_mixed_fields():
# #     api = MyAPIClass()
# #     api.parameters.properties = {
# #         "username": {"type": "string"},
# #         "user_id": {"type": "integer", "required": True},
# #         "email": {"type": "string", "default": "default@example.com"},
# #         "is_admin": {"type": "boolean", "default": False}
# #     }
# #
# #     model_class = api.create_parameter_model()
# #     instance = model_class(user_id=123)
# #
# #     assert instance.username is None
# #     assert instance.user_id == 123
# #     assert instance.email == "default@example.com"
# #     assert instance.is_admin is False
