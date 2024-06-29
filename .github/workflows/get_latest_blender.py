import re
import requests

def get_latest_daily_build_url():
    url = "https://builder.blender.org/download/daily/"
    response = requests.get(url)
    page_content = response.text

    # Find the download link for the latest daily build
    match = re.search(r"https://cdn\.builder\.blender\.org/download/daily/blender-\d+\.\d+\.\d+-\w+\.\w{12}-linux\.x86_64-release\.tar\.xz", page_content)
    
    if match:
        return match.group(0)
    return None

if __name__ == "__main__":
    #download_url = get_latest_daily_build_url()
    download_url = 'https://cdn.builder.blender.org/download/daily/blender-4.3.0-alpha+main.4162aeee5f91-linux.x86_64-release.tar.xz'
    if download_url:
        print(download_url)
    else:
        print("Failed to find the latest daily Blender build download URL.")
