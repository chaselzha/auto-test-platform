pipeline {

    agent any


    environment {
        PYTHONUNBUFFERED = '1'
    }


    stages {


        stage('环境检查') {

            steps {

                sh '''
                echo "Python版本"
                python3 --version

                echo "Java版本"
                java -version
                '''

            }

        }



        stage('安装依赖') {

            steps {

                sh '''
                python3 -m pip install --user -r requirements.txt
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

                allure([
                    includeProperties: false,
                    jdk: '',
                    results: [
                        [
                            path: 'allure-results'
                        ]
                    ]
                ])

            }

        }


    }



    post {


        always {

            echo '自动化测试执行完成'

        }


        success {

            echo '测试通过'

        }


        failure {

            echo '测试失败，请查看日志'

        }


    }


}