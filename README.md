# 🔇 PodcastClean

Automatically detect and censor swearing in podcast audio files using local AI. No uploads, no subscription, completely free.

---

## Features

- 🔔 **Bleep** — replace swearing with a soft tone
- 🔇 **Mute** — silence the word completely
- ✂️ **Cut Out** — remove the audio entirely, making the episode shorter
- Runs fully offline using OpenAI Whisper
- GPU accelerated (NVIDIA)
- Generates a transcript report showing every censored word with timestamps
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

### Step 3 — Install Python packages

```
py -3.11 -m pip install customtkinter openai-whisper pydub numpy pillow mutagen
```

If pip isn't working:
```
py -3.11 -m ensurepip --upgrade
```

If packages fail to download, add trusted hosts:
```
py -3.11 -m pip install customtkinter openai-whisper pydub numpy pillow mutagen --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

---

### Step 4 — Install PyTorch with CUDA (for GPU acceleration)

If you have an NVIDIA GPU:

```
py -3.11 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Verify your GPU is detected:
```
py -3.11 -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda)"
```
Should print `True` and `12.1`.

Without an NVIDIA GPU, install the CPU version instead:
```
py -3.11 -m pip install torch
```

---

### Step 5 — Install CUDA Toolkit (for best GPU performance)

Without this you may see a warning about Triton kernels falling back to a slower implementation.

1. Download CUDA Toolkit 12.1:
   👉 https://developer.nvidia.com/cuda-12-1-0-download-archive
2. Select: Windows → x86_64 → Local Installer
3. Run the installer (click through defaults, ~5 mins)

   Note: Items like "Nsight for Visual Studio" may show as Not Installed — this is fine.

4. Reinstall PyTorch to pick up the new CUDA install:
```
py -3.11 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --force-reinstall
```

5. Install Triton to fully silence the kernel warning:
```
py -3.11 -m pip install triton-windows
```

---

### Step 6 — Optional: Drag and Drop support

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
- `filename-report.txt` — full transcript with every censored word, timestamp, and context

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
Re-run the PyTorch CUDA install from Step 4 with `--force-reinstall`.

**"Failed to launch Triton kernels" warning**
Follow Step 5 fully — install CUDA Toolkit, force-reinstall PyTorch, then install `triton-windows`.

**Processing is very slow**
You're on CPU. Follow Step 4 to enable GPU acceleration.

**False positives — innocent words being censored**
Some short words (`god`, `hell`, `jesus`, `lord`) are included to catch religious oaths. If they trigger too often, edit the `CURSE_WORDS` list at the top of `podcast_clean_ui.py`.

---

## License

MIT
