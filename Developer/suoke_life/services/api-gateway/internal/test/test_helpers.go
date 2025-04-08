package test

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/suoke-life/api-gateway/internal/config"
	"github.com/suoke-life/api-gateway/internal/logger"
)

// MockLogger 实现logger.Logger接口的模拟日志记录器
type MockLogger struct{}

func (m *MockLogger) Debug(msg string, args ...interface{}) {}
func (m *MockLogger) Info(msg string, args ...interface{})  {}
func (m *MockLogger) Warn(msg string, args ...interface{})  {}
func (m *MockLogger) Error(msg string, args ...interface{}) {}
func (m *MockLogger) Fatal(msg string, args ...interface{}) {}

// GetTestConfig 返回用于测试的配置
func GetTestConfig() *config.Config {
	return &config.Config{
		Server: config.ServerConfig{
			Port:         8080,
			Host:         "localhost",
			ReadTimeout:  5,
			WriteTimeout: 5,
		},
		Services: config.ServicesConfig{
			AuthService: config.ServiceConfig{
				URL:           "http://localhost:8081",
				Timeout:       1,
				RetryCount:    1,
				RetryInterval: 1,
			},
			UserService: config.ServiceConfig{
				URL:           "http://localhost:8082",
				Timeout:       1,
				RetryCount:    1,
				RetryInterval: 1,
			},
		},
	}
}

// GetMockLogger 返回一个测试用的日志记录器
func GetMockLogger() logger.Logger {
	return &MockLogger{}
}

// PerformRequest 执行HTTP请求并返回响应
func PerformRequest(t *testing.T, r http.Handler, method, path string, body interface{}) *httptest.ResponseRecorder {
	var reqBody io.Reader
	
	if body != nil {
		jsonBytes, err := json.Marshal(body)
		if err != nil {
			t.Fatalf("无法序列化请求体: %v", err)
		}
		reqBody = bytes.NewBuffer(jsonBytes)
	}
	
	req, err := http.NewRequest(method, path, reqBody)
	if err != nil {
		t.Fatalf("创建请求失败: %v", err)
	}
	
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	return w
}

// ParseResponse 解析JSON响应
func ParseResponse(t *testing.T, w *httptest.ResponseRecorder, out interface{}) {
	if err := json.Unmarshal(w.Body.Bytes(), out); err != nil {
		t.Fatalf("无法解析响应: %v, 响应体: %s", err, w.Body.String())
	}
}

// MockBackendServer 创建模拟后端服务
func MockBackendServer(t *testing.T, path string, response interface{}, statusCode int) *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 检查请求路径
		if r.URL.Path != path {
			t.Errorf("期望路径 %s, 实际路径 %s", path, r.URL.Path)
			w.WriteHeader(http.StatusNotFound)
			return
		}
		
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(statusCode)
		
		if response != nil {
			jsonResp, err := json.Marshal(response)
			if err != nil {
				t.Fatalf("无法序列化响应: %v", err)
			}
			fmt.Fprintln(w, string(jsonResp))
		}
	}))
}