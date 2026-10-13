# 麦麦积分管家 (McDonald's Points Butler)

> 麦当劳程序员创意开发大赛 · 参赛作品
> 基于 **麦当劳中国 MCP** 的「积分价值最大化」助手，运行于 **腾讯 WorkBuddy**。

把积分花在刀刃上：查积分账户、对比麦麦商城兑换与积分抽奖的期望价值、一键领取麦麦省优惠券，并给出「积分怎么花最值」的个性化建议。所有数据来自麦当劳官方 MCP 实时返回，结论仅供参考。

---

## 一、项目介绍

麦麦积分管家是一个 WorkBuddy Skill，连接麦当劳中国官方 MCP Server（`mcp.mcd.cn`），帮用户：

1. **积分到期防清零** —— 识别即将过期积分，提示优先使用；
2. **价值最大化** —— 把商城兑换（每积分性价比）与积分抽奖（期望价值 EV）放在同一口径对比；
3. **省心领券** —— 一键领取「麦麦省」优惠券并复核到账；
4. **安全边界** —— 领券 / 抽奖 / 下单均为高敏操作，一律「先确认、后执行」，不存储 Token。

### 目标用户

- 麦当劳会员、麦门常客，攒了一堆积分不知道怎么花最值；
- 想避免积分静默过期清零的人；
- 想理性比较「换商城 vs 抽抽奖」的人。

---

## 二、安装方法

### 2.1 获取麦当劳 MCP Token（必需）

1. 打开 https://open.mcd.cn/mcp ；
2. 点击右上角【登录】→ 用手机号验证码登录；
3. 登录后右上角变为【控制台】，点击打开控制台弹窗；
4. 点击【激活】申请 MCP Token，阅读并同意服务协议；
5. 申请成功后【一键复制】Token。
   > 每个 Token 每分钟上限 600 次请求；请妥善保管，切勿泄露或提交到仓库。

### 2.2 在 WorkBuddy 中接入麦当劳 MCP

1. 打开 WorkBuddy，左侧【专家·技能·连接器】→ 选【连接器】页签；
2. 右上角【自定义连接器】→【配置 MCP】；
3. 在 WorkBuddy 的配置框里填入你的真实 Token。两种安全做法二选一：

   - **做法 A（推荐·最省心）**：直接在配置框的 `Authorization` 里写 `Bearer 你的真实Token`。这一步发生在你**本机 WorkBuddy**，不会进入 GitHub 仓库。
   - **做法 B（环境变量·适合二次开发）**：系统设置环境变量 `MCD_MCP_TOKEN=你的真实Token`，配置里保留 `${MCD_MCP_TOKEN}` 占位符，WorkBuddy 会自动读取。

   > ⚠️ **千万不要**编辑仓库里的 `mcp-config.example.json`、把占位符改成真实 Token 后提交/推送——那是公开仓库，任何人都能直接看到，且 git 历史无法彻底删除，等同于把账号凭证公开！
   > ⚠️ 也**不要**在仓库目录里放一份写有真实 Token 的 `mcp-config.json` 再运行发布脚本（脚本只上传白名单内的规定文件，但仍请保持真实配置在仓库目录之外）。

### 2.3 安装本 Skill

- 方式 A（项目内直接加载）：把本仓库作为 WorkBuddy 用户级/项目级 Skill 目录放入 `~/.workbuddy/skills/`（或 `.workbuddy/skills/`），WorkBuddy 会自动识别 `SKILL.md`；
- 方式 B：在 WorkBuddy 对话中说「用麦麦积分管家看看我的积分怎么花最值」，触发本 Skill 后按提示操作。

---

## 三、使用示例

**示例 1：积分快过期了怎么花**
> 用户：我积分快过期了，换点啥好？
> 管家：调用 `query-my-account` 发现你有 300 分将于 10-20 过期；结合 `mall-points-products` 测算，「麦辣鸡腿堡 400 分」性价比最高，建议优先把即将过期的分拿去兑换，避免清零。

**示例 2：积分抽奖值不值得抽**
> 用户：积分抽奖值得抽吗？
> 管家：调用 `query-lottery-info` 拿到单次消耗与奖品，测算 EV 并与商城兑换对比，给出「稳妥优先选商城 / 想碰运气再抽」的倾向建议。

**示例 3：一键领麦麦省券**
> 用户：帮我把麦麦省券都领了。
> 管家：先展示 `available-coupons` 列表 → 你确认 → 调用 `auto-bind-coupons` → 用 `query-my-coupons` 复核到账。

---

## 四、文件结构

| 文件 | 说明 |
|---|---|
| `SKILL.md` | WorkBuddy Skill 定义与编排逻辑（核心） |
| `points_advisor.py` | 积分价值最大化计算器（EV / 过期紧急度 / 商城性价比） |
| `MCP_INTEGRATION.md` | 实际使用的 MCP Server、Tool、调用流程与业务价值 |
| `mcp-config.example.json` | 脱敏后的 MCP 配置示例（仅环境变量占位） |
| `CONTEST_DECLARATION.md` | 参赛声明（官方原文，不可修改） |
| `workbuddy.md` | 使用 WorkBuddy 开发本项目的对话上下文（联动奖励核验用） |
| `README.md` | 本文件 |

---

## 五、合规与声明

- 本作品为大赛参赛作品，非麦当劳官方产品；输出仅供参考，餐品/价格/供应以官方实时结果为准。
- 严格遵守《麦当劳 MCP 服务规则》与大赛活动规则；不存储、不打印真实 Token；配置仅用环境变量占位符。
- 详见 `CONTEST_DECLARATION.md`。

---

## 六、相关链接

- 麦当劳 MCP 官方仓库：https://github.com/M-China/mcd-mcp-server
- 大赛官方仓库：https://github.com/M-China/mcd-developer-innovation-challenge
- MCP 开放平台：https://open.mcd.cn/mcp
- WorkBuddy 官网：https://www.workbuddy.cn
