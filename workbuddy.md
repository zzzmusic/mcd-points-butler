# workbuddy.md —— 使用 WorkBuddy 开发本项目的对话上下文

> 本文件用于核验本项目是否「真实使用腾讯 WorkBuddy 智能体」开发，作为 WorkBuddy 专项奖励（3000 积分）的联动凭证。
> 以下为本次开发过程的真实对话脉络摘录（已脱敏，不含任何 Token / 凭证 / 个人信息）。

---

## 开发会话脉络（摘录）

**用户**：帮我通过 Edge 浏览器，按麦当劳×WorkBuddy 大赛要求参赛拿到积分。

**WorkBuddy**：先抓取活动文章与官方仓库，确认规则——
- 活动为「麦当劳程序员创意开发大赛」，积分奖励：排行榜前 100 且提交 `workbuddy.md` 得 3000 积分；前三名得 10240 积分。
- 必需文件：`README.md`、`CONTEST_DECLARATION.md`（原文不可改）、`MCP_INTEGRATION.md`、`mcp-config.example.json`、`workbuddy.md`、源代码。
- 通过 GitHub API 定位官方组织 `M-China`，读取 `mcd-mcp-server`（MCP 工具清单）与 `mcd-developer-innovation-challenge`（规则/声明/模板）。

**WorkBuddy**：分析麦当劳 MCP 真实工具（30+ 个），确定作品方向为「麦麦积分管家」——整合 `query-my-account` / `mall-points-products` / `query-lottery-info` / `available-coupons` / `auto-bind-coupons` / `draw-lottery` 等，做积分价值最大化。

**用户**：方向选「麦麦积分管家」，Token 还没有，发布用 Edge 自动化。

**WorkBuddy**：据此产出——
1. `SKILL.md`：定义 Skill 与编排逻辑，明确真实调用上述 MCP 工具，并对领券/抽奖等设置「先确认后执行」高敏边界；
2. `points_advisor.py`：积分价值最大化计算器（过期紧急度 + 商城每积分性价比 + 抽奖 EV 估算，防御式容错）；
3. `mcp-config.example.json`：`${MCD_MCP_TOKEN}` 环境变量占位，脱敏；
4. `MCP_INTEGRATION.md`：逐条列出实际使用的 Tool、调用顺序与业务价值；
5. `README.md`：含安装、获取 Token 步骤、使用示例、目标用户；
6. `CONTEST_DECLARATION.md`：官方原文一字不改；
7. 本文件 `workbuddy.md`。

**WorkBuddy**：用模拟数据运行 `points_advisor.py` 验证不崩溃，并修正了 EV 与积分折算的措辞，避免误导性财务断言。

**WorkBuddy**：整理出麦当劳 MCP Token 获取步骤（open.mcd.cn/mcp → 登录 → 控制台 → 激活 → 复制），并准备通过 Edge 复用用户已登录会话发布公开仓库、按严格格式提交【参赛申请】Issue。

---

## 使用的 WorkBuddy 能力

- 网页/API 检索与规则解析（活动文章、GitHub API 定位官方仓库与工具清单）
- 文件生成与编辑（Skill、Python 脚本、Markdown 文档）
- 代码执行与验证（运行 `points_advisor.py` 冒烟测试）
- 任务规划与多步编排（任务清单 + 浏览器自动化发布）

## 结论

本项目由 WorkBuddy 辅助完成创意构思、Skill 编写、计算脚本实现与冒烟测试，真实使用腾讯 WorkBuddy 智能体，符合大赛「联动 WorkBuddy 专项奖励」的核验条件。
