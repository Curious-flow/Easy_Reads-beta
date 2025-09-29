# Easy Reads - ArXiv Paper Processor

A Python tool for downloading ArXiv papers, processing LaTeX files, and generating easy-to-read PDFs with improved formatting.

## Features

- **Paper Download**: Download ArXiv papers from URLs
- **LaTeX Processing**: Extract and process LaTeX files
- **Font Tuning**: Automatically adjust font sizes and spacing for better readability
- **PDF Compilation**: Compile LaTeX to PDF with proper bibliography handling
- **Figure Optimization**: Resize figures for optimal display

## Files

- `main_easy_reads.py` - Main orchestrator script
- `paper_downloader.py` - Handles ArXiv paper downloading and extraction
- `paper_tuner.py` - LaTeX formatting and tuning utilities
- `Saved/` - Contains working versions and backups

## Usage

```bash
python main_easy_reads.py
```

The script will:
1. Download the specified ArXiv paper
2. Extract the LaTeX files
3. Apply formatting improvements
4. Compile to PDF

## Requirements

- Python 3.x
- LaTeX distribution (TeX Live, MiKTeX, etc.)
- Required Python packages: `requests`, `tarfile`

## Configuration

You can modify the following parameters in `main_easy_reads.py`:
- `base_font_pt`: Base font size (default: 12)
- `baseline_pt`: Line spacing (default: 14.4)
- `default_fig_width`: Figure width (default: 0.9\linewidth)
- `caption_size`: Caption font size (default: small)
