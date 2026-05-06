from flask import Flask, render_template, request, redirect
from markupsafe import Markup
import requests
import netflix
import instagram
import grammarly
import duolingo
import re
import json
from urllib.parse import urlparse
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
        fence_match = re.search(r"```(?:html)?\s*([\s\S]*?)```", analysis, re.IGNORECASE)
        if fence_match:
            analysis = fence_match.group(1).strip()
        return render_template("netflixIndexSubmit.html", analysis = analysis)
    return redirect('/netflix')
@app.route("/instagram", methods = ["GET"])
def instagram_page():
    if request.method == "GET":
        return render_template("instagram_index.html")
@app.route("/instagramSubmit", methods = ["POST", "GET"])
def instagram_submit():
    if request.method == "POST":
        image_url = request.form["imageURLinput"]
        parsed = urlparse(image_url)
        if parsed.scheme not in ("http", "https"):
            return "Invalid URL scheme", 400
        import socket
        try:
            hostname = parsed.hostname
            ip = socket.gethostbyname(hostname)
        except Exception:
            return "Could not resolve hostname", 400
        import ipaddress
        addr = ipaddress.ip_address(ip)
        if addr.is_private or addr.is_loopback or addr.is_link_local:
            return "Private URLs are not allowed", 403
        imgData = requests.get(image_url, headers = {"User-agent": "Monzilla/5.0"}, timeout = 10).content
        if not imgData[:4] in (b'\xff\xd8\xff\xe0', b'\xff\xd8\xff\xe1', b'\x89PNG', b'GIF8', b'WEBP'):
            return "URL does not point to a valid image", 400
        with open("static/imageTest.jpg", "wb") as f:
            f.write(imgData)
        caption = instagram.call(request.form["imageURLinput"], request.form["language"], request.form["length"], request.form["hashtags"])
        return render_template("instagram_indexSubmit.html", caption=caption, imageName="static/imageTest.jpg")
    return redirect('/instagram')
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
    return redirect('/grammarly')
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
    return redirect('/duolingo')


# set FLASK_APP=app
# set FLASK_ENV=development
# flask --app app.py --debug run

