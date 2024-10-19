import os
import yaml
import requests

def get_latest_tag(repo_name):
    tags_url = f'https://hub.docker.com/v2/repositories/{repo_name}/tags'
    response = requests.get(tags_url)
    response.raise_for_status()
    tags = response.json()['results']
    version_tags = [tag['name'] for tag in tags if any(char.isdigit() for char in tag['name'])]
    return sorted(version_tags, reverse=True)[0] if version_tags else None

for root, dirs, files in os.walk('.'):
    for file in files:
        if file == 'config.yaml':
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
            if 'image' in config:
                print(f'Getting latest version of {config['image']}')
                latest_tag = get_latest_tag(config['image'])
                print(f'Latest version of {config['image']} is {latest_tag}')
                if latest_tag and config.get('version') != latest_tag:
                    print(f'Updating {file_path} from {config.get('version')} to {latest_tag}')
                    config['version'] = latest_tag
                    with open(file_path, 'w') as f:
                        yaml.dump(config, f)
