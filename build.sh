#!/bin/sh
# Build NewtonUnlock.pkg with NEWT/64 (https://github.com/MatthiasWM/NEWT64).
#   ./build.sh            (NEWT/64 expected at ~/NEWT64/build/newt64, or set NEWT64=...)
set -e
cd "$(dirname "$0")"
NEWT64="${NEWT64:-$HOME/NEWT64/build/newt64}"
mkdir -p build
{
    cat prelude/newton_defs.ns prelude/toolkit.ns prelude/icon.ns unlockers.ns
    echo "kPackagePath := \"$PWD/NewtonUnlock.pkg\";"
    cat NewtonUnlock.ns
} > build/NewtonUnlock-all.ns
rm -f NewtonUnlock.pkg
"$NEWT64" build/NewtonUnlock-all.ns
[ -s NewtonUnlock.pkg ] || { echo "build failed: no package written" >&2; exit 1; }
echo "wrote NewtonUnlock.pkg ($(wc -c < NewtonUnlock.pkg | tr -d ' ') bytes)"
