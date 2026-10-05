# PravithAI 🤖

### Local AI. Your computer. Your conversations.

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/ppppp44/PravithAI/releases)
[![Build](https://img.shields.io/github/actions/workflow/status/ppppp44/PravithAI/build.yml?label=build)](https://github.com/ppppp44/PravithAI/actions)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-555.svg)](https://github.com/ppppp44/PravithAI/releases)
[![Python](https://img.shields.io/badge/python-3.12+-3776AB.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/powered%20by-Ollama-black.svg)](https://ollama.com/)

**PravithAI** is a local AI desktop assistant powered by [Ollama](https://ollama.com/) and built with PySide6.

Chat with AI, understand images, and keep your conversations stored locally on your computer.

---

## ✨ Features

* 💬 **Local AI chat**
* 🧠 **Ollama-powered models**
* 🖼️ **Image understanding**
* 📚 **School-friendly AI tutor**
* 💾 **Local conversation storage**
* ⚙️ **First-launch setup wizard**
* 🖥️ **Cross-platform desktop app**
* 📦 **Native installers for each platform**
* 🎨 **Custom PravithAI interface and branding**

---

## 🤖 Models

PravithAI currently uses:

| Model         | Purpose                 |
| ------------- | ----------------------- |
| `qwen3:1.7b`  | Fast text conversations |
| `qwen3-vl:4b` | Image understanding     |

The setup wizard checks for Ollama and helps configure the required models.

---

# 📥 Download

## Latest Release: **v0.1.0**

Choose your platform:

| Platform   | Download                                                             |
| ---------- | -------------------------------------------------------------------- |
| 🐧 Linux   | **[Download `.deb`](https://github.com/ppppp44/PravithAI/releases)** |
| 🪟 Windows | **[Download `.exe`](https://github.com/ppppp44/PravithAI/releases)** |
| 🍎 macOS   | **[Download `.dmg`](https://github.com/ppppp44/PravithAI/releases)** |

**[⬇️ View all releases](https://github.com/ppppp44/PravithAI/releases)**

---

# 📦 Installation

### 🐧 Linux

Download the `.deb` package, then run:

```bash
sudo apt install ./PravithAI_0.1.0_amd64.deb
```

Launch **PravithAI** from your Applications menu.

The first launch opens the setup wizard.

### 🪟 Windows

Download and run:

```text
PravithAI.exe
```

No Python installation is required.

On first launch, PravithAI opens the setup wizard.

If Ollama isn't installed, the wizard provides the official Ollama download page.

### 🍎 macOS

Download and open:

```text
PravithAI-macOS.dmg
```

Then launch **PravithAI**.

No Python installation is required.

On first launch, PravithAI opens the setup wizard.

If Ollama isn't installed, the wizard provides the official Ollama download page.

---

# 💻 Requirements

### All Platforms

* 64-bit processor
* Internet connection for initial setup
* Enough free storage for the AI models
* Ollama

### Recommended

* 8 GB RAM or more
* Modern Intel, AMD, or Apple processor
* Several GB of available storage

AI performance depends heavily on your CPU, RAM, and available hardware acceleration.

---

# 🔐 Privacy

PravithAI is designed around local AI processing.

Normal AI conversations are processed through your locally running Ollama instance rather than a remote AI API.

Saved conversations are stored locally on your computer.

Internet access is required during initial setup to obtain Ollama and the required models.

---

# 🧩 How It Works

```text
                         PravithAI
                            │
                 ┌──────────┴──────────┐
                 │                     │
             PySide6 UI          Setup Wizard
                 │                     │
                 └──────────┬──────────┘
                            │
                          Ollama
                            │
               ┌────────────┴────────────┐
               │                         │
          Qwen3 1.7B               Qwen3-VL 4B
          Text model                Vision model
               │                         │
               └────────────┬────────────┘
                            │
                     Local AI responses
```

---

# 🛠️ Built With

* 🐍 Python
* 🎨 PySide6
* 🦙 Ollama
* 🧠 Qwen3
* 👁️ Qwen3-VL
* 📦 PyInstaller
* 🐧 Debian packaging
* ☁️ GitHub Actions

---

# 🧪 Build System

PravithAI uses GitHub Actions to build its desktop releases.

```text
Linux
  └── PravithAI_0.1.0_amd64.deb

Windows
  └── PravithAI.exe

macOS
  └── PravithAI-macOS.dmg
```

Windows and macOS builds are generated automatically using GitHub's hosted runners.

---

# 🚀 Project Status

**PravithAI v0.1.0**

🟢 Linux build
🟢 Windows build
🟢 macOS build
🟢 Cross-platform setup wizard
🟢 Local AI chat
🟢 Vision model support
🟢 Conversation saving

PravithAI is actively being developed.

---

# 📜 License

See the repository license for details.

---

<div align="center">

### 🤖 PravithAI

**Local AI. Your computer. Your conversations.**

[⬇️ Download PravithAI](https://github.com/ppppp44/PravithAI/releases) · [🐛 Report an Issue](https://github.com/ppppp44/PravithAI/issues) · [⭐ GitHub](https://github.com/ppppp44/PravithAI)

</div>
