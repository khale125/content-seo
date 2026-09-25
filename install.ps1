# Cai dat content-seo tren Windows.
#
#   powershell -ExecutionPolicy Bypass -File install.ps1
#
# Script nay KHONG cai goi Python nao, vi du an chi dung thu vien chuan. Viec cua
# no la: kiem phien ban, dung .env, do Node/Lark CLI, roi chay preflight.

Set-Location -Path $PSScriptRoot

$py = $null
foreach ($c in @("python", "python3", "py")) {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if ($null -ne $cmd) { $py = $cmd.Source; break }
}
if ($null -eq $py) {
    Write-Host "[LOI] Khong tim thay Python. Cai Python 3.10 tro len roi chay lai."
    exit 1
}

$ver = & $py -c "import sys; print('%d.%d' % sys.version_info[:2])"
$ok = & $py -c "import sys; print(1 if sys.version_info[:2] >= (3,10) else 0)"
if ($ok -ne "1") {
    Write-Host "[LOI] Python $ver qua cu, can 3.10 tro len."
    exit 1
}
Write-Host "[OK] Python $ver ($py)"

# .env: tao tu ban mau, khong ghi de neu da co
if (Test-Path ".env") {
    Write-Host "[OK] .env da co, giu nguyen"
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "[OK] Da tao .env tu .env.example -- hay dien MBWP_USER va MBWP_APP_PASSWORD"
}

# Node + Lark CLI: canh bao thoi, vi bo kiem chay duoc ma khong can chung
$node = Get-Command node -ErrorAction SilentlyContinue
if ($null -ne $node) {
    $nv = & node --version
    Write-Host "[OK] node $nv"
    # Do bang chinh ham cua du an: cai bang pnpm thi `lark` khong nam tren PATH
    # nhung du an van goi duoc qua node + run.js.
    & $py -c "import sys; sys.path.insert(0,'scripts/lark'); import lark_cli; sys.exit(0 if lark_cli._discover_cli() else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] @larksuite/cli da cai"
    } else {
        Write-Host "[CANH BAO] Chua co @larksuite/cli. Phan dong bo Lark se khong chay."
        Write-Host "           Cai: npm install -g @larksuite/cli   roi: lark auth login"
    }
} else {
    Write-Host "[CANH BAO] Chua co Node.js. Phan dong bo Lark se khong chay."
}

Write-Host ""
Write-Host "--- Kiem may ---"
$env:PYTHONIOENCODING = "utf-8"
& $py "scripts/preflight.py"
$code = $LASTEXITCODE

Write-Host ""
if ($code -eq 0) {
    Write-Host "Cai dat xong. Ba viec tiep theo:"
    Write-Host ""
    Write-Host "  1. Dien .env      : MBWP_USER va MBWP_APP_PASSWORD"
    Write-Host "                      (WP Admin -> Users -> Profile -> Application Passwords)"
    Write-Host "  2. Dang nhap Lark : lark auth login"
    Write-Host "  3. Mo Claude Code trong thu muc nay roi doc CLAUDE.md"
    Write-Host ""
    Write-Host "Kiem lai bat ky luc nao:  python scripts/preflight.py --all"
} else {
    Write-Host "Preflight con muc chua dat -- sua theo danh sach o tren roi chay lai:"
    Write-Host "  python scripts/preflight.py"
}
exit $code
