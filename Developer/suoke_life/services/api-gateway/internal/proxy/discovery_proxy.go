package proxy

import (
	"errors"
	"math/rand"
	"sync"
	"time"

	"github.com/suoke-life/api-gateway/internal/config"
	"github.com/suoke-life/api-gateway/internal/discovery"
	"github.com/suoke-life/api-gateway/internal/logger"
)

// DiscoveryProxyManager 扩展ProxyManager，集成服务发现
type DiscoveryProxyManager struct {
	*ProxyManager
	discovery     discovery.ServiceDiscovery
	serviceURLs   map[string]string
	serviceMutex  sync.RWMutex
	isInitialized bool
}

// NewDiscoveryProxyManager 创建新的服务发现代理管理器
func NewDiscoveryProxyManager(cfg *config.Config, log logger.Logger, discovery discovery.ServiceDiscovery) *DiscoveryProxyManager {
	// 先按静态配置创建基础代理管理器
	baseManager := NewProxyManager(cfg, log)
	
	manager := &DiscoveryProxyManager{
		ProxyManager: baseManager,
		discovery:    discovery,
		serviceURLs:  make(map[string]string),
	}
	
	// 初始化服务发现
	if err := discovery.Start(); err != nil {
		log.Error("启动服务发现失败", "error", err.Error())
	} else {
		// 更新服务URL
		manager.updateServiceEndpoints()
		manager.isInitialized = true
		
		// 启动定期更新
		go manager.startEndpointUpdater(5 * time.Minute)
	}
	
	return manager
}

// startEndpointUpdater 启动定期更新服务端点的goroutine
func (m *DiscoveryProxyManager) startEndpointUpdater(interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()
	
	for range ticker.C {
		m.updateServiceEndpoints()
	}
}

// updateServiceEndpoints 从服务发现更新服务端点
func (m *DiscoveryProxyManager) updateServiceEndpoints() {
	services, err := m.discovery.GetAllServices()
	if err != nil {
		m.logger.Error("获取服务列表失败", "error", err.Error())
		return
	}
	
	m.serviceMutex.Lock()
	defer m.serviceMutex.Unlock()
	
	// 更新每个已知服务的URL
	for serviceName := range m.proxies {
		// 尝试从服务发现获取端点
		serviceInfo, found := services[normalizeServiceName(serviceName)]
		if !found || len(serviceInfo.Endpoints) == 0 {
			m.logger.Warn("服务未在服务发现中找到", "service", serviceName)
			continue
		}
		
		// 随机选择一个端点（简单的负载均衡策略）
		endpoint := selectRandomEndpoint(serviceInfo.Endpoints)
		
		// 更新服务URL
		m.serviceURLs[serviceName] = endpoint
		m.logger.Info("服务端点已更新", "service", serviceName, "endpoint", endpoint)
	}
}

// GetServiceURL 获取服务URL，优先使用服务发现，回退到静态配置
func (m *DiscoveryProxyManager) GetServiceURL(serviceName string) (string, error) {
	// 如果服务发现未初始化，使用静态配置
	if !m.isInitialized {
		return m.getStaticServiceURL(serviceName)
	}
	
	// 先尝试从服务发现缓存获取
	m.serviceMutex.RLock()
	url, exists := m.serviceURLs[serviceName]
	m.serviceMutex.RUnlock()
	
	if exists && url != "" {
		return url, nil
	}
	
	// 如果缓存中没有，尝试直接从服务发现获取
	endpoints, err := m.discovery.GetService(serviceName)
	if err == nil && len(endpoints) > 0 {
		url = selectRandomEndpoint(endpoints)
		
		// 更新缓存
		m.serviceMutex.Lock()
		m.serviceURLs[serviceName] = url
		m.serviceMutex.Unlock()
		
		return url, nil
	}
	
	// 如果服务发现失败，回退到静态配置
	m.logger.Warn("从服务发现获取服务端点失败，使用静态配置", 
		"service", serviceName, 
		"error", err.Error(),
	)
	return m.getStaticServiceURL(serviceName)
}

// getStaticServiceURL 从静态配置获取服务URL
func (m *DiscoveryProxyManager) getStaticServiceURL(serviceName string) (string, error) {
	switch serviceName {
	case "user_service":
		return m.config.Services.UserService.URL, nil
	case "auth_service":
		return m.config.Services.AuthService.URL, nil
	case "rag_service":
		return m.config.Services.RAGService.URL, nil
	case "knowledge_graph_service":
		return m.config.Services.KnowledgeGraphService.URL, nil
	default:
		return "", errors.New("未知的服务")
	}
}

// GetProxy 重写获取代理方法，优先使用服务发现
func (m *DiscoveryProxyManager) GetProxy(serviceName string) (*ServiceProxy, error) {
	// 先获取或创建代理
	proxy, err := m.ProxyManager.GetProxy(serviceName)
	if err != nil {
		return nil, err
	}
	
	// 如果服务发现未初始化，直接返回基础代理
	if !m.isInitialized {
		return proxy, nil
	}
	
	// 从服务发现获取最新URL
	url, err := m.GetServiceURL(serviceName)
	if err != nil {
		// 如果获取失败，使用现有代理
		m.logger.Warn("从服务发现获取服务URL失败", "service", serviceName, "error", err.Error())
		return proxy, nil
	}
	
	// 更新代理的服务配置
	tmpConfig := proxy.serviceConfig
	tmpConfig.URL = url
	
	// 创建新的代理实例
	newProxy := NewServiceProxy(serviceName, tmpConfig, m.logger)
	
	return newProxy, nil
}

// selectRandomEndpoint 随机选择一个端点
func selectRandomEndpoint(endpoints []string) string {
	if len(endpoints) == 0 {
		return ""
	}
	
	if len(endpoints) == 1 {
		return endpoints[0]
	}
	
	// 随机选择一个端点
	rand.Seed(time.Now().UnixNano())
	index := rand.Intn(len(endpoints))
	return endpoints[index]
}

// normalizeServiceName 标准化服务名
func normalizeServiceName(name string) string {
	switch name {
	case "user_service":
		return "user-service"
	case "auth_service":
		return "auth-service"
	case "rag_service":
		return "rag-service"
	case "knowledge_graph_service":
		return "knowledge-graph-service"
	default:
		return name
	}
} 