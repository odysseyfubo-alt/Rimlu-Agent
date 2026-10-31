"""@tool 装饰器：把普通函数亮给模型。对照 s3_tools.py 里手写的 JSON Schema。"""

import json

from langchain_core.tools import tool

from shop import LOGISTICS, ORDERS


@tool
def query_order(order_id: str) -> dict:
    """根据订单号查询订单，返回商品、状态和快递单号。order_id 形如 SO20260901。"""
    return ORDERS.get(order_id, {"error": f"没有找到订单 {order_id}"})


@tool
def query_logistics(tracking_no: str) -> dict:
    """根据快递单号查询物流进度和预计送达时间。"""
    return LOGISTICS.get(tracking_no, {"error": f"没有找到快递单 {tracking_no}"})


if __name__ == "__main__":
    print("工具名：", query_order.name)
    print("给模型看的说明：", query_order.description)
    print("自动生成的参数 schema：")
    print(json.dumps(query_order.args_schema.model_json_schema(), ensure_ascii=False, indent=2))
