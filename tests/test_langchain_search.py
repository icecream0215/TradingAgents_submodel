#!/usr/bin/env python3
"""
简化的实时搜索功能测试
直接测试LangChain Agent + DuckDuckGo搜索
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_langchain_agent_search():
    """直接测试LangChain Agent搜索功能"""
    print("🔍 直接测试LangChain Agent实时搜索")
    print("=" * 50)
    
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        from langchain_openai import ChatOpenAI
        from langchain.agents import initialize_agent, AgentType
        
        # 设置API信息
        api_key = os.getenv("OPENAI_API_KEY", "EMPTY")
        base_url = "https://llm.submodel.ai/v1"
        model = "zai-org/GLM-4.5-FP8"
        
        print(f"🔧 配置信息:")
        print(f"   模型: {model}")
        print(f"   端点: {base_url}")
        print(f"   API密钥: {api_key[:20] if api_key != 'EMPTY' else 'EMPTY'}...")
        
        # 创建LLM实例
        print(f"\n🤖 创建LLM实例...")
        llm = ChatOpenAI(
            model=model,
            base_url=base_url,
            api_key=api_key,
            temperature=0.7,
            max_tokens=1000
        )
        
        # 创建搜索工具
        print(f"🔍 创建搜索工具...")
        tools = [DuckDuckGoSearchRun()]
        
        # 初始化agent
        print(f"🤝 初始化Agent...")
        agent = initialize_agent(
            tools, 
            llm, 
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True  # 启用详细输出以便调试
        )
        
        # 执行简单搜索测试
        current_date = datetime.now().strftime("%Y-%m-%d")
        search_query = f"2025年9月9日的最新AI新闻"
        
        print(f"\n🚀 执行搜索查询: {search_query}")
        print(f"⏰ 时间: {current_date}")
        print(f"💡 这可能需要一些时间...")
        
        response = agent.run(search_query)
        
        print(f"\n✅ 搜索完成!")
        print(f"📄 结果长度: {len(response)} 字符")
        print(f"\n--- 搜索结果 ---")
        print(response)
        print(f"--- 结果结束 ---")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_duckduckgo_only():
    """单独测试DuckDuckGo搜索工具"""
    print("\n🦆 单独测试DuckDuckGo搜索工具")
    print("=" * 40)
    
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        
        search = DuckDuckGoSearchRun()
        
        query = "OpenAI GPT latest news September 2025"
        print(f"🔍 搜索查询: {query}")
        
        result = search.run(query)
        
        print(f"✅ DuckDuckGo搜索成功!")
        print(f"📄 结果长度: {len(result)} 字符")
        print(f"\n--- 搜索结果预览 ---")
        preview = result[:300] + "..." if len(result) > 300 else result
        print(preview)
        print(f"--- 预览结束 ---")
        
        return True
        
    except Exception as e:
        print(f"❌ DuckDuckGo搜索失败: {e}")
        return False

def test_chatgpt_only():
    """单独测试ChatGPT连接"""
    print("\n🤖 单独测试ChatGPT连接")
    print("=" * 30)
    
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        
        api_key = os.getenv("OPENAI_API_KEY", "EMPTY")
        base_url = "https://llm.submodel.ai/v1"
        model = "zai-org/GLM-4.5-FP8"
        
        llm = ChatOpenAI(
            model=model,
            base_url=base_url,
            api_key=api_key,
            temperature=0.7,
            max_tokens=100
        )
        
        message = HumanMessage(content="请简单介绍一下你自己")
        print(f"💬 发送测试消息...")
        
        response = llm.invoke([message])
        
        print(f"✅ LLM连接成功!")
        print(f"📄 响应: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 LangChain Agent实时搜索功能测试")
    print("时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 分步测试
    test1 = test_duckduckgo_only()
    test2 = test_chatgpt_only()
    
    if test1 and test2:
        print(f"\n🎯 两个组件都正常，开始完整测试...")
        test3 = test_langchain_agent_search()
    else:
        print(f"\n⚠️ 基础组件测试失败，跳过完整测试")
        test3 = False
    
    print(f"\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    print(f"🦆 DuckDuckGo搜索: {'✅ 成功' if test1 else '❌ 失败'}")
    print(f"🤖 LLM连接: {'✅ 成功' if test2 else '❌ 失败'}")
    print(f"🤝 Agent集成: {'✅ 成功' if test3 else '❌ 失败'}")
    
    if test1 and test2 and test3:
        print(f"\n🎉 所有测试通过! LangChain Agent实时搜索功能正常工作")
    else:
        print(f"\n⚠️ 部分测试失败，需要进一步调试")
    
    return test1 and test2 and test3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)