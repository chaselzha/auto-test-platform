# auto-test-platform

[![Jenkins Build](http://localhost:8080/job/auto-test-platform/badge/icon)](http://localhost:8080/job/auto-test-platform/)
[![Allure Report](http://localhost:8080/job/auto-test-platform/lastBuild/allure/badge)](http://localhost:8080/job/auto-test-platform/lastBuild/allure/)

## 自动化测试平台

基于 Pytest + Selenium + Allure + Jenkins 的企业级自动化测试框架

---

## 📋 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| 🐍 Python | 3.9+ | 测试脚本语言 |
| 🧪 Pytest | 8.x | 测试框架 |
| 🌐 Selenium | 4.x | Web 自动化 |
| 📊 Allure | 2.x | 测试报告 |
| 🔄 Jenkins | 2.x | CI/CD |
| 🎨 POM | - | 设计模式 |
| 📦 YAML | - | 数据驱动 |

---
##[skip ci]
## 🚀 快速开始

### 安装依赖

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 执行所有测试
pytest automation/tests/

# 执行冒烟测试
pytest -m smoke

# 执行回归测试
pytest -m regression

# 并行执行 (4 进程)
pytest -n 4

# 指定浏览器
BROWSER=firefox pytest

# 指定环境
pytest --env=prod

# 生成报告
allure generate automation/reports/allure-results -o allure-report --clean

# 打开报告
allure open allure-report

📊 测试状态
环境	状态
test	http://localhost:8080/job/auto-test-platform/badge/icon
dev	http://localhost:8080/job/auto-test-platform/badge/icon
prod	http://localhost:8080/job/auto-test-platform/badge/icon

CI/CD 流水线
触发方式
Push 触发: 代码推送到 main 分支自动触发

定时触发: 每晚 2:00 自动执行

手动触发: Jenkins 界面手动构建

支持浏览器
✅ Chrome

✅ Firefox

✅ Edge

测试报告
Allure 报告

Jenkins 构建

auto-test-platform/
├── automation/          # 测试核心
│   ├── common/          # 通用组件
│   ├── pages/           # 页面对象 (POM)
│   ├── tests/           # 测试用例
│   ├── utils/           # 工具类
│   ├── data/            # 测试数据
│   ├── config/          # 配置文件
│   └── reports/         # 测试报告
├── ci/                  # CI/CD 配置
├── Jenkinsfile          # Jenkins 流水线
└── pytest.ini          # Pytest 配置