
import yaml

def add_to_blocklist(new_name, filepath="blocked_employers.yaml"):
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    if new_name not in data["blocked_employers"]:
        data["blocked_employers"].append(new_name)
        with open(filepath, "w") as f:
            yaml.dump(data, f)
        print(f"{new_name} added to blocklist.")
    else:
        print(f"{new_name} already in blocklist.")
