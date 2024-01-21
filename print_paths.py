import os
import sys

folder_path = f"outputs-interpolation/{sys.argv[1]}/"

spec = sys.argv[2]
postfix = "output"

# Loop through files in the folder and its subfolders
for folder_path, _, filenames in os.walk(folder_path):
    for filename in filenames:

        # Check if both substrings are present in the file name
        if spec in filename and postfix in filename:
            # Generate a clickable link with file URI
            file_path = os.path.join(folder_path, filename)
            print(file_path)
