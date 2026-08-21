# Honey Badger

Honey Badger is a lightweight desktop notes app for editing Markdown and plain-text files. It is built with Python, Tkinter and Mistune, with a simple folder browser and live Markdown formatting in the editor.

## Features

- Open a local folder and browse its subdirectories.
- Find `.md` and `.txt` files with recursive search.
- Edit notes in a single live-formatted text editor.
- Format Markdown headings, bold text, italic text, inline code, code blocks and unordered lists.
- Create new notes, rename existing notes or delete notes from the file browser.
- Prompt before losing unsaved changes when switching files or folders.
- Save notes with `Ctrl+S`.
- Remember the last opened folder between launches.

## Requirements

- Python 3.10 or newer
- Tkinter
- `mistune>=3.0.0`

Python's `tkinter` module is included with many Python installations. On Linux, it may need to be installed separately. For example:

```bash
# Debian or Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

## Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/kbarryfrank/Honey-Badger.git
cd Honey-Badger

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Run

With the virtual environment active, start Honey Badger with:

```bash
python main.py
```

Click **Open Folder** to choose the directory containing your notes. Honey Badger loads the previously opened folder automatically when it still exists.

## Keyboard shortcuts and actions

| Action | Shortcut or interaction |
| --- | --- |
| Open a folder | Click **Open Folder** |
| Create a note | `Ctrl+N` or click **New Note** |
| Search notes | `Ctrl+F`, then type in the search field |
| Save the current note | `Ctrl+S` |
| Open a note | Click a `.md` or `.txt` file |
| Browse a folder | Click a directory in the sidebar |
| Go to the parent folder | Click `.. (parent folder)` |
| Rename or delete a note | Right-click a note |

New notes use the Markdown extension by default. A `.txt` extension can be supplied when creating the note.

## Markdown formatting

The editor applies formatting after a short pause while you type. The current renderer supports these formatted elements:

````markdown
# Heading 1
## Heading 2

**bold** and *italic* text

`inline code`

- An unordered list item

```text
code block
```
````

Markdown files remain plain text on disk. The formatting is only the editor's visual presentation.

## Configuration

Honey Badger stores the last opened folder in a JSON file in the user's home directory:

```text
~/.honey_badger_config.json
```

The file contains the saved folder path and is created automatically when a folder is opened. It can be removed if the saved folder needs to be reset.

## Project structure

```text
Honey-Badger/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── app/
    ├── editor.py        # Editable Markdown editor
    ├── preview.py       # Markdown parsing and text styling
    ├── sidebar.py       # Folder browser and note actions
    ├── state.py         # Session state and saved configuration
    └── window.py        # Main Tkinter window and application events
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'mistune'`

Activate the virtual environment and install the dependencies again:

```bash
python -m pip install -r requirements.txt
```

### `ModuleNotFoundError: No module named 'tkinter'`

Install the Tkinter package provided by your operating system, then run `python main.py` again. See the platform examples in the Requirements section.

