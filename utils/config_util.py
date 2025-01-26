import os


def get_or_create_config(key):
    config_folder = "configs"
    if not os.path.exists(config_folder):
        os.mkdir(config_folder)
    config_path = os.path.join(config_folder, key)
    if not os.path.exists(config_path):
        value = ""
        while not value:
            value = input("Please input the value of the key:").strip().strip('"')
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(value)
    else:
        with open(config_path, "r", encoding="utf-8") as f:
            value = f.read().strip()
    return value
