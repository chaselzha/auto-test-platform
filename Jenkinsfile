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


        string(
            name: 'TEST_CASE',
            defaultValue: '',
            description: '指定测试文件，例如 test_baidu.py，不填则运行全部'
        )


        booleanParam(
            name: 'GENERATE_REPORT',
            defaultValue: true,
            description: '是否生成Allure报告'
        )
    }


    environment {

        PYTHON_HOME="/usr/bin/python3"

        PATH="/Users/chasel/Library/Python/3.9/bin:/opt/homebrew/bin:$PATH"

    }


    stages {


        stage('环境检查') {

            steps {

                sh '''
                echo "Python版本"
                python3 --version

                echo "Java版本"
                java -version

                echo "当前环境:"
                echo ${ENV}
                '''
            }
        }



        stage('安装依赖') {

            steps {

                sh '''
                python3 -m pip install -r requirements.txt
                '''
            }
        }




        stage('执行测试') {

            steps {

                sh '''

                chmod +x run_test.sh


                if [ -z "$TEST_CASE" ]
                then

                    ./run_test.sh ${ENV}

                else

                    pytest automation/tests/${TEST_CASE} \
                    --alluredir=allure-results

                fi


                '''

            }

        }





        stage('生成Allure报告') {

            when {

                expression {

                    return params.GENERATE_REPORT

                }

            }


            steps {

                allure(
                    includeProperties: false,
                    jdk: '',
                    results: [
                        [
                            path: 'allure-results'
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
                artifacts: 'allure-results/**',
                allowEmptyArchive: true
            )


        }



        success {

            echo "构建成功"

        }



        failure {

            echo "构建失败，请查看日志"

        }


    }

}