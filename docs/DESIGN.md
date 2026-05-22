# 砚友视觉设计与编排规范

> 2026-05-21 · design-agent · 第二次派单（上次 5 tools 挂在 session limit）

砚友 = 砚石与墨。**必经千百次按压与剧烈摩擦，才能研磨出最浓郁的墨汁，落笔成章**。视觉上要传达的就是这种克制、沉静、东方水墨的质感——这是砚友区别于 ChatGPT Study Mode、Khanmigo 等硅谷 AI 标准 UI 的核心差异化资产。

reviewer 给的 community value: 3 分是最低的一维，视觉传达是 ROI 最高的改善杠杆——本设计的全部 actionable 项都围绕"让评审第一眼记住砚友 ≠ 又一个聊天框"展开。

---

## 1. 砚友视觉符号系统

### Logo

**文字描述**：一方砚台俯视图，砚池里一滴墨刚刚滴落，墨晕呈不规则圆形扩散。砚台为正方形，墨滴居于偏左上方（约 1/3 位置，避免居中的呆板）。整体单色，砚台用 `#3A3A3A`，墨滴用纯黑 `#0A0A0A`。**不要**任何渐变、阴影、3D 效果。

**ASCII 草图**（前端 agent 据此 SVG 实现）：

```
  ┌──────────────────┐
  │                  │
  │    ●             │   ← 墨滴：纯黑实心圆，半径占整体 8%
  │   ◌◌◌            │   ← 墨晕：3 层同心圆，半透明递减
  │  ◌◌◌◌◌           │     opacity: 0.6 / 0.3 / 0.15
  │   ◌◌◌            │
  │                  │
  │                  │
  └──────────────────┘
       砚台外框 1px solid #3A3A3A，圆角 4px
```

实现要点：SVG `<circle>` 三层 + `<rect>` 砚台外框。**禁止** Lottie 动画、霓虹光晕、粒子效果。

### 主色卡

| 角色 | HEX | 含义 | 用途 |
|---|---|---|---|
| 墨色 | `#0A0A0A` | 主文字、logo 墨滴 | 标题、正文 |
| 砚石 | `#3A3A3A` | 副文字、边框 | 副标题、分隔线 |
| 宣纸 | `#FAF7F0` | 主背景 | README/文档/视频背景 |
| 朱砂 | `#A0322C` | **唯一点睛色**，仅用于"摩擦时刻" | 苏格拉底问句标记、警示 callout、CTA 按钮 |
| 远山青 | `#5C6B73` | 辅助点睛色，metadata | 来源标签、tag、链接 hover |

**铁律**：朱砂 `#A0322C` 全篇 ≤ 3 处出现。它是禁果的颜色——稀缺才有重量。

### 辅助 emoji 系统（替代滥用）

`aesthetic-rules.md` 已定章节 emoji 前缀规范。本设计补充砚友三大语义锚点：

| Emoji | 语义 | 出现位置 |
|---|---|---|
| 🪨 | 砚石 / 研磨模式 | yanyu-grinding 相关章节 |
| 🍎 | 禁果 / 跨界碰撞 | yanyu-fusion 相关章节 |
| 📜 | 入库 / 沉淀 | yanyu-import 相关章节 |

**禁止**使用：🚀🔥💯✨🎉🤖🌟——硅谷 AI 标配 emoji，与东方克制感冲突。

---

## 2. GitHub README 视觉规范

### Hero banner 布局

宽 1280 × 高 320 px 的横幅 PNG，放在 README 第一行（`<p align="center"><img src="docs/assets/banner.png" /></p>`）。

布局（从左到右三栏）：

```
┌────────────────────────────────────────────────────────────┐
│  [logo 80×80]      砚友 · Forbidden Fruit                  │
│                                                            │
│                    一组让你研磨知识的 Skill 包             │
│                                                            │
│                    ─── 砚石与墨的隐喻 ───                  │
└────────────────────────────────────────────────────────────┘
   背景 #FAF7F0          文字 #0A0A0A         分隔线 #3A3A3A
```

主标题 48px，副标题 18px，slogan 14px italic。字体优先 `Noto Serif SC`（思源宋体），fallback `STSong`。**衬线体是东方水墨感的核心**，不要 sans-serif。

### 徽章选择（README 第二行）

只放 4 个，按以下顺序：

```markdown
![Anthropic Skills](https://img.shields.io/badge/Anthropic-Skills_Protocol-A0322C?style=flat-square)
![Feishu](https://img.shields.io/badge/Lark-Integrated-3A3A3A?style=flat-square)
![Made in China](https://img.shields.io/badge/Made_in-China-A0322C?style=flat-square)
![License MIT](https://img.shields.io/badge/License-MIT-5C6B73?style=flat-square)
```

`style=flat-square` 是必须的——`for-the-badge` 太硅谷。颜色全部走主色卡。

### 章节顺序

1. Hero banner
2. 徽章行
3. 一句话 tagline（现有 README L7 即可）
4. **"砚石与墨"隐喻段**（现有 L11 单独提一行，加 `<blockquote>` 包裹）
5. 三个 Skill 表格（保留现有）
6. **新增**：一张"使用前 vs 使用后"对比图（左：信息焦虑感截图 / 右：砚友研磨后的飞书文档截图）
7. **新增 · 对标差异化海报**（呼应 BUSINESS §3）：左 ChatGPT Study Mode 截图（空白对话框 + 通用 Socratic），右砚友截图（**你自己的飞书知识库** + 引用具体段落反问）。海报底部小字 `Generic Socratic vs Your Own Knowledge Socratic`，朱砂 `#A0322C` 单字 highlight `Your Own`。这一张是评审第一眼差异化资产
8. 仓库结构
9. 设计哲学
10. 部署

---

## 3. 飞书文档"砚友模板"

入库文章首页布局严格遵守 `aesthetic-rules.md §六`，本设计补充**首屏视觉节奏**：

```
[标题 h1]
  ↓ 留 1 空行
[蓝色 callout 📖 来源元数据]      ← 必有
  ↓ 留 1 空行
[黄色 callout 🎯 核心观点 3 条]    ← 必有
  ↓ <hr/> 分隔
[h1 第一章（带 emoji）]
[灰色 callout 📌 本节要点]         ← 每章首必有
[正文 + 黄色 callout 🎙️ 高价值段]
  ↓ <hr/>
[h1 第二章...]
  ↓ <hr/>
[蓝色 callout 🔗 相关知识]         ← Step 6 知识关联
[绿色 callout 🧠 复习元数据]       ← 全篇唯一绿色
```

### 4 色 callout 完整 XML 示例

```xml
<!-- 🔵 蓝色：元数据 / 知识关联 / 自有强调 -->
<callout emoji="📖" background-color="light-blue" border-color="blue">
  <p><span text-color="blue">来源</span>：技术琐话 | <span text-color="blue">作者</span>：木鸟杂记</p>
</callout>

<!-- 🟡 黄色：核心观点 / 面试答法 -->
<callout emoji="🎯" background-color="light-yellow" border-color="yellow">
  <p><span text-color="blue">核心观点</span></p>
  <ul><li>💡 <b>观点 1</b>：...</li></ul>
</callout>

<!-- ⚪ 灰色：章节要点总纲 -->
<callout emoji="📌" background-color="light-gray" border-color="gray">
  <p><span text-color="blue">本节要点</span>：一句话</p>
</callout>

<!-- 🟢 绿色：复习元数据（全篇唯一） -->
<callout emoji="🧠" background-color="light-green" border-color="green">
  <p><span text-color="blue">复习元数据</span></p>
  <ul>
    <li>📅 <span text-color="blue">导入日期</span>：2026-05-21</li>
    <li>🏷️ <span text-color="blue">知识标签</span>：rag, hybrid-retrieval</li>
    <li>🔄 <span text-color="blue">下次复习</span>：2026-05-22</li>
  </ul>
</callout>
```

### 分隔节奏

- 章节之间 `<hr/>` 一个，**不要连续 `<hr/>`**
- 同章节内段落之间靠空行（`<p></p>`），不用 `<hr/>`
- 表格上下各空一行

---

## 4. forum.trae.cn 发帖模板

### 标题 hook（反叙事）

候选三选一：

1. **「为什么我做的这个 Skill，明确拒绝替你回答问题」**
2. **「我把伊甸园那枚禁果，做成了一组 Claude Skill」**
3. **「真正的 AI 学习工具应该让你卡住，而不是顺滑」**

第 2 个最 Trae，**首推**。

### 首图（封面）

960 × 540 png，左侧 logo + "砚友 Forbidden Fruit"，右侧一句话 "**让 AI 制造高价值摩擦**"。背景 `#FAF7F0`，文字 `#0A0A0A`，副标题用朱砂 `#A0322C`。**禁止**配图用任何 Midjourney 风赛博朋克 / 机械义肢 / 神经网络可视化。

### 内文配图节奏

每 300-400 字插入一张配图：

1. 第一张：砚友三个 Skill 关系图（手绘风线条，单色 `#3A3A3A`）
2. 第二张：苏格拉底对话真实截图（必须真，不要 mock）
3. 第三张：飞书入库文章截图（展示 4 色 callout）
4. 最后一张："被 agent 问住"那一刻的截图 + 用户回复的截图

### CTA

帖子末尾固定三段，**不要**任何 emoji：

```
如果你想体验"被 AI 问住"，去 GitHub 装一下：
github.com/xxx/forbiddenfruit

如果你只想看苏格拉底问句长什么样，直接看这条对话截图。

如果你觉得 AI 一直在帮你顺滑作弊，欢迎来吵架。
```

---

## 5. 5-7 分钟 demo 视频视觉脚本

总时长 6 分钟，**慢热 → 一次 aha → 落幕** 的节奏。

| 时间 | 画面 | 配音要点 |
|---|---|---|
| 0:00-0:30 | logo 静帧 + 砚台滴墨慢镜头 + 字幕"砚友 Forbidden Fruit" | 安静，只有水滴音效。无人声 |
| 0:30-1:00 | 屏幕录制：刷微信收藏夹 200+ 篇未读，焦虑感 | "你也有 200 篇收藏吃灰吗？" |
| 1:00-2:00 | yanyu-import 实操：粘贴公众号 URL → 飞书文档出现 | "第一层摩擦：物理摩擦，工具吃掉" |
| 2:00-2:30 | 镜头停在飞书 4 色 callout 文档，慢慢滚动 | 几乎不说话，让画面自己说 |
| 2:30-4:00 | yanyu-grinding 实操：用户问问题 → agent **反问** | "现在是第二层摩擦：智力摩擦" |
| **4:00-4:30** | **【高光】用户被 agent 问住，沉默 8 秒，光标闪烁** | **完全静音**。这是 aha 时刻 |
| 4:30-5:00 | 用户最终敲出回答，agent 给鼓励 | "他自己研磨出来的，不是 AI 给的" |
| 5:00-5:30 | yanyu-fusion 跨界标签碰撞示例 | 一带而过，留悬念 |
| 5:30-6:00 | 砚台慢镜头淡出 + 字幕 "github.com/xxx/forbiddenfruit" | 安静收尾，不放 BGM 高潮 |

**高光拍摄手法**：4:00-4:30 那 8 秒沉默是全片关键。摄像头**不切**，让光标真的闪烁 8 秒。多数 demo 视频不敢留白，砚友敢——这就是差异化。

**BGM**：全片仅用一首古琴或尺八独奏，音量压到 -20dB。**禁止**电子音乐 / lo-fi hip-hop / 任何"科技感"配乐。

---

## 6. 字体 / 留白 / 网格规范

### 字体

| 场景 | 字体 | 字号 |
|---|---|---|
| README h1 | Noto Serif SC Bold | 48px |
| README h2 | Noto Serif SC Medium | 32px |
| README 正文 | Noto Sans SC Regular | 16px / line-height 1.75 |
| 飞书文档标题 | 飞书默认（已是宋体类） | 24px |
| 飞书文档正文 | 飞书默认 | 14px / 行距 1.6 |
| 代码块 | JetBrains Mono | 14px |
| 视频字幕 | Noto Serif SC | 28px |

**铁律**：标题用宋体（衬线），正文用黑体（无衬线）。**反过来**就毁了整套美学。

### 留白比例

- 章节标题前留白：标题字号 × 2（h1 48px → 上留 96px）
- 段落之间留白：正文字号 × 1（16px → 段间 16px）
- callout 内边距：上下 12px，左右 16px
- README 整体左右边距：max-width 800px 居中

### 网格

- README / 文档：12 列栅格，但**实际只用居中单列**——东方留白美学的核心是**敢留空**，不要把所有列填满
- 视频：16:9，安全区上下各留 8% 不放关键信息

---

## 自检清单（交付前过一遍）

- [ ] 全篇朱砂 `#A0322C` 出现 ≤ 3 处
- [ ] 没有任何 🚀🔥💯✨ 等硅谷 emoji
- [ ] 标题衬线 / 正文非衬线
- [ ] demo 视频 4:00-4:30 那 8 秒沉默没被剪掉
- [ ] 飞书文档 4 色 callout 全部齐全，绿色仅在末尾出现一次
- [ ] forum.trae.cn 首图没有任何赛博朋克元素
