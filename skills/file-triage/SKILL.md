---
name: file-triage
description: Sort, rename, and organise files in a target directory with confirmation.
version: 0.1.0
author: nexus
trigger: "sort these files", "organise", "rename", "clean up this folder"
tools: [file_list, file_move, file_rename, file_delete, memory]
trust: builtin
---

# File triage

Sort, rename, and tidy a directory the user points you at.

## Steps

1. List the target directory and propose a plan (groupings, renames, deletes).
2. **Show the plan and wait for explicit approval before touching anything.**
   `file_delete` and any move that overwrites pass through the approval gate.
3. Apply the approved changes; report what was done.
4. Remember the user's naming/sorting conventions in `nexus_memory` so the next
   triage matches their taste.

## Safety

- Never delete without confirmation. Never overwrite silently.
- Prefer move-to-archive over delete when unsure.
- Operate only inside the directory the user named.
