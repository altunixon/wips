#!/usr/bin/env bash

set -u
set -o pipefail
set -o noclobber

help_msg="Usage:\n\t$0 <file_2b_patch> <file_is_latest>\n"

file_2b_patch=${1:-}
file_be_latest=${2:-}
patch_name="$(echo -n "$file_2b_patch" | awk -F '/' '{print $NF}')"

if [ $# -le 1 ] || [ -z $file_2b_patch ] ; then
    echo -e "$help_msg"
elif [ -f $file_2b_patch ] && [ -f $file_be_latest ]; then
    patch_file="/tmp/${patch_name}.patch"
    [ -f "$patch_file" ] && rm "$patch_file"
    diff --text --ignore-blank-lines --unified $file_2b_patch $file_be_latest | tee "$patch_file"
    if [ $? -le 1 ] && [ -s $patch_file ]; then
        echo "Copy: '$patch_file' => '$(pwd)/${patch_name}.patch'"
        cp -f -v "$patch_file" ./${patch_name}.patch
        echo -n "Applying: '$patch_file' => '$file_2b_patch' "
        patch --unified --backup $file_2b_patch -i $patch_file
        [ $? -eq 0 ] && echo '[DONE]' || echo '[FAIL]'
    else
        echo "diff($?) Patch file '$patch_file' Creation failed."
    fi
else
    echo -e "$help_msg\nCheck if both file exists:\n\t2b_patch: '$file_2b_patch'\n\tlatest  : '$file_be_latest'\n"
fi
