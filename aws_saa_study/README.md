# Anki Content Extractor

This tool automates the extraction of questions and answers from the Anki application.

## Setup

1. Activate the Python virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. Install required packages:
   ```powershell
   pip install -r requirements.txt
   ```

3. (Optional) For OCR support, install Tesseract:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add Tesseract to your PATH
   - Download Chinese language data if needed

## Usage

### Basic Version (extract_anki_content.py)
This version uses keyboard shortcuts and simple text extraction:

```powershell
python extract_anki_content.py
```

### Advanced Version (extract_anki_content_advanced.py)
This version includes OCR support for better button detection:

```powershell
python extract_anki_content_advanced.py
```

## How it Works

1. The script will give you 5 seconds to switch to your Anki window
2. It will automatically:
   - Click "显示答案" (Show Answer) button
   - Copy the content from "单选题" or "多选题" to "正确答案: X;"
   - Save the content to a timestamped text file
   - Click "重来" (Again/Reset) button
   - Repeat 100 times

## Controls

- Move your mouse to the top-left corner of the screen to stop the script
- Press Ctrl+C in the terminal to force quit

## Output

The extracted content will be saved to a file named:
- `anki_content_[timestamp].txt` (basic version)
- `anki_extracted_[timestamp].txt` (advanced version)

## Tips

1. Make sure the Anki window is fully visible and not minimized
2. The script works best with default Anki themes
3. If buttons aren't being clicked properly, try using keyboard shortcuts:
   - Space or Enter for "显示答案"
   - 1 or R for "重来"

## Troubleshooting

If the script isn't working properly:
1. Check that all text is selectable in your Anki cards
2. Try adjusting the delays in the script
3. Use the basic version if OCR isn't working
4. Make sure your Anki is in Chinese interface 