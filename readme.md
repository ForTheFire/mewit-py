# 🐱 mewit

> A homemade version control system, with its own rules, its own character, and a pinch of auto-cat.

`mewit` is a from-scratch reimplementation of Git in Python, built to understand what actually happens under the hood when you run `git commit`. It's not a 1:1 clone of Git — it makes a few different design choices, aimed at being simpler to use without losing the substance.

## Why it exists

Git looks like a magic box: you throw your code in, and if something goes wrong, it hands it back to you. `mewit` exists to take that box apart and see what's inside: hashes, blobs, trees, commits, and a history that holds itself together thanks to one simple principle — **the name of anything saved is the hash of what it contains**.

## Installation

```bash
git clone https://github.com/ForTheFire/mewit-py
cd mewit
pip install psutil
pip install -e .
```

`pip install -e .` registers `mewit` as an actual command on your system (editable mode: any change you make to the source is picked up immediately, no reinstall needed). After this, you can run `mewit` from any folder, instead of typing out the full path to `main.py` every time.

The only external dependency is `psutil` (used for managing the autosave daemon). Everything else is Python standard library.

## Commands

### `mewit init`
Initializes a new repository in the current folder, creating the `.mew/` structure.

```bash
mewit init
```

### `mewit add <file...>`
Stages one or more files for the next commit. Also accepts whole folders (explored recursively).

```bash
mewit add main.py
mewit add folder/
```

### `mewit rm <file...>`
Removes one or more files from tracking (doesn't delete them from disk, just stops following them).

```bash
mewit rm old_file.py
```

### `mewit commit [message]`
Saves a permanent snapshot of the current state. The message is optional.

```bash
mewit commit "added the parser"
```

**Note:** `commit` automatically checks all already-tracked files and updates the hashes of the ones that changed — you don't need to run `add` again on a file just because it changed, unless you specifically want to exclude it from the next commit.

### `mewit log`
Shows the commit history, from most recent to first.

```bash
mewit log
```

### `mewit status`
Compares the current state of your files against the last commit: what's changed, what's missing, what's safe.

```bash
mewit status
```

### `mewit checkout <hash>`
Restores the working folder to exactly how it looked at a specific commit. **Nothing gets destroyed**: any file that would be overwritten or removed is moved first into `.acf/checkoutN/`, recoverable by hand.

```bash
mewit checkout a1b2c3d4e5...
```

## 🤖 The autosave daemon

`mewit` includes an optional daemon that acts as a safety net while you work, independent of when you decide to `commit`.

**How it works:** instead of saving at fixed time intervals, the daemon counts **lines added or removed** across already-tracked files. Once the accumulated total crosses a threshold (20 lines), it triggers a raw snapshot of the files, saved under `.mew/autosave/<timestamp>/`.

```bash
mewit autosave-start    # starts the daemon in the background
mewit autosave-status   # checks whether it's running
mewit autosave-stop     # stops it
```

**Under the hood:** the daemon runs as a separate process, detached from the terminal. Inside it, a thread listens on a local socket waiting for the stop command, while the main loop periodically checks the state of the files. "Is it alive?" is verified not just by checking that the PID exists, but also that it actually belongs to a Python process — to avoid false positives in case the operating system reassigns that number to a different process after a reboot.

## Internal structure

```
.mew/
├── objects/
│   ├── blobs/       # file contents, one file per hash
│   ├── trees/       # path → hash maps, a snapshot of the structure
│   └── commits/      # metadata for each commit (tree, parent, message)
├── refs/
│   └── heads/main    # pointer to the latest commit
├── HEAD              # reference to the current branch
├── INDEX              # hash of the tree "ready" for the next commit
└── autosave.pid       # daemon PID, if running
```

Every object (`blob`, `tree`, `commit`) is identified **exclusively** by the SHA-1 hash of its own content. Identical contents produce the same hash, so they only get saved once — the same deduplication idea that makes Git efficient.

## Design choices (where mewit departs from Git)

- **No "granular" staging area:** `commit` updates all already-tracked files on its own, not just the ones explicitly passed to `add`. Philosophy: mewit is meant as a safety net, not a tool for surgical commits.
- **Deleted files:** if a tracked file disappears from disk, it's automatically removed from the tree on the next `add`/`commit` — no need for a dedicated command to "confirm" the deletion.
- **Non-destructive checkout:** every checkout saves everything it overwrites or removes into `.acf/`, numbered progressively.
- **Objects split by type** (`blobs/`, `trees/`, `commits/` in separate folders) instead of all mixed together like Git does — easier to inspect by hand.

## Roadmap

- [ ] Full port to Rust
- [ ] Multiple branches
- [ ] Short references to commits (not just the full hash)

## The name

mewit = **mew** (the sound a cat makes) + **git**. Because even version control systems need to purr sometimes.

---

*Built piece by piece, understanding every line before writing it.* 🐾
