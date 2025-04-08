package server

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/suoke-life/api-gateway/internal/config"
	"github.com/suoke-life/api-gateway/internal/logger"
)

func setupTestServer() *Server {
	// 使用测试模式
	gin.SetMode(gin.TestMode)
	
	// 创建测试配置
	cfg := DefaultConfig()
	cfg.Metrics.Enabled = true
	cfg.Metrics.Path = "/metrics"
	
	// 创建测试日志
	log := logger.NewLogger(logger.DefaultConfig())
	
	// 创建服务器实例
	server := NewServer(cfg, log)
	
	return server
}

func TestHealthCheck(t *testing.T) {
	// 设置测试服务器
	s := setupTestServer()
	
	// 创建测试HTTP请求
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/health", nil)
	
	// 执行请求
	s.router.ServeHTTP(w, req)
	
	// 检查响应状态码
	assert.Equal(t, http.StatusOK, w.Code)
	
	// 检查响应体
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	
	assert.Nil(t, err)
	assert.Equal(t, "ok", response["status"])
	assert.NotNil(t, response["time"])
}

func TestMetricsEndpoint(t *testing.T) {
	// 设置测试服务器
	s := setupTestServer()
	
	// 创建测试HTTP请求
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/metrics", nil)
	
	// 执行请求
	s.router.ServeHTTP(w, req)
	
	// 检查响应状态码
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestInvalidRoute(t *testing.T) {
	// 设置测试服务器
	s := setupTestServer()
	
	// 创建测试HTTP请求
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/invalid-route", nil)
	
	// 执行请求
	s.router.ServeHTTP(w, req)
	
	// 检查响应状态码 - 应该是404 Not Found
	assert.Equal(t, http.StatusNotFound, w.Code)
}

func TestCORSMiddleware(t *testing.T) {
	// 设置测试服务器
	s := setupTestServer()
	
	// 创建OPTIONS预检请求
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("OPTIONS", "/api/v1/auth/login", nil)
	req.Header.Set("Origin", "http://localhost:3000")
	req.Header.Set("Access-Control-Request-Method", "POST")
	
	// 执行请求
	s.router.ServeHTTP(w, req)
	
	// 检查CORS头部
	assert.Equal(t, http.StatusOK, w.Code)
	assert.Equal(t, "http://localhost:3000", w.Header().Get("Access-Control-Allow-Origin"))
	assert.Contains(t, w.Header().Get("Access-Control-Allow-Methods"), "POST")
}

func TestShutdown(t *testing.T) {
	// 设置测试服务器
	s := setupTestServer()
	
	// 创建一个上下文
	ctx := context.Background()
	
	// 执行关闭操作
	err := s.Shutdown(ctx)
	
	// 验证没有错误发生
	assert.Nil(t, err)
}