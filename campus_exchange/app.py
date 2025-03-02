from flask import Flask, render_template

app = Flask(__name__, static_folder="static")

@app.route('/')
def home():
    return render_template('index.html', title='Home')

if __name__ == '__main__':
    app.run(debug=True)
