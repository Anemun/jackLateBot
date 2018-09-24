pipeline {
    agent { label 'docker'} 
    environment {
        DOCKER_IMAGE = "anemun/anemrepo:jacklatebot"
        CONTAINER_NAME = "${params.containerName}"        
        BOT_TOKEN = "${params.botToken}"
        DATABASE_PATH_LOCAL = "${params.databasePath}"
        DATABASE_PATH_CONTAINER = "/usr/storage"
        DATABASE_FILENAME = "${params.databaseName}"
    }
    stages {         
        stage ('1. Build image'){
            steps {
                sh "docker build -t $DOCKER_IMAGE -f Dockerfile ."
            }
        }
        stage ('2. Push image') {
            steps {
                withDockerRegistry([credentialsId: 'dockerHubAnemun', url: ""]) {
                sh "docker push $DOCKER_IMAGE"
                }   
            }
        }
        stage ('3. Deploy image to remote server') {
            stages {
                stage ('3.1 Stop current container') {
                    steps {
                        sshagent(credentials: ['SSHroot']) {
                            withCredentials([string(credentialsId: 'ServerIP', variable: 'IP')]) {
                                sh "ssh -o StrictHostKeyChecking=no $IP docker stop $CONTAINER_NAME || true && ssh -o StrictHostKeyChecking=no $IP docker rm $CONTAINER_NAME || true"                              
                            }
                        }
                    }
                }
                stage ('3.2 Run new container') {
                    steps {
                        sshagent(credentials: ['SSHroot']) {
                            withCredentials([usernamePassword(credentialsId: 'dockerHubAnemun', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD'),
                                    string(credentialsId: 'ServerIP', variable: 'IP')]) { 
                                sh "ssh -o StrictHostKeyChecking=no $IP docker login -u $USERNAME -p $PASSWORD"
                                sh "ssh -o StrictHostKeyChecking=no $IP docker pull $DOCKER_IMAGE"
                                sh "ssh -o StrictHostKeyChecking=no $IP docker run -d --restart always -v /etc/localtime:/etc/localtime:ro -v $DATABASE_PATH_LOCAL:$DATABASE_PATH_CONTAINER --name $CONTAINER_NAME $DOCKER_IMAGE --botToken $BOT_TOKEN --databasePath $DATABASE_PATH_CONTAINER/$DATABASE_FILENAME"
                            }
                        }
                    }
                }
            }
        }
    }
}