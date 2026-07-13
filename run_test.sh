#!/bin/bash

ENV=$1

if [ -z "$ENV" ]; then
    ENV=test
fi

echo "=============================="
echo "当前运行环境：$ENV"
echo "=============================="

# pytest 所在目录
export PATH=$HOME/Library/Python/3.9/bin:$PATH

mkdir -p automation/reports/allure-results
mkdir -p automation/logs
mkdir -p automation/screenshots

pytest automation/tests \
    --env=$ENV \
    -vs \
    --alluredir=automation/reports/allure-results

echo "=============================="
echo "测试完成"
echo "=============================="