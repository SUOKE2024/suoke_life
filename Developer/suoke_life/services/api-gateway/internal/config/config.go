package config

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/spf13/viper"
)

// Config 表示API网关的配置
type Config struct {
	Server           ServerConfig       `mapstructure:"server"`
	Services         ServicesConfig     `mapstructure:"services"`
	Logging          LoggingConfig      `mapstructure:"logging"`
	Metrics          MetricsConfig      `mapstructure:"metrics"`
	Cache            CacheConfig        `mapstructure:"cache"`
	RateLimit        RateLimitConfig    `mapstructure:"rate_limit"`
	ServiceDiscovery DiscoveryConfig    `mapstructure:"service_discovery"`
	Circuit          CircuitBreakerConfig `mapstructure:"circuit_breaker"`
}

// ServerConfig 表示服务器配置
type ServerConfig struct {
	Port            int    `mapstructure:"port"`
	Host            string `mapstructure:"host"`
	ReadTimeout     int    `mapstructure:"read_timeout"`
	WriteTimeout    int    `mapstructure:"write_timeout"`
	ShutdownTimeout int    `mapstructure:"shutdown_timeout"`
}

// ServicesConfig 表示后端服务配置
type ServicesConfig struct {
	UserService            ServiceConfig `mapstructure:"user_service"`
	AuthService            ServiceConfig `mapstructure:"auth_service"`
	RAGService             ServiceConfig `mapstructure:"rag_service"`
	KnowledgeGraphService  ServiceConfig `mapstructure:"knowledge_graph_service"`
	KnowledgeBaseService   ServiceConfig `mapstructure:"knowledge_base_service"`
	InquiryDiagnosisService ServiceConfig `mapstructure:"inquiry_diagnosis_service"`
	LookingDiagnosisService ServiceConfig `mapstructure:"looking_diagnosis_service"`
	SmellDiagnosisService   ServiceConfig `mapstructure:"smell_diagnosis_service"`
	TouchDiagnosisService   ServiceConfig `mapstructure:"touch_diagnosis_service"`
}

// ServiceConfig 表示单个服务配置
type ServiceConfig struct {
	URL           string `mapstructure:"url"`
	Timeout       int    `mapstructure:"timeout"`
	RetryCount    int    `mapstructure:"retry_count"`
	RetryInterval int    `mapstructure:"retry_interval"`
}

// LoggingConfig 表示日志配置
type LoggingConfig struct {
	Level      string `mapstructure:"level"`
	FilePath   string `mapstructure:"file_path"`
	MaxSize    int    `mapstructure:"max_size"`
	MaxAge     int    `mapstructure:"max_age"`
	MaxBackups int    `mapstructure:"max_backups"`
}

// MetricsConfig 表示指标配置
type MetricsConfig struct {
	Enabled bool   `mapstructure:"enabled"`
	Path    string `mapstructure:"path"`
}

// CacheConfig 表示缓存配置
type CacheConfig struct {
	Enabled      bool   `mapstructure:"enabled"`
	DefaultTTL   int    `mapstructure:"default_ttl"`
	MaxCacheSize int    `mapstructure:"max_cache_size"`
	ExcludePaths []string `mapstructure:"exclude_paths"`
}

// RateLimitConfig 表示限流配置
type RateLimitConfig struct {
	Enabled           bool   `mapstructure:"enabled"`
	RequestsPerMinute int    `mapstructure:"requests_per_minute"`
	BurstSize         int    `mapstructure:"burst_size"`
	TimeWindow        int    `mapstructure:"time_window"`
}

// DiscoveryConfig 表示服务发现配置
type DiscoveryConfig struct {
	Enabled         bool   `mapstructure:"enabled"`
	URL             string `mapstructure:"url"`
	RefreshInterval int    `mapstructure:"refresh_interval"`
	Timeout         int    `mapstructure:"timeout"`
	FallbackToStatic bool  `mapstructure:"fallback_to_static"`
}

// CircuitBreakerConfig 表示断路器配置
type CircuitBreakerConfig struct {
	Enabled          bool `mapstructure:"enabled"`
	MaxFailures      int  `mapstructure:"max_failures"`
	Timeout          int  `mapstructure:"timeout"`
	ResetTimeout     int  `mapstructure:"reset_timeout"`
}

// LoadConfig 从指定路径加载配置
func LoadConfig(configPath string) (*Config, error) {
	var config Config

	viper.SetConfigName(filepath.Base(configPath))
	viper.SetConfigType("yaml")
	viper.AddConfigPath(filepath.Dir(configPath))

	// 默认配置
	setDefaults()

	// 从环境变量加载配置覆盖
	viper.SetEnvPrefix("SUOKE_GATEWAY")
	viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
	viper.AutomaticEnv()

	// 从配置文件读取
	err := viper.ReadInConfig()
	if err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, fmt.Errorf("读取配置文件错误: %w", err)
		}
		// 配置文件未找到，使用默认配置和环境变量
		fmt.Printf("配置文件未找到: %s, 使用默认配置和环境变量\n", configPath)
	}

	// 解析到Config结构体
	if err := viper.Unmarshal(&config); err != nil {
		return nil, fmt.Errorf("解析配置错误: %w", err)
	}

	return &config, nil
}

// setDefaults 设置默认配置
func setDefaults() {
	// 服务器配置
	viper.SetDefault("server.port", 8080)
	viper.SetDefault("server.host", "0.0.0.0")
	viper.SetDefault("server.read_timeout", 15)
	viper.SetDefault("server.write_timeout", 15)
	viper.SetDefault("server.shutdown_timeout", 10)

	// 日志配置
	viper.SetDefault("logging.level", "info")
	viper.SetDefault("logging.file_path", os.Getenv("LOG_FILE_PATH"))
	viper.SetDefault("logging.max_size", 100)  // MB
	viper.SetDefault("logging.max_age", 30)    // 天
	viper.SetDefault("logging.max_backups", 5)

	// 指标配置
	viper.SetDefault("metrics.enabled", true)
	viper.SetDefault("metrics.path", "/metrics")

	// 默认服务配置
	defaultServiceConfig := map[string]interface{}{
		"timeout":        5,
		"retry_count":    3,
		"retry_interval": 1,
	}

	// 设置各服务的默认配置
	viper.SetDefault("services.auth_service.url", "http://localhost:8081")
	viper.SetDefault("services.auth_service.timeout", defaultServiceConfig["timeout"])
	viper.SetDefault("services.auth_service.retry_count", defaultServiceConfig["retry_count"])
	viper.SetDefault("services.auth_service.retry_interval", defaultServiceConfig["retry_interval"])

	viper.SetDefault("services.user_service.url", "http://localhost:8082")
	viper.SetDefault("services.user_service.timeout", defaultServiceConfig["timeout"])
	viper.SetDefault("services.user_service.retry_count", defaultServiceConfig["retry_count"])
	viper.SetDefault("services.user_service.retry_interval", defaultServiceConfig["retry_interval"])

	// 缓存配置
	viper.SetDefault("cache.enabled", true)
	viper.SetDefault("cache.default_ttl", 300) // 5分钟
	viper.SetDefault("cache.max_cache_size", 1000) // 最多1000条缓存
	viper.SetDefault("cache.exclude_paths", []string{"/health", "/metrics"})

	// 限流配置
	viper.SetDefault("rate_limit.enabled", true)
	viper.SetDefault("rate_limit.requests_per_minute", 100)
	viper.SetDefault("rate_limit.burst_size", 20)
	viper.SetDefault("rate_limit.time_window", 60) // 秒

	// 服务发现配置
	viper.SetDefault("service_discovery.enabled", false)
	viper.SetDefault("service_discovery.url", "http://localhost:8500")
	viper.SetDefault("service_discovery.refresh_interval", 300) // 5分钟
	viper.SetDefault("service_discovery.timeout", 5) // 超时5秒
	viper.SetDefault("service_discovery.fallback_to_static", true)

	// 断路器配置
	viper.SetDefault("circuit_breaker.enabled", true)
	viper.SetDefault("circuit_breaker.max_failures", 5)
	viper.SetDefault("circuit_breaker.timeout", 10) // 断路器打开后保持10秒
	viper.SetDefault("circuit_breaker.reset_timeout", 60) // 半开状态持续60秒
}