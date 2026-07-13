pipeline {

    agent any

    /************************************************
     * Pipeline Options
     ************************************************/
    options {

        buildDiscarder(logRotator(
                numToKeepStr: '10',
                artifactNumToKeepStr: '5'
        ))

        disableConcurrentBuilds()

        timestamps()

        ansiColor('xterm')

    }

    /************************************************
     * Build Parameters
     ************************************************/
    parameters {

        choice(
                name: 'ENV',
                choices: [
                        'test',
                        'dev',
                        'prod'
                ],
                description: '请选择测试环境'
        )

        string(
                name: 'EMAIL_TO',
                defaultValue: 'cherryccc0327@gmail.com',
                description: '邮件接收人（多个邮箱使用英文逗号分隔）'
        )

    }

    /************************************************
     * Global Environment
     ************************************************/
    environment {

        ALLURE_HOME = tool 'allure'

        GIT_BRANCH_NAME = ''

        GIT_COMMIT_ID = ''

        GIT_COMMIT_MSG = ''

        GIT_AUTHOR = ''

        BUILD_STATUS = ''

        BUILD_DURATION = ''

        BUILD_START_TIME = ''

    }

    /************************************************
     * Pipeline Stages
     ************************************************/
    stages {

        /************************************************
         * Checkout Source Code
         ************************************************/
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.BUILD_START_TIME = new Date().format(
                            "yyyy-MM-dd HH:mm:ss",
                            TimeZone.getTimeZone("Asia/Shanghai")
                    )

                    env.GIT_BRANCH_NAME = sh(
                            script: "git rev-parse --abbrev-ref HEAD",
                            returnStdout: true
                    ).trim()

                    env.GIT_COMMIT_ID = sh(
                            script: "git rev-parse --short HEAD",
                            returnStdout: true
                    ).trim()

                    env.GIT_COMMIT_MSG = sh(
                            script: "git log -1 --pretty=%s",
                            returnStdout: true
                    ).trim()

                    env.GIT_AUTHOR = sh(
                            script: "git log -1 --pretty=%an",
                            returnStdout: true
                    ).trim()

                    // ===== 为邮件通知准备的变量 =====
                    env.ALLURE_REPORT_URL = "${env.BUILD_URL}allure/"

                    // 设置默认值，post 阶段会更新
                    env.BUILD_STATUS = "RUNNING"
                    env.BUILD_DURATION = "Calculating..."

                    echo """
==============================
Git Information

Branch : ${env.GIT_BRANCH_NAME}
Commit : ${env.GIT_COMMIT_ID}
Author : ${env.GIT_AUTHOR}
Message: ${env.GIT_COMMIT_MSG}
Allure: ${env.ALLURE_REPORT_URL}
==============================
"""
                }
            }
        }

        /************************************************
         * Environment Check
         ************************************************/
        stage('Environment Check') {

            steps {

                sh '''
                    echo "========================================="
                    echo "      Jenkins Environment Check"
                    echo "========================================="

                    echo ""
                    echo "Current User:"
                    whoami

                    echo ""
                    echo "Host Name:"
                    hostname

                    echo ""
                    echo "Current Directory:"
                    pwd

                    echo ""
                    echo "Operating System:"
                    uname -a

                    echo ""
                    echo "Workspace:"
                    echo $WORKSPACE

                    echo ""
                    echo "Build Number:"
                    echo $BUILD_NUMBER

                    echo ""
                    echo "Build URL:"
                    echo $BUILD_URL

                    echo ""
                    echo "========================================="
                    echo "Python Information"
                    echo "========================================="

                    python3 --version

                    which python3

                    pip3 --version

                    which pip3

                    echo ""
                    echo "========================================="
                    echo "Java Information"
                    echo "========================================="

                    java -version

                    which java

                    echo ""
                    echo "========================================="
                    echo "Git Information"
                    echo "========================================="

                    git --version

                    which git

                    echo ""
                    echo "========================================="
                    echo "Browser Information"
                    echo "========================================="

                    if command -v "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" >/dev/null 2>&1
                    then
                        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version
                    else
                        echo "Google Chrome Not Found"
                    fi

                    echo ""
                    echo "========================================="
                    echo "ChromeDriver Information"
                    echo "========================================="

                    if command -v chromedriver >/dev/null 2>&1
                    then
                        chromedriver --version
                    else
                        echo "ChromeDriver Not Found"
                    fi

                    echo ""
                    echo "========================================="
                    echo "Environment Parameter"
                    echo "========================================="

                    echo "ENV=${ENV}"

                    echo "EMAIL_TO=${EMAIL_TO}"

                    echo ""
                    echo "Environment Check Finished."

                '''

            }

        }

        /************************************************
         * Install Dependencies
         ************************************************/
        stage('Install Dependencies') {

            steps {

                script {

                    echo "========================================="
                    echo "Install Python Dependencies"
                    echo "========================================="

                    def start = System.currentTimeMillis()

                    sh '''
                        set -e

                        echo ""
                        echo "Python Version"
                        python3 --version

                        echo ""
                        echo "Pip Version"
                        pip3 --version

                        echo ""
                        echo "Upgrade Pip"

                        python3 -m pip install --upgrade pip

                        echo ""
                        echo "Install Requirements"

                        python3 -m pip install \
                            --disable-pip-version-check \
                            --no-cache-dir \
                            -r requirements.txt

                        echo ""
                        echo "Installed Packages"

                        python3 -m pip list
                    '''

                    def seconds = (System.currentTimeMillis() - start) / 1000

                    echo ""
                    echo "Dependency installation finished."
                    echo "Elapsed Time : ${seconds} s"
                    echo ""

                }

            }

        }

        /************************************************
         * Execute Automation Test
         ************************************************/
        stage('Execute Test') {

            steps {

                script {

                    echo "========================================="
                    echo "Execute Automation Test"
                    echo "========================================="

                    def startTime = System.currentTimeMillis()

                    // 执行测试，捕获退出码
                    int result = sh(
                            script: """
                                chmod +x run_test.sh
                                ./run_test.sh ${params.ENV}
                            """,
                            returnStatus: true
                    )

                    def duration = (System.currentTimeMillis() - startTime) / 1000

                    env.BUILD_DURATION = "${duration}s"

                    echo ""
                    echo "========================================="
                    echo "Test Summary"
                    echo "========================================="
                    echo "Environment : ${params.ENV}"
                    echo "Duration    : ${env.BUILD_DURATION}"
                    echo "Exit Code   : ${result}"
                    echo "========================================="

                    if (result == 0) {

                        env.BUILD_STATUS = "SUCCESS"

                        currentBuild.result = "SUCCESS"

                        echo ""
                        echo "Automation Test Passed."
                        echo ""

                    } else {

                        env.BUILD_STATUS = "FAILURE"

                        currentBuild.result = "FAILURE"

                        echo ""
                        echo "Automation Test Failed."
                        echo ""

                    }

                }

            }

        }

        /************************************************
         * Generate Allure Report
         ************************************************/
        stage('Generate Allure Report') {

            steps {

                script {

                    echo "========================================="
                    echo "Generate Allure Report"
                    echo "========================================="

                    if (fileExists('automation/reports/allure-results')) {

                        echo "Allure results found."

                        allure(
                                includeProperties: false,
                                jdk: '',
                                results: [[path: 'automation/reports/allure-results']]
                        )

                        echo ""
                        echo "========================================="
                        echo "Allure Report Generated Successfully"
                        echo "========================================="

                        env.ALLURE_REPORT_URL = "${env.BUILD_URL}allure"

                    } else {

                        echo ""
                        echo "========================================="
                        echo "WARNING"
                        echo "========================================="
                        echo "No allure-results directory found."
                        echo "Skip Allure Report."
                        echo ""

                        env.ALLURE_REPORT_URL = "N/A"

                    }

                }

            }

        }

    }

    /************************************************
     * Post Actions
     ************************************************/
    post {

        success {

            script {

                // 在 post 阶段重新设置这些变量
                env.BUILD_STATUS = "SUCCESS"
                env.BUILD_DURATION = currentBuild.durationString.replace(" and counting", "")
                env.BUILD_TIMESTAMP = new Date().format(
                        "yyyy-MM-dd HH:mm:ss",
                        TimeZone.getTimeZone("Asia/Shanghai")
                )

                // 尝试读取文件，如果不存在则使用内联 HTML
                def html
                try {
                    html = readFile("ci/email-success.html")
                    echo "✅ Loaded email template from ci/email-success.html"
                } catch (Exception e) {
                    echo "⚠️ ci/email-success.html not found, using inline template"
                    html = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                            .header { background: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px; }
                            .content { padding: 20px; background: #f9f9f9; border-radius: 5px; margin-top: 20px; }
                            .detail { margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #4CAF50; }
                            .label { font-weight: bold; color: #555; }
                            .footer { margin-top: 20px; text-align: center; color: #666; font-size: 12px; }
                            a { color: #4CAF50; text-decoration: none; }
                            a:hover { text-decoration: underline; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h2>✅ 自动化测试构建成功</h2>
                            </div>
                            <div class="content">
                                <h3>📋 构建信息</h3>
                                <div class="detail"><span class="label">项目名称：</span> ${JOB_NAME}</div>
                                <div class="detail"><span class="label">构建编号：</span> #${BUILD_NUMBER}</div>
                                <div class="detail"><span class="label">测试环境：</span> ${ENV}</div>
                                <div class="detail"><span class="label">构建状态：</span> ✅ ${BUILD_STATUS}</div>
                                <div class="detail"><span class="label">构建耗时：</span> ${BUILD_DURATION}</div>
                                <div class="detail"><span class="label">构建时间：</span> ${BUILD_TIMESTAMP}</div>
                                <h3>📝 Git 信息</h3>
                                <div class="detail"><span class="label">分支：</span> ${GIT_BRANCH}</div>
                                <div class="detail"><span class="label">提交 ID：</span> ${GIT_COMMIT}</div>
                                <div class="detail"><span class="label">提交信息：</span> ${GIT_MESSAGE}</div>
                                <div class="detail"><span class="label">提交作者：</span> ${GIT_AUTHOR}</div>
                                <h3>🔗 报告链接</h3>
                                <div class="detail"><span class="label">Allure 测试报告：</span> <a href="${ALLURE_URL}">${ALLURE_URL}</a></div>
                                <div class="detail"><span class="label">Jenkins 构建：</span> <a href="${BUILD_URL}">${BUILD_URL}</a></div>
                            </div>
                            <div class="footer">
                                <p>此邮件由 Jenkins 自动发送，请勿回复。</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                }

                html = html
                        .replace('${JOB_NAME}', env.JOB_NAME)
                        .replace('${BUILD_NUMBER}', env.BUILD_NUMBER)
                        .replace('${ENV}', params.ENV)
                        .replace('${BUILD_STATUS}', env.BUILD_STATUS)
                        .replace('${BUILD_DURATION}', env.BUILD_DURATION)
                        .replace('${GIT_BRANCH}', env.GIT_BRANCH_NAME)
                        .replace('${GIT_COMMIT}', env.GIT_COMMIT_ID)
                        .replace('${GIT_MESSAGE}', env.GIT_COMMIT_MSG)
                        .replace('${GIT_AUTHOR}', env.GIT_AUTHOR)
                        .replace('${BUILD_URL}', env.BUILD_URL)
                        .replace('${ALLURE_URL}', env.ALLURE_REPORT_URL)
                        .replace('${BUILD_TIMESTAMP}', env.BUILD_TIMESTAMP)

                emailext(
                        to: params.EMAIL_TO,
                        mimeType: 'text/html',
                        subject: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER} Build Success",
                        body: html
                )

                echo "📧 Success email sent to ${params.EMAIL_TO}"

            }

        }

        failure {

            script {

                // 在 post 阶段重新设置这些变量
                env.BUILD_STATUS = "FAILURE"
                env.BUILD_DURATION = currentBuild.durationString.replace(" and counting", "")
                env.BUILD_TIMESTAMP = new Date().format(
                        "yyyy-MM-dd HH:mm:ss",
                        TimeZone.getTimeZone("Asia/Shanghai")
                )

                // 尝试读取文件，如果不存在则使用内联 HTML
                def html
                try {
                    html = readFile("ci/email-failure.html")
                    echo "✅ Loaded email template from ci/email-failure.html"
                } catch (Exception e) {
                    echo "⚠️ ci/email-failure.html not found, using inline template"
                    html = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                            .header { background: #f44336; color: white; padding: 20px; text-align: center; border-radius: 5px; }
                            .content { padding: 20px; background: #f9f9f9; border-radius: 5px; margin-top: 20px; }
                            .detail { margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #f44336; }
                            .error-box { background: #fff3f3; border: 1px solid #f44336; padding: 15px; border-radius: 5px; margin: 15px 0; }
                            .label { font-weight: bold; color: #555; }
                            .footer { margin-top: 20px; text-align: center; color: #666; font-size: 12px; }
                            a { color: #f44336; text-decoration: none; }
                            a:hover { text-decoration: underline; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h2>❌ 自动化测试构建失败</h2>
                            </div>
                            <div class="content">
                                <div class="error-box">
                                    <strong>⚠️ 构建失败，请及时检查！</strong>
                                </div>
                                <h3>📋 构建信息</h3>
                                <div class="detail"><span class="label">项目名称：</span> ${JOB_NAME}</div>
                                <div class="detail"><span class="label">构建编号：</span> #${BUILD_NUMBER}</div>
                                <div class="detail"><span class="label">测试环境：</span> ${ENV}</div>
                                <div class="detail"><span class="label">构建状态：</span> ❌ ${BUILD_STATUS}</div>
                                <div class="detail"><span class="label">构建耗时：</span> ${BUILD_DURATION}</div>
                                <div class="detail"><span class="label">构建时间：</span> ${BUILD_TIMESTAMP}</div>
                                <h3>📝 Git 信息</h3>
                                <div class="detail"><span class="label">分支：</span> ${GIT_BRANCH}</div>
                                <div class="detail"><span class="label">提交 ID：</span> ${GIT_COMMIT}</div>
                                <div class="detail"><span class="label">提交信息：</span> ${GIT_MESSAGE}</div>
                                <div class="detail"><span class="label">提交作者：</span> ${GIT_AUTHOR}</div>
                                <h3>🔗 报告链接</h3>
                                <div class="detail"><span class="label">Allure 测试报告：</span> <a href="${ALLURE_URL}">${ALLURE_URL}</a></div>
                                <div class="detail"><span class="label">Jenkins 构建：</span> <a href="${BUILD_URL}">${BUILD_URL}</a></div>
                            </div>
                            <div class="footer">
                                <p>此邮件由 Jenkins 自动发送，请勿回复。</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                }

                html = html
                        .replace('${JOB_NAME}', env.JOB_NAME)
                        .replace('${BUILD_NUMBER}', env.BUILD_NUMBER)
                        .replace('${ENV}', params.ENV)
                        .replace('${BUILD_STATUS}', env.BUILD_STATUS)
                        .replace('${BUILD_DURATION}', env.BUILD_DURATION)
                        .replace('${GIT_BRANCH}', env.GIT_BRANCH_NAME)
                        .replace('${GIT_COMMIT}', env.GIT_COMMIT_ID)
                        .replace('${GIT_MESSAGE}', env.GIT_COMMIT_MSG)
                        .replace('${GIT_AUTHOR}', env.GIT_AUTHOR)
                        .replace('${BUILD_URL}', env.BUILD_URL)
                        .replace('${ALLURE_URL}', env.ALLURE_REPORT_URL)
                        .replace('${BUILD_TIMESTAMP}', env.BUILD_TIMESTAMP)

                emailext(
                        to: params.EMAIL_TO,
                        mimeType: 'text/html',
                        subject: "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER} Build Failed",
                        body: html
                )

                echo "📧 Failure email sent to ${params.EMAIL_TO}"

            }

        }

        always {

            echo "========================================="
            echo "Build Finished."
            echo "========================================="

            cleanWs()

        }

    }

}