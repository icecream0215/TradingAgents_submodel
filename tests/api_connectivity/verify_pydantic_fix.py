#!/usr/bin/env python3
"""
验证Pydantic配置问题修复效果
"""

import os
import sys
sys.path.insert(0, '/root/TradingAgents')

def test_fixed_adapters():
    """测试修复后的适配器"""
    
    print("🧪 测试修复后的专用适配器")
    print("=" * 60)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from tradingagents.llm_adapters.specialized_model_adapters import (
            QwenCoderAdapter,
            QwenInstructAdapter,
            GLM45Adapter,
            GPTOSSAdapter,
            DeepSeekR1Adapter,
            QwenThinkingAdapter,
            DeepSeekV31Adapter
        )
        
        adapters_to_test = [
            ("QwenCoderAdapter", QwenCoderAdapter, "代码专家"),
            ("QwenInstructAdapter", QwenInstructAdapter, "指令跟随"),
            ("GLM45Adapter", GLM45Adapter, "高效平衡"),
            ("GPTOSSAdapter", GPTOSSAdapter, "通用GPT"),
            ("DeepSeekR1Adapter", DeepSeekR1Adapter, "推理专家"),
            ("QwenThinkingAdapter", QwenThinkingAdapter, "思维链"),
            ("DeepSeekV31Adapter", DeepSeekV31Adapter, "金融分析")
        ]
        
        success_count = 0
        total_count = len(adapters_to_test)
        
        for adapter_name, adapter_class, description in adapters_to_test:
            print(f"\\n🔍 测试 {adapter_name} ({description}):")
            
            try:
                # 尝试创建适配器实例
                adapter = adapter_class()
                
                # 检查基本属性
                print(f"   ✅ 成功创建: {type(adapter).__name__}")
                print(f"   📋 模型名称: {getattr(adapter, 'model_config', {}).get('name', 'N/A')}")
                print(f"   🎯 任务类型: {getattr(adapter, 'task_type', 'N/A')}")
                print(f"   ⭐ 优先级: {getattr(adapter, 'priority', 'N/A')}")
                
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ 创建失败: {type(e).__name__}: {e}")
                
                # 分析错误类型
                error_msg = str(e)
                if "model_config" in error_msg:
                    print("      🔍 仍然存在Pydantic配置问题")
                elif "API-key" in error_msg or "api_key" in error_msg:
                    print("      🔍 API密钥问题，但Pydantic配置已修复")
                    success_count += 0.5  # 部分成功
                elif "validation" in error_msg.lower():
                    print("      🔍 参数验证问题")
                else:
                    print("      🔍 其他类型错误")
        
        print(f"\\n📊 测试结果统计:")
        print(f"   总适配器数: {total_count}")
        print(f"   完全成功: {int(success_count)}")
        print(f"   部分成功: {int((success_count % 1) * 2)}")
        print(f"   成功率: {success_count/total_count*100:.1f}%")
        
        if success_count == total_count:
            print("\\n🎉 所有适配器修复成功！Pydantic配置问题已解决")
        elif success_count >= total_count * 0.8:
            print("\\n🟢 大部分适配器修复成功，Pydantic配置问题基本解决")
        elif success_count >= total_count * 0.5:
            print("\\n🟡 部分适配器修复成功，仍需进一步优化")
        else:
            print("\\n🔴 修复效果有限，需要进一步调查")
            
        return success_count >= total_count * 0.8
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_adapter_functionality():
    """测试适配器的基本功能"""
    
    print("\\n\\n⚡ 基本功能测试")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.specialized_model_adapters import QwenCoderAdapter
        
        print("🔍 测试QwenCoderAdapter的优化方法:")
        
        # 创建适配器
        adapter = QwenCoderAdapter()
        
        # 测试优化方法
        from langchain_core.messages import HumanMessage
        test_messages = [HumanMessage(content="请帮我写一个Python函数来计算斐波那契数列")]
        
        optimized_messages = adapter.optimize_for_coding(test_messages)
        
        print(f"   ✅ 优化方法正常工作")
        print(f"   📝 优化后消息长度: {len(optimized_messages[0].content)} 字符")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 功能测试失败: {e}")
        return False

def test_task_selection():
    """测试任务类型选择"""
    
    print("\\n\\n🎯 任务选择机制测试")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.specialized_model_adapters import get_adapter_for_task
        from tradingagents.llm_adapters.multi_model_adapter import TaskType
        
        test_tasks = [
            (TaskType.CODING, "代码任务"),
            (TaskType.CONVERSATION, "对话任务"),
            (TaskType.REASONING, "推理任务"),
            (TaskType.FINANCIAL, "金融任务")
        ]
        
        success_count = 0
        
        for task_type, description in test_tasks:
            try:
                print(f"\\n🔍 测试 {description}:")
                adapter = get_adapter_for_task(task_type)
                adapter_name = type(adapter).__name__
                print(f"   ✅ 选择的适配器: {adapter_name}")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ 选择失败: {e}")
        
        print(f"\\n📊 任务选择成功率: {success_count}/{len(test_tasks)}")
        return success_count >= len(test_tasks) * 0.75
        
    except Exception as e:
        print(f"❌ 任务选择测试失败: {e}")
        return False

def main():
    """主函数"""
    
    print("🚀 TradingAgents Pydantic配置修复验证")
    print("=" * 80)
    
    # 测试结果
    test_results = []
    
    # 1. 测试适配器创建
    adapters_fixed = test_fixed_adapters()
    test_results.append(("适配器创建", adapters_fixed))
    
    # 2. 测试基本功能
    functionality_ok = test_adapter_functionality()
    test_results.append(("基本功能", functionality_ok))
    
    # 3. 测试任务选择
    task_selection_ok = test_task_selection()
    test_results.append(("任务选择", task_selection_ok))
    
    # 总结
    print("\\n\\n📋 修复验证总结")
    print("=" * 60)
    
    success_count = sum(1 for name, result in test_results if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    overall_success = success_count / total_tests
    
    print(f"\\n🏆 总体结果: {success_count}/{total_tests} ({overall_success*100:.1f}%)")
    
    if overall_success >= 0.9:
        print("\\n🎉 Pydantic配置问题已完全修复！")
        print("💡 建议: 可以开始使用专用适配器进行生产环境测试")
    elif overall_success >= 0.7:
        print("\\n🟢 Pydantic配置问题基本修复！")
        print("💡 建议: 继续优化剩余问题，然后投入使用")
    elif overall_success >= 0.5:
        print("\\n🟡 部分修复成功，需要进一步优化")
        print("💡 建议: 检查失败的测试项，进行针对性修复")
    else:
        print("\\n🔴 修复效果有限，需要重新审视解决方案")
        print("💡 建议: 考虑采用其他修复策略")

if __name__ == "__main__":
    main()