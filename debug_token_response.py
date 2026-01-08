#!/usr/bin/env python3
"""
调试Token响应结构的脚本
查看LLM响应中是否包含token用量信息
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入必要的模块
from tradingagents.llm_adapters.third_party_openai import ThirdPartyOpenAI
from tradingagents.utils.logging_manager import get_logger
from langchain_core.messages import HumanMessage, SystemMessage

logger = get_logger('debug')

def load_env_config():
    """加载环境配置"""
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
        logger.info("✅ 环境配置加载成功")
    else:
        logger.warning("⚠️ .env文件未找到")

def debug_llm_response():
    """调试LLM响应结构"""
    logger.info("🔍 调试LLM响应结构...")
    
    # 获取API配置
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = "https://llm.submodel.ai/v1"
    
    if not api_key:
        logger.error("❌ 未配置OPENAI_API_KEY环境变量")
        return False
    
    try:
        # 创建ThirdPartyOpenAI适配器
        logger.info(f"🚀 初始化ThirdPartyOpenAI适配器...")
        
        llm = ThirdPartyOpenAI(
            model="Qwen/Qwen3-235B-A22B-Instruct-2507",
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            max_tokens=200
        )
        
        # 生成唯一会话ID
        session_id = f"debug_test_{int(time.time())}"
        logger.info(f"📝 会话ID: {session_id}")
        
        # 测试消息
        messages = [
            SystemMessage(content="你是一个专业的股票分析师。"),
            HumanMessage(content="简单分析一下茅台股票，不超过30字。")
        ]
        
        logger.info(f"🚀 发送测试请求...")
        
        # 调用LLM
        response = llm.invoke(
            messages,
            session_id=session_id,
            analysis_type="debug_test"
        )
        
        logger.info(f"✅ 收到响应:")
        logger.info(f"   内容: {response.content[:100]}{'...' if len(response.content) > 100 else ''}")
        
        # 详细检查响应结构
        logger.info(f"🔍 响应结构分析:")
        logger.info(f"   响应类型: {type(response)}")
        logger.info(f"   响应属性: {dir(response)}")
        
        # 检查是否有llm_output属性
        if hasattr(response, 'llm_output'):
            logger.info(f"   llm_output存在: {response.llm_output}")
            if response.llm_output:
                logger.info(f"   llm_output内容: {json.dumps(response.llm_output, indent=2, ensure_ascii=False)}")
                if 'token_usage' in response.llm_output:
                    logger.info(f"   token_usage: {response.llm_output['token_usage']}")
                else:
                    logger.warning(f"   ⚠️ llm_output中没有token_usage字段")
            else:
                logger.warning(f"   ⚠️ llm_output为空或None")
        else:
            logger.warning(f"   ⚠️ 响应中没有llm_output属性")
        
        # 检查其他可能包含token信息的属性
        possible_attrs = ['usage', 'token_usage', 'generation_info', 'additional_kwargs']
        for attr in possible_attrs:
            if hasattr(response, attr):
                value = getattr(response, attr)
                logger.info(f"   {attr}: {value}")
        
        # 如果响应有generations属性
        if hasattr(response, 'generations'):
            logger.info(f"   generations数量: {len(response.generations)}")
            for i, gen in enumerate(response.generations):
                logger.info(f"   generation[{i}] 类型: {type(gen)}")
                logger.info(f"   generation[{i}] 属性: {dir(gen)}")
                if hasattr(gen, 'generation_info'):
                    logger.info(f"   generation[{i}].generation_info: {gen.generation_info}")
        
        # 直接测试原始API调用
        logger.info(f"🌐 测试直接API调用获取token信息...")
        test_direct_api_call(api_key, base_url, messages)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 调试测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

def test_direct_api_call(api_key, base_url, messages):
    """直接测试API调用获取token信息"""
    import requests
    
    try:
        # 转换消息格式
        api_messages = []
        for msg in messages:
            if hasattr(msg, 'type'):
                role = 'user' if msg.type == 'human' else 'assistant'
            else:
                role = 'user'
            api_messages.append({
                'role': role,
                'content': msg.content
            })
        
        # 构建请求数据
        request_data = {
            'model': 'Qwen/Qwen3-235B-A22B-Instruct-2507',
            'messages': api_messages,
            'temperature': 0.7,
            'max_tokens': 200,
            'stream': False  # 使用非流式请求以获取完整响应
        }
        
        # 请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        api_url = f"{base_url}/chat/completions"
        logger.info(f"🌐 直接API调用: {api_url}")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=request_data,
            timeout=120
        )
        
        logger.info(f"📡 API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"📊 完整API响应结构:")
            logger.info(f"{json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 检查是否有usage字段
            if 'usage' in data:
                usage = data['usage']
                logger.info(f"✅ 找到usage字段:")
                logger.info(f"   prompt_tokens: {usage.get('prompt_tokens', 'N/A')}")
                logger.info(f"   completion_tokens: {usage.get('completion_tokens', 'N/A')}")
                logger.info(f"   total_tokens: {usage.get('total_tokens', 'N/A')}")
                return usage
            else:
                logger.warning(f"⚠️ API响应中没有usage字段")
        else:
            logger.error(f"❌ API调用失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"❌ 直接API调用失败: {e}")
    
    return None

def main():
    """主调试函数"""
    logger.info("🔍 Token响应结构调试")
    logger.info("=" * 50)
    
    # 1. 加载环境配置
    load_env_config()
    
    # 2. 调试LLM响应
    success = debug_llm_response()
    
    # 3. 总结
    logger.info("\n" + "=" * 50)
    logger.info("📋 调试总结:")
    
    if success:
        logger.info("✅ 调试完成，请查看上面的响应结构分析")
    else:
        logger.error("❌ 调试失败")
    
    logger.info("\n💡 如果API响应中有usage字段但LangChain没有提取，")
    logger.info("   需要修改ThirdPartyOpenAI适配器来直接解析API响应")

if __name__ == "__main__":
    main()