$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPath = Join-Path $projectDir "DirectPrintTest.py"
$startupDir = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startupDir "Kuittitulostin.lnk"

$pythonw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
if (-not $pythonw) {
    $pythonw = (Get-Command python.exe -ErrorAction Stop).Source
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = '"' + $scriptPath + '"'
$shortcut.WorkingDirectory = $projectDir
$shortcut.Description = "Kuittitulostin"
$shortcut.Save()

Write-Host "Startup shortcut created:"
Write-Host $shortcutPath
