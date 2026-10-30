pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    environment {
        DOCKER_EXE = 'C:\\Users\\tkail\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        KUBECTL_EXE = 'C:\\Users\\tkail\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\kubectl.exe'

        IMAGE_NAME = '24mis0218/order-system:v1'
        KUBE_CONFIG = 'C:\\jenkins-kube\\config'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/kailash1306/order-system.git'
            }
        }

        stage('Verify Tools') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    if (-not (Test-Path $env:DOCKER_EXE)) {
                        throw "Docker executable not found: $env:DOCKER_EXE"
                    }

                    if (-not (Test-Path $env:KUBECTL_EXE)) {
                        throw "kubectl executable not found: $env:KUBECTL_EXE"
                    }

                    if (-not (Test-Path $env:KUBE_CONFIG)) {
                        throw "Kubeconfig not found: $env:KUBE_CONFIG"
                    }

                    & $env:DOCKER_EXE --version
                    if ($LASTEXITCODE -ne 0) {
                        throw "Docker version check failed."
                    }

                    & $env:KUBECTL_EXE --kubeconfig $env:KUBE_CONFIG get nodes
                    if ($LASTEXITCODE -ne 0) {
                        throw "Cannot access the Kubernetes cluster."
                    }
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    & $env:DOCKER_EXE build -t $env:IMAGE_NAME .
                    if ($LASTEXITCODE -ne 0) {
                        throw "Docker image build failed."
                    }

                    Write-Host "Docker image build successful."
                '''
            }
        }

        stage('Test Docker Hub Login') {
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

                        $configDir = Join-Path $env:WORKSPACE "docker-auth-test"
                        New-Item -ItemType Directory -Force -Path $configDir | Out-Null

                        $env:DOCKER_CONFIG = $configDir

                        try {
                            $env:DH_TOKEN |
                                & $env:DOCKER_EXE login `
                                    --username $env:DH_USER `
                                    --password-stdin

                            if ($LASTEXITCODE -ne 0) {
                                throw "Docker Hub login failed. Check the Jenkins credential."
                            }

                            Write-Host "Docker Hub login using Jenkins credentials: PASS"
                        }
                        finally {
                            & $env:DOCKER_EXE logout 2>$null | Out-Null

                            Remove-Item Env:DOCKER_CONFIG -ErrorAction SilentlyContinue
                            Remove-Item -Recurse -Force $configDir `
                                -ErrorAction SilentlyContinue
                        }
                    '''
                }
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

                        $configDir = Join-Path $env:WORKSPACE "docker-push-auth"
                        New-Item -ItemType Directory -Force -Path $configDir | Out-Null

                        $env:DOCKER_CONFIG = $configDir

                        try {
                            $env:DH_TOKEN |
                                & $env:DOCKER_EXE login `
                                    --username $env:DH_USER `
                                    --password-stdin

                            if ($LASTEXITCODE -ne 0) {
                                throw "Docker Hub login failed before push."
                            }

                            & $env:DOCKER_EXE push $env:IMAGE_NAME
                            if ($LASTEXITCODE -ne 0) {
                                throw "Docker image push failed."
                            }

                            Write-Host "Docker image pushed successfully."
                        }
                        finally {
                            & $env:DOCKER_EXE logout 2>$null | Out-Null

                            Remove-Item Env:DOCKER_CONFIG -ErrorAction SilentlyContinue
                            Remove-Item -Recurse -Force $configDir `
                                -ErrorAction SilentlyContinue
                        }
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $manifest = Join-Path $env:WORKSPACE "k8s\\v1.yaml"

                    if (-not (Test-Path $manifest)) {
                        throw "Kubernetes manifest not found: $manifest"
                    }

                    & $env:KUBECTL_EXE `
                        --kubeconfig $env:KUBE_CONFIG `
                        apply -f $manifest

                    if ($LASTEXITCODE -ne 0) {
                        throw "Kubernetes deployment failed."
                    }

                    & $env:KUBECTL_EXE `
                        --kubeconfig $env:KUBE_CONFIG `
                        rollout status deployment/order-v1 `
                        --timeout=180s

                    if ($LASTEXITCODE -ne 0) {
                        throw "Deployment rollout did not complete successfully."
                    }

                    Write-Host "Kubernetes deployment successful."
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    Write-Host "Deployment status:"
                    & $env:KUBECTL_EXE `
                        --kubeconfig $env:KUBE_CONFIG `
                        get deployment order-v1

                    if ($LASTEXITCODE -ne 0) {
                        throw "Failed to retrieve deployment status."
                    }

                    Write-Host "Pods:"
                    & $env:KUBECTL_EXE `
                        --kubeconfig $env:KUBE_CONFIG `
                        get pods

                    if ($LASTEXITCODE -ne 0) {
                        throw "Failed to retrieve pod status."
                    }

                    Write-Host "Services:"
                    & $env:KUBECTL_EXE `
                        --kubeconfig $env:KUBE_CONFIG `
                        get services

                    if ($LASTEXITCODE -ne 0) {
                        throw "Failed to retrieve services."
                    }
                '''
            }
        }
    }

    post {
        success {
            echo 'V1 pipeline completed successfully: build, push, and deployment verified.'
        }

        failure {
            echo 'V1 pipeline failed. Check the first failed stage in the Jenkins console output.'
        }

        always {
            echo 'V1 pipeline execution finished.'
        }
    }
}