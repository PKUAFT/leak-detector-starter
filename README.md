# 因子泄露检测入门项目（Leak Detector Starter）

本项目用于金融科技协会新生训练：一边熟悉 Codex CLI 的安装与使用，一边基于我们提供的脚手架实现“因子代码是否泄露未来信息”的检测工具。

## 项目亮点
- **模拟行情数据**：`data/sample_factors.csv` 仅包含 OHLCV 与 1 日收益，可由 `leak_detection/simulator.py` 重新生成。
- **因子注册表**：`factors/` 下提供三个示例因子，其中 `factor_future_return` 故意引用未来数据，便于做正反案例。
- **检测流水线**：`leak_detection/` 目录中需要补全 `detect_leaks`，完成后可输出 CSV / JSON / Markdown 报告。
- **命令行脚本**：`scripts/` 提供重制数据、预览样本、运行管线等脚本，方便验证。
- **配套文档**：`新生codex cli简单项目指导文档.md` 手把手讲解代理设置、Codex CLI 安装与推荐工作流。

## 快速上手
1. **安装前置环境**
   - Python 3.10–3.12
   - Node.js 18 LTS（用于安装 Codex CLI，可通过 `nodejs.org`、`nvm` 等途径获取）
   - Git（Windows 建议 Git Bash，macOS 可安装 Xcode Command Line Tools）
2. **克隆项目并进入目录**
   ```bash
   git clone git@github.com:PKU-AFT/leak-detector-starter.git
   cd leak-detector-starter
   ```
3. **创建并激活虚拟环境**
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # macOS/Linux/Git Bash
   # .venv\Scripts\Activate.ps1   # Windows PowerShell
   ```
4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
5. **（可选）安装 Codex CLI**
   ```bash
   npm install -g @openai/codex-cli
   codex --version
   ```
6. **基础验证**
   ```bash
   python scripts/preview_data.py -n 5
   python -m pytest
   ```

## 你需要完成的任务
- 打开 `leak_detection/detector.py`，实现 `detect_leaks` 函数，核心要求：
  - 以“前推重算”方式回放每个因子函数，只用到 `<= as_of` 的数据。
  - 捕捉引用未来信息的因子（例如示例中的 `factor_future_return`）。
  - 将发现的问题记录为 `LeakViolation` 并封装在 `LeakDetectionResult` 中返回。
- 完成后运行：
  ```bash
  python scripts/run_pipeline.py --output outputs/manual
  ```
  检查 `outputs/manual/summary.csv` 中是否列出泄露的因子函数。

## 搭配 Codex CLI 的推荐流程
1. 使用 `codex exec "rg 'NotImplementedError'"` 找出未完成代码。
2. 将 `factors/sample_factors.py` 的函数发给 Codex，讨论检测策略（前推检验、静态分析等）。
3. 迭代实现，持续运行 `codex exec "python -m pytest"` 及管线脚本验证效果。
4. 利用 `/save` 或个人笔记记录关键思路与踩坑总结。

## 参考资源
- 详细操作指南：`新生codex cli简单项目指导文档.md`
- 重新生成数据：`python scripts/regenerate_data.py`
- 因子注册表工具：`from factors import get_registered_factors`

## 延伸练习
- 自行添加更多安全/不安全因子，观察检测器表现。
- 为 `detect_leaks` 编写针对性的单元测试。
- 探索更多检测手段：AST 静态分析、统计漂移检测等。
