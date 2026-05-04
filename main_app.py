from flask import Flask, render_template, request
from markupsafe import Markup
import requests
import netflix
import instagram
import grammarly
import duolingo
import re
import json
app = Flask(__name__)
@app.route("/")
def hellow_world():
    return render_template("main_page_index.html")
@app.route("/netflix", methods = ["GET"])
def netflix_page():
    if request.method == "GET":
        return render_template("netflix_index.html")
@app.route("/netflixSubmit", methods = ["POST", "GET"])
def netflix_submit():
    if request.method == "POST":
        analysis = netflix.call("netflix_data.json", request.form["type"])
        analysis = analysis.replace("html", "")
        analysis = analysis.replace("```", "")
        return render_template("netflixIndexSubmit.html", analysis = analysis)
@app.route("/instagram", methods = ["GET"])
def instagram_page():
    if request.method == "GET":
        return render_template("instagram_index.html")
@app.route("/instagramSubmit", methods = ["POST", "GET"])
def instagram_submit():
    if request.method == "POST":
        imgData = requests.get(request.form["imageURLinput"], headers = {"User-Agent": "Monzilla/5.0"}).content
        with open("static/imageTest.jpg", "wb") as f:
            f.write(imgData)
        caption = instagram.call(request.form["imageURLinput"], request.form["language"], request.form["length"], request.form["hashtags"])
        return render_template("instagram_indexSubmit.html", caption=caption, imageName="static/imageTest.jpg")
@app.route("/grammarly", methods = ["GET"])
def grammarly_page():
    if request.method == "GET":
        return render_template("grammarly_index.html")
@app.route("/grammarlySubmit", methods = ["POST", "GET"])
def grammarly_submit():
    if request.method == "POST":
        raw = grammarly.call(request.form["text"])
        print(raw)
        if isinstance(raw, list):
            raw = "".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in raw
            )
        text = str(raw).strip()
        fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
        if fence:
            text = fence.group(1).strip()
        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found in the response")
        decoder = json.JSONDecoder()
        analysis, _ = decoder.raw_decode(text[start:])
        print(analysis)
        var1 = "<span class='highlight-tooltip' title='could not'>cannot</span>"
        return render_template("grammarly_indexSubmit.html", analysis = analysis, test=var1)
@app.route("/duolingo", methods = ["GET"])
def duolingo_page():
    if request.method == "GET":
        return render_template("duolingo_index.html")
@app.route("/duolingoSubmit", methods = ["POST", "GET"])
def duolingo_submit():
    if request.method == "POST":
        language = request.form.get("language")
        data = duolingo.call(language)
        if data.strip().startswith("```"):
            data = data.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(data)
        print(data)
        return render_template("duolingo_indexSubmit.html", data = data)



# set FLASK_APP=app
# set FLASK_ENV=development
# flask --app app.py --debug run

