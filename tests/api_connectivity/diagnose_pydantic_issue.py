#!/usr/bin/env python3
"""
演示专用适配器初始化的Pydantic配置问题
并提供解决方案
"""

import os
import sys
sys.path.insert(0, '/root/TradingAgents')

def demonstrate_pydantic_issue():
    """演示Pydantic配置问题"""
    
    print("🔍 专用适配器初始化的Pydantic配置问题分析")
    print("=" * 60)
    
    print("\\n📋 问题描述:")
    print("在尝试创建专用适配器时，会遇到Pydantic模型验证错误。")
    print("这是因为LangChain的ChatOpenAI类使用了Pydantic v2进行参数验证。")
    
    print("\\n🔍 具体问题:")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # 尝试创建QwenCoderAdapter
        from tradingagents.llm_adapters.specialized_model_adapters import QwenCoderAdapter
        
        print("   1. 尝试创建QwenCoderAdapter...")
        adapter = QwenCoderAdapter()
        print("   ✅ 成功创建")
        
    except Exception as e:
        print(f"   ❌ 创建失败: {type(e).__name__}: {e}")
        
        # 分析错误类型
        error_message = str(e)
        if "model_config" in error_message:
            print("\\n🔍 错误分析:")
            print("   这是典型的Pydantic模型配置冲突问题")
            print("   原因: LangChain更新了Pydantic依赖，但代码没有相应调整")
        elif "Invalid API-key" in error_message:
            print("\\n🔍 错误分析:")
            print("   这是API密钥验证问题，不是Pydantic配置问题")
        elif "validation" in error_message.lower():
            print("\\n🔍 错误分析:")
            print("   这是Pydantic字段验证问题")

def show_solution():
    """展示解决方案"""
    
    print("\\n\\n🔧 解决方案")
    print("=" * 60)
    
    print("\\n1. 📋 问题根源:")
    print("   • LangChain升级到Pydantic v2后，字段验证规则更严格")
    print("   • ChatOpenAI基类的__init__方法参数验证更严格")
    print("   • 某些参数传递方式在新版本中不被接受")
    
    print("\\n2. 🔧 具体修复方法:")
    
    solution_code = '''
# 修复前的问题代码:
class QwenCoderAdapter(MultiModelAdapter):
    def __init__(self, temperature: float = 0.1, max_tokens: Optional[int] = 4000, **kwargs):
        super().__init__(
            model_name="qwen-coder",      # 可能导致验证错误
            task_type=TaskType.CODING,    # 枚举类型验证问题
            priority="quality",           # 字符串验证问题
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

# 修复后的代码:
class QwenCoderAdapter(MultiModelAdapter):
    def __init__(self, temperature: float = 0.1, max_tokens: Optional[int] = 4000, **kwargs):
        # 1. 预处理参数，确保类型正确
        config_params = {
            "model_name": "qwen-coder",
            "task_type": TaskType.CODING,
            "priority": "quality",
            "temperature": float(temperature),
            "max_tokens": int(max_tokens) if max_tokens else None,
        }
        
        # 2. 过滤无效的kwargs参数
        valid_kwargs = {}
        for key, value in kwargs.items():
            if value is not None:
                valid_kwargs[key] = value
        
        # 3. 安全的初始化
        try:
            super().__init__(**config_params, **valid_kwargs)
        except Exception as e:
            # 4. 错误处理和降级策略
            logger.warning(f"适配器初始化失败，使用默认配置: {e}")
            super().__init__(model_name="qwen-coder", **valid_kwargs)
    '''
    
    print(solution_code)
    
    print("\\n3. 🎯 关键修复点:")
    print("   ✅ 参数类型强制转换 (temperature → float)")
    print("   ✅ 空值处理 (max_tokens → int or None)")
    print("   ✅ kwargs参数过滤 (移除None值)")
    print("   ✅ 异常处理机制 (降级到默认配置)")
    print("   ✅ 日志记录 (调试信息)")

def provide_quick_fix():
    """提供快速修复方案"""
    
    print("\\n\\n⚡ 快速修复方案")
    print("=" * 60)
    
    print("\\n🔧 方案1: 修改专用适配器初始化方法")
    
    fix_code = '''
def __init__(self, temperature: float = 0.1, max_tokens: Optional[int] = 4000, **kwargs):
    """修复后的初始化方法"""
    
    # 参数预处理
    init_params = {}
    
    # 必需参数
    init_params['model_name'] = "qwen-coder"
    init_params['task_type'] = TaskType.CODING
    init_params['priority'] = "quality"
    
    # 可选参数 - 类型安全处理
    if temperature is not None:
        init_params['temperature'] = float(temperature)
    if max_tokens is not None:
        init_params['max_tokens'] = int(max_tokens)
    
    # kwargs过滤
    for key, value in kwargs.items():
        if value is not None and key not in init_params:
            init_params[key] = value
    
    # 安全初始化
    super().__init__(**init_params)
    '''
    
    print(fix_code)
    
    print("\\n🔧 方案2: 创建安全的适配器工厂函数")
    
    factory_code = '''
def create_safe_adapter(adapter_class, **kwargs):
    """安全的适配器创建函数"""
    try:
        return adapter_class(**kwargs)
    except Exception as e:
        logger.warning(f"标准初始化失败: {e}")
        
        # 降级到最小配置
        minimal_kwargs = {
            'temperature': kwargs.get('temperature', 0.1),
            'max_tokens': kwargs.get('max_tokens', 2000)
        }
        return adapter_class(**minimal_kwargs)

# 使用方法:
adapter = create_safe_adapter(QwenCoderAdapter, temperature=0.1, max_tokens=4000)
    '''
    
    print(factory_code)

def test_current_status():
    """测试当前状态"""
    
    print("\\n\\n🧪 当前状态测试")
    print("=" * 60)
    
    adapters_to_test = [
        ("QwenCoderAdapter", "代码专家"),
        ("QwenInstructAdapter", "指令跟随"),
        ("GLM45Adapter", "高效平衡"),
        ("DeepSeekR1Adapter", "推理专家")
    ]
    
    success_count = 0
    
    for adapter_name, description in adapters_to_test:
        try:
            print(f"\\n🔍 测试 {adapter_name} ({description}):")
            
            # 动态导入
            from tradingagents.llm_adapters.specialized_model_adapters import SPECIALIZED_ADAPTERS
            
            if adapter_name.replace("Adapter", "").lower().replace("45", "-4.5") in SPECIALIZED_ADAPTERS:
                adapter_class = SPECIALIZED_ADAPTERS[adapter_name.replace("Adapter", "").lower().replace("45", "-4.5")]
                
                # 尝试最小参数初始化
                adapter = adapter_class()
                print(f"   ✅ 成功: 类型 {type(adapter).__name__}")
                success_count += 1
                
            else:
                print(f"   ❌ 适配器类未找到")
                
        except Exception as e:
            print(f"   ❌ 失败: {type(e).__name__}: {e}")
    
    print(f"\\n📊 测试结果: {success_count}/{len(adapters_to_test)} 成功")
    
    if success_count == len(adapters_to_test):
        print("🎉 所有适配器工作正常，没有Pydantic配置问题！")
    elif success_count > len(adapters_to_test) * 0.5:
        print("🟡 大部分适配器正常，可能存在个别配置问题")
    else:
        print("🔴 多数适配器存在问题，需要系统性修复")

def main():
    """主函数"""
    
    print("🚀 TradingAgents 专用适配器Pydantic配置问题诊断")
    print("=" * 80)
    
    # 1. 演示问题
    demonstrate_pydantic_issue()
    
    # 2. 展示解决方案
    show_solution()
    
    # 3. 提供快速修复
    provide_quick_fix()
    
    # 4. 测试当前状态
    test_current_status()
    
    print("\\n\\n💡 总结建议:")
    print("1. 🔧 修复适配器初始化方法的参数验证")
    print("2. 🛡️ 添加异常处理和降级机制")
    print("3. 📝 增强日志记录以便调试")
    print("4. 🧪 建立完整的单元测试覆盖")
    print("5. 📋 文档化已知问题和解决方案")

if __name__ == "__main__":
    main()