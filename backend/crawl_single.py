"""
爬取单篇文章并保存为 Markdown 格式
"""

import sys
import os
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.platforms.wechat_sogou import crawl_single_article


def save_article_as_markdown(article, base_path='data/articles'):
    """
    将文章保存为 Markdown 格式
    """
    author_name = article.get('author', 'unknown')
    title = article.get('title', 'untitled')

    # 创建作者目录
    author_dir = os.path.join(base_path, author_name)
    os.makedirs(author_dir, exist_ok=True)

    # 生成文件名（使用日期+标题）
    pub_time = article.get('pub_time', '')
    date_str = pub_time[:10] if pub_time else datetime.now().strftime('%Y-%m-%d')

    # 清理标题中的非法字符
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{date_str}-{safe_title[:50]}.md"
    filepath = os.path.join(author_dir, filename)

    # 构建 Markdown 内容
    md_content = f"""---
title: "{title}"
author: "{author_name}"
platform: "wechat"
url: "{article.get('url', '')}"
publish_date: "{article.get('pub_time', '')}"
crawl_date: "{datetime.now().isoformat()}"
summary: "{article.get('summary', '')}"
---

# {title}

**作者**: {author_name}
**发布时间**: {article.get('pub_time', '')}
**原文链接**: [{article.get('url', '')}]({article.get('url', '')})

---

{article.get('content', '')}
"""

    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"文章已保存: {filepath}")
    return filepath


def update_authors_json(article, base_path='data'):
    """
    更新 authors.json 文件
    """
    authors_file = os.path.join(base_path, 'authors.json')

    # 读取现有作者信息
    if os.path.exists(authors_file):
        with open(authors_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {'authors': {}, 'version': '1.0'}

    author_name = article.get('author', 'unknown')

    # 如果作者不存在，添加作者信息
    if author_name not in data['authors']:
        data['authors'][author_name] = {
            'platform': 'wechat',
            'name': author_name,
            'first_url': article.get('url', ''),
            'path': f'articles/{author_name}',
            'created_at': datetime.now().isoformat(),
            'last_crawl': datetime.now().isoformat(),
            'article_count': 1,
            'status': 'active'
        }
    else:
        # 更新作者信息
        data['authors'][author_name]['last_crawl'] = datetime.now().isoformat()
        data['authors'][author_name]['article_count'] = data['authors'][author_name].get('article_count', 0) + 1

    # 保存 authors.json
    with open(authors_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已更新 authors.json: {author_name}")


def main():
    # 用户提供的文章 URL
    article_url = 'https://mp.weixin.qq.com/s/SGbV1Sd2T4urp8yhKU0d8Q'

    print(f"开始爬取文章: {article_url}")
    print("-" * 50)

    # 爬取文章
    article = crawl_single_article(article_url)

    if not article:
        print("爬取文章失败！")
        return

    print("-" * 50)
    print(f"标题: {article['title']}")
    print(f"作者: {article['author']}")
    print(f"发布时间: {article['pub_time']}")
    print(f"摘要: {article['summary'][:100]}..." if article['summary'] else "无摘要")
    print(f"内容长度: {len(article['content'])} 字符")

    # 保存文章
    print("-" * 50)
    filepath = save_article_as_markdown(article)

    # 更新作者信息
    update_authors_json(article)

    print("-" * 50)
    print("爬取完成！")


if __name__ == '__main__':
    main()
