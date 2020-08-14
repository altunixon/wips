#!/usr/bin/env bash

set -u -e

help_msg="Usage:\n\t$0 <file_2b_patch> <file_is_latest>\n"

file_2b_patch=${1:-}
file_be_latest=${2:-}
patch_name="$(echo -n "$file_2b_patch" | awk -F '/' '{print $NF}')"

if [ -f $file_2b_patch ] && [ -f $file_be_latest ]; then
    patch_file="/tmp/${patch_name}.patch"
    [ -f "$patch_file" ] && rm "$patch_file"
    diff -u $file_2b_patch $file_be_latest | tee "$patch_file"
    echo "Copy: $patch_file => ${patch_name}.patch"
    cp -f -v "$patch_file" ./${patch_name}.patch
    [ $? -eq 0 ] && patch -u -b $file_2b_patch -i $patch_file || \
        echo "Patch file '${patch_name}.patch' Creation failed."
elif [ $# -le 1 ]; then
    echo -e "$help_msg"
else
    echo -e "$help_msg\nCheck if both file exists:\n\t2b_patch: '$file_2b_patch'\n\tlatest  : '$file_be_latest'\n"
fi
