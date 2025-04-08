package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// Config 应用程序配置
type Config struct {
	Server   ServerConfig   `json:"server"`
	Database DatabaseConfig `json:"database"`
	Redis    RedisConfig    `json:"redis"`
	Logging  LoggingConfig  `json:"logging"`
}

// ServerConfig 服务器配置
type ServerConfig struct {
	Host             string   `json:"host"`
	Port             int      `json:"port"`
	CorsAllowOrigins []string `json:"corsAllowOrigins"`
	ShutdownTimeout  int      `json:"shutdownTimeout"` // 单位：秒
}

// DatabaseConfig 数据库配置
type DatabaseConfig struct {
	Driver            string `json:"driver"`
	Host              string `json:"host"`
	Port              int    `json:"port"`
	Database          string `json:"database"`
	Username          string `json:"username"`
	Password          string `json:"password"`
	MaxIdleConns      int    `json:"maxIdleConns"`
	MaxOpenConns      int    `json:"maxOpenConns"`
	ConnMaxLifetime   int    `json:"connMaxLifetime"` // 单位：分钟
	MigrationsDir     string `json:"migrationsDir"`
	EnableAutoMigrate bool   `json:"enableAutoMigrate"`
}

// RedisConfig Redis配置
type RedisConfig struct {
	Host     string `json:"host"`
	Port     int    `json:"port"`
	Password string `json:"password"`
	DB       int    `json:"db"`
}

// LoggingConfig 日志配置
type LoggingConfig struct {
	Level  string `json:"level"`
	Format string `json:"format"`
	Output string `json:"output"`
}

// DefaultConfig 返回默认配置
func DefaultConfig() *Config {
	return &Config{
		Server: ServerConfig{
			Host:             "0.0.0.0",
			Port:             8082,
			CorsAllowOrigins: []string{"*"},
			ShutdownTimeout:  30,
		},
		Database: DatabaseConfig{
			Driver:            "mysql",
			Host:              "localhost",
			Port:              3306,
			Database:          "suoke_user",
			Username:          "suoke",
			Password:          "suoke_password",
			MaxIdleConns:      10,
			MaxOpenConns:      100,
			ConnMaxLifetime:   60,
			MigrationsDir:     "internal/database/migrations",
			EnableAutoMigrate: true,
		},
		Redis: RedisConfig{
			Host:     "localhost",
			Port:     6379,
			Password: "",
			DB:       0,
		},
		Logging: LoggingConfig{
			Level:  "info",
			Format: "json",
			Output: "stdout",
		},
	}
}

// LoadConfig 从文件加载配置
func LoadConfig(path string) (*Config, error) {
	// 确保配置目录存在
	configDir := filepath.Dir(path)
	if err := os.MkdirAll(configDir, 0755); err != nil {
		return nil, fmt.Errorf("创建配置目录失败: %w", err)
	}

	data, err := os.ReadFile(path)
	if err != nil {
		// 文件不存在，返回默认配置
		if os.IsNotExist(err) {
			return DefaultConfig(), nil
		}
		return nil, fmt.Errorf("读取配置文件失败: %w", err)
	}

	var config Config
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("解析配置文件失败: %w", err)
	}

	return &config, nil
}

// SaveConfig 将配置保存到文件
func SaveConfig(config *Config, path string) error {
	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return fmt.Errorf("序列化配置失败: %w", err)
	}

	if err := os.WriteFile(path, data, 0644); err != nil {
		return fmt.Errorf("写入配置文件失败: %w", err)
	}

	return nil
}

// GetDatabaseDSN 获取数据库连接字符串
func (c *DatabaseConfig) GetDatabaseDSN() string {
	return fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
		c.Host, c.Port, c.Username, c.Password, c.Database, c.Driver)
}

// GetRedisAddr 获取Redis连接地址
func (c *RedisConfig) GetRedisAddr() string {
	return fmt.Sprintf("%s:%d", c.Host, c.Port)
} 