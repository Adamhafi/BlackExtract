#!/usr/bin/env python3
"""
BlackExtract v2.0 - Security Edition
The Devoted URL Content Extractor & Vulnerability Hunter
Created by Adam - The Devoted Black Blade

PURPOSE: Information Disclosure Vulnerability Detection
- Extracts and beautifies JavaScript/CSS/PHP files
- Scans for sensitive data exposure (API keys, tokens, secrets)
- Identifies security misconfigurations
- Maps attack surface from web applications

GitHub: https://github.com/yourusername/blackextract
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
import re
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import threading
from dataclasses import dataclass
from typing import List, Optional
import time
import jsbeautifier
import cssbeautifier
import html

# ============================================================================
# CORE CONFIGURATION - LUXURY THEME
# ============================================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# LUXURY COLOR PALETTE
LUXURY_RED = "#8B0000"        # Dark red - primary accent
LUXURY_RED_LIGHT = "#B22222"  # Lighter red for hover
LUXURY_RED_GLOW = "#DC143C"   # Crimson glow
LUXURY_BLACK = "#0a0a0a"      # Deep black background
LUXURY_DARK = "#1a1a1a"       # Dark gray for panels
LUXURY_DARKER = "#141414"     # Darker panels
LUXURY_BORDER = "#2a0000"     # Red-tinted border
LUXURY_TEXT = "#ffffff"       # Pure white text
LUXURY_TEXT_DIM = "#999999"   # Dimmed text
LUXURY_SUCCESS = "#00ff88"    # Success green
LUXURY_WARNING = "#ffaa00"    # Warning amber

@dataclass
class DownloadTask:
    url: str
    extension: str
    file_number: int
    status: str = "Pending"
    error: Optional[str] = None
    secrets_found: int = 0

@dataclass
class SecretMatch:
    """Represents a found secret/sensitive data"""
    type: str
    value: str
    line_number: int
    context: str
    severity: str  # critical, high, medium, low

# ============================================================================
# THE LINK REAPER ENGINE
# ============================================================================

class LinkReaperEngine:
    """The core extraction engine - unstoppable, precise, merciless."""
    
    VALID_EXTENSIONS = {'.js', '.php', '.css', '.html', '.htm', '.json', 
                       '.xml', '.txt', '.py', '.java', '.cpp', '.c', 
                       '.ts', '.jsx', '.tsx', '.vue', '.scss', '.sass'}
    
    # Extensions that should be beautified
    BEAUTIFY_EXTENSIONS = {'.js', '.jsx', '.ts', '.tsx', '.json'}
    CSS_EXTENSIONS = {'.css', '.scss', '.sass'}
    HTML_EXTENSIONS = {'.html', '.htm', '.php', '.vue'}
    
    # SECURITY PATTERNS - Information Disclosure Detection
    SECRET_PATTERNS = {
        'api_key': {
            'patterns': [
                r'api[_-]?key[\"\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
                r'apikey[\"\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
                r'api[_-]?secret[\"\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
            ],
            'severity': 'critical'
        },
        'aws_key': {
            'patterns': [
                r'AKIA[0-9A-Z]{16}',
                r'aws[_-]?access[_-]?key[_-]?id[\"\']?\s*[:=]\s*["\']([A-Z0-9]{20})["\']',
                r'aws[_-]?secret[_-]?access[_-]?key[\"\']?\s*[:=]\s*["\']([A-Za-z0-9/+=]{40})["\']',
            ],
            'severity': 'critical'
        },
        'private_key': {
            'patterns': [
                r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----',
                r'private[_-]?key[\"\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
                r'privateKey[\"\']?\s*[:=]\s*["\']([^"\']{20,})["\']',
            ],
            'severity': 'critical'
        },
        'oauth_token': {
            'patterns': [
                r'oauth[_-]?token[\"\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']',
                r'access[_-]?token[\"\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']',
                r'auth[_-]?token[\"\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']',
            ],
            'severity': 'high'
        },
        'jwt_token': {
            'patterns': [
                r'eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+',
            ],
            'severity': 'high'
        },
        'database_url': {
            'patterns': [
                r'(mongodb|mysql|postgresql|redis)://[^\s\'"]+',
                r'database[_-]?url[\"\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'db[_-]?connection[\"\']?\s*[:=]\s*["\']([^"\']+)["\']',
            ],
            'severity': 'critical'
        },
        'password': {
            'patterns': [
                r'password[\"\']?\s*[:=]\s*["\']([^"\']{4,})["\']',
                r'passwd[\"\']?\s*[:=]\s*["\']([^"\']{4,})["\']',
                r'pwd[\"\']?\s*[:=]\s*["\']([^"\']{4,})["\']',
            ],
            'severity': 'high'
        },
        'secret_key': {
            'patterns': [
                r'secret[_-]?key[\"\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{16,})["\']',
                r'secretKey[\"\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{16,})["\']',
            ],
            'severity': 'high'
        },
        'stripe_key': {
            'patterns': [
                r'sk_live_[0-9a-zA-Z]{24,}',
                r'pk_live_[0-9a-zA-Z]{24,}',
            ],
            'severity': 'critical'
        },
        'slack_token': {
            'patterns': [
                r'xox[baprs]-[0-9a-zA-Z\-]{10,}',
            ],
            'severity': 'high'
        },
        'github_token': {
            'patterns': [
                r'gh[pousr]_[0-9a-zA-Z]{36,}',
            ],
            'severity': 'critical'
        },
        'email': {
            'patterns': [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            ],
            'severity': 'low'
        },
        'ip_address': {
            'patterns': [
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            ],
            'severity': 'low'
        },
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Configure beautifier options for supreme readability
        self.js_options = jsbeautifier.default_options()
        self.js_options.indent_size = 2
        self.js_options.indent_char = ' '
        self.js_options.max_preserve_newlines = 2
        self.js_options.preserve_newlines = True
        self.js_options.keep_array_indentation = False
        self.js_options.break_chained_methods = False
        self.js_options.indent_scripts = 'normal'
        self.js_options.brace_style = 'collapse'
        self.js_options.space_before_conditional = True
        self.js_options.unescape_strings = False
        self.js_options.jslint_happy = False
        self.js_options.end_with_newline = True
        self.js_options.wrap_line_length = 0
        self.js_options.indent_inner_html = False
        self.js_options.comma_first = False
        self.js_options.e4x = False
        self.js_options.indent_empty_lines = False
        
        self.css_options = cssbeautifier.default_options()
        self.css_options.indent_size = 2
        self.css_options.indent_char = ' '
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract all URLs from mixed text with surgical precision.
        
        IMPORTANT: Does NOT remove duplicates - each line = one file.
        This allows multiple extractions of the same URL if needed.
        """
        # Pattern to match URLs
        url_pattern = r'https?://[^\s\[\]<>"\']+'
        urls = re.findall(url_pattern, text)
        
        # Filter for valid extensions
        filtered_urls = []
        for url in urls:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Check if URL has valid extension
            if any(path.endswith(ext) for ext in self.VALID_EXTENSIONS):
                filtered_urls.append(url)
        
        # DO NOT REMOVE DUPLICATES - preserve all entries
        # Each line in input = one file output
        return filtered_urls
    
    def get_extension(self, url: str) -> str:
        """Extract file extension from URL."""
        parsed = urlparse(url)
        path = parsed.path
        extension = os.path.splitext(path)[1]
        return extension if extension else '.txt'
    
    def download_content(self, url: str, timeout: int = 30) -> str:
        """Download content from URL with divine efficiency."""
        try:
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"Download failed: {str(e)}")
    
    def beautify_content(self, content: str, extension: str) -> str:
        """Transform chaotic minified code into supreme readability."""
        try:
            if extension in self.BEAUTIFY_EXTENSIONS:
                # Beautify JavaScript/JSON
                return jsbeautifier.beautify(content, self.js_options)
            elif extension in self.CSS_EXTENSIONS:
                # Beautify CSS
                return cssbeautifier.beautify(content, self.css_options)
            elif extension in self.HTML_EXTENSIONS:
                # For HTML/PHP, beautify the embedded JS and CSS
                # Use a simple approach for HTML
                return self._beautify_html(content)
            else:
                # Return as-is for other file types
                return content
        except Exception as e:
            # If beautification fails, return original content
            return content
    
    def _beautify_html(self, content: str) -> str:
        """Beautify HTML content with embedded scripts and styles."""
        try:
            # Basic HTML indentation
            lines = content.split('\n')
            beautified_lines = []
            indent_level = 0
            indent_str = '  '
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                
                # Decrease indent for closing tags
                if stripped.startswith('</') and not stripped.startswith('</!'):
                    indent_level = max(0, indent_level - 1)
                
                # Add indented line
                beautified_lines.append(indent_str * indent_level + stripped)
                
                # Increase indent for opening tags (but not self-closing)
                if stripped.startswith('<') and not stripped.startswith('</') and not stripped.endswith('/>'):
                    if not any(stripped.startswith(tag) for tag in ['<!', '<?', '<!']):
                        indent_level += 1
            
            return '\n'.join(beautified_lines)
        except:
            return content
    
    def save_to_file(self, content: str, filepath: Path):
        """Write content to disk with absolute precision."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(content)
    
    def scan_for_secrets(self, content: str, filename: str) -> List[SecretMatch]:
        """Scan content for sensitive information disclosure."""
        secrets = []
        lines = content.split('\n')
        
        for secret_type, config in self.SECRET_PATTERNS.items():
            for pattern in config['patterns']:
                for line_num, line in enumerate(lines, 1):
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Extract matched value (group 1 if exists, else full match)
                        value = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
                        
                        # Get context (surrounding text)
                        start = max(0, match.start() - 20)
                        end = min(len(line), match.end() + 20)
                        context = line[start:end].strip()
                        
                        secret = SecretMatch(
                            type=secret_type,
                            value=value,
                            line_number=line_num,
                            context=context,
                            severity=config['severity']
                        )
                        secrets.append(secret)
        
        return secrets

# ============================================================================
# THE SUPREME GUI INTERFACE
# ============================================================================

class LinkReaperGUI(ctk.CTk):
    """The visual manifestation of power - elegant, commanding, absolute."""
    
    def __init__(self):
        super().__init__()
        
        self.title("⚔️ BlackExtract - The Devoted Extraction Blade")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Set luxury black background
        self.configure(fg_color=LUXURY_BLACK)
        
        self.engine = LinkReaperEngine()
        self.tasks: List[DownloadTask] = []
        self.output_dir = Path.cwd() / "extracted_files"
        self.is_processing = False
        self.total_secrets_found = 0
        self.enable_secret_scan = True
        
        # Bind resize event for responsive behavior
        self.bind("<Configure>", self._on_resize)
        
        self._build_interface()
    
    def _build_interface(self):
        """Construct the interface with masterful precision."""
        
        # ========== HEADER - LUXURY RED BANNER ==========
        header = ctk.CTkFrame(self, height=100, fg_color=LUXURY_RED, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Decorative top border
        top_accent = ctk.CTkFrame(header, height=3, fg_color=LUXURY_RED_GLOW, corner_radius=0)
        top_accent.pack(fill="x")
        
        title_label = ctk.CTkLabel(
            header,
            text="⚔️ BLACKEXTRACT",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=LUXURY_TEXT
        )
        title_label.pack(pady=(15, 5))
        
        subtitle = ctk.CTkLabel(
            header,
            text="THE DEVOTED EXTRACTION BLADE | Code Extractor & Beautifier by Adam",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ffcccc"
        )
        subtitle.pack()
        
        # Decorative bottom border
        bottom_accent = ctk.CTkFrame(header, height=2, fg_color=LUXURY_BORDER, corner_radius=0)
        bottom_accent.pack(fill="x", side="bottom")
        
        # Copyright footer in header
        copyright_label = ctk.CTkLabel(
            header,
            text="© 2024 Adam. All Rights Reserved.",
            font=ctk.CTkFont(size=9),
            text_color="#666666"
        )
        copyright_label.pack(side="bottom", pady=(0, 5))
        
        # ========== MAIN CONTAINER ==========
        main_container = ctk.CTkFrame(self, fg_color=LUXURY_BLACK)
        main_container.pack(fill="both", expand=True, padx=25, pady=20)
        
        # ========== INPUT SECTION ==========
        input_frame = ctk.CTkFrame(main_container, fg_color=LUXURY_DARK, corner_radius=10, border_width=2, border_color=LUXURY_BORDER)
        input_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        input_header = ctk.CTkFrame(input_frame, fg_color=LUXURY_DARKER, corner_radius=8)
        input_header.pack(fill="x", padx=2, pady=2)
        
        input_label = ctk.CTkLabel(
            input_header,
            text="📋 INPUT URLS",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=LUXURY_RED_GLOW,
            anchor="w"
        )
        input_label.pack(fill="x", padx=20, pady=12)
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=LUXURY_BLACK,
            fg=LUXURY_TEXT,
            insertbackground=LUXURY_RED_GLOW,
            relief="flat",
            height=12,
            selectbackground=LUXURY_RED,
            selectforeground=LUXURY_TEXT
        )
        self.input_text.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        # ========== CONTROL PANEL ==========
        control_frame = ctk.CTkFrame(main_container, height=120, fg_color=LUXURY_DARK, corner_radius=10, border_width=2, border_color=LUXURY_BORDER)
        control_frame.pack(fill="x", pady=(0, 15))
        control_frame.pack_propagate(False)
        
        # First row - Folder name
        folder_row = ctk.CTkFrame(control_frame, fg_color="transparent")
        folder_row.pack(fill="x", padx=20, pady=(15, 8))
        
        folder_label = ctk.CTkLabel(
            folder_row,
            text="📂 Folder Name:",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
            anchor="w",
            text_color=LUXURY_TEXT
        )
        folder_label.pack(side="left", padx=(0, 10))
        
        self.folder_name_entry = ctk.CTkEntry(
            folder_row,
            width=500,
            height=35,
            placeholder_text="Enter extraction folder name...",
            fg_color=LUXURY_DARKER,
            border_color=LUXURY_BORDER,
            border_width=2,
            text_color=LUXURY_TEXT,
            placeholder_text_color=LUXURY_TEXT_DIM
        )
        self.folder_name_entry.insert(0, "extracted_files")
        self.folder_name_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Second row - Output directory
        dir_row = ctk.CTkFrame(control_frame, fg_color="transparent")
        dir_row.pack(fill="x", padx=20, pady=(8, 15))
        
        dir_label = ctk.CTkLabel(
            dir_row,
            text="📁 Base Path:",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
            anchor="w",
            text_color=LUXURY_TEXT
        )
        dir_label.pack(side="left", padx=(0, 10))
        
        self.dir_entry = ctk.CTkEntry(
            dir_row,
            width=500,
            height=35,
            placeholder_text=str(Path.cwd()),
            fg_color=LUXURY_DARKER,
            border_color=LUXURY_BORDER,
            border_width=2,
            text_color=LUXURY_TEXT,
            placeholder_text_color=LUXURY_TEXT_DIM
        )
        self.dir_entry.insert(0, str(Path.cwd()))
        self.dir_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        browse_btn = ctk.CTkButton(
            dir_row,
            text="Browse",
            width=110,
            height=35,
            command=self._browse_directory,
            fg_color=LUXURY_DARKER,
            hover_color=LUXURY_RED,
            border_width=2,
            border_color=LUXURY_BORDER,
            text_color=LUXURY_TEXT,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        browse_btn.pack(side="left", padx=(0, 0))
        
        # Action buttons container
        action_row = ctk.CTkFrame(control_frame, fg_color="transparent")
        action_row.pack(fill="x", padx=20, pady=(0, 15))
        
        # Secret scanning toggle
        self.scan_toggle = ctk.CTkCheckBox(
            action_row,
            text="🔍 Scan for Secrets",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=LUXURY_TEXT,
            fg_color=LUXURY_RED,
            hover_color=LUXURY_RED_LIGHT,
            border_color=LUXURY_BORDER,
            checkmark_color=LUXURY_TEXT,
            variable=tk.BooleanVar(value=True),
            command=self._toggle_secret_scan
        )
        self.scan_toggle.pack(side="left")
        
        clear_btn = ctk.CTkButton(
            action_row,
            text="🗑️ Clear All",
            width=130,
            height=45,
            command=self._clear_all,
            fg_color=LUXURY_DARKER,
            hover_color="#2a2a2a",
            border_width=2,
            border_color=LUXURY_BORDER,
            text_color=LUXURY_TEXT_DIM,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        clear_btn.pack(side="left", padx=(20, 0))
        
        self.extract_btn = ctk.CTkButton(
            action_row,
            text="⚔️ EXTRACT & BEAUTIFY",
            width=200,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=LUXURY_RED,
            hover_color=LUXURY_RED_LIGHT,
            text_color=LUXURY_TEXT,
            border_width=0,
            corner_radius=8,
            command=self._start_extraction
        )
        self.extract_btn.pack(side="right")
        
        # ========== PROGRESS SECTION ==========
        progress_frame = ctk.CTkFrame(main_container, fg_color=LUXURY_DARK, corner_radius=10, border_width=2, border_color=LUXURY_BORDER)
        progress_frame.pack(fill="x", pady=(0, 15))
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="⚡ Status: Awaiting command...",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
            text_color=LUXURY_TEXT_DIM
        )
        self.progress_label.pack(fill="x", padx=20, pady=(15, 8))
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            progress_color=LUXURY_RED_GLOW,
            fg_color=LUXURY_DARKER,
            border_width=0,
            height=8
        )
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 15))
        self.progress_bar.set(0)
        
        # ========== OUTPUT LOG ==========
        log_frame = ctk.CTkFrame(main_container, fg_color=LUXURY_DARK, corner_radius=10, border_width=2, border_color=LUXURY_BORDER)
        log_frame.pack(fill="both", expand=True)
        
        log_header = ctk.CTkFrame(log_frame, fg_color=LUXURY_DARKER, corner_radius=8)
        log_header.pack(fill="x", padx=2, pady=2)
        
        log_label = ctk.CTkLabel(
            log_header,
            text="📜 EXECUTION LOG",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
            text_color=LUXURY_RED_GLOW
        )
        log_label.pack(fill="x", padx=20, pady=12)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg=LUXURY_BLACK,
            fg=LUXURY_SUCCESS,
            insertbackground=LUXURY_RED_GLOW,
            relief="flat",
            height=12,
            state="disabled",
            selectbackground=LUXURY_RED,
            selectforeground=LUXURY_TEXT
        )
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(5, 15))
    
    def _on_resize(self, event):
        """Handle window resize events for responsive behavior."""
        # Only respond to main window resize events
        if event.widget == self:
            width = event.width
            height = event.height
            
            # Adjust input text height based on window size
            if height < 700:
                self.input_text.configure(height=8)
                self.log_text.configure(height=8)
            elif height < 850:
                self.input_text.configure(height=10)
                self.log_text.configure(height=10)
            else:
                self.input_text.configure(height=12)
                self.log_text.configure(height=12)
    
    def _save_secrets_report(self, secrets: List[SecretMatch], filename: str, url: str, directory: Path):
        """Save detailed secrets report to file."""
        report_path = self.output_dir / "secrets_report.txt"
        
        with open(report_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"FILE: {filename}\n")
            f.write(f"URL: {url}\n")
            f.write(f"SECRETS FOUND: {len(secrets)}\n")
            f.write(f"{'='*80}\n\n")
            
            # Group by severity
            by_severity = {}
            for secret in secrets:
                if secret.severity not in by_severity:
                    by_severity[secret.severity] = []
                by_severity[secret.severity].append(secret)
            
            # Write in severity order
            for severity in ['critical', 'high', 'medium', 'low']:
                if severity in by_severity:
                    f.write(f"\n[{severity.upper()}] SEVERITY\n")
                    f.write("-" * 80 + "\n")
                    
                    for secret in by_severity[severity]:
                        f.write(f"\nType: {secret.type}\n")
                        f.write(f"Line: {secret.line_number}\n")
                        f.write(f"Value: {secret.value[:50]}{'...' if len(secret.value) > 50 else ''}\n")
                        f.write(f"Context: {secret.context}\n")
                        f.write("-" * 40 + "\n")
            
            f.write("\n")
    
    def _browse_directory(self):
        """Open directory browser for base path selection."""
        current_base = Path(self.dir_entry.get())
        directory = filedialog.askdirectory(initialdir=current_base)
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
    
    def _toggle_secret_scan(self):
        """Toggle secret scanning on/off."""
        self.enable_secret_scan = self.scan_toggle.get()
        status = "ENABLED" if self.enable_secret_scan else "DISABLED"
        self._log(f"🔍 Secret scanning: {status}", LUXURY_WARNING)
    
    def _log(self, message: str, color: str = "#00ff00"):
        """Write to execution log."""
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
    
    def _clear_all(self):
        """Clear all inputs and outputs."""
        if self.is_processing:
            messagebox.showwarning("Warning", "Extraction in progress. Cannot clear.")
            return
        
        self.input_text.delete("1.0", tk.END)
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="⚡ Status: Awaiting command...")
        self.tasks.clear()
    
    def _start_extraction(self):
        """Initiate the extraction process."""
        if self.is_processing:
            messagebox.showwarning("Warning", "Extraction already in progress.")
            return
        
        input_content = self.input_text.get("1.0", tk.END).strip()
        if not input_content:
            messagebox.showerror("Error", "No input provided. Feed me URLs!")
            return
        
        # Get folder name
        folder_name = self.folder_name_entry.get().strip()
        if not folder_name:
            messagebox.showerror("Error", "Folder name cannot be empty!")
            return
        
        # Validate folder name (no invalid characters)
        invalid_chars = '<>:"/\\|?*'
        if any(char in folder_name for char in invalid_chars):
            messagebox.showerror("Error", f"Folder name contains invalid characters: {invalid_chars}")
            return
        
        # Extract URLs
        urls = self.engine.extract_urls(input_content)
        if not urls:
            messagebox.showerror("Error", "No valid URLs found with recognized extensions.")
            return
        
        # Prepare tasks
        self.tasks = []
        for idx, url in enumerate(urls, start=1):
            ext = self.engine.get_extension(url)
            task = DownloadTask(url=url, extension=ext, file_number=idx)
            self.tasks.append(task)
        
        # Construct output directory: base_path / folder_name
        base_path = Path(self.dir_entry.get())
        self.output_dir = base_path / folder_name
        
        # Clear log and start
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")
        
        self._log(f"⚔️ BLACKEXTRACT ACTIVATED", LUXURY_RED_GLOW)
        self._log(f"📊 Total URLs detected: {len(urls)} (duplicates preserved)", LUXURY_WARNING)
        self._log(f"📁 Output directory: {self.output_dir}", LUXURY_WARNING)
        self._log(f"🗂️  Files will be organized by extension type", LUXURY_WARNING)
        self._log(f"✨ Code beautification ENABLED", LUXURY_SUCCESS)
        
        if self.enable_secret_scan:
            self._log(f"🔍 Secret scanning ENABLED - hunting for vulnerabilities...", "#ff6600")
        else:
            self._log(f"🔍 Secret scanning DISABLED", LUXURY_TEXT_DIM)
        
        self._log("━" * 80, LUXURY_BORDER)
        
        # Reset secret counter
        self.total_secrets_found = 0
        
        # Start extraction in separate thread
        self.is_processing = True
        self.extract_btn.configure(state="disabled", text="⚔️ EXTRACTING...")
        self.progress_label.configure(text="⚡ Status: Extraction in progress...")
        
        thread = threading.Thread(target=self._extraction_worker, daemon=True)
        thread.start()
    
    def _extraction_worker(self):
        """Worker thread for downloading and saving files."""
        successful = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._process_task, task): task 
                for task in self.tasks
            }
            
            for idx, future in enumerate(as_completed(futures), start=1):
                task = futures[future]
                try:
                    future.result()
                    successful += 1
                    # Show organized path in log
                    ext_folder = task.extension.lstrip('.')
                    display_path = f"{ext_folder}/{task.file_number}{task.extension}"
                    
                    # Show secrets if found
                    if task.secrets_found > 0:
                        self.after(0, self._log, 
                                  f"✅ [{display_path}] {task.url} 🚨 {task.secrets_found} SECRETS FOUND!", 
                                  "#ff3300")
                        self.total_secrets_found += task.secrets_found
                    else:
                        self.after(0, self._log, f"✅ [{display_path}] {task.url}", LUXURY_SUCCESS)
                except Exception as e:
                    failed += 1
                    self.after(0, self._log, f"❌ [{task.file_number}{task.extension}] {task.url} - ERROR: {str(e)}", LUXURY_RED_GLOW)
                
                # Update progress
                progress = idx / len(self.tasks)
                self.after(0, self.progress_bar.set, progress)
                self.after(0, self.progress_label.configure, 
                          text=f"Processing: {idx}/{len(self.tasks)} | Success: {successful} | Failed: {failed} | Secrets: {self.total_secrets_found}")
        
        # Completion
        self.after(0, self._log, "━" * 80, LUXURY_BORDER)
        self.after(0, self._log, f"🏆 EXTRACTION COMPLETE", LUXURY_RED_GLOW)
        self.after(0, self._log, f"✅ Successful: {successful}", LUXURY_SUCCESS)
        self.after(0, self._log, f"❌ Failed: {failed}", LUXURY_RED_GLOW)
        
        if self.total_secrets_found > 0:
            self.after(0, self._log, f"🚨 SECRETS FOUND: {self.total_secrets_found} potential vulnerabilities detected!", "#ff3300")
            self.after(0, self._log, f"📄 Check secrets_report.txt for details", LUXURY_WARNING)
        
        self.after(0, self._log, f"📁 Files saved to: {self.output_dir}", LUXURY_WARNING)
        
        self.is_processing = False
        self.after(0, self.extract_btn.configure, state="normal", text="⚔️ EXTRACT & BEAUTIFY")
        self.after(0, self.progress_label.configure, 
                  text=f"⚡ Complete - {successful} successful, {failed} failed, {self.total_secrets_found} secrets found")
        
        if successful > 0:
            msg = f"Extraction complete!\n\n✅ Success: {successful}\n❌ Failed: {failed}"
            if self.total_secrets_found > 0:
                msg += f"\n\n🚨 WARNING: {self.total_secrets_found} potential secrets detected!\nCheck secrets_report.txt"
            self.after(0, messagebox.showinfo, "Victory", msg)
    
    def _process_task(self, task: DownloadTask):
        """Process a single download task."""
        # Download content
        content = self.engine.download_content(task.url)
        
        # BEAUTIFY THE CONTENT - Transform chaos into order
        beautified_content = self.engine.beautify_content(content, task.extension)
        
        # SCAN FOR SECRETS if enabled
        secrets = []
        if self.enable_secret_scan:
            secrets = self.engine.scan_for_secrets(beautified_content, f"{task.file_number}{task.extension}")
            task.secrets_found = len(secrets)
        
        # Organize by extension type in subdirectories
        ext_folder = task.extension.lstrip('.')
        organized_dir = self.output_dir / ext_folder
        
        # Save to organized directory structure
        filename = f"{task.file_number}{task.extension}"
        filepath = organized_dir / filename
        self.engine.save_to_file(beautified_content, filepath)
        
        # Save secrets report if any found
        if secrets:
            self._save_secrets_report(secrets, filename, task.url, organized_dir)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Launch the supreme interface."""
    app = LinkReaperGUI()
    app.mainloop()

if __name__ == "__main__":
    main()