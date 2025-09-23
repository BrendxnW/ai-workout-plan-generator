from flask import Flask, render_template, request
from src.workout_planner import WorkoutPlanner
import logging

try:
    from src.parse_user_input import ParseInput
except Exception as e:
    ParseInput = None

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate", methods=["GET", "POST"])
def generate():
    data = request.values

    user_text = (data.get("prompt") or "").strip()
    difficulty = (data.get("difficulty") or "").strip().lower()
    num_days_raw = (data.get("num_days") or "").strip()
    if not (user_text or difficulty or num_days_raw):
        return render_template(
            "results.html",
            plan=None,
            difficulty="beginner",
            num_days=None,
            user_text="",
            error="Please enter a prompt or choose settings."
        )

    parsed = ParseInput(user_text).parse()

    if difficulty:
        parsed["difficulty"] = difficulty
    if num_days_raw.isdigit():
        parsed["days"] = int(num_days_raw)

    parsed["difficulty"] = (parsed.get("difficulty") or "beginner").lower()


    wp = WorkoutPlanner(parsed)
    plan = wp.plan_workout()

    return render_template(
        "results.html",
        plan=plan,
        difficulty=parsed.get("difficulty", "beginner"),
        num_days=parsed.get("days"),
        user_text=user_text
    )

'''@app.route("/edit", method=["POST"])
def edit():
    ...'''

if __name__ == "__main__":
    app.run(debug=True)