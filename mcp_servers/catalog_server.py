import asyncio
import os
import random
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("catalog",
              host="127.0.0.1", port=int(os.environ.get("PORT", "8103")))

_DELAY = float(os.environ.get("MOCK_DELAY_SECONDS", "0"))


@mcp.tool()
async def check_stock(
    product_name: Annotated[
        str,
        Field(description="商品名称,例如 '猫粮','猫砂盆','猫爬架','利姆露周边'"),
    ],
    quantity: Annotated[
        int,
        Field(description="购买数量,必须大于0"),
    ],
) -> dict:
    """检查商品库存是否足够, 以及预计可发货数量.用于用户询问商品是否有货时"""
    if quantity <= 0:
        return {"error": "购买数量必须大于0","code": "INVALID_QUANTITY"}
    
    if _DELAY > 0:
        await asyncio.sleep(_DELAY)

    rng = random.Random(f"stock:{product_name}")
    stock = rng.randint(0, 200)
    return {
        "product_name": product_name,
        "requested_quantity": quantity,
        "stock": stock,
        "available_quantity": min(quantity, stock),
        "available": stock >= quantity
    }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")