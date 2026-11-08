import os
import re
import yaml
import requests

PRE_RELEASE_KEYWORDS = [
    'beta',
    'alpha',
    'legacy',
    'dev',
    'synology',
    'arm64',
    'amd64',
    'armhf',
    'armv7',
    'i386',
    'version-',
    '-ls',
    'ubuntu',
    'alpine',
]
RC_PATTERN = re.compile(r'(?:^|[-_.\d])rc(?:[-_.\d]|$)')


def get_latest_tag(repo_name):
    """
    Fetches the first page of tags for a Docker repository and returns the name
    of the most recently updated tag on that page that is not a pre-release
    or architecture/build-specific tag.
    """
    print(f"  Fetching first page of tags for {repo_name}...")
    tags_url = f'https://hub.docker.com/v2/repositories/{repo_name}/tags?page_size=100'

    try:
        response = requests.get(tags_url, timeout=30)
        response.raise_for_status()
        tags = response.json().get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching tags: {e}")
        return None

    if not tags:
        print("  No tags found on the first page.")
        return None

    # --- Filtering Logic ---
    candidate_tags = []

    for tag in tags:
        tag_name = tag['name'].lower()

        # 1. Filter out tags without a version number (like 'latest', 'stable')
        if not any(char.isdigit() for char in tag_name):
            continue

        # 2. Filter out pre-release and arch/build-specific versions
        if any(keyword in tag_name for keyword in PRE_RELEASE_KEYWORDS):
            continue
        if RC_PATTERN.search(tag_name):
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


def update_version_in_yaml(content, new_version):
    """Update the top-level version field in-place, preserving comments and formatting."""
    version_line = yaml.safe_dump(
        {'version': str(new_version)}, default_flow_style=False
    ).strip()
    updated, count = re.subn(
        r'^version:\s*.*$', version_line, content, count=1, flags=re.MULTILINE
    )
    return updated if count else None


for root, dirs, files in os.walk('.'):
    for file in files:
        if file == 'config.yaml':
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            config = yaml.safe_load(raw_content)

            if 'image' in config:
                print(f"Processing {file_path}...")
                current_version = str(config.get('version', ''))
                # An add-on pinned to a named tag such as 'edge' stays there
                # until its version is changed to a numbered release by hand.
                if not any(char.isdigit() for char in current_version):
                    print(f"  Skipping: pinned to the named tag '{current_version}'.")
                    print("-" * 20)
                    continue
                print(f"Checking for updates to image: {config['image']}")

                latest_tag = get_latest_tag(config['image'])

                if latest_tag:
                    print(f"  Current version: {current_version}, Latest available: {latest_tag}")
                    if current_version != latest_tag:
                        print(f"  UPDATE FOUND: Updating from {current_version} to {latest_tag}")
                        updated_content = update_version_in_yaml(raw_content, latest_tag)
                        if updated_content is not None:
                            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                                f.write(updated_content)
                        else:
                            config['version'] = latest_tag
                            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                                yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)
                    else:
                        print("  Already up to date.")
                else:
                    print(f"  Could not determine the latest tag for {config['image']}.")
                print("-" * 20)
