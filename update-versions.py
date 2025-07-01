import os
import yaml
import requests

def get_latest_tag(repo_name):
    """
    Fetches the first page of tags for a Docker repository and returns the name
    of the most recently updated tag on that page that is not a pre-release.
    """
    print(f"  Fetching first page of tags for {repo_name}...")
    tags_url = f'https://hub.docker.com/v2/repositories/{repo_name}/tags'

    try:
        response = requests.get(tags_url)
        response.raise_for_status()
        tags = response.json().get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching tags: {e}")
        return None

    if not tags:
        print("  No tags found on the first page.")
        return None

    # --- Filtering Logic ---
    pre_release_keywords = ['beta', 'alpha', 'rc']
    candidate_tags = []

    for tag in tags:
        tag_name = tag['name'].lower()
        
        # 1. Filter out tags without a version number (like 'latest', 'stable')
        if not any(char.isdigit() for char in tag_name):
            continue
            
        # 2. Filter out pre-release versions
        if any(keyword in tag_name for keyword in pre_release_keywords):
            continue

        # 3. Ensure the tag has a timestamp to sort by
        if tag.get('last_updated'):
            candidate_tags.append(tag)

    if not candidate_tags:
        print("  No suitable version tags found on the first page after filtering.")
        return None

    # --- Sorting Logic ---
    # Sort the candidates by the 'last_updated' timestamp, descending.
    # The ISO 8601 date format ("2022-12-20T16:05:07.03921Z") can be sorted as a string.
    sorted_tags = sorted(
        candidate_tags,
        key=lambda t: t['last_updated'],
        reverse=True
    )

    # The most recent tag is the first one in the sorted list.
    latest_tag_name = sorted_tags[0]['name']
    return latest_tag_name

for root, dirs, files in os.walk('.'):
    for file in files:
        if file == 'config.yaml':
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)

            if 'image' in config:
                print(f"Processing {file_path}...")
                print(f"Checking for updates to image: {config['image']}")

                latest_tag = get_latest_tag(config['image'])
                
                if latest_tag:
                    current_version = config.get('version')
                    print(f"  Current version: {current_version}, Latest available: {latest_tag}")
                    if current_version != latest_tag:
                        print(f"  UPDATE FOUND: Updating from {current_version} to {latest_tag}")
                        config['version'] = latest_tag
                        with open(file_path, 'w') as f:
                            yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)
                    else:
                        print("  Already up to date.")
                else:
                    print(f"  Could not determine the latest tag for {config['image']}.")
                print("-" * 20)
