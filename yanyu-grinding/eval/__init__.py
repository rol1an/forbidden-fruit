"""砚友评估包：LLM-judge + Bloom's dashboard + 回归测试。

注意：决策 2 实施后会迁到 yanyu-dialogue/eval/。当前路径是 yanyu-grinding/eval/。

CLI 入口（cd 到本目录的父目录后）：
    python3 -m eval.judge --session session.json [--mock]
    python3 -m eval.bloom_tagger --question "..." [--mock]
    python3 -m eval.dashboard --session session.json --output dashboard.png [--mock]
    python3 -m eval.regression [--threshold 0.2] [--verbose]
"""
