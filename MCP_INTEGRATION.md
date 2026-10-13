# MCP 接入说明 (MCP_INTEGRATION.md)

本作品（麦麦积分管家）**真实使用**麦当劳中国官方 MCP Server（`M-China/mcd-mcp-server`），面向中国大陆地区，通过 WorkBuddy 的自定义连接器接入。

## 1. 使用的 MCP Server

| 项目 | 内容 |
|---|---|
| 提供方 | 麦当劳中国 (McDonald's China) |
| 官方仓库 | https://github.com/M-China/mcd-mcp-server |
| 接入地址 | `https://mcp.mcd.cn` |
| 传输协议 | Streamable HTTP |
| 鉴权方式 | 请求头 `Authorization: Bearer <MCP Token>` |
| Token 申请 | https://open.mcd.cn/mcp （手机号登录 → 控制台 → 激活） |

> 限流：每个 Token 每分钟最多 600 次请求，超限返回 429。本作品在领券/抽奖等高频场景前均做用户确认与节流提示。

## 2. 实际使用的 Tool 与调用流程

业务流程：**读取账户/活动数据 → 测算价值 → 给出建议 →（确认后）执行高敏操作**。

| 顺序 | MCP Tool | 用途 | 在 Skill 中的调用点 |
|---|---|---|---|
| 1 | `query-my-account` | 查询积分账户：可用/累计/冻结/即将过期积分及过期时间 | SKILL.md 第 1 步，数据输入 `points_advisor.py --account` |
| 2 | `mall-points-products` | 查询麦麦商城可用积分兑换商品列表（含积分成本） | SKILL.md 第 1 步，数据输入 `points_advisor.py --mall` |
| 3 | `mall-product-detail` | 查询指定商品详情、有效期、说明（按需） | 用户对某商品感兴趣时调用 |
| 4 | `query-lottery-info` | 查询当前积分抽奖活动状态、单次消耗、奖品列表 | SKILL.md 第 1 步，数据输入 `points_advisor.py --lottery` |
| 5 | `available-coupons` | 查询当前可领取的「麦麦省」优惠券列表 | SKILL.md 第 4 步，领券前展示 |
| 6 | `auto-bind-coupons` | 一键领取所有可用麦麦省券 | SKILL.md 第 4 步，**用户确认后**调用 |
| 7 | `query-my-coupons` | 复核已到账优惠券 | 领券后复核 |
| 8 | `draw-lottery` | 执行一次积分抽奖 | SKILL.md 第 5 步，**用户主动要求且确认后**调用 |
| 9 | `query-my-prizes` | 查询抽奖奖品记录 | 抽奖后展示结果 |

## 3. 调用流程示例（伪代码）

```text
1. account = mcp.call("query-my-account")
2. mall    = mcp.call("mall-points-products")
3. lottery = mcp.call("query-lottery-info")
4. advice  = run("python points_advisor.py --account <account> --mall <mall> --lottery <lottery>")
5. 向用户展示 advice（积分总览 / 紧急度 / 商城性价比 / 抽奖 EV / 总建议）
6. 用户确认 → mcp.call("auto-bind-coupons")  → mcp.call("query-my-coupons") 复核
7. （可选）用户要求抽奖 → mcp.call("draw-lottery") → mcp.call("query-my-prizes") 展示
```

## 4. 业务价值

- **积分到期防清零**：主动识别即将过期积分并给出「先花掉」的明确建议，避免用户无感损失。
- **价值最大化**：把商城兑换（每积分性价比）与积分抽奖（期望价值）放在同一口径对比，辅助用户理性决策。
- **省心领券**：一键领取麦麦省券并复核到账，降低手动操作成本。
- **安全边界**：领券、抽奖、下单均为高敏操作，一律「先确认、后执行」，不静默动作、不存储 Token。

## 5. 配置示例（脱敏）

见 `mcp-config.example.json`：Token 仅以环境变量 `${MCD_MCP_TOKEN}` 占位，不落地真实凭证。
在 WorkBuddy 中：左侧【专家·技能·连接器】→【连接器】→【自定义连接器】→【配置 MCP】，粘贴该 JSON 并填入自己的 Token 即可启用。
