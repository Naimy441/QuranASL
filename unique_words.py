import json
import re
import string

def get_unique_1():
    # Load the dataset from the JSON file
    with open('datasets/en-qurancom.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Function to clean, remove punctuation (except dashes), and split the string
    def clean_and_split(text):
        # Remove escaped quotes (\"), any text within parentheses or square brackets
        text = re.sub(r'\\\"', '', text)  # Remove escaped quotes
        text = re.sub(r'[\(\[].*?[\)\]]', '', text)  # Matches both () and []

        # Remove leading/trailing quotes if any
        text = text.strip('"')

        # Remove punctuation using string.punctuation, but keep the dash
        punctuation = string.punctuation.replace('-', '')  # Remove dash from punctuation
        text = re.sub(r'[{}]'.format(punctuation), '', text)

        # Convert text to lowercase
        text = text.lower()

        # Remove extra spaces and split by spaces
        words = text.strip().split()
        return words

    # Set to store unique words
    unique_words = set()

    # Iterate through the JSON data
    for key, value in data.items():
        words = clean_and_split(value)
        unique_words.update(words)

    # Convert the set back to a list and sort it
    unique_words_list = sorted(list(unique_words))

    # Output as a JSON file
    output_data = {i+1: word for i, word in enumerate(unique_words_list)}

    # Save to a JSON file
    with open('datasets/unique_words.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)

    print("Unique words have been saved to 'unique_words.json'.")

def get_unique_2():
    # Load the dataset from the JSON file
    with open('datasets/quran_verses.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Function to clean, remove punctuation (except dashes), and split the string
    def clean_and_split(text):
        # Remove escaped quotes (\"), any text within parentheses or square brackets
        text = re.sub(r'\\\"', '', text)  # Remove escaped quotes
        text = re.sub(r'[\(\[].*?[\)\]]', '', text)  # Matches both () and []

        # Remove leading/trailing quotes if any
        text = text.strip('"')

        # Remove punctuation using string.punctuation, but keep the dash
        punctuation = string.punctuation.replace('-', '')  # Remove dash from punctuation
        text = re.sub(r'[{}]'.format(punctuation), '', text)

        # Convert text to lowercase
        text = text.lower()

        # Remove extra spaces and split by spaces
        words = text.strip().split()
        return words

    # Set to store unique words
    unique_words = set()

    # Iterate through the surahs and their verses
    for surah_key, surah_data in data.items():
        verses = surah_data.get("verses", [])
        for verse in verses:
            words = clean_and_split(verse)
            unique_words.update(words)

    # Convert the set back to a list and sort it
    unique_words_list = sorted(list(unique_words))

    # Output as a JSON file
    output_data = {i+1: word for i, word in enumerate(unique_words_list)}

    # Save to a JSON file
    with open('datasets/unique_words2.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)

    print("Unique words have been saved to 'unique_words2.json'.")

get_unique_2()