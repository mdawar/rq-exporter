pipeline {
  agent {
    kubernetes {
      inheritFrom('kaniko')
      defaultContainer('kaniko')
    }
  }

  stages {
    stage('Build') {
      when { tag pattern: "^v*", comparator: "REGEXP" }
      steps {
        sh "/kaniko/executor --context $WORKSPACE --destination 132646897468.dkr.ecr.eu-west-1.amazonaws.com/cicd/rq-exporter:$TAG_NAME"
      }
    }
  }
}
