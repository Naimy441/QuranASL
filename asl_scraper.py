import requests
from bs4 import BeautifulSoup
import json
import time
import os

def get_asl_video_from_page(url, cache):
    """Scrapes a given URL and returns the first video URL if available."""
    if url in cache:
        print(f"Cache hit for URL: {url}")
        return cache[url]  # Return the cached URL if already found
    
    print(f"Fetching URL: {url}")
    response = requests.get(url)
    
    # Log the HTML response to a file
    # filename = url.split("/")[-1]  # Use the last part of the URL as filename
    # with open(f"html_responses/{filename}_response.txt", "w", encoding="utf-8") as file:
    #     file.write(response.text)
    
    if response.status_code != 200:
        print(f"Failed to fetch: {url} (Status code: {response.status_code})")
        cache[url] = None
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check if the 'no video found' message exists
    if "Sorry, no video found for this word." in soup.text:
        print(f"No video found on page: {url}")
        cache[url] = None
        return None
    
    # Find first video player
    video = soup.find('video')
    if video and video.find('source'):
        video_url = video.find('source')['src']
        print(f"Video found: {video_url} from {url}")
        cache[url] = video_url  # Cache the video URL
        return video_url
    
    # Check for "See also" or "Categories" recommendations
    recommendations = soup.find_all('a', href=True)
    for recommendation in recommendations:
        if recommendation['href'].startswith('/sign/'):
            # Follow the link and try again
            new_url = f"https://www.signasl.org{recommendation['href']}"
            print(f"No video found. Trying recommendation: {new_url}")
            video_url = get_asl_video_from_page(new_url, cache)
            if video_url:
                return video_url
    
    print(f"No video found for: {url} and recommendations.")
    cache[url] = None  # No video found, cache None
    return None

def get_asl_video(word, cache):
    """Main function to scrape SignASL for a given word and return a video URL, following recommendations if necessary."""
    search_url = f"https://www.signasl.org/sign/{word.replace(' ', '-')}"
    print(f"Searching for word: {word}")
    return get_asl_video_from_page(search_url, cache)

def process_quranic_phrases(phrases):
    """Queries SignASL for each word in the phrases and stores results in a hashmap."""
    results = {}
    cache = {}  # Hashmap to store previously fetched word URLs
    download_folder = "videos"  # Folder where videos will be saved
    
    for key, phrase in phrases.items():
        print(f"Searching for phrase: {phrase}")
        words = phrase.split()  # Split phrase into words
        video_urls = []
        
        for word in words:
            print(f"Searching for word: {word}")
            video_url = get_asl_video(word, cache)
            if video_url:  # If a video URL was found
                print(f"Found video URL for word: {word} - {video_url}")
                video_path = download_video(video_url, download_folder)  # Download the video
                if video_path:
                    video_urls.append(video_path)  # Save the downloaded video path
            else:
                print(f"No video found for word: {word}")
        
        # Store the video URLs or null if none found
        if video_urls:
            results[key] = {phrase: video_urls}  # Save the phrase and its associated URLs
        else:
            results[key] = {phrase: None}  # If no videos were found, store None
    
        time.sleep(1)  # Be polite to the server
    
    return results

def download_video(url, download_folder="videos"):
    """Downloads a video from a given URL and saves it to a specified folder."""
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # Get the video filename from the URL
    video_filename = url.split("/")[-1]
    video_path = os.path.join(download_folder, video_filename)
    
    # Skip download if the video already exists
    if os.path.exists(video_path):
        print(f"Video already exists: {video_filename}")
        return video_path

    print(f"Downloading video: {video_filename}")
    video_response = requests.get(url, stream=True)
    
    if video_response.status_code == 200:
        with open(video_path, 'wb') as video_file:
            for chunk in video_response.iter_content(chunk_size=8192):
                video_file.write(chunk)
        print(f"Video downloaded: {video_filename}")
        return video_path
    else:
        print(f"Failed to download video: {url}")
        return None

# Surah Al-Fatihah phrases
fatihah_phrases = {
    "1": "In the name",
    # "2": "of Allah",
    # "3": "the Most Gracious",
    # "4": "the Most Merciful",
    # "5": "All praises and thanks",
    # "6": "be to Allah",
    # "7": "the Lord",
    # "8": "of the universe",
    # "9": "The Most Gracious",
    # "10": "the Most Merciful",
    # "11": "The Master",
    # "12": "of the Day",
    # "13": "of the Judgment",
    # "14": "You Alone",
    # "15": "we worship",
    # "16": "and You Alone",
    # "17": "we ask for help",
    # "18": "Guide us",
    # "19": "to the path",
    # "20": "the straight",
    # "21": "The path",
    # "22": "of those",
    # "23": "You have bestowed Your Favors",
    # "24": "on them",
    # "25": "not of",
    # "26": "those who earned Your wrath",
    # "27": "on themselves",
    # "28": "and not",
    # "29": "of those who go astray"
}

# Run ASL matching
results = process_quranic_phrases(fatihah_phrases)

# Save to JSON file
with open("surah_fatihah_asl.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

print("Done! Results saved to surah_fatihah_asl.json")