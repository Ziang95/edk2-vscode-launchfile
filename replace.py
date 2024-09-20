import json

# Input the path to your JSON file, the 'name' value to find, and new 'setupCommands'
json_file_path = '.vscode/launch.json'
name_value = 'FU540 GDB'
new_setup_commands_file = 'new_args'

def update_setup_commands(json_file, name_to_find, new_setup_commands_file):
    # Open and read the JSON file
    with open(json_file, 'r') as file:
        ori_data = json.load(file)

    with open(new_setup_commands_file, 'r') as file:
            file_content = file.read().strip()

    new_setup_commands = json.loads(file_content)

    configs = ori_data["configurations"]
    # Find the entry with the specified 'name'
    entry_found = False
    for entry in configs:
        if entry.get('name') == name_to_find:
            # print(f"Original 'setupCommands' for '{name_to_find}': {entry.get('setupCommands', 'Not found')}")
            # Replace the 'setupCommands' key value
            entry['setupCommands'] = new_setup_commands
            entry_found = True
            break

    if entry_found:
        # Write the updated JSON back to the file
        with open(json_file, 'w') as file:
            json.dump(ori_data, file, indent=4)
        # print(f"Updated 'setupCommands' for '{name_to_find}' with new value: {new_setup_commands}")
    else:
        print(f"Entry with name '{name_to_find}' not found in the JSON array.")

# Example usage
if __name__ == "__main__":
    # Update the setupCommands key in the JSON file
    update_setup_commands(json_file_path, name_value, new_setup_commands_file)
