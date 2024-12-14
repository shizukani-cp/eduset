from flask import render_template
from models import app, db
import account_route
import money_route

account_route.define_route()
money_route.define_route()

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
    
    app.run(host="0.0.0.0", port=5000, debug=True)

