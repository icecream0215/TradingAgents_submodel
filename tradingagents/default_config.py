import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents", "data"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    
    # 多模型LLM设置
    "multi_model_enabled": True,
    "auto_model_selection": True,
    "intelligent_selection": True,
    
    # 传统LLM设置（向后兼容）
    "llm_provider": "multi_model",  # 改为multi_model以启用多模型系统
    "deep_think_llm": "qwen-thinking",  # 深度思考用思维链模型
    "quick_think_llm": "glm-4.5",       # 快速思考用高效模型
    "backend_url": "https://llm.submodel.ai/v1",
    
    # 任务特定模型配置
    "task_models": {
        "coding": "qwen-coder",
        "reasoning": "deepseek-r1", 
        "thinking": "qwen-thinking",
        "conversation": "qwen-instruct",
        "speed": "glm-4.5",
        "quality": "qwen-thinking",
        "general": "qwen-instruct",
        "financial": "deepseek-v31"
    },
    
    # 优先级设置
    "model_priority": "balanced",  # "speed", "quality", "cost", "balanced"
    
    # 备用模型配置
    "enable_fallback": True,
    "fallback_models": {
        "qwen-coder": ["deepseek-v31", "qwen-instruct"],
        "qwen-thinking": ["deepseek-r1", "qwen-instruct"],
        "deepseek-r1": ["qwen-thinking", "qwen-instruct"],
        "glm-4.5": ["qwen-instruct", "gpt-oss"]
    },
    
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    
    # Tool settings
    "online_tools": True,
    
    # Performance tracking
    "performance_tracking": True,
    "cost_tracking": True,

    # Note: Database and cache configuration is now managed by .env file and config.database_manager
    # No database/cache settings in default config to avoid configuration conflicts
}
