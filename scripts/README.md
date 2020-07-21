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
