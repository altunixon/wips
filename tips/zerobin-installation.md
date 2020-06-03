
#### [Install ZeroBin]()
```bash
pip install zerobin
zerobin --host 0.0.0.0 --port 8000 --compressed-static # as admin
```
*Note: If you installed zerobin in a virtualenv, you need to set the command to run directly from it*
```bash
/path/to/virtualenv/bin/zerobin --port 8000 --compressed-static
```
#### [Running With Supervisord](https://0bin.readthedocs.io/en/latest/en/using_supervisor.html)
- Installation
  ```bash
  sudo apt-get install supervisor
  ```
- Create a configuration file named supervisor.ini
  ```ini
  [unix_http_server]
  file=/tmp/supervisor.sock;

  [supervisorctl]
  serverurl=unix:///tmp/supervisor.sock;

  [rpcinterface:supervisor]
  supervisor.rpcinterface_factory=supervisor.rpcinterface:make_main_rpcinterface

  [supervisord]
  logfile=/tmp/zerobin.log
  logfile_maxbytes=50MB
  logfile_backups=2
  loglevel=trace
  pidfile=/tmp/supervisord.pid
  nodaemon=false
  minfds=1024
  minprocs=200
  user=zerobin

  [program:zerobin]
  command=/path/to/zerobin/zerobin.py --port 8000 --compressed-static
  directory=/path/to/zerobin/
  environment=PYTHONPATH='/path/to/zerobin/'
  user=zerobin
  autostart=true
  autorestart=true
  ```
  The 4 first entries are just boiler plate to get you started, you can copy them verbatim. </br>
  The last one define one (you can have many) process supervisor should manage. </br>
- The first time you run supervisor, pass it the configuration file:
  ```bash
  supervisord -c ./supervisor.ini
  ```
- Then you can manage the process by running:
  ```bash
  supervisorctl -c ./supervisor.ini
  ```
