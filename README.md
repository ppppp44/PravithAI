# PravithAI 🤖

**PravithAI** is a local AI desktop assistant for Linux, powered by [Ollama](https://ollama.com/) and built with PySide6.

It runs AI models locally on your computer, giving you a simple desktop interface for chatting with AI without relying on cloud AI services.

## ✨ Features

* 💬 Local AI chat
* 🧠 Powered by Ollama
* 🖼️ Image understanding with a vision model
* 📚 Designed to work as a school-friendly AI tutor
* 💾 Automatically saves conversations
* 🖥️ Native Linux desktop application
* ⚙️ First-launch setup wizard
* 📦 Installable `.deb` package
* 🎨 Custom PravithAI interface and branding

## 🤖 Models

PravithAI currently uses:

* `qwen3:1.7b` for fast text conversations
* `qwen3-vl:4b` for image understanding

The setup wizard automatically checks for Ollama and downloads any required models.

## 📦 Installation

Download the latest `.deb` package from the **Releases** page.

Then install it with:

```bash
sudo apt install ./PravithAI_0.1.0_amd64.deb
```

After installation, launch **PravithAI** from your Applications menu.

On the first launch, PravithAI will automatically open its setup wizard and configure the required AI components.

## 💻 Requirements

* Linux
* 64-bit Intel or AMD processor
* Python is **not required** for the packaged `.deb`
* Internet connection for the initial Ollama/model setup
* Enough storage for the AI models

### Recommended

* 8 GB RAM or more
* Modern Intel or AMD CPU
* Several GB of free storage

## 🧩 How It Works

```text
PravithAI
   │
   ├── PySide6 Desktop UI
   │
   ├── Ollama
   │      ├── Qwen3 1.7B
   │      └── Qwen3-VL 4B
   │
   └── Local AI Responses
```

Your conversations are stored locally on your computer.

## 🚀 Releases

Download the latest version from:

**GitHub → Releases**

Current version:

**PravithAI v0.1.0**

## 🛠️ Built With

* Python
* PySide6
* Ollama
* Qwen3
* Qwen3-VL
* PyInstaller
* Debian packaging

## 📜 License

See the repository license for details.

---

**PravithAI**
*Local AI. Your computer. Your conversations.*
