#!/usr/bin/env python3
"""
新闻和社交媒体API连通性测试
测试Google News和Reddit API的访问是否正常

支持的数据类型：
- Google News: 全球新闻 (Global news via web scraping)
- Reddit: 社交媒体情绪 (Social media sentiment via PRAW)
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import warnings

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 忽略警告
warnings.filterwarnings('ignore')

class NewsAndSocialAPITester:
    """新闻和社交媒体API测试器"""
    
    def __init__(self):
        self.reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.reddit_user_agent = os.getenv('REDDIT_USER_AGENT', 'TradingAgents-Test/1.0')
        
    def test_google_news_scraping(self, query: str = "AAPL stock") -> bool:
        """测试Google News网页爬虫"""
        print(f"\n📰 测试Google News爬虫 (查询: {query})...")
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # 构建Google News搜索URL
            search_url = f"https://news.google.com/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 查找新闻标题 (Google News的HTML结构可能会变化)
                articles = soup.find_all('article')
                
                if articles:
                    print(f"✅ Google News爬虫成功")
                    print(f"   找到文章数: {len(articles)}")
                    
                    # 尝试提取前几个标题
                    for i, article in enumerate(articles[:3]):
                        title_elem = article.find('a')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            print(f"   文章 {i+1}: {title[:60]}...")
                    
                    return True
                else:
                    print("⚠️ 未找到新闻文章，可能网页结构已变化")
                    return False
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return False
                
        except ImportError:
            print("❌ 缺少依赖库")
            print("💡 请安装: pip install beautifulsoup4 requests")
            return False
        except Exception as e:
            print(f"❌ Google News测试异常: {e}")
            return False
    
    def test_alternative_news_api(self, query: str = "Apple stock") -> bool:
        """测试替代新闻API (使用NewsAPI或其他免费API)"""
        print(f"\n📰 测试替代新闻源...")
        try:
            import requests
            
            # 使用一个免费的新闻API (例如GNews API)
            api_key = os.getenv('GNEWS_API_KEY')  # 如果有的话
            
            if api_key:
                url = "https://gnews.io/api/v4/search"
                params = {
                    'q': query,
                    'token': api_key,
                    'lang': 'en',
                    'max': 5
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    if articles:
                        print(f"✅ 新闻API连接成功")
                        print(f"   文章数量: {len(articles)}")
                        
                        for i, article in enumerate(articles[:3]):
                            print(f"   文章 {i+1}: {article['title'][:60]}...")
                        
                        return True
                    else:
                        print("⚠️ 未找到相关新闻")
                        return False
                else:
                    print(f"❌ API请求失败，状态码: {response.status_code}")
                    return False
            else:
                print("⚠️ 未配置新闻API密钥，跳过此测试")
                print("💡 可在 .env 中设置 GNEWS_API_KEY")
                return True  # 没有API密钥不算失败
                
        except Exception as e:
            print(f"❌ 新闻API测试异常: {e}")
            return False
    
    def test_reddit_api(self, subreddit: str = "stocks", limit: int = 5) -> bool:
        """测试Reddit API连接"""
        print(f"\n🔴 测试Reddit API (r/{subreddit})...")
        try:
            import praw
            
            # 检查API凭据
            if not self.reddit_client_id or not self.reddit_client_secret:
                print("⚠️ Reddit API凭据未配置")
                print("💡 请在 .env 文件中设置:")
                print("   REDDIT_CLIENT_ID=your_client_id")
                print("   REDDIT_CLIENT_SECRET=your_client_secret")
                return True  # 没有凭据不算失败
            
            # 创建Reddit实例
            reddit = praw.Reddit(
                client_id=self.reddit_client_id,
                client_secret=self.reddit_client_secret,
                user_agent=self.reddit_user_agent
            )
            
            # 测试连接
            subreddit_obj = reddit.subreddit(subreddit)
            posts = list(subreddit_obj.hot(limit=limit))
            
            if posts:
                print(f"✅ Reddit API连接成功")
                print(f"   获取帖子数: {len(posts)}")
                
                for i, post in enumerate(posts):
                    print(f"   帖子 {i+1}: {post.title[:50]}... (👍{post.score})")
                
                return True
            else:
                print(f"❌ 未能获取r/{subreddit}的帖子")
                return False
                
        except ImportError:
            print("❌ PRAW库未安装")
            print("💡 请运行: pip install praw")
            return False
        except Exception as e:
            print(f"❌ Reddit API测试异常: {e}")
            return False
    
    def test_reddit_sentiment_analysis(self, subreddit: str = "investing", query: str = "AAPL") -> bool:
        """测试Reddit情绪分析"""
        print(f"\n💭 测试Reddit情绪分析 (r/{subreddit}, 关键词: {query})...")
        try:
            import praw
            
            if not self.reddit_client_id or not self.reddit_client_secret:
                print("⚠️ Reddit API凭据未配置，跳过情绪分析测试")
                return True
            
            reddit = praw.Reddit(
                client_id=self.reddit_client_id,
                client_secret=self.reddit_client_secret,
                user_agent=self.reddit_user_agent
            )
            
            # 搜索相关帖子
            subreddit_obj = reddit.subreddit(subreddit)
            posts = list(subreddit_obj.search(query, limit=10))
            
            if posts:
                print(f"✅ 找到 {len(posts)} 个相关帖子")
                
                # 简单的情绪分析 (基于分数)
                total_score = sum(post.score for post in posts)
                avg_score = total_score / len(posts)
                
                print(f"   总分数: {total_score}")
                print(f"   平均分数: {avg_score:.1f}")
                
                sentiment = "积极" if avg_score > 0 else "消极" if avg_score < 0 else "中性"
                print(f"   整体情绪: {sentiment}")
                
                return True
            else:
                print(f"⚠️ 未找到关于 '{query}' 的相关帖子")
                return True  # 没有找到帖子不算失败
                
        except Exception as e:
            print(f"❌ Reddit情绪分析测试异常: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """运行所有测试"""
        print("🚀 开始新闻和社交媒体API连通性测试...")
        print("=" * 50)
        
        results = {}
        
        # 1. 测试Google News爬虫
        results['google_news_scraping'] = self.test_google_news_scraping()
        
        # 2. 测试替代新闻API
        results['alternative_news_api'] = self.test_alternative_news_api()
        
        # 3. 测试Reddit API
        results['reddit_api'] = self.test_reddit_api()
        
        # 4. 测试Reddit情绪分析
        results['reddit_sentiment'] = self.test_reddit_sentiment_analysis()
        
        # 输出总结
        print("\n" + "=" * 50)
        print("📊 新闻和社交媒体API测试结果总结:")
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
        
        success_rate = sum(results.values()) / len(results) * 100
        print(f"\n🎯 总体成功率: {success_rate:.1f}%")
        
        return results

def main():
    """主函数"""
    tester = NewsAndSocialAPITester()
    results = tester.run_all_tests()
    
    # 返回退出码
    if all(results.values()):
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️ 部分测试失败，请检查配置和网络连接")
        sys.exit(1)

if __name__ == "__main__":
    main()