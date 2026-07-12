#!/bin/bash

# 任意一步失败，立即退出
set -e

# 获取环境参数
ENV=${1:-test}

echo "当前环境:$ENV"

# 创建Allure结果目录
mkdir -p allure-results

# 执行自动化测试
python3 -m pytest \
automation/tests \
--env=$ENV \
--alluredir=allure-results


echo "测试执行完成"