"""
多模型配置管理器
支持9个模型的配置管理、动态切换和性能监控
"""

import os
import json
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

from tradingagents.utils.logging_manager import get_logger

logger = get_logger('agents')


class TaskType(Enum):
    """任务类型枚举"""
    CODING = "coding"                   # 代码相关任务
    REASONING = "reasoning"             # 推理分析任务  
    CONVERSATION = "conversation"       # 对话交互任务
    THINKING = "thinking"              # 思维链任务
    SPEED = "speed"                    # 快速响应任务
    QUALITY = "quality"                # 高质量输出任务
    GENERAL = "general"                # 通用任务
    FINANCIAL = "financial"            # 金融分析任务


@dataclass
class ModelCapability:
    """模型能力配置"""
    name: str
    provider: str
    model_id: str
    base_url: str
    api_key_env: str
    context_length: int
    supports_function_calling: bool
    supports_streaming: bool
    avg_response_time: float
    task_strengths: List[TaskType]
    quality_score: float  # 1-10评分
    speed_score: float    # 1-10评分
    cost_score: float     # 1-10评分，10为最便宜
    description: str


# 基础模型配置
MODEL_CONFIGURATIONS = {
    "qwen-instruct": ModelCapability(
        name="Qwen Instruct",
        provider="qwen",
        model_id="qwen-instruct",
        base_url="https://llm.submodel.ai/v1",
        api_key_env="OPENAI_API_KEY",
        context_length=32768,
        supports_function_calling=True,
        supports_streaming=True,
        avg_response_time=2.8,
        task_strengths=[TaskType.CONVERSATION, TaskType.GENERAL, TaskType.FINANCIAL],
        quality_score=9.0,
        speed_score=7.0,
        cost_score=6.0,
        description="通用对话模型"
    ),
    "deepseek-v31": ModelCapability(
        name="DeepSeek V3.1",
        provider="deepseek",
        model_id="deepseek-v31",
        base_url="https://llm.submodel.ai/v1",
        api_key_env="OPENAI_API_KEY",
        context_length=32768,
        supports_function_calling=True,
        supports_streaming=True,
        avg_response_time=2.2,
        task_strengths=[TaskType.CODING, TaskType.FINANCIAL, TaskType.GENERAL],
        quality_score=9.2,
        speed_score=8.0,
        cost_score=7.5,
        description="平衡性能和速度"
    )
}


@dataclass 
class MultiModelSettings:
    """多模型设置"""
    enabled_models: List[str]                    # 启用的模型列表
    default_model: str                          # 默认模型
    auto_selection_enabled: bool                # 是否启用自动选择
    fallback_models: Dict[str, List[str]]       # 备用模型映射
    performance_tracking_enabled: bool         # 是否启用性能跟踪
    cost_tracking_enabled: bool                # 是否启用成本跟踪
    task_model_mapping: Dict[str, str]          # 任务类型到模型的映射
    priority_settings: Dict[str, str]           # 优先级设置


@dataclass
class ModelEndpointConfig:
    """模型端点配置"""
    model_name: str
    model_id: str
    provider: str
    base_url: str
    api_key_env: str
    enabled: bool = True
    custom_headers: Dict[str, str] = None
    timeout: int = 120
    max_retries: int = 3


class MultiModelConfigManager:
    """多模型配置管理器"""
    
    def __init__(self, config_dir: str = None):
        """
        初始化多模型配置管理器
        
        Args:
            config_dir: 配置目录路径
        """
        self.config_dir = Path(config_dir or "config/multi_model")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.settings_file = self.config_dir / "multi_model_settings.json"
        self.endpoints_file = self.config_dir / "model_endpoints.json"
        self.performance_file = self.config_dir / "performance_cache.json"
        
        self.settings: Optional[MultiModelSettings] = None
        self.endpoints: Dict[str, ModelEndpointConfig] = {}
        
        self._load_configurations()
        self._ensure_default_configs()
    
    def _load_configurations(self):
        """加载配置文件"""
        try:
            # 加载设置
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.settings = MultiModelSettings(**data)
            
            # 加载端点配置
            if self.endpoints_file.exists():
                with open(self.endpoints_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.endpoints = {
                        name: ModelEndpointConfig(**config)
                        for name, config in data.items()
                    }
            
            logger.info(f"✅ 多模型配置加载完成")
            
        except Exception as e:
            logger.error(f"❌ 加载多模型配置失败: {e}")
            self._create_default_configs()
    
    def _ensure_default_configs(self):
        """确保默认配置存在"""
        if self.settings is None:
            self._create_default_configs()
        
        if not self.endpoints:
            self._create_default_endpoints()
    
    def _create_default_configs(self):
        """创建默认配置"""
        self.settings = MultiModelSettings(
            enabled_models=list(MODEL_CONFIGURATIONS.keys()),
            default_model="qwen-instruct",
            auto_selection_enabled=True,
            fallback_models={
                "qwen-coder": ["deepseek-v31", "qwen-instruct"],
                "qwen-instruct": ["gpt-oss", "glm-4.5"],
                "glm-4.5": ["qwen-instruct", "gpt-oss"],
                "gpt-oss": ["qwen-instruct", "deepseek-v31"],
                "deepseek-r1": ["qwen-thinking", "qwen-instruct"],
                "qwen-thinking": ["deepseek-r1", "qwen-instruct"],
                "deepseek-v31": ["qwen-instruct", "gpt-oss"]
            },
            performance_tracking_enabled=True,
            cost_tracking_enabled=True,
            task_model_mapping={
                TaskType.CODING.value: "qwen-coder",
                TaskType.REASONING.value: "deepseek-r1",
                TaskType.THINKING.value: "qwen-thinking",
                TaskType.CONVERSATION.value: "qwen-instruct",
                TaskType.SPEED.value: "glm-4.5",
                TaskType.QUALITY.value: "qwen-thinking",
                TaskType.GENERAL.value: "qwen-instruct",
                TaskType.FINANCIAL.value: "deepseek-v31"
            },
            priority_settings={
                "development": "quality",
                "production": "balanced",
                "testing": "speed"
            }
        )
        
        self._save_settings()
    
    def _create_default_endpoints(self):
        """创建默认端点配置"""
        for model_name, config in MODEL_CONFIGURATIONS.items():
            self.endpoints[model_name] = ModelEndpointConfig(
                model_name=model_name,
                model_id=config.model_id,
                provider=config.provider,
                base_url=config.base_url,
                api_key_env=config.api_key_env,
                enabled=True,
                timeout=120,
                max_retries=3
            )
        
        self._save_endpoints()
    
    def _save_settings(self):
        """保存设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 保存多模型设置失败: {e}")
    
    def _save_endpoints(self):
        """保存端点配置"""
        try:
            data = {
                name: asdict(config) for name, config in self.endpoints.items()
            }
            with open(self.endpoints_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 保存端点配置失败: {e}")
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return [
            model_name for model_name, config in self.endpoints.items()
            if config.enabled and model_name in self.settings.enabled_models
        ]
    
    def get_model_for_task(
        self,
        task_type: TaskType,
        use_intelligent_selection: bool = None,
        priority: str = None
    ) -> str:
        """
        获取任务的最佳模型
        
        Args:
            task_type: 任务类型
            use_intelligent_selection: 是否使用智能选择
            priority: 优先级设置
            
        Returns:
            模型名称
        """
        
        # 预设映射选择
        mapped_model = self.settings.task_model_mapping.get(task_type.value)
        if mapped_model and mapped_model in self.get_available_models():
            return mapped_model
        
        # 默认模型
        if self.settings.default_model in self.get_available_models():
            return self.settings.default_model
        
        # 兜底：第一个可用模型
        available = self.get_available_models()
        if available:
            return available[0]
        
        raise ValueError("没有可用的模型")
    
    def get_fallback_models(self, primary_model: str) -> List[str]:
        """获取备用模型列表"""
        fallbacks = self.settings.fallback_models.get(primary_model, [])
        available_models = self.get_available_models()
        
        return [model for model in fallbacks if model in available_models]
    
    def create_model_adapter(
        self,
        model_name: str = None,
        task_type: TaskType = TaskType.GENERAL,
        **kwargs
    ):
        """
        创建模型适配器
        
        Args:
            model_name: 模型名称，如果不提供则自动选择
            task_type: 任务类型
            **kwargs: 其他参数
            
        Returns:
            模型适配器实例
        """
        
        # 自动选择模型
        if model_name is None:
            model_name = self.get_model_for_task(task_type)
        
        # 检查模型是否可用
        if model_name not in self.get_available_models():
            raise ValueError(f"模型 {model_name} 不可用")
        
        # 获取端点配置
        endpoint_config = self.endpoints[model_name]
        
        # 检查API密钥
        api_key = os.getenv(endpoint_config.api_key_env)
        if not api_key:
            raise ValueError(
                f"模型 {model_name} 的API密钥未找到。"
                f"请设置环境变量 {endpoint_config.api_key_env}"
            )
        
        # 创建适配器
        from langchain_openai import ChatOpenAI
        
        adapter = ChatOpenAI(
            model=endpoint_config.model_id,
            api_key=api_key,
            base_url=endpoint_config.base_url,
            temperature=kwargs.get('temperature', 0.1),
            max_tokens=kwargs.get('max_tokens', 2000),
            timeout=endpoint_config.timeout,
            max_retries=endpoint_config.max_retries
        )
        
        logger.info(f"✅ 创建模型适配器: {model_name}")
        return adapter
    
    def enable_model(self, model_name: str):
        """启用模型"""
        if model_name in MODEL_CONFIGURATIONS:
            if model_name not in self.settings.enabled_models:
                self.settings.enabled_models.append(model_name)
            
            if model_name in self.endpoints:
                self.endpoints[model_name].enabled = True
            
            self._save_settings()
            self._save_endpoints()
            logger.info(f"✅ 启用模型: {model_name}")
        else:
            raise ValueError(f"未知模型: {model_name}")
    
    def disable_model(self, model_name: str):
        """禁用模型"""
        if model_name in self.settings.enabled_models:
            self.settings.enabled_models.remove(model_name)
        
        if model_name in self.endpoints:
            self.endpoints[model_name].enabled = False
        
        self._save_settings()
        self._save_endpoints()
        logger.info(f"❌ 禁用模型: {model_name}")
    
    def set_task_model_mapping(self, task_type: TaskType, model_name: str):
        """设置任务类型到模型的映射"""
        if model_name not in MODEL_CONFIGURATIONS:
            raise ValueError(f"未知模型: {model_name}")
        
        self.settings.task_model_mapping[task_type.value] = model_name
        self._save_settings()
        logger.info(f"✅ 设置任务映射: {task_type.value} -> {model_name}")
    
    def update_endpoint_config(
        self,
        model_name: str,
        base_url: str = None,
        api_key_env: str = None,
        timeout: int = None,
        max_retries: int = None
    ):
        """更新端点配置"""
        if model_name not in self.endpoints:
            raise ValueError(f"未知模型端点: {model_name}")
        
        config = self.endpoints[model_name]
        
        if base_url is not None:
            config.base_url = base_url
        if api_key_env is not None:
            config.api_key_env = api_key_env
        if timeout is not None:
            config.timeout = timeout
        if max_retries is not None:
            config.max_retries = max_retries
        
        self._save_endpoints()
        logger.info(f"✅ 更新端点配置: {model_name}")
    
    def get_model_status(self) -> Dict[str, Any]:
        """获取模型状态"""
        status = {
            "total_models": len(MODEL_CONFIGURATIONS),
            "enabled_models": len(self.get_available_models()),
            "models": {}
        }
        
        for model_name, config in MODEL_CONFIGURATIONS.items():
            endpoint_config = self.endpoints.get(model_name)
            
            # 检查API密钥
            api_key_available = bool(os.getenv(config.api_key_env)) if endpoint_config else False
            
            status["models"][model_name] = {
                "name": config.name,
                "provider": config.provider,
                "enabled": model_name in self.settings.enabled_models,
                "api_key_available": api_key_available,
                "task_strengths": [t.value for t in config.task_strengths],
                "quality_score": config.quality_score,
                "speed_score": config.speed_score,
                "avg_response_time": config.avg_response_time
            }
        
        return status
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        return {"message": "性能跟踪功能已移除"}
    
    def record_model_performance(
        self,
        model_name: str,
        task_type: TaskType,
        response_time: float,
        success: bool,
        quality_score: float = None,
        user_satisfaction: float = None
    ):
        """记录模型性能"""
        # 性能记录功能已移除
        pass
    
    def export_config(self) -> Dict[str, Any]:
        """导出配置"""
        return {
            "settings": asdict(self.settings),
            "endpoints": {name: asdict(config) for name, config in self.endpoints.items()},
            "model_configurations": {
                name: {
                    "name": config.name,
                    "description": config.description,
                    "provider": config.provider,
                    "task_strengths": [t.value for t in config.task_strengths],
                    "quality_score": config.quality_score,
                    "speed_score": config.speed_score,
                    "cost_score": config.cost_score
                }
                for name, config in MODEL_CONFIGURATIONS.items()
            }
        }
    
    def import_config(self, config_data: Dict[str, Any]):
        """导入配置"""
        try:
            if "settings" in config_data:
                self.settings = MultiModelSettings(**config_data["settings"])
                self._save_settings()
            
            if "endpoints" in config_data:
                self.endpoints = {
                    name: ModelEndpointConfig(**config)
                    for name, config in config_data["endpoints"].items()
                }
                self._save_endpoints()
            
            logger.info("✅ 配置导入成功")
            
        except Exception as e:
            logger.error(f"❌ 配置导入失败: {e}")
            raise
    
    def test_all_models(self) -> Dict[str, Dict[str, Any]]:
        """测试所有可用模型"""
        results = {}
        available_models = self.get_available_models()
        
        for model_name in available_models:
            try:
                start_time = time.time()
                
                # 创建适配器
                adapter = self.create_model_adapter(model_name)
                
                # 简单测试
                from langchain_core.messages import HumanMessage
                messages = [HumanMessage(content="请简单回答：你好")]
                
                result = adapter._generate(messages)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                results[model_name] = {
                    "status": "success",
                    "response_time": response_time,
                    "model_info": adapter.get_model_info(),
                    "error": None
                }
                
                logger.info(f"✅ 模型测试成功: {model_name} ({response_time:.2f}s)")
                
            except Exception as e:
                results[model_name] = {
                    "status": "failed",
                    "response_time": None,
                    "model_info": None,
                    "error": str(e)
                }
                
                logger.error(f"❌ 模型测试失败: {model_name} - {e}")
        
        return results


# 全局多模型配置管理器实例
_global_multi_config = None

def get_multi_model_config() -> MultiModelConfigManager:
    """获取全局多模型配置管理器实例"""
    global _global_multi_config
    if _global_multi_config is None:
        _global_multi_config = MultiModelConfigManager()
    return _global_multi_config


def create_smart_llm(
    task_description: str = None,
    task_type: TaskType = TaskType.GENERAL,
    priority: str = "balanced",
    **kwargs
):
    """
    智能创建LLM适配器的便捷函数
    
    Args:
        task_description: 任务描述（用于智能选择）
        task_type: 任务类型
        priority: 优先级
        **kwargs: 其他参数
        
    Returns:
        LLM适配器实例
    """
    
    config_manager = get_multi_model_config()
    
    # 根据任务类型选择
    return config_manager.create_model_adapter(None, task_type, **kwargs)


def test_multi_model_config():
    """测试多模型配置系统"""
    logger.info("🧪 测试多模型配置系统")
    logger.info("=" * 50)
    
    config_manager = get_multi_model_config()
    
    # 获取模型状态
    status = config_manager.get_model_status()
    logger.info(f"📊 总模型数: {status['total_models']}")
    logger.info(f"📊 可用模型数: {status['enabled_models']}")
    
    # 测试任务模型选择
    test_cases = [
        (TaskType.CODING, "写一个Python排序算法"),
        (TaskType.FINANCIAL, "分析苹果公司的股票"),
        (TaskType.SPEED, "快速回答当前时间"),
        (TaskType.THINKING, "深度分析人工智能的未来发展")
    ]
    
    for task_type, description in test_cases:
        try:
            model_name = config_manager.get_model_for_task(task_type)
            logger.info(f"✅ {task_type.value}: {model_name}")
            
        except Exception as e:
            logger.error(f"❌ {task_type.value}: {e}")


if __name__ == "__main__":
    test_multi_model_config()