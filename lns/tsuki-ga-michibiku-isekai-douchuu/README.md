#### Trash ads
```bash
ls -1 | xargs -I {} sed -i '/__ATA\.cmd\.push/,/\}\);/d' "{}"
```
#### TOC Generator
```powershell
$x = "./c030.md:31
./c064.md:30
./c065.md:2
./c066.md:1
./extra_22.md:1
./extra_26.md:4
./extra_47.md:9
"

$y = ($x.Split([Environment]::NewLine, [StringSplitOptions]::RemoveEmptyEntries))

$M = ($y.Length - 1)
$C = 3 # column
$D = [int]$($M / $C) # max row
$i = @() # index register
$H = "| No. | Count | Link |" + $(' | | |'  * $( $C - 1)) + "`n|" + $('----:|----:|:------------------------|' * $C)
foreach ($s in 0..$D) { # column seed
    while ($s -le $M){
        # Write-Host -NoNewline "[$s]"
        $i += $s
        $s += $D # stepsx
    }
}
Write-Host $i
Write-Host $H
foreach ($n in 0..$($i.Length - 1)) {
    $b = $i[$n]
    $L = ($y[$b].split(':'))
    $A = ($b.ToString().PadLeft(3 ,' ') + ' | ' + $L[1].PadLeft(3 ,' ') + ' | [@' + $L[0] + '](' + $L[0] + ')')
    if ($n -eq 0 -or $n % $C -ne 0) {
        if ($n -eq 0) {
            Write-Host -NoNewline "| $A | "
        } else {
            Write-Host -NoNewline "$A | "
        }
    } else {
        Write-Host -NoNewline "$A | `n| "
    }
}
```
