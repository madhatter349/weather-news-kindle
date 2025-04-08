import requests
import feedparser
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import io

# --- Settings ---
POINTS_URL = "https://api.weather.gov/points/40.7986,-73.9707"
RSS_FEED = "https://time.com/feed/"
OUTPUT_FILE = "bg_ss00.png"
KINDLE_SIZE = (1072, 1448)

# Weather emoji map (basic keywords)
ICON_MAP = {
    "Sunny": "☀️", "Clear": "🌙",
    "Partly Cloudy": "⛅", "Mostly Cloudy": "⛅",
    "Cloudy": "☁️", "Overcast": "☁️",
    "Rain": "🌧️", "Showers": "🌦️", "Light Rain": "🌦️",
    "Snow": "❄️", "Sleet": "🌨️",
    "Thunderstorm": "⛈️", "Thunderstorms": "⛈️"
}

# Fallback font
try:
    FONT = ImageFont.truetype("DejaVuSans.ttf", 28)
    SMALL = ImageFont.truetype("DejaVuSans.ttf", 22)
except:
    FONT = ImageFont.load_default()
    SMALL = ImageFont.load_default()

# --- Fetch weather forecast ---
def get_weather():
    points = requests.get(POINTS_URL).json()
    forecast_url = points["properties"]["forecastHourly"]
    forecast = requests.get(forecast_url).json()
    periods = forecast["properties"]["periods"][:6]

    forecast_list = []
    for p in periods:
        time_12hr = datetime.fromisoformat(p["startTime"]).strftime("%I:%M %p")
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

# --- Fetch top 5 headlines ---
def get_headlines():
    feed = feedparser.parse(RSS_FEED)
    return [
        {
            "title": entry["title"],
            "summary": entry.get("summary", "").strip().replace("\n", " ")[:120]
        }
        for entry in feed["entries"][:5]
    ]

# --- Draw everything ---
def render_image(weather, headlines):
    img = Image.new("L", (1448, 1072), 255)  # start in landscape
    draw = ImageDraw.Draw(img)

    y = 40
    draw.text((40, y), "☁️ Weather Forecast – Upper West Side", font=FONT, fill=0)
    y += 60
    for entry in weather:
        line = f'{entry["time"]}  {entry["temp"]}  {entry["icon"]}  {entry["short"]}'
        draw.text((60, y), line, font=SMALL, fill=0)
        y += 36

    # Divider
    y += 20
    draw.line((40, y, 1400, y), fill=200, width=1)
    y += 30

    # News Section
    draw.text((40, y), "📰 Latest Headlines from TIME", font=FONT, fill=0)
    y += 50
    for idx, article in enumerate(headlines, 1):
        draw.text((60, y), f"{idx}. {article['title']}", font=SMALL, fill=0)
        y += 28
        if article["summary"]:
            draw.text((80, y), f'↳ {article["summary"]}', font=SMALL, fill=0)
            y += 32
        y += 10  # spacing

    # Footer
    timestamp = datetime.now().strftime("Generated on %a %b %d, %I:%M %p")
    draw.text((40, 1020), timestamp, font=SMALL, fill=0)

    # Rotate & resize to Kindle portrait
    img = img.rotate(90, expand=True).resize(KINDLE_SIZE)
    img.save(OUTPUT_FILE)
    print(f"✅ Saved Kindle-ready image as {OUTPUT_FILE}")

# --- Main ---
if __name__ == "__main__":
    weather = get_weather()
    headlines = get_headlines()
    render_image(weather, headlines)
