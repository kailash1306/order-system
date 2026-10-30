
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        DOCKER_EXE = 'C:\\Users\\tkail\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        KUBECTL_EXE = 'C:\\Users\\tkail\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\kubectl.exe'
        KUBECONFIG = 'C:\\jenkins-kube\\config'

        IMAGE_NAME = '24mis0218/order-system:v1'
        DEPLOYMENT_NAME = 'order-v1'
        CONTAINER_NAME = 'order-system'
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

                    if (-not (Test-Path $env:KUBECONFIG)) {
                        throw "Kubeconfig not found: $env:KUBECONFIG"
                    }

                    & $env:DOCKER_EXE --version
                    if ($LASTEXITCODE -ne 0) {
                        throw "Docker is not working."
                    }

                    & $env:KUBECTL_EXE --kubeconfig $env:KUBECONFIG get nodes
                    if ($LASTEXITCODE -ne 0) {
                        throw "Cannot connect to Kubernetes."
                    }
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    if (-not (Test-Path "Dockerfile")) {
                        throw "Dockerfile is missing from the repository."
                    }

                    & $env:DOCKER_EXE build -t $env:IMAGE_NAME .
                    if ($LASTEXITCODE -ne 0) {
                        throw "Docker image build failed."
                    }

                    Write-Host "Docker image build successful."
                    & $env:DOCKER_EXE image inspect $env:IMAGE_NAME
                    if ($LASTEXITCODE -ne 0) {
                        throw "Built image could not be inspected."
                    }
                '''
            }
        }

        stage('Docker Hub Login and Push') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'docker-cred-kailash',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    powershell '''
                        $ErrorActionPreference = "Stop"

                        $docker = $env:DOCKER_EXE
                        $username = $env:DH_USER
                        $token = $env:DH_TOKEN

                        if ($username -ne "24mis0218") {
                            throw "Docker Hub username does not match the expected account."
                        }

                        if ([string]::IsNullOrWhiteSpace($token)) {
                            throw "Docker Hub token is empty. Check Jenkins credentials."
                        }

                        # Use a clean, isolated Docker configuration.
                        $configDir = Join-Path $env:WORKSPACE "docker-auth-push"

                        if (Test-Path $configDir) {
                            Remove-Item -Recurse -Force $configDir
                        }

                        New-Item -ItemType Directory -Path $configDir | Out-Null
                        $env:DOCKER_CONFIG = $configDir

                        try {
                            # Send the PAT through stdin, never as a command-line argument.
                            $startInfo = New-Object System.Diagnostics.ProcessStartInfo
                            $startInfo.FileName = $docker
                            $startInfo.Arguments = "login --username $username --password-stdin"
                            $startInfo.UseShellExecute = $false
                            $startInfo.CreateNoWindow = $true
                            $startInfo.RedirectStandardInput = $true
                            $startInfo.RedirectStandardOutput = $true
                            $startInfo.RedirectStandardError = $true

                            $process = New-Object System.Diagnostics.Process
                            $process.StartInfo = $startInfo

                            [void]$process.Start()

                            $stdoutTask = $process.StandardOutput.ReadToEndAsync()
                            $stderrTask = $process.StandardError.ReadToEndAsync()

                            $process.StandardInput.WriteLine($token)
                            $process.StandardInput.Close()

                            $process.WaitForExit()

                            $stdout = $stdoutTask.Result
                            $stderr = $stderrTask.Result
                            $loginCode = $process.ExitCode

                            $process.Dispose()

                            if ($loginCode -ne 0) {
                                Write-Host "Docker Hub login failed. Exit code: $loginCode"

                                if (-not [string]::IsNullOrWhiteSpace($stdout)) {
                                    Write-Host $stdout
                                }

                                if (-not [string]::IsNullOrWhiteSpace($stderr)) {
                                    Write-Host $stderr
                                }

                                throw "Docker Hub authentication failed. Verify the PAT and Jenkins credential."
                            }

                            Write-Host "Docker Hub login successful."

                            # Push only after successful authentication.
                            & $docker push $env:IMAGE_NAME

                            if ($LASTEXITCODE -ne 0) {
                                throw "Docker image push failed."
                            }

                            Write-Host "Docker image pushed successfully."
                        }
                        finally {
                            # Remove temporary authentication data.
                            & $docker logout 2>$null | Out-Null

                            Remove-Item Env:DOCKER_CONFIG -ErrorAction SilentlyContinue

                            if (Test-Path $configDir) {
                                Remove-Item -Recurse -Force $configDir
                            }
                        }
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    if (-not (Test-Path "k8s\\v1.yaml")) {
                        throw "Kubernetes manifest k8s\\v1.yaml was not found."
                    }

                    & $env:KUBECTL_EXE --kubeconfig $env:KUBECONFIG apply -f "k8s\\v1.yaml"

                    if ($LASTEXITCODE -ne 0) {
                        throw "Kubernetes deployment apply failed."
                    }

                    & $env:KUBECTL_EXE --kubeconfig $env:KUBECONFIG rollout status "deployment/$env:DEPLOYMENT_NAME" --timeout=180s

                    if ($LASTEXITCODE -ne 0) {
                        throw "Deployment rollout failed."
                    }
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    & $env:KUBECTL_EXE --kubeconfig $env:KUBECONFIG get deployment $env:DEPLOYMENT_NAME
                    if ($LASTEXITCODE -ne 0) {
                        throw "Could not verify deployment."
                    }

                    & $env:KUBECTL_EXE --kubeconfig $env:KUBECONFIG get pods -o wide
                    if ($LASTEXITCODE -ne 0) {
                        throw "Could not list Kubernetes pods."
                    }

                    & $env:KUBECTL_EXE --kubeconfig $env:KUBECONFIG get services
                    if ($LASTEXITCODE -ne 0) {
                        throw "Could not list Kubernetes services."
                    }

                    Write-Host "V1 deployment verification completed."
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: V1 pipeline completed, image pushed, and Kubernetes deployment verified.'
        }

        failure {
            echo 'FAILURE: Open Console Output and inspect the first failed stage.'
        }

        always {
            echo 'V1 pipeline execution finished.'
        }
    }
}
