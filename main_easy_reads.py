import paper_downloader
import paper_tuner
import subprocess
import os
import sys

from paper_downloader import download_file, extract_tar, find_largest_tex, ensure_tuning_block
from paper_tuner import set_tuning_values_newfile


def compile_latex_to_pdf(tex_file_path, output_dir=None, max_attempts=4):
    """
    Compiles a LaTeX file to PDF using pdflatex with proper bibliography handling.
    
    Args:
        tex_file_path: Path to the .tex file
        output_dir: Directory to run compilation in (default: same as tex file)
        max_attempts: Number of compilation attempts (for references, etc.)
    
    Returns:
        Path to the generated PDF file, or None if compilation failed
    """
    if output_dir is None:
        output_dir = os.path.dirname(tex_file_path)
    
    tex_filename = os.path.basename(tex_file_path)
    tex_name = os.path.splitext(tex_filename)[0]
    
    # Change to the output directory
    original_dir = os.getcwd()
    os.chdir(output_dir)
    
    try:
        print(f"🔄 Compiling {tex_filename} to PDF...")
        
        # First pass: pdflatex
        print("   Pass 1: pdflatex")
        result1 = subprocess.run([
            'pdflatex', 
            '-interaction=nonstopmode',
            '-output-directory', '.',
            tex_filename
        ], capture_output=True, text=True)
        
        # Second pass: bibtex (if .bib file exists)
        bib_file = tex_name + '.bib'
        if os.path.exists(bib_file):
            print("   Pass 2: bibtex")
            subprocess.run(['bibtex', tex_name], capture_output=True, text=True)
        else:
            print("   Pass 2: No .bib file found, skipping bibtex")
        
        # Third pass: pdflatex (for bibliography)
        print("   Pass 3: pdflatex (bibliography)")
        result3 = subprocess.run([
            'pdflatex', 
            '-interaction=nonstopmode',
            '-output-directory', '.',
            tex_filename
        ], capture_output=True, text=True)
        
        # Fourth pass: pdflatex (final references)
        print("   Pass 4: pdflatex (final references)")
        result4 = subprocess.run([
            'pdflatex', 
            '-interaction=nonstopmode',
            '-output-directory', '.',
            tex_filename
        ], capture_output=True, text=True)
        
        # Check if PDF was created
        pdf_path = os.path.join(output_dir, f"{tex_name}.pdf")
        if os.path.exists(pdf_path):
            # Check for common issues in the log
            log_file = tex_name + '.log'
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
                
                # Check for critical errors
                critical_errors = [
                    'Emergency stop',
                    'Fatal error',
                    '! LaTeX Error:',
                    '! Undefined control sequence',
                    '! Missing number',
                    '! Illegal unit of measure'
                ]
                
                has_critical_errors = any(error in log_content for error in critical_errors)
                
                if has_critical_errors:
                    print("⚠️ PDF generated but contains LaTeX errors")
                    print("   Check the log file for details")
                else:
                    print("✅ PDF successfully generated with minimal issues")
                
                # Check for undefined citations
                if 'undefined citations' in log_content.lower():
                    print("⚠️ Warning: Some citations are undefined (showing as ??)")
                    print("   This is normal for first compilation - run again to fix")
                
                # Check for overfull/underfull boxes
                overfull_count = log_content.count('Overfull \\hbox')
                underfull_count = log_content.count('Underfull \\hbox')
                if overfull_count > 0 or underfull_count > 0:
                    print(f"⚠️ Warning: {overfull_count} overfull and {underfull_count} underfull boxes")
                    print("   This may cause spacing issues in the PDF")
                
            print(f"📄 PDF location: {pdf_path}")
            return pdf_path
        else:
            print("❌ PDF file not found after compilation")
            return None
        
    except FileNotFoundError:
        print("❌ Error: pdflatex not found. Please install LaTeX (e.g., TeX Live, MiKTeX)")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None
    finally:
        # Return to original directory
        os.chdir(original_dir)


# Enter the URL of the paper and the folder to extract to
url = "https://arxiv.org/src/2509.19443"
folder = "unzipped"   # wherever you extracted

tar_path = download_file(url)      # e.g., paper.tar
extract_tar(tar_path, folder)  # extract into ./unzipped

# Find the largest tex file in the unzipped folder
largest_tex = find_largest_tex(folder)

# 1. Insert block (creates chess_easy.tex)
tex_with_block = ensure_tuning_block(largest_tex)

# 2. Edit values (creates chess_easy_easy.tex or you can adapt to overwrite)
new_tex = set_tuning_values_newfile(
    tex_with_block,
    base_font_pt=12,
    baseline_pt=14.4,
    default_fig_width=r"0.9\linewidth",
    caption_size="small",
)

# 3. Compile the tuned LaTeX file to PDF
if new_tex and os.path.exists(new_tex):
    print("🔄 Running initial compilation...")
    pdf_path = compile_latex_to_pdf(new_tex)
    
    if pdf_path:
        print("\n🔄 Running second compilation to fix citations...")
        pdf_path2 = compile_latex_to_pdf(new_tex)
        
        if pdf_path2:
            print(f"\n🎉 Success! Your PDF is ready: {pdf_path2}")
            print("   Citations should now be properly resolved")
        else:
            print(f"\n⚠️ PDF created but may have issues: {pdf_path}")
    else:
        print("❌ PDF compilation failed. Check the error messages above.")
else:
    print("❌ No tuned LaTeX file found to compile.")


