# Chibi Dance Party

Lightweight Linux desktop companion that spawns 2D chibi characters (PNG/GIF) in transparent windows.

## Quick start

```bash
pip install -r requirements.txt
python3 main.py
```

## Configuration

Copy and edit:

```bash
cp config.example.json config.json
```

Supported settings include spawn timing, spawn mode (`random`, `edges`, `bottom_walk`, `corners`), max active characters, and fade duration.

## Characters

Put `.png` or `.gif` files into `characters/`.

If none are found, the app exits with a friendly message instead of crashing.

## Dev install

```bash
pip install -e .
chibi-dance-party
```

## Legal

Do not commit copyrighted anime/movie/game characters unless you have explicit permission.
