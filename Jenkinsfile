pipeline {

    agent any

    // ===== 定义全局变量（在 pipeline 顶部） =====
    variables {
        GIT_BRANCH = "unknown"
        GIT_COMMIT = "unknown"
        GIT_MESSAGE = "unknown"
        GIT_AUTHOR = "unknown"
    }

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
                cleanWs()

                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: 'git@github.com:chaselzha/auto-test-platform.git',
                        credentialsId: 'github-ssh-key'
                    ]],
                    extensions: [
                        [$class: 'CleanCheckout'],
                        [$class: 'CloneOption',
                            depth: 0,
                            noTags: false,
                            reference: '',
                            shallow: false,
                            timeout: 10
                        ],
                        [$class: 'PruneStaleBranch'],
                        [$class: 'LocalBranch', localBranch: 'main']
                    ]
                ])

                script {
                    env.BUILD_START_TIME = new Date().format(
                            "yyyy-MM-dd HH:mm:ss",
                            TimeZone.getTimeZone("Asia/Shanghai")
                    )

                    // ===== 获取 Git 信息并赋值给全局变量 =====
                    script.GIT_BRANCH = sh(
                            script: "git rev-parse --abbrev-ref HEAD",
                            returnStdout: true
                    ).trim()

                    script.GIT_COMMIT = sh(
                            script: "git rev-parse --short HEAD",
                            returnStdout: true
                    ).trim()

                    script.GIT_MESSAGE = sh(
                            script: "git log -1 --pretty=%s",
                            returnStdout: true
                    ).trim()

                    script.GIT_AUTHOR = sh(
                            script: "git log -1 --pretty=%an",
                            returnStdout: true
                    ).trim()

                    // 同时也设置环境变量（备用）
                    env.GIT_BRANCH_NAME = script.GIT_BRANCH
                    env.GIT_COMMIT_ID = script.GIT_COMMIT
                    env.GIT_COMMIT_MSG = script.GIT_MESSAGE
                    env.GIT_AUTHOR = script.GIT_AUTHOR

                    // ===== 为邮件通知准备的变量 =====
                    env.ALLURE_REPORT_URL = "${env.BUILD_URL}allure/"
                    env.BUILD_STATUS = "RUNNING"
                    env.BUILD_DURATION = "Calculating..."

                    // ===== 验证 ci 目录和文件 =====
                    sh '''
                        echo "========================================="
                        echo "Checking ci directory contents"
                        echo "========================================="
                        pwd
                        echo ""
                        echo "Listing all files in workspace:"
                        ls -la
                        echo ""
                        if [ -d "ci" ]; then
                            echo "✅ ci directory exists"
                            ls -la ci/
                            echo ""
                            if [ -f "ci/email-success.html" ] && [ -f "ci/email-failure.html" ]; then
                                echo "✅ Both email templates found!"
                            else
                                echo "⚠️ Some template files are missing"
                            fi
                        else
                            echo "❌ ci directory NOT found!"
                        fi
                    '''

                    echo """
==============================
Git Information (from Checkout)

Branch : ${script.GIT_BRANCH}
Commit : ${script.GIT_COMMIT}
Author : ${script.GIT_AUTHOR}
Message: ${script.GIT_MESSAGE}
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
                        python3 -m pip install --disable-pip-version-check --no-cache-dir -r requirements.txt
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
                        echo "No allure-results directory found."
                        echo "Skip Allure Report."
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

                // ===== 从全局变量读取 Git 信息 =====
                def gitBranch = script.GIT_BRANCH ?: "unknown"
                def gitCommit = script.GIT_COMMIT ?: "unknown"
                def gitMessage = script.GIT_MESSAGE ?: "unknown"
                def gitAuthor = script.GIT_AUTHOR ?: "unknown"

                // 如果全局变量为空，尝试从环境变量读取
                if (gitBranch == "unknown") {
                    gitBranch = env.GIT_BRANCH_NAME ?: "unknown"
                    gitCommit = env.GIT_COMMIT_ID ?: "unknown"
                    gitMessage = env.GIT_COMMIT_MSG ?: "unknown"
                    gitAuthor = env.GIT_AUTHOR ?: "unknown"
                }

                // 在 post 阶段设置这些变量
                def buildStatus = "SUCCESS"
                def buildDuration = currentBuild.durationString.replace(" and counting", "")
                def buildTimestamp = new Date().format(
                        "yyyy-MM-dd HH:mm:ss",
                        TimeZone.getTimeZone("Asia/Shanghai")
                )

                def jobName = env.JOB_NAME
                def buildNumber = env.BUILD_NUMBER
                def testEnv = params.ENV
                def buildUrl = env.BUILD_URL
                def allureUrl = env.ALLURE_REPORT_URL ?: "N/A"

                // 尝试读取文件，如果不存在则使用内联 HTML
                def html
                try {
                    if (fileExists("ci/email-success.html")) {
                        html = readFile("ci/email-success.html")
                        echo "✅ Loaded email template from ci/email-success.html"
                    } else {
                        throw new Exception("File not found")
                    }

                    // 替换文件中的占位符
                    html = html
                            .replace('${JOB_NAME}', jobName)
                            .replace('${BUILD_NUMBER}', buildNumber)
                            .replace('${ENV}', testEnv)
                            .replace('${BUILD_STATUS}', buildStatus)
                            .replace('${BUILD_DURATION}', buildDuration)
                            .replace('${GIT_BRANCH}', gitBranch)
                            .replace('${GIT_COMMIT}', gitCommit)
                            .replace('${GIT_MESSAGE}', gitMessage)
                            .replace('${GIT_AUTHOR}', gitAuthor)
                            .replace('${BUILD_URL}', buildUrl)
                            .replace('${ALLURE_URL}', allureUrl)
                            .replace('${BUILD_TIMESTAMP}', buildTimestamp)
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
                            <div class="header"><h2>✅ 自动化测试构建成功</h2></div>
                            <div class="content">
                                <h3>📋 构建信息</h3>
                                <div class="detail"><span class="label">项目名称：</span> ${jobName}</div>
                                <div class="detail"><span class="label">构建编号：</span> #${buildNumber}</div>
                                <div class="detail"><span class="label">测试环境：</span> ${testEnv}</div>
                                <div class="detail"><span class="label">构建状态：</span> ✅ ${buildStatus}</div>
                                <div class="detail"><span class="label">构建耗时：</span> ${buildDuration}</div>
                                <div class="detail"><span class="label">构建时间：</span> ${buildTimestamp}</div>
                                <h3>📝 Git 信息</h3>
                                <div class="detail"><span class="label">分支：</span> ${gitBranch}</div>
                                <div class="detail"><span class="label">提交 ID：</span> ${gitCommit}</div>
                                <div class="detail"><span class="label">提交信息：</span> ${gitMessage}</div>
                                <div class="detail"><span class="label">提交作者：</span> ${gitAuthor}</div>
                                <h3>🔗 报告链接</h3>
                                <div class="detail"><span class="label">Allure 测试报告：</span> <a href="${allureUrl}">${allureUrl}</a></div>
                                <div class="detail"><span class="label">Jenkins 构建：</span> <a href="${buildUrl}">${buildUrl}</a></div>
                            </div>
                            <div class="footer"><p>此邮件由 Jenkins 自动发送，请勿回复。</p></div>
                        </div>
                    </body>
                    </html>
                    """
                }

                emailext(
                        to: params.EMAIL_TO,
                        mimeType: 'text/html',
                        subject: "✅ ${jobName} #${buildNumber} Build Success",
                        body: html
                )

                echo "📧 Success email sent to ${params.EMAIL_TO}"
                echo "   Git Branch: ${gitBranch}"
                echo "   Git Commit: ${gitCommit}"

            }

        }

        failure {

            script {

                // ===== 从全局变量读取 Git 信息 =====
                def gitBranch = script.GIT_BRANCH ?: "unknown"
                def gitCommit = script.GIT_COMMIT ?: "unknown"
                def gitMessage = script.GIT_MESSAGE ?: "unknown"
                def gitAuthor = script.GIT_AUTHOR ?: "unknown"

                // 如果全局变量为空，尝试从环境变量读取
                if (gitBranch == "unknown") {
                    gitBranch = env.GIT_BRANCH_NAME ?: "unknown"
                    gitCommit = env.GIT_COMMIT_ID ?: "unknown"
                    gitMessage = env.GIT_COMMIT_MSG ?: "unknown"
                    gitAuthor = env.GIT_AUTHOR ?: "unknown"
                }

                // 在 post 阶段设置这些变量
                def buildStatus = "FAILURE"
                def buildDuration = currentBuild.durationString.replace(" and counting", "")
                def buildTimestamp = new Date().format(
                        "yyyy-MM-dd HH:mm:ss",
                        TimeZone.getTimeZone("Asia/Shanghai")
                )

                def jobName = env.JOB_NAME
                def buildNumber = env.BUILD_NUMBER
                def testEnv = params.ENV
                def buildUrl = env.BUILD_URL
                def allureUrl = env.ALLURE_REPORT_URL ?: "N/A"

                // 尝试读取文件，如果不存在则使用内联 HTML
                def html
                try {
                    if (fileExists("ci/email-failure.html")) {
                        html = readFile("ci/email-failure.html")
                        echo "✅ Loaded email template from ci/email-failure.html"
                    } else {
                        throw new Exception("File not found")
                    }

                    html = html
                            .replace('${JOB_NAME}', jobName)
                            .replace('${BUILD_NUMBER}', buildNumber)
                            .replace('${ENV}', testEnv)
                            .replace('${BUILD_STATUS}', buildStatus)
                            .replace('${BUILD_DURATION}', buildDuration)
                            .replace('${GIT_BRANCH}', gitBranch)
                            .replace('${GIT_COMMIT}', gitCommit)
                            .replace('${GIT_MESSAGE}', gitMessage)
                            .replace('${GIT_AUTHOR}', gitAuthor)
                            .replace('${BUILD_URL}', buildUrl)
                            .replace('${ALLURE_URL}', allureUrl)
                            .replace('${BUILD_TIMESTAMP}', buildTimestamp)
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
                            <div class="header"><h2>❌ 自动化测试构建失败</h2></div>
                            <div class="content">
                                <div class="error-box"><strong>⚠️ 构建失败，请及时检查！</strong></div>
                                <h3>📋 构建信息</h3>
                                <div class="detail"><span class="label">项目名称：</span> ${jobName}</div>
                                <div class="detail"><span class="label">构建编号：</span> #${buildNumber}</div>
                                <div class="detail"><span class="label">测试环境：</span> ${testEnv}</div>
                                <div class="detail"><span class="label">构建状态：</span> ❌ ${buildStatus}</div>
                                <div class="detail"><span class="label">构建耗时：</span> ${buildDuration}</div>
                                <div class="detail"><span class="label">构建时间：</span> ${buildTimestamp}</div>
                                <h3>📝 Git 信息</h3>
                                <div class="detail"><span class="label">分支：</span> ${gitBranch}</div>
                                <div class="detail"><span class="label">提交 ID：</span> ${gitCommit}</div>
                                <div class="detail"><span class="label">提交信息：</span> ${gitMessage}</div>
                                <div class="detail"><span class="label">提交作者：</span> ${gitAuthor}</div>
                                <h3>🔗 报告链接</h3>
                                <div class="detail"><span class="label">Allure 测试报告：</span> <a href="${allureUrl}">${allureUrl}</a></div>
                                <div class="detail"><span class="label">Jenkins 构建：</span> <a href="${buildUrl}">${buildUrl}</a></div>
                            </div>
                            <div class="footer"><p>此邮件由 Jenkins 自动发送，请勿回复。</p></div>
                        </div>
                    </body>
                    </html>
                    """
                }

                emailext(
                        to: params.EMAIL_TO,
                        mimeType: 'text/html',
                        subject: "❌ ${jobName} #${buildNumber} Build Failed",
                        body: html
                )

                echo "📧 Failure email sent to ${params.EMAIL_TO}"
                echo "   Git Branch: ${gitBranch}"
                echo "   Git Commit: ${gitCommit}"

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