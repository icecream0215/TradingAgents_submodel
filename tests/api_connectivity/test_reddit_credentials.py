#!/usr/bin/env python3
"""
Reddit API凭据验证工具
专门用于验证Reddit API密钥的有效性
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class RedditCredentialsValidator:
    """Reddit API凭据验证器"""
    
    def __init__(self):
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT', 'TradingAgents-CN/1.0')
        
    def check_environment_variables(self) -> Dict[str, Any]:
        """检查环境变量配置"""
        print("🔍 检查Reddit API环境变量配置...")
        
        results = {
            'client_id_exists': bool(self.client_id),
            'client_secret_exists': bool(self.client_secret),
            'user_agent_exists': bool(self.user_agent),
            'all_configured': False
        }
        
        if self.client_id:
            print(f"✅ REDDIT_CLIENT_ID: {self.client_id}")
        else:
            print("❌ REDDIT_CLIENT_ID: 未配置")
        
        if self.client_secret:
            print(f"✅ REDDIT_CLIENT_SECRET: {self.client_secret[:10]}...")
        else:
            print("❌ REDDIT_CLIENT_SECRET: 未配置")
        
        if self.user_agent:
            print(f"✅ REDDIT_USER_AGENT: {self.user_agent}")
        else:
            print("❌ REDDIT_USER_AGENT: 未配置")
        
        results['all_configured'] = all([
            results['client_id_exists'],
            results['client_secret_exists'],
            results['user_agent_exists']
        ])
        
        return results
    
    def test_praw_import(self) -> bool:
        """测试PRAW库导入"""
        print("\n🔍 测试PRAW库导入...")
        try:
            import praw
            print("✅ PRAW库导入成功")
            print(f"   PRAW版本: {praw.__version__}")
            return True
        except ImportError:
            print("❌ PRAW库未安装")
            print("💡 请运行: pip install praw")
            return False
    
    def test_basic_authentication(self) -> Dict[str, Any]:
        """测试基础认证"""
        print("\n🔍 测试Reddit API基础认证...")
        
        result = {
            'success': False,
            'error': None,
            'reddit_instance': None
        }
        
        try:
            import praw
            
            # 创建Reddit实例
            reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            
            # 测试基础访问 - 获取用户信息（只读操作）
            try:
                # 尝试访问Reddit的只读信息
                user = reddit.user.me()
                print(f"✅ 认证成功！当前用户: {user}")
                result['success'] = True
                result['reddit_instance'] = reddit
            except Exception as e:
                if "401" in str(e) or "unauthorized" in str(e).lower():
                    print("❌ 认证失败 - 401 Unauthorized")
                    print("💡 可能的原因:")
                    print("   1. REDDIT_CLIENT_ID 或 REDDIT_CLIENT_SECRET 错误")
                    print("   2. Reddit应用类型配置不正确")
                    print("   3. API密钥已过期或被禁用")
                    result['error'] = "401 Unauthorized - 凭据无效"
                else:
                    # 可能是其他类型的错误，但认证可能是成功的
                    print(f"⚠️ 认证可能成功，但遇到其他问题: {e}")
                    # 尝试一个更简单的测试
                    try:
                        # 测试获取subreddit信息（只读，不需要用户认证）
                        subreddit = reddit.subreddit("python")
                        title = subreddit.display_name
                        print(f"✅ 可以访问Reddit API - 测试subreddit: {title}")
                        result['success'] = True
                        result['reddit_instance'] = reddit
                    except Exception as e2:
                        print(f"❌ 无法访问Reddit API: {e2}")
                        result['error'] = str(e2)
                        
        except ImportError:
            print("❌ PRAW库未安装")
            result['error'] = "PRAW library not installed"
        except Exception as e:
            print(f"❌ 创建Reddit实例失败: {e}")
            result['error'] = str(e)
        
        return result
    
    def test_read_only_access(self, reddit_instance) -> bool:
        """测试只读访问权限"""
        print("\n🔍 测试Reddit只读访问权限...")
        
        try:
            # 测试访问流行的subreddit
            subreddit = reddit_instance.subreddit("python")
            posts = list(subreddit.hot(limit=3))
            
            if posts:
                print(f"✅ 成功获取r/python的热门帖子")
                for i, post in enumerate(posts):
                    print(f"   帖子 {i+1}: {post.title[:50]}...")
                return True
            else:
                print("⚠️ 未获取到帖子数据")
                return False
                
        except Exception as e:
            print(f"❌ 只读访问测试失败: {e}")
            return False
    
    def test_search_functionality(self, reddit_instance) -> bool:
        """测试搜索功能"""
        print("\n🔍 测试Reddit搜索功能...")
        
        try:
            # 在投资相关的subreddit中搜索
            subreddit = reddit_instance.subreddit("investing")
            posts = list(subreddit.search("AAPL", limit=3))
            
            if posts:
                print(f"✅ 成功在r/investing中搜索AAPL相关帖子")
                for i, post in enumerate(posts):
                    print(f"   搜索结果 {i+1}: {post.title[:50]}...")
                    print(f"      分数: {post.score}, 评论: {post.num_comments}")
                return True
            else:
                print("⚠️ 搜索未返回结果")
                return False
                
        except Exception as e:
            print(f"❌ 搜索功能测试失败: {e}")
            return False
    
    def get_reddit_app_info(self) -> Dict[str, str]:
        """获取Reddit应用信息和设置建议"""
        return {
            'setup_url': 'https://www.reddit.com/prefs/apps',
            'app_type': 'script',
            'redirect_uri': 'http://localhost:8080',
            'instructions': [
                "1. 访问 https://www.reddit.com/prefs/apps",
                "2. 点击 'Create App' 或 'Create Another App'",
                "3. 选择应用类型: 'script'",
                "4. 填写应用名称: TradingAgents-CN",
                "5. 填写描述: Stock market analysis tool",
                "6. 重定向URI: http://localhost:8080",
                "7. 创建后复制 client_id 和 client_secret",
                "8. client_id 是应用名称下方的短字符串",
                "9. client_secret 是 'secret' 字段的长字符串"
            ]
        }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """运行综合测试"""
        print("🚀 开始Reddit API凭据综合验证")
        print("=" * 50)
        
        results = {
            'environment_check': {},
            'praw_import': False,
            'authentication': {},
            'read_access': False,
            'search_access': False,
            'overall_success': False
        }
        
        # 1. 检查环境变量
        results['environment_check'] = self.check_environment_variables()
        
        if not results['environment_check']['all_configured']:
            print("\n❌ 环境变量配置不完整，无法继续测试")
            app_info = self.get_reddit_app_info()
            print(f"\n💡 Reddit应用设置说明:")
            for instruction in app_info['instructions']:
                print(f"   {instruction}")
            return results
        
        # 2. 测试PRAW导入
        results['praw_import'] = self.test_praw_import()
        if not results['praw_import']:
            return results
        
        # 3. 测试认证
        results['authentication'] = self.test_basic_authentication()
        
        if results['authentication']['success']:
            reddit_instance = results['authentication']['reddit_instance']
            
            # 4. 测试只读访问
            results['read_access'] = self.test_read_only_access(reddit_instance)
            
            # 5. 测试搜索功能
            results['search_access'] = self.test_search_functionality(reddit_instance)
        
        # 计算总体成功率
        success_count = sum([
            results['environment_check']['all_configured'],
            results['praw_import'],
            results['authentication']['success'],
            results['read_access'],
            results['search_access']
        ])
        
        total_tests = 5
        success_rate = (success_count / total_tests) * 100
        
        results['overall_success'] = success_rate >= 80
        
        # 输出总结
        print("\n" + "=" * 50)
        print("📊 Reddit API验证结果总结:")
        print(f"   环境变量配置: {'✅' if results['environment_check']['all_configured'] else '❌'}")
        print(f"   PRAW库导入: {'✅' if results['praw_import'] else '❌'}")
        print(f"   API认证: {'✅' if results['authentication']['success'] else '❌'}")
        print(f"   只读访问: {'✅' if results['read_access'] else '❌'}")
        print(f"   搜索功能: {'✅' if results['search_access'] else '❌'}")
        
        print(f"\n🎯 总体成功率: {success_rate:.1f}%")
        
        if results['overall_success']:
            print("🎉 Reddit API配置正常，可以正常使用！")
        else:
            print("⚠️ Reddit API配置存在问题，需要检查配置")
            
            if not results['authentication']['success']:
                app_info = self.get_reddit_app_info()
                print(f"\n💡 Reddit应用设置说明:")
                print(f"   设置地址: {app_info['setup_url']}")
                print(f"   应用类型: {app_info['app_type']}")
                for instruction in app_info['instructions'][-3:]:
                    print(f"   {instruction}")
        
        return results

def main():
    """主函数"""
    validator = RedditCredentialsValidator()
    results = validator.run_comprehensive_test()
    
    # 返回退出码
    if results['overall_success']:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()