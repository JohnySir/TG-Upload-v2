# 🚀 TG Upload v2

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**A powerful, modern GUI application for uploading files to Telegram with advanced features and intelligent media handling.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots)

</div>

---

## ✨ Features

### 🎯 Smart Upload Management
- **Flexible File Selection**: Upload individual files or entire folders
- **Dual Upload Modes**: 
  - 📸 **Media Mode**: Send images/videos as compressed media (optimized for viewing)
  - 📄 **Document Mode**: Send files as documents (preserves quality, supports up to 2GB)
- **Auto-Thumbnail Generation**: Automatically generates thumbnails for videos and images
- **Progress Tracking**: Real-time upload progress with speed indicators

### 💬 Telegram Integration
- **Topic Support**: Upload to specific topics within Telegram groups
- **Smart Link Parser**: Automatically extract Chat ID and Topic ID from Telegram links
- **Bot Authentication**: Secure login with API credentials
- **Multi-Chat Support**: Save and switch between different chat configurations

### 🎨 User Experience
- **Modern GUI**: Clean, intuitive interface built with CustomTkinter
- **Caption Templates**: Dynamic caption system with variables:
  - `{filename}` - File name
  - `{size}` - File size
  - Caption helper with quick variable insertion
- **Credential Management**: Auto-save and load your Telegram credentials
- **Detailed Logging**: Track upload status and debug issues easily

### 🛡️ Reliability
- **Smart Error Handling**: 
  - Automatic retry on failures (3 attempts with exponential backoff)
  - FloodWait detection with user-friendly messages
  - PeerIdInvalid hints for troubleshooting
- **Type Detection**: Automatically identifies videos, images, audio files
- **RGBA Support**: Handles PNG images with transparency

---

## 📋 Prerequisites

### Required Software
- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **FFmpeg** - Required for video/audio thumbnail generation
  - Windows: [Download FFmpeg](https://ffmpeg.org/download.html)
  - Linux: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`

### Telegram Requirements
- **Telegram API Credentials** (API ID & API Hash)
  - Get yours at [my.telegram.org/apps](https://my.telegram.org/apps)
- **Bot Token** (for bot-based uploads)
  - Create a bot via [@BotFather](https://t.me/botfather)

---

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/tg-upload-v2.git
cd tg-upload-v2
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify FFmpeg Installation
```bash
ffmpeg -version
```

---

## 🚀 Usage

### Quick Start
```bash
python main.py
```

### Step-by-Step Guide

#### 1️⃣ **Login**
- Enter your **API ID**, **API Hash**, and **Bot Token**
- Click **Login** (credentials are auto-saved for next time)

#### 2️⃣ **Configure Upload**
- **File/Folder**: Select what to upload
- **Chat ID**: Your target chat ID (e.g., `-1001234567890`)
- **Caption**: Customize with variables or use the helper button
- **Upload to Topic** *(optional)*: Enable for topic groups
  - Use the **Parse** button to extract IDs from a Telegram link

#### 3️⃣ **Choose Upload Mode**
- **Unchecked**: Upload as media (compressed)
- **As Document ✓**: Upload as file (preserves quality, supports large files)

#### 4️⃣ **Upload**
- Click **Start Upload**
- Monitor progress in real-time
- Check the log for detailed status

---

## 📸 Screenshots

![SS](https://raw.githubusercontent.com/JohnySir/TG-Upload-v2/refs/heads/main/assets/Screenshot%202025-11-22%20193535.png "SS")

### Main Interface
*Clean, modern interface with all features at your fingertips*

### Caption Helper
*Quick variable insertion for dynamic captions*

### Topic Support
*Easy topic ID extraction from Telegram links*

---

## 🔍 Getting Chat ID & Topic ID

### Method 1: Using Parse Link (Recommended)
1. Right-click on a message in your target chat/topic
2. Select "Copy Link"
3. Click the **Parse** button in TG Upload v2
4. Paste the link - IDs are extracted automatically!

### Method 2: Manual
- **Chat ID**: For groups starting with `-100`, for example: `-1001234567890`
- **Topic ID**: The message thread number (visible in the link)

**Example Link**: `https://t.me/c/1234567890/11053/11054`
- **Chat ID**: `-1001234567890`
- **Topic ID**: `11053`

---

## 🛠️ Configuration

### Supported File Types
- **Videos**: MP4, MKV, AVI, MOV, etc.
- **Images**: JPG, PNG, WebP, GIF, etc.
- **Audio**: MP3, FLAC, WAV, OGG, etc.
- **Documents**: Any file type up to 2GB

### Caption Variables
- `{filename}` - Original file name
- `{size}` - Human-readable file size

**Example**: `{filename} - {size}` → `video.mp4 - 15.2 MB`

---

## 📁 Project Structure

```
tg-upload-v2/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── core/
│   ├── client.py          # Telegram client management
│   ├── config.py          # Configuration handler
│   └── uploader.py        # Upload logic
├── gui/
│   └── app.py             # GUI implementation
└── utils/
    ├── file_utils.py      # File operations
    ├── media_utils.py     # Media processing
    ├── status_utils.py    # Status formatting
    └── system_utils.py    # System operations
```

---

## 🐛 Troubleshooting

### Common Issues

#### ❌ `PeerIdInvalid` Error
**Solution**: Make sure your bot is added to the target chat/group and has permission to send messages.

#### ❌ `FloodWait` Error
**Solution**: You've been rate-limited by Telegram. Wait the specified time (displayed in the error) before trying again.

#### ❌ `PHOTO_SAVE_FILE_INVALID`
**Solution**: Your image exceeds Telegram's photo limits (10MB, 10000x10000px). Check the **As Document** box to upload as a file instead.

#### ❌ FFmpeg Not Found
**Solution**: Install FFmpeg and ensure it's in your system PATH.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💖 Acknowledgments

- Built with [Pyrogram](https://docs.pyrogram.org/) - Modern Telegram MTProto API framework
- UI powered by [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Inspired by the need for a simple, reliable Telegram upload tool


<div align="center">

**Made with ❤️ by the community**

⭐ Star this repo if you find it useful!

</div>
