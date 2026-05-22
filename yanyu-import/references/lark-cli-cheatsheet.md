# lark-cli 速查（yanyu-import 用到的子集）

> **何时读**：Step 5/6/7 调 lark-cli 时；命令报错需要核对参数时。

## 全局参数

| 参数 | 必填 | 说明 |
|---|---|---|
| `--profile` | 是 | 用户飞书租户标识（砚友默认 `new_tenant`）|
| `--as user/bot` | 视场景 | 飞书文档编辑必须 user；Bitable 写必须 bot；读两者皆可 |
| `--json '{}'` | 视命令 | 平铺 JSON，**不是嵌套 records 数组** |
| `--content @file` | docs +update 时 | 相对路径，**不能绝对路径** |
| `--api-version v2` | docs/wiki 必填 | 缺失会路由到老 API |

## 命令速查

### Wiki

```bash
# 在知识空间下创建节点（关联一篇空文档）— 一次性，不要重跑
lark-cli wiki +node-create --profile new_tenant \
  --space-id 7638158720962202573 --title "标题"
# → 输出含 obj_token、url，记下后续 docs +update 用
```

### Docs (v2)

```bash
# 覆盖写入整篇内容
lark-cli docs +update --profile new_tenant --api-version v2 \
  --doc <obj_token> --command overwrite --content @./article_docx.xml

# 追加到末尾（双向链接缝合用）
lark-cli docs +update --profile new_tenant --api-version v2 \
  --doc <obj_token> --command append --content @./xref.xml

# 局部 block 替换 / 插入 / 删除（高级，砚友 import 不用，研磨/研创可能用）
lark-cli docs +update --profile new_tenant --api-version v2 \
  --doc <obj_token> --command block_replace --block-id <id> --content @./snippet.xml

# 读取整篇
lark-cli docs +fetch --profile new_tenant --api-version v2 --doc <token>

# 读取目录（决定 block_replace 的 block-id）
lark-cli docs +fetch --profile new_tenant --api-version v2 \
  --doc <token> --scope outline --max-depth 3
```

### Base（Bitable）

```bash
# 搜索记录
lark-cli base +record-search --profile new_tenant --as bot \
  --base-token <app_token> --table-id "<表名或id>" \
  --json '{"keyword":"...","search_fields":["字段1","字段2"]}'

# Upsert 一条记录（按主键覆盖或插入）
lark-cli base +record-upsert --profile new_tenant --as bot \
  --base-token <app_token> --table-id "<表名或id>" \
  --json '{"字段1":"值1","字段2":数字值}'
```

**Base 字段类型陷阱**：

| 字段类型 | 传值 |
|---|---|
| 单值 select | 字符串 `"未复习"` |
| 多值 select | 数组 `["tag1","tag2"]` |
| 日期 | `"2026/05/21"`（斜杠！）|
| number | 数字 `0`，**不是** `"0"` |
| 富文本 | 字符串 |

### 认证补救

```bash
# user 身份缺 scope（写 Bitable 报 91403 时）
lark-cli auth login --profile new_tenant \
  --scope "base:record:create base:record:update"
```

### 高风险写门禁（exit 10）

不带 `--yes` 调高风险写命令 → exit 10，stderr 返回结构化 envelope：

```json
{"ok":false,"error":{"type":"confirmation_required","hint":"add --yes to confirm"}}
```

砚友 import 流程的所有写命令（wiki +node-create / docs +update / base +record-upsert）应该不是 high-risk-write 级别，正常不会触发。如果触发，向用户展示要做的操作 + 关键参数，**等用户明确同意**后追加 `--yes` 重试。**禁止默认 `--yes` 静默重试**。

## 升级提醒

`lark-cli` 输出 `_notice.update` 时，完成当前任务后建议用户：

```bash
npm update -g @larksuite/cli && npx skills add larksuite/cli -g -y
```

更新后**退出并重启 AI agent** 让新 Skill 生效。
