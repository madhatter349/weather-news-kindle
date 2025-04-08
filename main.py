import requests
import feedparser
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import textwrap

# --- Settings ---
POINTS_URL = "https://api.weather.gov/points/40.7986,-73.9707"
RSS_FEED = "https://time.com/feed/"
OUTPUT_FILE = "bg_ss00.png"
KINDLE_SIZE = (1072, 1448)

# Weather emoji map
ICON_MAP = {
    "Sunny": "☀️", "Clear": "🌙",
    "Partly Cloudy": "⛅", "Mostly Cloudy": "⛅",
    "Cloudy": "☁️", "Overcast": "☁️",
    "Rain": "🌧️", "Showers": "🌦️", "Light Rain": "🌦️",
    "Snow": "❄️", "Sleet": "🌨️",
    "Thunderstorm": "⛈️", "Thunderstorms": "⛈️"
}

# Fonts
try:
    FONT = ImageFont.truetype("DejaVuSans.ttf", 28)
    SMALL = ImageFont.truetype("DejaVuSans.ttf", 22)
except:
    FONT = ImageFont.load_default()
    SMALL = ImageFont.load_default()

def get_weather():
    points = requests.get(POINTS_URL).json()
    forecast_url = points["properties"]["forecastHourly"]
    forecast = requests.get(forecast_url).json()
    periods = forecast["properties"]["periods"][:6]

    forecast_list = []
    for p in periods:
        time_12hr = datetime.fromisoformat(p["startTime"]).astimezone(pytz.timezone("America/New_York")).strftime("%I:%M %p")
        short = p["shortForecast"]
        emoji = "🌡️"
        for key in ICON_MAP:
            if key.lower() in short.lower():
                emoji = ICON_MAP[key]
                break
        forecast_list.append({
            "time": time_12hr,
            "temp": f'{p["temperature"]}°{p["temperatureUnit"]}',
            "short": short,
            "icon": emoji
        })
    return forecast_list

def get_headlines():
    feed = feedparser.parse(RSS_FEED)
    return [
        {
            "title": entry["title"],
            "summary": entry.get("summary", "").strip().replace("\n", " ")[:240]
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

    x_padding = 80
    max_text_width = 1400 - x_padding * 2
    y = 40

    # Weather
    draw.text((x_padding, y), "☁️ Weather Forecast – Upper West Side", font=FONT, fill=0)
    y += 60
    for entry in weather:
        line = f'{entry["time"]}  {entry["temp"]}  {entry["icon"]}  {entry["short"]}'
        draw.text((x_padding + 20, y), line, font=SMALL, fill=0)
        y += 36

    y += 30
    draw.line((x_padding, y, 1440 - x_padding, y), fill=200)
    y += 30

    # Headlines
    draw.text((x_padding, y), "📰 Latest Headlines from TIME", font=FONT, fill=0)
    y += 50
    for i, article in enumerate(headlines, 1):
        draw.text((x_padding + 20, y), f"{i}. {article['title']}", font=SMALL, fill=0)
        y += 28

        summary_lines = wrap_text(draw, f'↳ {article["summary"]}', SMALL, max_text_width)
        for line in summary_lines:
            draw.text((x_padding + 40, y), line, font=SMALL, fill=0)
            y += 26

        y += 14
        draw.line((x_padding + 10, y, 1440 - x_padding - 10, y), fill=220)
        y += 20

    # Timestamp in EST
    now_est = datetime.now(pytz.timezone("America/New_York"))
    timestamp = now_est.strftime("Generated on %a %b %d, %I:%M %p (ET)")
    draw.text((x_padding, 1020), timestamp, font=SMALL, fill=0)

    # Rotate and save
    img = img.rotate(90, expand=True).resize(KINDLE_SIZE)
    img.save(OUTPUT_FILE)
    print(f"✅ Saved Kindle-ready image as {OUTPUT_FILE}")

# --- Main ---
if __name__ == "__main__":
    weather = get_weather()
    headlines = get_headlines()
    render_image(weather, headlines)
