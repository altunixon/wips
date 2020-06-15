#### Trash ads
```bash
ls -1 | xargs -I {} sed -i '/__ATA\.cmd\.push/,/\}\);/d' "{}"
```
#### TOC Generator
```powershell
$x="./c018.md:2
./c048.md:1
./c065.md:1
./c293.md:1
./c297.md:2
./c302.md:2
./extra_48.md:1"

$y = ($x.Split([Environment]::NewLine, [StringSplitOptions]::RemoveEmptyEntries))

$I = $($y.Length - 1)
$C = 3 # column
$R = [int]($I / $C)
$H = "| No. | Cnt | Link    |" + $(' =3= | =3= | ===7=== |'  * $( $C - 1)) + "`n|" + $('----:|----:|:--------|' * $C)

# split array horizontally
$A = @()
foreach ($x in 0..($R - 1)) {
    $M = @()
    $z = $x
    # while ($z -le $I) { # overflow right
    while ($M.Length -lt $C) { # no overflow, excess ($I % $C) != 0 will be clipped
        $M += $z
        $z += $R
    }
    $A += ,$M
}

# patch clipped ($I % $C) portion
$B = $($A.Length * $C) - 1
if ($I -gt $B) {
    $P = @(($B + 1)..$I)
    $A += ,@( @(foreach ($r in 1..($C - $P.Length)) {$null}) + $P ) # padding right
}

# draw table
$D = $H + "`n"
# Write-Host $H
$refer = "`n`n`n"
foreach ($R in $A) {
    $row = '| '
    foreach ($cell in $R) {
        if ($cell -ne $null) {
            $L = ($y[$cell].split(':'))
            $T = $L[1].PadLeft(3 , ' ')
            $lnk = '[@' + $L[0].split('./')[2] + ']'
            $refer += $lnk + ': ' + $L[0] + "`n"
            $row += ($cell.ToString().PadLeft(3 , ' ') + ' | ' + $T + ' | ' + $lnk + ' | ')
        } else {
            $row += '    |     | ' + $(' ' * $lnk.Length) + ' | '
        }
    }
    $D += $row + "`n"
}
$D += $refer
Write-Host $D
```
