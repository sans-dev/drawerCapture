import configparser
from pathlib import Path

def parse_config(config_file):
    config = configparser.ConfigParser()
    current_section = None
    current_dir = None
    choices_section = None

    with open(config_file, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            if line.startswith('/'):
                current_dir = line
            elif line == 'END':
                current_section = None
                current_dir = None
                choices_section = None
            else:
                key, value = line.split(':', 1)
                value = value.strip()

                if key == 'Label':
                    current_section = value
                    try:
                        config.add_section(current_section)
                    except configparser.DuplicateSectionError:
                        continue
                elif key == 'Readonly' and value == '0':
                    if current_dir:
                        config.set(current_section, 'setting_dir', current_dir)
                        config.set(current_section, 'setting', f"{current_dir}=")
                elif key == 'Current':
                    if current_dir:
                        config.set(current_section, 'current_choice', value)
                elif key == 'Type' and value == 'RADIO':
                    choices_section = f"{current_section} Choices"
                    config.add_section(choices_section)
                    config.set(current_section, 'Choices', choices_section)
                elif key == 'Choice' and choices_section:
                    choice_index, choice_value = value.split(' ', 1)
                    config.set(choices_section, choice_index, choice_value)
                    if choice_index == config.get(current_section, 'current_choice'):
                        config.set(current_section, 'setting', f"{current_dir}={choice_index}")

    return config

# Usage example
config_file = 'configs/fuji-gfx-100s.conf'
config = parse_config(config_file)

output_file = Path(config_file).stem + '.ini'
with open(output_file, 'w') as file:
    config.write(file)
