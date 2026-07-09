#!/usr/bin/env bash
# Lanceur Linux de l'atelier TP C, parcours be_c. Équivalent de lancer.bat.
# Utilise le Python du système et PyQt6. Le compilateur gcc doit être présent,
# il l'est par défaut sur la plupart des distributions ou s'installe en un paquet.
set -euo pipefail

# racine de la plateforme = dossier parent de packaging/
ici="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ici"

# Tuteur IA optionnel : rend claude ou codex trouvable s'il est installé pour l'utilisateur
export PATH="$HOME/.local/bin:$PATH"
[ -d "$HOME/.npm-global/bin" ] && export PATH="$HOME/.npm-global/bin:$PATH"

py="$(command -v python3 || true)"
if [ -z "$py" ]; then
    echo "Python 3 est introuvable. Installe-le, par exemple : sudo dnf install python3" >&2
    exit 1
fi
if ! "$py" -c "import PyQt6" 2>/dev/null; then
    echo "PyQt6 manque. Installe-le : pip install --user PyQt6" >&2
    echo "Sur Fedora tu peux aussi : sudo dnf install python3-pyqt6" >&2
    exit 1
fi

exec "$py" atelier_snake.py --parcours be_c "$@"
