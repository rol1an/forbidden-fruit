# Trae SOLO 平台兼容性摸底清单

> 阶段 0 产物。目的：在投入大量工程前，验证砚友三个 Skill 在 Trae SOLO 桌面端能跑得起来。

## 已确认

### A · 来自 `npx skills add larksuite/cli -g -y` 输出

- ✅ **Trae CN 是 `npx skills` CLI 的一等公民 install target**——25 个 `lark-*` skill 都被 symlink 到 `~/.agents/skills/`
- ✅ Skill 安装路径统一在 `~/.agents/skills/`，host 通过 symlink 接入

### B · 来自 Trae SOLO 桌面端 2026-05-21 实测（截图 `forbiddenfruit/traesolo.png`）

- ✅ **Trae SOLO 设置 → 技能与命令 → "启用 .agents 技能目录"开关**：官方明文支持 Anthropic Skills 协议标准路径 `.agents/skills`——**不需要为 Trae SOLO 单独写一份 Skill**
- ✅ **lark-* skill 全部正常加载**（lark-wiki / lark-workflow / lark-whiteboard 等可见，分页 6 页装满）；每个 skill 有独立 toggle 开关，用户可选择性启用
- ✅ **底部输入框支持 `/plan` `/spec` slash commands** + SOLO Agent 文案明示"自主编排智能体"——砚友 multi-agent 设计也能跑

### C · Q1 多轮对话 + Q2 shell 调用（2026-05-21 实测，详见下方）

- ✅ **Q1 通过**：Trae SOLO 自动选 skill + 维持上下文（A 观察点通过）
- ✅ **Q2 通过**：Skill 真的执行 `lark-cli base +record-search` 子进程 + 把结果带回上下文（B 观察点通过）
- ⚠️ **C 观察点（飞书认证）失败**——不是平台问题；跑 `lark-cli auth login --profile new_tenant --scope "base:record:read base:record:create base:record:update"` 增量授权即解

### 总结

**🟢 砚友架构全部假设成立**：决策 1（LocalFileBackend）/ 决策 2（合并 dialogue）/ 决策 6a-d 全可推进。

## 实测记录（详情）

### Q1：Trae SOLO 是否支持多轮对话 Skill？

**为什么重要**：`yanyu-grinding` 和 `yanyu-fusion` 都需要 agent 提问 → 用户作答 → agent 追问 → ... 的多轮交互。如果 Trae SOLO 的 Skill 只支持"一问一答"或"用户给 prompt → agent 输出"的单轮模式，整个研磨/研创模式都没法落地。

**怎么验证**：
1. 下载 Trae SOLO 桌面端 / 网页端（**注意：不是 IDE 内的 SOLO 模式，技能创作赛明确不接受**）
2. 在 Trae SOLO 里启用 `import-wechat` 或任意 `lark-*` Skill
3. 尝试一个需要 agent 多轮追问的场景，看 Skill 内的对话是否能维持上下文
4. 记录：☐ 支持 / ☐ 不支持 / ☐ 部分支持（说明限制）

**Go/No-Go**：
- ☑ **支持**（2026-05-21 实测：Trae SOLO 自动选 lark-base skill + 维持上下文跨多轮）→ 继续按 plan 推进

### Q2：Skill 能在对话中调用本地 shell（`lark-cli`）吗？

**为什么重要**：`yanyu-import` 需要调 `lark-cli docs +update` 写飞书；`yanyu-grinding/fusion` 需要调 `lark-cli base +record-search/upsert` 读写用户画像。

**怎么验证**：
1. 在 Trae SOLO 里启用 `lark-base` Skill
2. 让它跑 `lark-cli base +record-search` 查一条记录
3. 看返回值是否进了 agent 上下文

**Go/No-Go**：
- ☑ **能直接调 shell**（2026-05-21 实测：Skill 真的 fork `lark-cli base +record-search` 子进程，结果回 agent 上下文）→ 用现有 `lark-cli` 流程
- ⚠️ 实测时 C 观察点（飞书数据返回）因 scope 不足卡住，跑 `lark-cli auth login --profile new_tenant --scope "base:record:read base:record:create base:record:update"` 增量授权即解

### Q3：Skill 之间能否共享 `scripts/`？

**为什么重要**：`profile_read.py` / `profile_write.py` 是横切关注点，`yanyu-grinding` 和 `yanyu-fusion` 都要用。

**怎么验证**：
1. 创建一个最小 Skill A 引用 Skill B 的 scripts/foo.py
2. 看 Skill A 的 SKILL.md 用 `../skill-b/scripts/foo.py` 引用是否能成功执行

**备选方案**：
- 如果不支持跨 Skill 引用，把 profile 脚本独立成一个 Skill `yanyu-profile`，让其他 Skill 通过 Skill 调用而非文件引用复用
- 或者每个 Skill 各自拷贝一份脚本（违反 DRY，但简单）

### Q4：Skill 发布形式？

**为什么重要**：技能创作赛要求"分享链接（GitHub 或 TRAE 平台公开链接）"。

**怎么验证**：
1. 在 forum.trae.cn 找一篇已发布的 SOLO 技能创作赛作品
2. 看其分享链接是 GitHub repo 还是 TRAE 平台内的某种 ID
3. 看作品 README 是怎么写的、怎么引导用户安装的

**记录**：
- ☐ GitHub repo 链接（推荐——版本管理 + diff 友好）
- ☐ TRAE 平台公开链接（看是否有 web 端 viewer）
- ☐ 两种都可以

### Q5：description 字段触发匹配灵敏度？

**为什么重要**：description 是检索词典，写得不准 = Skill 装了等于没装。需要知道 Trae SOLO 是用 keyword 匹配、embedding 匹配、还是 LLM 自动选择。

**怎么验证**：
1. 给 yanyu-import 写两版 description——一版只写"导入微信文章"，一版按 Anthropic 规范写"当用户提供微信公众号 URL 想要去广告入库飞书时使用，触发词：微信文章、公众号、收藏导入..."
2. 用同一句用户输入（"把这个公众号文章存到知识库"）分别测，看哪版触发
3. 记录触发机制（如果能从 Trae SOLO 的 debug log 里看到）

**记录**：
- ☐ 关键词字面匹配
- ☐ 语义匹配（embedding）
- ☐ LLM 自动选择
- 触发灵敏度：☐ 高 / ☐ 中 / ☐ 低

---

## 摸底完成后

1. 把所有 Q1-Q5 的实测结果填进上面的 ☐
2. 如果发现任何 No-Go 或重大约束，立刻在 `docs/PLAN.md` 加一节"摸底修正"
3. 把这份文档作为附录贴到 GitHub README 和论坛发帖里——评审看得到"你做过严肃的平台调研"，是 completeness 和工程素养的强信号
