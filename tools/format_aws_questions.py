import re
import os

def format_questions(input_file, output_file):
    """
    Parses and formats AWS practice questions from a text file.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Split by question type, keeping the delimiter
    question_blocks = re.split(r'(单选题|多选题)', content)
    
    formatted_lines = []
    question_counter = 1
    
    # The first element is text before the first delimiter, which we can probably ignore.
    # The rest are pairs of (delimiter, question_text).
    for i in range(1, len(question_blocks), 2):
        question_type = question_blocks[i].strip()
        raw_text = question_blocks[i+1]

        # Clean the text by removing the noisy metadata part and any repeated question text.
        # The metadata seems to follow the answer.
        main_part = re.split(r'正确率', raw_text)[0]

        # Extract the answer which is at the end of the main_part
        answer_match = re.search(r'\s*([A-Z](?:,[A-Z])*)\s*$', main_part)
        
        if not answer_match:
            continue

        answer = answer_match.group(1)
        text_without_answer = main_part[:answer_match.start()].strip()

        # Extract the question, which usually ends with '?' or ':'
        question_match = re.search(r'^(.*?[:?])\s*', text_without_answer, re.DOTALL)
        
        if not question_match:
            # As a fallback, take the first sentence.
            parts = text_without_answer.split('.')
            question = parts[0] + '.'
            options_text = '.'.join(parts[1:]).strip()
        else:
            question = question_match.group(1).strip()
            options_text = text_without_answer[question_match.end():].strip()

        # Build the formatted output
        formatted_lines.append(f"Question {question_counter} ({question_type})")
        formatted_lines.append(question)
        formatted_lines.append("\\nOptions:")
        
        # Split options text into sentences and format them as a list
        sentences = re.split(r'(?<=[.?!])\\s+', options_text)
        for sentence in sentences:
            if sentence.strip():
                formatted_lines.append(f"- {sentence.strip()}")

        formatted_lines.append(f"\\nAnswer: {answer}")
        formatted_lines.append("\\n" + "="*80 + "\\n")
        
        question_counter += 1

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\\n'.join(formatted_lines))
        print(f"Processing complete. Formatted file saved to: {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == '__main__':
    # Ensure the script can be run from the workspace root
    # or the tools directory
    if os.path.basename(os.getcwd()) == 'tools':
        os.chdir('..')

    input_path = os.path.join('aws_saa_study', 'AWS Certified Solutions Architect - Associate SAA-C03.txt')
    output_path = os.path.join('aws_saa_study', 'Formatted_AWS_Questions.txt')
    format_questions(input_path, output_path) 