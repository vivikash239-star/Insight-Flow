"""
InsightFlow - Sample Data Generator
Generates realistic e-commerce customer review data covering:
- Critical manufacturing defects and failure points
- Praised product features
- Customer wishlist and upcoming feature requests
"""

import os
import csv
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_input")
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample_reviews.csv")

PRODUCTS = [
    {
        "product_id": "PROD-001",
        "product_name": "AcousticPro Wireless Headphones",
        "reviews": [
            {
                "rating": 1,
                "text": "Extremely disappointed. The left earbud stopped charging completely after only four days of normal use. The charging case pin seems dead and loose. Display LED just blinks red forever. Do not buy this defect prone product."
            },
            {
                "rating": 1,
                "text": "Severe audio failure! Left speaker started producing unbearable high-pitched static crackle whenever active noise cancellation is turned on. Returning this immediately for a refund."
            },
            {
                "rating": 2,
                "text": "The headband hinge cracked while putting them on normally. Plastic is extremely fragile and cheap. I wish it had metal reinforced joints and a physical volume dial instead of sensitive touch controls."
            },
            {
                "rating": 5,
                "text": "Active noise cancellation completely silences subway commute and office chatter! Soundstage is wonderfully wide with rich bass. Battery easily lasts 3 full days of heavy listening."
            },
            {
                "rating": 4,
                "text": "Crisp highs and warm mids make jazz recordings sound divine. The memory foam ear cushions are ultra plush for all-day comfort. However, I wish it had multipoint Bluetooth pairing for switching between laptop and phone."
            },
            {
                "rating": 3,
                "text": "Sound quality is punchy and enjoyable. Microphone works well on Zoom calls. Next version should include an IPX7 water resistance rating and replaceable ear cups."
            },
            {
                "rating": 2,
                "text": "Audio cuts out randomly when walking outside due to weak Bluetooth connection. Also, the charging port gets alarmingly hot during fast charge. Needs a firmware fix ASAP."
            },
            {
                "rating": 4,
                "text": "Great build aesthetics and lightweight profile. Battery life is fantastic. Would be better if the companion app allowed custom 10-band EQ presets instead of just three generic profiles."
            },
            {
                "rating": 1,
                "text": "The power switch failed on day 10 and wouldn't shut off. Battery drained to zero and now unit is completely dead. Serious quality control defect."
            },
            {
                "rating": 5,
                "text": "Outstanding transparency mode and phenomenal acoustic clarity. The included carrying case is compact and durable. Hope future versions have wireless charging for the case."
            },
            {
                "rating": 3,
                "text": "Comfortable fit and decent sound isolation. The voice prompt is unnecessarily loud. Hope to see an option to disable voice cues in future firmware updates."
            },
            {
                "rating": 1,
                "text": "Right ear cup sound died during workout. Sweat seems to have caused internal short circuit. Defective moisture seal around internal drivers."
            }
        ]
    },
    {
        "product_id": "PROD-002",
        "product_name": "Vortex AMOLED Smartwatch",
        "reviews": [
            {
                "rating": 1,
                "text": "Catastrophic screen defect! Display glass cracked under minimal thumb pressure while tapping the stopwatch. The glass is ridiculously fragile and has zero scratch resistance."
            },
            {
                "rating": 1,
                "text": "Severe overheating warning! Watch gets scorching hot while charging on the magnetic cradle and shuts down. Battery swelling noticed near the rear sensor after 1 week. Huge safety hazard."
            },
            {
                "rating": 2,
                "text": "Heart rate sensor constantly disconnects during runs and gives wildly inaccurate numbers. Step counter is loose and registers bumps in the car as 500 steps. Software crashes often."
            },
            {
                "rating": 5,
                "text": "Vibrant AMOLED display is razor sharp even under direct midday sunlight! The UI animation is buttery smooth at 60Hz. GPS locks onto satellites in under three seconds."
            },
            {
                "rating": 4,
                "text": "Sleep tracking breakdown is remarkably precise and battery easily lasts 4 full days with always-on display disabled. Elegant titanium bezel looks luxurious on wrist."
            },
            {
                "rating": 3,
                "text": "The display is gorgeous and notifications arrive promptly. However, I wish it had offline Spotify music storage and NFC payment support. Needs a standalone voice assistant."
            },
            {
                "rating": 2,
                "text": "Screen touch digitizer started failing along the lower edge. Tapping back button does not respond. Hope to see better capacitive touch calibration in future batches."
            },
            {
                "rating": 4,
                "text": "Lightweight on the wrist and sleep metrics are actionable. Would be better if the companion iOS app synced background health data without requiring manual refresh."
            },
            {
                "rating": 1,
                "text": "Watch crown button broke off after accidental bump against doorframe. Internal spring popped out. Fragile mounting mechanism is an unacceptable design failure."
            },
            {
                "rating": 5,
                "text": "Magnificent display colors and deep blacks. Water resistance held up during lap swimming in the pool. Next version should include ECG and body temperature monitoring."
            },
            {
                "rating": 3,
                "text": "Satisfactory fitness tracker with great screen brightness. Missing third-party watch face support. We hope future versions have customizable widget layouts."
            },
            {
                "rating": 1,
                "text": "Display developed a permanent bright green vertical line across the matrix on day 3. Return initiated. Defective screen connector."
            }
        ]
    },
    {
        "product_id": "PROD-003",
        "product_name": "BoltCharge 65W Power Bank",
        "reviews": [
            {
                "rating": 1,
                "text": "Fire hazard! The power bank began swelling visibly after fast charging my laptop twice. Outer plastic casing warped from extreme internal heat. Battery pack failed completely."
            },
            {
                "rating": 1,
                "text": "USB-C output port became loose and wobbles inside the enclosure. Cable disconnects at the slightest movement. Poor soldering on PCB causes intermittent power cutoff."
            },
            {
                "rating": 2,
                "text": "Digital percentage display died after dropping from coffee table height (less than two feet). The casing cracked along the seam. Fragile shell lacks drop protection."
            },
            {
                "rating": 5,
                "text": "Incredible charging speed! Powers my MacBook Pro and iPhone 15 simultaneously without breaking a sweat. Compact form factor slides easily into my laptop backpack."
            },
            {
                "rating": 4,
                "text": "High power output delivers honest 65W Power Delivery. Pass-through charging works seamlessly while plugged into wall. Aluminum shell feels durable and dissipates heat nicely."
            },
            {
                "rating": 3,
                "text": "Great capacity and reliable wattage delivery. However, I wish it had an integrated retractable USB-C cable so I don't have to carry extra cords everywhere."
            },
            {
                "rating": 2,
                "text": "Output wattage drops dramatically from 65W down to 18W when unit gets warm after 20 minutes. Thermal throttling fails to sustain high-speed laptop charging."
            },
            {
                "rating": 4,
                "text": "Solid battery capacity and digital display is informative. Next version should include MagSafe wireless charging pad on top for emergency phone top-ups."
            },
            {
                "rating": 1,
                "text": "Unit arrived completely dead out of the box. Would not accept charge from 65W GaN adapter. Defective battery management controller."
            },
            {
                "rating": 5,
                "text": "Phenomenal portable power station. Airline approved capacity and charges devices rapidly. Hope to see a 100W version for dual laptops in the future."
            },
            {
                "rating": 3,
                "text": "Charges fast and looks sleek. Missing an extra USB-A port for older legacy devices. Hope they add rubber bumper feet to prevent sliding on glass desks."
            },
            {
                "rating": 1,
                "text": "Smelled electrical burning odor during first 65W charging session. Unit clicked and stopped working forever. Internal fuse blown."
            }
        ]
    }
]

def generate_sample_dataset(filepath=SAMPLE_CSV_PATH, target_count=90):
    """Generates a rich, realistic review dataset with multiple reviews per product."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    reviews_written = 0
    base_date = datetime.now() - timedelta(days=60)
    
    with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["review_id", "product_id", "product_name", "review_text", "rating", "date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write base detailed reviews first
        review_counter = 1001
        for prod in PRODUCTS:
            for item in prod["reviews"]:
                days_offset = random.randint(1, 55)
                review_date = (base_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
                writer.writerow({
                    "review_id": f"REV-{review_counter}",
                    "product_id": prod["product_id"],
                    "product_name": prod["product_name"],
                    "review_text": item["text"],
                    "rating": item["rating"],
                    "date": review_date
                })
                review_counter += 1
                reviews_written += 1
                
        # Synthesize additional variations to reach target_count
        variations = [
            ("Display glass cracked along upper bezel. Fragile material needs tempered upgrade.", 1),
            ("Active noise cancellation works wonders during busy flights. Crystal clear highs.", 5),
            ("I wish it had a physical mute switch for conference calls and volume rocker.", 3),
            ("Battery swelling and extreme heat detected after quick charge cycle. Defective cell.", 1),
            ("Battery easily lasts 3 full days of intense usage. Terrific endurance.", 5),
            ("Should include IP68 dust and water resistance in the upcoming version.", 4),
            ("Left charging contact is loose and fails to connect to cradle pins reliably.", 2),
            ("Would be better if the companion app had a built-in equalizer and dark mode.", 3),
            ("Microphone sound distortion during calls. Hardware crackling noise reported.", 1),
            ("Hoping they add wireless Qi charging and longer braided USB-C cable.", 4)
        ]
        
        while reviews_written < target_count:
            prod = random.choice(PRODUCTS)
            var_text, var_rating = random.choice(variations)
            days_offset = random.randint(1, 60)
            review_date = (base_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            
            writer.writerow({
                "review_id": f"REV-{review_counter}",
                "product_id": prod["product_id"],
                "product_name": prod["product_name"],
                "review_text": var_text,
                "rating": var_rating,
                "date": review_date
            })
            review_counter += 1
            reviews_written += 1
            
    print(f"[InsightFlow] Generated {reviews_written} sample reviews at: {filepath}")
    return filepath

if __name__ == "__main__":
    generate_sample_dataset()
