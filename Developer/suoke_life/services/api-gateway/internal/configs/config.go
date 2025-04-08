package configs

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v2"
)

// ServerConfig 服务器配置
type ServerConfig struct {
	Port            int    `yaml:"port"`
	Host            string `yaml:"host"`
	ReadTimeout     int    `yaml:"read_timeout"`
	WriteTimeout    int    `yaml:"write_timeout"`
	ShutdownTimeout int    `yaml:"shutdown_timeout"`
	JWTSecret       string `yaml:"jwt_secret"`
	JWTExpiration   int    `yaml:"jwt_expiration"`
	JWTRefreshTime  int    `yaml:"jwt_refresh_time"`
}

// LoggingConfig 日志配置
type LoggingConfig struct {
	Level      string `yaml:"level"`
	FilePath   string `yaml:"file_path"`
	MaxSize    int    `yaml:"max_size"`
	MaxAge     int    `yaml:"max_age"`
	MaxBackups int    `yaml:"max_backups"`
}

// MetricsConfig 指标配置
type MetricsConfig struct {
	Enabled bool   `yaml:"enabled"`
	Path    string `yaml:"path"`
}

// CacheConfig 缓存配置
type CacheConfig struct {
	Enabled      bool     `yaml:"enabled"`
	DefaultTTL   int      `yaml:"default_ttl"`
	MaxCacheSize int      `yaml:"max_cache_size"`
	ExcludePaths []string `yaml:"exclude_paths"`
}

// RateLimitConfig 速率限制配置
type RateLimitConfig struct {
	Enabled          bool `yaml:"enabled"`
	RequestsPerMinute int  `yaml:"requests_per_minute"`
	BurstSize        int  `yaml:"burst_size"`
	TimeWindow       int  `yaml:"time_window"`
}

// ServiceDiscoveryConfig 服务发现配置
type ServiceDiscoveryConfig struct {
	Enabled          bool   `yaml:"enabled"`
	URL              string `yaml:"url"`
	RefreshInterval  int    `yaml:"refresh_interval"`
	Timeout          int    `yaml:"timeout"`
	FallbackToStatic bool   `yaml:"fallback_to_static"`
}

// CircuitBreakerConfig 断路器配置
type CircuitBreakerConfig struct {
	Enabled      bool `yaml:"enabled"`
	MaxFailures  int  `yaml:"max_failures"`
	Timeout      int  `yaml:"timeout"`
	ResetTimeout int  `yaml:"reset_timeout"`
}

// ServiceConfig 服务配置
type ServiceConfig struct {
	URL           string `yaml:"url"`
	Timeout       int    `yaml:"timeout"`
	RetryCount    int    `yaml:"retry_count"`
	RetryInterval int    `yaml:"retry_interval"`
}

// ServicesConfig 所有服务配置
type ServicesConfig struct {
	AuthEnabled           bool          `yaml:"auth_enabled"`
	AuthService          ServiceConfig `yaml:"auth_service"`
	UserService          ServiceConfig `yaml:"user_service"`
	RAGService           ServiceConfig `yaml:"rag_service"`
	KnowledgeGraphService ServiceConfig `yaml:"knowledge_graph_service"`
}

// Config 总配置结构
type Config struct {
	Server          ServerConfig          `yaml:"server"`
	Logging         LoggingConfig         `yaml:"logging"`
	Metrics         MetricsConfig         `yaml:"metrics"`
	Cache           CacheConfig           `yaml:"cache"`
	RateLimit       RateLimitConfig       `yaml:"rate_limit"`
	ServiceDiscovery ServiceDiscoveryConfig `yaml:"service_discovery"`
	CircuitBreaker  CircuitBreakerConfig  `yaml:"circuit_breaker"`
	Services        ServicesConfig        `yaml:"services"`
}

// LoadConfig 从指定路径加载配置
func LoadConfig(configPath string) (*Config, error) {
	// 如果未指定配置路径，寻找默认位置
	if configPath == "" {
		// 先检查环境变量
		configPath = os.Getenv("API_GATEWAY_CONFIG")
		if configPath == "" {
			// 使用默认配置路径
			configPath = "./internal/configs/config.yaml"
			// 检查默认配置文件是否存在，如果不存在则尝试其他可能的路径
			if _, err := os.Stat(configPath); os.IsNotExist(err) {
				// 尝试上级目录
				configPath = "../configs/config.yaml"
				if _, err := os.Stat(configPath); os.IsNotExist(err) {
					// 尝试配置目录
					configPath = "/etc/api-gateway/config.yaml"
					if _, err := os.Stat(configPath); os.IsNotExist(err) {
						return nil, fmt.Errorf("找不到配置文件，请使用环境变量API_GATEWAY_CONFIG指定配置文件路径")
					}
				}
			}
		}
	}

	// 确保配置文件存在
	absPath, err := filepath.Abs(configPath)
	if err != nil {
		return nil, fmt.Errorf("无法确定配置文件的绝对路径: %w", err)
	}

	if _, err := os.Stat(absPath); os.IsNotExist(err) {
		return nil, fmt.Errorf("配置文件不存在: %s", absPath)
	}

	// 读取配置文件
	fileData, err := ioutil.ReadFile(absPath)
	if err != nil {
		return nil, fmt.Errorf("无法读取配置文件: %w", err)
	}

	// 解析YAML配置
	var config Config
	if err := yaml.Unmarshal(fileData, &config); err != nil {
		return nil, fmt.Errorf("无法解析YAML配置: %w", err)
	}

	return &config, nil
}

// GetConfig 获取配置单例实例
var configInstance *Config

// GetConfig 返回配置实例，如果未初始化则加载配置
func GetConfig(configPath string) (*Config, error) {
	if configInstance == nil {
		config, err := LoadConfig(configPath)
		if err != nil {
			return nil, err
		}
		configInstance = config
	}
	return configInstance, nil
}