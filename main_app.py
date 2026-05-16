from flask import Flask, render_template, request, redirect, flash
import os
import requests
import netflix
import instagram
import grammarly
import duolingo
import re
import json
import importlib
import html
from urllib.parse import urlparse, urljoin
import bleach
import socket
import ipaddress
repair_json = None
def _is_public_ip(ip_address):
    ip = ipaddress.ip_address(ip_address)
    return not (
        ip.is_private or
        ip.is_loopback or
        ip.is_link_local or
        ip.is_reserved or
        ip.is_unspecified
    )
def _repair_llm_json(candidate_json):
    global repair_json
    if repair_json is None:
        try:
            repair_json = importlib.import_module("json_repair").repair_json
        except Exception:
            return None
    return repair_json(candidate_json)
def _extract_replacement_text(correct_value):
    if not isinstance(correct_value, str):
        return ""
    single_quote_match = re.search(r"'([^']+)'", correct_value)
    if single_quote_match:
        return single_quote_match.group(1)
    double_quote_match = re.search(r'"([^"]+)"', correct_value)
    if double_quote_match:
        return double_quote_match.group(1)
    return correct_value
def _find_error_range(base_text, error_obj, cursor):
    if not isinstance(base_text, str) or not isinstance(error_obj, dict):
        return None
    start = error_obj.get("start_char")
    end = error_obj.get("end_char")
    mistake_text = error_obj.get("mistake_text")
    if isinstance(start, int) and isinstance(end, int):
        if cursor <= start < end <= len(base_text):
            segment = base_text[start:end]
            if not isinstance(mistake_text, str) or not mistake_text:
                return (start, end)
            if segment == mistake_text or segment.lower() == mistake_text.lower():
                return (start, end)
    if isinstance(mistake_text, str) and mistake_text:
        found = base_text.find(mistake_text, cursor)
        if found != -1:
            return (found, found + len(mistake_text))
        found = base_text.lower().find(mistake_text.lower(), cursor)
        if found != -1:
            return (found, found + len(mistake_text))
    return None
def _build_mistake_html(base_text, errors):
    if not isinstance(base_text, str) or not isinstance(errors, list):
        return ""
    result = []
    cursor = 0
    ordered_errors = sorted(
        [err for err in errors if isinstance(err, dict)],
        key=lambda err: err.get("start_char", 0),
    )
    for err in ordered_errors:
        error_range = _find_error_range(base_text, err, cursor)
        if error_range is None:
            continue
        start, end = error_range
        result.append(html.escape(base_text[cursor:start]))
        mistake_segment = html.escape(base_text[start:end])
        tooltip = html.escape(str(err.get("correct", "")), quote=True)
        result.append(
            f"<span class='highlight-tooltip-red' title='{tooltip}'>{mistake_segment}</span>"
        )
        cursor = end
    result.append(html.escape(base_text[cursor:]))
    return "".join(result)
def _build_corrected_html(base_text, errors):
    if not isinstance(base_text, str) or not isinstance(errors, list):
        return ""
    result = []
    cursor = 0
    ordered_errors = sorted(
        [err for err in errors if isinstance(err, dict)],
        key=lambda err: err.get("start_char", 0),
    )
    for err in ordered_errors:
        error_range = _find_error_range(base_text, err, cursor)
        if error_range is None:
            continue
        start, end = error_range
        result.append(html.escape(base_text[cursor:start]))
        replacement_text = _extract_replacement_text(err.get("correct", ""))
        if not replacement_text:
            replacement_text = base_text[start:end]
        replacement_text = html.escape(str(replacement_text))
        tooltip = html.escape(str(base_text[start:end]), quote=True)
        result.append(
            f"<span class='highlight-tooltip-green' title='{tooltip}'>{replacement_text}</span>"
        )
        cursor = end
    result.append(html.escape(base_text[cursor:]))
    return "".join(result)
def _build_corrected_html_from_corrected(corrected_text, errors):
    if not isinstance(corrected_text, str) or not isinstance(errors, list):
        return ""
    result = []
    cursor = 0
    for err in [e for e in errors if isinstance(e, dict)]:
        replacement_text = _extract_replacement_text(err.get("correct", ""))
        if not replacement_text:
            continue
        found = corrected_text.find(replacement_text, cursor)
        if found == -1:
            found = corrected_text.lower().find(replacement_text.lower(), cursor)
        if found == -1:
            continue
        end = found + len(replacement_text)
        result.append(html.escape(corrected_text[cursor:found]))
        tooltip = html.escape(str(err.get("mistake_text", "")), quote=True)
        result.append(
            f"<span class='highlight-tooltip-green' title='{tooltip}'>{html.escape(corrected_text[found:end])}</span>"
        )
        cursor = end
    result.append(html.escape(corrected_text[cursor:]))
    return "".join(result)
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
def _warn_and_go_back(message, fallback_route):
    flash(f"{message} Try again.", "warning")
    return redirect(request.referrer or fallback_route)
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
        try:
            analysis = netflix.call("netflix_data.json", request.form["type"])
            fence_match = re.search(r"```(?:html)?\s*([\s\S]*?)```", analysis, re.IGNORECASE)
            if fence_match:
                analysis = fence_match.group(1).strip()
            return render_template("netflixIndexSubmit.html", analysis = analysis)
        except Exception as e:
            return _warn_and_go_back(str(e), "/netflix")
    return redirect('/netflix')
@app.route("/instagram", methods = ["GET"])
def instagram_page():
    if request.method == "GET":
        return render_template("instagram_index.html")
@app.route("/instagramSubmit", methods = ["POST", "GET"])
def instagram_submit():
    if request.method == "POST":
        try:
            image_url = request.form["imageURLinput"]
            parsed = urlparse(image_url)
            if parsed.scheme not in ("http", "https"):
                raise ValueError("Invalid URL scheme")
            import socket
            try:
                hostname = parsed.hostname
                ip = socket.gethostbyname(hostname)
            except Exception:
                raise ValueError("Could not resolve hostname")
            import ipaddress
            addr = ipaddress.ip_address(ip)
            if addr.is_private or addr.is_loopback or addr.is_link_local:
                raise ValueError("Private URLs are not allowed")
            imgData = requests.get(image_url, headers = {"User-agent": "Monzilla/5.0"}, timeout = 10).content
            if not imgData[:4] in (b'\xff\xd8\xff\xe0', b'\xff\xd8\xff\xe1', b'\x89PNG', b'GIF8', b'WEBP'):
                raise ValueError("URL does not point to a valid image")
            with open("static/imageTest.jpg", "wb") as f:
                f.write(imgData)
            caption = instagram.call(request.form["imageURLinput"], request.form["language"], request.form["length"], request.form["hashtags"])
            return render_template("instagram_indexSubmit.html", caption=caption, imageName="static/imageTest.jpg")
        except Exception as e:
            return _warn_and_go_back(str(e), "/instagram")
    return redirect('/instagram')
@app.route("/grammarly", methods = ["GET"])
def grammarly_page():
    if request.method == "GET":
        return render_template("grammarly_index.html")
@app.route("/grammarlySubmit", methods = ["POST", "GET"])
def grammarly_submit():
    if request.method == "POST":
        try:
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
            candidate_json = text[start:]
            decoder = json.JSONDecoder()
            try:
                analysis, _ = decoder.raw_decode(candidate_json)
            except json.JSONDecodeError:
                repaired_json = _repair_llm_json(candidate_json)
                if repaired_json is None:
                    raise
                analysis = json.loads(repaired_json)
            if not isinstance(analysis, dict):
                raise ValueError(f"Unexpected Grammarly response type: {type(analysis).__name__}")
            text_data = analysis.setdefault("text", {})
            if not isinstance(text_data, dict):
                analysis["text"] = {}
                text_data = analysis["text"]
            initial_text = text_data.get("initial", "")
            corrected_text = text_data.get("corrected", "")
            errors = analysis.get("errors", []) if isinstance(analysis, dict) else []
            text_data["mistake_text_html"] = _build_mistake_html(initial_text, errors)
            text_data["corrected_text_html"] = _build_corrected_html_from_corrected(corrected_text, errors)
            if not text_data["corrected_text_html"]:
                text_data["corrected_text_html"] = html.escape(corrected_text)
            print(analysis)
            var1 = "<span class='highlight-tooltip' title='could not'>cannot</span>"
            return render_template("grammarly_indexSubmit.html", analysis = analysis, test=var1)
        except Exception as e:
            return _warn_and_go_back(str(e), "/grammarly")
    return redirect('/grammarly')
@app.route("/duolingo", methods = ["GET"])
def duolingo_page():
    if request.method == "GET":
        return render_template("duolingo_index.html")
@app.route("/duolingoSubmit", methods = ["POST", "GET"])
def duolingo_submit():
    if request.method == "POST":
        try:
            language = request.form.get("language")
            data = duolingo.call(language)
            if data.strip().startswith("```"):
                data = data.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                repaired = _repair_llm_json(data)
                if repaired is None:
                    raise ValueError("Invalid JSON returned from Duolingo model")
                try:
                    data = json.loads(repaired)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON returned from Duolingo model")
            print(data)
            return render_template("duolingo_indexSubmit.html", data = data)
        except Exception as e:
            return _warn_and_go_back(str(e), "/duolingo")
    return redirect('/duolingo')


# set FLASK_APP=app
# set FLASK_ENV=development
# flask --app app.py --debug run

