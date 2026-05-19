# 🚀 MonScripts

A lightweight, human-readable scripting language designed to be even easier to learn than Python. MonScripts eliminates complex bracket spacing and indentation rules, allowing you to code using intuitive abbreviations or pure emojis.

## 🌟 Features
- **Zero Indentation Stress:** No structural whitespace or indentation errors.
- **Emoji Support:** Write fully executable code using your favorite symbols.
- **Ultra Lightweight:** Runs instantly inside a fast, isolated Python interpreter pipeline.

## 🗺️ Syntax Mapping

| Standard | Short | Emoji | Description |
| :--- | :--- | :--- | :--- |
| `set` | `s` | ✏️ | Creates or updates a variable |
| `say` | `p` | 🗣️ | Outputs text or data to the screen |
| `if` | `chk` | 🤔 | Begins a conditional check block |
| `else` | `alt` | 🤷 | Executes fallback logic if conditions fail |
| `end` | `en` | 🛑 | Closes out an active conditional block |

## 💻 Code Example

```text
✏️ wallet = 50
✏️ cost = 30
set balance = wallet - cost

🤔 balance > 10
    🗣️ "You have plenty of funds left!"
🤷
    p "Warning: Low balance."
🛑
