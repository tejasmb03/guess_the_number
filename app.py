from flask import Flask, request, jsonify, session, render_template
import os
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_2025'

DIFFICULTIES = {
    'easy': (1, 10, 5),
    'medium': (1, 50, 5),
    'hard': (1, 100, 5),
    'expert': (1, 500, 3)
}

@app.route('/')
def home():
    if 'stats' not in session:
        session['stats'] = {
            'wins': 0,
            'losses': 0,
            'current_streak': 0,
            'best_streak': 0
        }
    return render_template('index.html', stats=session['stats'])

@app.route('/start', methods=['POST'])
def start_game():
    data = request.get_json()
    difficulty = data.get('difficulty', 'easy')
    min_num, max_num, chances = DIFFICULTIES.get(difficulty, (1, 10, 5))
    session['game'] = {
        'number': random.randint(min_num, max_num),
        'chances': chances,
        'range': (min_num, max_num),
        'start_time': datetime.now().timestamp(),
        'last_guess': None
    }
    return jsonify({
        "message": "Game started.",
        "range": f"{min_num}-{max_num}",
        "chances": chances
    })

@app.route('/guess', methods=['POST'])
def guess_number():
    data = request.get_json()
    guess = int(data.get('guess'))
    game = session.get('game', {})
    stats = session.get('stats', {'wins': 0, 'losses': 0, 'current_streak': 0, 'best_streak': 0})

    if not game or game['chances'] <= 0:
        return jsonify({"result": "🛑 Start a new game first!", "stats": stats, "chances_left": 0})

    time_elapsed = int(datetime.now().timestamp() - game['start_time'])
    game['chances'] -= 1
    hint = ""

    if guess == game['number']:
        stats['wins'] += 1
        stats['current_streak'] += 1
        if stats['current_streak'] > stats['best_streak']:
            stats['best_streak'] = stats['current_streak']
        result = f"🎉 Correct! Number was {game['number']} (Time: {time_elapsed}s)"
        game['chances'] = 0
        
    else:
        if game['last_guess'] is not None:
            prev_diff = abs(game['last_guess'] - game['number'])
            curr_diff = abs(guess - game['number'])
            hint = "🔥 Hotter!" if curr_diff < prev_diff else "❄️ Colder!"
        else:
            hint = "⬆️ Higher!" if guess < game['number'] else "⬇️ Lower!"
        game['last_guess'] = guess

        if game['chances'] > 0:
            result = f"❌ Wrong! {hint} {game['chances']} chance(s) left."
            
        else:
            stats['losses'] += 1
            stats['current_streak'] = 0
            result = f"💀 Game Over! Number was {game['number']}"

    session['game'] = game
    session['stats'] = stats

    return jsonify({
        "result": result,
        "stats": stats,
        "chances_left": game['chances'],
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
