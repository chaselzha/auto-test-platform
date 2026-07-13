#!/bin/bash
# run_test.sh

# 设置编码
export PYTHONIOENCODING=utf-8
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 获取参数
ENV=${1:-test}
BROWSER=${2:-chrome}
PARALLEL=${3:-4}
MARKERS=${4:-smoke}

echo "=============================="
echo "自动化测试执行器"
echo "=============================="
echo "环境      : ${ENV}"
echo "浏览器    : ${BROWSER}"
echo "并行数    : ${PARALLEL}"
echo "测试标记  : ${MARKERS}"
echo "=============================="

# 设置环境变量
export BROWSER=${BROWSER}
export HEADLESS=true
export TEST_ENV=${ENV}

# 执行测试
cd automation

python3 -m pytest tests/ \
    --env=${ENV} \
    --alluredir=reports/allure-results \
    -n ${PARALLEL} \
    -v \
    --tb=short \
    -m "${MARKERS}"

EXIT_CODE=$?

echo "=============================="
echo "测试完成"
echo "退出码: ${EXIT_CODE}"
echo "=============================="

exit ${EXIT_CODE}