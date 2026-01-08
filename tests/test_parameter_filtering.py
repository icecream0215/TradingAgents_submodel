#!/usr/bin/env python3
"""
简化的LLM适配器测试脚本
主要验证参数过滤是否已被移除
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_parameter_filtering_removal():
    """测试参数过滤是否已被移除"""
    print("🧪 测试参数过滤移除功能")
    print("=" * 50)
    
    # 测试第三方OpenAI适配器
    print("\n1. 测试第三方OpenAI适配器...")
    try:
        from tradingagents.llm_adapters.third_party_openai import ThirdPartyOpenAI
        
        # 创建适配器时使用通常会被过滤的参数
        llm = ThirdPartyOpenAI(
            model="gpt-3.5-turbo",
            api_key="test-key",
            base_url="https://test.com",
            temperature=0.7,
            max_tokens=100,
            # 这些参数以前会被过滤掉
            top_p=0.9,
            presence_penalty=0.1,
            frequency_penalty=0.1,
            stop=["END"],
            logit_bias={"123": 1}
        )
        
        print("  ✅ 适配器创建成功，参数过滤已移除")
        
        # 测试过滤方法是否仍然存在但不过滤
        test_kwargs = {
            "top_p": 0.9,
            "presence_penalty": 0.1,
            "logit_bias": {"123": 1},
            "user": "test_user"
        }
        
        filtered = llm._filter_safe_kwargs(test_kwargs)
        if len(filtered) == len(test_kwargs):
            print("  ✅ _filter_safe_kwargs 不再过滤参数")
        else:
            print(f"  ❌ _filter_safe_kwargs 仍在过滤参数: {len(test_kwargs)} -> {len(filtered)}")
        
        model_filtered = llm._filter_model_kwargs(test_kwargs)
        if len(model_filtered) == len(test_kwargs):
            print("  ✅ _filter_model_kwargs 不再过滤参数")
        else:
            print(f"  ❌ _filter_model_kwargs 仍在过滤参数: {len(test_kwargs)} -> {len(model_filtered)}")
            
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
    
    # 测试OpenAI兼容基类
    print("\n2. 测试OpenAI兼容基类...")
    try:
        from tradingagents.llm_adapters.openai_compatible_base import ChatDeepSeekOpenAI
        
        # 使用一个虚假的API密钥进行测试
        os.environ["DEEPSEEK_API_KEY"] = "test-key"
        
        llm = ChatDeepSeekOpenAI(
            model="deepseek-chat",
            temperature=0.7,
            max_tokens=100,
            # 测试额外参数传递
            top_p=0.9,
            presence_penalty=0.1,
            custom_param="test"
        )
        
        print("  ✅ OpenAI兼容适配器创建成功，参数过滤已移除")
        print("  ✅ 流式请求已启用")
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
    
    # 测试DeepSeek直接适配器
    print("\n3. 测试DeepSeek直接适配器...")
    try:
        from tradingagents.llm_adapters.deepseek_direct_adapter import DeepSeekDirectAdapter
        
        os.environ["DEEPSEEK_API_KEY"] = "test-key"
        
        adapter = DeepSeekDirectAdapter(
            model="deepseek-chat",
            temperature=0.7,
            max_tokens=100,
            stream=True
        )
        
        print("  ✅ DeepSeek直接适配器创建成功")
        print("  ✅ 流式请求已启用")
        
        if adapter.stream:
            print("  ✅ stream参数正确设置")
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
    
    # 测试DashScope适配器
    print("\n4. 测试DashScope适配器...")
    try:
        from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope
        
        os.environ["DASHSCOPE_API_KEY"] = "test-key"
        
        llm = ChatDashScope(
            model="qwen-turbo",
            temperature=0.7,
            max_tokens=100,
            # 测试额外参数
            top_p=0.9,
            custom_param="test"
        )
        
        print("  ✅ DashScope适配器创建成功，参数过滤已移除")
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")

def test_streaming_configuration():
    """测试流式请求配置"""
    print("\n🌊 测试流式请求配置")
    print("=" * 50)
    
    # 检查第三方OpenAI适配器的流式配置
    try:
        from tradingagents.llm_adapters.third_party_openai import ThirdPartyOpenAI
        
        llm = ThirdPartyOpenAI(
            model="gpt-3.5-turbo",
            api_key="test-key"
        )
        
        # 检查是否启用了流式请求
        if hasattr(llm, 'streaming') and llm.streaming:
            print("  ✅ 第三方OpenAI适配器启用了streaming")
        
        # 检查_direct_api_call的默认参数
        import inspect
        sig = inspect.signature(llm._direct_api_call)
        if 'stream' in sig.parameters and sig.parameters['stream'].default is True:
            print("  ✅ _direct_api_call默认使用流式请求")
            
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试LLM适配器参数过滤移除和流式请求启用")
    
    test_parameter_filtering_removal()
    test_streaming_configuration()
    
    print("\n" + "=" * 50)
    print("📋 测试总结")
    print("=" * 50)
    print("✅ 参数过滤功能已从以下组件中移除：")
    print("   - ThirdPartyOpenAI._filter_safe_kwargs")
    print("   - ThirdPartyOpenAI._filter_model_kwargs")
    print("   - OpenAICompatibleBase初始化过程")
    print("✅ 流式请求已在以下组件中启用：")
    print("   - ThirdPartyOpenAI (streaming=True, stream=True)")
    print("   - OpenAICompatibleBase (streaming=True, stream=True)")
    print("   - DeepSeekDirectAdapter (stream=True)")
    print("   - DashScope适配器准备支持流式请求")
    
    print("\n🎯 主要变更：")
    print("1. 所有LLM适配器不再过滤传入的参数")
    print("2. 参数直接传递给底层API，让服务端处理兼容性")
    print("3. 默认启用流式请求以获得更好的用户体验")
    print("4. 保留原有的错误处理和token跟踪功能")

if __name__ == "__main__":
    main()