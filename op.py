# -*- coding: utf-8 -*-

import os
import re
import zipfile
from google import genai
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

# -----------------------------
# Load API key
# -----------------------------
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# -----------------------------
# Extract transcript
# Compatible with youtube-transcript-api >= 0.7.0 (new) and older versions
# -----------------------------
def extract_transcript(video_id):
    try:
        # New API (>= 0.7.0): instance-based, returns objects with .text
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        text = " ".join([t.text for t in transcript_list])
        return text
    except TypeError:
        pass
    except Exception as e:
        print("Error fetching transcript:", e)
        return ""

    try:
        # Old API (< 0.7.0): static method, returns list of dicts
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript_list])
        return text
    except Exception as e:
        print("Error fetching transcript:", e)
        return ""

# -----------------------------
# Gemini text generation
# -----------------------------
def generate_text(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print("Gemini error:", e)
        return ""

# -----------------------------
# Summarize
# -----------------------------
def summarize(text):
    MAX_CHARS = 30000
    if len(text) > MAX_CHARS:
        print(f"  Transcript too long ({len(text):,} chars), truncating to {MAX_CHARS:,}...")
        text = text[:MAX_CHARS]

    prompt = (
        "Convert this YouTube transcript into a professional article.\n\n"
        "RULES:\n"
        "- Ignore intro, ads, subscribe prompts\n"
        "- Focus only on useful technical content\n"
        "- Use ## headings and bullet points\n"
        "- Keep it clean and structured\n\n"
        "TRANSCRIPT:\n"
        + text
    )
    return generate_text(prompt)

# -----------------------------
# Generate webpage
# -----------------------------
def generate_webpage(article):
    prompt = (
        "Create a modern responsive article webpage.\n\n"
        "STRICT FORMAT — use EXACTLY these delimiters, no extra text outside them:\n\n"
        "--html--\n[html code here]\n--html--\n\n"
        "--css--\n[css code here]\n--css--\n\n"
        "--js--\n[js code here]\n--js--\n\n"
        "Requirements:\n"
        "- The HTML file must link to style.css and script.js\n"
        "- Mobile responsive, clean typography\n"
        "- Dark/light mode toggle in JS\n\n"
        "ARTICLE CONTENT:\n"
        + article
    )
    return generate_text(prompt)

# -----------------------------
# Extract parts safely
# -----------------------------
def extract_part(text, tag):
    try:
        pattern = rf"--{tag}--\s*(.*?)\s*--{tag}--"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        print(f"  Warning: could not find --{tag}-- section in response")
        return ""
    except Exception as e:
        print(f"Error extracting {tag}:", e)
        return ""

# -----------------------------
# Extract video ID robustly
# -----------------------------
def extract_video_id(url):
    m = re.search(r"(?:v=|/v/|youtu\.be/|/embed/)([a-zA-Z0-9_-]{11})", url)
    if m:
        return m.group(1)
    raise ValueError(f"Could not parse video ID from URL: {url}")

# -----------------------------
# MAIN PIPELINE
# -----------------------------
def run(video_url):
    video_id = extract_video_id(video_url)
    print(f"Video ID: {video_id}")

    print("Extracting transcript...")
    transcript = extract_transcript(video_id)
    if not transcript:
        print("No transcript found. Exiting.")
        return
    print(f"  Transcript length: {len(transcript):,} characters")

    print("Generating article summary...")
    article = summarize(transcript)
    if not article:
        print("Summary generation failed. Exiting.")
        return

    print("Generating webpage...")
    webpage = generate_webpage(article)

    html = extract_part(webpage, "html")
    css  = extract_part(webpage, "css")
    js   = extract_part(webpage, "js")

    if not html:
        print("  Warning: HTML extraction failed, using fallback wrapper")
        html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Article</title><link rel="stylesheet" href="style.css"></head>
<body><article style="max-width:740px;margin:2rem auto;padding:1rem;font-family:Georgia,serif;line-height:1.8">
<pre style="white-space:pre-wrap">{article}</pre>
</article><script src="script.js"></script></body></html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  Saved: index.html")

    with open("style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print("  Saved: style.css")

    with open("script.js", "w", encoding="utf-8") as f:
        f.write(js)
    print("  Saved: script.js")

    with zipfile.ZipFile("website.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("index.html")
        zipf.write("style.css")
        zipf.write("script.js")
    print("  Saved: website.zip")

    print("\nDone! Open index.html in your browser.")

# -----------------------------
# RUN
# -----------------------------
run("https://www.youtube.com/watch?v=3JZ_D3ELwOQ")