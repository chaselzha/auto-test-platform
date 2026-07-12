#!/bin/bash


ENV=$1


if [ -z "$ENV" ]
then

    ENV=test

fi


echo "当前环境:$ENV"


pytest \
--env=$ENV \
automation/tests \
--alluredir=reports/allure-results



allure generate \
reports/allure-results \
-o reports/allure-report \
--clean


echo "测试完成"