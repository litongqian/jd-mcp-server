#!/usr/bin/env python3
"""京东 MCP 连接器（基于 catbus-cli 的轻量包装层）。

将 catbus 的京东个人账号能力封装为标准 MCP 工具：
商品搜索/详情/评价、优惠券、消息收发、订单、购物车等。
登录态由 catbus 管理（catbus jd auth login 扫码登录），凭证存于 ~/.catbus/。
"""
import json
import subprocess

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "jd",
    instructions="京东个人账号 MCP 连接器（基于 catbus）。大部分工具需要先扫码登录："
    "运行 `catbus jd auth login` 或让用户在终端执行扫码。注意京东风控较严，"
    "不要高频调用；遇到 RISK_CONTROL 错误应停止并等待，不要自动重试。",
)

CATBUS = "catbus"


def _run(args: list[str], timeout: int = 60) -> str:
    """执行 catbus 命令并返回归一化 JSON 字符串。"""
    try:
        proc = subprocess.run(
            [CATBUS, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return json.dumps(
            {"ok": False, "error": f"命令超时（>{timeout}s）：{' '.join(args)}"},
            ensure_ascii=False,
        )
    out = (proc.stdout or "").strip()
    if out:
        try:
            envelope = json.loads(out)
        except json.JSONDecodeError:
            envelope = {"ok": proc.returncode == 0, "data": out}
        # 控制输出体积，避免超出 MCP 单帧限制
        text = json.dumps(envelope, ensure_ascii=False)
        if len(text) > 400_000:
            envelope["data"] = "[输出过大已截断]"
            envelope["truncated"] = True
            text = json.dumps(envelope, ensure_ascii=False)
        return text
    return json.dumps(
        {"ok": False, "error": proc.stderr.strip() or f"exit={proc.returncode}"},
        ensure_ascii=False,
    )


# ---------- 登录态 ----------

@mcp.tool()
def jd_auth_status() -> str:
    """检查京东登录状态（是否已扫码登录、当前账号）。"""
    return _run(["jd", "auth", "status"])


# ---------- 商品 ----------

@mcp.tool()
def jd_item_search(keyword: str, sort: str = "general", limit: int = 20) -> str:
    """搜索京东商品。sort 可选 general|sales|price_asc|price_desc|comments。"""
    return _run(["jd", "item", "search", keyword, "--sort", sort, "--limit", str(limit)])


@mcp.tool()
def jd_item_get(sku: str) -> str:
    """获取京东商品详情。sku 为纯数字商品 ID、item.jd.com 链接或 3.cn 短链。"""
    return _run(["jd", "item", "get", sku])


@mcp.tool()
def jd_item_related(sku: str) -> str:
    """获取京东相关商品推荐（近似结果）。"""
    return _run(["jd", "item", "related", sku])


@mcp.tool()
def jd_comment_list(sku: str, limit: int = 20) -> str:
    """获取京东商品评价（上游仅支持第一页）。"""
    return _run(["jd", "comment", "list", sku, "--limit", str(limit)])


@mcp.tool()
def jd_coupon_list(sku: str) -> str:
    """查询商品可用的优惠券。"""
    return _run(["jd", "coupon", "list", sku])


@mcp.tool()
def jd_keyword_hot() -> str:
    """获取京东热搜关键词。"""
    return _run(["jd", "keyword", "hot"])


# ---------- 消息 ----------

@mcp.tool()
def jd_msg_list(limit: int = 30) -> str:
    """读取京东客服/私信会话列表。"""
    return _run(["jd", "msg", "list", "--limit", str(limit)])


@mcp.tool()
def jd_msg_history(conversation_id: str, limit: int = 30) -> str:
    """读取指定会话的消息记录。conversation_id 来自 jd_msg_list 返回的 id。"""
    return _run(["jd", "msg", "history", conversation_id, "--limit", str(limit)])


@mcp.tool()
def jd_msg_send(
    text: str,
    item: str = "",
    conversation: str = "",
    order: str = "",
    confirmed: bool = False,
) -> str:
    """发送京东私信/联系商家客服（写操作）。

    - 联系商品卖家/客服：传 item（商品 ID 或 URL）
    - 回复已有会话：传 conversation（会话 ID）
    - 按订单咨询：传 order（订单号）

    必须先向用户确认消息内容和收件对象，confirmed=True 才会真正发送。
    """
    if not confirmed:
        return json.dumps(
            {
                "ok": False,
                "error": "未确认：请先向用户展示将要发送的内容和对象，用户同意后以 confirmed=True 重试",
            },
            ensure_ascii=False,
        )
    args = ["jd", "msg", "send", text, "-y"]
    if item:
        args += ["--item", item]
    if conversation:
        args += ["--conversation", conversation]
    if order:
        args += ["--order", order]
    return _run(args)


# ---------- 订单 / 购物车 ----------

@mcp.tool()
def jd_order_list(range_: str = "3m") -> str:
    """查询京东订单列表。range_ 可选 3m|this_year|<年份>，默认近三个月。"""
    return _run(["jd", "order", "list", "--range", range_])


@mcp.tool()
def jd_cart_count() -> str:
    """查询京东购物车商品数量。"""
    return _run(["jd", "cart", "count"])


if __name__ == "__main__":
    mcp.run()
