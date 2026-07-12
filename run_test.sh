#!/bin/bash

set -e

ENV=${1:-test}

echo "======================"
echo "当前环境: $ENV"
echo "======================"


# 添加 pip 用户安装目录
export PATH=$HOME/Library/Python/3.9/bin:$PATH


echo "Python:"
python3 --version


echo "Pytest:"
pytest --version


echo "Allure:"
allure --version


echo "开始执行测试"


pytest \
automation/tests \
--alluredir=automation/reports/allure-results


echo "生成 Allure"


allure generate \
automation/reports/allure-results \
-o automation/reports/allure-report \
--clean


echo "测试完成"