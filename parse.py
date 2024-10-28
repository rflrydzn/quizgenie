import json

def parse_and_quiz(json_file="questions.json"):
    """Parses questions from a JSON file, quizzes the user, and checks answers."""
    with open(json_file, "r") as f:
        questions = json.load(f)
    
    score = 0
    for i, q in enumerate(questions, start=1):
        print(f"Question {i}: {q['question']}")
        for option in q["options"]:
            print(f"  {option}")
        
        # Get user's answer
        user_answer = input("Your answer (a, b, c, or d): ").strip().lower()
        
        # Check if the answer is correct
        if user_answer == q["correct_answer"]:
            print("Correct!\n")
            score += 1
        else:
            print(f"Incorrect! The correct answer was: {q['correct_answer']}\n")
    
    # Display final score
    print(f"You got {score} out of {len(questions)} correct.")

def main():
    json_file = "questions.json"
    parse_and_quiz(json_file)

if __name__ == "__main__":
    main()
