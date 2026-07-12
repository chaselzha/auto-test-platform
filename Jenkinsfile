pipeline {


    agent any



    parameters {


        choice(
            name: 'ENV',
            choices: [
                'test',
                'dev',
                'prod'
            ],
            description: '选择运行环境'
        )


        choice(
            name: 'BROWSER',
            choices: [
                'chrome'
            ],
            description: '选择浏览器'
        )


    }



    environment {


        PATH = "/Users/chasel/Library/Python/3.9/bin:/opt/homebrew/bin:$PATH"


    }



    stages {



        stage('环境检查') {


            steps {


                sh """

                echo 当前环境:
                echo ${ENV}


                echo 当前浏览器:
                echo ${BROWSER}


                python3 --version


                java -version


                pytest --version


                allure --version


                """

            }

        }





        stage('安装依赖') {


            steps {


                sh """

                python3 -m pip install -r requirements.txt


                """

            }

        }






        stage('执行自动化测试') {


            steps {


                sh """


                chmod +x run_test.sh


                ./run_test.sh ${ENV}



                """


            }

        }





        stage('生成Allure报告') {


            steps {


                allure(
                    includeProperties: false,
                    jdk: '',
                    results: [
                        [
                            path: 'automation/reports/allure-results'
                        ]
                    ]
                )


            }

        }




    }



    post {


        always {


            echo "自动化测试执行完成"


            archiveArtifacts(
                artifacts:
                'automation/logs/**/*,automation/screenshots/**/*',
                allowEmptyArchive:true
            )


        }



        success {


            echo "测试成功"


        }



        failure {


            echo "测试失败，请查看Allure报告"


        }


    }


}