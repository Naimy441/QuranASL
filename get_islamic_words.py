import os

# Path to the folder
folder_path = "islam_vids"

# Get all filenames in the folder
filenames = os.listdir(folder_path)

# Extract filenames without extensions, sort them, and convert to uppercase
filenames_without_ext = sorted([os.path.splitext(filename)[0].upper() for filename in filenames])

# Join the filenames into a comma-separated string
filenames_csv = ", ".join(filenames_without_ext)

# Print the result
print(filenames_csv)