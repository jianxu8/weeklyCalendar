import requests
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import os
import matplotlib.pyplot as plt

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

tickers = [
    'NVDA', 'GOOGL', 'AMZN', 'AAPL', 'META', 'MSFT', 'TSLA', 'SPCX',
    'MU', 'AVGO', 'INTC', 'AMD', 'TXN', 'TSM', 'SMCI', 'MRVL', 'SNDK', 'SKHY',
    'BE', 'CEG', 'GEV', 'OKLO', 'VLO', 'PBF', 'TE', 'VST', 'NEE',
    'IREN', 'NBIS', 'CRWV', 'APLD', 'WULF', 'CORZ',
    'NFLX', 'IBM', 'NOW', 'QCOM', 'PLTR', 'SNAP', 'T', 'ORCL', 'DELL', 'CRWD', 'CRM', 'STX',
    'JPM', 'BAC', 'WFC', 'V', 'HOOD', 'SOFI', 'PYPL', 'MA', 'AXP', 'GS', 'MS', 'C', 'SCHW',
    'JNJ', 'LLY', 'ISRG', 'UNH', 'PFE', 'MRNA', 'ABBV',
    'WMT', 'GM', 'CMG', 'MCD', 'F', 'SBUX', 'TGT', 'HD', 'NKE', 'COST', 'KO', 'PEP',
    'STLD', 'CLF', 'GE', 'RTX', 'LMT', 'CAT', 'BA', 'XOM', 'CVX',
    'DIS', 'TMUS', 'UBER', 'PGR', 'ABNB', 'DASH', 'BBY'
]


def post_weekly_earnings_calendar():
    today = datetime.today()
    this_monday = today - timedelta(days=today.weekday())
    next_monday = this_monday + timedelta(days=7)
    next_weekdays = [next_monday + timedelta(days=i) for i in range(5)]

    dates = []
    for d in next_weekdays:
        dates.append(f"{d:%Y-%m-%d}")
    
    mon, tue, wed, thu, fri = [], [], [], [], []
    for t in tickers:
        ticker = yf.Ticker(t)
        df = ticker.calendar["Earnings Date"]
        earnings_date = df[0].strftime('%Y-%m-%d')
        short_name = ticker.info.get("shortName")
        if earnings_date == dates[0]:
            mon.append(f"{t}\n{short_name}")
        elif earnings_date == dates[1]:
            tue.append(f"{t}\n{short_name}")
        elif earnings_date == dates[2]:
            wed.append(f"{t}\n{short_name}")
        elif earnings_date == dates[3]:
            thu.append(f"{t}\n{short_name}")
        elif earnings_date == dates[4]:
            fri.append(f"{t}\n{short_name}")

    all_dates = [mon, tue, wed, thu, fri]
    max_len = max(len(lst) for lst in all_dates)
    for lst in all_dates:
        lst.extend([" "] * (max_len - len(lst)))

    data = {
        "Monday " + f"{d:%m/%d}": mon,
        "Tuesday " + f"{d:%m/%d}": tue,
        "Wednesday " + f"{d:%m/%d}": wed,
        "Thursday " + f"{d:%m/%d}": thu,
        "Friday " + f"{d:%m/%d}": fri,
    }

    # Ensure all columns have the exact same length for the table grid
    df = pd.DataFrame(data)

    # 3. Create the Calendar Visualization with Matplotlib
    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    ax.axis("off")  # Hide standard graph axes

    # Generate the visual table layout
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
    )

    # Apply sleek styling (Dark theme with a clean finance aesthetic)
    table.auto_set_font_size(False)  # Turn off auto-scaling so your manual size takes effect
    table.scale(1.2, 2.8)            # Expand padding for better breathing room

    # Loop through and paint the table components professionally
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            # Header row styling (Sleek dark background with white text)
            cell.set_text_props(
                weight="bold", color="#ffffff", size=11, fontname="sans-serif"
            )
            cell.set_facecolor("#1f2937")  # Charcoal Grey
            cell.set_edgecolor("#374151")
        else:
            # Body cell styling (Setting size directly inside set_text_props)
            cell.set_text_props(
                color="#d1d5db", size=10, fontname="sans-serif"
            )
            cell.set_facecolor("#111827")  # Deep Discord dark-mode style slate
            cell.set_edgecolor("#374151")

            # Color-code timing visual cues safely
            text = cell.get_text().get_text()
            if "☀️" in text:
                cell.set_facecolor("#1e293b")  # Slight subtle blue tint for morning
            elif "🌙" in text:
                cell.set_facecolor("#14532d")  # Subtle green tint for evening lock-in


    # Title overlay
    plt.title(
        "Weekly Earnings Calendar",
        pad=20,
        fontsize=14,
        weight="bold",
        color="#ffffff",
        fontname="sans-serif",
    )
    fig.patch.set_facecolor("#111827")  # Match global canvas with table slate

    # Save the final calendar map to disk
    image_path = "earnings_calendar.png"
    plt.savefig(
        image_path, bbox_inches="tight", facecolor=fig.get_facecolor(), dpi=300
    )
    plt.close()

    # 4. Stream and upload the image file to Discord via Webhook
    payload = {
        "content": f"📊 Calendar for the week of {next_weekdays[0].strftime('%b')} {next_weekdays[0].strftime('%d')}-{next_weekdays[4].strftime('%d')}:"
    }

    with open(image_path, "rb") as file:
        files = {"file": (image_path, file, "image/png")}
        response = requests.post(WEBHOOK_URL, data=payload, files=files)

    if response.status_code in [200, 204]:
        print("Success: Calendar image successfully dispatched to Discord!")
    else:
        print(f"Failed to transmit message: {response.status_code}")
        print(response.text)


def post_weekly_calendar():
    today = datetime.now()
    days_until_monday = (0 - today.weekday() + 7) % 7
    if days_until_monday == 0:
        days_until_monday = 7

    next_week_start = today + timedelta(days=days_until_monday)
    next_week_end = next_week_start + timedelta(days=6)

    from_param = next_week_start.strftime("%Y-%m-%d")
    to_param = next_week_end.strftime("%Y-%m-%d")

    url = "https://www.financecalendar.com/wp-json/fc/v1/calendar?impact=high&from={from_param}&to={to_param}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        events = data.get("events", [])
        attribution = data.get("attribution", {}).get("source", "financecalendar.com")
        
        print(f"Successfully fetched {len(events)} high-impact market events from {attribution}.\n")

        row_format = "{:<16} {:<35} {:<20}"

        discord_message = "```yaml\n"
        discord_message += row_format.format("Date (ET)", "Event", "Prior Metric") + "\n"
        discord_message += "-" * 76 + "\n"  # Exactly matches your 76-character separator line

        for event in events:
            name = event.get("name") or "Unknown Event"
            date_val = event.get("date")
            time_et = event.get("time_et")
            prior = event.get("prior") or "None"
            
            # Normalize fallback text to match your exact output
            if prior == "N/A" or not str(prior).strip():
                prior = "None"
            
            # Handle Date conversion
            if date_val:
                try:
                    date_obj = datetime.strptime(str(date_val), "%Y-%m-%d")
                    date_display = date_obj.strftime("%b %d")
                except Exception:
                    date_display = str(date_val)
            else:
                date_display = "No Date"
                
            # Handle Time display
            time_display = f"{time_et}" if (time_et and str(time_et).strip()) else "All Day"
            date_time_col = f"{date_display} {time_display}".strip()
            
            # Build the perfectly aligned row string
            discord_message += row_format.format(str(date_time_col), str(name), str(prior)) + "\n"

        discord_message += "```"
        payload = {
            "content": discord_message
        }

        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("Success!")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")

if __name__ == '__main__':
    post_weekly_earnings_calendar()
    post_weekly_calendar()
