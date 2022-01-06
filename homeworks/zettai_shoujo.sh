#sed -i 's/^\.\///g; s/\///g' z.txt ze.txt
IFS=$'\r\n'
for x in $(cat ze.txt); do
    echo "FOR: ${x}"
    y=$(echo "$x" | sed -nE 's/^\(([^\)]*)\).*/\1/p');
    if [ -z "$y" ]; then
        echo "MANUAL: $x"
        echo -n "Manual Search Term: "
        read y
    fi
    
    a=($(grep -F "$y" z.txt))
    a+=('NULL')
    if [ ${#a[@]} -gt 2 ]; then
        selected=()
        PS3='Select the one shall be moved first: '
        select k in "${a[@]}" ; do
            for reply in $REPLY ; do
                selected+=(${a[reply - 1]})
                PS3='Now select the empty one: '
            done
            [ ${#selected[@]} -eq 1 ] && break
        done
        o=${selected[0]}
    else
        o="${a[0]}"
    fi
    
    z=($(grep -F "$o" y.txt | sed -E 's/^INSERT INTO .(.*). VALUES .*/\1/p' | uniq))
    echo "${z[@]}"
    if [ ${#z[@]} -gt 1 ]; then
        gid="${z[1]}"
    else
        echo "${z[@]}"
        echo -n "Manual INPUT: "
        read gid
    fi
    
    [ "$o" == 'NULL' ] || echo "mv --no-clobber -v -v --no-clobber '${o}' '${x%%/} [${gid}]' && mv --no-clobber -v '${x}' _empty/" | tee -a ze-fix.txt
    
done
