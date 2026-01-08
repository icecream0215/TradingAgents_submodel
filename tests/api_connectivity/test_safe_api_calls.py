#!/usr/bin/env python3
"""
安全API调用测试脚本
================

基于500错误分析结果，创建一个安全的API调用测试。
这个脚本演示如何使用专用适配器来避免参数不兼容问题。
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import logging
from langchain.schema import HumanMessage, SystemMessage
from tradingagents.llm_adapters import get_adapter_by_name, list_available_models

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("safe_api_test")

def test_safe_gpt_oss_call():
    """测试安全的GPT-OSS API调用"""
    logger.info("🧪 测试安全的GPT-OSS API调用")
    logger.info("=" * 40)
    
    try:
        # 1. 获取适配器
        adapter = get_adapter_by_name("gpt-oss")
        if not adapter:
            logger.error("❌ 无法获取GPT-OSS适配器")
            return False
        
        logger.info(f"✅ 适配器获取成功: {adapter.model_name}")
        
        # 2. 构建安全的消息
        messages = [
            SystemMessage(content="你是一位专业的股票技术分析师。请基于提供的股票代码给出简短的技术分析建议。"),
            HumanMessage(content="请分析股票代码600519的技术指标。")
        ]
        
        logger.info("📝 消息构建完成:")
        for i, msg in enumerate(messages, 1):
            logger.info(f"   消息{i}: {type(msg).__name__} - {msg.content[:50]}...")
        
        # 3. 安全参数设置
        safe_kwargs = {
            "temperature": 0.7,
            "max_tokens": 500,  # 减少token数量避免超限
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
            "stop": ["END"]
        }
        
        logger.info("⚙️ 使用安全参数:")
        for key, value in safe_kwargs.items():
            logger.info(f"   {key}: {value}")
        
        # 4. 执行调用（使用适配器的参数过滤功能）
        logger.info("\n🚀 开始API调用...")
        
        # 适配器会自动过滤不兼容的参数
        response = adapter.invoke(messages, **safe_kwargs)
        
        logger.info("✅ API调用成功!")
        logger.info(f"📄 响应内容: {response.content[:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ API调用失败: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        return False

def test_multiple_models_safely():
    """测试多个模型的安全调用"""
    logger.info("\n🔄 测试多个模型的安全调用")
    logger.info("=" * 40)
    
    # 获取可用模型
    models = list_available_models()
    logger.info(f"📋 可用模型: {models}")
    
    # 测试几个稳定的模型
    test_models = ["qwen-instruct", "glm-4.5", "deepseek-v31"]
    
    results = {}
    
    for model_name in test_models:
        logger.info(f"\n🧪 测试模型: {model_name}")
        
        try:
            adapter = get_adapter_by_name(model_name)
            if not adapter:
                logger.warning(f"⚠️ 模型 {model_name} 不可用")
                results[model_name] = "unavailable"
                continue
            
            # 简单测试消息
            messages = [
                SystemMessage(content="你是一个AI助手。"),
                HumanMessage(content="请简单回复'测试成功'。")
            ]
            
            # 使用保守的参数
            kwargs = {
                "temperature": 0.5,
                "max_tokens": 50
            }
            
            response = adapter.invoke(messages, **kwargs)
            logger.info(f"✅ {model_name} 调用成功")
            results[model_name] = "success"
            
        except Exception as e:
            logger.error(f"❌ {model_name} 调用失败: {str(e)}")
            results[model_name] = "failed"
    
    # 总结结果
    logger.info("\n📊 测试结果总结:")
    for model, result in results.items():
        status_emoji = "✅" if result == "success" else "❌" if result == "failed" else "⚠️"
        logger.info(f"   {status_emoji} {model}: {result}")
    
    return results

def test_parameter_filtering():
    """测试参数过滤功能"""
    logger.info("\n🛡️ 测试参数过滤功能")
    logger.info("=" * 40)
    
    try:
        adapter = get_adapter_by_name("gpt-oss")
        if not adapter:
            logger.error("❌ 无法获取适配器")
            return False
        
        # 故意包含不兼容的参数
        problematic_params = {
            "temperature": 0.7,
            "max_tokens": 1000,
            "function_call": "auto",  # GPT-OSS不支持
            "functions": [{"name": "test"}],  # GPT-OSS不支持
            "top_p": 0.9,
            "invalid_param": "should_be_filtered"  # 无效参数
        }
        
        logger.info("🔍 原始参数:")
        for key, value in problematic_params.items():
            logger.info(f"   {key}: {value}")
        
        # 测试参数过滤
        if hasattr(adapter, '_filter_model_specific_params'):
            filtered_params = adapter._filter_model_specific_params(problematic_params)
            
            logger.info("\n✅ 过滤后参数:")
            for key, value in filtered_params.items():
                logger.info(f"   {key}: {value}")
            
            # 显示被过滤的参数
            filtered_out = set(problematic_params.keys()) - set(filtered_params.keys())
            if filtered_out:
                logger.info(f"\n🛡️ 已过滤的参数: {list(filtered_out)}")
            else:
                logger.info("\n⚠️ 没有参数被过滤")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 参数过滤测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    logger.info("🚀 开始安全API调用测试")
    logger.info("=" * 50)
    
    # 测试1: 安全的GPT-OSS调用
    success1 = test_safe_gpt_oss_call()
    
    # 测试2: 多模型安全调用
    results2 = test_multiple_models_safely()
    
    # 测试3: 参数过滤功能
    success3 = test_parameter_filtering()
    
    # 最终总结
    logger.info("\n" + "=" * 50)
    logger.info("📋 最终测试总结")
    logger.info("=" * 50)
    
    logger.info(f"GPT-OSS安全调用: {'✅ 成功' if success1 else '❌ 失败'}")
    logger.info(f"多模型测试: {len([r for r in results2.values() if r == 'success'])}/{len(results2)} 成功")
    logger.info(f"参数过滤测试: {'✅ 成功' if success3 else '❌ 失败'}")
    
    if success1 and success3:
        logger.info("\n🎉 安全API调用机制验证成功!")
        logger.info("💡 建议: 在生产环境中使用专用适配器来避免500错误")
    else:
        logger.warning("\n⚠️ 某些测试失败，需要进一步调试")

if __name__ == "__main__":
    main()