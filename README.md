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
  <img width="500" alt="image" align="center" src="https://github.com/user-attachments/assets/5ffeb935-9198-402f-88e2-240332c7fe7a">
</h1>

#### - Initializing a Repository
To start a new repository, use the start command:
```
gpgit start
```
This will create a new repository in your current working directory.

----
#### - Writing a Tree
To create a tree object from the current index, use the write-tree command:
```
gpgit write-tree
```
----
#### - Committing Changes
To record changes to the repository, use the save command:
```
gpgit save -m "Your commit message"
```
----
#### - Viewing the History
To show the saved history, use the history command:
```
gpgit history
```
----
#### - Comparing Changes
To show changes between commits, the commit and working tree, etc., use the compare command:
```
gpgit compare
```
----
#### - Switching Branches
To switch branches or restore working tree files, use the switch command:
```
gpgit switch <branch-name>
```
----
#### - Labelling
To create, list, delete, or verify a tag object signed with GPG, use the label command:
```
gpgit label <label-name>
```
----
#### - Branch Management
To list, create, or delete branches, use the branch command:
```
gpgit branch
```
---- 
