package config

import (
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/joho/godotenv"
	"github.com/spf13/viper"
)

// Config 存储所有配置信息
type Config struct {
	App            AppConfig
	Server         ServerConfig
	Database       DatabaseConfig
	Redis          RedisConfig
	Vector         VectorConfig
	Knowledge      KnowledgeConfig
	Security       SecurityConfig
	WebSearch      WebSearchConfig
	Embedding      EmbeddingConfig
	Rag            RagConfig
	Reranker       RerankerConfig
	Llm            LlmConfig
	Cache          CacheConfig
	RateLimit      RateLimitConfig
}

// AppConfig 应用基本配置
type AppConfig struct {
	Name        string
	Environment string
	Debug       bool
	LogLevel    string
	DataDir     string
	LogsDir     string
	ConfigDir   string
	ModelsDir   string
}

// ServerConfig 服务器配置
type ServerConfig struct {
	Host           string
	Port           int
	ApiPrefix      string
	ReadTimeout    time.Duration
	WriteTimeout   time.Duration
	IdleTimeout    time.Duration
	MaxHeaderBytes int
	Workers        int
	Threads        int
	RequestTimeout int
	MaxRequestSize int
}

// DatabaseConfig 数据库配置
type DatabaseConfig struct {
	MongoDB struct {
		URI        string
		Database   string
		Collection string
	}
}

// RedisConfig Redis配置
type RedisConfig struct {
	URL string
	TTL int
}

// VectorConfig 向量存储配置
type VectorConfig struct {
	DbType      string
	Path        string
	Collection  string
	Dimension   int
	Qdrant      QdrantConfig
	Milvus      MilvusConfig
}

// QdrantConfig Qdrant配置
type QdrantConfig struct {
	URL          string
	Port         int
	CollectionName string
}

// MilvusConfig Milvus配置
type MilvusConfig struct {
	URI           string
	CollectionName string
}

// KnowledgeConfig 知识图谱配置
type KnowledgeConfig struct {
	GraphStore string
	Neo4j struct {
		URI      string
		Username string
		Password string
	}
}

// SecurityConfig 安全配置
type SecurityConfig struct {
	JwtSecret    string
	JwtAlgorithm string
	JwtExpiry    int
	Cors         CorsConfig
}

// CorsConfig CORS配置
type CorsConfig struct {
	AllowOrigins []string
}

// WebSearchConfig Web搜索配置
type WebSearchConfig struct {
	ApiKeys struct {
		Brave  string
		Google string
	}
	Search struct {
		DefaultEngine string
		MaxResults    int
		Timeout       int
	}
	Content struct {
		SummarizationEnabled bool
		MaxSummaryLength     int
		TranslationEnabled   bool
		TargetLanguage       string
		FilteringEnabled     bool
		BlockedDomains       []string
	}
	Knowledge struct {
		KnowledgeBaseURL   string
		KnowledgeGraphURL  string
		ApiKey             string
		Timeout            int
	}
}

// EmbeddingConfig 嵌入模型配置
type EmbeddingConfig struct {
	EnableLocalModels bool
	ModelCacheDir     string
	Model             string
	MaxLength         int
	Device            string
}

// RagConfig RAG配置
type RagConfig struct {
	TopK                int
	SimilarityThreshold float64
}

// RerankerConfig 重排序配置
type RerankerConfig struct {
	Enabled   bool
	Type      string
	Model     string
	TopN      int
}

// LlmConfig LLM配置
type LlmConfig struct {
	Provider   string
	ApiKey     string
	ApiBase    string
	ModelName  string
	MaxTokens  int
	Temperature float64
}

// CacheConfig 缓存配置
type CacheConfig struct {
	Enabled    bool
	TTL        int
	MaxEntries int
}

// RateLimitConfig 限流配置
type RateLimitConfig struct {
	Enabled bool
	Limit   int
	Period  int
}

// 默认配置值
const (
	DefaultServerPort = 8000
	DefaultWorkers    = 2
	DefaultThreads    = 4
	DefaultCacheTTL   = 3600
	DefaultTopK       = 5
)

// LoadConfig 加载配置
func LoadConfig() (*Config, error) {
	// 尝试加载.env文件
	_ = godotenv.Load()

	// 初始化默认配置
	cfg := DefaultConfig()

	// 加载配置文件
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(".")
	viper.AddConfigPath("./config")
	viper.AddConfigPath("/app/config")

	if err := viper.ReadInConfig(); err != nil {
		// 配置文件不存在时，只使用环境变量
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, fmt.Errorf("读取配置文件错误: %w", err)
		}
	}

	// 从环境变量覆盖配置
	LoadFromEnv(cfg)

	return cfg, nil
}

// DefaultConfig 返回默认配置
func DefaultConfig() *Config {
	return &Config{
		App: AppConfig{
			Name:        "索克生活RAG服务",
			Environment: "production",
			Debug:       false,
			LogLevel:    "info",
			DataDir:     "/app/data",
			LogsDir:     "/app/logs",
			ConfigDir:   "/app/config",
			ModelsDir:   "/app/models",
		},
		Server: ServerConfig{
			Host:           "0.0.0.0",
			Port:           DefaultServerPort,
			ApiPrefix:      "/api",
			ReadTimeout:    30 * time.Second,
			WriteTimeout:   30 * time.Second,
			IdleTimeout:    60 * time.Second,
			MaxHeaderBytes: 1 << 20, // 1 MB
			Workers:        DefaultWorkers,
			Threads:        DefaultThreads,
			RequestTimeout: 30,
			MaxRequestSize: 50, // MB
		},
		Redis: RedisConfig{
			URL: "redis://redis:6379/0",
			TTL: 3600,
		},
		Database: DatabaseConfig{
			MongoDB: struct {
				URI        string
				Database   string
				Collection string
			}{
				URI:        "mongodb://mongodb:27017/",
				Database:   "suoke_life",
				Collection: "rag_data",
			},
		},
		Vector: VectorConfig{
			DbType:     "chroma",
			Path:       "/app/data/vectors",
			Collection: "suoke_vectors",
			Dimension:  768,
			Qdrant: QdrantConfig{
				URL:            "http://qdrant:6333",
				Port:           0,
				CollectionName: "suoke_vectors",
			},
			Milvus: MilvusConfig{
				URI:            "http://milvus:19530",
				CollectionName: "suoke_vectors",
			},
		},
		Knowledge: KnowledgeConfig{
			GraphStore: "neo4j",
			Neo4j: struct {
				URI      string
				Username string
				Password string
			}{
				URI:      "bolt://neo4j:7687",
				Username: "neo4j",
				Password: "password",
			},
		},
		Security: SecurityConfig{
			JwtSecret:    "default_secret_key_change_in_production",
			JwtAlgorithm: "HS256",
			JwtExpiry:    86400,
			Cors: CorsConfig{
				AllowOrigins: []string{"*"},
			},
		},
		WebSearch: WebSearchConfig{
			ApiKeys: struct {
				Brave  string
				Google string
			}{
				Brave:  "",
				Google: "",
			},
			Search: struct {
				DefaultEngine string
				MaxResults    int
				Timeout       int
			}{
				DefaultEngine: "brave",
				MaxResults:    5,
				Timeout:       30,
			},
			Content: struct {
				SummarizationEnabled bool
				MaxSummaryLength     int
				TranslationEnabled   bool
				TargetLanguage       string
				FilteringEnabled     bool
				BlockedDomains       []string
			}{
				SummarizationEnabled: true,
				MaxSummaryLength:     200,
				TranslationEnabled:   false,
				TargetLanguage:       "zh",
				FilteringEnabled:     true,
				BlockedDomains:       []string{"spam.com", "ads.example.com"},
			},
			Knowledge: struct {
				KnowledgeBaseURL  string
				KnowledgeGraphURL string
				ApiKey            string
				Timeout           int
			}{
				KnowledgeBaseURL:  "http://localhost:8000/api",
				KnowledgeGraphURL: "http://localhost:8000/api",
				ApiKey:            "",
				Timeout:           5,
			},
		},
		Embedding: EmbeddingConfig{
			EnableLocalModels: true,
			ModelCacheDir:     "/app/models/cache",
			Model:             "BAAI/bge-small-zh",
			MaxLength:         512,
			Device:            "cpu",
		},
		Rag: RagConfig{
			TopK:                5,
			SimilarityThreshold: 0.7,
		},
		Reranker: RerankerConfig{
			Enabled: true,
			Type:    "bge",
			Model:   "BAAI/bge-reranker-base",
			TopN:    10,
		},
		Llm: LlmConfig{
			Provider:    "openai",
			ApiKey:      "",
			ApiBase:     "",
			ModelName:   "gpt-3.5-turbo",
			MaxTokens:   4096,
			Temperature: 0.7,
		},
		Cache: CacheConfig{
			Enabled:    true,
			TTL:        3600,
			MaxEntries: 1000,
		},
		RateLimit: RateLimitConfig{
			Enabled: true,
			Limit:   60,
			Period:  60,
		},
	}
}

// LoadFromEnv 从环境变量加载配置
func LoadFromEnv(cfg *Config) {
	// App配置
	if val := os.Getenv("RAG_ENV"); val != "" {
		cfg.App.Environment = val
	}
	if val := os.Getenv("RAG_DEBUG"); val != "" {
		cfg.App.Debug = strings.ToLower(val) == "true"
	}
	if val := os.Getenv("RAG_LOG_LEVEL"); val != "" {
		cfg.App.LogLevel = val
	}

	// 服务器配置
	if val := os.Getenv("RAG_HOST"); val != "" {
		cfg.Server.Host = val
	}
	if val := os.Getenv("RAG_PORT"); val != "" {
		if port, err := strconv.Atoi(val); err == nil {
			cfg.Server.Port = port
		}
	}
	if val := os.Getenv("RAG_WORKERS"); val != "" {
		if workers, err := strconv.Atoi(val); err == nil {
			cfg.Server.Workers = workers
		}
	}
	if val := os.Getenv("RAG_THREADS"); val != "" {
		if threads, err := strconv.Atoi(val); err == nil {
			cfg.Server.Threads = threads
		}
	}

	// Redis配置
	if val := os.Getenv("RAG_REDIS_URL"); val != "" {
		cfg.Redis.URL = val
	}
	if val := os.Getenv("RAG_REDIS_TTL"); val != "" {
		if ttl, err := strconv.Atoi(val); err == nil {
			cfg.Redis.TTL = ttl
		}
	}

	// MongoDB配置
	if val := os.Getenv("RAG_MONGODB_URI"); val != "" {
		cfg.Database.MongoDB.URI = val
	}
	if val := os.Getenv("RAG_MONGODB_DB"); val != "" {
		cfg.Database.MongoDB.Database = val
	}
	if val := os.Getenv("RAG_MONGODB_COLLECTION"); val != "" {
		cfg.Database.MongoDB.Collection = val
	}

	// 向量数据库配置
	if val := os.Getenv("RAG_VECTOR_DB_TYPE"); val != "" {
		cfg.Vector.DbType = val
	}
	if val := os.Getenv("RAG_VECTOR_DB_PATH"); val != "" {
		cfg.Vector.Path = val
	}
	if val := os.Getenv("RAG_VECTOR_DB_COLLECTION"); val != "" {
		cfg.Vector.Collection = val
	}
	if val := os.Getenv("RAG_VECTOR_DIMENSION"); val != "" {
		if dim, err := strconv.Atoi(val); err == nil {
			cfg.Vector.Dimension = dim
		}
	}

	// Qdrant配置
	if val := os.Getenv("QDRANT_URL"); val != "" {
		cfg.Vector.Qdrant.URL = val
	}
	if val := os.Getenv("QDRANT_PORT"); val != "" {
		if port, err := strconv.Atoi(val); err == nil {
			cfg.Vector.Qdrant.Port = port
		}
	}
	if val := os.Getenv("QDRANT_COLLECTION_NAME"); val != "" {
		cfg.Vector.Qdrant.CollectionName = val
	}

	// Milvus配置
	if val := os.Getenv("MILVUS_URI"); val != "" {
		cfg.Vector.Milvus.URI = val
	}
	if val := os.Getenv("MILVUS_COLLECTION_NAME"); val != "" {
		cfg.Vector.Milvus.CollectionName = val
	}

	// Neo4j配置
	if val := os.Getenv("NEO4J_URI"); val != "" {
		cfg.Knowledge.Neo4j.URI = val
	}
	if val := os.Getenv("NEO4J_USER"); val != "" {
		cfg.Knowledge.Neo4j.Username = val
	}
	if val := os.Getenv("NEO4J_PASSWORD"); val != "" {
		cfg.Knowledge.Neo4j.Password = val
	}

	// 嵌入模型配置
	if val := os.Getenv("ENABLE_LOCAL_MODELS"); val != "" {
		cfg.Embedding.EnableLocalModels = strings.ToLower(val) == "true"
	}
	if val := os.Getenv("MODEL_CACHE_DIR"); val != "" {
		cfg.Embedding.ModelCacheDir = val
	}
	if val := os.Getenv("EMBEDDING_MODEL"); val != "" {
		cfg.Embedding.Model = val
	}
	if val := os.Getenv("EMBEDDING_MAX_LENGTH"); val != "" {
		if maxLen, err := strconv.Atoi(val); err == nil {
			cfg.Embedding.MaxLength = maxLen
		}
	}
	if val := os.Getenv("EMBEDDING_DEVICE"); val != "" {
		cfg.Embedding.Device = val
	}

	// RAG配置
	if val := os.Getenv("TOP_K"); val != "" {
		if topK, err := strconv.Atoi(val); err == nil {
			cfg.Rag.TopK = topK
		}
	}
	if val := os.Getenv("SIMILARITY_THRESHOLD"); val != "" {
		if thresh, err := strconv.ParseFloat(val, 64); err == nil {
			cfg.Rag.SimilarityThreshold = thresh
		}
	}

	// 重排序配置
	if val := os.Getenv("RERANK_ENABLED"); val != "" {
		cfg.Reranker.Enabled = strings.ToLower(val) == "true"
	}
	if val := os.Getenv("RERANK_TYPE"); val != "" {
		cfg.Reranker.Type = val
	}
	if val := os.Getenv("RERANK_MODEL"); val != "" {
		cfg.Reranker.Model = val
	}
	if val := os.Getenv("RERANK_TOP_N"); val != "" {
		if topN, err := strconv.Atoi(val); err == nil {
			cfg.Reranker.TopN = topN
		}
	}

	// LLM配置
	if val := os.Getenv("LLM_PROVIDER"); val != "" {
		cfg.Llm.Provider = val
	}
	if val := os.Getenv("LLM_API_KEY"); val != "" {
		cfg.Llm.ApiKey = val
	}
	if val := os.Getenv("LLM_API_BASE"); val != "" {
		cfg.Llm.ApiBase = val
	}
	if val := os.Getenv("LLM_MODEL_NAME"); val != "" {
		cfg.Llm.ModelName = val
	}
	if val := os.Getenv("LLM_MAX_TOKENS"); val != "" {
		if maxTokens, err := strconv.Atoi(val); err == nil {
			cfg.Llm.MaxTokens = maxTokens
		}
	}
	if val := os.Getenv("LLM_TEMPERATURE"); val != "" {
		if temp, err := strconv.ParseFloat(val, 64); err == nil {
			cfg.Llm.Temperature = temp
		}
	}

	// 路径配置
	if val := os.Getenv("DATA_DIR"); val != "" {
		cfg.App.DataDir = val
	}
	if val := os.Getenv("LOGS_DIR"); val != "" {
		cfg.App.LogsDir = val
	}
	if val := os.Getenv("CONFIG_DIR"); val != "" {
		cfg.App.ConfigDir = val
	}
	if val := os.Getenv("MODELS_DIR"); val != "" {
		cfg.App.ModelsDir = val
	}

	// JWT配置
	if val := os.Getenv("JWT_SECRET"); val != "" {
		cfg.Security.JwtSecret = val
	}
	if val := os.Getenv("JWT_EXPIRY"); val != "" {
		if expiry, err := strconv.Atoi(val); err == nil {
			cfg.Security.JwtExpiry = expiry
		}
	}

	// CORS配置
	if val := os.Getenv("CORS_ORIGINS"); val != "" {
		cfg.Security.Cors.AllowOrigins = strings.Split(val, ",")
	}

	// 缓存配置
	if val := os.Getenv("CACHE_ENABLED"); val != "" {
		cfg.Cache.Enabled = strings.ToLower(val) == "true"
	}
	if val := os.Getenv("CACHE_TTL"); val != "" {
		if ttl, err := strconv.Atoi(val); err == nil {
			cfg.Cache.TTL = ttl
		}
	}
	if val := os.Getenv("CACHE_MAX_ENTRIES"); val != "" {
		if maxEntries, err := strconv.Atoi(val); err == nil {
			cfg.Cache.MaxEntries = maxEntries
		}
	}

	// 限流配置
	if val := os.Getenv("RATE_LIMIT_ENABLED"); val != "" {
		cfg.RateLimit.Enabled = strings.ToLower(val) == "true"
	}
	if val := os.Getenv("RATE_LIMIT"); val != "" {
		if limit, err := strconv.Atoi(val); err == nil {
			cfg.RateLimit.Limit = limit
		}
	}
	if val := os.Getenv("RATE_LIMIT_PERIOD"); val != "" {
		if period, err := strconv.Atoi(val); err == nil {
			cfg.RateLimit.Period = period
		}
	}

	// Web搜索配置
	if val := os.Getenv("RAG_BRAVE_API_KEY"); val != "" {
		cfg.WebSearch.ApiKeys.Brave = val
	}
	if val := os.Getenv("RAG_GOOGLE_API_KEY"); val != "" {
		cfg.WebSearch.ApiKeys.Google = val
	}
	if val := os.Getenv("RAG_KB_API_KEY"); val != "" {
		cfg.WebSearch.Knowledge.ApiKey = val
	}
}

// EnsureDirectories 确保必要的目录存在
func EnsureDirectories(cfg *Config) error {
	dirs := []string{
		cfg.App.DataDir,
		cfg.App.LogsDir,
		cfg.App.ConfigDir,
		cfg.App.ModelsDir,
		filepath.Join(cfg.App.DataDir, "vectors"),
		filepath.Join(cfg.App.DataDir, "cache"),
		filepath.Join(cfg.App.ModelsDir, "cache"),
	}

	for _, dir := range dirs {
		if err := os.MkdirAll(dir, 0755); err != nil {
			return fmt.Errorf("创建目录失败 %s: %w", dir, err)
		}
	}

	return nil
} 