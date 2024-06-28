import os
import json
import requests
import shutil
from dotenv import load_dotenv
from datetime import datetime
import re

# 加载环境变量
load_dotenv()

# 设置自定义API端点和密钥
CUSTOM_API_URL = os.getenv("CUSTOM_API_URL")
API_KEY = os.getenv("API_KEY")
RATING_CRITERIA = os.getenv("RATING_CRITERIA")
TOP_ARTICLES = int(os.getenv("TOP_ARTICLES", 5))

def read_article(file_path):
    # 读取文章内容
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_article(file_path, content):
    # 写入文章内容
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def extract_score(content):
    # 从文章内容中提取评分
    score_pattern = re.compile(r'Article Score: (\d+(\.\d+)?)\s*out of 10')
    return score_pattern.search(content)

def replace_score(content, new_score):
    # 替换文章内容中的评分
    score_pattern = re.compile(r'Article Score: (\d+(\.\d+)?)\s*out of 10\nRated on: [^\n]+')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_score_line = f"Article Score: {new_score} out of 10\nRated on: {timestamp}"
    if score_pattern.search(content):
        return score_pattern.sub(new_score_line, content)
    else:
        return content + f"\n\n{new_score_line}"

def get_article_rating(content):
    # 获取文章评分
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": f"You are an AI assistant that rates articles strictly based on the criteria: '{RATING_CRITERIA}'. First, determine if the article strictly matches the criteria. If it does not, respond with 'Not relevant'. If it matches, rate the article based on its value in 'X out of 10' format, where X is a number from 1 to 10."},
            {"role": "user", "content": f"Rate the following article:\n\n{content}"}
        ]
    }
    
    try:
        response = requests.post(CUSTOM_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        raw_rating = response.json()['choices'][0]['message']['content'].strip()
        print(f"Raw rating response: {raw_rating}")  # Add this line for debugging
        if raw_rating.lower() == "not relevant":
            return None
        match = re.search(r'(\d+(\.\d+)?)\s*out of 10', raw_rating)
        if match:
            return f"{match.group(1)}"
        else:
            print(f"Unexpected rating format: {raw_rating}")
            return None
    except requests.RequestException as e:
        print(f"Error getting rating: {e}")
        return None

def main():
    articles_dir = 'articles_text'  # 文章目录
    high_rated_dir = 'high_rated_articles'  # 高评分文章目录
    results = {}  # 存储结果
    scores = []  # 存储评分

    # 确保高评分文章目录存在
    os.makedirs(high_rated_dir, exist_ok=True)

    for filename in os.listdir(articles_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(articles_dir, filename)
            print(f"Processing {filename}...")
            
            content = read_article(file_path)
            
            # 获取新的评分
            rating = get_article_rating(content)
            
            if rating:
                score = float(rating)
                updated_content = replace_score(content, rating)
                write_article(file_path, updated_content)
                
                results[filename] = score
                scores.append((filename, score))
                print(f"Rating for {filename}: {rating} out of 10")
            else:
                print(f"Failed to get rating for {filename}")

    # 按评分排序并选择前 TOP_ARTICLES 篇文章
    scores.sort(key=lambda x: x[1], reverse=True)
    top_articles = scores[:TOP_ARTICLES]

    # 复制前 TOP_ARTICLES 篇高评分文章
    for filename, score in top_articles:
        src = os.path.join(articles_dir, filename)
        dst = os.path.join(high_rated_dir, filename)
        shutil.copy2(src, dst)
        print(f"Copied {filename} to high_rated_articles (Score: {score})")

    # 将结果保存到JSON文件
    with open('article_ratings.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print("Ratings saved to article_ratings.json")
    print(f"High-rated articles copied to {high_rated_dir}")

if __name__ == "__main__":
    main()