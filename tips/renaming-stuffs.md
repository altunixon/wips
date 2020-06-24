### Rename the kets
```bash
find ./ -type d -maxdepth 1 -regextype sed -regex '^\(C[0-9]{1,2}\).*'
find ./ -type d -maxdepth 1 -regextype sed -regex '^\(C[0-9]{1,2}\).*' | head -n 5 | sed -n '/^\.\/\((C[0-9]{1,2})\)/\1/p')
```
```bash
IFS=$'\r\n'
CUR=$(pwd)
for X in $(find ./ -type d -maxdepth 1 -regextype sed -regex '^\(C[0-9]{1,2}\).*'); do
K=$(echo "$X" | sed -n '/^\.\/\((C[0-9]{1,2})\)/\1/p')
cd "$X" && rnpa -p "${X## }" -s "_" /*
cd "$CUR"
done
```
### img no-clobber
```bash
for Y in ${@}; do
N=${Y##*/}
case $N in
    "[A-Za-z]"*"-[0-9]"*"[0-9]-"*)
    
    ;;
    "[0-9]"*)
    
    ;;
    "[a-z]"*" [0-9]"*"_"*)
    
    ;;
    *)
    
    ;;
esac
done
```
