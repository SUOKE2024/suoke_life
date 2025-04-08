package tests

import (
	"os"
	"testing"

	"github.com/suoke/suoke_life/services/rag-service/internal/config"
	"github.com/stretchr/testify/assert"
)

func TestDefaultConfig(t *testing.T) {
	cfg := config.DefaultConfig()
	
	// 检查默认配置值
	assert.Equal(t, "development", cfg.AppConfig.Environment)
	assert.Equal(t, "rag-service", cfg.AppConfig.Name)
	assert.Equal(t, "info", cfg.AppConfig.LogLevel)
	
	// 检查默认服务器配置
	assert.Equal(t, 8080, cfg.ServerConfig.Port)
	assert.Equal(t, 4, cfg.ServerConfig.Workers)
}

func TestLoadFromEnv(t *testing.T) {
	// 设置测试环境变量
	os.Setenv("APP_ENV", "test")
	os.Setenv("APP_NAME", "test-rag")
	os.Setenv("SERVER_PORT", "9000")
	
	// 清理函数
	defer func() {
		os.Unsetenv("APP_ENV")
		os.Unsetenv("APP_NAME")
		os.Unsetenv("SERVER_PORT")
	}()
	
	// 创建默认配置
	cfg := config.DefaultConfig()
	
	// 从环境变量加载
	config.LoadFromEnv(cfg)
	
	// 验证配置已正确加载
	assert.Equal(t, "test", cfg.AppConfig.Environment)
	assert.Equal(t, "test-rag", cfg.AppConfig.Name)
	assert.Equal(t, 9000, cfg.ServerConfig.Port)
}

func TestEnsureDirectories(t *testing.T) {
	// 设置临时目录
	tempDir := os.TempDir() + "/rag-test"
	os.Setenv("APP_DATA_DIR", tempDir)
	
	defer func() {
		os.Unsetenv("APP_DATA_DIR")
		os.RemoveAll(tempDir) // 清理
	}()
	
	// 执行目录创建
	config.EnsureDirectories()
	
	// 验证目录是否创建
	dataDirInfo, err := os.Stat(tempDir)
	assert.NoError(t, err)
	assert.True(t, dataDirInfo.IsDir())
	
	// 验证子目录是否创建
	logDirInfo, err := os.Stat(tempDir + "/logs")
	assert.NoError(t, err)
	assert.True(t, logDirInfo.IsDir())
} 