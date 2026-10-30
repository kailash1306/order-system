
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    environment {
        DOCKER_EXE = 'C:\\Users\\tkail\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        KUBECTL_EXE = 'C:\\Users\\tkail\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\kubectl.exe'
        KUBE_CONFIG = 'C:\\jenkins-kube\\config'
        IMAGE_NAME = '24mis0218/order-system:v1'
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
                        throw "Docker executable not found."
                    }

                    if (-not (Test-Path $env:KUBECTL_EXE)) {
                        throw "kubectl executable not found."
                    }

                    if (-not (Test-Path $env:KUBE_CONFIG)) {
                        throw "Kubeconfig not found."
                    }

                    & $env:DOCKER_EXE --version
                    if ($LASTEXITCODE -ne 0) {
                        throw "Docker check failed."
                    }

                    & $env:KUBECTL_EXE --kubeconfig $env:KUBE_CONFIG get nodes
                    if ($LASTEXITCODE -ne 0) {
                        throw "Kubernetes connection failed."
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

        stage('Diagnose Docker Hub Credential') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    powershell '''
                        if ($env:DH_USER -cne "24mis0218") {
                            throw "Unexpected Docker Hub username."
                        }

                        if ([string]::IsNullOrWhiteSpace($env:DH_TOKEN)) {
                            throw "Docker Hub token is empty."
                        }

                        Write-Host "Credential ID resolved: PASS"
                        Write-Host "Username exact match: PASS"
                        Write-Host "Token present: PASS"
                        Write-Host "Token length: $($env:DH_TOKEN.Length)"
                    '''
                }
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
                                throw "Docker Hub login failed."
                            }

                            Write-Host "Docker Hub login: PASS"
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
                                throw "Docker Hub login before push failed."
                            }

                            & $env:DOCKER_EXE push $env:IMAGE_NAME
                            if ($LASTEXITCODE -ne 0) {
                                throw "Docker image push failed."
                            }

                            Write-Host "Docker image push successful."
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
                        throw "Manifest k8s/v1.yaml not found."
                    }

                    & $env:KUBECTL_EXE `
                        --kubeconfig $env:KUBE_CONFIG `
                        apply -f $manifest

                    if ($LASTEXITCODE -ne 0) {
                        throw "Kubernetes apply failed."
                    }

                    & $env:KUBECTL_EXE `
                        --kubeconfig $env:KUBE_CONFIG `
                        rollout status deployment/order-v1 `
                        --timeout=180s

                    if ($LASTEXITCODE -ne 0) {
                        throw "Deployment rollout failed."
                    }

                    Write-Host "Kubernetes deployment successful."
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    & $env:KUBECTL_EXE `
                        --kubeconfig $env:KUBE_CONFIG `
                        get deployment order-v1

                    if ($LASTEXITCODE -ne 0) {
                        throw "Could not verify deployment."
                    }

                    & $env:KUBECTL_EXE `
                        --kubeconfig $env:KUBE_CONFIG `
                        get pods

                    if ($LASTEXITCODE -ne 0) {
                        throw "Could not verify pods."
                    }

                    & $env:KUBECTL_EXE `
                        --kubeconfig $env:KUBE_CONFIG `
                        get services

                    if ($LASTEXITCODE -ne 0) {
                        throw "Could not verify services."
                    }

                    Write-Host "Deployment verification complete."
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: V1 image built, pushed, and deployment verified.'
        }

        failure {
            echo 'FAILURE: Check the first failed stage in Console Output.'
        }

        always {
            echo 'V1 pipeline execution finished.'
        }
    }
}
