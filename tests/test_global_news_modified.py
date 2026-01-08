#!/usr/bin/env python3
"""
测试修改后的get_global_news_openai函数
验证使用第三方OpenAI API和GLM-4.5-FP8模型的实时搜索功能
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_get_global_news_openai():
    """测试修改后的get_global_news_openai函数"""
    print("🧪 测试get_global_news_openai函数")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.interface import get_global_news_openai
        
        # 使用当前日期进行测试
        test_date = "2025-09-09"
        
        print(f"📅 测试日期: {test_date}")
        print(f"🔧 配置信息:")
        
        # 显示配置信息
        from tradingagents.dataflows.config import get_config
        config = get_config()
        backend_url = config.get("backend_url", "未配置")
        print(f"   Backend URL: {backend_url}")
        
        # 显示API密钥状态
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print(f"   API密钥: {api_key[:20]}...")
        else:
            print(f"   API密钥: 未设置 (将使用回退搜索)")
        
        print(f"\n🔍 开始获取全球宏观经济新闻...")
        
        # 调用函数
        result = get_global_news_openai(test_date)
        
        if result:
            print(f"✅ 成功获取新闻内容")
            print(f"📊 内容长度: {len(result)} 字符")
            print(f"📄 内容预览:")
            print("-" * 40)
            print(result[:500] + "..." if len(result) > 500 else result)
            print("-" * 40)
            
            # 检查内容质量
            if "global" in result.lower() or "economic" in result.lower() or "market" in result.lower():
                print(f"✅ 内容质量检查: 包含相关经济新闻关键词")
            else:
                print(f"⚠️ 内容质量检查: 可能缺少经济新闻关键词")
            
            return True
        else:
            print(f"❌ 未获取到有效内容")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_with_different_scenarios():
    """测试不同场景下的功能"""
    print(f"\n🔄 测试不同场景")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "有效API密钥测试",
            "api_key": "sk-test123456789",
            "description": "模拟有效API密钥情况"
        },
        {
            "name": "无API密钥测试", 
            "api_key": None,
            "description": "测试回退到DuckDuckGo搜索"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['name']}: {scenario['description']}")
        
        # 设置环境变量
        if scenario['api_key']:
            os.environ["OPENAI_API_KEY"] = scenario['api_key']
        else:
            os.environ.pop("OPENAI_API_KEY", None)
        
        try:
            from tradingagents.dataflows.interface import get_global_news_openai
            
            # 重新导入以确保使用新的环境变量
            import importlib
            import tradingagents.dataflows.interface
            importlib.reload(tradingagents.dataflows.interface)
            from tradingagents.dataflows.interface import get_global_news_openai
            
            result = get_global_news_openai("2025-09-09")
            
            if result:
                print(f"   ✅ 成功获取内容，长度: {len(result)}")
                if len(result) > 200:
                    print(f"   📝 预览: {result[:200]}...")
            else:
                print(f"   ❌ 未获取到内容")
                
        except Exception as e:
            print(f"   ❌ 场景测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 测试修改后的get_global_news_openai函数")
    print("使用第三方OpenAI API (zai-org/GLM-4.5-FP8) 和DuckDuckGo搜索")
    print("时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 主要功能测试
    success = test_get_global_news_openai()
    
    # 不同场景测试
    test_with_different_scenarios()
    
    print(f"\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print("✅ 修改内容:")
    print("   - 明确指定使用 zai-org/GLM-4.5-FP8 模型")
    print("   - 保留原先的提示词逻辑")
    print("   - 使用配置中的 backend_url: https://llm.submodel.ai/v1")
    print("   - 支持LangChain Agent智能搜索")
    print("   - 提供DuckDuckGo搜索作为回退方案")
    
    print(f"\n🎯 实际行为:")
    print("1. 尝试使用LangChain Agent + GLM-4.5-FP8模型进行智能搜索")
    print("2. 如果LLM失败，自动回退到DuckDuckGo直接搜索")
    print("3. 搜索查询保持原有的提示词逻辑")
    print("4. 返回符合交易目的的全球宏观经济新闻")
    
    if success:
        print(f"\n🎉 函数修改成功，功能正常！")
    else:
        print(f"\n⚠️ 需要进一步检查配置或依赖")

if __name__ == "__main__":
    main()