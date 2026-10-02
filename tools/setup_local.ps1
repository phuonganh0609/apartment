$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Cannot create Python environment.' }
}
& '.venv/Scripts/python.exe' -m ensurepip --upgrade
if ($LASTEXITCODE -ne 0) { throw 'Cannot bootstrap pip.' }
& '.venv/Scripts/python.exe' -m pip install -r requirements/base.txt
if ($LASTEXITCODE -ne 0) { throw 'Cannot install requirements.' }
& '.venv/Scripts/python.exe' -X utf8 tools/scaffold_support.py
if ($LASTEXITCODE -ne 0) { throw 'Cannot prepare local configuration.' }
& '.venv/Scripts/python.exe' -X utf8 tools/vendor_bootstrap.py
if ($LASTEXITCODE -ne 0) { throw 'Cannot download Bootstrap.' }
& '.venv/Scripts/python.exe' manage.py makemigrations accounts buildings tenants contracts payments maintenance regulations
if ($LASTEXITCODE -ne 0) { throw 'Cannot generate migrations.' }
& '.venv/Scripts/python.exe' manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'Cannot migrate database.' }
& '.venv/Scripts/python.exe' -X utf8 manage.py seed_demo
if ($LASTEXITCODE -ne 0) { throw 'Cannot seed demo.' }
Write-Output 'Ready. Run: .venv/Scripts/python.exe manage.py runserver'
