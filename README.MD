# Python UI 自动化测试平台
"# webhook test"

## 一、项目介绍

本项目是一套基于 Python + Selenium 构建的 Web UI 自动化测试框架。

采用企业级自动化测试架构设计：

- pytest 测试框架
- Selenium WebDriver 浏览器自动化
- POM(Page Object Model) 页面对象模型
- Allure 测试报告
- Jenkins 持续集成
- FastAPI 自动化测试平台


目前支持：

- Web UI 自动化测试
- 页面元素统一管理
- 测试日志记录
- 失败自动截图
- 测试报告生成


---

# 二、技术栈
"# test"

| 技术 | 用途 |
|---|---|
| Python 3.11 | 开发语言 |
| Selenium | Web自动化 |
| pytest | 测试框架 |
| POM | 页面对象设计 |
| Allure | 测试报告 |
| Jenkins | CI持续集成 |
| FastAPI | 测试平台接口 |

## Jenkins CI

项目支持 Jenkins 自动持续集成。

功能：

- GitHub Webhook 自动触发
- 参数化构建
- 自动安装依赖
- 自动执行 Pytest
- 自动生成 Allure 报告
- 自动保存测试日志
- 自动保存截图
- 自动清理历史构建


---
