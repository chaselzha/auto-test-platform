#!/bin/bash


set -e



ENV=${1:-test}


echo "当前环境:$ENV"



export PATH=$HOME/Library/Python/3.9/bin:$PATH



pytest \
automation/tests \
-v \
--alluredir=automation/reports/allure-results \
--env=$ENV



allure generate \
automation/reports/allure-results \
-o automation/reports/allure-report \
--clean



echo "测试完成"