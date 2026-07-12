#!/bin/bash


# 默认环境

ENV=${1:-test}



echo "===================="

echo "当前环境:$ENV"

echo "===================="




# 使用Jenkins创建的虚拟环境


.venv/bin/python -m pytest \

automation/tests \

--env=$ENV \

--alluredir=allure-results




echo "===================="

echo "测试完成"

echo "===================="
