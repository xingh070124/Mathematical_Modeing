# Disk space analysis script
$drive = Get-PSDrive C
$totalGB = [math]::Round(($drive.Used + $drive.Free) / 1GB, 2)
$freeGB = [math]::Round($drive.Free / 1GB, 2)
$usedGB = [math]::Round($drive.Used / 1GB, 2)
Write-Host "=== C Drive Summary ==="
Write-Host "Total: $totalGB GB"
Write-Host "Used: $usedGB GB"
Write-Host "Free: $freeGB GB"

$paths = @(
    @{Name="User Temp"; Path="$env:LOCALAPPDATA\Temp"},
    @{Name="Windows Temp"; Path="C:\Windows\Temp"},
    @{Name="Recycle Bin"; Path="C:\`$Recycle.Bin"},
    @{Name="Prefetch"; Path="C:\Windows\Prefetch"},
    @{Name="WinUpdate Cache"; Path="C:\Windows\SoftwareDistribution\Download"},
    @{Name="Chrome Cache"; Path="$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache"},
    @{Name="Edge Cache"; Path="$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache"}
)

Write-Host ""
Write-Host "=== Cleanable Space ==="
foreach ($item in $paths) {
    $p = $item.Path
    if (Test-Path $p) {
        try {
            $size = (Get-ChildItem -Path $p -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
            $sizeMB = if ($size) { [math]::Round($size / 1MB, 2) } else { 0 }
            Write-Host "$($item.Name): $sizeMB MB"
        } catch {
            Write-Host "$($item.Name): Access denied"
        }
    } else {
        Write-Host "$($item.Name): Not found"
    }
}

Write-Host ""
Write-Host "=== Large User Folders ==="
Get-ChildItem "C:\Users" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $size = (Get-ChildItem -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        $sizeGB = if ($size) { [math]::Round($size / 1GB, 2) } else { 0 }
        Write-Host "$($_.Name): $sizeGB GB"
    } catch {
        Write-Host "$($_.Name): Cannot calculate"
    }
}
