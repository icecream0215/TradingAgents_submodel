#!/usr/bin/env python3
"""
测试导入路径问题
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("测试导入路径...")

try:
    print("尝试从 utils.analysis_runner 导入 format_analysis_results...")
    from web.utils.analysis_runner import format_analysis_results
    print("✅ 成功导入")
except ImportError as e:
    print(f"❌ 导入失败: {e}")

try:
    print("尝试从 web.utils.analysis_runner 导入 format_analysis_results...")
    from web.utils.analysis_runner import format_analysis_results
    print("✅ 成功导入")
except ImportError as e:
    print(f"❌ 导入失败: {e}")

print("\nPython路径:")
for path in sys.path:
    print(f"  {path}")
