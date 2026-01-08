#!/usr/bin/env python3
"""
PRAW专用Reddit API测试
只测试PRAW功能，绕过HTTP认证问题
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def test_reddit_praw_only():
    """仅测试PRAW功能"""
    print("🔍 PRAW专用Reddit测试...")
    
    try:
        import praw
        
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        # 测试基础功能
        subreddit = reddit.subreddit("stocks")
        posts = list(subreddit.hot(limit=2))
        
        if posts:
            print(f"✅ Reddit API (PRAW) 工作正常")
            print(f"   获取到 {len(posts)} 个帖子")
            return True
        else:
            print(f"❌ 未获取到数据")
            return False
            
    except Exception as e:
        print(f"❌ PRAW测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_reddit_praw_only()
    sys.exit(0 if success else 1)
