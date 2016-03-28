from flask import Flask, render_template, request, jsonify
import random
import string

app = Flask(__name__)
app.config['budget'] = "budget.json"


if __name__ == "__main__":
    N = 64
    app.secret_key = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(N))
    app.debug = True
    app.run(host='0.0.0.0', port=987)