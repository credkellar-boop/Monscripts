# 🚀 MonScripts

MonScripts is a lightweight, human-readable, and emoji-compatible scripting language designed to make programming accessible and fun. By removing bracket stress and mandatory indentation rules, it offers the ultimate beginner-friendly environment with shorthand codes and emojis.

---

## 🌟 Language Core Features
- **Emoji-Powered Logic:** Code using intuitive symbols like ✏️, 🗣️, and 👂.
- **Zero Syntax Stress:** No strict spacing or indentation rules to cause bugs.
- **Built-in Standard Utilities:** Native systems for time delays (⏱️) and random loops (🎲).

---

## 🗺️ Master Syntax Cheat Sheet

| Core Keyword | Shorthand | Emoji | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `set` | `s` | ✏️ | Creates / Updates a variable | `✏️ energy = 100` |
| `say` | `p` | 🗣️ | Prints text or data to screen | `🗣️ "System Live"` |
| `listen` | `in` | 👂 | Pauses to read keyboard input | `👂 user_input` |
| `loop` | `rp` | 🔁 | Repeats a block a set number of times | `🔁 5` |
| `if` | `chk` | 🤔 | Starts a true/false condition check | `🤔 score > 90` |
| `else` | `alt` | 🤷 | Fallback route for conditional checks | `🤷` |
| `end` | `en` | 🛑 | Closes a loop or conditional block | `🛑` |
| `wait` | `wt` | ⏱️ | Freezes execution for $N$ seconds | `⏱️ 2` |
| `rand` | `rd` | 🎲 | Saves a random number ($1$ to $N$) | `🎲 roll 6` |

---

## 🎮 Code Showcase: `casino.ms`

Save the following text inside a file named `casino.ms` to test your language engine parameters:

```text
🗣️ "=== MonScripts Mobile Casino ==="
🗣️ "Rolling a lucky 6-sided dice..."

⏱️ 2

🎲 result 6
🗣️ "Your roll result:"
🗣️ result

🤔 result > 3
    🗣️ "🎉 You win the high-stakes round!"
🤷
    🗣️ "❌ Low roll. Try your luck again."
🛑
