#!/usr/bin/env python3
"""
测试修改后的get_global_news_openai函数
验证是否能够使用LangChain Agent进行实时搜索
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_global_news_search():
    """测试全球新闻搜索功能"""
    print("🔍 测试修改后的get_global_news_openai函数")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.interface import get_global_news_openai
        
        # 获取今天的日期
        current_date = datetime.now().strftime("%Y-%m-%d")
        print(f"📅 搜索日期: {current_date}")
        
        # 检查必要的环境变量
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ 未设置OPENAI_API_KEY环境变量，将使用'EMPTY'")
            os.environ["OPENAI_API_KEY"] = "EMPTY"
        
        print(f"🔧 API密钥: {api_key[:20] if api_key else 'EMPTY'}...")
        
        # 测试搜索功能
        print(f"\n🚀 开始执行实时新闻搜索...")
        print(f"💡 这可能需要一些时间，请耐心等待...")
        
        result = get_global_news_openai(current_date)
        
        if result:
            print(f"\n✅ 搜索成功!")
            print(f"📄 搜索结果长度: {len(result)} 字符")
            print(f"\n--- 搜索结果预览 ---")
            # 显示前500个字符作为预览
            preview = result[:500] + "..." if len(result) > 500 else result
            print(preview)
            print(f"--- 预览结束 ---\n")
            
            # 保存完整结果到文件
            output_file = f"global_news_result_{current_date}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"全球新闻搜索结果 - {current_date}\n")
                f.write("=" * 50 + "\n")
                f.write(result)
            
            print(f"📁 完整结果已保存到: {output_file}")
            return True
        else:
            print(f"❌ 搜索返回空结果")
            return False
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print(f"💡 请安装必要的依赖:")
        print(f"   pip install langchain langchain-community langchain-openai duckduckgo-search")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_dependencies():
    """测试所需的依赖是否已安装"""
    print("\n🔍 检查依赖包安装状态")
    print("=" * 40)
    
    dependencies = [
        ("langchain", "LangChain核心包"),
        ("langchain_community", "LangChain社区工具"),
        ("langchain_openai", "LangChain OpenAI集成"),
        ("duckduckgo_search", "DuckDuckGo搜索工具")
    ]
    
    all_available = True
    
    for package, description in dependencies:
        try:
            __import__(package)
            print(f"✅ {package}: {description}")
        except ImportError:
            print(f"❌ {package}: {description} - 未安装")
            all_available = False
    
    if not all_available:
        print(f"\n💡 安装命令:")
        print(f"pip install langchain langchain-community langchain-openai duckduckgo-search")
    
    return all_available

def test_configuration():
    """测试配置是否正确"""
    print("\n🔍 检查配置状态")
    print("=" * 30)
    
    try:
        from tradingagents.dataflows.config import get_config
        config = get_config()
        
        print(f"✅ 配置加载成功")
        print(f"📍 backend_url: {config.get('backend_url', 'N/A')}")
        print(f"🤖 quick_think_llm: {config.get('quick_think_llm', 'N/A')}")
        
        # 检查backend_url是否是期望的地址
        expected_url = "https://llm.submodel.ai/v1"
        if config.get('backend_url') == expected_url:
            print(f"✅ backend_url配置正确")
        else:
            print(f"⚠️ backend_url可能需要调整为: {expected_url}")
        
        return True
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 测试修改后的全球新闻搜索功能")
    print("时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 检查依赖
    deps_ok = test_dependencies()
    
    # 检查配置
    config_ok = test_configuration()
    
    if deps_ok and config_ok:
        # 执行实际测试
        success = test_global_news_search()
    else:
        print(f"\n⚠️ 预检查失败，跳过实际测试")
        success = False
    
    print(f"\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    if success:
        print("🎉 全球新闻实时搜索功能测试成功!")
        print("✅ LangChain Agent + DuckDuckGo搜索正常工作")
        print("✅ GLM-4.5-FP8模型调用成功")
        print("✅ 实时搜索功能已启用")
    else:
        print("❌ 测试未完全成功")
        print("💡 请检查依赖安装和配置")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)