from dotenv import load_dotenv

load_dotenv()

from flask import render_template
from models import app
import account_route
import money_route
import class_route

account_route.define_route()
money_route.define_route()
class_route.define_route()

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

