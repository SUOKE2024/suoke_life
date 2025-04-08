package discovery

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// MockLogger 实现日志接口
type MockLogger struct{}

func (m *MockLogger) Debug(msg string, args ...interface{}) {}
func (m *MockLogger) Info(msg string, args ...interface{})  {}
func (m *MockLogger) Warn(msg string, args ...interface{})  {}
func (m *MockLogger) Error(msg string, args ...interface{}) {}
func (m *MockLogger) Fatal(msg string, args ...interface{}) {}

func TestServiceRegistry_GetService(t *testing.T) {
	// 创建模拟注册服务
	mockRegistry := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 验证请求路径
		if r.URL.Path != "/services" {
			t.Errorf("期望路径 /services, 实际路径 %s", r.URL.Path)
			w.WriteHeader(http.StatusNotFound)
			return
		}
		
		// 验证请求方法
		if r.Method != "GET" {
			t.Errorf("期望方法 GET, 实际方法 %s", r.Method)
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}
		
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{
			"user-service": {
				"Name": "user-service",
				"Endpoints": ["http://10.0.0.1:8080", "http://10.0.0.2:8080"],
				"Version": "1.0.0",
				"Status": "UP",
				"Metadata": {
					"api_version": "v1"
				}
			},
			"auth-service": {
				"Name": "auth-service",
				"Endpoints": ["http://10.0.0.3:8081"],
				"Version": "1.0.0",
				"Status": "UP",
				"Metadata": {
					"api_version": "v1"
				}
			}
		}`))
	}))
	defer mockRegistry.Close()
	
	// 创建服务注册表
	config := DiscoveryConfig{
		URL:             mockRegistry.URL,
		RefreshInterval: 500 * time.Millisecond, // 减少刷新间隔以避免测试超时
		Timeout:         100 * time.Millisecond,
	}
	registry := NewServiceRegistry(config, &MockLogger{})
	
	// 启动服务发现后立即停止，仅执行初始化加载
	err := registry.Start()
	assert.NoError(t, err)
	registry.(interface{ Stop() }).Stop()
	
	// 测试获取服务
	endpoints, err := registry.GetService("user-service")
	
	// 验证结果
	assert.NoError(t, err)
	assert.Len(t, endpoints, 2)
	assert.Contains(t, endpoints, "http://10.0.0.1:8080")
	assert.Contains(t, endpoints, "http://10.0.0.2:8080")
}

func TestServiceRegistry_GetAllServices(t *testing.T) {
	// 创建模拟注册服务
	mockRegistry := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 验证请求路径
		if r.URL.Path != "/services" {
			t.Errorf("期望路径 /services, 实际路径 %s", r.URL.Path)
			w.WriteHeader(http.StatusNotFound)
			return
		}
		
		// 验证请求方法
		if r.Method != "GET" {
			t.Errorf("期望方法 GET, 实际方法 %s", r.Method)
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}
		
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{
			"user-service": {
				"Name": "user-service",
				"Endpoints": ["http://10.0.0.1:8080", "http://10.0.0.2:8080"],
				"Version": "1.0.0",
				"Status": "UP",
				"Metadata": {
					"api_version": "v1"
				}
			},
			"auth-service": {
				"Name": "auth-service",
				"Endpoints": ["http://10.0.0.3:8081"],
				"Version": "1.0.0",
				"Status": "UP",
				"Metadata": {
					"api_version": "v1"
				}
			}
		}`))
	}))
	defer mockRegistry.Close()
	
	// 创建服务注册表
	config := DiscoveryConfig{
		URL:             mockRegistry.URL,
		RefreshInterval: 500 * time.Millisecond,
		Timeout:         100 * time.Millisecond,
	}
	registry := NewServiceRegistry(config, &MockLogger{})
	
	// 启动服务发现后立即停止，仅执行初始化加载
	err := registry.Start()
	assert.NoError(t, err)
	registry.(interface{ Stop() }).Stop()
	
	// 测试获取所有服务
	services, err := registry.GetAllServices()
	
	// 验证结果
	assert.NoError(t, err)
	assert.Len(t, services, 2)
	assert.Contains(t, services, "user-service")
	assert.Contains(t, services, "auth-service")
	assert.Len(t, services["user-service"].Endpoints, 2)
	assert.Equal(t, "1.0.0", services["user-service"].Version)
}

func TestServiceRegistry_RefreshServices(t *testing.T) {
	// 创建模拟服务列表，每次请求返回不同的服务列表
	requestCount := 0
	mockRegistry := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 验证请求路径
		if r.URL.Path != "/services" {
			t.Errorf("期望路径 /services, 实际路径 %s", r.URL.Path)
			w.WriteHeader(http.StatusNotFound)
			return
		}
		
		// 验证请求方法
		if r.Method != "GET" {
			t.Errorf("期望方法 GET, 实际方法 %s", r.Method)
			w.WriteHeader(http.StatusMethodNotAllowed)
			return
		}
		
		requestCount++
		
		// 第一次请求返回两个服务
		if requestCount == 1 {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`{
				"user-service": {
					"Name": "user-service",
					"Endpoints": ["http://10.0.0.1:8080"],
					"Version": "1.0.0",
					"Status": "UP",
					"Metadata": {}
				},
				"auth-service": {
					"Name": "auth-service",
					"Endpoints": ["http://10.0.0.2:8081"],
					"Version": "1.0.0",
					"Status": "UP",
					"Metadata": {}
				}
			}`))
		} else { 
			// 后续请求添加新服务
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`{
				"user-service": {
					"Name": "user-service",
					"Endpoints": ["http://10.0.0.1:8080", "http://10.0.0.2:8080"],
					"Version": "1.0.0",
					"Status": "UP",
					"Metadata": {}
				},
				"auth-service": {
					"Name": "auth-service",
					"Endpoints": ["http://10.0.0.2:8081"],
					"Version": "1.0.0",
					"Status": "UP",
					"Metadata": {}
				},
				"rag-service": {
					"Name": "rag-service",
					"Endpoints": ["http://10.0.0.3:8082"],
					"Version": "1.0.0",
					"Status": "UP",
					"Metadata": {}
				}
			}`))
		}
	}))
	defer mockRegistry.Close()
	
	// 创建服务注册表
	config := DiscoveryConfig{
		URL:             mockRegistry.URL,
		RefreshInterval: 100 * time.Millisecond, // 短的刷新间隔
		Timeout:         100 * time.Millisecond,
	}
	registry := NewServiceRegistry(config, &MockLogger{})
	
	// 启动服务发现，让它自动刷新
	err := registry.Start()
	assert.NoError(t, err)
	
	// 初始状态下应该有两个服务
	services, err := registry.GetAllServices()
	assert.NoError(t, err)
	assert.Len(t, services, 2)
	
	// 等待自动刷新
	time.Sleep(300 * time.Millisecond)
	
	// 停止服务发现
	registry.(interface{ Stop() }).Stop()
	
	// 刷新后应该有三个服务
	services, err = registry.GetAllServices()
	assert.NoError(t, err)
	assert.Len(t, services, 3)
	assert.Contains(t, services, "rag-service")
	assert.Len(t, services["user-service"].Endpoints, 2)
}

func TestMockServiceDiscovery(t *testing.T) {
	// 创建模拟服务发现
	mockDiscovery := NewMockServiceDiscovery()
	
	// 添加一些服务
	mockDiscovery.AddService("user-service", []string{"http://localhost:8080", "http://localhost:8081"})
	mockDiscovery.AddService("auth-service", []string{"http://localhost:8082"})
	
	// 测试获取服务
	endpoints, err := mockDiscovery.GetService("user-service")
	assert.NoError(t, err)
	assert.Len(t, endpoints, 2)
	assert.Contains(t, endpoints, "http://localhost:8080")
	
	// 测试获取所有服务
	services, err := mockDiscovery.GetAllServices()
	assert.NoError(t, err)
	assert.Len(t, services, 2)
	
	// 测试删除服务
	mockDiscovery.RemoveService("auth-service")
	services, err = mockDiscovery.GetAllServices()
	assert.NoError(t, err)
	assert.Len(t, services, 1)
	
	// 测试获取不存在的服务
	_, err = mockDiscovery.GetService("nonexistent-service")
	assert.Error(t, err)
}