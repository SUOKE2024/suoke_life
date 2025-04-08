package config

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"
)

// Config 应用配置结构
type Config struct {
	// 环境配置
	Environment        string `json:"environment"`
	Port               int    `json:"port"`
	
	// 服务配置
	ServiceName        string `json:"serviceName"`
	ServiceVersion     string `json:"serviceVersion"`
	
	// 中间件配置
	LoggingEnabled     bool   `json:"loggingEnabled"`
	LogLevel           string `json:"logLevel"`
	AuthEnabled        bool   `json:"authEnabled"`
	ApiKey             string `json:"apiKey"`
	RateLimitEnabled   bool   `json:"rateLimitEnabled"`
	MaxRequestsPerMinute int  `json:"maxRequestsPerMinute"`
	
	// 存储配置
	PersistenceType    string `json:"persistenceType"` // memory, redis, file
	RedisHost          string `json:"redisHost"`
	RedisPort          int    `json:"redisPort"`
	RedisPassword      string `json:"redisPassword"`
	RedisDB            int    `json:"redisDB"`
}

// LoadConfig 从环境变量或配置文件加载配置
func LoadConfig() (*Config, error) {
	cfg := &Config{
		// 设置默认值
		Environment:        "development",
		Port:               3007,
		ServiceName:        "agent-coordinator-service",
		ServiceVersion:     "1.0.0",
		LoggingEnabled:     true,
		LogLevel:           "info",
		AuthEnabled:        false,
		RateLimitEnabled:   false,
		MaxRequestsPerMinute: 100,
		PersistenceType:    "memory",
	}

	// 尝试从配置文件加载
	configPath := os.Getenv("CONFIG_PATH")
	if configPath != "" {
		if err := loadFromFile(configPath, cfg); err != nil {
			return nil, fmt.Errorf("从配置文件加载失败: %w", err)
		}
	}

	// 从环境变量覆盖配置
	overrideFromEnv(cfg)

	return cfg, nil
}

// loadFromFile 从JSON文件加载配置
func loadFromFile(path string, cfg *Config) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("读取配置文件失败: %w", err)
	}

	if err := json.Unmarshal(data, cfg); err != nil {
		return fmt.Errorf("解析配置文件失败: %w", err)
	}

	return nil
}

// overrideFromEnv 从环境变量覆盖配置
func overrideFromEnv(cfg *Config) {
	// 基本配置
	if env := os.Getenv("ENVIRONMENT"); env != "" {
		cfg.Environment = env
	}
	if port := os.Getenv("PORT"); port != "" {
		if p, err := strconv.Atoi(port); err == nil {
			cfg.Port = p
		}
	}

	// 服务配置
	if name := os.Getenv("SERVICE_NAME"); name != "" {
		cfg.ServiceName = name
	}
	if version := os.Getenv("SERVICE_VERSION"); version != "" {
		cfg.ServiceVersion = version
	}

	// 中间件配置
	if logging := os.Getenv("ENABLE_REQUEST_LOGGING"); logging != "" {
		cfg.LoggingEnabled = logging == "true"
	}
	if logLevel := os.Getenv("LOG_LEVEL"); logLevel != "" {
		cfg.LogLevel = logLevel
	}
	if auth := os.Getenv("ENABLE_API_AUTH"); auth != "" {
		cfg.AuthEnabled = auth == "true"
	}
	if apiKey := os.Getenv("API_KEY"); apiKey != "" {
		cfg.ApiKey = apiKey
	}
	if rateLimit := os.Getenv("RATE_LIMIT_ENABLED"); rateLimit != "" {
		cfg.RateLimitEnabled = rateLimit == "true"
	}
	if maxRequests := os.Getenv("MAX_REQUESTS_PER_MINUTE"); maxRequests != "" {
		if m, err := strconv.Atoi(maxRequests); err == nil {
			cfg.MaxRequestsPerMinute = m
		}
	}

	// 存储配置
	if persistenceType := os.Getenv("AGENT_STATE_PERSISTENCE"); persistenceType != "" {
		cfg.PersistenceType = persistenceType
	}
	if redisHost := os.Getenv("REDIS_HOST"); redisHost != "" {
		cfg.RedisHost = redisHost
	}
	if redisPort := os.Getenv("REDIS_PORT"); redisPort != "" {
		if p, err := strconv.Atoi(redisPort); err == nil {
			cfg.RedisPort = p
		}
	}
	if redisPassword := os.Getenv("REDIS_PASSWORD"); redisPassword != "" {
		cfg.RedisPassword = redisPassword
	}
	if redisDB := os.Getenv("REDIS_DB"); redisDB != "" {
		if db, err := strconv.Atoi(redisDB); err == nil {
			cfg.RedisDB = db
		}
	}
} 