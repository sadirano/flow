Work in Progress - Core Overlay Engine (Prototype)

# Quiz Project

This project provides a quiz application that can run either as a GUI (using Tkinter) or as a CLI application.
You can run the quiz in two modes:
- **Romaji mode:** Answers are handled in their original form.
- **Kana mode:** Answers (and autocompletion) are converted from romaji to kana.

## File Structure

```
project/
├── README.md      # This file
├── utils.py       # Common utility functions (question loading, statistics, display, etc.)
├── kana.py        # Romaji-to-Kana conversion functions and kana-specific autocomplete
├── gui.py         # Custom Tkinter widgets (e.g. AutocompleteEntry)
├── quiz_app.py    # The main GUI quiz application (supports both romaji and kana modes)
├── cli_romaji.py  # Command-line quiz in Romaji mode
└── cli_kana.py    # Command-line quiz in Kana mode
```

## Usage

### GUI Version

Run the GUI version by providing the quiz file and (optionally) the mode:
```
python quiz_app.py <quiz_file> [romaji|kana]
```
If no mode is provided, **romaji** is used by default.

### CLI Version

For the CLI quiz in Romaji mode:
```
python cli_romaji.py <quiz_file>
```

For the CLI quiz in Kana mode:
```
python cli_kana.py <quiz_file>
```

## Requirements

- Python 3.x
- Tkinter (for the GUI version)
- readline (for the CLI version)
- wcwidth (for proper text alignment in the CLI)
```

