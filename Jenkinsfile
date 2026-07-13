pipeline {

    agent any

    /**********************
     * 参数化构建
     **********************/
    parameters {
        choice(
            name: 'ENV',
            choices: [
                'dev',
                'test',
                'prod'
            ],
            description: '请选择运行环境'
        )
    }

    /**********************
     * Pipeline 配置
     **********************/
    options {
        timestamps()

        disableConcurrentBuilds()

        buildDiscarder(
            logRotator(
                numToKeepStr: '30',
                daysToKeepStr: '15'
            )
        )
    }

    /**********************
     * 环境变量
     **********************/
    environment {

        PYTHON = "python3"

        PIP = "pip3"

    }

    stages {

        stage('环境检查') {

            steps {

                sh '''
                    echo "========== Python =========="
                    ${PYTHON} --version

                    echo "========== Java =========="
                    java -version

                    echo "========== Git =========="
                    git --version
                '''
            }

        }

        stage('安装依赖') {

            steps {

                sh '''
                    ${PIP} install -r requirements.txt
                '''

            }

        }

        stage('执行自动化测试') {

            steps {

                sh """
                    chmod +x run_test.sh
                    ./run_test.sh ${params.ENV}
                """

            }

        }

        stage('生成Allure报告') {

            steps {

                allure(
                        includeProperties: false,
                        jdk: '',
                        results: [[path: 'automation/reports/allure-results']]
                )

            }

        }

    }

    /**********************
     * Post
     **********************/
    post {

        always {

            echo "========== 自动化测试结束 =========="

            script {

                currentBuild.description =
                        "ENV=${params.ENV}"

            }

            archiveArtifacts(
                    artifacts: '''
automation/logs/**,
automation/screenshots/**,
automation/reports/**
''',
                    fingerprint: true,
                    allowEmptyArchive: true
            )

        }

        success {

            echo "构建成功"

        }

        failure {

            echo "构建失败"

        }

    }

}