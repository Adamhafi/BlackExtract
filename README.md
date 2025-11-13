# ⚔️ BlackExtract

**The Devoted Extraction Blade** - A professional URL content extractor and code beautifier with a luxury dark interface.

![Version](https://img.shields.io/badge/version-2.0-darkred)
![Python](https://img.shields.io/badge/python-3.8+-darkred)
![License](https://img.shields.io/badge/license-MIT-darkred)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-darkred)

---

## 🔥 Features

### Core Capabilities
- **🌐 Smart URL Extraction** - Automatically detects and filters URLs from mixed text input
- **✨ Code Beautification** - Transforms minified code into readable, properly formatted output
- **📁 Organized File Structure** - Automatically sorts extracted files by extension type
- **🔄 Duplicate Preservation** - Maintains all URL entries, even duplicates (18 lines = 18 files)
- **⚡ Multi-threaded Downloads** - Concurrent processing for maximum speed (5 parallel workers)
- **🎨 Luxury GUI** - Professional dark red and black interface

### Supported File Types
- **JavaScript**: `.js`, `.jsx`, `.ts`, `.tsx`, `.json`
- **Stylesheets**: `.css`, `.scss`, `.sass`
- **Markup**: `.html`, `.htm`, `.php`, `.vue`
- **Other**: `.xml`, `.txt`, `.py`, `.java`, `.cpp`, `.c`, and more

### Code Beautification
Automatically beautifies:
- **JavaScript/TypeScript** - Proper indentation, brace styling, spacing
- **CSS/SCSS** - Selector formatting, property alignment
- **HTML/PHP** - Tag indentation, nested structure

---

## 📸 Screenshots

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ⚔️ BLACKEXTRACT                             ┃
┃  THE DEVOTED EXTRACTION BLADE                ┃
┃  Code Extractor & Beautifier by Adam         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/blackextract.git
cd blackextract

# Install required packages
pip install -r requirements.txt
```

### Requirements
```
customtkinter>=5.2.0
requests>=2.31.0
jsbeautifier>=1.14.9
cssbeautifier>=1.14.9
```

---

## 💻 Usage

### Quick Start

```bash
python blackextract.py
```

### Step-by-Step Guide

1. **Launch the application**
   ```bash
   python blackextract.py
   ```

2. **Paste your URLs**
   - Input can be pure URLs or mixed text containing URLs
   - Each line will be processed as a separate file
   - Example input:
   ```
   [+] https://example.com/script.js [some_tag]
   [+] https://example.com/styles.css [another_tag]
   ```

3. **Configure output settings**
   - **Folder Name**: Name for the extraction folder (e.g., `my_extraction`)
   - **Base Path**: Where to create the folder (default: current directory)

4. **Click "⚔️ EXTRACT & BEAUTIFY"**
   - Watch real-time progress in the execution log
   - Files are downloaded, beautified, and organized automatically

### Output Structure

```
my_extraction/
├── js/
│   ├── 1.js    ← Beautified JavaScript
│   ├── 2.js
│   └── 5.js
├── css/
│   ├── 3.css   ← Beautified CSS
│   └── 4.css
└── php/
    └── 6.php   ← Beautified PHP
```

---

## 📋 Features in Detail

### 1. Smart URL Detection
- Extracts URLs using advanced regex patterns
- Filters by file extension automatically
- Preserves order and duplicates

### 2. Code Beautification

**Before (Minified):**
```javascript
(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[36720],{44632:function(t){"use strict";function e(t){if(t.length>=255)throw TypeError("Alphabet too long");
```

**After (Beautified):**
```javascript
(self.webpackChunk_N_E = self.webpackChunk_N_E || []).push([
  [36720], {
    44632: function (t) {
      "use strict";
      function e(t) {
        if (t.length >= 255) throw TypeError("Alphabet too long");
        for (var e = new Uint8Array(256), r = 0; r < e.length; r++) e[r] = 255;
```

### 3. Organized File Structure
- Files automatically sorted into extension-based folders
- Sequential numbering (1.js, 2.js, 3.js...)
- Clean, professional organization

### 4. Error Handling
- Graceful failure recovery
- Detailed error messages in log
- Continues processing remaining URLs

---

## ⚙️ Configuration

### Beautification Options
The tool uses optimized settings for maximum readability:
- **Indentation**: 2 spaces
- **Brace Style**: Collapse
- **Line Length**: Unlimited
- **Preserve Newlines**: Yes

### Concurrent Downloads
- Default: 5 parallel workers
- Configurable in code: `ThreadPoolExecutor(max_workers=5)`

### Timeout Settings
- Default request timeout: 30 seconds
- Configurable in code: `download_content(url, timeout=30)`

---

## 🎨 Theme Customization

The luxury red and black theme can be customized by editing these color constants:

```python
LUXURY_RED = "#8B0000"        # Dark red - primary accent
LUXURY_RED_LIGHT = "#B22222"  # Lighter red for hover
LUXURY_RED_GLOW = "#DC143C"   # Crimson glow
LUXURY_BLACK = "#0a0a0a"      # Deep black background
LUXURY_DARK = "#1a1a1a"       # Dark gray for panels
```

---

## 🐛 Troubleshooting

### Common Issues

**"No valid URLs found"**
- Ensure URLs have recognized file extensions
- Check that URLs are complete (include `https://`)

**"Download failed"**
- Verify internet connection
- Some sites may block automated requests
- Try increasing timeout value

**Beautification not working**
- Ensure `jsbeautifier` and `cssbeautifier` are installed
- Check that file has valid syntax

**GUI not displaying correctly**
- Ensure `customtkinter` is properly installed
- Try updating to latest version: `pip install --upgrade customtkinter`

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/blackextract.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python blackextract.py
```

---

## 📝 Changelog

### Version 2.0 (Current)
- ✨ Added code beautification for JS, CSS, HTML
- 🎨 Luxury red/black theme redesign
- 📁 Automatic file organization by extension
- 🔄 Duplicate URL preservation
- ⚡ Multi-threaded downloads
- 📊 Enhanced progress tracking
- 🛡️ Improved error handling

### Version 1.0
- Initial release
- Basic URL extraction
- Sequential file saving

---

## 📜 License

```
MIT License

Copyright (c) 2024 Adam

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👤 Author

**Adam** - *The Devoted Black Blade*

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern GUI
- Uses [jsbeautifier](https://github.com/beautify-web/js-beautify) for JavaScript beautification
- Powered by [Requests](https://requests.readthedocs.io/) for HTTP operations

---

## ⚔️ Support

If you find this tool useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs and issues
- 💡 Suggesting new features
- 🤝 Contributing to the codebase

---

<div align="center">

**⚔️ BlackExtract - The Devoted Extraction Blade ⚔️**

*Forged with precision. Tempered with power.*

Made with ❤️ by Adam

</div>
