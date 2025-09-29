import requests
import os
import tarfile
import shutil
from typing import Optional
import re

def download_file(url, save_as=None):

    '''
    Downloads a file from a URL and saves it to a local path.
    If `save_as` is not provided, the filename is inferred from the URL or headers.
    '''

    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Try filename from Content-Disposition header
    if save_as is None:
        cd = response.headers.get("content-disposition")
        if cd and "filename=" in cd:
            save_as = cd.split("filename=")[-1].strip().strip('"')
        else:
            save_as = os.path.basename(url) or "downloaded_file"

    # Save to disk
    with open(save_as, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Downloaded: {save_as}")
    return save_as



def extract_tar(filename, extract_to="."):

    '''
    Extracts a tar file to a specified directory.
    '''

    with tarfile.open(filename, "r:*") as tar:  # r:* auto-detects compression (.gz, .bz2, .xz, or plain .tar)
        tar.extractall(path=extract_to)
        print(f"📂 Extracted {len(tar.getnames())} files to '{os.path.abspath(extract_to)}'")


def find_largest_tex(root_folder):

    """
    Finds the largest .tex file in a root folder and its subfolders.
    """


    largest_file = None
    largest_size = -1

    for dirpath, _, filenames in os.walk(root_folder):
        for f in filenames:
            if f.endswith(".tex"):
                path = os.path.join(dirpath, f)
                size = os.path.getsize(path)
                if size > largest_size:
                    largest_size = size
                    largest_file = path

    if largest_file:
        print(f"📄 Largest .tex file Found is: {largest_file} ({largest_size/1024:.2f} KB)")
    else:
        print("⚠️ No .tex files found")

    return largest_file

############################## Works Fine till Above #####################################
##########################################################################################


TUNING_BLOCK = r"""
% === BEGIN AUTO FONT/FIG TUNING (inserted by script) =========================
\newcommand{\BaseFontSizePt}{12}
\newcommand{\BaseBaselineSkipPt}{14.4}
\newcommand{\DefaultFigureWidth}{0.9\linewidth}
\newcommand{\CaptionSize}{small}

\usepackage{graphicx}
\usepackage{caption}
\usepackage{etoolbox}

% Apply figure width + caption settings at begin document
\AtBeginDocument{%
  \setkeys{Gin}{width=\DefaultFigureWidth}
  \captionsetup{font=\CaptionSize, labelfont=bf}
}

% === EASY_READS forced font override =================
\makeatletter
\renewcommand\normalsize{%
   \@setfontsize\normalsize{\BaseFontSizePt}{\BaseBaselineSkipPt}%
}
\normalsize
\makeatother
% =====================================================
% === END AUTO FONT/FIG TUNING ================================================
""".lstrip("\n")

def ensure_tuning_block(tex_path: str) -> str:
    """
    Ensures the tuning block exists in the .tex file.
    Creates a new file with _easy suffix if added.
    """
    with open(tex_path, "r", encoding="utf-8", errors="ignore") as f:
        tex = f.read()

    if "BEGIN AUTO FONT/FIG TUNING" in tex:
        print("ℹ️ Tuning block already present")
        return tex_path

    # Insert after \documentclass if found, else prepend
    m = re.search(r"\\documentclass(?:\[[^\]]*\])?\{[^\}]+\}", tex)
    if m:
        new_tex = tex[: m.end()] + "\n" + TUNING_BLOCK + "\n" + tex[m.end():]
    else:
        new_tex = TUNING_BLOCK + "\n" + tex

    root, ext = os.path.splitext(tex_path)
    new_path = root + "_easy" + ext

    with open(new_path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(new_tex)

    print(f"✅ Inserted tuning block into new file: {new_path}")
    return new_path