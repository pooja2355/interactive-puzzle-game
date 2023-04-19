from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key'

# Initialize the user progress database
conn = sqlite3.connect('puzzle.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS user_progress (id INTEGER PRIMARY KEY, email TEXT, step INTEGER DEFAULT 0)")


conn.commit()
conn.close()

# Define the game steps
game_steps = [
    {'file': 'question_1.html', 'answer': 'coin'},
    {'file': 'question_2.html', 'answer': 'footsteps'},
    {'file': 'question_3.html', 'answer': 'fire'},
    {'file': 'question_4.html', 'answer': 'artichoke'},
    {'file': 'question_5.html', 'answer': 'fire'}
]

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session['email'] = email
        return redirect('/game/1')
    else:
        return render_template('login.html')

@app.route('/game/complete')
def game_complete():
    session.pop('email', None)
    return "Congratulations! You have completed the game."

@app.route('/game/<int:step>', methods=['GET', 'POST'])
def game(step):
    if 'email' not in session:
        return redirect('/')
    
    email = session['email']
    
    if request.method == 'POST':
        answer = request.form['answer']
        print (answer)
        
        # Check if answer is correct
        if answer.lower() == game_steps[step - 1]['answer'].lower(): # Convert correct answer to lowercase
            # Update the user's progress
            conn = sqlite3.connect('puzzle.db')
            c = conn.cursor()
            c.execute("SELECT step FROM user_progress WHERE email=?", (email,))
            data = c.fetchone()
            
            if data:
                c.execute("UPDATE user_progress SET step=? WHERE email=?", (step, email))
            else:
                c.execute("INSERT INTO user_progress (email, step) VALUES (?, ?)", (email, step))
                
            conn.commit()
            conn.close()
            
            # Check if the game is complete
            if step == len(game_steps):
                return redirect(url_for('game_complete'))
            else:
                next_question = game_steps[step]['file']
                return render_template(next_question)
        else:
            question_file = game_steps[step - 1]['file']
            with open(question_file, 'r') as f:
              data = f.read().split('\n')
              question = data[0].strip()
        
            correct_answer = game_steps[step - 1]['answer']
            return render_template('question.html', step=step, question=question, correct_answer=correct_answer, message="Sorry, your answer is incorrect. Please try again.")

    else:
        question_file = game_steps[step - 1]['file']
        return render_template(question_file)

if __name__ == '__main__':
    app.run(debug=True)
