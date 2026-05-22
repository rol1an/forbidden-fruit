# 跨界标签碰撞算法

> **何时读**：执行 yanyu-fusion Step 2 时；想升级碰撞质量时。

## 设计目标

让两个标签的距离**够远**——近了用户会说"这早就有人做了"；远了才有戏剧性，才能跳出思维定势。

但也不能太远——纯随机会抽到"具身智能 + 古代陶瓷工艺"这种用户根本接不上的组合。需要至少一极是用户**已熟悉**的，另一极才能是**陌生**的。

**已知 × 未知 = 碰撞密度最大的组合**。

## 算法 V1（MVP，本次交付）

### 输入
- `domain_familiarity_tags`：用户已熟悉的领域列表（来自 profile）
- `all_tags`：Bitable 知识库里所有出现过的标签

### 步骤
```python
import random

def pick_cross_domain(user_tags: list[str], all_tags: list[str]) -> tuple[str, str]:
    """V1: 用户熟悉 × 用户陌生 + 简单领域簇距离过滤"""
    # 1. 已知极：从 user_tags 抽 1 个
    A = random.choice(user_tags)

    # 2. 陌生极候选：all_tags 里不在 user_tags 的
    unknown_pool = [t for t in all_tags if t not in user_tags]
    if not unknown_pool:
        raise ValueError("知识库太小，没有用户陌生的标签可抽")

    # 3. 简单簇距离：避免抽到与 A 同簇的（如 RAG / Agent / LLM 都算 AI 簇）
    same_cluster = SAME_CLUSTER.get(A, [])
    far_pool = [t for t in unknown_pool if t not in same_cluster]
    pool = far_pool if far_pool else unknown_pool

    B = random.choice(pool)
    return A, B
```

### 领域簇定义（V1 手写，V2 用 embedding 聚类）

```python
SAME_CLUSTER = {
    # AI 相关簇
    "RAG":        ["Agent编排", "LLM 微调", "向量检索", "Embedding"],
    "Agent编排": ["RAG", "LLM 微调", "Multi-Agent", "Tool use"],
    "LLM 微调":  ["RAG", "Agent编排", "RLHF", "DPO"],
    # 工程相关簇
    "分布式系统": ["微服务", "消息队列", "数据库设计"],
    # ... 用户实际知识库的标签都加进来
}
```

**V1 局限**：簇定义全手写、严重依赖人工。V2 改进方向见下文。

## 算法 V2（stretch goal，赛后做）

用 sentence-embedding 计算所有标签两两余弦相似度，按相似度的反序加权随机：

```python
# 伪代码
embeddings = embed(all_tags)
similarity = cosine(embeddings[A], embeddings)
distance = 1 - similarity
# 距离越远，被抽中概率越高（softmax over distance）
weights = softmax(distance / temperature)
B = weighted_random_choice(all_tags, weights)
```

优势：自动适应任意知识库标签集，不需要手写簇定义。

## 反作弊：避免短期内重复组合

每次碰撞写入 `fusion_history`（profile 里加个字段，或独立表），下次抽到相同 (A,B) 时 reroll：

```python
def pick_with_no_recent_dup(user_tags, all_tags, recent_pairs: set, max_retries=10):
    for _ in range(max_retries):
        A, B = pick_cross_domain(user_tags, all_tags)
        if (A, B) not in recent_pairs and (B, A) not in recent_pairs:
            return A, B
    # 兜底：允许重复，但提示用户"我抽到了之前的组合"
    return A, B
```

`recent_pairs` 定义为最近 5 次的碰撞历史。

## 挑衅性问题模板（用 A × B 填入）

模板 1（最常用）：
```text
如果让 <A 领域的方法论> 来解决 <B 领域的问题>，最荒谬的地方在哪？最有道理的地方在哪？
```

模板 2（适合用户能立刻接住的组合）：
```text
你想做 <用户主题>。如果你强行借鉴 <A> 的核心思路 + <B> 的核心约束，会变成什么？
```

模板 3（适合用户对 B 完全陌生时——先逼他了解 B）：
```text
你熟悉 <A>。我们抽到的另一边是 <B>，你了解吗？如果不了解，告诉我你对 <B> 的第一印象——任何印象都行。然后我们看看 <A> 的某个机制能不能套到那个印象上。
```

模板 4（升阶，给已经做过几次 fusion 的用户）：
```text
你的画像里有一条方法论：「<用户金句>」。如果这条方法论被强行应用到 <B> 上，最先暴露的局限是什么？
```

## 调用示例

```python
profile = read_profile(user_id)
all_tags = fetch_all_article_tags()
recent = profile.get("fusion_history_recent", set())

A, B = pick_with_no_recent_dup(
    profile["domain_familiarity_tags"], all_tags, recent
)

question = TEMPLATES[choose_template(profile, A, B)].format(A=A, B=B, topic=user_topic)
print(question)  # 抛给用户作为 Step 2 的开场
```

## 反例（不要这样做）

| 反例 | 为什么不行 |
|---|---|
| 完全随机抽两个标签 | 80% 概率抽到无意义组合（用户对两极都不熟） |
| 优先抽用户最熟悉的两个标签 | 没有"未知"维度 = 没碰撞，等于普通辩论 |
| 让用户自己选 A 和 B | 用户会选自己舒服的——失去强制跨界的意义 |
| 给三个标签同时碰撞 | 用户会失焦——人脑同时持有 3 个抽象概念已经接近极限 |
