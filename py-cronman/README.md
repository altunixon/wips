#### Crontab manager, this script itself should be run from crontab
- Resource:
    - https://stackabuse.com/scheduling-jobs-with-python-crontab/
    - https://code.tutsplus.com/tutorials/managing-cron-jobs-using-python--cms-28231
- Install python-crontab
  ```bash
  pip install python-crontab
  ```
- List current cron jobs
  ```python
  from crontab import CronTab
  cron_tabs = CronTab(user='user')
  for cron_job in cron_tabs:
      print (cron_job)
  ```
- Add cronjob with **comment (Important)**
  ```python
  from crontab import CronTab
  from datetime import datetime
  cron_tabs = CronTab(user='user')
  cron_new = my_cron.new(command='/opt/py3-venv/bin/python /home/${USER}/foo.py', comment='barz')
  cron_schedule = datetime.datetime.now() + datetime.timedelta(minutes=7)
  ```
