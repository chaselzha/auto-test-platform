pipeline {

    agent any

    options {
        buildDiscarder(logRotator(
                numToKeepStr: '10',
                artifactNumToKeepStr: '5'
        ))
        disableConcurrentBuilds()
        timestamps()
    }

    parameters {
        choice(
                name: 'ENV',
                choices: ['test', 'dev', 'prod'],
                description: '请选择测试环境'
        )
    }

    environment {
        ALLURE_HOME = tool 'allure'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('环境检查') {
            steps {
                sh '''
                    echo "==============================="
                    echo "Python版本"
                    python3 --version

                    echo ""
                    echo "Java版本"
                    java -version

                    echo ""
                    echo "当前环境：${ENV}"
                    echo "==============================="
                '''
            }
        }

        stage('安装依赖') {
            steps {
                sh '''
                    pip3 install -r requirements.txt
                '''
            }
        }

        stage('执行测试') {
            steps {
                sh '''
                    chmod +x run_test.sh
                    ./run_test.sh ${ENV}
                '''
            }
        }

        stage('生成Allure报告') {
            steps {
                allure(
                        includeProperties: false,
                        jdk: '',
                        results: [[path: 'allure-results']]
                )
            }
        }
    }

    post {

        success {

            echo '自动化测试执行成功'

            emailext(
                    to: 'cherryccc0327@gmail.com',
                    subject: "✅ ${JOB_NAME} #${BUILD_NUMBER} 构建成功",
                    mimeType: 'text/html',
                    body: """
                    <html>
                    <body>

                    <h2 style="color:green;">✅ Jenkins 自动化测试成功</h2>

                    <table border="1" cellspacing="0" cellpadding="8">
                        <tr>
                            <td><b>项目</b></td>
                            <td>${JOB_NAME}</td>
                        </tr>

                        <tr>
                            <td><b>构建号</b></td>
                            <td>#${BUILD_NUMBER}</td>
                        </tr>

                        <tr>
                            <td><b>运行环境</b></td>
                            <td>${params.ENV}</td>
                        </tr>

                        <tr>
                            <td><b>构建状态</b></td>
                            <td style="color:green;">SUCCESS</td>
                        </tr>

                        <tr>
                            <td><b>构建地址</b></td>
                            <td>
                                <a href="${BUILD_URL}">
                                    ${BUILD_URL}
                                </a>
                            </td>
                        </tr>

                        <tr>
                            <td><b>Allure报告</b></td>
                            <td>
                                <a href="${BUILD_URL}allure">
                                    查看Allure Report
                                </a>
                            </td>
                        </tr>

                    </table>

                    </body>
                    </html>
                    """
            )

        }

        failure {

            echo '自动化测试执行失败'

            emailext(
                    to: 'cherryccc0327@gmail.com',
                    subject: "❌ ${JOB_NAME} #${BUILD_NUMBER} 构建失败",
                    mimeType: 'text/html',
                    body: """
                    <html>
                    <body>

                    <h2 style="color:red;">❌ Jenkins 自动化测试失败</h2>

                    <table border="1" cellspacing="0" cellpadding="8">
                        <tr>
                            <td><b>项目</b></td>
                            <td>${JOB_NAME}</td>
                        </tr>

                        <tr>
                            <td><b>构建号</b></td>
                            <td>#${BUILD_NUMBER}</td>
                        </tr>

                        <tr>
                            <td><b>运行环境</b></td>
                            <td>${params.ENV}</td>
                        </tr>

                        <tr>
                            <td><b>构建状态</b></td>
                            <td style="color:red;">FAILED</td>
                        </tr>

                        <tr>
                            <td><b>查看日志</b></td>
                            <td>
                                <a href="${BUILD_URL}">
                                    ${BUILD_URL}
                                </a>
                            </td>
                        </tr>

                    </table>

                    </body>
                    </html>
                    """
            )
        }

        always {
            cleanWs()
        }
    }
}