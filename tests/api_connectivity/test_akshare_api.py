#!/usr/bin/env python3
"""
AKShare API 连通性测试
测试AKShare库对A股和港股数据的访问是否正常

支持的数据类型：
- A股实时数据 (A-share real-time data)
- 港股数据 (Hong Kong stock data)
- 基本面数据 (Fundamental data)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import warnings

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 忽略警告
warnings.filterwarnings('ignore')

class AKShareAPITester:
    """AKShare API 测试器"""
    
    def __init__(self):
        self.ak = None
        self._import_akshare()
    
    def _import_akshare(self) -> bool:
        """导入AKShare库"""
        try:
            import akshare as ak
            self.ak = ak
            print("✅ AKShare 库导入成功")
            return True
        except ImportError:
            print("❌ AKShare 库未安装")
            print("💡 请运行: pip install akshare")
            return False
    
    def test_a_share_realtime(self) -> bool:
        """测试A股实时数据"""
        print("\n📈 测试A股实时数据...")
        try:
            if not self.ak:
                return False
            
            # 获取A股实时行情
            df = self.ak.stock_zh_a_spot_em()
            
            if df is not None and len(df) > 0:
                print(f"✅ 获取A股实时数据成功")
                print(f"   股票数量: {len(df)}")
                print(f"   示例股票: {df.iloc[0]['名称']} ({df.iloc[0]['代码']})")
                print(f"   当前价格: {df.iloc[0]['最新价']}")
                return True
            else:
                print("❌ 获取A股实时数据失败")
                return False
                
        except Exception as e:
            print(f"❌ A股实时数据测试异常: {e}")
            return False
    
    def test_a_share_individual(self, symbol: str = "000001") -> bool:
        """测试单个A股股票数据"""
        print(f"\n📊 测试单个A股数据 ({symbol})...")
        try:
            if not self.ak:
                return False
            
            # 获取个股实时数据
            df = self.ak.stock_individual_info_em(symbol=symbol)
            
            if df is not None and len(df) > 0:
                print(f"✅ 获取 {symbol} 个股数据成功")
                # 显示一些关键信息
                for idx, row in df.head(5).iterrows():
                    print(f"   {row['item']}: {row['value']}")
                return True
            else:
                print(f"❌ 获取 {symbol} 个股数据失败")
                return False
                
        except Exception as e:
            print(f"❌ 个股数据测试异常: {e}")
            return False
    
    def test_hk_stock_data(self) -> bool:
        """测试港股数据"""
        print("\n🇭🇰 测试港股数据...")
        try:
            if not self.ak:
                return False
            
            # 获取港股实时行情
            df = self.ak.stock_hk_spot_em()
            
            if df is not None and len(df) > 0:
                print(f"✅ 获取港股数据成功")
                print(f"   股票数量: {len(df)}")
                print(f"   示例股票: {df.iloc[0]['名称']} ({df.iloc[0]['代码']})")
                print(f"   当前价格: {df.iloc[0]['最新价']}")
                return True
            else:
                print("❌ 获取港股数据失败")
                return False
                
        except Exception as e:
            print(f"❌ 港股数据测试异常: {e}")
            return False
    
    def test_fundamental_data(self, symbol: str = "000001") -> bool:
        """测试基本面数据"""
        print(f"\n📋 测试基本面数据 ({symbol})...")
        try:
            if not self.ak:
                return False
            
            # 获取财务指标
            df = self.ak.stock_financial_abstract_ths(symbol=symbol)
            
            if df is not None and len(df) > 0:
                print(f"✅ 获取 {symbol} 基本面数据成功")
                print(f"   数据条数: {len(df)}")
                # 显示最新的财务数据
                latest = df.iloc[0]
                print(f"   报告期: {latest['报告期']}")
                print(f"   营业收入: {latest.get('营业收入', 'N/A')}")
                print(f"   净利润: {latest.get('净利润', 'N/A')}")
                return True
            else:
                print(f"❌ 获取 {symbol} 基本面数据失败")
                return False
                
        except Exception as e:
            print(f"❌ 基本面数据测试异常: {e}")
            return False
    
    def test_market_index(self) -> bool:
        """测试市场指数数据"""
        print("\n📊 测试市场指数数据...")
        try:
            if not self.ak:
                return False
            
            # 获取上证指数实时数据
            df = self.ak.index_zh_a_hist(symbol="000001", period="daily", start_date="20240101")
            
            if df is not None and len(df) > 0:
                print(f"✅ 获取上证指数数据成功")
                print(f"   数据天数: {len(df)}")
                latest = df.iloc[-1]
                print(f"   最新日期: {latest['日期']}")
                print(f"   收盘价: {latest['收盘']}")
                print(f"   涨跌幅: {latest.get('涨跌幅', 'N/A')}%")
                return True
            else:
                print("❌ 获取上证指数数据失败")
                return False
                
        except Exception as e:
            print(f"❌ 市场指数测试异常: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """运行所有测试"""
        print("🚀 开始 AKShare API 连通性测试...")
        print("=" * 50)
        
        results = {}
        
        # 0. 检查库导入
        if not self.ak:
            results['library_import'] = False
            return results
        results['library_import'] = True
        
        # 1. 测试A股实时数据
        results['a_share_realtime'] = self.test_a_share_realtime()
        
        # 2. 测试个股数据
        results['a_share_individual'] = self.test_a_share_individual()
        
        # 3. 测试港股数据
        results['hk_stock_data'] = self.test_hk_stock_data()
        
        # 4. 测试基本面数据
        results['fundamental_data'] = self.test_fundamental_data()
        
        # 5. 测试市场指数
        results['market_index'] = self.test_market_index()
        
        # 输出总结
        print("\n" + "=" * 50)
        print("📊 AKShare API 测试结果总结:")
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
        
        success_rate = sum(results.values()) / len(results) * 100
        print(f"\n🎯 总体成功率: {success_rate:.1f}%")
        
        return results

def main():
    """主函数"""
    tester = AKShareAPITester()
    results = tester.run_all_tests()
    
    # 返回退出码
    if all(results.values()):
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️ 部分测试失败，请检查网络连接和依赖库")
        sys.exit(1)

if __name__ == "__main__":
    main()