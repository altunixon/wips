#### Patching procedure
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
- Using diff on directories
  ```bash
  diff -ruN old/ latest/ > patch_dir.diff
  ```
  The options we’re going to use with diff are: 
  - -u (unified context) option we have used earlier
  - -r (recursive) option to make diff look into any sub-directories
  - -N (new file) option.
    The -N option tells diff how to handle files in the latest directory that are not in the working directory. <br/>
    It forces diff to put instructions in the patch file so that patch creates files that are present in the latest directory but missing from the working directory.
  
  Note that we’re only providing the directory names, we’re not telling diff to look at specific files.
- Patching directory
  Cooking with gas
  ```bash
  patch --dry-run -ruN -d old/ < patch_dir.diff
  ```
  Patching a large collection of files can be a little unnerving, so we’re going to use the 
  - --dry-run option to check everything is fine before we take the plunge and commit ourselves to making the changes. <br/>
    The --dry-run option tells patch to do everything apart from actually modifying the files. <br/>
    Patch will perform all of its pre-flight checks on the files and if it encounters any problems, it reports them. <br/>
    Either way, no files are modified. <br/>
    If no problems are reported, we can repeat the command without the --dry-run option and confidently patch our files.
  - -d (directory) option tell patch which directory to work on.
  
  Note that we’re **NOT** using the -i (input) option to tell patch which patch file contains the instructions from diff. <br/>
  Instead, we’re redirecting the patch file into patch with "<". <br/>
  To genuinely apply the patches to the files we use the previous command without the --dry-run option. <br/>
  ```bash
  patch -ruN -d old/ < patch_dir.diff
  ```
  This time each line of output will start with “patching” instead of “checking” like when you're using --dry-run.
  
