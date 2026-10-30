
pipeline {
    agent any

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
                    "%DOCKER_EXE%" --version
                    "%KUBECTL_EXE%" version --client
                    "%KUBECTL_EXE%" get nodes
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                    "%DOCKER_EXE%" build -t "%DOCKER_IMAGE%" .
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
                    "%KUBECTL_EXE%" apply -f k8s/v1.yaml
                    "%KUBECTL_EXE%" set image deployment/order-v1 order-system="%DOCKER_IMAGE%"
                    "%KUBECTL_EXE%" rollout status deployment/order-v1 --timeout=120s
                    "%KUBECTL_EXE%" get deployments
                    "%KUBECTL_EXE%" get services
                '''
            }
        }
    }

    post {
        success {
            echo 'V1 pipeline completed successfully.'
        }
        failure {
            echo 'V1 pipeline failed. Check Console Output.'
        }
        always {
            echo 'V1 CI/CD pipeline finished.'
        }
    }
}
