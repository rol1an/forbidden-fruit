# 砚友美学铁律

> **何时读本文件**：执行 yanyu-import Step 4（渲染飞书 DocxXML）时。L2 SKILL.md 已经摘出了铁律名字，本文给出完整规则、模板和反例。

## 一、原文强力标记 1:1 映射（最容易被新手忽略）

**为什么**：作者对自己内容的加粗/彩色是"创作意图"的一部分。把它们抹平=破坏作者意图=变成 "AI 嚼过的二手知识"。砚友区别于普通 AI 摘要工具的核心就在这里。

**怎么做**：

| 原文 HTML | 飞书 DocxXML |
|---|---|
| `<strong>关键</strong>` 或 `<b>关键</b>` | `<b>关键</b>` |
| `<span style="color:#ff0000">关键</span>` | `<span text-color="red">关键</span>` |
| `<span style="color:#0070c0">关键</span>` | `<span text-color="blue">关键</span>` |
| `<blockquote>引用段</blockquote>` | `<blockquote>引用段</blockquote>` 或 `<callout>` |

**强制流程**：Step 1 抓取 HTML 后立刻用脚本提取所有 `<strong>` / `<b>` / `style="color:..."` 的文本片段，建立一个 list；Step 4 渲染完成后用该 list 自检——每条都必须在飞书 XML 中找到对应保留。

## 二、自有强调：深蓝色字体不加粗

**砚友自己添加**的标签和标注——「核心观点」「本节要点」「面试答法」「加分点」「来源」「作者」「复习元数据」——统一用：

```xml
<span text-color="blue">本节要点</span>
```

**不用 `<b>`**。`<b>` 加粗只留给原作者的强调。这样视觉上能让"作者声音"和"砚友声音"清晰可辨。

## 三、4 色封顶（反疲劳）

**为什么**：颜色超过 4 种 = 视觉混乱 = 用户扫读疲劳。心理学扫读训练要求每种颜色对应固定语义，形成条件反射。

| 颜色 | 用途 | 飞书 background-color / border-color |
|---|---|---|
| 🔵 蓝色系 | 元数据、来源、知识标签、相关知识引用、砚友自有强调 | `light-blue` / `blue` |
| 🟡 黄色系 | 核心观点、重要提示、面试答法 | `light-yellow` / `yellow` |
| ⚪ 灰色系 | 章节要点总纲 callout（每章一个） | `light-gray` / `gray` |
| 🟢 绿色系 | **仅用于文末复习元数据** | `light-green` / `green` |

超出这 4 色 = 违规。装饰性颜色 = 违规。

## 四、反表格嵌套铁律

**为什么**：飞书表格单元格放长段落 → 同行其他列空着 → 该列堆一大块文字 → 整张表又丑又难读。

**禁止**：
- 面试答法、实战经验、技术细节推导塞进 `<td>`
- 多段落塞进 `<td>`
- 同一个 `<td>` 超过 3 行短文本

**正确做法**：表格只放结构对齐的**短文本**（2-3 行内）。长段内容用表格下方的独立 `<callout emoji="🎙️">` 承载，可放多个 callout 对应表格各行。

❌ 反例：

```xml
<table>
  <tr>
    <td>问题1</td>
    <td>面试时这个问题的标准答法是：第一步...第二步...第三步...（长达 500 字的完整论述）</td>
  </tr>
</table>
```

✅ 正例：

```xml
<table>
  <tr><td>问题1</td><td>简短结论一句</td></tr>
</table>

<callout emoji="🎙️" background-color="light-yellow" border-color="yellow">
  <p><span text-color="blue">问题1 · 完整答法</span></p>
  <p>第一步...第二步...第三步...</p>
</callout>
```

## 五、Emoji 扫读规范

| 位置 | 规则 |
|---|---|
| 章节标题 | 加 emoji 前缀（`## 🧠 记忆机制` / `## 🔧 工具链`）。不同章节用不同 emoji 形成视觉锚点 |
| 列表项 | 每项前 1 个语义 emoji（🔄流程 / 🧠记忆 / 🔧工具 / 🛡️安全 / 📊对比）。**同一列表保持同一 emoji**，跨列表换 |
| 表格 header | **不加 emoji**，保持简洁 |
| Callout | emoji 由 `<callout emoji="...">` 属性指定，不在正文重复 |

## 六、DocxXML 完整模板（Step 4 直接用）

```xml
<title>重构后的标题（反映核心知识点，禁止原文营销标题）</title>

<callout emoji="📖" background-color="light-blue" border-color="blue">
  <p><span text-color="blue">来源</span>：公众号名 | <span text-color="blue">作者</span>：xxx | <span text-color="blue">日期</span>：yyyy-mm-dd</p>
  <p><span text-color="blue">原文链接</span>：<a href="原文URL">原文</a></p>
</callout>

<callout emoji="🎯" background-color="light-yellow" border-color="yellow">
  <p><span text-color="blue">核心观点</span></p>
  <ul>
    <li>💡 <b>观点1</b>：一句话总结</li>
    <li>💡 <b>观点2</b>：一句话总结</li>
  </ul>
</callout>

<hr/>

<h1>🔧 第一章标题</h1>
<callout emoji="📌" background-color="light-gray" border-color="gray">
  <p><span text-color="blue">本节要点</span>：一句话概括本章核心</p>
</callout>
<p>重构后的正文...</p>
<ul>
  <li>🔹 <b>要点A</b>：说明</li>
  <li>🔹 <b>要点B</b>：说明</li>
</ul>

<!-- 高价值实战段落用 callout 提示 -->
<callout emoji="🎙️" background-color="light-yellow" border-color="yellow">
  <p><span text-color="blue">面试答法</span></p>
  <p>详细论述...</p>
</callout>

<h1>🧠 第二章标题（emoji 与第一章不同）</h1>
<!-- ... -->

<hr/>

<!-- Step 6 知识关联（如有） -->
<callout emoji="🔗" background-color="light-blue" border-color="blue">
  <p><span text-color="blue">相关知识</span></p>
  <ul>
    <li>📄 <a href="飞书文档URL">相关文章标题</a>：一句话说明关联点</li>
  </ul>
</callout>

<callout emoji="🧠" background-color="light-green" border-color="green">
  <p><span text-color="blue">复习元数据</span></p>
  <ul>
    <li>📅 <span text-color="blue">导入日期</span>：{TODAY}</li>
    <li>🏷️ <span text-color="blue">知识标签</span>：tag1, tag2, tag3</li>
    <li>🔄 <span text-color="blue">下次复习</span>：{TODAY+1d}</li>
  </ul>
</callout>
```

## 七、自检清单（Step 4 结束前过一遍）

- [ ] 整篇用色 ≤ 4 种（不算正文黑色）
- [ ] 复习元数据 callout 是绿色，且**只有这一个绿色 callout**
- [ ] 所有表格单元格 ≤ 3 行短文本；长内容已挪到下方 callout
- [ ] Step 1 抓取的强力标记 list 每条都在 XML 里能找到对应保留
- [ ] 砚友自有标签（来源/作者/核心观点/本节要点 等）全用 `<span text-color="blue">` 不加粗
- [ ] 章节标题有 emoji 前缀，且不同章节 emoji 不重复
- [ ] 所有 `<img>` 的 `href` 是完整 URL（含 `?wx_fmt=...` 参数，`&amp;` 已 decode 成 `&`）
