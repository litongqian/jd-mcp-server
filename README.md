# 🛒 京东 MCP 连接器（jd-mcp-server）

把京东个人账号能力封装成标准 MCP 工具，接入 WorkBuddy 后用自然语言比价、看评价、查订单、联系商家客服。

> 架构：MCP 服务器（本仓库 `server.py`，基于 FastMCP）→ [catbus](https://github.com/mankezhou/catbus) CLI → 京东 web 接口
> 登录态由 catbus 管理，凭证只保存在本地 `~/.catbus/`，不上传任何服务器。

---

## ✨ 能力一览（12 个 MCP 工具）

| 分类 | 工具 | 说明 |
|------|------|------|
| 登录 | `jd_auth_status` | 检查京东登录状态 |
| 商品 | `jd_item_search` | 搜索商品（支持按销量/价格/评价排序） |
| 商品 | `jd_item_get` / `jd_item_related` | 商品详情、相关推荐 |
| 商品 | `jd_comment_list` / `jd_coupon_list` | 商品评价（上游仅第一页）、可用优惠券 |
| 商品 | `jd_keyword_hot` | 京东热搜关键词 |
| 消息 | `jd_msg_list` / `jd_msg_history` | 客服/私信会话列表、历史消息 |
| 消息 | `jd_msg_send` | 发私信/联系商家客服（写操作，MCP 层要求先向用户确认） |
| 订单 | `jd_order_list` / `jd_cart_count` | 订单查询（3m/年内/指定年份）、购物车数量 |

---

## 📦 安装

### 环境要求

- Node ≥ 22（catbus 依赖）与 npm
- Python 3.11+ 且已安装 `mcp` 包（`pip install "mcp[cli]"`）
- macOS / Linux

### 步骤

```bash
# 1. 安装 catbus CLI
npm i -g catbus-cli
catbus doctor   # 环境自检，全部 ok 即可

# 2. 扫码登录京东（用京东 App 扫码）
catbus jd auth login

# 3. 验证登录
catbus jd auth status
```

### 接入 WorkBuddy

连接器管理 → 自定义连接器 → 配置 MCP，粘贴：

```json
{
  "mcpServers": {
    "jd": {
      "command": "/绝对路径/python3",
      "args": ["/绝对路径/jd-mcp-server/server.py"],
      "cwd": "/绝对路径/jd-mcp-server",
      "env": {}
    }
  }
}
```

保存后对 `jd` 点击「信任/启用」。其他 MCP 客户端（Claude Desktop、Cursor 等）配置同理。

---

## 💬 使用示例

- 「帮我搜一下京东上的机械键盘，按销量排序」
- 「这个商品（SKU 100012043978）现在卖多少钱，有什么优惠券」
- 「看看这件商品的差评都在说什么」
- 「查一下我最近的京东订单」
- 「用京东客服问问这个商品什么时候发货」（发送前我会先向你确认内容）

---

## ⚠️ 注意事项

- 京东**风控较严**：请勿高频调用、批量翻页；遇到 `RISK_CONTROL` 错误应停下等待，不要自动重试（MCP 层和 catbus 均不会悄悄重试）
- `comment list` 上游仅支持第一页
- 发消息属于写操作，`jd_msg_send` 要求 `confirmed=True` 才会真正发送
- 本项目仅供学习与个人效率工具使用，使用行为需符合当地法律法规及平台服务条款

---

## 🙏 致谢

- [mankezhou/catbus](https://github.com/mankezhou/catbus) — 统一的多平台命令行工具，本仓库的能力全部来自它
- [modelcontextprotocol](https://github.com/modelcontextprotocol) — MCP 协议及 Python SDK
