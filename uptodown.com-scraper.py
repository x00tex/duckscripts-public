#!/opt/homebrew/bin/python3.11

"""
Author: poorduck
Date: 2024-07-24
"""

import argparse
import requests
import json
from bs4 import BeautifulSoup
import subprocess
import os
from rich.console import Console
import sys

class DataHandler:
    def __init__(self, host, file_id):
        self.host = host
        self.file_id = file_id
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0"
        }
        self.data_file = f"{file_id}.json"
        self.console = Console()

    def fetch_data(self):
        combined_data = []
        i = 1
        while True:
            url = f"{self.host}/android/apps/{self.file_id}/versions/{i}"
            try:
                response = self.session.get(url)
                response.raise_for_status()
                data = response.json()
                if data.get('success') == 1 and data.get('data'):
                    for item in data['data']:
                        fileID = item.get('fileID')
                        if fileID:
                            item['post-download'] = f"{self.host}/android/download/{fileID}"
                    combined_data.extend(data.get('data', []))
                else:
                    break
            except requests.exceptions.RequestException as e:
                print(f"Request failed for ID {i}: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"JSON decode error for ID {i}: {e}")
                break
            i += 1
        
        # Save the fetched data to the file
        with open(self.data_file, 'w') as outfile:
            json.dump(combined_data, outfile, indent=4)
        
        return combined_data

    def check_and_fetch_data(self):
        if not os.path.exists(self.data_file):
            combined_data = self.fetch_data()
        else:
            # print("Data already exists!")
            with open(self.data_file, 'r') as f:
                combined_data = json.load(f)
        return combined_data

    def download_files(self, data, enable_download, specific_file_id=None):
        if not enable_download and not specific_file_id:
            print("Downloading is disabled.")
            return

        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.2; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]

        try:
            for idx, item in enumerate(data):
                if specific_file_id and item.get('fileID') != int(specific_file_id):
                    continue

                post_download_url = item.get('post-download')
                if post_download_url:
                    try:
                        response = self.session.get(post_download_url)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.content, 'html.parser')
                        div_tag = soup.find('button', class_='button download')
                        if div_tag and div_tag.has_attr('data-url'):
                            data_url = div_tag['data-url']
                            download_url = f"https://dw.uptodown.com/dwn/{data_url}"

                            user_agent = user_agents[idx % len(user_agents)]
                            command = ["aria2c", "--user-agent", user_agent, download_url, "-c"]

                            # Display which file is being downloaded
                            with self.console.status(f"[bold green]Downloading:[/bold green] {item.get('version')}", spinner="dots"):
                                try:
                                    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                                except subprocess.CalledProcessError as e:
                                    self.console.print(f"[red]Failed to download {download_url} with user-agent {user_agent}: {e}[/red]")
                    except requests.exceptions.RequestException as e:
                        self.console.print(f"[red]Request failed for post-download URL {post_download_url}: {e}[/red]")
                    except Exception as e:
                        self.console.print(f"[red]Failed to process post-download URL {post_download_url}: {e}[/red]")
        except KeyboardInterrupt:
            self.console.print("[red]Download interrupted by user. Exiting...[/red]")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Fetch and process data from a server.")
    parser.add_argument('-host', required=True, type=str, help='The host URL')
    parser.add_argument('-id', required=True, type=str, help='The file ID to fetch data for')
    parser.add_argument('-d', action='store_true', help='Enable downloading of all files')
    parser.add_argument('-did', type=int, help='Specific file ID to download (expects data file to exist)')

    args = parser.parse_args()

    data_handler = DataHandler(args.host, args.id)
    data = data_handler.check_and_fetch_data()
    data_handler.download_files(data, args.d, args.did)

if __name__ == "__main__":
    main()
