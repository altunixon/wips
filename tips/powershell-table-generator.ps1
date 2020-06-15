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
$R = [int]($I / $C) # rows
$H = "| No. | Cnt | Link |" + $(' | | |'  * $( $C - 1)) + "`n|" + $('----:|----:|:------------------------|' * $C) # headers

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
Write-Host $H
foreach ($R in $A) {
    $row = '| '
    foreach ($cell in $R) {
        if ($cell -ne $null) {
            $L = ($y[$cell].split(':'))
            $T = $L[1].PadLeft(3 , ' ')
            $lnk = '[@' + $L[0] + '](' + $L[0] + ')'
            $row += ($cell.ToString().PadLeft(3 , ' ') + ' | ' + $T + ' | ' + $lnk + ' | ')
        } else {
            $row += '    |     | ' + $(' ' * $lnk.Length) + ' | '
        }
    }
    Write-Host $row
}
