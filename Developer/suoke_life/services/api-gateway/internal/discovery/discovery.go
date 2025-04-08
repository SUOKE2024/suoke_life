package discovery

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/suoke-life/api-gateway/internal/logger"
)

// DiscoveryConfig 服务发现配置
type DiscoveryConfig struct {
	URL             string        // 服务注册中心URL
	RefreshInterval time.Duration // 刷新间隔
	Timeout         time.Duration // 请求超时
}

// ServiceInfo 服务信息
type ServiceInfo struct {
	Name     string   // 服务名称
	Endpoints []string // 服务端点列表
	Version  string   // 服务版本
	Status   string   // 服务状态
	Metadata map[string]string // 服务元数据
}

// ServiceDiscovery 服务发现接口
type ServiceDiscovery interface {
	// GetService 获取指定服务的端点
	GetService(name string) ([]string, error)
	
	// GetAllServices 获取所有服务信息
	GetAllServices() (map[string]ServiceInfo, error)
	
	// Start 启动服务发现
	Start() error
	
	// Stop 停止服务发现
	Stop()
}

// ServiceRegistry 实现服务发现
type ServiceRegistry struct {
	config        DiscoveryConfig
	logger        logger.Logger
	services      map[string]ServiceInfo // 服务缓存
	mutex         sync.RWMutex
	client        *http.Client
	refreshTicker *time.Ticker
	stopChan      chan struct{}
	started       bool
}

// NewServiceRegistry 创建新的服务注册表
func NewServiceRegistry(config DiscoveryConfig, log logger.Logger) ServiceDiscovery {
	return &ServiceRegistry{
		config:   config,
		logger:   log,
		services: make(map[string]ServiceInfo),
		client: &http.Client{
			Timeout: config.Timeout,
		},
		stopChan: make(chan struct{}),
	}
}

// Start 启动服务发现
func (sr *ServiceRegistry) Start() error {
	sr.mutex.Lock()
	defer sr.mutex.Unlock()
	
	if sr.started {
		return nil
	}
	
	// 初始加载服务列表
	err := sr.refreshServices()
	if err != nil {
		return fmt.Errorf("初始化服务发现失败: %w", err)
	}
	
	// 启动定期刷新
	sr.refreshTicker = time.NewTicker(sr.config.RefreshInterval)
	sr.started = true
	
	go func() {
		for {
			select {
			case <-sr.refreshTicker.C:
				if err := sr.refreshServices(); err != nil {
					sr.logger.Error("刷新服务列表失败", "error", err.Error())
				}
			case <-sr.stopChan:
				sr.refreshTicker.Stop()
				return
			}
		}
	}()
	
	return nil
}

// Stop 停止服务发现
func (sr *ServiceRegistry) Stop() {
	sr.mutex.Lock()
	defer sr.mutex.Unlock()
	
	if !sr.started {
		return
	}
	
	close(sr.stopChan)
	if sr.refreshTicker != nil {
		sr.refreshTicker.Stop()
	}
	sr.started = false
}

// GetService 获取指定服务的端点
func (sr *ServiceRegistry) GetService(name string) ([]string, error) {
	sr.mutex.RLock()
	defer sr.mutex.RUnlock()
	
	// 标准化服务名
	name = normalizeServiceName(name)
	
	service, exists := sr.services[name]
	if !exists {
		return nil, fmt.Errorf("服务 '%s' 未找到", name)
	}
	
	if len(service.Endpoints) == 0 {
		return nil, fmt.Errorf("服务 '%s' 没有可用端点", name)
	}
	
	return service.Endpoints, nil
}

// GetAllServices 获取所有服务信息
func (sr *ServiceRegistry) GetAllServices() (map[string]ServiceInfo, error) {
	sr.mutex.RLock()
	defer sr.mutex.RUnlock()
	
	// 复制服务信息
	result := make(map[string]ServiceInfo, len(sr.services))
	for k, v := range sr.services {
		result[k] = v
	}
	
	return result, nil
}

// refreshServices 从服务注册中心刷新服务列表
func (sr *ServiceRegistry) refreshServices() error {
	// 构造请求
	req, err := http.NewRequest("GET", sr.config.URL+"/services", nil)
	if err != nil {
		return err
	}
	
	// 发送请求
	resp, err := sr.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	
	// 检查状态码
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("服务注册中心返回错误: %d", resp.StatusCode)
	}
	
	// 读取响应体
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	
	// 解析响应
	var services map[string]ServiceInfo
	if err := json.Unmarshal(body, &services); err != nil {
		return err
	}
	
	// 更新缓存
	sr.mutex.Lock()
	sr.services = services
	sr.mutex.Unlock()
	
	sr.logger.Info("服务列表已刷新", "serviceCount", len(services))
	return nil
}

// normalizeServiceName 标准化服务名
func normalizeServiceName(name string) string {
	// 转换为小写并替换下划线为短横线
	name = strings.ToLower(name)
	name = strings.ReplaceAll(name, "_", "-")
	return name
}

// MockServiceDiscovery 用于测试的模拟服务发现
type MockServiceDiscovery struct {
	services map[string][]string
	mutex    sync.RWMutex
}

// NewMockServiceDiscovery 创建模拟服务发现
func NewMockServiceDiscovery() *MockServiceDiscovery {
	return &MockServiceDiscovery{
		services: make(map[string][]string),
	}
}

// GetService 获取指定服务的端点
func (m *MockServiceDiscovery) GetService(name string) ([]string, error) {
	m.mutex.RLock()
	defer m.mutex.RUnlock()
	
	endpoints, exists := m.services[name]
	if !exists {
		return nil, fmt.Errorf("服务 '%s' 未找到", name)
	}
	
	return endpoints, nil
}

// GetAllServices 获取所有服务信息
func (m *MockServiceDiscovery) GetAllServices() (map[string]ServiceInfo, error) {
	m.mutex.RLock()
	defer m.mutex.RUnlock()
	
	result := make(map[string]ServiceInfo)
	for name, endpoints := range m.services {
		result[name] = ServiceInfo{
			Name:      name,
			Endpoints: endpoints,
			Status:    "UP",
		}
	}
	
	return result, nil
}

// Start 启动服务发现
func (m *MockServiceDiscovery) Start() error {
	return nil
}

// Stop 停止服务发现
func (m *MockServiceDiscovery) Stop() {
}

// AddService 添加服务端点
func (m *MockServiceDiscovery) AddService(name string, endpoints []string) {
	m.mutex.Lock()
	defer m.mutex.Unlock()
	
	m.services[name] = endpoints
}

// RemoveService 移除服务
func (m *MockServiceDiscovery) RemoveService(name string) {
	m.mutex.Lock()
	defer m.mutex.Unlock()
	
	delete(m.services, name)
} 