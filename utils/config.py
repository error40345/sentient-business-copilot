import os
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class APIConfig:
    """Configuration for external APIs"""
    fireworks_api_key: str
    serper_api_key: str
    jina_api_key: str
    openrouter_api_key: str

@dataclass
class ModelConfig:
    """Configuration for AI models"""
    dobby_model_name: str
    opendeepsearch_model: str
    default_temperature: float
    max_tokens: int

@dataclass
class AppConfig:
    """Main application configuration"""
    app_name: str
    version: str
    debug_mode: bool
    max_chat_history: int
    auto_save_interval: int

class Config:
    """
    Central configuration management for the Sentient Business Copilot
    Handles environment variables, API keys, and application settings
    """
    
    def __init__(self):
        self.api_config = self._load_api_config()
        self.model_config = self._load_model_config()
        self.app_config = self._load_app_config()
        
        # Validate critical configurations
        self._validate_config()
    
    def _load_api_config(self) -> APIConfig:
        """Load API configuration from environment variables"""
        
        return APIConfig(
            fireworks_api_key=os.getenv("FIREWORKS_API_KEY", ""),
            serper_api_key=os.getenv("SERPER_API_KEY", ""),
            jina_api_key=os.getenv("JINA_API_KEY", ""),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", "")
        )
    
    def _load_model_config(self) -> ModelConfig:
        """Load model configuration"""
        
        return ModelConfig(
            dobby_model_name=os.getenv(
                "DOBBY_MODEL_NAME",
                "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new"
            ),
            opendeepsearch_model=os.getenv(
                "OPENDEEPSEARCH_MODEL",
                "openrouter/google/gemini-2.0-flash-001"
            ),
            default_temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0.6")),
            max_tokens=int(os.getenv("MAX_TOKENS", "2048"))
        )
    
    def _load_app_config(self) -> AppConfig:
        """Load application configuration"""
        
        return AppConfig(
            app_name="Sentient Business Copilot",
            version="1.0.0",
            debug_mode=os.getenv("DEBUG", "false").lower() == "true",
            max_chat_history=int(os.getenv("MAX_CHAT_HISTORY", "100")),
            auto_save_interval=int(os.getenv("AUTO_SAVE_INTERVAL", "30"))  # seconds
        )
    
    def _validate_config(self):
        """Validate critical configuration values"""
        
        warnings = []
        errors = []
        
        # Check API keys (warnings for missing, not errors - fallbacks available)
        if not self.api_config.fireworks_api_key:
            warnings.append("FIREWORKS_API_KEY not set - Dobby-70B will use fallback responses")
        
        if not self.api_config.serper_api_key:
            warnings.append("SERPER_API_KEY not set - OpenDeepSearch will use limited functionality")
        
        if not self.api_config.jina_api_key:
            warnings.append("JINA_API_KEY not set - semantic reranking will be simplified")
        
        # Check model configuration
        if self.model_config.default_temperature < 0 or self.model_config.default_temperature > 2:
            errors.append("DEFAULT_TEMPERATURE must be between 0 and 2")
        
        if self.model_config.max_tokens < 100 or self.model_config.max_tokens > 8192:
            errors.append("MAX_TOKENS must be between 100 and 8192")
        
        # Store validation results
        self._config_warnings = warnings
        self._config_errors = errors
        
        # Log warnings and errors if in debug mode
        if self.app_config.debug_mode:
            if warnings:
                print("Configuration Warnings:")
                for warning in warnings:
                    print(f"  - {warning}")
            
            if errors:
                print("Configuration Errors:")
                for error in errors:
                    print(f"  - {error}")
    
    def get_api_key(self, service: str) -> str:
        """Get API key for a specific service"""
        
        service_mapping = {
            "fireworks": self.api_config.fireworks_api_key,
            "dobby": self.api_config.fireworks_api_key,
            "serper": self.api_config.serper_api_key,
            "opendeepsearch": self.api_config.serper_api_key,
            "jina": self.api_config.jina_api_key,
            "openrouter": self.api_config.openrouter_api_key
        }
        
        return service_mapping.get(service.lower(), "")
    
    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """Get model configuration for a specific model type"""
        
        base_config = {
            "temperature": self.model_config.default_temperature,
            "max_tokens": self.model_config.max_tokens
        }
        
        if model_type == "dobby":
            return {
                **base_config,
                "model_name": self.model_config.dobby_model_name,
                "api_key": self.api_config.fireworks_api_key,
                "base_url": "https://api.fireworks.ai/inference/v1"
            }
        elif model_type == "opendeepsearch":
            return {
                **base_config,
                "model_name": self.model_config.opendeepsearch_model,
                "api_key": self.api_config.openrouter_api_key,
                "search_api_key": self.api_config.serper_api_key,
                "reranker_api_key": self.api_config.jina_api_key
            }
        else:
            return base_config
    
    def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all configured services"""
        
        services = {
            "dobby": {
                "name": "Dobby-70B (Fireworks AI)",
                "configured": bool(self.api_config.fireworks_api_key),
                "model": self.model_config.dobby_model_name,
                "purpose": "Business planning and analysis"
            },
            "opendeepsearch": {
                "name": "OpenDeepSearch",
                "configured": bool(self.api_config.serper_api_key),
                "model": "Semantic search with reranking",
                "purpose": "Market research and data gathering"
            },
            "serper": {
                "name": "Serper API",
                "configured": bool(self.api_config.serper_api_key),
                "model": "Google Search API",
                "purpose": "Web search functionality"
            },
            "jina": {
                "name": "Jina AI Reranker",
                "configured": bool(self.api_config.jina_api_key),
                "model": "Semantic reranking",
                "purpose": "Search result optimization"
            }
        }
        
        return services
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment and configuration information"""
        
        return {
            "app_name": self.app_config.app_name,
            "version": self.app_config.version,
            "debug_mode": self.app_config.debug_mode,
            "python_version": sys.version.split()[0],
            "environment_vars_loaded": len([k for k in os.environ.keys() if k.startswith(("FIREWORKS_", "SERPER_", "JINA_", "OPENROUTER_"))]),
            "config_warnings": len(self._config_warnings),
            "config_errors": len(self._config_errors),
            "services_configured": len([s for s in self.get_service_status().values() if s["configured"]])
        }
    
    def get_config_warnings(self) -> list:
        """Get configuration warnings"""
        return self._config_warnings.copy()
    
    def get_config_errors(self) -> list:
        """Get configuration errors"""
        return self._config_errors.copy()
    
    def is_production_ready(self) -> bool:
        """Check if configuration is ready for production use"""
        
        # At minimum, we need Dobby (Fireworks) for core functionality
        critical_services = [
            self.api_config.fireworks_api_key  # Dobby-70B for business planning
        ]
        
        return all(critical_services) and len(self._config_errors) == 0
    
    def get_fallback_config(self) -> Dict[str, Any]:
        """Get fallback configuration for demo/development mode"""
        
        return {
            "demo_mode": True,
            "fallback_responses": True,
            "limited_functionality": True,
            "message": "Running in demo mode with limited functionality. Configure API keys for full features."
        }
    
    def update_runtime_config(self, **kwargs):
        """Update runtime configuration parameters"""
        
        valid_updates = {}
        
        if "temperature" in kwargs:
            temp = float(kwargs["temperature"])
            if 0 <= temp <= 2:
                self.model_config.default_temperature = temp
                valid_updates["temperature"] = temp
        
        if "max_tokens" in kwargs:
            tokens = int(kwargs["max_tokens"])
            if 100 <= tokens <= 8192:
                self.model_config.max_tokens = tokens
                valid_updates["max_tokens"] = tokens
        
        if "debug_mode" in kwargs:
            self.app_config.debug_mode = bool(kwargs["debug_mode"])
            valid_updates["debug_mode"] = self.app_config.debug_mode
        
        return valid_updates
