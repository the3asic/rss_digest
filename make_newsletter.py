import json
import os
import requests
import re
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_youtube_thumbnail(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc in ['www.youtube.com', 'youtu.be']:
        if parsed_url.netloc == 'youtu.be':
            video_id = parsed_url.path[1:]
        else:
            video_id = parse_qs(parsed_url.query).get('v', [None])[0]
        if video_id:
            return f"https://img.youtube.com/vi/{video_id}/0.jpg"
    return None

def get_og_image(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        og_image = soup.find('meta', property='og:image')
        if og_image:
            return og_image['content']
    except requests.RequestException:
        pass
    return None

def get_first_image(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        first_image = soup.find('img')
        if first_image and 'src' in first_image.attrs:
            return first_image['src']
    except requests.RequestException:
        pass
    return None

def get_thumbnail(url):
    thumbnail_url = get_youtube_thumbnail(url)
    if thumbnail_url and is_url_reachable(thumbnail_url):
        return thumbnail_url

    thumbnail_url = get_og_image(url)
    if thumbnail_url and is_url_reachable(thumbnail_url):
        return thumbnail_url

    thumbnail_url = get_first_image(url)
    if thumbnail_url and is_url_reachable(thumbnail_url):
        return thumbnail_url

    return None

def sanitize_filename(filename):
    # Remove or replace special characters
    filename = re.sub(r'[?<>:*|"\\/]', '', filename)
    filename = re.sub(r'[\s]+', '_', filename)  # Replace spaces with underscores
    filename = re.sub(r'[^\w\-_\.]', '', filename)  # Remove any remaining non-word characters
    return filename[:255]  # Truncate to max filename length

def download_thumbnail(url, filename):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    except requests.RequestException:
        return False

def is_url_reachable(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def write_titles_and_links(summaries, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for data in summaries.values():
            f.write(f"{data['chinese_title']}\n{data['url']}\n\n")

def main():
    # Load article summaries
    with open('article_summaries.json', 'r', encoding='utf-8') as f:
        summaries = json.load(f)

    # Create thumbnails directory
    thumbnails_dir = 'thumbnails'
    os.makedirs(thumbnails_dir, exist_ok=True)

    # Process each article
    for filename, data in summaries.items():
        url = data['url']
        thumbnail_url = get_thumbnail(url)
        
        if thumbnail_url:
            safe_filename = sanitize_filename(filename)
            thumbnail_filename = os.path.join(thumbnails_dir, f"{safe_filename.replace('.txt', '.jpg')}")
            if download_thumbnail(thumbnail_url, thumbnail_filename):
                data['thumbnail'] = os.path.relpath(thumbnail_filename)
            else:
                data['thumbnail'] = None
        else:
            data['thumbnail'] = None

    # Get title and font from environment variables
    title = os.getenv('NEWSLETTER_TITLE', '文章摘要通讯')
    font = os.getenv('NEWSLETTER_FONT', 'Arial, sans-serif')

    # Create newsletter using Jinja2 template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('newsletter_template.html')

    newsletter_html = template.render(articles=summaries.values(), title=title, font=font)

    # Save the newsletter
    with open('newsletter.html', 'w', encoding='utf-8') as f:
        f.write(newsletter_html)

    # Write titles and links to a text file
    write_titles_and_links(summaries, 'titles_and_links.txt')

    print("Newsletter created: newsletter.html")
    print("Titles and links saved: titles_and_links.txt")

if __name__ == "__main__":
    main()