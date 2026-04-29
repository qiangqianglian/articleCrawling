"""
微信公众号爬虫 - 使用搜狗搜索方案
替换 RSSHub，直接使用搜狗搜索获取文章列表
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote
import re


class WechatSogouCrawler:
    """使用搜狗搜索爬取微信公众号文章"""

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        self.base_url = 'https://weixin.sogou.com'

    def _get_sogou_token(self):
        """获取搜狗搜索需要的 cookie 和 token"""
        try:
            # 访问首页获取必要的 cookie
            resp = self.session.get(
                'https://weixin.sogou.com/',
                headers=self.headers,
                timeout=10
            )
            time.sleep(random.uniform(1, 2))
            return True
        except Exception as e:
            print(f"获取搜狗 token 失败: {e}")
            return False

    def search_articles(self, author_name, pages=1):
        """
        搜索公众号文章
        :param author_name: 公众号名称
        :param pages: 搜索页数
        :return: 文章列表
        """
        articles = []

        # 先获取 token
        if not self._get_sogou_token():
            return articles

        for page in range(1, pages + 1):
            try:
                # 构建搜索 URL - 使用公众号名称搜索
                query = quote(author_name)
                url = f"{self.base_url}/weixin?type=2&query={query}&page={page}&ie=utf8"

                print(f"正在搜索第 {page} 页: {url}")

                resp = self.session.get(
                    url,
                    headers=self.headers,
                    timeout=15
                )

                if resp.status_code != 200:
                    print(f"请求失败: {resp.status_code}")
                    continue

                soup = BeautifulSoup(resp.text, 'html.parser')

                # 解析搜索结果 - 搜狗微信搜索结果在 .txt-box 中
                result_items = soup.find_all('li', class_='txt-box')

                if not result_items:
                    print(f"第 {page} 页没有搜索结果")
                    continue

                for item in result_items:
                    try:
                        # 提取标题
                        title_elem = item.find('h3')
                        if not title_elem:
                            continue
                        title = title_elem.get_text(strip=True)

                        # 提取链接
                        link_elem = item.find('a')
                        if not link_elem:
                            continue
                        link = link_elem.get('href', '')

                        # 搜狗链接需要处理
                        if link.startswith('/'):
                            link = f"https://weixin.sogou.com{link}"

                        # 提取摘要
                        summary_elem = item.find('p', class_='txt-info')
                        summary = summary_elem.get_text(strip=True) if summary_elem else ""

                        # 提取发布时间
                        time_elem = item.find('span', class_='s2') or item.find('span', class_='time')
                        pub_time = time_elem.get_text(strip=True) if time_elem else ""

                        article = {
                            'title': title,
                            'url': link,
                            'summary': summary,
                            'pub_time': pub_time
                        }
                        articles.append(article)
                        print(f"找到文章: {title}")

                    except Exception as e:
                        print(f"解析文章失败: {e}")
                        continue

                # 随机延迟，避免被封
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"搜索第 {page} 页失败: {e}")
                continue

        return articles

    def get_article_list(self, author_name, max_articles=20):
        """
        获取公众号文章列表（供后端调用）
        """
        # 计算需要搜索的页数（每页约10条）
        pages = min(3, (max_articles + 9) // 10)

        articles = self.search_articles(author_name, pages)

        # 限制返回数量
        return articles[:max_articles]


    def crawl_article(self, url):
        """
        爬取单篇文章的详细内容
        :param url: 文章URL
        :return: 文章详细信息的字典
        """
        try:
            print(f"正在爬取文章: {url}")
            resp = self.session.get(
                url,
                headers=self.headers,
                timeout=15
            )

            if resp.status_code != 200:
                print(f"请求失败: {resp.status_code}")
                return None

            soup = BeautifulSoup(resp.text, 'html.parser')

            # 提取标题
            title_elem = soup.find('h1', class_='rich_media_title') or soup.find('h2', class_='rich_media_title')
            title = title_elem.get_text(strip=True) if title_elem else "未知标题"

            # 提取作者
            author_elem = soup.find('span', class_='profile_nickname') or soup.find('a', id='js_name')
            author = author_elem.get_text(strip=True) if author_elem else "未知作者"

            # 提取发布时间
            time_elem = soup.find('em', id='publish_time')
            pub_time = time_elem.get_text(strip=True) if time_elem else ""

            # 提取正文内容
            content_elem = soup.find('div', id='js_content')
            content = ""
            if content_elem:
                # 处理图片
                for img in content_elem.find_all('img'):
                    img_url = img.get('data-src', img.get('src', ''))
                    if img_url:
                        img.name = 'img'
                        img['src'] = img_url

                # 提取文本内容
                content = content_elem.get_text(separator='\n', strip=True)

            # 提取摘要
            summary_elem = soup.find('meta', property='og:description')
            summary = summary_elem.get('content', '') if summary_elem else ""

            article = {
                'title': title,
                'author': author,
                'url': url,
                'pub_time': pub_time,
                'summary': summary,
                'content': content
            }

            print(f"成功爬取文章: {title}")
            return article

        except Exception as e:
            print(f"爬取文章失败: {e}")
            return None


# 供后端导入使用的函数 - 替换原来的 RSSHub 版本
def get_author_articles(author_name, max_articles=20):
    """
    使用搜狗搜索获取公众号文章列表
    替代原来的 RSSHub 方案
    """
    crawler = WechatSogouCrawler()
    return crawler.get_article_list(author_name, max_articles)


def crawl_single_article(url):
    """
    爬取单篇文章的详细内容
    :param url: 文章URL
    :return: 文章详细信息的字典
    """
    crawler = WechatSogouCrawler()
    return crawler.crawl_article(url)


if __name__ == '__main__':
    # 测试
    test_author = "猫笔叨"
    print(f"正在搜索公众号: {test_author}")
    articles = get_author_articles(test_author, max_articles=10)
    print(f"\n共找到 {len(articles)} 篇文章:")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   链接: {article['url']}")
        print(f"   时间: {article['pub_time']}")
        print()
