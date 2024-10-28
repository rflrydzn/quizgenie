from flask import Flask, render_template, request, redirect, url_for
import subprocess
import json
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'

# Route to upload file and specify number of questions
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Save the uploaded file
        uploaded_file = request.files['file']
        num_items = request.form['num_items']
        question_type = request.form['question_type']  # Capture question type
        
        # Save file to the uploads folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
        
        # Run main.py with question type as an additional argument
        subprocess.run([
            '/Library/Frameworks/Python.framework/Versions/3.12/bin/python3', 
            'main.py', 
            file_path, 
            str(num_items),
            question_type  # Pass question type to main.py
        ])

        return redirect(url_for('quiz'))
    return render_template('index.html')

# Route to display and answer quiz questions
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Collect answers submitted by the user
        user_answers = request.form.to_dict()
        
        # Read the questions from questions.json
        with open('questions.json', 'r') as f:
            questions = json.load(f)
        
        # Validate answers and calculate score
        score = 0
        results = []
        for i, question in enumerate(questions):
            correct_answer_letter = question['correct_answer']
            user_answer_letter = user_answers.get(f'question_{i+1}')

            # Convert answer letters to index for full text
            correct_answer_index = ord(correct_answer_letter) - ord('a')
            user_answer_index = ord(user_answer_letter) - ord('a') if user_answer_letter else None

            # Extract the full text of the options
            correct_answer_text = question['options'][correct_answer_index] if correct_answer_index is not None else ""
            user_answer_text = question['options'][user_answer_index] if user_answer_index is not None else "No answer selected"

            # Include explanation
            explanation_text = question['explanation']  # Get the explanation from the question data

            is_correct = (user_answer_letter == correct_answer_letter)
            results.append({
                'question': question['question'],
                'options': question['options'],
                'correct_answer': correct_answer_text,  # Only full text of the correct answer
                'user_answer': user_answer_text,         # Only full text of the user's answer
                'explanation': explanation_text,         # Include explanation here
                'is_correct': is_correct
            })
            score += is_correct

        return render_template('result.html', results=results, score=score, total=len(questions))
    
    # Load and display the questions for the quiz, adding an index for each question
    with open('questions.json', 'r') as f:
        questions = json.load(f)
        for idx, question in enumerate(questions, start=1):
            question['index'] = idx  # Adding an index to each question

    return render_template('quiz.html', questions=questions)

if __name__ == '__main__':
    app.run(debug=True)
