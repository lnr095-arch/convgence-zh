# apply_extra.ps1 - translates the strings apocalyptic_translatorZ cannot reach:
#   (1) placeholder / legacy note titles baked into level* scene files
#   (2) C# string literals inside il2cpp global-metadata.dat
# Pure ASCII source; all text comes from the UTF-8 JSON files in .\data
# Usage: powershell -ExecutionPolicy Bypass -File apply_extra.ps1 [-Mode apply|restore|check]
param([string]$Mode = "apply")
$ErrorActionPreference = 'Stop'

$tools = $PSScriptRoot
$game  = Split-Path -Parent $tools
$data  = Join-Path $tools 'data'
if (-not (Test-Path (Join-Path $game 'CONVRGENCE.exe'))) {
    Write-Host "[ERR] CONVRGENCE.exe not found next to this package." -ForegroundColor Red
    Write-Host "      Copy the folder CONTENTS into the game root (the dir holding"
    Write-Host "      CONVRGENCE.exe), then run again."
    exit 2
}
$U8 = New-Object System.Text.UTF8Encoding($false)
function EqBytes($a, $b) {
    if ($null -eq $a -or $null -eq $b) { return $false }
    if ($a.Length -ne $b.Length) { return $false }
    for ($i = 0; $i -lt $a.Length; $i++) { if ($a[$i] -ne $b[$i]) { return $false } }
    return $true
}
function PadBytes($body, $len, $fill) {
    $o = New-Object byte[] $len
    for ($i = 0; $i -lt $len; $i++) { $o[$i] = $fill }
    [Array]::Copy($body, 0, $o, 0, $body.Length)
    return ,$o
}

# ---------------- 1. scene-file placeholders ----------------
$ph = [System.IO.File]::ReadAllText((Join-Path $data 'placeholders.json'), [System.Text.Encoding]::UTF8) | ConvertFrom-Json
$ph = @($ph)
$dir = Join-Path $game 'CONVRGENCE_Data'
$st = @{ done = 0; already = 0; checked = 0; refuse = 0 }
foreach ($g in ($ph | Group-Object file)) {
    $p = Join-Path $dir $g.Name
    if (-not (Test-Path $p)) { Write-Host "[ERR] missing $p" -ForegroundColor Red; $st.refuse += $g.Count; continue }
    $fs = [System.IO.File]::Open($p, 'Open', 'ReadWrite')
    try {
        foreach ($e in $g.Group) {
            $src = if ($Mode -eq 'restore') { $e.zh } else { $e.ru }
            $dst = if ($Mode -eq 'restore') { $e.ru } else { $e.zh }
            $want = PadBytes ($U8.GetBytes($src)) $e.len 0x20
            $new  = PadBytes ($U8.GetBytes($dst)) $e.len 0x20
            $buf  = New-Object byte[] $e.len
            $pref = New-Object byte[] 4
            $fs.Position = $e.off - 4
            [void]$fs.Read($pref, 0, 4)
            if ([BitConverter]::ToInt32($pref, 0) -ne $e.len) {
                Write-Host "[SKIP] $($g.Name) @$($e.off): int32 length prefix mismatch (game updated?)" -ForegroundColor Yellow
                $st.refuse++; continue
            }
            $fs.Position = $e.off
            if ($fs.Read($buf, 0, $e.len) -ne $e.len) { $st.refuse++; continue }
            if (EqBytes $buf $new) { $st.already++; continue }
            if (-not (EqBytes $buf $want)) {
                Write-Host "[SKIP] $($g.Name) @$($e.off): bytes differ from the expected source" -ForegroundColor Yellow
                $st.refuse++; continue
            }
            if ($Mode -eq 'check') { $st.checked++; continue }
            $fs.Position = $e.off
            $fs.Write($new, 0, $new.Length)
            $st.done++
        }
    } finally { $fs.Dispose() }
}
Write-Host ("scene placeholders : written={0} already={1} checked={2} refused={3} (of {4})" -f `
    $st.done, $st.already, $st.checked, $st.refuse, $ph.Count)

# ---------------- 2. il2cpp string literals ----------------
$mpath = Join-Path $dir 'il2cpp_data\Metadata\global-metadata.dat'
if (-not (Test-Path $mpath)) { Write-Host "[ERR] no $mpath" -ForegroundColor Red; exit 3 }
$bak = Join-Path $tools 'global-metadata.dat.orig'
if (-not (Test-Path $bak)) {
    Copy-Item $mpath $bak
    Write-Host "[ok] pristine metadata copy saved as tools\global-metadata.dat.orig" -ForegroundColor DarkGray
}
$mt = [System.IO.File]::ReadAllText((Join-Path $data 'meta_literals.json'), [System.Text.Encoding]::UTF8) | ConvertFrom-Json
$mt = @($mt)
$d = [System.IO.File]::ReadAllBytes($mpath)
$slOff = [BitConverter]::ToInt32($d, 8); $slSz = [BitConverter]::ToInt32($d, 12)
$sdOff = [BitConverter]::ToInt32($d, 16)
$n = [int]($slSz / 8)
$regP = New-Object 'int[]' $n
$regL = New-Object 'int[]' $n
for ($i = 0; $i -lt $n; $i++) {
    $regL[$i] = [int][BitConverter]::ToUInt32($d, $slOff + $i * 8)
    $regP[$i] = $sdOff + [int][BitConverter]::ToUInt32($d, $slOff + $i * 8 + 4)
}
# Match by TABLE INDEX and verify the text there, never by text alone: the game keeps
# English twins of these enum names right next to them (РШ-12 / RSh-12), so a text
# lookup would rewrite the wrong literal on restore.
$hits = @(); $m = @{ done = 0; refuse = 0; already = 0 }
foreach ($e in $mt) {
    $i = [int]$e.idx
    if ($i -lt 0 -or $i -ge $n) { Write-Host "[SKIP] table index $i out of range" -ForegroundColor Yellow; $m.refuse++; continue }
    $ln = $regL[$i]; $p = $regP[$i]
    if ($ln -le 0 -or $p + $ln -gt $d.Length) { $m.refuse++; continue }
    $txt = $U8.GetString($d, $p, $ln)
    $dst = if ($Mode -eq 'restore') { $e.ru } else { $e.zh }
    $exp = if ($Mode -eq 'restore') { $e.zh } else { $e.ru }
    if ($txt -eq $dst) { $m.already++; continue }
    if ($txt -ne $exp) {
        Write-Host "[SKIP] literal #$i text differs from the table (game updated?)" -ForegroundColor Yellow
        $m.refuse++; continue
    }
    $hits += [pscustomobject]@{ idx = $i; pos = $p; len = $ln; to = $dst; cap = [int]$e.maxlen }
}
$isHit = @{}
foreach ($h in $hits) { $isHit[[int]$h.idx] = $true }
foreach ($h in $hits) {
    $body = $U8.GetBytes($h.to)
    if ($body.Length -gt $h.cap) {
        Write-Host ("[SKIP] literal #{0}: {1}B > reserved {2}B" -f $h.idx, $body.Length, $h.cap) -ForegroundColor Yellow
        $m.refuse++; continue
    }
    $clash = $false
    for ($j = 0; $j -lt $n; $j++) {
        if ($j -eq $h.idx -or $regL[$j] -le 0) { continue }
        # il2cpp dedupes identical literals: several indices may share one data region.
        # That is fine as long as both sides want the same replacement text.
        if ($isHit.ContainsKey($j) -and $regP[$j] -eq $h.pos) { continue }
        if ($regP[$j] -lt ($h.pos + $h.cap) -and $h.pos -lt ($regP[$j] + $regL[$j])) { $clash = $true; break }
    }
    if ($clash) { Write-Host "[SKIP] literal #$($h.idx): data region overlaps another literal" -ForegroundColor Yellow; $m.refuse++; continue }
    if ($Mode -eq 'check') { $m.done++; continue }
    for ($k = 0; $k -lt $h.cap; $k++) { $d[$h.pos + $k] = 0 }
    [Array]::Copy($body, 0, $d, $h.pos, $body.Length)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$body.Length), 0, $d, $slOff + $h.idx * 8, 4)
    $m.done++
}
Write-Host ("metadata literals  : writable={0} already={1} refused={2} (table={3})" -f $m.done, $m.already, $m.refuse, $mt.Count)
if ($Mode -ne 'check' -and $m.done -gt 0) {
    [System.IO.File]::WriteAllBytes($mpath, $d)
    $chk = [System.IO.File]::ReadAllBytes($mpath)
    $bad = 0
    foreach ($h in $hits) {
        $i = $h.idx
        $l2 = [int][BitConverter]::ToUInt32($chk, $slOff + $i * 8)
        $d2 = [int][BitConverter]::ToUInt32($chk, $slOff + $i * 8 + 4)
        if ($U8.GetString($chk, $sdOff + $d2, $l2) -ne $h.to) { $bad++ }
    }
    if ($bad -gt 0) {
        Copy-Item $bak $mpath -Force
        Write-Host "[!!] read-back mismatches=$bad  -> rolled back from tools\global-metadata.dat.orig" -ForegroundColor Red
        exit 4
    }
    Write-Host "[ok] metadata written, read-back verified" -ForegroundColor Green
} elseif ($Mode -eq 'check') {
    Write-Host "[check] nothing written" -ForegroundColor DarkGray
} else {
    Write-Host "[--] metadata untouched" -ForegroundColor DarkGray
}
Write-Host ""
Write-Host ("DONE  mode={0}  game={1}" -f $Mode, $game)
