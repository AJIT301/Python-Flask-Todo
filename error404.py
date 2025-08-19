from flask import Flask, render_template

app = Flask(__name__)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return 'Home page'

if __name__ == "__main__":
    app.run(debug=False)