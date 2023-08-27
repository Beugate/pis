# app/routes.py
from flask import Flask
import sqlite3
from flask import render_template, request, redirect, url_for, flash
from pony.flask import Pony
from pony.orm import Database, Required, Optional, db_session, commit, get, select,PrimaryKey

app = Flask(__name__)
app.config.update(
    PONY={
        'provider': 'sqlite',
        'filename': 'players.db',
    }
)
pony = Pony(app)
db = Database()
class Players(db.Entity):
    id=PrimaryKey(int,auto = True)
    username=Required(str)
    country=Required(str)
    team=Optional(str)
    region=Required(str)
    role=Required(str)
    rank=Required(str)
db.bind(provider='sqlite', filename='players.db', create_db=True)
db.generate_mapping(create_tables=True)    
# Database connection
def get_db_connection():
    conn = sqlite3.connect('players.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
@db_session
def index():
    conn = get_db_connection()
    players = conn.execute('SELECT * FROM Players').fetchall()
    conn.close()
    return render_template('index.html', players=players)

# Define other routes (create, read, update, delete) here
# app/routes.py
# ... (previous code)

@app.route('/add_player', methods=['GET', 'POST'])
@db_session
def add_player():
    if request.method == 'POST':
        # Get player data from the form
        player_data = (
            request.form['username'],
            request.form['country'],
            request.form['team'],
            request.form['region'],
            request.form['role'],
            request.form['rank'],
        )
        conn = get_db_connection()
        conn.execute('INSERT INTO players (username, country, team, region, role, rank) VALUES (?, ?, ?, ?, ?, ?)', player_data)
        conn.commit()
        conn.close()
        flash('Igrac dodan', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_player.html')

# Define other CRUD routes here
@app.route('/player/<int:player_id>')
@db_session
def view_player(player_id):
    player = Players.get(id=player_id)
    if player:
        return render_template('view_player.html', player=player)
    else:
        flash('Igrac ne postoji', 'error')
        return redirect(url_for('index'))

@app.route('/update_player/<int:player_id>', methods=['GET', 'POST'])
@db_session
def update_player(player_id):
    player = Players.get(id=player_id)
    if player:
        if request.method == 'POST':
            player.username = request.form['username']
            player.country = request.form['country']
            player.team = request.form['team']
            player.region = request.form['region']
            player.role = request.form['role']
            player.rank = request.form['rank']
            commit()
            flash('Igrac ažuriran', 'success')
            return redirect(url_for('view_player', player_id=player.id))
        return render_template('update_player.html', player=player)
    else:
        flash('Igrac ne postoji', 'error')
        return redirect(url_for('index'))
    
@app.route('/delete_player/<int:player_id>', methods=['POST'])
@db_session
def delete_player(player_id):
    player = Players.get(id=player_id)
    if player:
        player.delete()
        commit()
        flash('Igrac izbrisan', 'success')
    else:
        flash('Igrac ne postoji', 'error')
    return redirect(url_for('index'))

@app.route('/data_for_graph')
@db_session
def data_for_graph():
    regions = select(r.region for r in Players)
    region_counts = {region: regions.count(region) for region in regions}
    labels = list(region_counts.keys())
    values = list(region_counts.values())
    return {'labels': labels, 'values': values}


    
if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
    

