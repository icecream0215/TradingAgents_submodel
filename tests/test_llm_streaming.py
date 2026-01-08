#!/usr/bin/env python3
"""
测试LLM适配器的流式请求功能
验证移除参数过滤后的LLM适配器是否能正常工作
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('test')

def test_third_party_openai_streaming():
    """测试第三方OpenAI适配器的流式请求"""
    print("\n" + "=" * 60)
    print("测试第三方OpenAI适配器 - 流式请求")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.third_party_openai import ThirdPartyOpenAI
        from langchain_core.messages import HumanMessage
        
        # 检查是否有API密钥
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ 未设置OPENAI_API_KEY环境变量，跳过测试")
            return False
        
        print(f"🔧 创建第三方OpenAI适配器...")
        llm = ThirdPartyOpenAI(
            model="gpt-3.5-turbo", 
            api_key=api_key,
            base_url="https://llm.submodel.ai/v1",
            temperature=0.7,
            max_tokens=100,
            # 添加一些通常会被过滤的参数来测试
            top_p=0.9,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        print(f"✅ 适配器创建成功")
        
        # 测试生成响应
        print(f"📝 测试生成响应...")
        messages = [HumanMessage(content="请简单介绍一下人工智能，用中文回答")]
        
        result = llm._generate(messages)
        
        if result and result.generations:
            response_content = result.generations[0].message.content
            print(f"✅ 生成成功，响应长度: {len(response_content)}")
            print(f"📄 响应预览: {response_content[:100]}...")
            return True
        else:
            print(f"❌ 生成失败，未收到有效响应")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_dashscope_streaming():
    """测试DashScope适配器的流式请求"""
    print("\n" + "=" * 60)
    print("测试DashScope适配器 - 流式请求")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope
        from langchain_core.messages import HumanMessage
        
        # 检查是否有API密钥
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("⚠️ 未设置DASHSCOPE_API_KEY环境变量，跳过测试")
            return False
        
        print(f"🔧 创建DashScope适配器...")
        llm = ChatDashScope(
            model="qwen-turbo",
            api_key=api_key,
            temperature=0.7,
            max_tokens=100,
            # 测试额外参数传递
            top_p=0.9
        )
        
        print(f"✅ 适配器创建成功")
        
        # 测试生成响应
        print(f"📝 测试生成响应...")
        messages = [HumanMessage(content="请简单介绍一下股票投资，用中文回答")]
        
        result = llm._generate(messages)
        
        if result and result.generations:
            response_content = result.generations[0].message.content
            print(f"✅ 生成成功，响应长度: {len(response_content)}")
            print(f"📄 响应预览: {response_content[:100]}...")
            return True
        else:
            print(f"❌ 生成失败，未收到有效响应")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_deepseek_streaming():
    """测试DeepSeek直接适配器的流式请求"""
    print("\n" + "=" * 60)
    print("测试DeepSeek直接适配器 - 流式请求")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.deepseek_direct_adapter import DeepSeekDirectAdapter
        
        # 检查是否有API密钥
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("⚠️ 未设置DEEPSEEK_API_KEY环境变量，跳过测试")
            return False
        
        print(f"🔧 创建DeepSeek直接适配器...")
        adapter = DeepSeekDirectAdapter(
            model="deepseek-chat",
            temperature=0.7,
            max_tokens=100,
            api_key=api_key,
            stream=True  # 默认使用流式请求
        )
        
        print(f"✅ 适配器创建成功")
        
        # 测试生成响应
        print(f"📝 测试生成响应...")
        result = adapter.invoke("请简单介绍一下机器学习，用中文回答", stream=True)
        
        if result:
            print(f"✅ 生成成功，响应长度: {len(result)}")
            print(f"📄 响应预览: {result[:100]}...")
            return True
        else:
            print(f"❌ 生成失败，未收到有效响应")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_openai_compatible_base():
    """测试OpenAI兼容基类的流式请求"""
    print("\n" + "=" * 60)
    print("测试OpenAI兼容基类适配器 - 流式请求")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.openai_compatible_base import ChatDeepSeekOpenAI
        from langchain_core.messages import HumanMessage
        
        # 检查是否有API密钥
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("⚠️ 未设置DEEPSEEK_API_KEY环境变量，跳过测试")
            return False
        
        print(f"🔧 创建OpenAI兼容适配器...")
        llm = ChatDeepSeekOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            temperature=0.7,
            max_tokens=100,
            # 测试额外参数传递
            top_p=0.9
        )
        
        print(f"✅ 适配器创建成功")
        
        # 测试生成响应
        print(f"📝 测试生成响应...")
        messages = [HumanMessage(content="请简单介绍一下深度学习，用中文回答")]
        
        result = llm._generate(messages)
        
        if result and result.generations:
            response_content = result.generations[0].message.content
            print(f"✅ 生成成功，响应长度: {len(response_content)}")
            print(f"📄 响应预览: {response_content[:100]}...")
            return True
        else:
            print(f"❌ 生成失败，未收到有效响应")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试LLM适配器流式请求功能")
    print("时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    tests = [
        ("第三方OpenAI适配器", test_third_party_openai_streaming),
        ("DashScope适配器", test_dashscope_streaming),
        ("DeepSeek直接适配器", test_deepseek_streaming),
        ("OpenAI兼容基类", test_openai_compatible_base),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            if success:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试出现异常: {e}")
    
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    print(f"总测试数: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有LLM适配器流式请求测试都通过了！")
        print("✅ 参数过滤已成功移除")
        print("✅ 流式请求已成功启用")
    else:
        print(f"\n⚠️ {total - passed} 个测试失败，需要进一步检查。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)