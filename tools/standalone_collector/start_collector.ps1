# -*- coding: utf-8 -*-
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$Host.UI.RawUI.WindowTitle = "明日方舟干员仓库数据采集工具 (PowerShell)"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "        明日方舟干员仓库一键采集启动器 (PowerShell 启动版)" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$collectorPy = Join-Path $scriptDir "collector.py"

$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py -3"
}

if ($pythonCmd) {
    Write-Host "[检测] 发现 Python 执行器: " -NoNewline -ForegroundColor Green
    Write-Host $pythonCmd -ForegroundColor Yellow
    Write-Host "[启动] 正在以 UTF-8 模式运行采集脚本..." -ForegroundColor Gray
    Write-Host ""
    if ($pythonCmd -eq "python") {
        & python -X utf8 $collectorPy @args
    } else {
        & py -3 -X utf8 $collectorPy @args
    }
} else {
    Write-Host "[错误] 系统中未找到 Python 环境！" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先从 https://www.python.org/downloads/ 下载并安装 Python (安装时务必勾选 Add to PATH)。" -ForegroundColor Yellow
    Read-Host "按 Enter 键退出..."
}
