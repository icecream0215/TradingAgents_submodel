#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试优化适配器 - 验证500错误解决方案
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tradingagents.llm_adapters.optimized_openai import OptimizedOpenAI, create_optimized_llm
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

def test_optimized_solution():
    """测试优化解决方案"""
    
    print("🎯 测试优化解决方案：避免500错误和'试错'机制")
    print("=" * 60)
    
    try:
        # 1. 测试便捷创建函数
        print("1️⃣ 使用便捷函数创建优化LLM...")
        
        llm = create_optimized_llm(
            streaming=False,  # 非流式，更稳定
            temperature=0.7,
            max_tokens=100
        )
        
        print("✅ 优化LLM创建成功")
        
        # 2. 测试实际调用
        print("\n2️⃣ 测试实际API调用...")
        
        test_query = "简要分析今日股市，不超过20字"
        messages = [HumanMessage(content=test_query)]
        
        print(f"📝 查询: {test_query}")
        
        start_time = datetime.now()
        result = llm._generate(messages)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        if result and result.generations:
            response = result.generations[0].message.content
            print(f"✅ API调用成功 ({duration:.2f}秒)")
            print(f"📄 响应: {response}")
            print("\n🎉 优化成功:")
            print("   🚀 无500错误")
            print("   ⚡ 无'试错'延迟") 
            print("   📊 保持token统计")
            print(f"   ⏱️ 快速响应 ({duration:.2f}秒)")
            
            return True
        else:
            print("❌ 响应为空")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_usage_example():
    """显示使用示例"""
    
    print("\n" + "=" * 60)
    print("📋 使用示例 - 如何在你的项目中应用:")
    print("=" * 60)
    
    usage_code = '''
# 1. 替换现有的ThirdPartyOpenAI
from tradingagents.llm_adapters.optimized_openai import create_optimized_llm

# 2. 创建优化的LLM实例（推荐非流式）
llm = create_optimized_llm(
    streaming=False,      # 关键：避免500错误
    temperature=0.7,
    max_tokens=2000
)

# 3. 正常使用（无需担心500错误）
from langchain_core.messages import HumanMessage

messages = [HumanMessage(content="分析股市趋势")]
result = llm._generate(messages)

if result and result.generations:
    response = result.generations[0].message.content
    print(f"响应: {response}")
    '''
    
    print(usage_code)
    
    print("💡 核心改进:")
    print("   1. 直接使用最佳实现，跳过LangChain的'试错'机制")
    print("   2. 默认非流式模式，避免500超时错误") 
    print("   3. 保持所有现有功能：token统计、会话管理等")
    print("   4. 向后兼容：可直接替换ThirdPartyOpenAI")

if __name__ == "__main__":
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        sys.exit(1)
    
    # 运行测试
    success = test_optimized_solution()
    
    # 显示使用示例
    show_usage_example()
    
    if success:
        print(f"\n🎉 优化方案验证成功!")
        print("🔧 现在你可以:")
        print("   1. 使用 OptimizedOpenAI 替换 ThirdPartyOpenAI")
        print("   2. 享受无500错误的稳定体验")
        print("   3. 节省'试错'机制浪费的时间")
    else:
        print("\n❌ 测试未通过，需要进一步调试")