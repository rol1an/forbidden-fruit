---
name: yanyu-import
version: 0.1.0
description: "当用户提供微信公众号文章 URL，希望去掉广告与营销号噪音、按知识结构重组并入库到飞书知识库时使用。会保留原作者的强力标记（加粗/彩色字体）、按 4 色约束做美学排版、自动在 Bitable 索引表里做双向链接缝合。触发词：微信文章、公众号文章、收藏导入、知识入库、去广告、把这篇文章存到飞书、import-wechat、砚友导入。"
metadata:
  requires:
    bins: ["lark-cli", "python3", "curl"]
  category: "砚友 · 原料层"
---

# yanyu-import · 砚友原料层

把微信公众号文章脱水入库飞书。**这是砚友的原料层**——它消灭"低价值物理摩擦"（找链接、跟反爬虫斗、忍受营销号、调排版），把干净的知识沉淀到飞书供后续 `yanyu-grinding`（研磨模式）和 `yanyu-fusion`（研创模式）使用。

> 设计哲学：本 SKILL.md 是 L2 工作流。具体的美学规则、DocxXML 模板、lark-cli 参数速查都下沉到 L3 `references/`，**只在你真正要执行对应步骤时才读**。

## 前置

- 先读 [`../../../.agents/skills/lark-shared/SKILL.md`](../../../.agents/skills/lark-shared/SKILL.md) 了解 lark-cli 认证、`--as bot/user` 切换、权限处理
- 阶段 0 摸底确认 Trae SOLO 能调本地 shell（见 [`../probe/TRAE_SOLO_PROBE.md`](../probe/TRAE_SOLO_PROBE.md) Q2）；如果不能，把所有 `lark-cli` 调用换成 `scripts/lark_oapi_fallback.py`

## 配置

读取用户当前会话的飞书 profile。默认值（用户私有，覆盖请改本节）：

| 项 | 值 |
|---|---|
| 飞书租户 profile | `new_tenant` |
| 知识空间 space_id | `7638158720962202573`（大模型 Agent 面试）|
| Bitable app_token | `RZeFbv8rCaoDoosMvqmcvBupnXg`（文章索引）|
| Bitable 表名 | `文章索引` |

## 输入

用户给的微信公众号文章 URL（一篇或多篇）。

## 8 步流程

### Step 1 · 抓取文章

先试 WebFetch；遇到微信安全验证（reCAPTCHA），回退到 `scripts/wechat_scrape.py`——它会带模拟浏览器 UA 做 curl，并直接产出"文字块 + 图片"有序列表。

**输出必须包含**：标题、公众号名、发布日期、按原文顺序排列的"段落 / 图片 / 公式"有序结构。图片的 `data-src` 完整 URL 必须保留参数（`?wx_fmt=png&from=appmsg`），HTML 实体 `&amp;` 解码成 `&`——截断 URL 会导致后续下载 0 bytes。

**强力标记提取**：在抓取阶段就提取原文 `<strong>`/`<b>` 与 `style="color:..."` 的文本片段列表，在 Step 4 渲染时 1:1 还原——这是砚友区别于"长垃圾变短垃圾"AI 摘要的关键。

### Step 2 · 噪音清洗

删除：关注引导、付费引流、文末广告、扫码进群、互推、水文填充、营销话术与情绪渲染。**这部分摩擦由工具吃掉，不要让用户看见。**

### Step 3 · 知识重构

目标：清晰的知识结构，**不是原文复述**。

1. 提炼 1-3 个核心观点
2. 识别论点-论据-案例的逻辑关系
3. 结构散乱 → 按"概念 → 原理 → 应用 → 总结"重构；结构清晰 → 保留只优化表述
4. Paraphrase 重写，保留术语 / 数据 / 案例
5. 每个章节提一句话要点放 callout

**论文类文章特殊处理**（含数学推导/架构图/实验结果）：**所有公式和图表必须保留**，不得简化为文字描述。详见 [`references/paper-handling.md`](references/paper-handling.md)。

**禁止**：把长文本塞表格单元格——见下文 Step 4 美学铁律。

### Step 4 · 渲染飞书 DocxXML

**必读** [`references/aesthetic-rules.md`](references/aesthetic-rules.md)——4 色约束、反表格铁律、原文强调样式保留、自有强调用深蓝色不加粗、emoji 规范、DocxXML 完整模板都在那。

L2 这里只列铁律摘要：
- **4 色封顶**：蓝（元数据/标签）/ 黄（核心观点）/ 灰（章节要点纲）/ 绿（复习元数据）
- **反表格**：长段落禁进 `<td>`，改用表格下方独立 callout
- **强力标记 1:1 映射**：原文 `<b>` → 飞书 `<b>`；原文彩色 → 飞书 `<span text-color="blue">`
- **自有强调**：用 `<span text-color="blue">` 深蓝色字体，**不加粗**——加粗只留给原作者

### Step 5 · 写入飞书知识库

```bash
# Step 5a: 在知识空间创建 wiki 节点，记录 obj_token
lark-cli wiki +node-create --profile new_tenant \
  --space-id 7638158720962202573 --title "<重构后标题>"
```

**⚠️ 禁止重跑 `wiki +node-create`**——成功即创建节点，重跑会产生同名空节点。如果脚本解析失败，从终端肉眼提取 `obj_token` 和 `url`。

```bash
# Step 5b: 写入 DocxXML
lark-cli docs +update --profile new_tenant --api-version v2 \
  --doc <obj_token> --command overwrite --content @./article_docx.xml
```

`--content @file` 必须是当前目录相对路径，不能用绝对路径。详细参数见 [`references/lark-cli-cheatsheet.md`](references/lark-cli-cheatsheet.md)。

### Step 6 · 知识网络缝合（双向链接）

身份策略：**读 Bitable** 用 bot 或 user 都可；**写 Bitable** 用 `--as bot`（user 可能 91403）；**写飞书文档**用 user（bot 无文档编辑权限）。

1. 搜索 Bitable 索引表中标签重叠的文章：

   ```bash
   lark-cli base +record-search --profile new_tenant --as bot \
     --base-token RZeFbv8rCaoDoosMvqmcvBupnXg --table-id "文章索引" \
     --json '{"keyword": "<标签关键词>", "search_fields": ["知识标签", "标题"]}'
   ```

2. **段落级内联引用**：找到相关文章后，**只用标题 + 核心观点**做一次轻量 LLM 匹配（不读全文，控 token），输出哪些章节与哪篇老文章交叉。匹配到的章节末尾插入 `<callout emoji="👉">相似内容可参考 <a>...</a></callout>`。

3. 新文章末尾（复习元数据之前）插入「相关知识」callout 列出关联文章。

4. **双向**——用 `docs +update --command append` 在老文章末尾追加对新文章的引用：

   ```bash
   lark-cli docs +update --profile new_tenant --api-version v2 \
     --doc <老文章obj_token> --command append --content @./xref.xml
   ```

5. 关联判断：标签重叠 ≥2 个 = 强关联必须互引；重叠 1 个但主题相近 = 弱关联酌情；无重叠 = 不关联。

6. **索引为空兜底**：跳过交叉引用，「相关知识」callout 填"暂无已关联文章"，后续新文章导入时会自动回头补上。

### Step 7 · 写入 Bitable 索引表

```bash
lark-cli base +record-upsert --profile new_tenant --as bot \
  --base-token RZeFbv8rCaoDoosMvqmcvBupnXg --table-id "文章索引" \
  --json '{
    "标题": "<重构后标题>",
    "原文链接": "<微信URL>",
    "文档链接": "<飞书URL>",
    "知识标签": "<标签1>",
    "导入日期": "YYYY/MM/DD",
    "复习状态": "未复习",
    "复习轮次": 0,
    "下次复习": "YYYY/MM/DD",
    "文档Token": "<obj_token>"
  }'
```

**关键坑**：
- `--json` 是平铺 `Map<FieldName, CellValue>`，**不是** `{"records":[{"fields":{}}]}` 嵌套
- `知识标签` 是单值 select，传字符串非数组
- 日期格式 `yyyy/MM/dd`
- `复习轮次` number，传 `0` 不是 `"0"`
- 首次可能需要 `lark-cli auth login --profile new_tenant --scope "base:record:create base:record:update"`

### Step 8 · 输出确认

给用户：飞书文档链接、重构后标题、核心观点摘要、知识标签、下次复习日期、关联到的已有文章。**到这里这篇文章对 `yanyu-grinding` 和 `yanyu-fusion` 可见**，用户后续可以用研磨/研创模式深度学习。

## 失败处理

| 错误 | 排查 |
|---|---|
| `wiki +node-create` 后续命令失败 | **不要重跑 wiki**，肉眼从输出提 token，从 Step 5b 继续 |
| Step 5b 写入超时 | DocxXML 可能过大（>50KB），拆 Step 5b 为 overwrite 主体 + append 末尾 |
| Step 7 报 91403 | 改 `--as bot` 重试；仍报错走 `lark-cli auth login --scope ...` 增量授权 |
| 图片 0 bytes | Step 1 `data-src` 截断或未 decode `&amp;`，回 Step 1 重抓 |
| 微信防爬 | `scripts/wechat_scrape.py` 已包含模拟 UA 与 cookie 兜底 |

## 测试 description 触发率（部署前必做）

部署到 Trae SOLO / Claude Code 前，用 10 条不同口吻的真实需求测一遍 description 触发率：

```text
1. 把这篇微信文章存到飞书
2. 帮我去广告导入这个公众号文章 <URL>
3. import-wechat <URL>
4. 收藏夹里这篇 <URL> 整理一下
5. <URL> 这篇值得收藏，砚友导入
6. 把营销号噪音去掉，结构化下这篇 <URL>
7. 这是个公众号链接 <URL>，知识入库
8. /yanyu-import <URL>
9. 帮我处理一下这个微信链接
10. 砚友，吃掉这篇文章 <URL>
```

10 条中触发 ≥8 条即 ≥80% 合格，否则按 [`references/description-tuning.md`](references/description-tuning.md) 重写 description。
