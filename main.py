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

# Optional: load a nicer font if available
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
    return [
        {
            "time": p["startTime"][11:16],
            "temp": f'{p["temperature"]}°{p["temperatureUnit"]}',
            "short": p["shortForecast"]
        }
        for p in periods
    ]

# --- Fetch top 5 headlines ---
def get_headlines():
    feed = feedparser.parse(RSS_FEED)
    return [entry["title"] for entry in feed["entries"][:5]]

# --- Draw everything ---
def render_image(weather, headlines):
    img = Image.new("L", (1448, 1072), 255)  # landscape first
    draw = ImageDraw.Draw(img)

    # Weather section
    draw.text((40, 40), "Weather Forecast (Upper West Side)", font=FONT, fill=0)
    y = 100
    for entry in weather:
        line = f'{entry["time"]}  {entry["temp"]}  {entry["short"]}'
        draw.text((60, y), line, font=SMALL, fill=0)
        y += 40

    # News section
    draw.text((40, 380), "Latest Headlines from TIME", font=FONT, fill=0)
    y = 440
    for i, headline in enumerate(headlines, 1):
        draw.text((60, y), f"{i}. {headline}", font=SMALL, fill=0)
        y += 40

    # Footer
    timestamp = datetime.now().strftime("Generated on %Y-%m-%d %H:%M")
    draw.text((40, 1020), timestamp, font=SMALL, fill=0)

    # Rotate & resize to Kindle portrait
    img = img.rotate(90, expand=True).resize(KINDLE_SIZE)
    img.save(OUTPUT_FILE)
    print(f"Saved {OUTPUT_FILE}")

# --- Main ---
if __name__ == "__main__":
    weather = get_weather()
    headlines = get_headlines()
    render_image(weather, headlines)
