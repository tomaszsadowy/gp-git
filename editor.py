import tkinter as tk
import ctypes
import re
import os
import platform


def execute(event=None):
    # Write the Content to the Temporary File
    with open("run.py", "w", encoding="utf-8") as f:
        f.write(editArea.get("1.0", tk.END))
    # Start the File in a new CMD Window
    os.system('start cmd /K "python run.py"')


def changes(event=None):
    global previousText
    # If actually no changes have been made stop / return the function
    if editArea.get("1.0", tk.END) == previousText:
        return
    # Remove all tags so they can be redrawn
    for tag in editArea.tag_names():
        editArea.tag_remove(tag, "1.0", "end")
    # Add tags where the search_re function found the pattern
    i = 0
    for pattern, color in repl:
        for start, end in search_re(pattern, editArea.get("1.0", tk.END)):
            editArea.tag_add(f"{i}", start, end)
            editArea.tag_config(f"{i}", foreground=color)
            i += 1
    previousText = editArea.get("1.0", tk.END)


def search_re(pattern, text, groupid=0):
    matches = []
    text = text.splitlines()
    for i, line in enumerate(text):
        for match in re.finditer(pattern, line):
            matches.append((f"{i + 1}.{match.start()}", f"{i + 1}.{match.end()}"))
    return matches


if platform.system() == "Windows":
    ctypes.windll.shcore.SetProcessDpiAwareness(True)


# Function to convert RGB to Hexadecimal
def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


# Setup Tkinter
root = tk.Tk()  # Corrected tk() to tk.Tk() to properly initialize a Tkinter window
root.geometry("500x500")

previousText = ""

# Define colors for the various types of tokens using the rgb_to_hex function
normal = rgb_to_hex(234, 234, 234)
keywords = rgb_to_hex(234, 95, 95)
comments = rgb_to_hex(95, 234, 165)
string = rgb_to_hex(234, 162, 95)
function = rgb_to_hex(95, 211, 234)
background = rgb_to_hex(42, 42, 42)
font = "Consolas 15"

# Define a list of Regex Pattern that should be colored in a certain way
repl = [
    [
        "(^| )(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)($| )",
        keywords,
    ],
    ['".*?"', string],
    ["'.*?'", string],
    ["#.*?$", comments],
]

# Make the Text Widget
# Add a hefty border width so we can achieve a little bit of padding
editArea = tk.Text(
    root,
    background=background,
    foreground=normal,
    insertbackground=normal,
    relief=tk.FLAT,
    borderwidth=30,
    font=font,
)

# Place the Edit Area with the pack method
editArea.pack(fill=tk.BOTH, expand=1)

# Insert some Standard Text into the Edit Area
editArea.insert(
    "1.0",
    """from argparse import ArgumentParser
from random import shuffle, choice
import string

# Setting up the Argument Parser
parser = ArgumentParser(

    prog='Password Generator.',
    description='Generate any number of passwords with this tool.'
)
""",
)

# Bind the KeyRelase to the Changes Function
editArea.bind("<KeyRelease>", changes)

# Bind Control + R to the exec function
root.bind("<Control-r>", execute)

changes()
root.mainloop()
