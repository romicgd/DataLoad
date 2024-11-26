import os
import re
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from get_cookies import get_valid_cookies
import hashlib
from datetime import datetime

# Load cookies for authentication
cookies = get_valid_cookies()

if not cookies:
    print("Failed to retrieve valid cookies. Exiting.")
    exit()

start_url = "https://www.sa.mcss.gov.on.ca/"
base_url = "https://www.sa.mcss.gov.on.ca"

# Folder setup
output_folder = "downloaded_content"
docx_folder = os.path.join(output_folder, "docx_files")
pdf_folder = os.path.join(output_folder, "pdf_files")
ppt_folder = os.path.join(output_folder, "ppt_files")
xlsx_folder = os.path.join(output_folder, "xlsx_files")
html_folder = os.path.join(output_folder, "html_files")

os.makedirs(docx_folder, exist_ok=True)
os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(ppt_folder, exist_ok=True)
os.makedirs(xlsx_folder, exist_ok=True)
os.makedirs(html_folder, exist_ok=True)

def clean_filename(link_text):
    link_text = re.sub(r' \(DOC.*?\)| \(PDF.*?\)| \(PPT.*?\)| \(XLS.*?\)', '', link_text).strip()
    sanitized = re.sub(r'[^\w\-_\. ]', '_', link_text)
    return sanitized[:200]

def get_file_extension(content_type):
    if content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return 'docx'
    elif content_type == 'application/msword':
        return 'doc'
    elif content_type == 'application/pdf':
        return 'pdf'
    elif content_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        return 'pptx'
    elif content_type == 'application/vnd.ms-powerpoint':
        return 'ppt'
    elif content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        return 'xlsx'
    elif content_type == 'application/vnd.ms-excel.sheet.macroenabled.12':
        return 'xlsm'
    return None

def download_file(file_url, link_text, created_date, audience, tag):
    filename_safe_text = clean_filename(link_text)
    response = requests.get(file_url, cookies=cookies, allow_redirects=True)
    content_type = response.headers.get('Content-Type')
    file_extension = get_file_extension(content_type)

    if not file_extension:
        print(f"Unsupported file extension for URL: {file_url}")
        return None, None, None, None, None, False

    if file_extension in ['docx', 'doc']:
        file_path = os.path.join(docx_folder, f"{filename_safe_text}.{file_extension}")
    elif file_extension == 'pdf':
        file_path = os.path.join(pdf_folder, f"{filename_safe_text}.{file_extension}")
    elif file_extension in ['ppt', 'pptx']:
        file_path = os.path.join(ppt_folder, f"{filename_safe_text}.{file_extension}")
    elif file_extension in ['xlsx', 'xlsm']:
        file_path = os.path.join(xlsx_folder, f"{filename_safe_text}.{file_extension}")
    else:
        print(f"Unsupported file extension for URL: {file_url}")
        return None, None, None, None, None, False

    if os.path.exists(file_path):
        print(f"Skipped file because it already exists: {file_path}")
        return file_url, file_path, created_date, audience, tag, True

    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        if not created_date:
            created_date = datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        return file_url, file_path, created_date, audience, tag, False
    else:
        print(f"Failed to download {file_url}. Status code: {response.status_code}")
        return None, None, None, None, None, False

def hash_content(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def content_exists(folder, new_content):
    new_content_hash = hash_content(new_content)
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".html"):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                    existing_content_hash = hash_content(existing_content)
                    if new_content_hash == existing_content_hash:
                        return True
    return False

def extract_metadata(parent_element):
    date_text = parent_element.find("div", class_="entry-meta")
    audience_text = parent_element.find("div", class_="entry-meta-audience")
    tag_text = parent_element.find("div", class_="entry-meta").find("li")
    created_date = None
    audience = None
    tag = None
    
    if date_text:
        date_match = re.search(r'Updated\s+(\w+\s+\d{1,2},\s+\d{4})', date_text.get_text())
        if date_match:
            created_date = date_match.group(1)
    
    if audience_text:
        audience_li = audience_text.find_all("li")
        if len(audience_li) > 1:
            audience = audience_li[1].text.strip()
    
    if tag_text:
        tag = tag_text.text.strip()
    
    return created_date, audience, tag

def read_existing_metadata(csv_file):
    existing_metadata = {}
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_metadata[row['downloadable_file_link']] = row
    return existing_metadata

def scrape_page(url, csv_writer, skipped_writer, visited, existing_metadata):
    if url in visited:
        return
    visited.add(url)

    parsed_url = urlparse(url)
    if parsed_url.fragment:
        print(f"Skipping URL with fragment: {url}")
        return

    print(f"Scraping URL: {url}")
    response = requests.get(url, cookies=cookies)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return

    html_content = response.text

    if content_exists(html_folder, html_content):
        print(f"Content already exists, skipping saving: {url}")
        return

    sanitized_path = clean_filename(parsed_url.path.lstrip('/'))
    if not sanitized_path:
        sanitized_path = "index"
    html_file_path = os.path.join(html_folder, sanitized_path + ".html")

    counter = 1
    unique_html_file_path = html_file_path
    while os.path.exists(unique_html_file_path):
        unique_html_file_path = html_file_path.replace(".html", f"_{counter}.html")
        counter += 1

    os.makedirs(os.path.dirname(unique_html_file_path), exist_ok=True)

    with open(unique_html_file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML content of the current page saved to {unique_html_file_path}")

    soup = BeautifulSoup(html_content, "html.parser")

    links = soup.find_all("a", href=True)
    file_links = []

    for link in links:
        href = link["href"]
        if any(ext in link.text.upper() for ext in ["DOC", "PDF", "PPT", "XLS"]):
            file_links.append((href, link.text.strip(), link.find_parent("header")))

    if not file_links:
        print("No DOCX, PDF, PPT, or XLS links found on the page.")
    else:
        print(f"Found {len(file_links)} file links.")

    for file_url, link_text, parent_element in file_links:
        created_date, audience, tag = extract_metadata(parent_element) if parent_element else (None, None, None)
        if not file_url.startswith("http"):
            file_url = urljoin(base_url, file_url)
        
        existing_file_data = existing_metadata.get(file_url)
        if existing_file_data:
            if (created_date != existing_file_data['created_date'] or
                audience != existing_file_data['audience'] or
                tag != existing_file_data['tag']):
                print(f"Metadata changed for {file_url}, updating...")
                file_url, file_filename, created_date, audience, tag, skipped = download_file(file_url, link_text, created_date, audience, tag)
                if file_url and file_filename:
                    csv_writer.writerow([url, file_url, file_filename, created_date, audience, tag])
            else:
                print(f"No metadata changes for {file_url}, skipping...")
                skipped_writer.writerow([url, file_url, existing_file_data['file_name'], created_date, audience, tag])
        else:
            file_url, file_filename, created_date, audience, tag, skipped = download_file(file_url, link_text, created_date, audience, tag)
            if file_url and file_filename:
                csv_writer.writerow([url, file_url, file_filename, created_date, audience, tag])

    for link in links:
        href = link["href"]
        if not href.startswith("http"):
            href = urljoin(base_url, href)
        scrape_page(href, csv_writer, skipped_writer, visited, existing_metadata)

metadata_file_path = os.path.join(output_folder, "metadata.csv")

existing_metadata = read_existing_metadata(metadata_file_path)

with open(metadata_file_path, "w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["current_url", "downloadable_file_link", "file_name", "created_date", "audience", "tag"])

    with open(os.path.join(output_folder, "skippedfiles.csv"), "w", newline="", encoding="utf-8") as skippedfile:
        skipped_writer = csv.writer(skippedfile)
        skipped_writer.writerow(["current_url", "downloadable_file_link", "file_name", "created_date", "audience", "tag"])

        visited_urls = set()
        scrape_page(start_url, csv_writer, skipped_writer, visited_urls, existing_metadata)

print("Process completed.")
