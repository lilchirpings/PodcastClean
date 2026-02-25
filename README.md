# 🔇 PodcastClean

Automatically detect and censor swearing in podcast audio files using local AI. No uploads, no subscription, completely free.

---

## Features

- 🔔 **Bleep** — replace swearing with a soft tone
- 🔇 **Mute** — silence the word completely
- ✂️ **Cut Out** — remove the audio entirely, making the episode shorter
- Runs fully offline using OpenAI Whisper
- GPU accelerated (NVIDIA)
- Generates a transcript report with timestamps and obfuscated censored words
- Custom word list support

---

## Requirements

- Windows 10/11
- Python 3.11 (not 3.12, not 3.14 — see note below)
- NVIDIA GPU recommended (CPU works but is much slower)

---

## Installation

### Step 1 — Install Python 3.11

**Important: You must use Python 3.11 specifically.**

- Python 3.12+ breaks some dependencies
- Python 3.14 removed the `audioop` module which pydub requires

Download Python 3.11 from:
👉 https://www.python.org/downloads/release/python-3119/

During install, check **"Add Python to PATH"**.

Confirm it installed correctly:
```
py -3.11 --version
```
Should print `Python 3.11.x`.

---

### Step 2 — Install ffmpeg

ffmpeg is required to read and write audio files:

```
winget install ffmpeg
```

Restart your Command Prompt afterwards, then confirm:
```
ffmpeg -version
```

---

### Step 3 *(optional)* — Install CUDA Toolkit (NVIDIA GPU only)

> **Skip this step if you don't have an NVIDIA GPU.** The app works on CPU — it's just slower.

> ⚠️ **Order matters!** The CUDA Toolkit must be installed **before** PyTorch (Step 5). If you install PyTorch first, it won't detect your GPU and you'll have to uninstall and reinstall PyTorch with `--force-reinstall` to fix it. Following the steps in order avoids this.

1. Download CUDA Toolkit 12.1:
   👉 https://developer.nvidia.com/cuda-12-1-0-download-archive
2. Select: Windows → x86_64 → Local Installer
3. Run the installer (click through defaults, ~5 mins)

   Note: Items like "Nsight for Visual Studio" may show as Not Installed — this is fine.

---

### Step 4 — Install Python packages

If pip isn't working, run this first:
```
py -3.11 -m ensurepip --upgrade
```

Install all required packages:
```
py -3.11 -m pip install customtkinter openai-whisper pydub numpy pillow mutagen
```

If packages fail to download, add trusted hosts:
```
py -3.11 -m pip install customtkinter openai-whisper pydub numpy pillow mutagen --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

---

### Step 5 — Install PyTorch

> ⚠️ If you have an NVIDIA GPU, make sure you completed Step 3 **before** this step. Installing PyTorch without the CUDA Toolkit already present means PyTorch won't detect your GPU, and you'll need to reinstall it.

**If you completed Step 3** (NVIDIA GPU with CUDA Toolkit installed):
```
py -3.11 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Verify your GPU is detected:
```
py -3.11 -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda)"
```
Should print `True` and `12.1`.

**If you skipped Step 3** (no NVIDIA GPU, or CPU-only):
```
py -3.11 -m pip install torch
```

---

### Step 6 *(optional)* — Install Triton

Without this you may see a warning about Triton kernels falling back to a slower implementation. It doesn't affect results, just performance.

```
py -3.11 -m pip install triton-windows
```

---

### Step 7 *(optional)* — Drag and Drop support

```
py -3.11 -m pip install tkinterdnd2
```

Without this the app still works fine — just use the click-to-browse button instead.

---

## Running the App

Double-click **`PodcastClean.bat`** — it automatically finds your Python 3.11 installation.

Or from Command Prompt:
```
py -3.11 podcast_clean_ui.py
```

---

## First Run

The first time you process a file, Whisper downloads the AI model:

| Model | Size | Notes |
|-------|------|-------|
| Tiny | ~75MB | Fastest, least accurate |
| Base | ~140MB | Recommended — good balance |
| Small | ~460MB | More accurate, slower |
| Medium | ~1.4GB | Most accurate, slowest |

Downloaded once and cached — no repeated downloads.

---

## Output Files

After processing, two files are saved next to your original audio:

- `filename-clean.mp3` — censored audio, exported at the same bitrate as the original
- `filename-report.txt` — full transcript with obfuscated censored words, timestamps, and context

---

## Troubleshooting

**`No module named 'customtkinter'`**
Use `py -3.11` explicitly, or use the `PodcastClean.bat` launcher.

**`No module named 'pip'`**
```
py -3.11 -m ensurepip --upgrade
```

**`Couldn't find ffmpeg`**
```
winget install ffmpeg
```
Then restart your terminal.

**`No module named 'PIL'`**
```
py -3.11 -m pip install pillow
```

**`torch.cuda.is_available()` returns `False`**
Make sure you installed the CUDA Toolkit (Step 3) before PyTorch (Step 5). If you installed them in the wrong order, reinstall PyTorch:
```
py -3.11 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --force-reinstall
```

**"Failed to launch Triton kernels" warning**
Install Triton (Step 6). If it persists, make sure the CUDA Toolkit is installed (Step 3) and reinstall PyTorch.

**Processing is very slow**
You're on CPU. Follow Steps 3 and 5 to enable GPU acceleration.

**False positives — innocent words being censored**
Some short words (`god`, `hell`, `jesus`, `lord`) are included to catch religious oaths.

Use the **Filter religious words** toggle in the app to disable those matches.

Advanced: built-in word lists are stored in encoded form in `podcast_clean_ui.py` as `_CURSE_WORDS_B64` and `_RELIGIOUS_WORDS_B64`.

---

## License

MIT
