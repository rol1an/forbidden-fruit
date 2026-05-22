"""砚友评估包：LLM-judge + Bloom's dashboard + 回归测试。

合并后的 yanyu-dialogue 评估包：grinding mode + fusion mode 共用同一套指标。
move 分类沿用 MathDial 四分类（focus / probing / telling / generic），见
references/teacher-move-classifier.md。

CLI 入口（cd 到本目录的父目录 yanyu-dialogue/ 后）：
    python3 -m eval.judge --session session.json [--mock]
    python3 -m eval.bloom_tagger --question "..." [--mock]
    python3 -m eval.dashboard --session session.json --output dashboard.png [--mock]
    python3 -m eval.regression [--threshold 0.2] [--verbose]
"""
