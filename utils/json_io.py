import json


def json_write(json_data, json_path):
    with open(json_path, "w", encoding="utf-8") as f:
        if isinstance(json_data, str):
            f.write(json.loads(json_data))
        elif isinstance(json_data, dict):
            f.write(json_data)

