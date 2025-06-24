#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Anki Content Extractor
Automates the process of extracting question content from Anki application
"""

import pyautogui
import pyperclip
import time
import os
import sys
from datetime import datetime

# Configure pyautogui settings
pyautogui.FAILSAFE = True  # Move mouse to top-left corner to stop
pyautogui.PAUSE = 0.5  # Pause between commands

def find_and_click_button(button_text, confidence=0.8, timeout=10):
    """
    Find and click a button with specified text
    Returns True if successful, False otherwise
    """
    print(f"[DEBUG] Looking for button: {button_text}")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Try to find the button using image recognition
            # First, we'll try to locate the button on screen
            # Note: This requires the button to be visible
            button_location = pyautogui.locateOnScreen(button_text, confidence=confidence)
            if button_location:
                button_center = pyautogui.center(button_location)
                pyautogui.click(button_center)
                print(f"[DEBUG] Clicked button: {button_text}")
                return True
        except:
            pass
        
        # Alternative method: Click based on text (requires OCR or known positions)
        # For now, we'll use a simpler approach with keyboard shortcuts or known positions
        time.sleep(0.5)
    
    print(f"[ERROR] Could not find button: {button_text}")
    return False

def find_text_and_select_to_end(start_text, end_text):
    """
    Find text on screen and select from start_text to end_text
    """
    print(f"[DEBUG] Trying to select text from '{start_text}' to '{end_text}'")
    
    # Use Ctrl+F to open find dialog
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.5)
    
    # Type the start text
    pyperclip.copy(start_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    # Close find dialog
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # Start selection - hold shift and search for end text
    pyautogui.keyDown('shift')
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.5)
    
    # Clear search box and type end text
    pyautogui.hotkey('ctrl', 'a')
    pyperclip.copy(end_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    # Close find dialog
    pyautogui.press('escape')
    pyautogui.keyUp('shift')
    time.sleep(0.5)
    
    # Copy selected text
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)
    
    return pyperclip.paste()

def extract_content_simple():
    """
    Simplified extraction method using keyboard shortcuts
    """
    # Select all text in the window
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    
    # Copy to clipboard
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)
    
    # Get clipboard content
    content = pyperclip.paste()
    
    # Extract relevant portion
    if "单选题" in content or "多选题" in content:
        start_marker = "单选题" if "单选题" in content else "多选题"
        start_idx = content.find(start_marker)
        
        # Find the end marker (正确答案: followed by answers)
        import re
        end_pattern = r"正确答案[：:]\s*[A-Z,\s]+[;；]"
        end_match = re.search(end_pattern, content[start_idx:])
        
        if start_idx != -1 and end_match:
            end_idx = start_idx + end_match.end()
            extracted = content[start_idx:end_idx]
            print(f"[DEBUG] Extracted {len(extracted)} characters")
            return extracted
    
    print("[WARNING] Could not find expected content markers")
    return content

def main():
    """
    Main automation loop
    """
    print("=" * 50)
    print("Anki Content Extractor")
    print("=" * 50)
    print("[INFO] Starting in 5 seconds. Please switch to Anki window...")
    print("[INFO] Move mouse to top-left corner to stop the script")
    print("=" * 50)
    
    # Give user time to switch to Anki
    for i in range(5, 0, -1):
        print(f"[INFO] Starting in {i}...")
        time.sleep(1)
    
    # Output file setup
    output_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"anki_content_{timestamp}.txt")
    
    print(f"[INFO] Output file: {output_file}")
    
    successful_extractions = 0
    failed_extractions = 0
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Anki Content Extraction - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        for i in range(100):
            print(f"\n[INFO] Processing item {i+1}/100...")
            
            try:
                # Step 1: Click "显示答案" button
                # Using Tab key navigation as a fallback
                print("[DEBUG] Attempting to click '显示答案' button...")
                
                # Try using space or enter key (common shortcuts for primary button)
                pyautogui.press('space')
                time.sleep(1)  # Wait for answer to show
                
                # Step 2: Extract content
                print("[DEBUG] Extracting content...")
                content = extract_content_simple()
                
                if content and len(content) > 10:  # Basic validation
                    # Step 3: Save to file
                    f.write(f"Question {i+1}:\n")
                    f.write(content)
                    f.write("\n\n" + "-" * 40 + "\n\n")
                    f.flush()  # Ensure data is written
                    successful_extractions += 1
                    print(f"[SUCCESS] Extracted content for item {i+1}")
                else:
                    failed_extractions += 1
                    print(f"[WARNING] No valid content extracted for item {i+1}")
                
                # Step 4: Click "重来" button
                print("[DEBUG] Clicking '重来' button...")
                # Try common shortcuts for reset/next
                pyautogui.press('r')  # 'r' for replay/reset
                time.sleep(0.5)
                
                # Alternative: try clicking a specific key combination
                if i % 10 == 0:  # Every 10 items, try alternative method
                    pyautogui.hotkey('ctrl', 'r')  # Refresh/reset
                    time.sleep(1)
                
            except Exception as e:
                print(f"[ERROR] Failed to process item {i+1}: {str(e)}")
                failed_extractions += 1
                
                # Try to recover by pressing escape or clicking somewhere safe
                pyautogui.press('escape')
                time.sleep(0.5)
            
            # Small delay between iterations
            time.sleep(0.5)
        
        # Write summary
        f.write("\n\n" + "=" * 80 + "\n")
        f.write(f"Extraction Summary:\n")
        f.write(f"Total attempts: 100\n")
        f.write(f"Successful: {successful_extractions}\n")
        f.write(f"Failed: {failed_extractions}\n")
        f.write(f"Success rate: {successful_extractions}%\n")
    
    print("\n" + "=" * 50)
    print(f"[INFO] Extraction completed!")
    print(f"[INFO] Successful extractions: {successful_extractions}/100")
    print(f"[INFO] Output saved to: {output_file}")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Script interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        sys.exit(1) 