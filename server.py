import json
import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')
DB_PATH = os.path.join(os.path.dirname(__file__), 'finance.db')

DEFAULT_STATE = {
    'accounts': [
        {'name': 'BOA Income Deposite', 'type': 'checking', 'balance': 4200},
        {'name': 'BOA Rent and Utility', 'type': 'checking', 'balance': 3400},
        {'name': 'BOA Savings', 'type': 'savings', 'balance': 9000},
        {'name': 'Chase Checking', 'type': 'checking', 'balance': 2800},
        {'name': 'Chase Saving', 'type': 'savings', 'balance': 12000},
        {'name': 'Chase Freedom Flex', 'type': 'credit_card', 'balance': 320},
        {'name': 'BOA Credit Card', 'type': 'credit_card', 'balance': 540},
    ],
    'expenseCategories': ['Housing', 'Groceries', 'Dining', 'Coffee', 'Transportation', 'Utilities', 'Entertainment', 'Health', 'Shopping', 'Travel', 'Subscription'],
    'incomeCategories': ['Salary', 'Freelance', 'Bonus'],
    'investmentAccounts': ['Brokerage', 'ETF Portfolio', 'Retirement'],
    'investmentRecords': [],
    'investmentReturns': [],
    'monthlyExpenseRecords': [],
    'monthlyIncomeRecords': [],
    'fixedRules': [],
}


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS app_state (id INTEGER PRIMARY KEY CHECK(id = 1), data TEXT NOT NULL)')
    row = conn.execute('SELECT data FROM app_state WHERE id = 1').fetchone()
    if row is None:
        conn.execute('INSERT INTO app_state (id, data) VALUES (1, ?)', (json.dumps(DEFAULT_STATE),))
    conn.commit()
    conn.close()


@app.get('/api/health')
def health():
    return jsonify({'ok': True, 'status': 'running'})


@app.get('/api/state')
def get_state():
    conn = get_db_connection()
    row = conn.execute('SELECT data FROM app_state WHERE id = 1').fetchone()
    conn.close()
    if row is None:
        return jsonify(DEFAULT_STATE)
    return jsonify(json.loads(row['data']))


@app.post('/api/state')
def save_state():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({'error': 'State payload is required'}), 400

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO app_state (id, data) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET data = excluded.data',
        (json.dumps(payload),),
    )
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    return send_from_directory('.', path if path else 'index.html')


init_db()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
