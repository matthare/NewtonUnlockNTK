#!/usr/bin/env python3
"""Run the NewtonScript unlock functions (unlockers.ns) with NEWT/64 on this Mac
and compare every answer with the original Python scripts.

    python3 tests/check.py

NEWT/64 only handles ASCII text properly and lacks the Newton's Downcase, so
this uses ASCII inputs and defines a stand-in for Downcase. On a real Newton, text is Unicode, just like Python's ord().
"""
import importlib.util, os, random, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REGISTER = os.path.dirname(SRC)
NEWT = os.path.expanduser('~/NEWT64/build/newt64')

# same order as `games` in unlockers.ns
GAMES = [('columns', 'unlock_code'), ('deepspacenewt', 'reg_code'), ('mahjongg', 'reg_string'),
         ('minefieldii', 'unlock_code'), ('motile', 'unlock_code'), ('newthack', 'reg_number'),
         ('newtopoly', 'reg_code'), ('scramble', 'unlock_code'), ('seahunt', 'unlock_code'),
         ('siliconcasino', None), ('solitodx', 'unlock_code'), ('supernewtris', 'unlock_code'),
         ('worldcon', 'unlock_code'), ('xwordbuddy', 'unlock_code'), ('xwordsearch', 'unlock_code'),
         ('yazi', 'reg_string')]

SHIMS = r'''
// Host stand-in for the Newton's Downcase, which NEWT/64 lacks (ASCII only)
global Downcase(s) begin
    for i := 0 to StrLen(s) - 1 do
        if Ord(s[i]) >= 65 and Ord(s[i]) <= 90 then s[i] := Chr(Ord(s[i]) + 32);
    return s;
end;
'''


def load(folder, fn):
    if fn is None:
        code = open(f'{REGISTER}/{folder}/serialnumber.txt').read().strip()
        return lambda text: code
    spec = importlib.util.spec_from_file_location(folder, f'{REGISTER}/{folder}/{folder}_unlock.py')
    m = importlib.util.module_from_spec(spec)
    sys.modules[folder] = m
    spec.loader.exec_module(m)
    return getattr(m, fn)


def expected(f, folder, fn, text):
    """What the apps should show: the code, ERR, or NONE for a blank entry."""
    if fn is not None and not text.strip(' \t'):
        return 'NONE'
    try:
        if folder == 'newtopoly' and len(text) < 2:
            return 'ERR'
        if fn == 'unlock_code':
            t = text.strip(' \t')
            if not t.isdigit() or len(t) > 9 or int(t) > 536870909:
                return 'ERR'
            salt = getattr(sys.modules[folder], 'SALT', None)
            if int(t) < (ord(salt[0]) * 100 + ord(salt[1]) if salt else 6767):
                return 'ERR'
        return str(f(text))
    except Exception:
        return 'ERR'


def ns_string(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    random.seed(11)
    printable = [chr(c) for c in range(32, 127)]
    names = ['John Appleseed', 'Hare', 'A', 'ab', 'Sam', 'Jo Smith', '  Spaced Name  ', 'abcdefg',
             '1234567', 'O\'Brien', 'Back\\slash', 'Quote"d']
    cases = []
    for i, (folder, fn) in enumerate(GAMES):
        f = load(folder, fn)
        if fn is None:
            inputs = ['', 'anything']
        elif fn == 'unlock_code':
            inputs = [str(random.randint(0, 99999999)) for _ in range(150)] + \
                     ['12345678', '10000', '6767', '0', ' 12345678 ', '12a45', '', '   ', '999999999']
        else:
            inputs = names + [''.join(random.choice(printable) for _ in range(random.randint(1, 30)))
                              for _ in range(150)]
        for t in inputs:
            cases.append((i, t, expected(f, folder, fn, t)))

    # Run in chunks: one script holding every case compiles to a single function
    # bigger than 64 KB, past the reach of NewtonScript's 16-bit branch offsets.
    got = []
    with tempfile.TemporaryDirectory() as tmp:
        script = os.path.join(tmp, 'test.ns')
        for start in range(0, len(cases), 200):
            body = ['local r;']
            for i, t, _ in cases[start:start + 200]:
                body.append(f'r := unlock:Compute(games[{i}], {ns_string(t)});')
                body.append('print(if r = nil then "NONE" else if r.error then "ERR" else r.code); print("\\n");')
            with open(script, 'w') as out:
                out.write(SHIMS)
                out.write(open(os.path.join(SRC, 'unlockers.ns')).read())
                out.write('\n'.join(body) + '\n')
            out = subprocess.run([NEWT, script], capture_output=True, text=True).stdout
            got += out.split('\n')[:len(cases[start:start + 200])]

    bad = [(GAMES[i][0], t, want, have) for (i, t, want), have in zip(cases, got) if want != have]
    for b in bad[:20]:
        print('MISMATCH', b)
    print(f'{len(cases)} cases, {len(bad)} mismatches')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
