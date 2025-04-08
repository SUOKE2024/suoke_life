package config

import (
	"os"
	"strconv"
	"strings"
	"time"
)

// Config 应用配置
type Config struct {
	// 环境配置
	Environment string // 运行环境：development, production, testing
	
	// 服务配置
	Server struct {
		Port         int           // 服务监听端口
		ReadTimeout  time.Duration // 读取超时
		WriteTimeout time.Duration // 写入超时
		IdleTimeout  time.Duration // 空闲连接超时
	}
	
	// Neo4j配置
	Neo4j struct {
		URI      string // Neo4j连接URI
		Username string // Neo4j用户名
		Password string // Neo4j密码
		Database string // Neo4j数据库名
		MaxConn  int    // 最大连接数
	}
	
	// 日志配置
	Log struct {
		Level string // 日志级别
		Path  string // 日志文件路径
	}
}

// LoadConfig 从环境变量加载配置
func LoadConfig() *Config {
	config := &Config{}
	
	// 环境配置
	config.Environment = getEnv("ENVIRONMENT", "development")
	
	// 服务配置
	config.Server.Port = getEnvAsInt("SERVER_PORT", 8080)
	config.Server.ReadTimeout = getEnvAsDuration("SERVER_READ_TIMEOUT", 10*time.Second)
	config.Server.WriteTimeout = getEnvAsDuration("SERVER_WRITE_TIMEOUT", 10*time.Second)
	config.Server.IdleTimeout = getEnvAsDuration("SERVER_IDLE_TIMEOUT", 60*time.Second)
	
	// Neo4j配置
	config.Neo4j.URI = getEnv("NEO4J_URI", "bolt://localhost:7687")
	config.Neo4j.Username = getEnv("NEO4J_USERNAME", "neo4j")
	config.Neo4j.Password = getEnv("NEO4J_PASSWORD", "password")
	config.Neo4j.Database = getEnv("NEO4J_DATABASE", "neo4j")
	config.Neo4j.MaxConn = getEnvAsInt("NEO4J_MAX_CONN", 50)
	
	// 日志配置
	config.Log.Level = getEnv("LOG_LEVEL", "info")
	config.Log.Path = getEnv("LOG_PATH", "logs/app.log")
	
	return config
}

// getEnv 获取环境变量，如果不存在则返回默认值
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

// getEnvAsInt 获取环境变量并转换为整数
func getEnvAsInt(key string, defaultValue int) int {
	valueStr := getEnv(key, "")
	if valueStr == "" {
		return defaultValue
	}
	value, err := strconv.Atoi(valueStr)
	if err != nil {
		return defaultValue
	}
	return value
}

// getEnvAsBool 获取环境变量并转换为布尔值
func getEnvAsBool(key string, defaultValue bool) bool {
	valueStr := getEnv(key, "")
	if valueStr == "" {
		return defaultValue
	}
	value, err := strconv.ParseBool(valueStr)
	if err != nil {
		return defaultValue
	}
	return value
}

// getEnvAsDuration 获取环境变量并转换为时间间隔
func getEnvAsDuration(key string, defaultValue time.Duration) time.Duration {
	valueStr := getEnv(key, "")
	if valueStr == "" {
		return defaultValue
	}
	
	// 检查是否包含时间单位
	if !strings.Contains(valueStr, "s") && !strings.Contains(valueStr, "m") && !strings.Contains(valueStr, "h") {
		// 默认为秒
		valueStr = valueStr + "s"
	}
	
	value, err := time.ParseDuration(valueStr)
	if err != nil {
		return defaultValue
	}
	return value
} 