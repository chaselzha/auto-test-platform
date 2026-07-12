#!/bin/bash


ENV=${1:-test}


echo "===================="

echo "当前环境:$ENV"

echo "===================="



.venv/bin/python -m pytest \
automation/tests \
--env=$ENV \
--alluredir=allure-results



echo "===================="

echo "测试完成"

echo "===================="