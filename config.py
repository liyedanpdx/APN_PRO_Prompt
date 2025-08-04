import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    """
    配置管理类，从环境变量和.env文件中读取配置
    """
    
    def __init__(self):
        self._load_config()
    
    def _load_config(self):
        """加载配置参数"""
        # OpenAI配置
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.OPENAI_DEFAULT_MODEL = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4-1106-preview")
        self.OPENAI_DEFAULT_TEMPERATURE = float(os.getenv("OPENAI_DEFAULT_TEMPERATURE", "0.7"))
        self.OPENAI_DEFAULT_MAX_TOKENS = self._get_int_env("OPENAI_DEFAULT_MAX_TOKENS", None)
        
        # Perplexity配置
        self.PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
        self.PERPLEXITY_BASE_URL = os.getenv("PERPLEXITY_BASE_URL", "https://api.perplexity.ai")
        self.PERPLEXITY_DEFAULT_MODEL = os.getenv("PERPLEXITY_DEFAULT_MODEL", "llama-3.1-sonar-small-128k-online")
        self.PERPLEXITY_DEFAULT_TEMPERATURE = float(os.getenv("PERPLEXITY_DEFAULT_TEMPERATURE", "0.2"))
        self.PERPLEXITY_DEFAULT_MAX_TOKENS = self._get_int_env("PERPLEXITY_DEFAULT_MAX_TOKENS", None)
        
        # Groq配置
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        self.GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        self.GROQ_DEFAULT_MODEL = os.getenv("GROQ_DEFAULT_MODEL", "llama-3.1-70b-versatile")
        self.GROQ_DEFAULT_TEMPERATURE = float(os.getenv("GROQ_DEFAULT_TEMPERATURE", "0.2"))
        self.GROQ_DEFAULT_MAX_TOKENS = self._get_int_env("GROQ_DEFAULT_MAX_TOKENS", None)
        
        # Ali（阿里云）配置
        self.ALI_API_KEY = os.getenv("ALI_API_KEY", "")
        self.ALI_API_BASE = os.getenv("ALI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.ALI_DEFAULT_MODEL = os.getenv("ALI_DEFAULT_MODEL", "deepseek-v3")
        self.ALI_DEFAULT_TEMPERATURE = float(os.getenv("ALI_DEFAULT_TEMPERATURE", "0.2"))
        self.ALI_DEFAULT_MAX_TOKENS = self._get_int_env("ALI_DEFAULT_MAX_TOKENS", None)
        
        # Gemini配置
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.GEMINI_API_BASE = os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta/openai")
        self.GEMINI_DEFAULT_MODEL = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.5-flash-lite")
        self.GEMINI_DEFAULT_TEMPERATURE = float(os.getenv("GEMINI_DEFAULT_TEMPERATURE", "0.2"))
        self.GEMINI_DEFAULT_MAX_TOKENS = self._get_int_env("GEMINI_DEFAULT_MAX_TOKENS", None)
        
        # 通用配置
        self.DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai")
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
        self.RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))
        
        # 日志配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "llm_client.log")
        
        # 项目配置
        self.PROJECT_NAME = os.getenv("PROJECT_NAME", "APN Pro AI")
        self.VERSION = os.getenv("VERSION", "1.0.0")
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    def _get_int_env(self, key: str, default: Optional[int]) -> Optional[int]:
        """安全地获取整数环境变量"""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default
    
    def validate_config(self) -> tuple[bool, list[str]]:
        """
        验证配置的有效性
        
        Returns:
            tuple: (是否有效, 错误消息列表)
        """
        errors = []
        
        # 检查API密钥（仅在使用时验证，不强制要求所有密钥）
        # OpenAI密钥验证
        if self.OPENAI_API_KEY and not self.OPENAI_API_KEY.startswith("sk-"):
            errors.append("OPENAI_API_KEY format appears invalid (should start with 'sk-')")
            
        # Perplexity密钥验证  
        if self.PERPLEXITY_API_KEY and not self.PERPLEXITY_API_KEY.startswith("pplx-"):
            errors.append("PERPLEXITY_API_KEY format appears invalid (should start with 'pplx-')")
            
        # Groq密钥验证
        if self.GROQ_API_KEY and not self.GROQ_API_KEY.startswith("gsk_"):
            errors.append("GROQ_API_KEY format appears invalid (should start with 'gsk_')")
            
        # Ali密钥验证
        if self.ALI_API_KEY and not self.ALI_API_KEY.startswith("sk-"):
            errors.append("ALI_API_KEY format appears invalid (should start with 'sk-')")
            
        # Gemini密钥验证
        if self.GEMINI_API_KEY and not self.GEMINI_API_KEY.startswith("AIza"):
            errors.append("GEMINI_API_KEY format appears invalid (should start with 'AIza')")
        
        # 检查温度参数范围
        if not (0 <= self.OPENAI_DEFAULT_TEMPERATURE <= 2):
            errors.append("OPENAI_DEFAULT_TEMPERATURE must be between 0 and 2")
            
        if not (0 <= self.PERPLEXITY_DEFAULT_TEMPERATURE <= 2):
            errors.append("PERPLEXITY_DEFAULT_TEMPERATURE must be between 0 and 2")
            
        if not (0 <= self.GROQ_DEFAULT_TEMPERATURE <= 2):
            errors.append("GROQ_DEFAULT_TEMPERATURE must be between 0 and 2")
            
        if not (0 <= self.ALI_DEFAULT_TEMPERATURE <= 2):
            errors.append("ALI_DEFAULT_TEMPERATURE must be between 0 and 2")
            
        if not (0 <= self.GEMINI_DEFAULT_TEMPERATURE <= 2):
            errors.append("GEMINI_DEFAULT_TEMPERATURE must be between 0 and 2")
        
        # 检查提供商
        if self.DEFAULT_PROVIDER not in ["openai", "perplexity", "groq", "ali", "gemini"]:
            errors.append("DEFAULT_PROVIDER must be 'openai', 'perplexity', 'groq', 'ali', or 'gemini'")
        
        return len(errors) == 0, errors
    
    def get_openai_config(self) -> dict:
        """获取OpenAI相关配置"""
        return {
            "api_key": self.OPENAI_API_KEY,
            "base_url": self.OPENAI_BASE_URL,
            "default_model": self.OPENAI_DEFAULT_MODEL,
            "default_temperature": self.OPENAI_DEFAULT_TEMPERATURE,
            "default_max_tokens": self.OPENAI_DEFAULT_MAX_TOKENS,
        }
    
    def get_perplexity_config(self) -> dict:
        """获取Perplexity相关配置"""
        return {
            "api_key": self.PERPLEXITY_API_KEY,
            "base_url": self.PERPLEXITY_BASE_URL,
            "default_model": self.PERPLEXITY_DEFAULT_MODEL,
            "default_temperature": self.PERPLEXITY_DEFAULT_TEMPERATURE,
            "default_max_tokens": self.PERPLEXITY_DEFAULT_MAX_TOKENS,
        }
    
    def get_groq_config(self) -> dict:
        """获取Groq相关配置"""
        return {
            "api_key": self.GROQ_API_KEY,
            "base_url": self.GROQ_BASE_URL,
            "default_model": self.GROQ_DEFAULT_MODEL,
            "default_temperature": self.GROQ_DEFAULT_TEMPERATURE,
            "default_max_tokens": self.GROQ_DEFAULT_MAX_TOKENS,
        }
    
    def get_ali_config(self) -> dict:
        """获取Ali（阿里云）相关配置"""
        return {
            "api_key": self.ALI_API_KEY,
            "api_base": self.ALI_API_BASE,
            "default_model": self.ALI_DEFAULT_MODEL,
            "default_temperature": self.ALI_DEFAULT_TEMPERATURE,
            "default_max_tokens": self.ALI_DEFAULT_MAX_TOKENS,
        }
    
    def get_gemini_config(self) -> dict:
        """获取Gemini相关配置"""
        return {
            "api_key": self.GEMINI_API_KEY,
            "api_base": self.GEMINI_API_BASE,
            "default_model": self.GEMINI_DEFAULT_MODEL,
            "default_temperature": self.GEMINI_DEFAULT_TEMPERATURE,
            "default_max_tokens": self.GEMINI_DEFAULT_MAX_TOKENS,
        }
    
    def __repr__(self) -> str:
        """配置的字符串表示（隐藏敏感信息）"""
        return f"""Config(
    OPENAI_API_KEY={'*' * 10 + self.OPENAI_API_KEY[-4:] if self.OPENAI_API_KEY else 'Not Set'},
    PERPLEXITY_API_KEY={'*' * 10 + self.PERPLEXITY_API_KEY[-4:] if self.PERPLEXITY_API_KEY else 'Not Set'},
    GROQ_API_KEY={'*' * 10 + self.GROQ_API_KEY[-4:] if self.GROQ_API_KEY else 'Not Set'},
    ALI_API_KEY={'*' * 10 + self.ALI_API_KEY[-4:] if self.ALI_API_KEY else 'Not Set'},
    GEMINI_API_KEY={'*' * 10 + self.GEMINI_API_KEY[-4:] if self.GEMINI_API_KEY else 'Not Set'},
    DEFAULT_PROVIDER={self.DEFAULT_PROVIDER},
    OPENAI_DEFAULT_MODEL={self.OPENAI_DEFAULT_MODEL},
    PERPLEXITY_DEFAULT_MODEL={self.PERPLEXITY_DEFAULT_MODEL},
    GROQ_DEFAULT_MODEL={self.GROQ_DEFAULT_MODEL},
    ALI_DEFAULT_MODEL={self.ALI_DEFAULT_MODEL},
    GEMINI_DEFAULT_MODEL={self.GEMINI_DEFAULT_MODEL},
    DEBUG={self.DEBUG}
)"""


# 全局配置实例
config = Config()

# 配置验证
is_valid, validation_errors = config.validate_config()
if not is_valid:
    print("Configuration validation failed:")
    for error in validation_errors:
        print(f"  - {error}")
    print("\nPlease check your .env file or environment variables.")


if __name__ == "__main__":
    print("Configuration Status:")
    print(config)
    print(f"\nValidation: {'✓ Valid' if is_valid else '✗ Invalid'}")
    if validation_errors:
        print("Errors:")
        for error in validation_errors:
            print(f"  - {error}")