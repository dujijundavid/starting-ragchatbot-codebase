import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    """Configuration settings for the RAG system"""
    # LLM provider selection
    MODEL_PROVIDER: str = os.getenv("LLM_PROVIDER", "deepseek").lower()
    
    # Provider-specific settings
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    QWEN_MODEL: str = os.getenv("QWEN_MODEL", "qwen-plus")
    QWEN_BASE_URL: str = os.getenv(
        "QWEN_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    
    # Generic OpenAI-compatible overrides
    LLM_API_KEY_OVERRIDE: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL_OVERRIDE: str = os.getenv("LLM_MODEL", "")
    LLM_BASE_URL_OVERRIDE: str = os.getenv("LLM_BASE_URL", "")
    
    # Active LLM configuration (populated post-init)
    LLM_API_KEY: str = field(init=False)
    LLM_MODEL: str = field(init=False)
    LLM_BASE_URL: str = field(init=False)
    
    # Embedding model settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Document processing settings
    CHUNK_SIZE: int = 800       # Size of text chunks for vector storage
    CHUNK_OVERLAP: int = 100     # Characters to overlap between chunks
    MAX_RESULTS: int = 5         # Maximum search results to return
    MAX_HISTORY: int = 2         # Number of conversation messages to remember
    
    # Database paths
    CHROMA_PATH: str = "./chroma_db"  # ChromaDB storage location

    def __post_init__(self):
        provider = self.MODEL_PROVIDER
        if provider == "deepseek":
            api_key = self.DEEPSEEK_API_KEY
            model = self.DEEPSEEK_MODEL
            base_url = self.DEEPSEEK_BASE_URL
        elif provider == "qwen":
            api_key = self.QWEN_API_KEY
            model = self.QWEN_MODEL
            base_url = self.QWEN_BASE_URL
        else:
            api_key = self.LLM_API_KEY_OVERRIDE
            model = self.LLM_MODEL_OVERRIDE or self.DEEPSEEK_MODEL
            base_url = self.LLM_BASE_URL_OVERRIDE or self.DEEPSEEK_BASE_URL
        
        # Apply optional overrides when provided
        if self.LLM_API_KEY_OVERRIDE:
            api_key = self.LLM_API_KEY_OVERRIDE
        if self.LLM_MODEL_OVERRIDE:
            model = self.LLM_MODEL_OVERRIDE
        if self.LLM_BASE_URL_OVERRIDE:
            base_url = self.LLM_BASE_URL_OVERRIDE
        
        self.LLM_API_KEY = api_key
        self.LLM_MODEL = model
        self.LLM_BASE_URL = base_url

config = Config()

