"""
智能模型选择器
基于任务特征、性能需求和历史数据自动选择最佳模型
"""

import os
import json
import time
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path

from .multi_model_adapter import TaskType, MODEL_CONFIGURATIONS, ModelCapability
from tradingagents.utils.logging_manager import get_logger

logger = get_logger('agents')


@dataclass
class TaskCharacteristics:
    """任务特征"""
    task_type: TaskType
    complexity: int  # 1-5复杂度
    urgency: int     # 1-5紧急度
    quality_requirement: int  # 1-5质量要求
    expected_length: int      # 预期输出长度
    requires_reasoning: bool
    requires_creativity: bool
    requires_precision: bool
    context_length_needed: int


@dataclass
class ModelPerformance:
    """模型性能记录"""
    model_name: str
    task_type: TaskType
    avg_response_time: float
    success_rate: float
    quality_score: float
    user_satisfaction: float
    usage_count: int
    last_updated: float


class IntelligentModelSelector:
    """智能模型选择器"""
    
    def __init__(self, performance_cache_file: str = None):
        """
        初始化智能选择器
        
        Args:
            performance_cache_file: 性能缓存文件路径
        """
        self.cache_file = performance_cache_file or os.path.join(
            os.path.dirname(__file__), "model_performance_cache.json"
        )
        self.performance_history: Dict[str, ModelPerformance] = {}
        self.load_performance_history()
    
    def load_performance_history(self):
        """加载性能历史数据"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for key, value in data.items():
                    self.performance_history[key] = ModelPerformance(**value)
                    
                logger.info(f"✅ 加载了 {len(self.performance_history)} 条性能记录")
            else:
                logger.info("🔄 创建新的性能缓存")
        except Exception as e:
            logger.error(f"❌ 加载性能历史失败: {e}")
    
    def save_performance_history(self):
        """保存性能历史数据"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            data = {}
            for key, performance in self.performance_history.items():
                data[key] = asdict(performance)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.debug(f"💾 保存了 {len(self.performance_history)} 条性能记录")
        except Exception as e:
            logger.error(f"❌ 保存性能历史失败: {e}")
    
    def analyze_task_characteristics(
        self, 
        task_description: str,
        task_type: TaskType = None,
        context_length: int = None
    ) -> TaskCharacteristics:
        """
        分析任务特征
        
        Args:
            task_description: 任务描述
            task_type: 任务类型（如果未指定则自动推断）
            context_length: 上下文长度
            
        Returns:
            任务特征对象
        """
        
        # 自动推断任务类型
        if task_type is None:
            task_type = self._infer_task_type(task_description)
        
        # 分析复杂度
        complexity = self._analyze_complexity(task_description)
        
        # 分析紧急度
        urgency = self._analyze_urgency(task_description)
        
        # 分析质量要求
        quality_requirement = self._analyze_quality_requirement(task_description)
        
        # 分析预期输出长度
        expected_length = self._estimate_output_length(task_description)
        
        # 分析特殊要求
        requires_reasoning = self._requires_reasoning(task_description)
        requires_creativity = self._requires_creativity(task_description)
        requires_precision = self._requires_precision(task_description)
        
        # 估算上下文长度需求
        context_length_needed = context_length or self._estimate_context_length(task_description)
        
        return TaskCharacteristics(
            task_type=task_type,
            complexity=complexity,
            urgency=urgency,
            quality_requirement=quality_requirement,
            expected_length=expected_length,
            requires_reasoning=requires_reasoning,
            requires_creativity=requires_creativity,
            requires_precision=requires_precision,
            context_length_needed=context_length_needed
        )
    
    def _infer_task_type(self, description: str) -> TaskType:
        """推断任务类型"""
        description_lower = description.lower()
        
        # 关键词映射
        keywords = {
            TaskType.CODING: ['代码', '编程', '函数', '算法', 'code', 'function', 'programming', '开发'],
            TaskType.REASONING: ['分析', '推理', '逻辑', '判断', 'analysis', 'reasoning', 'logic'],
            TaskType.THINKING: ['思考', '深入', '复杂', '多角度', 'thinking', 'complex', 'deep'],
            TaskType.FINANCIAL: ['股票', '投资', '财务', '金融', '分析', 'stock', 'investment', 'financial'],
            TaskType.CONVERSATION: ['对话', '聊天', '交流', 'chat', 'conversation', 'discuss'],
            TaskType.SPEED: ['快速', '紧急', '立即', 'quick', 'fast', 'urgent', 'immediate']
        }
        
        scores = {}
        for task_type, words in keywords.items():
            score = sum(1 for word in words if word in description_lower)
            if score > 0:
                scores[task_type] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return TaskType.GENERAL
    
    def _analyze_complexity(self, description: str) -> int:
        """分析任务复杂度 (1-5)"""
        complexity_indicators = {
            5: ['非常复杂', '多步骤', '深入分析', 'very complex', 'multi-step', 'comprehensive'],
            4: ['复杂', '详细', '全面', 'complex', 'detailed', 'thorough'],
            3: ['中等', '标准', 'moderate', 'standard'],
            2: ['简单', '基础', 'simple', 'basic'],
            1: ['非常简单', '快速', 'very simple', 'quick']
        }
        
        description_lower = description.lower()
        for level, indicators in complexity_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                return level
        
        # 根据描述长度推断复杂度
        if len(description) > 500:
            return 4
        elif len(description) > 200:
            return 3
        elif len(description) > 50:
            return 2
        else:
            return 1
    
    def _analyze_urgency(self, description: str) -> int:
        """分析任务紧急度 (1-5)"""
        urgency_indicators = {
            5: ['紧急', '立即', '马上', 'urgent', 'immediate', 'asap'],
            4: ['尽快', '快速', 'quickly', 'fast'],
            3: ['及时', '正常', 'timely', 'normal'],
            2: ['不急', '慢慢', 'no rush'],
            1: ['不紧急', '有时间', 'not urgent']
        }
        
        description_lower = description.lower()
        for level, indicators in urgency_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                return level
        
        return 3  # 默认中等紧急度
    
    def _analyze_quality_requirement(self, description: str) -> int:
        """分析质量要求 (1-5)"""
        quality_indicators = {
            5: ['高质量', '精确', '专业', 'high quality', 'precise', 'professional'],
            4: ['质量好', '准确', 'good quality', 'accurate'],
            3: ['标准', '正常', 'standard', 'normal'],
            2: ['基本', '够用', 'basic', 'sufficient'],
            1: ['简单', '快速', 'simple', 'quick']
        }
        
        description_lower = description.lower()
        for level, indicators in quality_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                return level
        
        return 3  # 默认中等质量要求
    
    def _estimate_output_length(self, description: str) -> int:
        """估算预期输出长度"""
        length_indicators = {
            4000: ['详细报告', '全面分析', 'detailed report', 'comprehensive analysis'],
            2000: ['详细', '完整', 'detailed', 'complete'],
            1000: ['标准', '正常', 'standard', 'normal'],
            500: ['简短', '概要', 'brief', 'summary'],
            200: ['很短', '快速', 'very short', 'quick']
        }
        
        description_lower = description.lower()
        for length, indicators in length_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                return length
        
        # 根据描述长度推断期望输出长度
        return min(2000, max(500, len(description) * 3))
    
    def _requires_reasoning(self, description: str) -> bool:
        """是否需要推理能力"""
        reasoning_keywords = [
            '分析', '推理', '判断', '比较', '评估', 
            'analysis', 'reasoning', 'evaluate', 'compare', 'assess'
        ]
        description_lower = description.lower()
        return any(keyword in description_lower for keyword in reasoning_keywords)
    
    def _requires_creativity(self, description: str) -> bool:
        """是否需要创造力"""
        creativity_keywords = [
            '创意', '创新', '设计', '想象', 
            'creative', 'innovative', 'design', 'imagine'
        ]
        description_lower = description.lower()
        return any(keyword in description_lower for keyword in creativity_keywords)
    
    def _requires_precision(self, description: str) -> bool:
        """是否需要精确性"""
        precision_keywords = [
            '精确', '准确', '具体', '数字', '计算',
            'precise', 'accurate', 'specific', 'calculation'
        ]
        description_lower = description.lower()
        return any(keyword in description_lower for keyword in precision_keywords)
    
    def _estimate_context_length(self, description: str) -> int:
        """估算上下文长度需求"""
        if len(description) > 2000:
            return 16384
        elif len(description) > 1000:
            return 8192
        elif len(description) > 500:
            return 4096
        else:
            return 2048
    
    def select_optimal_model(
        self,
        task_characteristics: TaskCharacteristics,
        exclude_models: List[str] = None,
        consider_history: bool = True
    ) -> Tuple[str, float]:
        """
        选择最优模型
        
        Args:
            task_characteristics: 任务特征
            exclude_models: 排除的模型列表
            consider_history: 是否考虑历史性能
            
        Returns:
            (模型名称, 匹配分数)
        """
        exclude_models = exclude_models or []
        
        model_scores = {}
        
        for model_name, config in MODEL_CONFIGURATIONS.items():
            if model_name in exclude_models:
                continue
            
            score = self._calculate_model_score(config, task_characteristics, consider_history)
            model_scores[model_name] = score
        
        if not model_scores:
            return "qwen-instruct", 0.0  # 默认模型
        
        best_model = max(model_scores, key=model_scores.get)
        best_score = model_scores[best_model]
        
        logger.info(f"🎯 智能选择: {best_model} (分数: {best_score:.2f})")
        return best_model, best_score
    
    def _calculate_model_score(
        self,
        config: ModelCapability,
        characteristics: TaskCharacteristics,
        consider_history: bool
    ) -> float:
        """计算模型适配分数"""
        
        score = 0.0
        
        # 1. 任务类型匹配 (权重: 30%)
        if characteristics.task_type in config.task_strengths:
            score += 30.0
        elif TaskType.GENERAL in config.task_strengths:
            score += 15.0
        
        # 2. 质量vs速度平衡 (权重: 25%)
        if characteristics.urgency >= 4:  # 高紧急度，优先速度
            score += config.speed_score * 2.5
        elif characteristics.quality_requirement >= 4:  # 高质量要求
            score += config.quality_score * 2.5
        else:  # 平衡
            score += (config.quality_score + config.speed_score) * 1.25
        
        # 3. 复杂度匹配 (权重: 20%)
        if characteristics.complexity >= 4 and config.quality_score >= 8.5:
            score += 20.0
        elif characteristics.complexity <= 2 and config.speed_score >= 8.0:
            score += 20.0
        elif characteristics.complexity == 3:
            score += 15.0
        
        # 4. 上下文长度要求 (权重: 10%)
        if characteristics.context_length_needed <= config.context_length:
            score += 10.0
        else:
            score += 5.0  # 部分减分
        
        # 5. 特殊能力要求 (权重: 10%)
        special_score = 0.0
        if characteristics.requires_reasoning and characteristics.task_type == TaskType.REASONING:
            special_score += 3.0
        if characteristics.requires_precision and config.quality_score >= 9.0:
            special_score += 3.0
        if characteristics.requires_creativity and config.model_id.startswith("Qwen"):
            special_score += 2.0
        score += min(10.0, special_score)
        
        # 6. 历史性能 (权重: 5%)
        if consider_history:
            history_key = f"{config.name}_{characteristics.task_type.value}"
            if history_key in self.performance_history:
                perf = self.performance_history[history_key]
                history_score = (perf.success_rate * 2 + perf.quality_score + perf.user_satisfaction) / 4
                score += history_score * 5.0
        
        return score
    
    def record_performance(
        self,
        model_name: str,
        task_type: TaskType,
        response_time: float,
        success: bool,
        quality_score: float = None,
        user_satisfaction: float = None
    ):
        """记录模型性能"""
        
        history_key = f"{model_name}_{task_type.value}"
        
        if history_key in self.performance_history:
            perf = self.performance_history[history_key]
            
            # 更新平均值
            perf.avg_response_time = (perf.avg_response_time * perf.usage_count + response_time) / (perf.usage_count + 1)
            perf.success_rate = (perf.success_rate * perf.usage_count + (1.0 if success else 0.0)) / (perf.usage_count + 1)
            
            if quality_score is not None:
                perf.quality_score = (perf.quality_score * perf.usage_count + quality_score) / (perf.usage_count + 1)
            
            if user_satisfaction is not None:
                perf.user_satisfaction = (perf.user_satisfaction * perf.usage_count + user_satisfaction) / (perf.usage_count + 1)
            
            perf.usage_count += 1
            perf.last_updated = time.time()
        else:
            # 创建新记录
            self.performance_history[history_key] = ModelPerformance(
                model_name=model_name,
                task_type=task_type,
                avg_response_time=response_time,
                success_rate=1.0 if success else 0.0,
                quality_score=quality_score or 5.0,
                user_satisfaction=user_satisfaction or 5.0,
                usage_count=1,
                last_updated=time.time()
            )
        
        # 定期保存
        if len(self.performance_history) % 10 == 0:
            self.save_performance_history()
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        report = {
            "total_records": len(self.performance_history),
            "by_model": {},
            "by_task": {},
            "top_performers": {
                "speed": [],
                "quality": [],
                "reliability": []
            }
        }
        
        # 按模型统计
        model_stats = {}
        task_stats = {}
        
        for key, perf in self.performance_history.items():
            # 按模型
            if perf.model_name not in model_stats:
                model_stats[perf.model_name] = {
                    "usage_count": 0,
                    "avg_response_time": 0.0,
                    "success_rate": 0.0,
                    "quality_score": 0.0
                }
            
            stats = model_stats[perf.model_name]
            stats["usage_count"] += perf.usage_count
            stats["avg_response_time"] = (stats["avg_response_time"] + perf.avg_response_time) / 2
            stats["success_rate"] = (stats["success_rate"] + perf.success_rate) / 2
            stats["quality_score"] = (stats["quality_score"] + perf.quality_score) / 2
            
            # 按任务类型
            task_name = perf.task_type.value
            if task_name not in task_stats:
                task_stats[task_name] = {
                    "usage_count": 0,
                    "best_model": "",
                    "best_score": 0.0
                }
            
            task_stats[task_name]["usage_count"] += perf.usage_count
            combined_score = (perf.success_rate + perf.quality_score + perf.user_satisfaction) / 3
            if combined_score > task_stats[task_name]["best_score"]:
                task_stats[task_name]["best_model"] = perf.model_name
                task_stats[task_name]["best_score"] = combined_score
        
        report["by_model"] = model_stats
        report["by_task"] = task_stats
        
        # 顶级表现者
        all_performances = list(self.performance_history.values())
        
        # 速度最快
        speed_sorted = sorted(all_performances, key=lambda x: x.avg_response_time)
        report["top_performers"]["speed"] = [
            {"model": p.model_name, "task": p.task_type.value, "time": p.avg_response_time}
            for p in speed_sorted[:5]
        ]
        
        # 质量最高
        quality_sorted = sorted(all_performances, key=lambda x: x.quality_score, reverse=True)
        report["top_performers"]["quality"] = [
            {"model": p.model_name, "task": p.task_type.value, "score": p.quality_score}
            for p in quality_sorted[:5]
        ]
        
        # 可靠性最高
        reliability_sorted = sorted(all_performances, key=lambda x: x.success_rate, reverse=True)
        report["top_performers"]["reliability"] = [
            {"model": p.model_name, "task": p.task_type.value, "rate": p.success_rate}
            for p in reliability_sorted[:5]
        ]
        
        return report


# 全局智能选择器实例
_global_selector = None

def get_intelligent_selector() -> IntelligentModelSelector:
    """获取全局智能选择器实例"""
    global _global_selector
    if _global_selector is None:
        _global_selector = IntelligentModelSelector()
    return _global_selector


def smart_select_model(
    task_description: str,
    task_type: TaskType = None,
    priority: str = "balanced",
    context_length: int = None
) -> str:
    """
    智能选择模型的便捷函数
    
    Args:
        task_description: 任务描述
        task_type: 任务类型
        priority: 优先级
        context_length: 上下文长度
        
    Returns:
        最佳模型名称
    """
    
    selector = get_intelligent_selector()
    
    # 分析任务特征
    characteristics = selector.analyze_task_characteristics(
        task_description, task_type, context_length
    )
    
    # 选择最优模型
    model_name, score = selector.select_optimal_model(characteristics)
    
    logger.info(f"🧠 智能选择结果: {model_name} (匹配度: {score:.1f}%)")
    return model_name


def test_intelligent_selector():
    """测试智能选择器"""
    logger.info("🧠 测试智能模型选择器")
    logger.info("=" * 50)
    
    selector = IntelligentModelSelector()
    
    test_cases = [
        ("请帮我写一个Python函数来计算斐波那契数列", None),
        ("我需要对苹果公司的股票进行深入的财务分析", None),
        ("请快速回答：今天天气怎么样？", None),
        ("请详细分析人工智能对未来社会的影响，需要深入思考", None),
        ("帮我debug这段代码的问题", TaskType.CODING),
        ("分析一下比特币价格的走势和投资建议", TaskType.FINANCIAL)
    ]
    
    for task_desc, task_type in test_cases:
        try:
            characteristics = selector.analyze_task_characteristics(task_desc, task_type)
            model_name, score = selector.select_optimal_model(characteristics)
            
            logger.info(f"📝 任务: {task_desc[:50]}...")
            logger.info(f"   类型: {characteristics.task_type.value}")
            logger.info(f"   复杂度: {characteristics.complexity}/5")
            logger.info(f"   选择: {model_name} (分数: {score:.1f})")
            logger.info("")
            
        except Exception as e:
            logger.error(f"❌ 测试失败: {e}")
    
    # 生成性能报告
    report = selector.get_performance_report()
    logger.info(f"📊 性能报告: 共 {report['total_records']} 条记录")


if __name__ == "__main__":
    test_intelligent_selector()