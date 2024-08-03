<h1 align="center">
  <img src="https://github.com/user-attachments/assets/e26fac92-5d9e-4be4-8dc3-349f295cbd9b" width=250>
</h1>

<p align="center">
  <i align="center"> A local version control system for newbies, fully built in Python </i>
</p> 

## Introduction

'<b>gp-git</b>' (<i>general purpose git</i>) is a local, lightweight version control system designed specifically for new programmers learning Git. It encapsulates the essential features of Git, streamlined with a more user-friendly command set and simplified syntax. 

This package is entirely written in Python and includes a built-in code editor for on-the-fly changes and editing. Easily install gp-git via PyPI, with all commands executed through the terminal.

## Installation

1. Install with [pip](xxxx)
   + $ `pip install gp-git`
   + $ `gp-git`
2. xxx


## Usage

This package offers a vast amount of commands, with its full list being accesible via the `gpgit help` command. Below you can see all available commands and their descriptions.
<h1 align="center">
  <img width="1197" alt="image" src="https://github.com/user-attachments/assets/d8a47d3f-2e6d-4faf-a061-94518ce0999b">
</h1>

Below are some examples of the more common commands:
#### - Initializing a Repository
<i><b>start</b></i>: Initializes a new project in the current working directory. This is essential for beginning version control on a new project.
```
gp-git start
```
----
#### - Record Changes to a Repository
<i><b>save</b></i>: Records changes to the repository with a message describing the changes. This is a core function of any version control system, allowing you to save the state of your project.
```
gp-git save "Your commit message"
```
----
#### - Send Changes to Repository
<i><b>throw</b></i>: Sends your saved changes to the remote repository. This is critical for sharing changes with collaborators and backing up your work.
```
gp-git throw
```
----
#### - Display Save History
<i><b>history</b></i>: Displays the commit history of the repository. This is important for tracking changes over time and understanding the evolution of the project.
```
gp-git history
```
