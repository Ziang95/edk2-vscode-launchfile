import re
from elftools.elf.elffile import ELFFile

log_file = './qemu_uart.log'  # Replace with the path to your UEFI boot log file
sec_sym = '/Path/to/Sec/SecMain/DEBUG/SecMain.debug' # Replace with the path to SecMain symbol file. SecMain is special hence needs to be treated separatly.
header_offset = 0x80002000

def analyze_uefi_log(log_file):
    with open(log_file, 'r') as file:
        lines = file.readlines()

    # Adjusted to account for spaces before "Image - " and now checking for ".dll"
    image_pattern = re.compile(r'^\s*Image\s-\s.*\.dll$')
    hex_pattern = re.compile(r'0x[0-9A-Fa-f]+')
    set_uefi_pattern = re.compile(r'^SetUefiImageMemoryAttributes')

    results = []

    with open(sec_sym, 'rb') as f:
        elf = ELFFile(f)
        sec_secs = {}
        for section in elf.iter_sections():
            if section.name == '.text':
                tmp_txt = section['sh_addr'] + header_offset
            if section.name == '.data':
                tmp_data = section['sh_addr'] + header_offset
            if section.name == '.entry':
                tmp_entry = section['sh_addr'] + header_offset
    results.append({
        'description': 'SecMain',
        'text': f'add-symbol-file {sec_sym} -s .text {hex(tmp_txt)} -s .entry {hex(tmp_entry)} -s .data {hex(tmp_data)}',
        'ignoreFailures': "false"
    })

    # Iterate through the log file
    for i in range(len(lines)):
        # Check if the current line matches the "Image - " and ".dll" pattern
        if image_pattern.match(lines[i].strip()):
            # Check if the next three lines start with "SetUefiImageMemoryAttributes"
            if i + 3 < len(lines):
                if (set_uefi_pattern.match(lines[i + 1].strip()) and 
                    set_uefi_pattern.match(lines[i + 2].strip()) and 
                    set_uefi_pattern.match(lines[i + 3].strip())):
                    
                    # Extract the description (last word separated by "/")
                    description_match = re.search(r'/(\w+)\.dll$', lines[i].strip())
                    if description_match:
                        description = description_match.group(1)

                    # Create the "text" value by replacing ".dll" with ".debug"
                    text_value = lines[i].strip().replace(".dll", ".debug")

                    # Extract the offset of the "text" segment from the second line below the "Image - " line
                    if i + 2 < len(lines):
                        second_line_below = lines[i + 2].strip()
                        text_segment_offset = hex_pattern.search(second_line_below)
                    
                    # Extract the offset of the "data" segment from the third line below the "Image - " line
                    if i + 3 < len(lines):
                        third_line_below = lines[i + 3].strip()
                        data_segment_offset = hex_pattern.search(third_line_below)

                    # Only proceed if both text and data segment offsets are found
                    if text_segment_offset and data_segment_offset:
                        # Add the "-s .text" and "-s .data" fields to the text
                        text_value_with_segments = f'add-symbol-file ' + f'{text_value.replace("Image - ", "").strip()} -s .text {text_segment_offset.group()} -s .data {data_segment_offset.group()}'
                        
                        # Append the dictionary to the results list
                        results.append({
                            'description': description,
                            'text': text_value_with_segments,
                            'ignoreFailures': "false"
                        })

    return results


# Example usage
hex_values = analyze_uefi_log(log_file)

print('[')
for idx in range(len(hex_values)):
    print('{')
    hex_value = hex_values[idx]
    for idx_2, key_2 in enumerate(hex_value):
        print(f'\t\"{key_2}\": ', end = '')
        if hex_value[key_2] == 'false' or hex_value[key_2] == 'true':
            print(hex_value[key_2], end = '')
        else:
            print(f'\"{hex_value[key_2]}\"', end = '')
        if idx_2 >= len(hex_value) - 1:
            continue
        print(',')
    print('}', end = '')
    if idx >= len(hex_values) - 1:
        continue
    print(',')
print(']')
