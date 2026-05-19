# 🚀 MonScripts

![Build Status](https://img.shields.io/github/actions/workflow/status/credkellar-boop/MonScripts/ci.yml?branch=main&style=flat-square)
![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square)
![Docker Supported](https://img.shields.io/badge/docker-supported-2496ED.svg?style=flat-square&logo=docker)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)

MonScripts is a lightweight, human-readable, and emoji-compatible scripting language designed to make programming accessible and fun. By removing bracket stress and mandatory indentation rules, it offers the ultimate beginner-friendly environment with shorthand codes and emojis.

---

## 🌟 Language Core Features

* **Emoji-Powered Logic:** Code using intuitive symbols like ✏️, 🗣️, and 👂.
* **Zero Syntax Stress:** No strict spacing or indentation rules to cause bugs.
* **Built-in Standard Utilities:** Native systems for time delays (⏱️) and random loops (🎲).

---

## 📁 Project Structure

```text
MonScripts/
├── .github/workflows/
│   └── ci.yml              # Multi-platform build & test pipeline
├── Dockerfile              # Containerized environment setup
├── main.py                 # Core MonScripts engine and interpreter
├── requirements.txt        # Python dependencies (Cryptography, SpeechRecognition, etc.)
├── game.ms                 # Example Script: Number guessing game
├── test.ms                 # Example Script: Hidden database values test
└── README.md               # Project documentation
