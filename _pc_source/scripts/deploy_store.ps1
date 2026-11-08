<#
.SYNOPSIS
    Publica `data/publish_site/` en GitHub Pages (repo público, gh ya autenticado).

.DESCRIPTION
    Por defecto SOLO valida e imprime el plan: no crea repositorios, no hace push
    y no toca GitHub. Para ejecutar el deploy de verdad hay que pasar -Confirm.

    Flujo:
      1. Verifica que el sitio exista y que el manifest tenga 55 rutas.
      2. Con -Confirm: crea (si falta) el repo público `<owner>/<repo>` con rama
         `gh-pages`, sube el contenido y activa/actualiza GitHub Pages.
      3. Imprime la URL pública y recuerda reconstruir con --base-url para URLs
         canónicas absolutas.

.PARAMETER Confirm
    Ejecuta el deploy real. Sin este switch el script es solo lectura.

.PARAMETER Repo
    Nombre del repositorio. Por defecto `ronin-ventas-store`.

.PARAMETER BaseUrl
    Dominio final para dejarlo escrito en las instrucciones. Opcional.

.EXAMPLE
    .\scripts\deploy_store.ps1
    .\scripts\deploy_store.ps1 -Confirm -Repo ronin-ventas-store
#>
param(
    [switch]$Confirm,
    [string]$Repo = "ronin-ventas-store",
    [string]$BaseUrl = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$siteDir = Join-Path $repoRoot "data\publish_site"
$manifestPath = Join-Path $siteDir "manifest.json"

Write-Host "== Ronin Ventas OS · deploy del sitio estático =="

if (-not (Test-Path $manifestPath)) {
    throw "No existe $manifestPath. Ejecuta primero: .\.venv\Scripts\python.exe scripts\build_publish_pack.py"
}

$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
$routeCount = @($manifest.routes).Count
Write-Host "Manifest: $($manifest.skus) SKUs · $routeCount rutas · $($manifest.files) archivos"
if ($routeCount -ne 55) {
    throw "El manifest tiene $routeCount rutas; se esperaban 55. Regenera el sitio antes de publicar."
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) no está instalado. Instálalo y ejecuta 'gh auth login'."
}
$ghStatus = & gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "gh no está autenticado. Ejecuta 'gh auth login'. Detalle: $ghStatus"
}
$owner = (& gh api user --jq ".login").Trim()
if (-not $owner) { throw "No se pudo resolver el usuario autenticado de gh." }
$pagesUrl = "https://$owner.github.io/$Repo/"

if (-not $Confirm) {
    Write-Host ""
    Write-Host "MODO PLAN (solo lectura). No se ha modificado nada en GitHub."
    Write-Host "Owner detectado : $owner"
    Write-Host "Repositorio      : $owner/$Repo (público, rama gh-pages)"
    Write-Host "URL de Pages     : $pagesUrl"
    Write-Host ""
    Write-Host "Para ejecutar el deploy real:"
    Write-Host "  .\scripts\deploy_store.ps1 -Confirm -Repo $Repo"
    Write-Host ""
    Write-Host "Después del primer deploy, reconstruye con URLs absolutas y vuelve a publicar:"
    Write-Host "  .\.venv\Scripts\python.exe scripts\build_publish_pack.py --base-url $pagesUrl --verify"
    if ($BaseUrl) { Write-Host "BaseUrl indicada: $BaseUrl" }
    exit 0
}

Write-Host "Deploy confirmado en $owner/$Repo..."
$work = Join-Path $env:TEMP ("ronin_publish_site_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $work | Out-Null
Copy-Item -Path (Join-Path $siteDir "*") -Destination $work -Recurse -Force

Push-Location $work
try {
    git init -b gh-pages | Out-Null
    git add -A | Out-Null
    git -c user.name="ronin-publisher" -c user.email="example@example.invalid" `
        commit -m "Publica sitio estático ($($manifest.skus) SKUs, $routeCount rutas)" | Out-Null

    $repoExists = $true
    & gh repo view "$owner/$Repo" --json name 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { $repoExists = $false }

    if (-not $repoExists) {
        & gh repo create "$owner/$Repo" --public --description "Ronin Ventas OS · tienda estática de los 55 SKUs" | Out-Null
    }
    git remote add origin "https://github.com/$owner/$Repo.git"
    git push -u origin gh-pages --force

    $pagesBody = @{ source = @{ branch = "gh-pages"; path = "/" } } | ConvertTo-Json -Depth 4
    $pagesBody | & gh api --method POST "repos/$owner/$Repo/pages" --input - | Out-Null
    if ($LASTEXITCODE -ne 0) {
        $pagesBody | & gh api --method PUT "repos/$owner/$Repo/pages" --input - | Out-Null
    }
} finally {
    Pop-Location
    Remove-Item -Recurse -Force $work
}

Write-Host ""
Write-Host "Publicado. GitHub Pages puede tardar 1-2 minutos en propagar."
Write-Host "URL: $pagesUrl"
Write-Host "Siguiente paso: reconstruir con --base-url $pagesUrl y repetir este script con -Confirm."
