package config

import (
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/joho/godotenv"
)

// Config 应用配置
type Config struct {
	Server       ServerConfig
	Database     DatabaseConfig
	VectorStore  VectorStoreConfig
	Embedding    EmbeddingConfig
	TextSplitter TextSplitterConfig
	Security     SecurityConfig
	Logging      LoggingConfig
	Monitoring   MonitoringConfig
	Version      string
}

// ServerConfig 服务器配置
type ServerConfig struct {
	Port                int
	Host                string
	ReadTimeoutSeconds  int
	WriteTimeoutSeconds int
	IdleTimeoutSeconds  int
	MaxHeaderBytes      int
}

// DatabaseConfig 数据库配置
type DatabaseConfig struct {
	ConnString   string
	MaxOpenConns int
	MaxIdleConns int
	MaxLifetime  int
}

// VectorStoreConfig 向量存储配置
type VectorStoreConfig struct {
	Host       string
	Port       int
	Collection string
	APIKey     string
	UseSSL     bool
	IndexType  string
}

// EmbeddingConfig 嵌入配置
type EmbeddingConfig struct {
	ModelURL    string
	APIToken    string
	ContextSize int
	Dimensions  int
	BatchSize   int
}

// TextSplitterConfig 文本分割配置
type TextSplitterConfig struct {
	ChunkSize        int
	ChunkOverlap     int
	UseSmartBoundary bool
}

// SecurityConfig 安全配置
type SecurityConfig struct {
	AllowedOrigins []string
	JWTSecret      string
	JWTExpiresIn   int
}

// LoggingConfig 日志配置
type LoggingConfig struct {
	Level      string
	Format     string
	OutputPath string
	ErrorPath  string
}

// MonitoringConfig 监控配置
type MonitoringConfig struct {
	EnableMetrics      bool
	MetricsPort        int
	EnableTracing      bool
	TracingExporter    string
	TracingServiceName string
}

// Load 加载配置
func Load() (*Config, error) {
	// 加载.env文件（如果存在）
	godotenv.Load()

	config := &Config{
		Server: ServerConfig{
			Port:                getIntEnv("PORT", 3002),
			Host:                getEnv("APP_HOST", "0.0.0.0"),
			ReadTimeoutSeconds:  getIntEnv("SERVER_READ_TIMEOUT", 60),
			WriteTimeoutSeconds: getIntEnv("SERVER_WRITE_TIMEOUT", 60),
			IdleTimeoutSeconds:  getIntEnv("SERVER_IDLE_TIMEOUT", 120),
			MaxHeaderBytes:      getIntEnv("SERVER_MAX_HEADER_BYTES", 1<<20), // 1MB
		},
		Database: DatabaseConfig{
			ConnString:   getEnv("DB_CONNECTION_STRING", ""),
			MaxOpenConns: getIntEnv("DB_MAX_OPEN_CONNS", 25),
			MaxIdleConns: getIntEnv("DB_MAX_IDLE_CONNS", 25),
			MaxLifetime:  getIntEnv("DB_MAX_LIFETIME", 300),
		},
		VectorStore: VectorStoreConfig{
			Host:       getEnv("VECTOR_STORE_HOST", "localhost"),
			Port:       getIntEnv("VECTOR_STORE_PORT", 19530),
			Collection: getEnv("VECTOR_STORE_COLLECTION", "knowledge_base_documents"),
			APIKey:     getEnv("VECTOR_STORE_API_KEY", ""),
			UseSSL:     getBoolEnv("VECTOR_STORE_USE_SSL", false),
			IndexType:  getEnv("VECTOR_STORE_INDEX_TYPE", "FLAT"),
		},
		Embedding: EmbeddingConfig{
			ModelURL:    getEnv("EMBEDDING_MODEL_URL", "http://localhost:8000/embed"),
			APIToken:    getEnv("EMBEDDING_API_TOKEN", ""),
			ContextSize: getIntEnv("EMBEDDING_CONTEXT_SIZE", 4096),
			Dimensions:  getIntEnv("EMBEDDING_DIMENSIONS", 1536),
			BatchSize:   getIntEnv("EMBEDDING_BATCH_SIZE", 10),
		},
		TextSplitter: TextSplitterConfig{
			ChunkSize:        getIntEnv("TEXT_SPLITTER_CHUNK_SIZE", 512),
			ChunkOverlap:     getIntEnv("TEXT_SPLITTER_CHUNK_OVERLAP", 128),
			UseSmartBoundary: getBoolEnv("TEXT_SPLITTER_SMART_BOUNDARY", true),
		},
		Security: SecurityConfig{
			AllowedOrigins: getStringSliceEnv("CORS_ORIGINS", []string{"*"}),
			JWTSecret:      getEnv("JWT_SECRET", "default_secret_change_me"),
			JWTExpiresIn:   getIntEnv("JWT_EXPIRES_IN", 86400), // 24小时
		},
		Logging: LoggingConfig{
			Level:      getEnv("LOG_LEVEL", "info"),
			Format:     getEnv("LOG_FORMAT", "json"),
			OutputPath: getEnv("LOG_OUTPUT_PATH", "stdout"),
			ErrorPath:  getEnv("LOG_ERROR_PATH", "stderr"),
		},
		Monitoring: MonitoringConfig{
			EnableMetrics:      getBoolEnv("ENABLE_METRICS", true),
			MetricsPort:        getIntEnv("METRICS_PORT", 9090),
			EnableTracing:      getBoolEnv("OTEL_ENABLED", false),
			TracingExporter:    getEnv("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc"),
			TracingServiceName: getEnv("OTEL_SERVICE_NAME", "knowledge-base-service"),
		},
		Version: getEnv("APP_VERSION", "1.0.0"),
	}

	// 验证必需的配置
	if config.Database.ConnString == "" {
		return nil, fmt.Errorf("必须提供数据库连接字符串 (DB_CONNECTION_STRING)")
	}

	return config, nil
}

// 辅助函数

func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

func getIntEnv(key string, defaultValue int) int {
	if value, exists := os.LookupEnv(key); exists {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getBoolEnv(key string, defaultValue bool) bool {
	if value, exists := os.LookupEnv(key); exists {
		if boolValue, err := strconv.ParseBool(value); err == nil {
			return boolValue
		}
	}
	return defaultValue
}

func getStringSliceEnv(key string, defaultValue []string) []string {
	if value, exists := os.LookupEnv(key); exists && value != "" {
		// 简单地按逗号分割
		return strings.Split(value, ",")
	}
	return defaultValue
}
