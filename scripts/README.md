### Windows Show Product Key
```cmd
wmic path softwarelicensingservice get OA3xOriginalProductKey
powershell "(Get-WmiObject -query 'select * from SoftwareLicensingService').OA3xOriginalProductKey"
```

### Patching
- Create a diff patch file
  ```bash
  diff -u $file_2b_patched $file_bleeding_edge > patch_file.diff
  ```
  The -u (unified) option tells diff to also list some of the un-modified text lines from before and after each of the changed sections. <br/>
  These lines are called context lines. <br/>
  They help the patch command locate precisely where a change must be made in the original file.
- Patching file
  ```bash
  patch -u $file_2b_patched -i patch_file.diff
  ```
  The -u (unified) option lets patch know that the patch file contains unified context lines. <br/>
  In other words, we used the -u option with diff, so we use the -u option with patch. <br/>
  The -i (input) option tells patch the name of the patch file to use. <br/>
  If all goes well, there’s a single line of output telling you patch is patching the file.
- Extra
  Apply patch with backup
  ```bash
  patch -u -b $file_2b_patched -i patch_file.diff
  ```
  We can instruct patch to make a backup copy of patched files before they are changed by using the -b (backup) option. <br/>
  The file is patched as before, with no visible difference in the output. <br/>
  However, if you look into the working folder, you’ll see that file called "${file_2b_patched}.orig" has been created.

### Bashrc
```bash
alias hg="history | grep -i"
alias ht="history | grep 'trem' | grep -i"

function ext-swap() {
    IFS=$'\r\n'
    for x_in in $(ls ./*.${1}); do
        x_out=$(echo "$x_in" | sed -E "s/(.*)\.${1}/\1\.${2}/")
        mv -v --no-clobber "$x_in" "$x_out"
    done
    unset IFS
}

function auto-xarg() {
    IFS=$'\r\n'
    cmd_out=${1:-}
    cmd_in=${2:-}
    if [ -z $cmd_in ] || [ -z $cmd_out ]; then
        echo -e "Usage:\n\tauto-xarg '<cmd_out>' '<cmd_in>'\nNot: auto-xarg '$cmd_out' '$cmd_in'"
    else
        for x_arg in $(eval "$cmd_in"); do
            eval "$cmd_out" "$x_arg"
        done
    fi
    unset IFS
}
```
