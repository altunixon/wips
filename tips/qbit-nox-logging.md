#### Default log location
```bash
cd ~/.local/share/data/qBittorrent/
```
#### Config
If it's not there you'll need to add/change some lines in your config
```bash
vim ~/.config/qBittorrent/qBittorrent.conf
```
```ini
[Application]
FileLogger\Enabled=true
FileLogger\Age=6
FileLogger\DeleteOld=true
FileLogger\Backup=true
FileLogger\AgeType=1
FileLogger\Path=path/to/log/folder/of/your/choice
FileLogger\MaxSize=10
```
- Explanation:
  - FileLogger\Backup= backup the log file when it becomes bigger than 
    - FileLogger\MaxSize= x MB
  - FileLogger\DeleteOld= delete the backup logs after
    - FileLogger\Age= 6 
    - FileLogger\AgeType= x where x can be 0=days, 1=months, 2=years
