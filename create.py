import string

# Define the keys to include
letters = string.ascii_lowercase + string.ascii_uppercase
numbers = string.digits
special_characters = ['`', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '{', '}', '[', ']', '\\', '|', ';', ':', '\'', '"', ',', '.', '/', '<', '>', '?']
space = [' ']

# Combine all keys
all_keys = letters + numbers + ''.join(special_characters) + ''.join(space)

# Format the keys into the specified format
key_mapping = [f"{key} : {key}" for key in all_keys]

# Write the output to a file
file_path = 'train.txt'
with open(file_path, 'w') as file:
    file.write("\n".join(key_mapping))

print(f"File created at: {file_path}")

