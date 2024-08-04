import tkinter as tk
import ctypes
import re
import os
import platform


def execute(event=None):
    with open("run.py", "w", encoding="utf-8") as f:
        f.write(editArea.get("1.0", tk.END))
    os.system('start cmd /K "python run.py"')


def changes(event=None):
    global previousText
    if editArea.get("1.0", tk.END) == previousText:
        return
    for tag in editArea.tag_names():
        editArea.tag_remove(tag, "1.0", "end")
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


def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


root = tk.Tk()
root.geometry("500x500")

previousText = ""

normal = rgb_to_hex(234, 234, 234)
keywords = rgb_to_hex(234, 95, 95)
comments = rgb_to_hex(95, 234, 165)
string = rgb_to_hex(234, 162, 95)
function = rgb_to_hex(95, 211, 234)
background = rgb_to_hex(42, 42, 42)
font = "Consolas 15"

repl = [
    [
        "(^| )(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)($| )",
        keywords,
    ],
    ['".*?"', string],
    ["'.*?'", string],
    ["#.*?$", comments],
]

editArea = tk.Text(
    root,
    background=background,
    foreground=normal,
    insertbackground=normal,
    relief=tk.FLAT,
    borderwidth=30,
    font=font,
)

editArea.pack(fill=tk.BOTH, expand=1)
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

editArea.bind("<KeyRelease>", changes)
root.bind("<Control-r>", execute)

changes()
root.mainloop()
