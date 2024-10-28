import os
import google.generativeai as genai
import json
import re
import sys
import time  # Import time for the `wait_for_file_active` function

# Initialize the Google Gemini API with your API key
genai.configure(api_key="AIzaSyBQaD16PkvnqsVrUcp2a66HTeAlz8JTGJU")  # Replace with your actual API key

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini and returns the file."""
    file = genai.upload_file(path, mime_type=mime_type)
    return file

def wait_for_file_active(file):
    """Waits for the file to be active (processed by Gemini API)."""
    while file.state.name == "PROCESSING":
        time.sleep(10)
        file = genai.get_file(file.name)
    if file.state.name != "ACTIVE":
        raise Exception(f"File {file.name} failed to process")
    return file

def generate_questions(file, num_questions, question_type):
    """Generates questions based on the specified type (Multiple Choice or True/False)"""
    wait_for_file_active(file)
    
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    # Define format instructions based on question type, requesting explanations
    if question_type == "true_false":
        format_instructions = (
            f"Generate {num_questions} true/false questions based on the following format:\n\n"
            "Each question should appear as follows:\n"
            "1. Question text?\n"
            "   a) True\n"
            "   b) False\n"
            "Answer: (answer letter only)\n"
            "Explanation: Provide a brief explanation for the correct answer.\n\n"
            "Please ensure all questions use this format exactly."
        )
    else:  # Default to multiple choice
        format_instructions = (
            f"Generate {num_questions} multiple-choice questions based on the following format:\n\n"
            "Each question should appear as follows:\n"
            "1. Question text?\n"
            "   a) Option 1\n"
            "   b) Option 2\n"
            "   c) Option 3\n"
            "   d) Option 4\n"
            "Answer: (answer letter only)\n"
            "Explanation: Provide a brief explanation for the correct answer.\n\n"
            "Please ensure all questions use this format exactly."
        )

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    file,
                    format_instructions,
                ],
            }
        ]
    )

    response = chat_session.send_message("Generate questions with explanations")
    try:
        question_text = response.candidates[0].content.parts[0].text
        print("Extracted Question Text:\n", question_text)
        return question_text
    except (AttributeError, IndexError) as e:
        print(f"Error extracting question text: {e}")
        return ""

def convert_to_json(text, output_file="questions.json"):
    """Converts structured text of questions, answers, and explanations into JSON format."""
    questions = []
    content = text.strip().split("\n\n")  # Split by double newlines for question blocks
    
    for block in content:
        lines = block.strip().splitlines()
        
        # Extract question line
        question_line = lines[0] if re.match(r"^\d+\.", lines[0]) else None
        if question_line:
            question = question_line.strip()

            # Extract options
            options = [line.strip() for line in lines[1:-2] if re.match(r"^[abcd]\)", line.strip())]
            
            # Extract answer line
            answer_line = lines[-2] if "Answer:" in lines[-2] else None
            if answer_line:
                answer_match = re.search(r"\b([abcd])\b", answer_line)
                answer = answer_match.group(1) if answer_match else None
            
            # Extract explanation line
            explanation_line = lines[-1] if "Explanation:" in lines[-1] else None
            explanation = explanation_line.split("Explanation:")[1].strip() if explanation_line else ""

            # Ensure we only save complete question blocks
            if question and options and answer:
                questions.append({
                    "question": question,
                    "options": options,
                    "correct_answer": answer,
                    "explanation": explanation  # Add explanation here
                })
            else:
                print(f"Skipped incomplete block: {block}")

    # Save to JSON
    with open(output_file, "w") as json_file:
        json.dump(questions, json_file, indent=4)
    print(f"Converted questions saved to {output_file}")

def main():
    # Get file path, number of questions, and question type from command-line arguments
    if len(sys.argv) != 4:
        print("Usage: python main.py <file_path> <num_questions> <question_type>")
        sys.exit(1)

    file_path = sys.argv[1]
    num_questions = int(sys.argv[2])
    question_type = sys.argv[3]

    if not os.path.exists(file_path):
        print("The file path you provided does not exist.")
        return

    # Generate questions and save to JSON
    file = upload_to_gemini(file_path)
    question_text = generate_questions(file, num_questions, question_type)
    convert_to_json(question_text)

if __name__ == "__main__":
    main()
