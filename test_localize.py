import json
from urllib.parse import urlparse
import re

def _localize_json_urls(json_tree: dict, design_name: str) -> tuple[dict, dict]:
    url_mapping = {}
    counter = [0]

    def _make_local_name(remote_url: str) -> str:
        parsed = urlparse(remote_url)
        path = parsed.path
        ext = '.png'
        if '.' in path.split('/')[-1]:
            ext = '.' + path.split('/')[-1].rsplit('.', 1)[-1]
            if ext.lower() not in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'):
                ext = '.png'
        counter[0] += 1
        return f"img_{counter[0]}{ext}"

    def _replace_css_url(match):
        url = match.group(1).strip('\'"')
        if not url or not url.startswith('http'):
            return match.group(0)
        local_name = _make_local_name(url)
        local_path = f"./assets/slices/{local_name}"
        url_mapping[local_path] = url
        return f"url('{local_path}')"

    def _traverse(node):
        if isinstance(node, dict):
            for key, value in list(node.items()):
                if isinstance(value, str):
                    if key in ('src', 'url', 'image') and value.startswith('http'):
                        local_name = _make_local_name(value)
                        local_path = f"./assets/slices/{local_name}"
                        url_mapping[local_path] = value
                        node[key] = local_path
                    elif key == 'backgroundImage' and 'url(' in value:
                        node[key] = re.sub(r'url\(([\'"]*https?://[^\)]*)\)', _replace_css_url, value)
                elif isinstance(value, (dict, list)):
                    _traverse(value)
        elif isinstance(node, list):
            for item in node:
                _traverse(item)

    _traverse(json_tree)
    return json_tree, url_mapping

with open('/home/jettm/ppWorkspace/lanhu-mcp/data/lanhu_designs/186f8d15-3d6c-49da-b507-895b702d1c40/design_analysis_result_1775139819.txt', 'r') as f:
    text = f.read()

# Extract JSON string
start = text.find('```json\n') + 8
end = text.find('\n   ```', start)
json_str = text[start:end]

try:
    data = json.loads(json_str)
    new_data, mapping = _localize_json_urls(data, "test")
    print("Mapping found:", mapping)
    print("First image path in data:", new_data['children'][0]['children'][0]['children'][1]['children'][0]['children'][0]['src'])
except Exception as e:
    print("Error:", e)
