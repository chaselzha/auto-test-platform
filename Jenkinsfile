pipeline {
    agent any

    /************************************************
     * Pipeline Triggers
     ************************************************/
    triggers {
        // 每晚 2 点自动执行
        cron('0 2 * * *')
        // 每周一早上 8 点执行完整测试
        // cron('0 8 * * 1')
    }

    /************************************************
     * Pipeline Options
     ************************************************/
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5'))
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
            choices: ['test', 'dev', 'prod'],
            description: '请选择测试环境'
        )
        choice(
            name: 'BROWSER',
            choices: ['chrome', 'firefox', 'edge', 'all'],
            description: '请选择浏览器'
        )
        string(
            name: 'EMAIL_TO',
            defaultValue: 'cherryccc0327@gmail.com',
            description: '邮件接收人'
        )
        booleanParam(
            name: 'PARALLEL',
            defaultValue: true,
            description: '是否并行执行'
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
        HEADLESS = 'true'
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
                        [$class: 'CloneOption', depth: 0, noTags: false, shallow: false, timeout: 10],
                        [$class: 'PruneStaleBranch'],
                        [$class: 'LocalBranch', localBranch: 'main']
                    ]
                ])
                script {
                    env.BUILD_START_TIME = new Date().format(
                        "yyyy-MM-dd HH:mm:ss",
                        TimeZone.getTimeZone("Asia/Shanghai")
                    )
                    def gitBranch = sh(script: "git rev-parse --abbrev-ref HEAD", returnStdout: true).trim()
                    def gitCommit = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    def gitMsg = sh(script: "git log -1 --pretty=%s", returnStdout: true).trim()
                    def gitAuthor = sh(script: "git log -1 --pretty=%an", returnStdout: true).trim()

                    env.GIT_BRANCH_NAME = gitBranch
                    env.GIT_COMMIT_ID = gitCommit
                    env.GIT_COMMIT_MSG = gitMsg
                    env.GIT_AUTHOR = gitAuthor

                    writeFile(file: '.git-info/branch', text: gitBranch)
                    writeFile(file: '.git-info/commit', text: gitCommit)
                    writeFile(file: '.git-info/message', text: gitMsg)
                    writeFile(file: '.git-info/author', text: gitAuthor)

                    env.ALLURE_REPORT_URL = "${env.BUILD_URL}allure/"
                    env.BUILD_STATUS = "RUNNING"
                    env.BUILD_DURATION = "Calculating..."

                    sh '''
                        echo "========================================="
                        echo "Git Information"
                        echo "========================================="
                        echo "Branch: ${GIT_BRANCH_NAME}"
                        echo "Commit: ${GIT_COMMIT_ID}"
                        echo "Author: ${GIT_AUTHOR}"
                        echo "Message: ${GIT_COMMIT_MSG}"
                        echo "========================================="
                        echo "Checking ci directory..."
                        ls -la ci/ 2>/dev/null || echo "ci/ not found"
                    '''
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
                    echo "Python: $(python3 --version)"
                    echo "Java: $(java -version 2>&1 | head -1)"
                    echo "Git: $(git --version)"
                    echo ""
                    echo "Browser: ${BROWSER}"
                    echo "Environment: ${ENV}"
                    echo "Parallel: ${PARALLEL}"
                    echo "========================================="
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
                        python3 -m pip install --upgrade pip
                        python3 -m pip install --disable-pip-version-check --no-cache-dir -r requirements.txt
                    '''
                    def seconds = (System.currentTimeMillis() - start) / 1000
                    echo "Dependency installation finished. Elapsed Time : ${seconds} s"
                }
            }
        }

        /************************************************
         * Execute Test - 单浏览器
         ************************************************/
        stage('Execute Test') {
            when {
                expression { params.BROWSER != 'all' }
            }
            steps {
                script {
                    echo "========================================="
                    echo "Execute Automation Test"
                    echo "========================================="
                    echo "Browser: ${params.BROWSER}"
                    echo "Environment: ${params.ENV}"

                    def startTime = System.currentTimeMillis()
                    def parallelFlag = params.PARALLEL ? "-n 4" : ""

                    int result = sh(
                        script: """
                            export BROWSER=${params.BROWSER}
                            export HEADLESS=true
                            cd automation
                            python3 -m pytest tests/ \
                                --env=${params.ENV} \
                                --alluredir=reports/allure-results \
                                ${parallelFlag} \
                                -m "smoke or regression"
                        """,
                        returnStatus: true
                    )

                    // 计算耗时
                    def duration = (System.currentTimeMillis() - startTime) / 1000
                    env.BUILD_DURATION = "${duration}s"
                    env.BUILD_STATUS = result == 0 ? "SUCCESS" : "FAILURE"
                    currentBuild.result = result == 0 ? "SUCCESS" : "FAILURE"

                    echo ""
                    echo "========================================="
                    echo "Test Summary"
                    echo "========================================="
                    echo "Environment : ${params.ENV}"
                    echo "Browser     : ${params.BROWSER}"
                    echo "Duration    : ${env.BUILD_DURATION}"
                    echo "Exit Code   : ${result}"
                    echo "Status      : ${env.BUILD_STATUS}"
                    echo "========================================="
                }
            }
        }

        /************************************************
         * Execute Test - 多浏览器矩阵
         ************************************************/
        stage('Execute Test - Multi Browser') {
            when {
                expression { params.BROWSER == 'all' }
            }
            steps {
                script {
                    echo "========================================="
                    echo "Execute Multi-Browser Test"
                    echo "========================================="

                    def browsers = ['chrome', 'firefox', 'edge']
                    def results = [:]
                    def startTime = System.currentTimeMillis()

                    parallel browsers.collectEntries { browser ->
                        ["${browser}".toString(), {
                            echo "🚀 启动 ${browser} 测试..."
                            def browserStart = System.currentTimeMillis()
                            def parallelFlag = params.PARALLEL ? "-n 2" : ""

                            int result = sh(
                                script: """
                                    export BROWSER=${browser}
                                    export HEADLESS=true
                                    cd automation
                                    python3 -m pytest tests/ \
                                        --env=${params.ENV} \
                                        --alluredir=reports/allure-results-${browser} \
                                        ${parallelFlag} \
                                        -m "smoke or regression"
                                """,
                                returnStatus: true
                            )

                            results[browser] = result
                            def duration = (System.currentTimeMillis() - browserStart) / 1000
                            echo "${browser} 测试完成，耗时: ${duration}s，结果: ${result == 0 ? '✅ PASSED' : '❌ FAILED'}"
                        }]
                    }

                    // 计算总耗时
                    def totalDuration = (System.currentTimeMillis() - startTime) / 1000
                    env.BUILD_DURATION = "${totalDuration}s"

                    def failed = results.values().findAll { it != 0 }
                    env.BUILD_STATUS = failed.isEmpty() ? "SUCCESS" : "FAILURE"
                    currentBuild.result = failed.isEmpty() ? "SUCCESS" : "FAILURE"

                    echo ""
                    echo "========================================="
                    echo "Multi-Browser Test Summary"
                    echo "========================================="
                    results.each { key, value ->
                        echo "${key}: ${value == 0 ? '✅ PASSED' : '❌ FAILED'}"
                    }
                    echo "Total Duration: ${env.BUILD_DURATION}"
                    echo "========================================="
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

                    def resultDirs = []
                    if (params.BROWSER == 'all') {
                        resultDirs = ['chrome', 'firefox', 'edge'].collect { "automation/reports/allure-results-${it}" }
                    } else {
                        resultDirs = ['automation/reports/allure-results']
                    }

                    resultDirs.each { dir ->
                        if (fileExists(dir)) {
                            echo "✅ Allure results found: ${dir}"
                        } else {
                            echo "⚠️ Allure results not found: ${dir}"
                        }
                    }

                    allure(
                        includeProperties: false,
                        jdk: '',
                        results: resultDirs.collect { [path: it] }
                    )

                    env.ALLURE_REPORT_URL = "${env.BUILD_URL}allure"
                    echo "✅ Allure Report Generated Successfully"
                    echo "📊 Allure Report URL: ${env.ALLURE_REPORT_URL}"
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
                def gitBranch = "unknown"
                def gitCommit = "unknown"
                def gitMessage = "unknown"
                def gitAuthor = "unknown"

                try {
                    gitBranch = readFile('.git-info/branch').trim()
                    gitCommit = readFile('.git-info/commit').trim()
                    gitMessage = readFile('.git-info/message').trim()
                    gitAuthor = readFile('.git-info/author').trim()
                } catch (Exception e) {
                    echo "⚠️ Could not read Git info"
                }

                // 添加空值检查
                def buildDuration = env.BUILD_DURATION ?: "N/A"
                def buildStatus = "SUCCESS"
                def browser = params.BROWSER ?: "chrome"
                def buildTimestamp = new Date().format("yyyy-MM-dd HH:mm:ss", TimeZone.getTimeZone("Asia/Shanghai"))
                def jobName = env.JOB_NAME ?: "N/A"
                def buildNumber = env.BUILD_NUMBER ?: "N/A"
                def testEnv = params.ENV ?: "test"
                def buildUrl = env.BUILD_URL ?: "N/A"
                def allureUrl = env.ALLURE_REPORT_URL ?: "N/A"

                def html = readFile("ci/email-success.html")
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
                    .replace('${BROWSER}', browser)

                emailext(
                    to: params.EMAIL_TO,
                    mimeType: 'text/html',
                    subject: "✅ ${jobName} #${buildNumber} Build Success",
                    body: html
                )

                echo "📧 Success email sent to ${params.EMAIL_TO}"
                echo "   Duration: ${buildDuration}"
                cleanWs()
            }
        }

        failure {
            script {
                def gitBranch = "unknown"
                def gitCommit = "unknown"
                def gitMessage = "unknown"
                def gitAuthor = "unknown"

                try {
                    gitBranch = readFile('.git-info/branch').trim()
                    gitCommit = readFile('.git-info/commit').trim()
                    gitMessage = readFile('.git-info/message').trim()
                    gitAuthor = readFile('.git-info/author').trim()
                } catch (Exception e) {
                    echo "⚠️ Could not read Git info"
                }

                // 添加空值检查
                def buildDuration = env.BUILD_DURATION ?: "N/A"
                def buildStatus = "FAILURE"
                def browser = params.BROWSER ?: "chrome"
                def buildTimestamp = new Date().format("yyyy-MM-dd HH:mm:ss", TimeZone.getTimeZone("Asia/Shanghai"))
                def jobName = env.JOB_NAME ?: "N/A"
                def buildNumber = env.BUILD_NUMBER ?: "N/A"
                def testEnv = params.ENV ?: "test"
                def buildUrl = env.BUILD_URL ?: "N/A"
                def allureUrl = env.ALLURE_REPORT_URL ?: "N/A"

                def html = readFile("ci/email-failure.html")
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
                    .replace('${BROWSER}', browser)

                emailext(
                    to: params.EMAIL_TO,
                    mimeType: 'text/html',
                    subject: "❌ ${jobName} #${buildNumber} Build Failed",
                    body: html
                )

                echo "📧 Failure email sent to ${params.EMAIL_TO}"
                echo "   Duration: ${buildDuration}"
                cleanWs()
            }
        }

        always {
            echo ""
            echo "========================================="
            echo "Pipeline execution completed."
            echo "Build: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            echo "Status: ${env.BUILD_STATUS}"
            echo "Duration: ${env.BUILD_DURATION}"
            echo "========================================="
        }
    }
}