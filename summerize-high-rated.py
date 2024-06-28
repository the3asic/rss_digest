import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime
import re
import pangu  # Import pangu

# Load environment variables
load_dotenv()

# Set up custom API endpoint and key
CUSTOM_API_URL = os.getenv("CUSTOM_API_URL")
API_KEY = os.getenv("API_KEY")

def read_article(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_summary(file_path, summary):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(summary)

def extract_url_and_title(content):
    lines = content.split('\n')
    url = ''
    title = ''
    
    for line in lines:
        if line.startswith('URL:'):
            url = line.replace('URL:', '').strip()
        elif line.startswith('Title:'):
            title = line.replace('Title:', '').strip()
        
        if url and title:
            break
    
    return url, title

def get_chinese_title_and_summary(title, content, url):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Translate title
    title_payload = {
        "model": "gpt-4o",  # Updated model
        "messages": [
            {"role": "system", "content": "You are a translator. Translate the given title to Chinese (zh-CN). Output only the translated title without any additional text."},
            {"role": "user", "content": f"Translate this title to Chinese:\n\n{title}"}
        ]
    }
    
    # Summarize and translate content
    content_payload = {
        "model": "gpt-4o",  # Updated model
        "messages": [
            {"role": "system", "content": "You are an AI assistant that summarizes articles in Chinese (zh-CN). Provide a concise summary in about 3-5 sentences in Chinese."},
            {"role": "user", "content": f"Summarize the following article in Chinese (zh-CN):\n\nTitle: {title}\n\nContent:\n{content}"}
        ]
    }
    
    try:
        # Get translated title
        title_response = requests.post(CUSTOM_API_URL, headers=headers, json=title_payload)
        title_response.raise_for_status()
        chinese_title = title_response.json()['choices'][0]['message']['content'].strip()

        # Get Chinese summary
        content_response = requests.post(CUSTOM_API_URL, headers=headers, json=content_payload)
        content_response.raise_for_status()
        chinese_summary = content_response.json()['choices'][0]['message']['content'].strip()
        
        # Apply pangu spacing
        chinese_title = pangu.spacing_text(chinese_title)
        chinese_summary = pangu.spacing_text(chinese_summary)
        
        return chinese_title, chinese_summary
    except requests.RequestException as e:
        print(f"Error getting Chinese title and summary: {e}")
        return None, None

def main():
    high_rated_dir = 'high_rated_articles'
    summaries_dir = 'article_summaries'
    results = {}

    # Ensure summaries_dir exists
    os.makedirs(summaries_dir, exist_ok=True)

    for filename in os.listdir(high_rated_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(high_rated_dir, filename)
            print(f"Processing {filename}...")
            
            content = read_article(file_path)
            
            url, title = extract_url_and_title(content)
            # Remove URL and title lines from content
            content = '\n'.join(line for line in content.split('\n') if not line.startswith(('URL:', 'Title:')))
            
            chinese_title, chinese_summary = get_chinese_title_and_summary(title, content, url)
            
            if chinese_summary and chinese_title:
                summary_filename = f"summary_{filename}"
                summary_path = os.path.join(summaries_dir, summary_filename)
                write_summary(summary_path, f"标题：{chinese_title}\n\nURL: {url}\n\n{chinese_summary}")
                
                results[filename] = {
                    "url": url,
                    "original_title": title,
                    "chinese_title": chinese_title,
                    "chinese_summary": chinese_summary
                }
                print(f"Chinese title and summary for {filename} saved.")
            else:
                print(f"Failed to get Chinese title and summary for {filename}")

    # Save results to a JSON file
    with open('article_summaries.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("Summaries saved to article_summaries.json")
    print(f"Article summaries saved in {summaries_dir}")

if __name__ == "__main__":
    main()