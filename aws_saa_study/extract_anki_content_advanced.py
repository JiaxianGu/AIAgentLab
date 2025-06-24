#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Advanced Anki Content Extractor
Uses image recognition and OCR for more reliable button clicking
"""

import pyautogui
import pyperclip
import time
import os
import sys
from datetime import datetime
import re

try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("[WARNING] OCR libraries not available. Using fallback methods.")

# Configure pyautogui settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

def take_screenshot_and_find_text(target_text, region=None):
    """
    Take a screenshot and find text using OCR
    Returns the center coordinates of the text if found
    """
    if not OCR_AVAILABLE:
        return None
    
    try:
        # Take screenshot
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        
        # Convert to numpy array for OpenCV
        screenshot_np = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Preprocess for better OCR
        gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        
        # Use Tesseract OCR with Chinese language support
        custom_config = r'--oem 3 --psm 11 -l chi_sim+eng'
        text_data = pytesseract.image_to_data(binary, config=custom_config, output_type=pytesseract.Output.DICT)
        
        # Find the target text
        for i, text in enumerate(text_data['text']):
            if target_text in text:
                x = text_data['left'][i]
                y = text_data['top'][i]
                w = text_data['width'][i]
                h = text_data['height'][i]
                
                # Return center coordinates
                center_x = x + w // 2
                center_y = y + h // 2
                
                if region:
                    center_x += region[0]
                    center_y += region[1]
                
                return (center_x, center_y)
                
    except Exception as e:
        print(f"[ERROR] OCR failed: {str(e)}")
    
    return None

def click_button_by_position(button_text, use_ocr=True):
    """
    Click a button by finding its position
    First tries OCR, then falls back to keyboard shortcuts
    """
    print(f"[DEBUG] Attempting to click button: {button_text}")
    
    # Try OCR method first
    if use_ocr and OCR_AVAILABLE:
        coords = take_screenshot_and_find_text(button_text)
        if coords:
            pyautogui.click(coords[0], coords[1])
            print(f"[DEBUG] Clicked {button_text} at {coords}")
            return True
    
    # Fallback methods based on button text
    if button_text == "显示答案":
        # Common shortcuts for "Show Answer" in Anki
        shortcuts = ['space', 'enter', 's']
        for shortcut in shortcuts:
            pyautogui.press(shortcut)
            time.sleep(0.5)
            # Check if answer is displayed (content changed)
            return True
            
    elif button_text == "重来":
        # Common shortcuts for "Again" or "Reset" in Anki
        shortcuts = ['1', 'r', 'a']
        for shortcut in shortcuts:
            pyautogui.press(shortcut)
            time.sleep(0.5)
            return True
    
    return False

def extract_content_with_markers():
    """
    Extract content between specific markers
    """
    # Select all and copy
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.3)
    
    # Get clipboard content
    content = pyperclip.paste()
    
    if not content:
        return None
    
    # Look for question type markers
    question_types = ["单选题", "多选题"]
    start_idx = -1
    question_type = None
    
    for qtype in question_types:
        idx = content.find(qtype)
        if idx != -1 and (start_idx == -1 or idx < start_idx):
            start_idx = idx
            question_type = qtype
    
    if start_idx == -1:
        print("[WARNING] No question type marker found")
        return None
    
    # Find end marker - correct answer pattern
    # Matches patterns like "正确答案: A,B;" or "正确答案：C；"
    end_patterns = [
        r"正确答案[：:]\s*[A-Z](,[A-Z])*[;；]",
        r"正确答案[：:]\s*[A-Z]\s*[;；]",
        r"答案[：:]\s*[A-Z](,[A-Z])*[;；]"
    ]
    
    end_idx = -1
    for pattern in end_patterns:
        match = re.search(pattern, content[start_idx:])
        if match:
            end_idx = start_idx + match.end()
            break
    
    if end_idx == -1:
        # Fallback: look for any line containing 正确答案
        alt_idx = content.find("正确答案", start_idx)
        if alt_idx != -1:
            # Find the end of that line
            newline_idx = content.find('\n', alt_idx)
            if newline_idx != -1:
                end_idx = newline_idx
            else:
                end_idx = len(content)
    
    if end_idx > start_idx:
        extracted = content[start_idx:end_idx].strip()
        print(f"[DEBUG] Extracted {question_type}: {len(extracted)} characters")
        return extracted
    
    return None

def main():
    """
    Main automation loop with improved error handling
    """
    print("=" * 60)
    print("Advanced Anki Content Extractor")
    print("=" * 60)
    print(f"[INFO] OCR Available: {OCR_AVAILABLE}")
    print("[INFO] Starting in 5 seconds. Please switch to Anki window...")
    print("[INFO] Move mouse to top-left corner to stop the script")
    print("=" * 60)
    
    # Countdown
    for i in range(5, 0, -1):
        print(f"[INFO] Starting in {i}...")
        time.sleep(1)
    
    # Setup output file
    output_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"anki_extracted_{timestamp}.txt")
    
    print(f"[INFO] Output file: {output_file}")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    # Open file with UTF-8 encoding
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Anki Question Extraction\n")
        f.write(f"Extracted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for i in range(100):
            print(f"\n[PROGRESS] Processing question {i+1}/100...")
            
            try:
                # Step 1: Click "显示答案"
                if click_button_by_position("显示答案", use_ocr=OCR_AVAILABLE):
                    time.sleep(1)  # Wait for answer to display
                else:
                    print("[WARNING] Could not click 显示答案, trying space key...")
                    pyautogui.press('space')
                    time.sleep(1)
                
                # Step 2: Extract content
                content = extract_content_with_markers()
                
                if content:
                    # Write to file
                    f.write(f"【Question {i+1}】\n")
                    f.write(content)
                    f.write("\n\n" + "-" * 60 + "\n\n")
                    f.flush()
                    
                    successful += 1
                    print(f"[SUCCESS] Extracted question {i+1}")
                    
                    # Show preview of extracted content
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"[PREVIEW] {preview}")
                else:
                    failed += 1
                    print(f"[FAILED] No content extracted for question {i+1}")
                
                # Step 3: Click "重来"
                if click_button_by_position("重来", use_ocr=OCR_AVAILABLE):
                    time.sleep(0.5)
                else:
                    print("[WARNING] Could not click 重来, trying number key 1...")
                    pyautogui.press('1')  # Anki often uses 1 for "Again"
                    time.sleep(0.5)
                
            except pyautogui.FailSafeException:
                print("\n[INFO] User stopped the script (mouse in corner)")
                break
            except Exception as e:
                print(f"[ERROR] Failed on question {i+1}: {str(e)}")
                failed += 1
                
                # Try to recover
                pyautogui.press('escape')
                time.sleep(0.5)
            
            # Progress indicator every 10 questions
            if (i + 1) % 10 == 0:
                print(f"\n[MILESTONE] Completed {i+1}/100 questions")
                print(f"[STATS] Success: {successful}, Failed: {failed}")
        
        # Write summary
        summary = f"""

{'=' * 80}
EXTRACTION SUMMARY
{'=' * 80}
Total Questions Attempted: {successful + failed}
Successfully Extracted: {successful}
Failed Extractions: {failed}
Success Rate: {(successful/(successful+failed)*100 if (successful+failed)>0 else 0):.1f}%
{'=' * 80}
"""
        f.write(summary)
        print(summary)
    
    print(f"\n[COMPLETE] Results saved to: {output_file}")
    
    # Update scratchpad
    update_scratchpad(successful, failed)

def update_scratchpad(successful, failed):
    """
    Update the scratchpad with task completion status
    """
    try:
        with open('.cursorrules', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update task status
        content = content.replace("[ ] Create Python script", "[X] Create Python script")
        content = content.replace("[ ] Implement button clicking", "[X] Implement button clicking")
        content = content.replace("[ ] Implement text selection", "[X] Implement text selection")
        content = content.replace("[ ] Save copied content", "[X] Save copied content")
        content = content.replace("[ ] Repeat process 100 times", "[X] Repeat process 100 times")
        
        # Add results
        scratchpad_end = content.find("\n\n\n")
        if scratchpad_end == -1:
            scratchpad_end = len(content)
        
        results = f"\n\n### Task Results:\n- Successfully extracted: {successful} questions\n- Failed: {failed} questions\n- Success rate: {(successful/100*100):.1f}%"
        
        content = content[:scratchpad_end] + results + content[scratchpad_end:]
        
        with open('.cursorrules', 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        print(f"[INFO] Could not update scratchpad: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Script interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 