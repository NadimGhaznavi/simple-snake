# Changelog

## [Unreleased]

### Summary

Port the AI Snake game to a portable Qt desktop application, with clear game and learning modules following the pinned BMForge standards.

### Added

- Display-independent Snake rules and AI training, preserving Loeber's 11 observations, relative actions, network dimensions, replay memory, and rewards. Handle a full board as a win and detach Q-learning targets.
- Domain-grouped constants, immutable game snapshots, an English message catalogue, and atomic best-model saves.
- PySide6 window with human play, AI training on a worker thread, pause/resume, speed control, and embedded Matplotlib score/mean charts. Save record-breaking model weights in the platform application-data directory.
- Pinned CPU dependencies and portable Linux/Windows launch and install/upgrade/uninstall commands adapted from BMForge's installer, with isolated runtime environments and startup verification.
- Tests for game rules, observation order, Bellman targets, checkpoint saves, localization, Qt controls and thread shutdown, plus real offline dependency installation and upgrade/failure cleanup.
- Source/deployment instructions for Linux and Windows, a module/threading guide, and the upstream MIT attribution notice.
- Keep application packages isolated in the app's venv and route worker updates through Qt GUI slots, with cooperative cleanup on application exit.
- BMForge project, constants, localization, installation, and GitHub Pages skills, with bundled references and templates pinned to upstream commit `7554b12a17332876f69d845fa752c4945cf6a3a0`.
- Project-local BMForge manager and lock file for integrity verification and offline update checks.
