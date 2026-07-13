# CI Configuration

This directory contains all Continuous Integration (CI) related configuration files used by Jenkins.

---

## Directory Structure

```text
ci
│
├── email-template.html
├── README.md
```

---

## email-template.html

Enterprise HTML email template used by Jenkins Email Extension Plugin.

This template is shared by both successful and failed builds.

The Jenkins Pipeline replaces all placeholders before sending the email.

Example:

```groovy
def html = readFile('ci/email-template.html')

html = html
        .replace('${JOB_NAME}', env.JOB_NAME)
        .replace('${BUILD_NUMBER}', env.BUILD_NUMBER)
        .replace('${BUILD_STATUS}', currentBuild.currentResult)
```

---

## Supported Variables

| Variable | Description |
|----------|-------------|
| `${STATUS_COLOR}` | Status color |
| `${STATUS_ICON}` | Status icon |
| `${STATUS_TITLE}` | SUCCESS / FAILURE |
| `${STATUS_MESSAGE}` | Notification message |
| `${JOB_NAME}` | Jenkins Job Name |
| `${BUILD_NUMBER}` | Build Number |
| `${BUILD_STATUS}` | Build Status |
| `${BUILD_DURATION}` | Build Duration |
| `${BUILD_START_TIME}` | Build Time |
| `${ENV}` | Test Environment |
| `${GIT_BRANCH}` | Git Branch |
| `${GIT_COMMIT}` | Commit ID |
| `${GIT_MESSAGE}` | Commit Message |
| `${GIT_AUTHOR}` | Commit Author |
| `${BUILD_URL}` | Jenkins Build URL |
| `${ALLURE_URL}` | Allure Report URL |

---

## Jenkins Plugins

The following Jenkins plugins are required.

- Email Extension Plugin
- Allure Jenkins Plugin
- Git Plugin
- Pipeline Plugin

---

## Email Preview

The email includes the following information.

- Build Status
- Build Environment
- Git Branch
- Commit ID
- Commit Message
- Commit Author
- Build Duration
- Build Time
- Jenkins Build URL
- Allure Report URL
- Console Log URL

---

## Notes

This template follows the enterprise CI/CD email style.

It is designed to be reused by all Jenkins Pipeline jobs.

Avoid putting HTML directly inside Jenkinsfile.

Instead, maintain the HTML template here.

---

## Future Improvements

- Attach failed screenshots
- Attach test report
- Show Allure statistics
- Display Pass Rate
- Display Failed Cases
- Display Trend Chart
- DingTalk Notification
- WeCom Notification
- Slack Notification