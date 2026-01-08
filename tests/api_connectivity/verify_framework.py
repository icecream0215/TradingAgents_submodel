#!/usr/bin/env python3
"""
API连通性测试框架验证脚本
验证测试框架的基础结构是否正确
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_framework_structure():
    """测试框架结构"""
    print("🔍 验证API连通性测试框架结构...")
    
    test_dir = Path(__file__).parent
    
    # 检查必要的文件
    required_files = [
        "__init__.py",
        "test_finnhub_api.py", 
        "test_akshare_api.py",
        "test_news_social_api.py",
        "run_all_tests.py",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = test_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️ 缺少文件: {missing_files}")
        return False
    else:
        print(f"\n🎉 所有必要文件都存在！")
        return True

def check_basic_imports():
    """检查基础导入"""
    print(f"\n🔍 检查基础Python模块...")
    
    basic_modules = [
        "os", "sys", "pathlib", "datetime", "json", "warnings"
    ]
    
    failed_imports = []
    for module in basic_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️ 基础模块导入失败: {failed_imports}")
        return False
    else:
        print(f"\n✅ 所有基础模块导入成功！")
        return True

def check_optional_dependencies():
    """检查可选依赖"""
    print(f"\n🔍 检查可选依赖库...")
    
    optional_modules = {
        "requests": "HTTP请求库",
        "beautifulsoup4": "网页解析库", 
        "akshare": "A股数据库",
        "praw": "Reddit API库",
        "dotenv": "环境变量库"
    }
    
    available_modules = {}
    for module_name, description in optional_modules.items():
        try:
            if module_name == "beautifulsoup4":
                import bs4
                module_name = "bs4"
            elif module_name == "dotenv":
                from dotenv import load_dotenv
            else:
                __import__(module_name)
            print(f"✅ {module_name} - {description}")
            available_modules[module_name] = True
        except ImportError:
            print(f"⚠️ {module_name} - {description} (未安装)")
            available_modules[module_name] = False
    
    installed_count = sum(available_modules.values())
    total_count = len(available_modules)
    
    print(f"\n📊 可选依赖安装情况: {installed_count}/{total_count}")
    
    if installed_count == 0:
        print("💡 建议安装: pip install requests beautifulsoup4 akshare praw python-dotenv")
    
    return available_modules

def main():
    """主函数"""
    print("🚀 API连通性测试框架验证")
    print("=" * 50)
    
    # 1. 检查框架结构
    structure_ok = test_framework_structure()
    
    # 2. 检查基础导入
    imports_ok = check_basic_imports()
    
    # 3. 检查可选依赖
    dependencies = check_optional_dependencies()
    
    # 输出总结
    print("\n" + "=" * 50)
    print("📋 验证结果总结:")
    print(f"   框架结构: {'✅ 正常' if structure_ok else '❌ 异常'}")
    print(f"   基础模块: {'✅ 正常' if imports_ok else '❌ 异常'}")
    
    available_deps = sum(dependencies.values())
    total_deps = len(dependencies)
    print(f"   可选依赖: {available_deps}/{total_deps} 已安装")
    
    if structure_ok and imports_ok:
        print(f"\n🎉 测试框架基础结构验证通过！")
        
        if available_deps > 0:
            print(f"💡 可以开始运行部分API连通性测试")
        else:
            print(f"💡 请安装必要的依赖库后再运行具体的API测试")
        
        return True
    else:
        print(f"\n❌ 测试框架存在问题，请检查文件结构")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)