package config

import (
    "fmt"
    "os"
    "strconv"
    
    "github.com/joho/godotenv"
)

// Config 应用程序配置
type Config struct {
    Server      ServerConfig
    Database    DatabaseConfig
    VectorStore VectorStoreConfig
    TextSplitter TextSplitterConfig
    Embedding   EmbeddingConfig
    Blockchain  BlockchainConfig
}

// ServerConfig 服务器配置
type ServerConfig struct {
    Port int
    ReadTimeoutSeconds  int
    WriteTimeoutSeconds int
    IdleTimeoutSeconds  int
}

// DatabaseConfig 数据库配置
type DatabaseConfig struct {
    Host     string
    Port     int
    User     string
    Password string
    DBName   string
    SSLMode  string
    ConnString string
    TimeoutSeconds int
}

// VectorStoreConfig 向量存储配置
type VectorStoreConfig struct {
    Host string
    Port int
    Collection string
    TimeoutSeconds int
}

// TextSplitterConfig 文本分割器配置
type TextSplitterConfig struct {
    ChunkSize    int
    ChunkOverlap int
}

// EmbeddingConfig 嵌入服务配置
type EmbeddingConfig struct {
    Model       string
    APIKey      string
    ModelURL    string
    APIToken    string
    BatchSize   int
    Dimensions  int
    ContextSize int
    TimeoutSeconds int
}

// BlockchainConfig 区块链配置
type BlockchainConfig struct {
    ChainID   string
    NodeURL   string
    PrivateKey string
    ContractAddress string
}

// Load 从环境变量加载配置
func Load() (*Config, error) {
    // 尝试加载.env文件
    _ = godotenv.Load()
    
    cfg := &Config{
        Server: ServerConfig{
            Port: getEnvAsInt("SERVER_PORT", 8080),
            ReadTimeoutSeconds: getEnvAsInt("SERVER_READ_TIMEOUT_SECONDS", 60),
            WriteTimeoutSeconds: getEnvAsInt("SERVER_WRITE_TIMEOUT_SECONDS", 60),
            IdleTimeoutSeconds: getEnvAsInt("SERVER_IDLE_TIMEOUT_SECONDS", 120),
        },
        Database: DatabaseConfig{
            Host:     getEnv("DB_HOST", "localhost"),
            Port:     getEnvAsInt("DB_PORT", 5432),
            User:     getEnv("DB_USER", "postgres"),
            Password: getEnv("DB_PASSWORD", "postgres"),
            DBName:   getEnv("DB_NAME", "knowledgebase"),
            SSLMode:  getEnv("DB_SSL_MODE", "disable"),
            TimeoutSeconds: getEnvAsInt("DB_TIMEOUT_SECONDS", 30),
        },
        VectorStore: VectorStoreConfig{
            Host: getEnv("VECTOR_STORE_HOST", "localhost"),
            Port: getEnvAsInt("VECTOR_STORE_PORT", 19530),
            Collection: getEnv("VECTOR_STORE_COLLECTION", "knowledge_base_documents"),
            TimeoutSeconds: getEnvAsInt("VECTOR_STORE_TIMEOUT_SECONDS", 30),
        },
        TextSplitter: TextSplitterConfig{
            ChunkSize:    getEnvAsInt("TEXT_SPLITTER_CHUNK_SIZE", 1000),
            ChunkOverlap: getEnvAsInt("TEXT_SPLITTER_CHUNK_OVERLAP", 200),
        },
        Embedding: EmbeddingConfig{
            Model:          getEnv("EMBEDDING_MODEL", "text-embedding-ada-002"),
            APIKey:         getEnv("OPENAI_API_KEY", ""),
            ModelURL:       getEnv("EMBEDDING_MODEL_URL", "https://api.example.com/embedding"),
            APIToken:       getEnv("EMBEDDING_API_TOKEN", ""),
            BatchSize:      getEnvAsInt("EMBEDDING_BATCH_SIZE", 16),
            Dimensions:     getEnvAsInt("EMBEDDING_DIMENSIONS", 1536),
            ContextSize:    getEnvAsInt("EMBEDDING_CONTEXT_SIZE", 1024),
            TimeoutSeconds: getEnvAsInt("EMBEDDING_TIMEOUT_SECONDS", 30),
        },
        Blockchain: BlockchainConfig{
            ChainID:         getEnv("BLOCKCHAIN_CHAIN_ID", "2035"),
            NodeURL:         getEnv("BLOCKCHAIN_NODE_URL", "http://localhost:8545"),
            PrivateKey:      getEnv("BLOCKCHAIN_PRIVATE_KEY", ""),
            ContractAddress: getEnv("BLOCKCHAIN_CONTRACT_ADDRESS", ""),
        },
    }
    
    // 构造数据库连接字符串
    cfg.Database.ConnString = fmt.Sprintf(
        "host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
        cfg.Database.Host,
        cfg.Database.Port,
        cfg.Database.User,
        cfg.Database.Password,
        cfg.Database.DBName,
        cfg.Database.SSLMode,
    )
    
    return cfg, nil
}

// getEnv 从环境变量获取字符串值，如果不存在则返回默认值
func getEnv(key, defaultValue string) string {
    value := os.Getenv(key)
    if value == "" {
        return defaultValue
    }
    return value
}

// getEnvAsInt 从环境变量获取整数值，如果不存在或无效则返回默认值
func getEnvAsInt(key string, defaultValue int) int {
    valueStr := os.Getenv(key)
    if valueStr == "" {
        return defaultValue
    }
    
    value, err := strconv.Atoi(valueStr)
    if err != nil {
        return defaultValue
    }
    
    return value
}