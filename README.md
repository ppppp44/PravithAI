PravithAI 🤖
Local AI. Your computer. Your conversations.
Version Build Platform Python Ollama

PravithAI is a local AI desktop assistant for Linux,powered by Ollama and built with PySide6.

It runs AI models locally on your computer, giving you a simple desktop interface for chatting with AI without relying on cloud AI services.

Chat with AI, understand images, and keep your conversations stored locally on your computer.

✨ Features
💬 Local AI chatLocal AI chat
🧠 Powered by Ollama
🖼️ Image understanding with a vision model
📚 Designed to work as a school-friendly AI tutor
💾 Automatically saves conversations
🖥️ Native Linux desktop application
🧠 Ollama-powered models
🖼️ Image understanding
📚 School-friendly AI tutor
💾 Local conversation storage
⚙️ First-launch setup wizardFirst-launch setup wizard
📦 Installable .deb package
🖥️ Cross-platform desktop app
📦 Native installers for each platform
🎨 Custom PravithAI interface and brandingCustom PravithAI interface and branding
🤖 Models
PravithAI currently uses:

qwen3:1.7b for fast text conversations
qwen3-vl:4b for image understanding
Model	Purpose
qwen3:1.7b	Fast text conversations
qwen3-vl:4b	Image understanding
The setup wizard automatically checks for Ollama and downloads anychecks for Ollama and helps configure the required models.

📥 Download
Latest Release: v0.1.0
Choose your platform:

Platform	Download
🐧 Linux	Download .deb
🪟 Windows	Download .exe
🍎 macOS	Download .dmg
⬇️ View all releases

📦 Installation
🐧 Linux
Download the latest .deb package from the Releases page..deb package, then run:

Then install it with:

sudo apt install ./PravithAI_0.1.0_amd64.deb
After installation, launchLaunch PravithAI from your Applications menu.

On the first launch, PravithAI will automatically open its setup wizard and configure the required AI components.

The first launch opens the setup wizard.

🪟 Windows
Download and run:

PravithAI.exe
No Python installation is required.

On first launch, PravithAI opens the setup wizard.

If Ollama isn't installed, the wizard provides the official Ollama download page.

🍎 macOS
Download and open:

PravithAI-macOS.dmg
Then launch PravithAI.

No Python installation is required.

On first launch, PravithAI opens the setup wizard.

If Ollama isn't installed, the wizard provides the official Ollama download page.

💻 Requirements
All Platforms
Linux
64-bit Intel or AMD processor
Python is not required for the packaged .deb
Internet connection for the initial Ollama/model setup
64-bit processor
Internet connection for initial setup
Enough free storage for the AI models
Ollama
Recommended
8 GB RAM or more
Modern Intel or AMD CPU
Several GB of free storage
Modern Intel, AMD, or Apple processor
Several GB of available storage
AI performance depends heavily on your CPU, RAM, and available hardware acceleration.

🔐 Privacy
PravithAI is designed around local AI processing.

Normal AI conversations are processed through your locally running Ollama instance rather than a remote AI API.

Saved conversations are stored locally on your computer.

Internet access is required during initial setup to obtain Ollama and the required models.

🧩 How It Works
PravithAI
   │
   ├── PySide6 Desktop UI
   │
   ├── Ollama
   │      ├── Qwen3 1.7B
   │      └── Qwen3-VL 4B
   │
   └── Local AI Responses
Your conversations are stored locally on your computer.

🚀 Releases
Download the latest version from:

GitHub → Releases

Current version:

PravithAI v0.1.0

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
🛠️ Built With
Python
PySide6
Ollama
Qwen3
Qwen3-VL
PyInstaller
Debian packaging
🐍 Python
🎨 PySide6
🦙 Ollama
🧠 Qwen3
👁️ Qwen3-VL
📦 PyInstaller
🐧 Debian packaging
☁️ GitHub Actions
🧪 Build System
PravithAI uses GitHub Actions to build its desktop releases.

Linux
  └── PravithAI_0.1.0_amd64.deb

Windows
  └── PravithAI.exe

macOS
  └── PravithAI-macOS.dmg
Windows and macOS builds are generated automatically using GitHub's hosted runners.

🚀 Project Status
PravithAI v0.1.0

🟢 Linux build 🟢 Windows build 🟢 macOS build 🟢 Cross-platform setup wizard 🟢 Local AI chat 🟢 Vision model support 🟢 Conversation saving

PravithAI is actively being developed.

📜 License
See the repository license for details.

🤖 PravithAI
PravithAI Local AI. Your computer. Your conversations.

⬇️ Download PravithAI · 🐛 Report an Issue · ⭐ GitHub
