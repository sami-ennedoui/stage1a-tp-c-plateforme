#!/usr/bin/env bash
# lancer.sh -- compile et lance les quatre harnais de test de la logique Snake.
# Sortie : 0 si tous passent, 1 si au moins un echoue.

HERE="$(cd "$(dirname "$0")" && pwd)"
SNAKE="$HERE/../SNAKE"

# Detection des paquets SDL (meme logique que build.sh).
PKGS="sdl3"
for c in sdl3-ttf SDL3_ttf; do
    pkg-config --exists "$c" 2>/dev/null && { PKGS="$PKGS $c"; break; }
done
for c in sdl3-image SDL3_image; do
    pkg-config --exists "$c" 2>/dev/null && { PKGS="$PKGS $c"; break; }
done

CFLAGS="$(pkg-config --cflags $PKGS)"
LIBS="$(pkg-config --libs $PKGS) -lm"

# Sources communes du projet (logique pure, sans main ni modules graphiques).
SRCS_PROJET="$SNAKE/VariablesGlobales.c $SNAKE/InitialisationJeu.c $SNAKE/GestionJeu.c"

ECHOUE=0

# compile_et_tester <nom_sans_extension>
# Compile le harnais et l'execute. Met ECHOUE a 1 si compilation ou execution echoue.
compile_et_tester() {
    local nom="$1"
    local src="$HERE/${nom}.c"
    local bin="$HERE/${nom}"

    printf "  Compilation %-22s ... " "$nom"
    if gcc -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable \
           -I"$SNAKE" \
           $CFLAGS \
           "$src" $SRCS_PROJET \
           $LIBS \
           -o "$bin" 2>&1; then
        printf "OK\n"
    else
        printf "ECHEC compilation\n"
        ECHOUE=1
        return
    fi

    printf "  Execution  %-22s\n" "$nom"
    if "$bin"; then
        : # succes, le test lui-meme a affiche PASS
    else
        ECHOUE=1
    fi
    printf "\n"
}

echo "========================================="
echo "  Harnais de test -- logique Snake"
echo "========================================="
compile_et_tester test_init
compile_et_tester test_deplacement
compile_et_tester test_croissance
compile_et_tester test_collision
echo "========================================="

if [ "$ECHOUE" -eq 0 ]; then
    echo "  Resultat final : PASS (tous les tests ont reussi)"
    exit 0
else
    echo "  Resultat final : FAIL (au moins un test a echoue)"
    exit 1
fi
