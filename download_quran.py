import requests
import json

def download_quran():
    url = "http://api.alquran.cloud/v1/quran/en.sahih"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        with open("datasets/api-alquran-cloud-en.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print("Downloaded and saved as quran-en.json")
    else:
        print(f"Failed to download. Status code: {response.status_code}")

def extract_verses():
    # Load the JSON file
    with open('datasets/api-alquran-cloud-en.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract surahs
    surah_verses = {}
    for surah in data.get("data", {}).get("surahs", []):
        surah_number = surah.get("number")
        surah_name = surah.get("englishName")
        verses = [ayah["text"] for ayah in surah.get("ayahs", [])]
        
        # Store the verses for the surah
        surah_verses[surah_number] = {
            "name": surah_name,
            "verses": verses
        }

    # Save the extracted data to a new JSON file
    with open('datasets/quran_verses.json', 'w', encoding='utf-8') as output_file:
        json.dump(surah_verses, output_file, indent=4, ensure_ascii=False)

    print("Extracted verses saved to quran_verses.json")

if __name__ == "__main__":
    # download_quran()
    extract_verses()