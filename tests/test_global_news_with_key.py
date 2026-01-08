#!/usr/bin/env python3
"""
测试带有API密钥的全球新闻搜索功能
"""

import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, '/root/TradingAgents')

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_with_dummy_key():
    """测试使用虚拟API密钥的情况"""
    print("=" * 60)
    print("测试1: 使用虚拟API密钥")
    print("=" * 60)
    
    # 设置一个虚拟的API密钥
    os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-testing"
    
    try:
        from tradingagents.dataflows.interface import get_global_news_openai
        
        # 测试日期
        test_date = "2025-09-15"
        print(f"搜索日期: {test_date}")
        
        # 执行搜索
        result = get_global_news_openai(test_date)
        
        print(f"结果长度: {len(result)} 字符")
        print(f"结果预览:\n{result[:500]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_without_key():
    """测试没有API密钥的情况"""
    print("\n" + "=" * 60)
    print("测试2: 没有API密钥")
    print("=" * 60)
    
    # 清除所有可能的API密钥环境变量
    for key in ["OPENAI_API_KEY", "CUSTOM_OPENAI_API_KEY", "API_KEY"]:
        if key in os.environ:
            del os.environ[key]
    
    try:
        from tradingagents.dataflows.interface import get_global_news_openai
        
        # 测试日期
        test_date = "2025-09-15"
        print(f"搜索日期: {test_date}")
        
        # 执行搜索
        result = get_global_news_openai(test_date)
        
        print(f"结果长度: {len(result)} 字符")
        print(f"结果预览:\n{result[:500]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_duckduckgo_direct():
    """直接测试DuckDuckGo搜索"""
    print("\n" + "=" * 60)
    print("测试3: 直接DuckDuckGo搜索")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.interface import _get_global_news_duckduckgo_only
        
        # 测试日期
        test_date = "2025-09-15"
        print(f"搜索日期: {test_date}")
        
        # 执行搜索
        result = _get_global_news_duckduckgo_only(test_date)
        
        print(f"结果长度: {len(result)} 字符")
        print(f"结果预览:\n{result[:500]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试带有API密钥管理的全球新闻搜索功能\n")
    
    results = []
    
    # 测试1: 使用虚拟API密钥（会失败但应该回退到DuckDuckGo）
    results.append(("虚拟API密钥", test_with_dummy_key()))
    
    # 测试2: 没有API密钥（应该直接使用DuckDuckGo）
    results.append(("无API密钥", test_without_key()))
    
    # 测试3: 直接DuckDuckGo搜索
    results.append(("直接DuckDuckGo", test_duckduckgo_direct()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(success for _, success in results)
    print(f"\n总体测试结果: {'✅ 全部通过' if all_passed else '❌ 部分失败'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)