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

                    echo """
==============================
Git Information

Branch : ${env.GIT_BRANCH_NAME}

Commit : ${env.GIT_COMMIT_ID}

Author : ${env.GIT_AUTHOR}

Message: ${env.GIT_COMMIT_MSG}

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




    /************************************************
     * Post Actions
     ************************************************/
    post {

    success {

        script {

            def html = readFile("ci/email-success.html")

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

            emailext(
                    to: params.EMAIL_TO,
                    mimeType: 'text/html',
                    subject: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER} Build Success",
                    body: html
            )

        }

    }

    failure {

        script {

            def html = readFile("ci/email-failure.html")

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

            emailext(
                    to: params.EMAIL_TO,
                    mimeType: 'text/html',
                    subject: "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER} Build Failed",
                    body: html
            )

        }

    }

    always {

        echo "Build Finished."

        cleanWs()

    }

}

}

