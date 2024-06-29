import re
from urllib import request
from bs4 import BeautifulSoup


def get_latest_daily_build_url():
    try:
        resp = request.urlopen("https://builder.blender.org/download/daily/")
        soup = BeautifulSoup(resp, 'html.parser')

        # Find all <a> tags with href matching the specific pattern
        releases = soup.find_all('a', href=re.compile(
            r"https://cdn\.builder\.blender\.org/download/daily/blender-\d+\.\d+\.\d+-\w+\+\w+\.\w+-linux\.x86_64-release\.tar\.xz"))

        # Filter out URLs containing '.sha256'
        releases = [release['href']
                    for release in releases if '.sha256' not in release['href']]

        # Return only the latest version (assuming list is sorted in descending order by version)
        if releases:
            return [releases[0]]
        else:
            return None

    except Exception as e:
        print(f"Error fetching or parsing data: {e}")
        return None


if __name__ == "__main__":
    download_urls = get_latest_daily_build_url()
    if download_urls:
        for url in download_urls:
            print(url)
    else:
        print("Failed to find the latest daily Blender build download URL.")
