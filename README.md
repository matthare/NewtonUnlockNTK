# Newton Unlock for the Newton

A native Newton OS 2.x version of Newton Unlock, written in NewtonScript.

Tap **Game** to pick a game, write the registration code or owner name on the
input line, and the unlock code appears under **Unlock Code**. The name line
starts out filled in with the Newton's owner name, which most of these games
use. Silicon Casino needs no input and just shows its code.

Runs on Newton OS 2.0 and 2.1: MessagePad 120/130 (with 2.0), 2000, 2100 and
eMate 300. It's installed in the Extras drawer as **Unlock**.

## Files

| File | What it is |
|---|---|
| `NewtonUnlock.pkg` | The finished package, ready to install. |
| `NewtonUnlock.ns` | The app: its views (built from the standard Newton protos) and their scripts. |
| `unlockers.ns` | The games and the unlock algorithms, ported from the Python scripts in each game's folder. |
| `prelude/newton_defs.ns` | Newton OS 2.1 constants (protos, fonts, view flags), extracted from the Einstein emulator's source. |
| `prelude/toolkit.ns` | NTK-style helpers (`AddStepForm`, `StepDeclare`) and the package wrapper. |
| `prelude/icon.ns` | The Extras-drawer icon, made by `tools/make_icon.py` from the Newton logo. |
| `build.sh` | Builds `NewtonUnlock.pkg`. |
| `tests/check.py` | Runs `unlockers.ns` on this Mac and compares every answer with the Python scripts. |

## Installing

- **Real Newton:** install `NewtonUnlock.pkg` with Newton Connection Utilities,
  NCX, or a similar package installer, or from a PC Card.
- **Einstein:** drag `NewtonUnlock.pkg` onto the Einstein window, or use
  Einstein's install-package command.

## Building

Classic NTK projects are binary files that only open in NTK on an old Mac, so
this project is plain NewtonScript text built with
[NEWT/64](https://github.com/MatthiasWM/NEWT64), the NewtonScript compiler
used by Einstein's Toolkit. On this Mac it's in `~/NEWT64`.

```
./build.sh
```

If you want to open it in real NTK instead, the code in `NewtonUnlock.ns` and
`unlockers.ns` can be pasted into an NTK text file almost unchanged; the views
would be redrawn in NTK's layout editor.

## Checking the algorithms

```
python3 tests/check.py
```

Expect `0 mismatches`. Newton integers are 30 bits, so the code avoids any
arithmetic past 536,870,911, and registration codes over 9 digits (or above
536,870,909) are rejected as too long. Real codes are 8 digits.

## Adding a game

1. Add a frame to `games` in `unlockers.ns`; a Tactile Systems game is just a
   title and its two-letter salt.
2. Add the game to `GAMES` in `tests/check.py`, at the same position, and run it.
3. If it goes before World Conquest in the list, bump `gameIndex` in
   `NewtonUnlock.ns` (the game shown first).
4. `./build.sh`
