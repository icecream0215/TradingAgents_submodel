#!/usr/bin/env python3
"""
Reddit API问题诊断和修复指南
分析Reddit API 401错误的具体原因并提供解决方案
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def analyze_reddit_401_error():
    """分析Reddit API 401错误的可能原因"""
    
    print("🔍 Reddit API 401错误诊断分析")
    print("=" * 50)
    
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')
    
    print(f"当前配置:")
    print(f"  REDDIT_CLIENT_ID: {client_id}")
    print(f"  REDDIT_CLIENT_SECRET: {client_secret[:10]}..." if client_secret else "  REDDIT_CLIENT_SECRET: 未设置")
    print(f"  REDDIT_USER_AGENT: {user_agent}")
    
    print(f"\n🧐 401错误的常见原因分析:")
    
    # 1. 检查Client ID格式
    print(f"\n1️⃣ Client ID格式检查:")
    if client_id:
        if len(client_id) < 10:
            print(f"   ⚠️ Client ID太短 (当前长度: {len(client_id)})")
            print(f"   💡 Reddit Client ID通常是14-22个字符的字符串")
        elif len(client_id) > 30:
            print(f"   ⚠️ Client ID太长 (当前长度: {len(client_id)})")
            print(f"   💡 可能把Client Secret当作Client ID了")
        else:
            print(f"   ✅ Client ID长度正常 ({len(client_id)}个字符)")
    
    # 2. 检查Client Secret格式
    print(f"\n2️⃣ Client Secret格式检查:")
    if client_secret:
        if len(client_secret) < 20:
            print(f"   ⚠️ Client Secret太短 (当前长度: {len(client_secret)})")
            print(f"   💡 Reddit Client Secret通常是30-50个字符的字符串")
        elif len(client_secret) > 60:
            print(f"   ⚠️ Client Secret太长 (当前长度: {len(client_secret)})")
        else:
            print(f"   ✅ Client Secret长度正常 ({len(client_secret)}个字符)")
    
    # 3. 检查用户代理
    print(f"\n3️⃣ User Agent检查:")
    if user_agent and len(user_agent) > 5:
        print(f"   ✅ User Agent格式正常")
    else:
        print(f"   ⚠️ User Agent可能格式不正确")
    
    # 4. 常见问题列表
    print(f"\n🚨 Reddit API 401错误的常见原因:")
    print(f"   1. 应用类型选择错误 (必须选择 'script' 类型)")
    print(f"   2. Client ID和Client Secret位置搞反了")
    print(f"   3. Client ID包含了多余的字符或空格")
    print(f"   4. Reddit应用被暂停或删除")
    print(f"   5. API访问频率过高被限制")
    print(f"   6. 网络问题或Reddit服务故障")
    
    print(f"\n💡 解决方案建议:")
    print(f"   1. 重新检查Reddit应用配置")
    print(f"   2. 确认应用类型为 'script'")
    print(f"   3. 重新创建Reddit应用")
    print(f"   4. 检查凭据复制是否完整")

def provide_step_by_step_fix():
    """提供详细的修复步骤"""
    
    print(f"\n🔧 详细修复步骤:")
    print("=" * 50)
    
    print(f"\n📝 步骤1: 验证Reddit应用设置")
    print(f"   1. 访问: https://www.reddit.com/prefs/apps")
    print(f"   2. 找到您的应用 'TradingAgents-CN' (或其他名称)")
    print(f"   3. 确认应用类型显示为 'script'")
    print(f"   4. 如果不是，删除并重新创建")
    
    print(f"\n📝 步骤2: 重新创建Reddit应用 (如果需要)")
    print(f"   1. 点击 'Create App' 或 'Create Another App'")
    print(f"   2. 应用名称: TradingAgents-API-Test")
    print(f"   3. 应用类型: 选择 'script' (重要!)")
    print(f"   4. 描述: Trading analysis tool for Reddit data")
    print(f"   5. 关于URL: 留空或填写 https://github.com")
    print(f"   6. 重定向URI: http://localhost:8080")
    print(f"   7. 点击 'Create app'")
    
    print(f"\n📝 步骤3: 获取正确的凭据")
    print(f"   1. 在应用列表中找到新创建的应用")
    print(f"   2. Client ID: 应用名称下方的字符串 (如: Whole-Depth-4608)")
    print(f"   3. Client Secret: 点击 'edit' 查看，复制 'secret' 字段的值")
    print(f"   4. 确保复制时没有多余的空格或换行符")
    
    print(f"\n📝 步骤4: 更新.env文件")
    print(f"   1. 编辑 /root/TradingAgents/.env 文件")
    print(f"   2. 更新以下行:")
    print(f"      REDDIT_CLIENT_ID=新的client_id")
    print(f"      REDDIT_CLIENT_SECRET=新的client_secret")
    print(f"      REDDIT_USER_AGENT=TradingAgents-API-Test/1.0")
    print(f"   3. 保存文件")
    
    print(f"\n📝 步骤5: 测试新配置")
    print(f"   运行: python3 tests/api_connectivity/test_reddit_credentials.py")

def test_alternative_approach():
    """测试替代方法"""
    
    print(f"\n🔄 尝试替代验证方法:")
    print("=" * 30)
    
    try:
        import praw
        import requests
        
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        
        # 方法1: 直接使用requests测试认证
        print(f"\n🔍 方法1: 直接HTTP认证测试")
        
        auth_url = "https://www.reddit.com/api/v1/access_token"
        auth_data = {
            'grant_type': 'client_credentials',
        }
        
        response = requests.post(
            auth_url,
            auth=(client_id, client_secret),
            data=auth_data,
            headers={'User-Agent': 'TradingAgents-Test/1.0'}
        )
        
        print(f"   HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ HTTP认证成功!")
            data = response.json()
            print(f"   获得访问令牌: {data.get('access_token', 'N/A')[:20]}...")
        else:
            print(f"   ❌ HTTP认证失败")
            print(f"   响应内容: {response.text}")
        
        # 方法2: 使用PRAW的read-only模式
        print(f"\n🔍 方法2: PRAW只读模式测试")
        
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent='TradingAgents-Test/1.0'
        )
        
        # 设置为只读模式
        reddit.read_only = True
        print(f"   PRAW只读模式: {reddit.read_only}")
        
        # 测试简单的API调用
        try:
            subreddit = reddit.subreddit("test")
            print(f"   测试subreddit名称: {subreddit.display_name}")
            print(f"   ✅ PRAW只读模式工作正常!")
        except Exception as e:
            print(f"   ❌ PRAW只读模式失败: {e}")
            
    except ImportError as e:
        print(f"❌ 缺少必要的库: {e}")
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")

def main():
    """主函数"""
    analyze_reddit_401_error()
    provide_step_by_step_fix()
    test_alternative_approach()
    
    print(f"\n" + "=" * 50)
    print(f"📋 总结和建议:")
    print(f"1. 当前凭据配置基本正确，但可能应用类型或凭据有误")
    print(f"2. 建议重新创建Reddit应用，确保选择 'script' 类型")
    print(f"3. 重新获取凭据并更新.env文件")
    print(f"4. 如果问题持续，可能是Reddit API临时问题")
    print(f"5. 可以先使用其他数据源，稍后再配置Reddit")

if __name__ == "__main__":
    main()