$w2008 = Import-Csv -LiteralPath 2008.csv
$w2016 = Import-Csv -LiteralPath 2016.csv

$wmerge = @($w2008 | Select-Object -ExpandProperty service)
foreach ( $x in ($w2016 | Select-Object -ExpandProperty service) ) {
    if ( ! $wmerge.Contains($x) ) {
        $wmerge += $x
    }
}
$wy = @($wmerge | Sort-Object -Descending)

$d2008 = @($w2008[0] | Get-member | Where-Object {$_.MemberType -eq "NoteProperty" -and $_.Name.Contains('DCS')} | Select-Object -ExpandProperty Name)
$d2016 = @($w2016[0] | Get-member | Where-Object {$_.MemberType -eq "NoteProperty" -and $_.Name.Contains('DCS')} | Select-Object -ExpandProperty Name)

$ws = @()
foreach ( $y in $wy ) {
    $y
    $whash = [ordered]@{}
    $whash.add('ServiceName', $y)
    $whash.add('win2008', 'なし')
    $whash.add('win2016', 'なし')
    $chck_2008 = $($w2008 | Where-Object {$_.service -eq $y})
    $chck_2016 = $($w2016 | Where-Object {$_.service -eq $y})
    #$chck_2008
    if ($chck_2008) {
        $whash['win2008'] = '〇'
        foreach ( $z1 in $d2008 ) { $whash.add($z1, $chck_2008.$z1) }
    }
    else {
        foreach ( $z1 in $d2008 ) { $whash.add($z1, 'なし') }
    }
    #$chck_2016
    if ($chck_2016) { 
        $whash['win2016'] = '〇'
        foreach ( $z2 in $d2016 ) { $whash.add($z2, $chck_2016.$z2) }
    }
    else {
        foreach ( $z2 in $d2016 ) { $whash.add($z2, 'なし') }
    }

    $whash
    Write-Host '============================================'
    $ws += $(New-Object PSObject -Property $whash)
}
$ws | Sort-Object -Property ServiceName | Export-Csv -NoTypeInformation -Encoding UTF8 -Path merge.csv