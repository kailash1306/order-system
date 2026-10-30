
pipeline {
    agent any

    options {
        skipDefaultCheckout(false)
        timestamps()
    }

    environment {
        DOCKER_EXE = 'C:\\Users\\tkail\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        KUBECTL_EXE = 'C:\\Users\\tkail\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\kubectl.exe'

        DOCKER_IMAGE = '24mis0218/order-system:v1'
        KUBECONFIG = 'C:\\jenkins-kube\\config'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Source code checked out from GitHub.'
                bat 'git log -1 --oneline'
            }
        }

        stage('Verify Tools') {
            steps {
                bat '''
                    @echo off
                    "%DOCKER_EXE%" --version
                    if errorlevel 1 exit /b 1

                    "%KUBECTL_EXE%" version --client
                    if errorlevel 1 exit /b 1

                    "%KUBECTL_EXE%" get nodes
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                    @echo off
                    "%DOCKER_EXE%" build -t "%DOCKER_IMAGE%" .
                    if errorlevel 1 exit /b 1
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
                    powershell '''
                        $ErrorActionPreference = "Stop"
                        $docker = $env:DOCKER_EXE

                        $env:DH_TOKEN |
                            & $docker login `
                                --username $env:DH_USER `
                                --password-stdin

                        if ($LASTEXITCODE -ne 0) {
                            throw "Docker Hub login failed."
                        }

                        & $docker push $env:DOCKER_IMAGE

                        if ($LASTEXITCODE -ne 0) {
                            throw "Docker Hub push failed."
                        }

                        & $docker logout
                    '''
                }
            }
        }

        stage('Deploy V1 to Kubernetes') {
            steps {
                bat '''
                    @echo off

                    "%KUBECTL_EXE%" apply -f k8s/v1.yaml
                    if errorlevel 1 exit /b 1

                    "%KUBECTL_EXE%" set image deployment/order-v1 order-system="%DOCKER_IMAGE%"
                    if errorlevel 1 exit /b 1

                    "%KUBECTL_EXE%" rollout status deployment/order-v1 --timeout=120s
                    if errorlevel 1 exit /b 1

                    "%KUBECTL_EXE%" get deployments
                    if errorlevel 1 exit /b 1

                    "%KUBECTL_EXE%" get services
                    if errorlevel 1 exit /b 1
                '''
            }
        }
    }

    post {
        success {
            echo 'V1 pipeline succeeded: image pushed and Kubernetes rollout verified.'
        }

        failure {
            echo 'V1 pipeline failed. Check the first failing stage in Console Output.'
        }

        always {
            echo 'V1 CI/CD pipeline finished.'
        }
    }
}
