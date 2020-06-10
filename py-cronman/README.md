#### Crontab manager, this script itself should be run from crontab
- Resource:
    - https://gitlab.com/doctormo/python-crontab/
    - https://stackabuse.com/scheduling-jobs-with-python-crontab/
    - https://code.tutsplus.com/tutorials/managing-cron-jobs-using-python--cms-28231
  
  Crontab format
  ```cron
  ┌───────────── minute (0 - 59)
  │ ┌───────────── hour (0 - 23) 
  │ │ ┌───────────── day of month (1 - 31)
  │ │ │ ┌───────────── month (1 - 12)
  │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday; 7 is also Sunday on some obscure systems)
  │ │ │ │ │
  * * * * *  command_to_execute
  ```
- Install python-crontab
  ```bash
  pip install python-crontab
  ```
- List current cron jobs
  ```python
  from crontab import CronTab
  cron_tabs = CronTab(user=True)
  for cron_job in cron_tabs:
      print (cron_job)
  ```
- Backup current crontabs
  ```python
  from crontab import CronTab
  cron_tabs = CronTab(user=True)
  cron_tabs.write('backup_cron.tab')
  ```
- Add cronjob with **comment (Important)**
  ```python
  from crontab import CronTab
  from datetime import datetime
  import hashlib
  cron_tabs = CronTab(user=True)
  cron_command = '/opt/py3-venv/bin/python /home/${USER}/foo.py'
  # hashlib expects bytestring input, thus the .encode('utf-8')
  cron_id = hashlib.md5(cron_command.encode('utf-8')).hexdigest()
  cron_new = my_cron.new(command=cron_command, comment=cron_id)
  time_now = datetime.datetime.now()
  # you could set the run schedule like so
  cron_new.setall(
      time_now.minute + 7, 
      time_now.hour, 
      time_now.day, 
      time_now.month, 
      None
  )
  # or set it by adding individual field, default for all this is [None], which equates to [*]
  #cron_new.month.on(time_now.month)
  #cron_new.day.on(time_now.day)
  #cron_new.hour.on(time_now.hour)
  #cron_new.minute.on(time_now.minute + 7)
  
  # check new job validity
  if cron_new.is_valid():
      cron_new.enable()
  else:
      cron_new.enable(False)
  print (cron_new)
  ```
- Delete cronjob with **comment**
  ```python
  from crontab import CronTab
  cron_tabs = CronTab(user=True)
  # using the built-in fuction remove_all()
  cron_tabs.remove_all(comment=cron_id)
  # or
  for current_tab in cron_tabs:
      if current_tab.comment == cron_id:
          cron_tabs.remove(current_tab)
  ```
- Script job file (JSON)
  ```json
  {
      "work": [
          {
              "do": "add", 
              "schedule": "once",
              "command": "/usr/bin/python3 /path/to/script.py",
              "comment": null
          },
          {
              "do": "disable",
              "schedule": null,
              "command": null,
              "comment": "<md5sum>"
          },
          {
              "do": "update",
              "schedule": null,
              "command": null,
              "comment": "<md5sum>"
          },
          {
              "do": "dump",
          }
      ],
      "history": {
          "<md5sum>": "<cron_entry>"
      },
      "config": {
          "history": 25,
          "delete": false,
          "backup": true,
          "backup_file": "./cron_backup.tab",
          "dump_file": "./cron_dump.tab"
      }
  }
  ```
