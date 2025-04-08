package env

import (
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/joho/godotenv"
)

// Load loads environment variables from .env file
func Load(files ...string) error {
	// 如果没有指定文件，则加载默认的.env文件
	if len(files) == 0 {
		return godotenv.Load()
	}
	return godotenv.Load(files...)
}

// Get returns the value of environment variable
func Get(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

// GetBool returns the boolean value of environment variable
func GetBool(key string, defaultValue bool) bool {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}

	val, err := strconv.ParseBool(value)
	if err != nil {
		// 尝试其他可能的布尔值表示
		switch strings.ToLower(value) {
		case "yes", "y", "1", "true", "t", "on":
			return true
		case "no", "n", "0", "false", "f", "off":
			return false
		default:
			return defaultValue
		}
	}

	return val
}

// GetInt returns the integer value of environment variable
func GetInt(key string, defaultValue int) int {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}

	val, err := strconv.Atoi(value)
	if err != nil {
		return defaultValue
	}

	return val
}

// GetFloat returns the float value of environment variable
func GetFloat(key string, defaultValue float64) float64 {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}

	val, err := strconv.ParseFloat(value, 64)
	if err != nil {
		return defaultValue
	}

	return val
}

// GetDuration returns the duration value of environment variable
func GetDuration(key string, defaultValue time.Duration) time.Duration {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}

	// 首先尝试直接解析
	duration, err := time.ParseDuration(value)
	if err == nil {
		return duration
	}

	// 尝试解析为秒数
	seconds, err := strconv.ParseInt(value, 10, 64)
	if err != nil {
		return defaultValue
	}

	return time.Duration(seconds) * time.Second
}

// GetSlice returns the slice value of environment variable
func GetSlice(key string, defaultValue []string, sep string) []string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}

	if sep == "" {
		sep = ","
	}

	parts := strings.Split(value, sep)
	var result []string
	for _, part := range parts {
		trimmed := strings.TrimSpace(part)
		if trimmed != "" {
			result = append(result, trimmed)
		}
	}

	if len(result) == 0 {
		return defaultValue
	}

	return result
}

// Set sets the value of environment variable
func Set(key, value string) error {
	return os.Setenv(key, value)
}

// Unset unsets the environment variable
func Unset(key string) error {
	return os.Unsetenv(key)
}

// IsProduction returns true if environment is production
func IsProduction() bool {
	env := strings.ToLower(Get("ENV", "development"))
	return env == "production" || env == "prod"
}

// IsDevelopment returns true if environment is development
func IsDevelopment() bool {
	env := strings.ToLower(Get("ENV", "development"))
	return env == "development" || env == "dev"
}

// IsTest returns true if environment is test
func IsTest() bool {
	env := strings.ToLower(Get("ENV", "development"))
	return env == "test"
}

// GetEnv returns the current environment
func GetEnv() string {
	return strings.ToLower(Get("ENV", "development"))
} 