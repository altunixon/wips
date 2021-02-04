### Usage
```bash
trem-history add <path_dest> bolze
# > trem <path_dest> <cwd>/*bolze*
# > echo bolze|<path_dest> >> mapfile.txt
trem-history ls bolze
# > echo "trem /media/nfs/mounts-hub/bolze <cwd>/*bolze*"
trem-history replay bolze
# > trem /media/nfs/mounts-hub/bolze <cwd>/*bolze*
# > rm *bolze*
trem-history autoplay <path|cwd>
# > trem /media/nfs/mounts-hub/bolze <path|cwd>/*bolze*
# > trem /media/nfs/mounts-hub/bolze <path|cwd>/*rit*
# > trem /media/nfs/mounts-hub/z-ton <path|cwd>/*SHIS*
```

### MapFile format
```csv
bolze|/media/nfs/mounts-hub/bolze
SHIS|/media/nfs/mounts-hub/z-ton
```

### Search map file
-m 1, --max-count, stop reading a file after 1 matching line
```bash
$map_line=$(grep -m 1 "bolze" mapfile.txt)
$map_key=$(echo "$map_line" | awk -F '|' '{print $1}')
$map_path=$(echo "$map_line" | awk -F '|' '{print $2}')
```
