#!/usr/bin/env bash
# Build Linux du BE Snake, sur une COPIE de l'archive (l'original reste intact).
# Sortie : un binaire snake dans SNAKE/, à lancer depuis SNAKE/ car les assets
# (polices/, images/) sont chargés en chemin relatif.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
SNAKE="$HERE/SNAKE"

# pkg-config : le nom du module ttf/image varie selon la distro, on détecte.
PKGS="sdl3"
for c in sdl3-ttf SDL3_ttf; do pkg-config --exists "$c" 2>/dev/null && { PKGS="$PKGS $c"; break; }; done
for c in sdl3-image SDL3_image; do pkg-config --exists "$c" 2>/dev/null && { PKGS="$PKGS $c"; break; }; done
echo "paquets pkg-config utilisés : $PKGS"

cd "$SNAKE"
# Tous les .c sauf les deux mains alternatifs (main_start.c, save.c).
# myLib.c est un reliquat console Windows (windows.h/conio.h), non référencé.
SOURCES=$(find . -name '*.c' ! -name 'main_start.c' ! -name 'save.c' ! -name 'myLib.c')
gcc -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable \
    $(pkg-config --cflags $PKGS) \
    $SOURCES \
    $(pkg-config --libs $PKGS) -lm \
    -o snake
echo "OK -> $SNAKE/snake   (à lancer depuis $SNAKE)"
