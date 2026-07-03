<#
.SYNOPSIS
  Prepare l'environnement de build sur un PC Windows neuf (droits admin conseilles) et
  construit le bundle lancable TP-C-perso a partir d'un clone du depot.

.DESCRIPTION
  Etapes, toutes idempotentes (ce qui est deja present est reutilise) :
    1. Python 3.12       -> winget si absent
    2. Paquets pip       -> pyinstaller, pyqt6, markdown
    3. w64devkit (gcc)   -> telecharge + auto-extrait a la racine du depot si absent
    4. Exe (PyInstaller) -> .build\dist\TP-C-perso\
    5. Captures + PDF    -> outils\captures_doc.py puis outils\doc_pdf.py
    6. Bundle assemble   -> _bundle\TP-C-perso\ (exe, w64devkit, lanceurs, README+pdf, captures)
    7. Verification      -> l'exe assemble demarre (mode offscreen)
    8. Zip (option -Zip) -> _bundle\TP-C-perso.zip, pret pour une Release GitHub

  Ne modifie rien hors du depot. Les sorties (w64devkit\, .build\, _bundle\) sont
  ignorees par git.

.PARAMETER Zip
  Fabrique aussi le zip distribuable a la fin.

.PARAMETER SkipInstall
  Ne tente pas les installations (Python, pip, w64devkit) : suppose l'environnement pret.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1 -Zip
#>
param(
    [switch]$Zip,
    [switch]$SkipInstall
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Info($m) { Write-Host "[build] $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "[ ok ] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[ !! ] $m" -ForegroundColor Yellow }

# Racine du depot = dossier parent de packaging\
$Repo = Split-Path $PSScriptRoot -Parent
Set-Location $Repo
Info "Depot : $Repo"

$estAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $estAdmin) { Warn "Pas en administrateur : winget peut demander une elevation par paquet." }

# ---------------------------------------------------------------------------
# 1. Python 3.12
# ---------------------------------------------------------------------------
function Trouver-Python {
    $cands = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "${env:ProgramFiles(x86)}\Python312\python.exe"
    )
    foreach ($c in $cands) { if (Test-Path $c) { return $c } }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        $exe = & py -3.12 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $exe) { return $exe.Trim() }
    }
    return $null
}

$Python = Trouver-Python
if (-not $Python -and -not $SkipInstall) {
    Info "Python 3.12 absent, installation via winget..."
    winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements --disable-interactivity
    $Python = Trouver-Python
}
if (-not $Python) { throw "Python 3.12 introuvable. Installe-le (winget install Python.Python.3.12) puis relance." }
Ok "Python : $Python"

# ---------------------------------------------------------------------------
# 2. Paquets pip
# ---------------------------------------------------------------------------
if (-not $SkipInstall) {
    Info "Paquets pip : pyinstaller, pyqt6, markdown..."
    & $Python -m pip install --upgrade pip | Out-Null
    & $Python -m pip install pyinstaller pyqt6 markdown
}
Ok "Paquets pip prets"

# ---------------------------------------------------------------------------
# 3. w64devkit (gcc) a la racine du depot
# ---------------------------------------------------------------------------
$Wk  = Join-Path $Repo 'w64devkit'
$Gcc = Join-Path $Wk 'bin\gcc.exe'
if (-not (Test-Path $Gcc) -and -not $SkipInstall) {
    Info "w64devkit absent, telechargement de la derniere version x64..."
    $rel = Invoke-RestMethod 'https://api.github.com/repos/skeeto/w64devkit/releases/latest' -Headers @{ 'User-Agent' = 'build-tpc' }
    $asset = $rel.assets | Where-Object { $_.name -match '^w64devkit-x64-.*\.7z\.exe$' } | Select-Object -First 1
    if (-not $asset) { throw "Asset w64devkit x64 introuvable dans la derniere release." }
    $sfx = Join-Path $env:TEMP $asset.name
    Info ("Telechargement " + $asset.name + " (" + [math]::Round($asset.size/1MB) + " Mo)...")
    Invoke-WebRequest $asset.browser_download_url -OutFile $sfx
    Info "Extraction (auto-extractible 7z)..."
    & $sfx -y "-o$Repo" | Out-Null    # le SFX depose un dossier w64devkit\ dans -o
    Remove-Item $sfx -ErrorAction SilentlyContinue
    if (-not (Test-Path $Gcc)) { throw "Extraction w64devkit echouee. Extrais l'archive manuellement pour obtenir $Wk\." }
}
if (-not (Test-Path $Gcc)) { throw "gcc introuvable ($Gcc). w64devkit doit etre a la racine du depot." }
Ok ("gcc : " + (& $Gcc --version | Select-Object -First 1))
$env:PATH = (Join-Path $Wk 'bin') + ';' + $env:PATH   # gcc dispo pour les tests et les captures

# ---------------------------------------------------------------------------
# 4. Build de l'exe (PyInstaller)
# ---------------------------------------------------------------------------
$BuildDir = Join-Path $Repo '.build'
Info "Build de l'exe (PyInstaller)..."
& $Python -m PyInstaller --noconfirm --windowed --name TP-C-perso `
    --paths "$Repo" `
    --add-data "$Repo\contenu\be_c;contenu/be_c" `
    --distpath "$BuildDir\dist" --workpath "$BuildDir\work" --specpath "$BuildDir" `
    "$Repo\packaging\entree_be_c.py"
$ExeSrc = Join-Path $BuildDir 'dist\TP-C-perso'
if (-not (Test-Path (Join-Path $ExeSrc 'TP-C-perso.exe'))) { throw "Build echoue : exe introuvable." }
Ok "exe construit"

# ---------------------------------------------------------------------------
# 5. Regenerer captures + (le PDF est genere dans le bundle plus bas)
# ---------------------------------------------------------------------------
Info "Regeneration des captures (capture Qt, sans prendre l'ecran)..."
& $Python "$Repo\outils\captures_doc.py"
Ok "captures a jour"

# ---------------------------------------------------------------------------
# 6. Assembler le bundle
# ---------------------------------------------------------------------------
$Bundle = Join-Path $Repo '_bundle\TP-C-perso'
if (Test-Path $Bundle) { Remove-Item $Bundle -Recurse -Force }
New-Item -ItemType Directory -Force -Path $Bundle | Out-Null
Info "Assemblage du bundle dans $Bundle ..."
Copy-Item "$ExeSrc\*" $Bundle -Recurse -Force
Copy-Item $Wk (Join-Path $Bundle 'w64devkit') -Recurse -Force
Copy-Item "$Repo\packaging\lancer.bat" $Bundle -Force
Copy-Item "$Repo\packaging\diagnostic.bat" $Bundle -Force
# doc utilisateur du bundle : GUIDE.md (pas le README depot) sous le nom README.md
Copy-Item "$Repo\GUIDE.md" (Join-Path $Bundle 'README.md') -Force
Copy-Item "$Repo\captures" (Join-Path $Bundle 'captures') -Recurse -Force
& $Python "$Repo\outils\doc_pdf.py" "$Repo\GUIDE.md" (Join-Path $Bundle 'README.pdf')
# NB : lancer_demo.bat (interne) n'est volontairement PAS copie -> le bundle est distribuable.
Ok "bundle assemble"

# ---------------------------------------------------------------------------
# 7. Verification : l'exe assemble demarre
# ---------------------------------------------------------------------------
Info "Verification : l'exe demarre depuis le bundle ?"
$env:QT_QPA_PLATFORM = 'offscreen'
$proc = Start-Process -FilePath (Join-Path $Bundle 'TP-C-perso.exe') -PassThru
Start-Sleep -Seconds 6
$vivant = -not $proc.HasExited
if ($vivant) { Stop-Process -Id $proc.Id -Force }
Remove-Item Env:\QT_QPA_PLATFORM
if (-not $vivant) { throw "L'exe assemble ne demarre pas (imports ou assets manquants ?)." }
Ok "l'exe demarre depuis le bundle"

# ---------------------------------------------------------------------------
# 8. Zip distribuable (option)
# ---------------------------------------------------------------------------
if ($Zip) {
    $ZipPath = Join-Path $Repo '_bundle\TP-C-perso.zip'
    if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
    Info "Fabrication du zip..."
    # tar.exe natif de Windows (libarchive) : bien plus rapide que Compress-Archive sur
    # les milliers de fichiers de w64devkit. -a deduit le format zip de l'extension.
    $tar    = "$env:SystemRoot\System32\tar.exe"
    $parent = Split-Path $Bundle -Parent    # _bundle
    $leaf   = Split-Path $Bundle -Leaf       # TP-C-perso -> dossier racine dans le zip
    Push-Location $parent
    try { & $tar -a -c -f $ZipPath $leaf } finally { Pop-Location }
    if (-not (Test-Path $ZipPath)) { throw "Zip non produit (tar)." }
    Ok ("zip : " + $ZipPath + " (" + [math]::Round((Get-Item $ZipPath).Length/1MB) + " Mo)")
}

Write-Host ""
Ok "Termine."
Write-Host ("Bundle lancable : " + $Bundle) -ForegroundColor Green
if ($Zip) { Write-Host ("Zip a publier   : " + (Join-Path $Repo '_bundle\TP-C-perso.zip')) -ForegroundColor Green }
Write-Host "Publication en Release GitHub : voir RECONSTRUCTION.md." -ForegroundColor Cyan
