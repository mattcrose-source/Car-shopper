import os
import requests

# Configuration
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN", "YOUR_APIFY_TOKEN")
ACTOR_ID = "apify/car-max-scraper" # Or your specific Autotrader/CarGurus actor ID

# Define your strict acquisition criteria
TARGET_CRITERIA = [
    {"make": "Nissan", "model": "Ariya", "trim": "Engage+", "max_price": 27500},
    {"make": "Volvo", "model": "XC40 Recharge", "trim": None, "max_price": 29500},
    {"make": "Kia", "model": "EV6", "trim": None, "max_price": 31000},
    {"make": "Hyundai", "model": "Ioniq 5", "trim": None, "max_price": 31000}
]

def fetch_car_listings():
    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items?token={APIFY_API_TOKEN}"
    
    # Example payload matching the scraper actor's requirements
    payload = {
        "searchRadius": 100,
        "zipCode": "80202", # Denver area focus
        "maxResults": 100
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Apify: {e}")
        return []

def filter_listings(listings):
    matches = []
    for car in listings:
        price = car.get("price", 999999)
        title = car.get("title", "").lower()
        make = car.get("make", "").lower()
        model = car.get("model", "").lower()
        
        # Guard clauses matching your target parameters
        for target in TARGET_CRITERIA:
            if target["make"].lower() not in make and target["make"].lower() not in title:
                continue
            if target["model"].lower() not in model and target["model"].lower() not in title:
                continue
            if target["trim"] and target["trim"].lower() not in title:
                continue
            if price > target["max_price"]:
                continue
                
            # If it passes all guards, it's a valid hit
            matches.append({
                "title": car.get("title"),
                "price": price,
                "url": car.get("url"),
                "mileage": car.get("mileage"),
                "location": car.get("location", "Denver")
            })
    return matches

if __name__ == "__main__":
    print("Starting inventory scrape...")
    raw_data = fetch_car_listings()
    valid_deals = filter_listings(raw_data)
    
    if valid_deals:
        print(f" Found {len(valid_deals)} matches matching your target criteria:")
        for deal in valid_deals:
            print(f"- {deal['title']}: ${deal['price']} | {deal['url']}")
            # Add webhook/email notification logic here if desired
    else:
        print("No inventory matches found within your price thresholds today.")
