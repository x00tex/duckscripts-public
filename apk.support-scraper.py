#!/Users/poorduck/projects/.project-env/bin/python

"""
Author: poorduck
Date: 2024-08-07
"""

import json
import argparse
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import shutil

def extract_download_link(driver, data, package_name, debug=False):
    for item in data:
        # Skip items that already have a download link
        if 'download_link' in item and item['download_link']:
            if debug:
                print(f"Skipping version {item['version_name']} as it already has a download link.")
            continue

        version_code = item['version_code']
        version_name = item['version_name']
        base_url = f"https://apk.support/download-app/{package_name}/{version_code}/{version_name}"

        if debug:
            print(f"Navigating to: {base_url}")

        driver.get(base_url)

        try:
            # Execute JavaScript to send POST request
            script = """
            var xhr = new XMLHttpRequest();
            xhr.open('POST', window.location.href, true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.onload = function() {{
                if (xhr.status === 200) {{
                    document.body.innerHTML = xhr.responseText;
                }}
            }};
            xhr.send('cmd=apk&pkg={pkg}&arch=default&tbi=default&device_id=&model=default&language=en&dpi=default&av=default&vc={vc}&gc=');
            """.format(pkg=package_name, vc=version_code)

            driver.execute_script(script)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'bdlinks'))
            )
            if debug:
                print("Page loaded successfully")

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            download_div = soup.find('div', class_='bdlinks')

            if not download_div:
                if debug:
                    print("Download div not found in the response.")
                item['download_link'] = None
                continue

            download_link = download_div.find('a', rel='nofollow')
            if download_link:
                href = download_link['href']
                if debug:
                    print(f"Download link found: {href}")
                item['download_link'] = href
            else:
                if debug:
                    print("Download link not found.")
                item['download_link'] = None

        except Exception as e:
            if debug:
                print(f"Error while extracting download link: {e}")
            item['download_link'] = None

    return data

def extract_data_from_pages(base_url, driver, package_name, debug):
    page = 1
    all_data = []

    while True:
        url = f"{base_url}?page={page}"
        if debug:
            print(f"Fetching URL: {url}")  # Debugging statement
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'other_version'))
            )
            if debug:
                print("Page loaded successfully")  # Debugging statement
        except Exception as e:
            if debug:
                print(f"Error waiting for page to load: {e}")
            break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        other_versions = soup.find('div', class_='other_version')
        if debug:
            print(f"Found 'other_version' div: {other_versions is not None}")  # Debugging statement

        if not other_versions:
            break

        for li in other_versions.find_all('li'):
            anchor = li.find('a')
            if anchor:
                href = anchor['href']
                verlist = anchor.find('p', class_='verlist').text
                release_date = anchor.find_all('p')[1].text
                size = anchor.find_all('p')[2].text

                version_code = href.split('/')[-2]
                version_name = href.split('/')[-1]

                data = {
                    'href': href,
                    'version': verlist,
                    'release_date': release_date,
                    'size': size,
                    'version_code': version_code,
                    'version_name': version_name
                }
                all_data.append(data)
                if debug:
                    print(f"Extracted data: {data}")  # Debugging statement

        page += 1

    return json.dumps(all_data, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Scrape app versions from a given package name.')
    parser.add_argument('package_name', type=str, help='The package name of the app (e.g., com.mudah.my).')
    parser.add_argument('--chromedriver-path', type=str, help='The path to the ChromeDriver executable.', default=shutil.which("chromedriver"))
    parser.add_argument('--debug', action='store_true', help='Enable debug mode for additional output.')
    args = parser.parse_args()

    package_name = args.package_name
    output_file = f"{package_name}.json"
    download_links_file = f"{package_name}-downloadlinks.json"

    # Check if the output file already exists and contains data
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        print(f"The file {output_file} already exists and contains data. Skipping extraction from pages.")
        # Load data from the output file
        with open(output_file, 'r') as file:
            data = json.load(file)
    else:
        base_url = f'https://apk.support/app/{package_name}/versions'

        # Set up Selenium WebDriver
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Comment out headless mode for debugging
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(service=Service(args.chromedriver_path), options=options)

        try:
            json_data = extract_data_from_pages(base_url, driver, package_name, args.debug)

            with open(output_file, 'w') as file:
                file.write(json_data)
                print(f"Data written to {output_file}")

            data = json.loads(json_data)

        except Exception as e:
            print(f"An error occurred: {e}")
        except KeyboardInterrupt as e:
            exit(e)
        finally:
            driver.quit()

    # Check if the download links file already exists and load data if it does

    
    if os.path.exists(download_links_file) and os.path.getsize(download_links_file) > 0:
        print(f"The file {download_links_file} already exists. Loading data and checking for missing download links.")
        with open(download_links_file, 'r') as file:
            existing_data = json.load(file)
        
        # Create a dictionary to quickly access existing data by version_code
        existing_data_dict = {item['version_code']: item for item in existing_data}

        # Update the data with existing download links
        for item in data:
            if item['version_code'] in existing_data_dict:
                item['download_link'] = existing_data_dict[item['version_code']].get('download_link')

    else:
        print(f"The file {download_links_file} does not exist. Extracting download links from scratch.")
    
    # Set up Selenium WebDriver for extracting download links
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Comment out headless mode for debugging
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=Service(args.chromedriver_path), options=options)

    # Extract download links
    try:
        data_with_links = extract_download_link(driver, data, package_name, args.debug)

        # Save data with download links to the download links file
        with open(download_links_file, 'w') as file:
            json.dump(data_with_links, file, indent=4)
            print(f"Data with download links written to {download_links_file}")

    except Exception as e:
        print(f"An error occurred while extracting download links: {e}")
    except KeyboardInterrupt as e:
        exit(e)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
