$ErrorActionPreference = "Stop"

$python = (python -c "import sys; print(sys.executable)").Trim()
$stockCheck = Join-Path $PSScriptRoot "enforce_elecrow_google_ads_stock.py"
$taskName = "Elecrow Google Ads Stock Gate"

if (-not (Test-Path -LiteralPath $stockCheck)) {
    throw "Missing stock enforcement script: $stockCheck"
}

$action = New-ScheduledTaskAction -Execute $python -Argument "`"$stockCheck`""
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date).AddMinutes(5) `
    -RepetitionInterval (New-TimeSpan -Hours 1)
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Pause Google Ads ad groups when Elecrow product pages are unavailable." `
    -Force | Out-Null

Write-Output "Registered hourly task: $taskName"
