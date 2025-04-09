from flask import Flask, jsonify, send_from_directory, request, session
import os

app = Flask(__name__)
app.secret_key = '9da8de4a43bac84723c66d54'

# Define the directory for static files (e.g., HTML, JavaScript, images)
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Frontend/dist")

# Define the endpoint to serve static assets
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)

@app.route('/public/<path:filename>')
def public_files(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'public'), filename)

@app.route('/assets/<path:filename>')
def src_files(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'assets'), filename)

# Define the endpoint to serve the index.html file
@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/game/<uid>')
def game(uid):
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/lobby/<lobby_id>')
def lob(lobby_id):
    return send_from_directory(FRONTEND_DIR, 'index.html')

def run():   
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    run()