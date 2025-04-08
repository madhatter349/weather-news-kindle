import requests
import feedparser
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz

# --- Settings ---
POINTS_URL = "https://api.weather.gov/points/40.7986,-73.9707"
RSS_FEED = "https://rss.jpost.com/rss/rssfeedsheadlines.aspx"
OUTPUT_FILE = "bg_ss00.png"
KINDLE_SIZE = (1072, 1448)

# Load fonts
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
            "title": entry.get("title", "").strip()
        }
        for entry in feed.entries[:5]
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
    draw.line((x_pad, y, x_pad + max_width, y), fill=180)
    y += 20

    # Weather rows
    col1, col2, col3 = x_pad, x_pad + 160, x_pad + 280
    for entry in weather:
        draw.text((col1, y), entry["time"], font=MONO, fill=0)
        draw.text((col2, y), entry["temp"].rjust(5), font=MONO, fill=0)
        draw.text((col3, y), entry["short"], font=SMALL, fill=0)
        y += 36

    # Spacer
    y += 40

    # News Section Header (boxed background)
    header_h = 40
    draw.rectangle([x_pad, y, x_pad + max_width, y + header_h], fill=240)
    draw.text((x_pad + 10, y + 6), "Latest Headlines from The Jerusalem Post", font=FONT, fill=0)
    y += header_h + 20

    # News Items
    for i, article in enumerate(headlines, 1):
        lines = wrap_text(draw, f"{i}. {article['title']}", FONT, max_width)
        for line in lines:
            draw.text((x_pad, y), line, font=FONT, fill=0)
            y += 30
        y += 10
        draw.line((x_pad + 10, y, x_pad + max_width - 10, y), fill=220)
        y += 20

    # Footer with timestamp (EST)
    now_est = datetime.now(pytz.timezone("America/New_York"))
    timestamp = now_est.strftime("Generated on %a %b %d, %I:%M %p (ET)")
    draw.line((x_pad, 1020, x_pad + max_width, 1020), fill=200)
    draw.text((x_pad, 1025), timestamp, font=SMALL, fill=0)

    # Final output
    img = img.rotate(90, expand=True).resize(KINDLE_SIZE)
    img.save(OUTPUT_FILE)
    print(f"✅ Saved Kindle-ready image as {OUTPUT_FILE}")

# --- Main ---
if __name__ == "__main__":
    weather = get_weather()
    headlines = get_headlines()
    render_image(weather, headlines)
