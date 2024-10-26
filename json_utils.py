import json
import os

def append_to_json_file(data, filename='data.json'):
    try:
        # 기존 데이터를 읽어옵니다.
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                existing_data = json.load(file)
        else:
            existing_data = []

        # 새로운 데이터를 추가합니다.
        existing_data.append(data)

        # 파일에 저장합니다.
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error writing to JSON file: {e}")

def save_to_json_file(data, filename):
    try:
        # 데이터를 파일에 덮어씁니다.
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {filename}.")
    except Exception as e:
        print(f"Error writing to JSON file: {e}")