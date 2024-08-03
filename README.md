
<h1 align="center">
  <img src="https://github.com/user-attachments/assets/e26fac92-5d9e-4be4-8dc3-349f295cbd9b" width=250>
</h1>

<p align="center">
  <i>A local version control system for newbies, fully built in Python 🐍</i>
</p> 

## Introduction

**gp-git** (*general purpose git*) is a local, lightweight version control system designed specifically for new programmers learning Git. It encapsulates the essential features of Git, streamlined with a more user-friendly command set and simplified syntax.

This package is entirely written in Python and includes a built-in code editor for on-the-fly changes and editing. Easily install gp-git via PyPI, with all commands executed through the terminal.

## Installation

1. Install with [pip](xxxx):
   ```sh
   pip install gp-git
   gp-git
   ```
2. Follow the on-screen instructions to complete the setup.

## Usage

gp-git offers a comprehensive set of commands, accessible via the `gp-git help` command. Below is a summary of available commands and their descriptions. The commands in square brackets indicate the equivalent Git commands.

<h1 align="center">
  <img width="1197" alt="image" src="https://github.com/user-attachments/assets/d8a47d3f-2e6d-4faf-a061-94518ce0999b">
</h1>

### Common Commands

#### Initializing a Repository
**start**: Initializes a new project in the current working directory. This is essential for beginning version control on a new project.
```sh
gp-git start
```

#### Recording Changes to a Repository
**save**: Records changes to the repository with a message describing the changes. This is a core function of any version control system, allowing you to save the state of your project.
```sh
gp-git save <"Your commit message">
```

#### Sending Changes to a Repository
**throw**: Sends your saved changes to the remote repository. This is critical for sharing changes with collaborators and backing up your work.
```sh
gp-git throw
```

#### Displaying Commit History
**history**: Displays the commit history of the repository. This is important for tracking changes over time and understanding the evolution of the project.
```sh
gp-git history
```

#### Switching Branches
**switch**: Switches branches or restores working tree files. This is necessary for working on different features or versions of the project simultaneously.
```sh
gp-git switch <branch-name>
```

