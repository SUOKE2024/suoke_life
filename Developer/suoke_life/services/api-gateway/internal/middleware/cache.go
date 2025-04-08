package middleware

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"net/http"
	"regexp"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/patrickmn/go-cache"
	"github.com/suoke-life/api-gateway/internal/configs"
)

// CacheStore 缓存存储接口
type CacheStore interface {
	Get(key string) (interface{}, bool)
	Set(key string, value interface{}, expiration time.Duration)
	Delete(key string)
}

// MemoryCacheStore 内存缓存存储实现
type MemoryCacheStore struct {
	cache *cache.Cache
}

// NewMemoryCacheStore 创建一个新的内存缓存存储
func NewMemoryCacheStore(defaultExpiration, cleanupInterval time.Duration) *MemoryCacheStore {
	return &MemoryCacheStore{
		cache: cache.New(defaultExpiration, cleanupInterval),
	}
}

// Get 从缓存中获取值
func (m *MemoryCacheStore) Get(key string) (interface{}, bool) {
	return m.cache.Get(key)
}

// Set 将值存入缓存
func (m *MemoryCacheStore) Set(key string, value interface{}, expiration time.Duration) {
	m.cache.Set(key, value, expiration)
}

// Delete 从缓存中删除值
func (m *MemoryCacheStore) Delete(key string) {
	m.cache.Delete(key)
}

// CachedResponse 缓存的响应
type CachedResponse struct {
	Status int
	Header http.Header
	Data   []byte
}

// CacheMiddleware 缓存中间件配置
type CacheMiddleware struct {
	Store        CacheStore
	TTL          time.Duration
	ExcludePaths []*regexp.Regexp
}

// NewCacheMiddleware 创建一个新的缓存中间件
func NewCacheMiddleware(config *configs.Config) *CacheMiddleware {
	if !config.Cache.Enabled {
		return nil
	}

	// 编译排除路径正则表达式
	excludePaths := make([]*regexp.Regexp, 0, len(config.Cache.ExcludePaths))
	for _, path := range config.Cache.ExcludePaths {
		r, err := regexp.Compile(path)
		if err == nil {
			excludePaths = append(excludePaths, r)
		}
	}

	return &CacheMiddleware{
		Store:        NewMemoryCacheStore(time.Duration(config.Cache.DefaultTTL)*time.Second, time.Minute),
		TTL:          time.Duration(config.Cache.DefaultTTL) * time.Second,
		ExcludePaths: excludePaths,
	}
}

// ShouldCacheRequest 检查是否应该缓存请求
func (m *CacheMiddleware) ShouldCacheRequest(c *gin.Context) bool {
	// 只缓存GET请求
	if c.Request.Method != http.MethodGet {
		return false
	}

	// 检查请求路径是否被排除
	path := c.Request.URL.Path
	for _, regex := range m.ExcludePaths {
		if regex.MatchString(path) {
			return false
		}
	}

	return true
}

// GenerateCacheKey 生成缓存键
func (m *CacheMiddleware) GenerateCacheKey(c *gin.Context) string {
	// 使用URL路径和查询参数作为缓存键的基础
	baseKey := c.Request.URL.Path + "?" + c.Request.URL.RawQuery

	// 如果有认证信息，加入到键中
	if userID, exists := c.Get("userID"); exists {
		baseKey = fmt.Sprintf("%s|user:%v", baseKey, userID)
	}

	// 使用SHA256进行哈希处理，创建固定长度的键
	hash := sha256.Sum256([]byte(baseKey))
	return hex.EncodeToString(hash[:])
}

// Cache 缓存中间件
func Cache(config *configs.Config) gin.HandlerFunc {
	middleware := NewCacheMiddleware(config)
	if middleware == nil {
		// 如果缓存未启用，返回一个空的中间件
		return func(c *gin.Context) {
			c.Next()
		}
	}

	return func(c *gin.Context) {
		// 检查是否应该缓存这个请求
		if !middleware.ShouldCacheRequest(c) {
			c.Next()
			return
		}

		// 生成缓存键
		cacheKey := middleware.GenerateCacheKey(c)

		// 尝试从缓存中获取响应
		if cachedResp, found := middleware.Store.Get(cacheKey); found {
			response := cachedResp.(*CachedResponse)

			// 设置响应状态码
			c.Status(response.Status)

			// 设置响应头
			for key, values := range response.Header {
				for _, value := range values {
					c.Header(key, value)
				}
			}

			// 设置缓存命中头
			c.Header("X-Cache", "HIT")

			// 写入响应内容
			c.Writer.Write(response.Data)

			// 中止执行后续处理函数
			c.Abort()
			return
		}

		// 没有缓存，替换响应写入器以捕获响应
		responseWriter := &responseBodyWriter{
			ResponseWriter: c.Writer,
			body:           &bytes.Buffer{},
		}
		c.Writer = responseWriter

		// 继续执行后续处理函数
		c.Next()

		// 设置缓存未命中头
		c.Header("X-Cache", "MISS")

		// 将响应存入缓存
		if c.Writer.Status() < 300 && c.Writer.Status() >= 200 {
			response := &CachedResponse{
				Status: c.Writer.Status(),
				Header: c.Writer.Header(),
				Data:   responseWriter.body.Bytes(),
			}
			middleware.Store.Set(cacheKey, response, middleware.TTL)
		}
	}
}

// responseBodyWriter 是一个自定义的响应写入器，用于捕获响应内容
type responseBodyWriter struct {
	gin.ResponseWriter
	body *bytes.Buffer
}

// Write 写入响应并捕获内容
func (r *responseBodyWriter) Write(b []byte) (int, error) {
	r.body.Write(b)
	return r.ResponseWriter.Write(b)
}

// WriteString 写入字符串并捕获内容
func (r *responseBodyWriter) WriteString(s string) (int, error) {
	r.body.WriteString(s)
	return r.ResponseWriter.WriteString(s)
}

// WriteHeader 写入响应头
func (r *responseBodyWriter) WriteHeader(code int) {
	r.ResponseWriter.WriteHeader(code)
}