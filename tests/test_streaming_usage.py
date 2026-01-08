#!/usr/bin/env python3
"""
测试流式响应中是否包含usage信息
检查第三方API在流式响应结束时是否提供token使用统计
"""

import os
import sys
import json
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.utils.logging_manager import get_logger

logger = get_logger('stream_test')

def load_env_config():
    """加载环境配置"""
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
        logger.info("✅ 环境配置加载成功")
    else:
        logger.warning("⚠️ .env文件未找到")

def test_streaming_response_usage():
    """测试流式响应是否包含usage信息"""
    logger.info("🔍 测试流式响应中的usage信息...")
    
    # 获取API配置
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = "https://llm.submodel.ai/v1"
    
    if not api_key:
        logger.error("❌ 未配置OPENAI_API_KEY环境变量")
        return False
    
    try:
        # 构建请求数据
        request_data = {
            'model': 'Qwen/Qwen3-235B-A22B-Instruct-2507',
            'messages': [
                {'role': 'user', 'content': '请说你好'}
            ],
            'temperature': 0.7,
            'max_tokens': 50,
            'stream': True  # 流式请求
        }
        
        # 请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        api_url = f"{base_url}/chat/completions"
        logger.info(f"🌐 流式API调用: {api_url}")
        logger.info(f"📝 请求数据: {request_data}")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=request_data,
            timeout=120,
            stream=True
        )
        
        logger.info(f"📡 响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"❌ API调用失败: {response.status_code} - {response.text}")
            return False
        
        # 处理流式响应
        full_content = ""
        chunk_count = 0
        usage_found = False
        final_usage = None
        
        logger.info("📊 开始解析流式响应chunks:")
        logger.info("-" * 60)
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    data_str = decoded_line[6:]  # 移除 'data: ' 前缀
                    
                    logger.info(f"Chunk {chunk_count}: {data_str}")
                    
                    if data_str == '[DONE]':
                        logger.info("✅ 收到[DONE]标记，流式响应结束")
                        break
                    
                    try:
                        chunk_data = json.loads(data_str)
                        
                        # 检查是否有choices字段（正常内容）
                        if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                            delta = chunk_data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                full_content += content
                                logger.info(f"  内容: {repr(content)}")
                        
                        # 检查是否有usage字段
                        if 'usage' in chunk_data:
                            usage_found = True
                            final_usage = chunk_data['usage']
                            logger.info(f"🎯 找到usage信息: {final_usage}")
                        
                        # 显示完整的chunk结构（仅用于调试）
                        logger.debug(f"  完整chunk: {json.dumps(chunk_data, indent=2, ensure_ascii=False)}")
                        
                        chunk_count += 1
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ 无法解析流式数据: {data_str} - 错误: {e}")
        
        logger.info("-" * 60)
        logger.info(f"📊 流式响应分析结果:")
        logger.info(f"  总chunks数: {chunk_count}")
        logger.info(f"  完整内容: {repr(full_content)}")
        logger.info(f"  内容长度: {len(full_content)}字符")
        logger.info(f"  包含usage: {'✅' if usage_found else '❌'}")
        
        if usage_found:
            logger.info(f"🎯 Usage信息详情:")
            logger.info(f"  prompt_tokens: {final_usage.get('prompt_tokens', 'N/A')}")
            logger.info(f"  completion_tokens: {final_usage.get('completion_tokens', 'N/A')}")
            logger.info(f"  total_tokens: {final_usage.get('total_tokens', 'N/A')}")
            return final_usage
        else:
            logger.warning(f"⚠️ 流式响应中未找到usage信息")
            # 手动估算进行对比
            input_text = '请说你好'
            estimated_input = max(1, int(len(input_text) * 0.75))
            estimated_output = max(1, int(len(full_content) * 0.75))
            logger.info(f"📊 估算对比:")
            logger.info(f"  估算输入tokens: {estimated_input}")
            logger.info(f"  估算输出tokens: {estimated_output}")
            return None
            
    except Exception as e:
        logger.error(f"❌ 流式响应测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return None

def test_non_streaming_response_usage():
    """测试非流式响应的usage信息作为对比"""
    logger.info("🔍 测试非流式响应中的usage信息（对比）...")
    
    # 获取API配置
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = "https://llm.submodel.ai/v1"
    
    try:
        # 构建请求数据（非流式）
        request_data = {
            'model': 'Qwen/Qwen3-235B-A22B-Instruct-2507',
            'messages': [
                {'role': 'user', 'content': '请说你好'}
            ],
            'temperature': 0.7,
            'max_tokens': 50,
            'stream': False  # 非流式请求
        }
        
        # 请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        api_url = f"{base_url}/chat/completions"
        
        response = requests.post(
            api_url,
            headers=headers,
            json=request_data,
            timeout=120
        )
        
        logger.info(f"📡 非流式响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"📊 非流式响应结构:")
            logger.info(f"{json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if 'usage' in data:
                usage = data['usage']
                logger.info(f"✅ 非流式响应包含usage: {usage}")
                return usage
            else:
                logger.warning(f"⚠️ 非流式响应也没有usage信息")
                return None
        else:
            logger.error(f"❌ 非流式API调用失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ 非流式响应测试失败: {e}")
        return None

def main():
    """主测试函数"""
    logger.info("🎯 流式响应Usage信息测试")
    logger.info("=" * 80)
    
    # 1. 加载环境配置
    load_env_config()
    
    # 2. 测试流式响应
    streaming_usage = test_streaming_response_usage()
    
    logger.info("\n" + "=" * 80)
    
    # 3. 测试非流式响应（对比）
    non_streaming_usage = test_non_streaming_response_usage()
    
    # 4. 总结
    logger.info("\n" + "=" * 80)
    logger.info("📋 测试总结:")
    
    if streaming_usage:
        logger.info("🎉 流式响应包含准确的usage信息！")
        logger.info("💡 可以修改适配器来解析流式响应中的usage数据")
    elif non_streaming_usage:
        logger.info("⚠️ 只有非流式响应包含usage信息")
        logger.info("💡 建议：")
        logger.info("   1. 优先使用非流式响应获取准确token数据")
        logger.info("   2. 或者在流式响应后发送一个简单的非流式请求获取usage")
    else:
        logger.warning("❌ 两种响应都没有usage信息")
        logger.info("💡 只能依赖估算方法")
    
    logger.info("\n📚 如果流式响应包含usage信息，可以修改:")
    logger.info("   - tradingagents/llm_adapters/third_party_openai.py")
    logger.info("   - 在流式响应处理中检查并提取usage字段")

if __name__ == "__main__":
    main()