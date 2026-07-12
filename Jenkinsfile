pipeline {

    agent any


    environment {

        PATH = "/Users/chasel/Library/Python/3.9/bin:/opt/homebrew/bin:$PATH"

    }


    stages {


        stage('环境检查') {

            steps {

                sh '''
                echo "Python版本"
                python3 --version

                echo "Java版本"
                java -version

                echo "PATH"
                echo $PATH
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

                ./run_test.sh test
                '''

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

        }


    }


}