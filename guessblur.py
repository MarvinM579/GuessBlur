from flask import Flask, render_template, url_for, session, request, redirect
from random import randint
import pg

db = pg.DB(host="localhost", user="postgres", passwd="rocket", dbname="fiftyfifty")

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_game', methods=['POST'])
def start_game():
    name = request.form.get('name')
    session['name'] = name
    session['points'] = 0
    session['missed'] = 0
    return redirect('/game')


@app.route('/game', methods=['GET', 'POST'])
def number():
    s = randint(1, 2)
    img = db.query('select * from images order by random() limit 1').namedresult()
    return render_template("number.html", s=s, img=img)


@app.route('/selection', methods=['POST', 'GET'])
def selection():
    action = request.args.get('action')
    print "action=" + action
    if action == 'Yes':
        session['points'] = session.get('points', 0) + 1
        return '{"success": True, "points": %d}' % session['points']
    elif action == 'No':
        session['missed'] = session.get('missed') + 1
        if session['missed'] == 3:
            return redirect('/game_over')
        # session.get('points',0) += 0
        return '{"success": False, "points": %d}' % session['points']


@app.route('/game_over')
def game_over():
    return render_template('/game_over.html')


@app.route('/end_game', methods=['POST', 'GET'])
def end_game():
    name = session.get('name')
    score = session.get('points')
    db.insert('scores',
              name=name,
              score=score)
    del session['name']
    return redirect('/')


@app.route('/highscores', methods=['GET'])
def highscores():
    scores = db.query('select * from scores order by score desc limit 10').namedresult()
    return render_template('scores.html', scores=scores)


app.secret_key = 'whaaaaaaa'

if __name__ == '__main__':
    app.run(debug=True)
