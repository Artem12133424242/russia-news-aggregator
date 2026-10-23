import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import re

def clean_html(text):
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = clean.replace('&nbsp;', ' ').replace('&amp;', '&')
    return clean.strip()

def parse_rss(city, url):
    events = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url.strip(), headers=headers, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        for item in root.findall('.//item')[:5]:
            title = item.find('title')
            desc = item.find('description')
            link = item.find('link')
            pub_date = item.find('pubDate')
            
            if title is None or title.text is None:
                continue
                
            events.append({
                "city": city,
                "type": "Новость",
                "title": title.text.strip(),
                "description": clean_html(desc.text if desc is not None and desc.text else "")[:300],
                "date": pub_date.text.strip() if pub_date is not None and pub_date.text else datetime.now().strftime("%Y-%m-%d"),
                "place": city,
                "link": link.text.strip() if link is not None and link.text else url
            })
    except Exception as e:
        print(f"️  {city}: {e}")
    
    return events

def main():
    print(f"🚀 Запуск: {datetime.now()}")
    
    with open('sources.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)
    
    print(f" Городов: {len(sources)}")
    
    all_data = []
    success = 0
    
    for city, url in sources.items():
        events = parse_rss(city, url)
        if events:
            all_data.extend(events)
            success += 1
            print(f"✅ {city}: +{len(events)}")
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Итого: {len(all_data)} записей из {success} городов")

if __name__ == "__main__":
    main()
