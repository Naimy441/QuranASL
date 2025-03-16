import json

# Function to load the words from the .txt file and remove the numbers
def load_txt_words(txt_file):
    with open(txt_file, 'r', encoding='utf-8') as file:
        # Extract words from each line by splitting on the first space and keeping only the word
        txt_words = set(line.split(maxsplit=1)[1].strip() for line in file.readlines() if line.strip())
    return txt_words

# Load the dataset from the JSON file
with open('datasets/unique_words2.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Load words from the .txt file
txt_words = load_txt_words('datasets/wlasl_class_list.txt')

# Collect words from the JSON that are not in the .txt file
words_not_in_txt = {key: word for key, word in json_data.items() if word not in txt_words}

# Output the result
print("Words from JSON not in the .txt file:")
for key, word in words_not_in_txt.items():
    print(f"{key}: {word}")

# Optional: Save the result to a new JSON file
with open('datasets/missing.json', 'w', encoding='utf-8') as output_file:
    json.dump(words_not_in_txt, output_file, indent=4)

print("\nWords not in the .txt file have been saved to 'missing.json'.")