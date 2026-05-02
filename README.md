# Chibi Dance Party

A lightweight desktop companion for Linux that spawns cute chibi characters
across your screen. Inspired by tools like Anima Engine, this app uses
pure 2D sprites to bring a bit of whimsy to your workspace. Characters
appear at random positions, dance (or just hang out!) for a few
seconds, then fade away. You can add your own PNG sprites with
transparent backgrounds by placing them in the `characters/` directory.

## Features

- **Random appearances:** Characters spawn at random intervals (2–8 seconds) and
  random screen positions.
- **Fade in/out:** Each sprite fades away smoothly after a set duration.
- **Customisable:** Add your own PNG files to the `characters/` folder. The
  application will load all images in that directory.
- **Open source:** Uses only Python and open‑source libraries (PySide6 and
  Pillow).

## Installation

1. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:

   ```bash
   python3 main.py
   ```

If you see no sprites, make sure the `characters/` folder contains at
least one PNG file. A simple placeholder chibi (`sample_chibi.png`)
is provided, and you can generate more by drawing your own or using
open‑source art.

## Adding Your Own Characters

Place any PNG images with transparent backgrounds into the
`characters/` directory. The script will automatically load them at
startup. For best results, use images around 128×128 pixels, though
larger images will also work. Files with larger dimensions may appear
bigger on screen.

## License

This project is released under the MIT License (see `LICENSE`). You
are free to use, modify, and distribute it as long as you include the
copyright notice.
