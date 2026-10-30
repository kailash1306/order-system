
pipeline {
    agent any

    environment {
        KUBECONFIG = 'C:\\jenkins-kube\\config'
        DOCKER_EXE = 'C:\\Users\\tkail\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        KUBECTL_EXE = 'C:\\Users\\tkail\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\kubectl.exe'
        IMAGE_NAME = '24mis0218/order-system:v1'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Source code will be checked out from GitHub by Jenkins.'
            }
        }

        stage('Verify Tools') {
            steps {
                bat '''
                    "%DOCKER_EXE%" --version
                    "%KUBECTL_EXE%" get nodes
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                    "%DOCKER_EXE%" build -t "%IMAGE_NAME%" .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    bat '''
                        echo %DH_TOKEN% | "%DOCKER_EXE%" login -u "%DH_USER%" --password-stdin
                        "%DOCKER_EXE%" push "%IMAGE_NAME%"
                        "%DOCKER_EXE%" logout
                    '''
                }
            }
        }

        stage('Deploy V1 to Kubernetes') {
            steps {
                bat '''
                    "%KUBECTL_EXE%" apply -f k8s/v1.yaml
                    "%KUBECTL_EXE%" set image deployment/order-v1 order-system="%IMAGE_NAME%"
                    "%KUBECTL_EXE%" rollout status deployment/order-v1 --timeout=120s
                    "%KUBECTL_EXE%" get deployments
                '''
            }
        }
    }

    post {
        success {
            echo 'V1 CI/CD pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check Console Output for the failing stage.'
        }
    }
}
