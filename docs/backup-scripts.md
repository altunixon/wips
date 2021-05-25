### Backup from remote dir
1. using current dir $(ls -1 ./) as list
2. check if sync_dir exists in remote dir
  - Yes: rsync --delete remote_dir/sync_dir ./sync_dir
  - No : Skip
3. Usage:
    ```bash
    sync2here <source_dir> [<backup_mode>: dryrun|keep|delete]
    ```
### Code
```bash
function sync2here() {
    backup_root=${1:-}
    backup_mode=${2:-dryrun}
    if [ ! -z $backup_root ] && [ -d $backup_root ]; then
        for x in $(ls -1 ./); do
            if [ -d "./$x" ]; then
                backup_src="${backup_root%/}${x##/}"
                if [ -d $backup_src ]; then
                    case $backup_mode in
                        keep|sync)
                            rsync "${backup_src%/}" "${x%/}"
                        ;;
                        delete)
                            rsync --delete "${backup_src%/}" "${x%/}"
                        ;;
                        *)
                            rsync --delete --dry-run "${backup_src%/}" "${x%/}"
                        ;;
                    esac
                else
                    echo "[SKIP] Src NotFound: '$backup_src'"
                fi
            else
                echo "[SKIP] Is File: './$x'"
            fi
        done
    else
        echo "[ERRO] Invalid ROOT Src: '$backup_root'"
    fi
}
```
