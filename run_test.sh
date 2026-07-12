#!/bin/bash


ENV=${1:-test}


echo "当前环境:$ENV"


export PATH=$HOME/Library/Python/3.9/bin:$PATH


pytest \
automation/tests \
--env=$ENV \
--alluredir=allure-results



echo "测试完成"
