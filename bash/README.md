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
```
