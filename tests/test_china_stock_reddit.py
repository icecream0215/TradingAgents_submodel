#!/usr/bin/env python3
"""
测试直接访问Reddit API的get_stock_news_openai函数对中国股票的支持
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.dataflows.interface import get_stock_news_openai
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

def test_get_stock_news_openai_china():
    """测试get_stock_news_openai函数对中国股票的支持"""
    print("🔍 测试直接访问Reddit API的get_stock_news_openai函数对中国股票的支持...")
    
    # 测试中国股票代码
    ticker = "601138"
    curr_date = "2025-09-08"
    
    print(f"   测试股票: {ticker}")
    print(f"   日期: {curr_date}")
    
    try:
        result = get_stock_news_openai(ticker, curr_date)
        print(f"   ✅ 函数执行成功")
        print(f"   结果长度: {len(result)} 字符")
        
        if "错误" in result or "失败" in result:
            print(f"   ⚠️  返回错误信息:")
            print(f"   {result[:200]}...")
        else:
            print(f"   📊 返回结果预览:")
            print(f"   {result[:500]}...")
            
    except Exception as e:
        print(f"   ❌ 函数执行异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_get_stock_news_openai_china()
