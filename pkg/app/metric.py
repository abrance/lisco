import json
from typing import Optional, Dict

from fastapi import Query
from pydantic import BaseModel, Field

from pkg.server.http.server import AppServer


class MetricAppServer(AppServer):
    def __init__(self):
        super().__init__("/metric")


metric_app_server = MetricAppServer()
metric_app = metric_app_server.get_app()


@metric_app.get(
    path="/",
    summary="展示应用内部指标",
    description="获取应用内部指标接口，可以接收一个可选的'size'参数来展示如何处理查询参数。",
    tags=["Metric"],
    response_description="""
response data json schema:
{
    "Hello": "World, metric",
}    
    """
)
def read_root(
        size: Optional[int] = Query(3, description="一个可选的整数参数，用于演示如何处理查询参数", title=None)
):
    if size is not None:
        return {"Hello": "World, metric", "size": size}
    else:
        return {"Hello": "World, metric"}



class MetricResponse(BaseModel):
    data: Dict[str, str] = Field(description="指标键值对")


# 写一个 POST metric 接口，同样是 展示应用内部指标， body 参数 json， 参数有 size
@metric_app.post(
    path="/",
    summary="展示应用内部指标",
    name="GetMetrics",
    description="获取应用内部指标接口，可以接收一个可选的'size'参数来展示如何处理查询参数。",
    tags=["Metric"],
    response_model=MetricResponse,
)
def read_root(
        size: Optional[int] = Query(3, description="一个可选的整数参数，用于演示如何处理查询参数", title=None)
):
    data= {
        "CPUUsage": "10%",
        "MemoryUsage": "20%",
        "DiskUsage": "30%",
        "NetworkUsage": "40%",
        "BatteryUsage": "90%"
    }

    # 根据 size 返回  size 个数据
    if size is not None:
        data = {k: v for k, v in data.items() for _ in range(size)}

    return {"data": data}
