#### Install [Pyinstaller]
```bash
pip install pyinstaller
```
#### Jenkins [Pyinstaller Pipeline]
- Optional: Set jenkins shell to /bin/bash
  - Open jenknins URI: Manage Jenkins -> Configure System -> Shell -> Shell executable. Set this to /bin/bash
- Jenkinsfile
  ```groovy
  pipeline {
      agent none 
      stages {
          stage('Test') {
              agent none
              steps { sh '/opt/py3-venv/bin/activate && py.test --junit-xml test-reports/results.xml nu-rss.py' }
              post { always {junit 'test-reports/results.xml'} }
          }
          stage('Build') { 
              agent none
              steps {
                  sh '/opt/py3-venv/bin/activate && python -m py_compile nu-rss.py' 
                  stash(name: 'pyinstaller-results', includes: '*.py*') 
              }
          }
      }
  }
  ```
#### TODO
Actually test all these stuffs, probly wont work

[Pyinstaller]: https://www.pyinstaller.org/
[Pyinstaller Pipeline]: https://www.jenkins.io/doc/tutorials/build-a-python-app-with-pyinstaller/#create-your-pipeline-project-in-jenkins
