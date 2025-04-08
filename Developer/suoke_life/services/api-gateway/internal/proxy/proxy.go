package proxy

import (
	"bytes"
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"net/url"
	"path"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/suoke-life/api-gateway/internal/config"
	"github.com/suoke-life/api-gateway/internal/logger"
)

// ServiceProxy 表示服务代理
type ServiceProxy struct {
	logger       logger.Logger
	client       *http.Client
	serviceConfig config.ServiceConfig
	serviceName   string
}

// NewServiceProxy 创建新的服务代理
func NewServiceProxy(serviceName string, cfg config.ServiceConfig, log logger.Logger) *ServiceProxy {
	return &ServiceProxy{
		logger:       log,
		serviceName:  serviceName,
		serviceConfig: cfg,
		client: &http.Client{
			Timeout: time.Duration(cfg.Timeout) * time.Second,
		},
	}
}

// Proxy 处理代理请求
func (p *ServiceProxy) Proxy(targetPath string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 构造目标URL
		targetURL, err := url.Parse(p.serviceConfig.URL)
		if err != nil {
			p.logger.Error("无法解析服务URL", "error", err, "service", p.serviceName)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "代理服务错误"})
			return
		}
		
		// 替换路径参数
		// 例如，将 "/users/:id" 替换为实际的 "/users/123"
		resolvedPath := resolvePath(targetPath, c.Params)
		targetURL.Path = path.Join(targetURL.Path, resolvedPath)
		
		// 添加查询参数
		query := targetURL.Query()
		for k, v := range c.Request.URL.Query() {
			for _, vv := range v {
				query.Add(k, vv)
			}
		}
		targetURL.RawQuery = query.Encode()
		
		// 读取请求体
		var reqBody []byte
		if c.Request.Body != nil {
			reqBody, err = io.ReadAll(c.Request.Body)
			if err != nil {
				p.logger.Error("读取请求体失败", "error", err)
				c.JSON(http.StatusInternalServerError, gin.H{"error": "无法读取请求数据"})
				return
			}
			// 关闭原始请求体
			c.Request.Body.Close()
		}
		
		// 创建代理请求
		proxyReq, err := p.createProxyRequest(c.Request.Method, targetURL.String(), reqBody, c.Request.Header)
		if err != nil {
			p.logger.Error("创建代理请求失败", "error", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "代理服务错误"})
			return
		}
		
		// 添加额外的头部
		proxyReq.Header.Set("X-Forwarded-For", c.ClientIP())
		proxyReq.Header.Set("X-Proxy-Service", p.serviceName)
		
		// 发送请求（带重试逻辑）
		startTime := time.Now()
		resp, err := p.sendRequestWithRetries(proxyReq, reqBody)
		duration := time.Since(startTime)
		
		// 记录请求详情
		p.logger.Info("代理请求",
			"service", p.serviceName,
			"method", c.Request.Method,
			"path", targetURL.Path,
			"duration", duration,
			"client_ip", c.ClientIP(),
		)
		
		if err != nil {
			p.logger.Error("代理请求失败", "error", err, "service", p.serviceName)
			c.JSON(http.StatusBadGateway, gin.H{"error": "目标服务不可用"})
			return
		}
		defer resp.Body.Close()
		
		// 复制响应状态码
		c.Status(resp.StatusCode)
		
		// 复制响应头部
		for k, v := range resp.Header {
			for _, vv := range v {
				c.Header(k, vv)
			}
		}
		
		// 复制响应体
		responseBody, err := io.ReadAll(resp.Body)
		if err != nil {
			p.logger.Error("读取响应体失败", "error", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "无法读取服务响应"})
			return
		}
		
		c.Writer.Write(responseBody)
	}
}

// sendRequestWithRetries 发送请求，支持重试
func (p *ServiceProxy) sendRequestWithRetries(req *http.Request, originalBody []byte) (*http.Response, error) {
	var resp *http.Response
	var err error
	
	// 初始化重试次数
	retries := 0
	maxRetries := p.serviceConfig.RetryCount
	
	// 实现带退避的重试
	for retries <= maxRetries {
		// 如果这是重试，并且有请求体，需要重新创建请求体
		if retries > 0 && len(originalBody) > 0 {
			req.Body = io.NopCloser(bytes.NewBuffer(originalBody))
			req.ContentLength = int64(len(originalBody))
		}
		
		// 发送请求
		resp, err = p.client.Do(req)
		
		// 判断是否需要重试
		if err == nil && resp.StatusCode < 500 {
			// 成功或客户端错误，不需要重试
			return resp, err
		}
		
		// 如果有响应但需要重试，关闭响应体
		if resp != nil {
			resp.Body.Close()
		}
		
		// 达到最大重试次数，返回最后一次错误
		if retries == maxRetries {
			break
		}
		
		// 计算退避时间: 基础间隔 * (2^重试次数)
		backoff := time.Duration(p.serviceConfig.RetryInterval) * 
				  time.Second * time.Duration(1<<uint(retries))
				  
		// 添加随机抖动 (0-100ms)
		jitter := time.Duration(rand.Intn(100)) * time.Millisecond
		backoff = backoff + jitter
		
		p.logger.Warn("代理请求失败，准备重试",
			"service", p.serviceName,
			"retry", retries+1,
			"backoff", backoff,
			"error", err,
		)
		
		// 等待后重试
		time.Sleep(backoff)
		retries++
	}
	
	return resp, err
}

// createProxyRequest 创建代理HTTP请求
func (p *ServiceProxy) createProxyRequest(method, url string, body []byte, originalHeaders http.Header) (*http.Request, error) {
	// 创建请求
	var bodyReader io.Reader
	if len(body) > 0 {
		bodyReader = bytes.NewBuffer(body)
	}
	
	req, err := http.NewRequest(method, url, bodyReader)
	if err != nil {
		return nil, err
	}
	
	// 复制原始请求的头部
	for k, v := range originalHeaders {
		// 忽略一些特定的头部
		if !shouldSkipHeader(k) {
			for _, vv := range v {
				req.Header.Add(k, vv)
			}
		}
	}
	
	// 设置Content-Length
	if len(body) > 0 {
		req.ContentLength = int64(len(body))
	}
	
	return req, nil
}

// resolvePath 替换路径中的参数
func resolvePath(pathTemplate string, params gin.Params) string {
	result := pathTemplate
	for _, param := range params {
		placeholder := fmt.Sprintf(":%s", param.Key)
		result = strings.Replace(result, placeholder, param.Value, 1)
	}
	return result
}

// shouldSkipHeader 检查是否应该跳过该头部
func shouldSkipHeader(header string) bool {
	skipHeaders := []string{
		"Connection",
		"Keep-Alive",
		"Proxy-Authenticate",
		"Proxy-Authorization",
		"TE",
		"Trailers",
		"Transfer-Encoding",
		"Upgrade",
	}
	
	header = strings.ToLower(header)
	for _, h := range skipHeaders {
		if strings.ToLower(h) == header {
			return true
		}
	}
	return false
}

// ProxyManager 管理各个服务的代理
type ProxyManager struct {
	logger    logger.Logger
	config    *config.Config
	proxies   map[string]*ServiceProxy
}

// NewProxyManager 创建新的代理管理器
func NewProxyManager(cfg *config.Config, log logger.Logger) *ProxyManager {
	manager := &ProxyManager{
		logger:  log,
		config:  cfg,
		proxies: make(map[string]*ServiceProxy),
	}
	
	// 初始化所有服务的代理
	manager.initProxies()
	return manager
}

// initProxies 初始化所有服务的代理
func (m *ProxyManager) initProxies() {
	// 实例化所有服务的代理
	// 用户服务
	m.proxies["user_service"] = NewServiceProxy("user_service", m.config.Services.UserService, m.logger)
	
	// 认证服务
	m.proxies["auth_service"] = NewServiceProxy("auth_service", m.config.Services.AuthService, m.logger)
	
	// RAG服务
	m.proxies["rag_service"] = NewServiceProxy("rag_service", m.config.Services.RAGService, m.logger)
	
	// 知识图谱服务
	m.proxies["knowledge_graph_service"] = NewServiceProxy("knowledge_graph_service", m.config.Services.KnowledgeGraphService, m.logger)
	
	// 其他服务...可以类似地添加
}

// GetProxy 获取指定服务的代理
func (m *ProxyManager) GetProxy(serviceName string) (*ServiceProxy, error) {
	proxy, ok := m.proxies[serviceName]
	if !ok {
		return nil, fmt.Errorf("未找到服务: %s", serviceName)
	}
	return proxy, nil
}

// ProxyToService 创建代理到指定服务的处理函数
func (m *ProxyManager) ProxyToService(serviceName, targetPath string) gin.HandlerFunc {
	return func(c *gin.Context) {
		proxy, err := m.GetProxy(serviceName)
		if err != nil {
			m.logger.Error("获取服务代理失败", "error", err, "service", serviceName)
			c.JSON(http.StatusBadGateway, gin.H{"error": "服务不可用"})
			return
		}
		
		// 代理请求
		handler := proxy.Proxy(targetPath)
		handler(c)
	}
} 