import json

with open('politics_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('data.js', 'w', encoding='utf-8') as f:
    f.write('window.POLITICS_DATA = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';')

print("Exported data.js successfully!")
