import json
import os
from pathlib import Path


def collect_json(json_paths: list[str]):
    assert isinstance(json_paths, list)
    out = list()
    for start_path in json_paths:
        start_path = os.path.expanduser(start_path)
        if os.path.isdir(start_path):
            for root, directories, files in os.walk(start_path):
                for file in files:
                    target_path = os.path.join(root, file)
                    if os.path.isfile(target_path) and os.path.splitext(target_path)[1].lower() == '.json':
                        with open(target_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        assert isinstance(data, list)
                        out.extend(data)
        else:
            with open(start_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert isinstance(data, list)
            out.extend(data)

    return out


if __name__ == "__main__":
    in_path = ""
    out_path = ""
    data = collect_json([in_path])

    Path(out_path).write_text(json.dumps(data, indent=4))
