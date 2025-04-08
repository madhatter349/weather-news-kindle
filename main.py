import requests
import feedparser
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz

# --- Settings ---
POINTS_URL = "https://api.weather.gov/points/40.7986,-73.9707"
RSS_FEED = "https://time.com/feed/"
OUTPUT_FILE = "bg_ss00.png"
KINDLE_SIZE = (1072, 1448)

# Fonts
try:
    FONT = ImageFont.truetype("DejaVuSans.ttf", 28)
    SMALL = ImageFont.truetype("DejaVuSans.ttf", 22)
    MONO = ImageFont.truetype("DejaVuSansMono.ttf", 22)
except:
    FONT = ImageFont.load_default()
    SMALL = ImageFont.load_default()
    MONO = SMALL

def get_weather():
    points = requests.get(POINTS_URL).json()
    forecast_url = points["properties"]["forecastHourly"]
    forecast = requests.get(forecast_url).json()
    periods = forecast["properties"]["periods"][:6]

    forecast_list = []
    for p in periods:
        time_est = datetime.fromisoformat(p["startTime"]).astimezone(pytz.timezone("America/New_York"))
        time_12hr = time_est.strftime("%I:%M %p")
        forecast_list.append({
            "time": time_12hr,
            "temp": f'{p["temperature"]}°{p["temperatureUnit"]}',
            "short": p["shortForecast"]
        })
    return forecast_list

def get_headlines():
    feed = feedparser.parse(RSS_FEED)
    return [
        {
            "title": entry["title"],
            "summary": entry.get("summary", "").strip().replace("\n", " ")[:300]
        }
        for entry in feed["entries"][:5]
    ]

def wrap_text(draw, text, font, max_width):
    lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        if draw.textlength(test_line, font=font) <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def render_image(weather, headlines):
    img = Image.new("L", (1448, 1072), 255)
    draw = ImageDraw.Draw(img)

    x_pad = 80
    max_width = 1448 - 2 * x_pad
    y = 40

    # Weather Header
    draw.text((x_pad, y), "Weather Forecast – Upper West Side", font=FONT, fill=0)
    y += 50
    draw.line((x_pad, y, x_pad + max_width, y), fill=200)
    y += 20

    # Weather Table (3-column layout)
    col1_x, col2_x, col3_x = x_pad, x_pad + 160, x_pad + 280
    for entry in weather:
        draw.text((col1_x, y), entry["time"], font=MONO, fill=0)
        draw.text((col2_x, y), entry["temp"], font=MONO, fill=0)
        draw.text((col3_x, y), entry["short"], font=SMALL, fill=0)
        y += 36

    y += 30
    draw.line((x_pad, y, x_pad + max_width, y), fill=200)
    y += 30

    # Headlines Header
    draw.text((x_pad, y), "Latest Headlines from TIME", font=FONT, fill=0)
    y += 50

    for i, article in enumerate(headlines, 1):
        draw.text((x_pad, y), f"{i}. {article['title']}", font=SMALL, fill=0)
        y += 28

        for line in wrap_text(draw, article["summary"], SMALL, max_width - 20):
            draw.text((x_pad + 20, y), line, font=SMALL, fill=0)
            y += 26

        y += 12
        draw.line((x_pad + 10, y, x_pad + max_width - 10, y), fill=220)
        y += 20

    # Footer with timestamp
    now_est = datetime.now(pytz.timezone("America/New_York"))
    timestamp = now_est.strftime("Generated on %a %b %d, %I:%M %p (ET)")
    draw.text((x_pad, 1020), timestamp, font=SMALL, fill=0)

    # Rotate & Save
    img = img.rotate(90, expand=True).resize(KINDLE_SIZE)
    img.save(OUTPUT_FILE)
    print(f"✅ Saved Kindle-ready image as {OUTPUT_FILE}")

if __name__ == "__main__":
    weather = get_weather()
    headlines = get_headlines()
    render_image(weather, headlines)
