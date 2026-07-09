#!/usr/bin/env bash
# Construit le bundle Linux lançable TP-C-perso à partir d'un clone du dépôt.
# Équivalent Linux de build_windows.ps1. Différence : Linux fournit gcc en système,
# donc le bundle n'embarque pas de compilateur, il est bien plus léger.
#
# Étapes, toutes réutilisent ce qui est déjà présent :
#   1. Paquets pip     -> pyinstaller, pyqt6, markdown (en --user, sans droits admin)
#   2. Binaire         -> PyInstaller, dossier .build/dist/TP-C-perso/
#   3. Bundle assemblé -> _bundle/TP-C-perso-linux/ (binaire, lanceur, GUIDE)
#   4. Vérification    -> le binaire assemblé démarre en mode offscreen
#   5. Archive (option -a) -> _bundle/TP-C-perso-linux.tar.gz, prête pour une release
#
# Ne modifie rien hors du dépôt. Les sorties (.build/, _bundle/) sont ignorées par git.
#
# Usage :
#   packaging/build_linux.sh            construit le bundle
#   packaging/build_linux.sh -a         construit et fabrique l'archive tar.gz
#   packaging/build_linux.sh --skip-install   suppose pyinstaller déjà présent
set -euo pipefail

info() { printf '\033[36m[build]\033[0m %s\n' "$1"; }
ok()   { printf '\033[32m[ ok ]\033[0m %s\n' "$1"; }

archive=0
skip_install=0
for a in "$@"; do
    case "$a" in
        -a|--archive) archive=1 ;;
        --skip-install) skip_install=1 ;;
    esac
done

# racine du dépôt = dossier parent de packaging/
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo"
info "Dépôt : $repo"

py="$(command -v python3)"
[ -z "$py" ] && { echo "python3 introuvable" >&2; exit 1; }

if [ "$skip_install" -eq 0 ]; then
    info "Paquets pip (--user) : pyinstaller, pyqt6, markdown..."
    "$py" -m pip install --user --quiet --upgrade pip
    "$py" -m pip install --user --quiet pyinstaller pyqt6 markdown
fi
"$py" -c "import PyInstaller" 2>/dev/null || { echo "PyInstaller manque, relance sans --skip-install" >&2; exit 1; }

command -v gcc >/dev/null || { echo "gcc introuvable. Installe-le, par ex : sudo dnf install gcc" >&2; exit 1; }

# 2. Build du binaire
build_dir="$repo/.build"
info "Build du binaire (PyInstaller)..."
"$py" -m PyInstaller --noconfirm --windowed --name TP-C-perso \
    --paths "$repo" \
    --add-data "$repo/contenu/be_c:contenu/be_c" \
    --distpath "$build_dir/dist" --workpath "$build_dir/work" --specpath "$build_dir" \
    "$repo/packaging/entree_be_c.py"
exe_src="$build_dir/dist/TP-C-perso"
[ -x "$exe_src/TP-C-perso" ] || { echo "Build échoué : binaire introuvable" >&2; exit 1; }
ok "binaire construit"

# 3. Assemblage du bundle
bundle="$repo/_bundle/TP-C-perso-linux"
rm -rf "$bundle"
mkdir -p "$bundle"
info "Assemblage du bundle dans $bundle ..."
cp -a "$exe_src/." "$bundle/"
[ -f "$repo/GUIDE.md" ] && cp "$repo/GUIDE.md" "$bundle/README.md"
[ -d "$repo/captures" ] && cp -a "$repo/captures" "$bundle/captures"

# lanceur du bundle : PyQt6 et Python sont figés dans le binaire, seul gcc reste requis
cat > "$bundle/lancer.sh" <<'LANCEUR'
#!/usr/bin/env bash
# Lance TP-C-perso. gcc doit être présent sur la machine (compilation des exercices C).
set -euo pipefail
ici="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$HOME/.local/bin:$PATH"
if ! command -v gcc >/dev/null; then
    echo "gcc est requis pour compiler les exercices. Installe-le :" >&2
    echo "  Fedora : sudo dnf install gcc     Debian/Ubuntu : sudo apt install gcc" >&2
    exit 1
fi
exec "$ici/TP-C-perso" "$@"
LANCEUR
chmod +x "$bundle/lancer.sh"
ok "bundle assemblé"

# 4. Vérification : le binaire démarre
info "Vérification : le binaire démarre depuis le bundle ?"
QT_QPA_PLATFORM=offscreen "$bundle/TP-C-perso" &
pid=$!
sleep 6
if kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    ok "le binaire démarre depuis le bundle"
else
    echo "Le binaire assemblé ne démarre pas (imports ou assets manquants ?)" >&2
    exit 1
fi

# 5. Archive
if [ "$archive" -eq 1 ]; then
    arch="$repo/_bundle/TP-C-perso-linux.tar.gz"
    rm -f "$arch"
    info "Fabrication de l'archive..."
    tar -C "$repo/_bundle" -czf "$arch" TP-C-perso-linux
    ok "archive : $arch ($(du -h "$arch" | cut -f1))"
fi
