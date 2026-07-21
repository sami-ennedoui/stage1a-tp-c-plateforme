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
    6. Bundle assemble   -> _bundle\TP-C-perso\ (exe, w64devkit elague, lanceurs, README+pdf, captures)
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
# 3bis. clangd (diagnostics en direct) a la racine du depot
# ---------------------------------------------------------------------------
# w64devkit fournit gcc et MinGW, mais PAS clangd : clangd appartient a LLVM, c'est
# un autre paquet. Sans cette etape, lsp_clangd.clangd_disponible() rend False sur une
# machine etudiante et les diagnostics en direct sont silencieusement desactives.
$Cd    = Join-Path $Repo 'clangd'
$Clangd = Join-Path $Cd 'bin\clangd.exe'
if (-not (Test-Path $Clangd) -and -not $SkipInstall) {
    Info "clangd absent, telechargement de la derniere version windows..."
    $rel = Invoke-RestMethod 'https://api.github.com/repos/clangd/clangd/releases/latest' -Headers @{ 'User-Agent' = 'build-tpc' }
    $asset = $rel.assets | Where-Object { $_.name -match '^clangd-windows-.*\.zip$' } | Select-Object -First 1
    if (-not $asset) { throw "Asset clangd windows introuvable dans la derniere release." }
    $zipClangd = Join-Path $env:TEMP $asset.name
    Info ("Telechargement " + $asset.name + " (" + [math]::Round($asset.size/1MB) + " Mo)...")
    Invoke-WebRequest $asset.browser_download_url -OutFile $zipClangd
    $tmp = Join-Path $env:TEMP 'clangd-extrait'
    if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
    Expand-Archive -Path $zipClangd -DestinationPath $tmp -Force
    # l'archive contient un unique dossier clangd_<version>\ : on le remonte en clangd\
    $racine = Get-ChildItem $tmp -Directory | Select-Object -First 1
    if (-not $racine) { throw "Archive clangd inattendue : aucun dossier a la racine." }
    if (Test-Path $Cd) { Remove-Item $Cd -Recurse -Force }
    Move-Item $racine.FullName $Cd
    Remove-Item $zipClangd, $tmp -Recurse -Force -ErrorAction SilentlyContinue
    # Les runtimes sanitizer (lib\clang\<n>\lib) pesent ~30 Mo et ne servent jamais a un
    # serveur de langage : verifie sur la VM, 0 erreur sur un fichier sain et les vraies
    # erreurs toujours signalees sans eux. 92 Mo -> 63 Mo.
    Get-ChildItem (Join-Path $Cd 'lib\clang') -Directory -ErrorAction SilentlyContinue |
        ForEach-Object {
            $sanit = Join-Path $_.FullName 'lib'
            if (Test-Path $sanit) { Remove-Item $sanit -Recurse -Force }
        }
    if (-not (Test-Path $Clangd)) { throw "Extraction clangd echouee, attendu $Clangd." }
}
if (-not (Test-Path $Clangd)) {
    Warn "clangd absent ($Clangd) : le bundle n'aura pas les diagnostics en direct."
} else {
    Ok ("clangd : " + ((& $Clangd --version) -split "`n" | Select-Object -First 1))
    $env:PATH = (Join-Path $Cd 'bin') + ';' + $env:PATH
}

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
# $ErrorActionPreference = 'Stop' ne rattrape PAS le code de sortie d'un executable
# natif : sans ce test, l'etape imprimait « captures a jour » alors que le script
# n'existait meme pas. Un build qui ment sur une etape est pire qu'un build qui echoue.
$scriptCaptures = Join-Path $Repo 'outils\captures_doc.py'
if (-not (Test-Path $scriptCaptures)) {
    throw "Captures : $scriptCaptures introuvable. La couche de livraison (GUIDE.md, outils\, captures\) n'est pas sur cette branche."
}
& $Python $scriptCaptures
if ($LASTEXITCODE -ne 0) { throw "Captures : $scriptCaptures a echoue (code $LASTEXITCODE)." }
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

# Elagage de la COPIE livree seulement : le w64devkit du depot reste complet, un
# developpeur garde g++, gdb et cmake sous la main. Ce qui part ici ne sert a aucun
# moment au parcours be_c, seul parcours embarque.
#
# 567 Mo -> 319 Mo, mesure. Ce n'est pas de la cosmetique : le bundle se telecharge
# par une promo entiere sur le reseau de l'ecole.
#
# Choix volontairement conservateur. On ne retire que ce dont l'absence est
# demontrable : les compilateurs d'autres langages (Fortran, C++) et leurs
# bibliotheques, l'outillage de build tiers (cmake, ninja, ccache), le debogueur,
# l'editeur vim, et les sources .idl qui ne servent qu'a widl. On GARDE tout le
# reste, notamment lib\ et include\ : les bibliotheques d'import Windows et les
# en-tetes sont ce que l'editeur de liens et clangd consultent, et trier dedans
# demanderait une certitude qu'on n'a pas. c++filt est garde aussi, c'est un
# demangleur de binutils et pas un compilateur -- coupures a l'aveugle s'abstenir.
$WkB = Join-Path $Bundle 'w64devkit'
$binInutiles = @('cmake.exe', 'ccmake.exe', 'cpack.exe', 'ctest.exe', 'cmcldeps.exe',
                 'dcmake.exe', 'ninja.exe', 'gdb.exe', 'gdbserver.exe', 'ccache.exe',
                 'ctags.exe', 'quilt.exe',
                 'g++.exe', 'c++.exe', 'x86_64-w64-mingw32-c++.exe',
                 'gfortran.exe', 'x86_64-w64-mingw32-gfortran.exe')
$libexecInutiles = @('f951.exe', 'cc1plus.exe')      # Fortran et C++ proprement dits
$poidsAvant = (Get-ChildItem $WkB -Recurse -File | Measure-Object Length -Sum).Sum

$aRetirer = @()
foreach ($d in @('share\vim', 'share\cmake-4.3')) {
    $p = Join-Path $WkB $d
    if (Test-Path $p) { $aRetirer += Get-Item $p }
}
$aRetirer += Get-ChildItem (Join-Path $WkB 'bin') -File |
             Where-Object { $binInutiles -contains $_.Name }
$aRetirer += Get-ChildItem (Join-Path $WkB 'libexec') -Recurse -File |
             Where-Object { $libexecInutiles -contains $_.Name }
$aRetirer += Get-ChildItem (Join-Path $WkB 'lib') -Recurse -File |
             Where-Object { $_.Name -like 'libstdc++*' -or $_.Name -like 'libsupc++*' -or
                            $_.Name -like 'libgfortran*' -or $_.Name -like 'libcaf*' }
$aRetirer += Get-ChildItem $WkB -Recurse -File -Include '*.idl'

foreach ($c in $aRetirer) {
    if ($c -and (Test-Path -LiteralPath $c.FullName)) {
        Remove-Item -LiteralPath $c.FullName -Recurse -Force -ErrorAction SilentlyContinue
    }
}
$poidsApres = (Get-ChildItem $WkB -Recurse -File | Measure-Object Length -Sum).Sum
Ok ("w64devkit elague : {0:N0} Mo -> {1:N0} Mo" -f ($poidsAvant/1MB), ($poidsApres/1MB))

# gcc doit encore repondre APRES l'elagage, et depuis la copie livree. Sans ce
# controle, une coupure de trop ne se verrait qu'a l'ouverture du zip par un etudiant.
$GccBundle = Join-Path $WkB 'bin\gcc.exe'
if (-not (Test-Path $GccBundle)) { throw "Elagage : gcc.exe a disparu de la copie livree." }
$vGcc = & $GccBundle --version 2>&1 | Select-Object -First 1
if ($LASTEXITCODE -ne 0) { throw "Elagage : le gcc livre ne repond plus (code $LASTEXITCODE)." }
Ok "gcc livre apres elagage : $vGcc"

if (Test-Path $Cd) { Copy-Item $Cd (Join-Path $Bundle 'clangd') -Recurse -Force }
Copy-Item "$Repo\packaging\lancer.bat" $Bundle -Force
Copy-Item "$Repo\packaging\diagnostic.bat" $Bundle -Force
# doc utilisateur du bundle : GUIDE.md (pas le README depot) sous le nom README.md
Copy-Item "$Repo\GUIDE.md" (Join-Path $Bundle 'README.md') -Force
Copy-Item "$Repo\captures" (Join-Path $Bundle 'captures') -Recurse -Force
$pdf = Join-Path $Bundle 'README.pdf'
& $Python "$Repo\outils\doc_pdf.py" "$Repo\GUIDE.md" $pdf
# Meme piege qu'a l'etape 5 : un exe natif qui echoue ne stoppe pas le script. Sans ce
# test, le bundle partait sans son PDF et l'etape s'annoncait quand meme reussie.
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $pdf)) { throw "PDF du guide non produit ($pdf)." }
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

# Le demarrage ci-dessus ECRIT dans le bundle : journaux\session-*.jsonl, et selon les
# chemins parcourus progression.json / reglages.json / moodle_sync.json. Sans ce
# nettoyage, l'etape qui verifie le livrable le pollue : l'etudiant deballe une session
# fantome de la machine de build, et le zip change a chaque construction (horodatage et
# identifiant de session) alors qu'il devrait etre reproductible.
#
# Le nettoyage balaie la racine ET _internal. Mesure le 20 juillet en ouvrant une porte
# dans le bundle extrait : l'exe fige ecrit sa progression dans _internal\progression.json,
# pas a la racine. Ne nettoyer que la racine laissait donc passer le residu le plus
# revelateur, celui qui contient les exercices reussis sur la machine de build.
$residus = @('journaux', 'progression.json', 'reglages.json', 'moodle_sync.json', 'auteur.json', 'releve.txt')
foreach ($dossier in @($Bundle, (Join-Path $Bundle '_internal'))) {
    if (-not (Test-Path $dossier)) { continue }
    foreach ($r in $residus) {
        $p = Join-Path $dossier $r
        if (Test-Path $p) {
            Remove-Item $p -Recurse -Force
            $ou = if ($dossier -eq $Bundle) { '' } else { '_internal\' }
            Info "residu du test retire : $ou$r"
        }
    }
}

# clangd doit etre DANS le bundle, pas seulement sur la machine de build : c'est
# exactement le piege « ca marche chez moi ». On verifie le fichier livre.
$ClangdBundle = Join-Path $Bundle 'clangd\bin\clangd.exe'
if (Test-Path $ClangdBundle) {
    Ok ("clangd present dans le bundle : " + [math]::Round((Get-Item $ClangdBundle).Length/1MB) + " Mo")
} else {
    Warn "clangd ABSENT du bundle : pas de diagnostics en direct chez l'etudiant."
}

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
