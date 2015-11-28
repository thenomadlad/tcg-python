from flask import Flask, render_template

app = Flask(__name__)

# config app


# routes
@app.route('/')
def testing_framework():
    return render_template('framework.html')
