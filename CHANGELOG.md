---
title: "Changelog"
lang: en
locale: en-US
language_name: English
translation_key: simple-snake-changelog
classes: wide
author_profile: true
---

## [Unreleased]

### Summary

Fix launching the installed Windows game from the extracted source folder.

### Fixed

- Let `run.cmd` find the default per-user installation when the source has no virtual environment, retain local source and custom installation launches, and explain how to recover when no runtime exists.
- Add Windows launcher regression coverage for runtime selection, paths and arguments containing spaces, missing runtimes, and application exit codes.

## [0.4.1] - 2026-11-27 @ 05:11

### Summary

Check the Windows C++ runtime before installation and explain how to recover from PyTorch DLL loading failures.

### Fixed

- Check that PyTorch's required Microsoft Visual C++ runtime DLLs load during Windows install and upgrade preflight, including read-only checks, with a repair link and retry instructions on failure.
- Document the x64 redistributable prerequisite for installed and source setups, when to reboot, and how to retry a partially completed installation.

## [0.4.0] - 2026-11-27 @ 04:50

## [0.3.0] - 2026-11-27 @ 03:57

### Summary

Make the training chart interactive with an offline Plotly.js view embedded in the desktop window.

### Changed

- Replace Matplotlib with locally bundled Plotly.js 4.1.1 in Qt WebEngine, preserving completed-game scores, cumulative means and session resets while adding hover values, zoom, pan and legend toggles.
- Package chart assets and the Plotly MIT license, remove the Matplotlib dependency, and verify chart rendering during installation.
- Record the approved desktop embedding and offline asset delivery adaptations to the BMForge visualization contract.

### Fixed

- Keep the disposable installation test's version fixture independent of the current application release.

## [0.2.1] - 2026-11-27 @ 03:30

### Summary

Restore the BMForge documentation configuration while preserving the existing page content and URLs.

### Fixed

- Enable English-default multilingual documentation support and apply the single layout, wide content and author profile defaults to pages as well as posts.
- Exclude application source and tooling from the site output and make the dedication image URL baseurl-aware.

## [0.2.0] - 2026-11-27 @ 03:25

### Summary

Port the AI Snake game to a portable Qt desktop application with clear game and learning modules following the pinned BMForge standards. The GitHub Pages documentation now guides players from installation to hands-on reinforcement-learning experiments, and a project-branded script supports publishing releases.

### Fixed

- Website sidebar.
- Correct the website's repository link and logo asset path.

### Changed

- Rewrite the player-facing documentation around Windows/Linux prerequisites, gameplay, training and reading the score chart. Add a guide to editing the existing learning and reward constants, with repeatable experiment suggestions and explicit current limitations.

### Added

- Adapt the release script for Simple Snake, preserving version/codename updates, changelog versioning, feature-to-dev-to-main merges, annotated tags, atomic pushes, and creation of the next feature branch.
- BMForge GitHub Pages site using the shared dark Minimal Mistakes theme, the supplied project logo, English translation metadata, explicit wide layout and author profile on every site page, and a main-only GitHub Actions publishing workflow.
- Website guides preserving the source setup, controls/training, installation lifecycle, development, architecture, and license documentation; restore the original short README linking to the website.

- Display-independent Snake rules and AI training, preserving Loeber's 11 observations, relative actions, network dimensions, replay memory, and rewards. Handle a full board as a win and detach Q-learning targets.
- Domain-grouped constants, immutable game snapshots, an English message catalogue, and atomic best-model saves.
- PySide6 window with human play, AI training on a worker thread, pause/resume, speed control, and embedded Matplotlib score/mean charts. Save record-breaking model weights in the platform application-data directory.
- Pinned CPU dependencies and portable Linux/Windows launch and install/upgrade/uninstall commands adapted from BMForge's installer, with isolated runtime environments and startup verification.
- Tests for game rules, observation order, Bellman targets, checkpoint saves, localization, Qt controls and thread shutdown, plus real offline dependency installation and upgrade/failure cleanup.
- Source/deployment instructions for Linux and Windows, a module/threading guide, and the upstream MIT attribution notice.
- Keep application packages isolated in the app's venv and route worker updates through Qt GUI slots, with cooperative cleanup on application exit.
- BMForge project, constants, localization, installation, and GitHub Pages skills, with bundled references and templates pinned to upstream commit `7554b12a17332876f69d845fa752c4945cf6a3a0`.
- Project-local BMForge manager and lock file for integrity verification and offline update checks.


---

[Documentation index]({{ site.baseurl }}{% link index.md %})
