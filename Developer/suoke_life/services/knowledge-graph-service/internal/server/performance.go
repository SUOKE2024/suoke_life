package server

import (
	"context"
	"runtime"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/juju/ratelimit"
	"go.uber.org/zap"

	"knowledge-graph-service/internal/api/middleware"
	"knowledge-graph-service/internal/api/profiling"
)

// 性能监控和优化配置参数
type PerformanceConfig struct {
	// 是否启用性能监控和分析
	EnableMonitoring bool
	
	// 请求速率限制配置
	RateLimit struct {
		Enable    bool    // 是否启用速率限制
		Rate      float64 // 每秒允许的请求数
		Capacity  int64   // 令牌桶容量
		ByIP      bool    // 是否按IP地址限制
		WhiteList []string // IP白名单
	}
	
	// 超时控制
	Timeouts struct {
		ReadTimeout     time.Duration // 读取超时
		WriteTimeout    time.Duration // 写入超时
		RequestTimeout  time.Duration // 请求处理超时
		ShutdownTimeout time.Duration // 优雅关闭超时
	}
	
	// 连接控制
	Connections struct {
		MaxConcurrent int    // 最大并发连接数
		IdleTimeout   time.Duration // 空闲连接超时
	}
	
	// 日志配置
	Logging struct {
		RequestSampling     int  // 请求日志采样率 (1/N)
		SlowThreshold       time.Duration // 慢请求阈值
		LogRequestBody      bool // 是否记录请求体
		LogResponseBody     bool // 是否记录响应体
		LogLargeResponsesOnly bool // 仅记录大响应体
		LargeResponseThreshold int // 大响应体阈值(字节)
	}
	
	// 资源控制
	Resources struct {
		MaxProcs      int    // GOMAXPROCS设置
		MemoryLimit   uint64 // 内存使用限制
		GCPercent     int    // GC触发阈值百分比
		GCInterval    time.Duration // 强制GC间隔
	}
}

// 默认性能配置
func DefaultPerformanceConfig() PerformanceConfig {
	config := PerformanceConfig{
		EnableMonitoring: true,
	}
	
	// 速率限制默认配置
	config.RateLimit.Enable = true
	config.RateLimit.Rate = 100
	config.RateLimit.Capacity = 200
	config.RateLimit.ByIP = true
	
	// 超时默认配置
	config.Timeouts.ReadTimeout = 5 * time.Second
	config.Timeouts.WriteTimeout = 10 * time.Second
	config.Timeouts.RequestTimeout = 30 * time.Second
	config.Timeouts.ShutdownTimeout = 10 * time.Second
	
	// 连接默认配置
	config.Connections.MaxConcurrent = 1000
	config.Connections.IdleTimeout = 90 * time.Second
	
	// 日志默认配置
	config.Logging.RequestSampling = 1 // 记录所有请求
	config.Logging.SlowThreshold = 500 * time.Millisecond
	config.Logging.LogRequestBody = false
	config.Logging.LogResponseBody = false
	config.Logging.LogLargeResponsesOnly = true
	config.Logging.LargeResponseThreshold = 1024 * 10 // 10KB
	
	// 资源默认配置
	config.Resources.MaxProcs = runtime.NumCPU()
	config.Resources.GCPercent = 100
	config.Resources.GCInterval = 0 // 不强制GC
	
	return config
}

// 应用性能优化和监控配置
func ApplyPerformanceConfig(config PerformanceConfig, logger *zap.Logger) {
	// 设置GOMAXPROCS
	if config.Resources.MaxProcs > 0 {
		prevMaxProcs := runtime.GOMAXPROCS(config.Resources.MaxProcs)
		logger.Info("设置GOMAXPROCS",
			zap.Int("newValue", config.Resources.MaxProcs),
			zap.Int("prevValue", prevMaxProcs),
		)
	}
	
	// 设置GC百分比
	if config.Resources.GCPercent != 0 {
		prevGCPercent := runtime.SetGCPercent(config.Resources.GCPercent)
		logger.Info("设置GC百分比",
			zap.Int("newValue", config.Resources.GCPercent),
			zap.Int("prevValue", prevGCPercent),
		)
	}
	
	// 如果配置了定期GC，启动GC协程
	if config.Resources.GCInterval > 0 {
		logger.Info("启用定期GC", zap.Duration("interval", config.Resources.GCInterval))
		go periodicGC(config.Resources.GCInterval, logger)
	}
}

// 定期运行垃圾回收
func periodicGC(interval time.Duration, logger *zap.Logger) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()
	
	for range ticker.C {
		startTime := time.Now()
		runtime.GC()
		duration := time.Since(startTime)
		
		// 记录GC耗时
		if duration > 100*time.Millisecond {
			logger.Warn("强制GC耗时较长", zap.Duration("duration", duration))
		} else {
			logger.Debug("强制GC完成", zap.Duration("duration", duration))
		}
	}
}

// 配置性能监控和优化中间件
func SetupPerformanceMiddlewares(router *gin.Engine, config PerformanceConfig, logger *zap.Logger) {
	// 如果不启用监控，直接返回
	if !config.EnableMonitoring {
		return
	}
	
	// 注册性能分析工具
	profiling.RegisterProfiler(router, logger)
	
	// 注册超时中间件
	if config.Timeouts.RequestTimeout > 0 {
		router.Use(createTimeoutMiddleware(config.Timeouts.RequestTimeout, logger))
	}
	
	// 注册速率限制中间件
	if config.RateLimit.Enable {
		router.Use(createRateLimitMiddleware(config, logger))
	}
	
	// 注册内存使用情况监控中间件
	router.Use(memoryUsageMonitorMiddleware(logger))
}

// 请求超时中间件
func createTimeoutMiddleware(timeout time.Duration, logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 创建带超时的上下文
		ctx, cancel := context.WithTimeout(c.Request.Context(), timeout)
		defer cancel()
		
		// 将带超时的上下文关联到请求
		c.Request = c.Request.WithContext(ctx)
		
		// 在goroutine中处理超时
		done := make(chan bool)
		go func() {
			c.Next()
			done <- true
		}()
		
		// 等待处理完成或超时
		select {
		case <-done:
			// 请求正常完成
			return
		case <-ctx.Done():
			// 请求超时
			if ctx.Err() == context.DeadlineExceeded {
				logger.Warn("请求处理超时",
					zap.String("path", c.Request.URL.Path),
					zap.String("method", c.Request.Method),
					zap.Duration("timeout", timeout),
					zap.String("request_id", middleware.GetRequestID(c)),
				)
				
				// 如果响应还未发送，返回超时响应
				if !c.Writer.Written() {
					c.AbortWithStatusJSON(504, gin.H{
						"success": false,
						"code":    "request_timeout",
						"message": "请求处理超时",
					})
				}
			}
		}
	}
}

// 速率限制中间件
func createRateLimitMiddleware(config PerformanceConfig, logger *zap.Logger) gin.HandlerFunc {
	// 创建全局限流器
	globalBucket := ratelimit.NewBucketWithRate(config.RateLimit.Rate, config.RateLimit.Capacity)
	
	// 如果按IP限流，创建IP限流器映射
	var ipBuckets map[string]*ratelimit.Bucket
	if config.RateLimit.ByIP {
		ipBuckets = make(map[string]*ratelimit.Bucket)
	}
	
	return func(c *gin.Context) {
		// 检查IP是否在白名单中
		if config.RateLimit.ByIP {
			clientIP := c.ClientIP()
			for _, whitelistedIP := range config.RateLimit.WhiteList {
				if clientIP == whitelistedIP {
					c.Next()
					return
				}
			}
			
			// 获取或创建IP限流器
			bucket, exists := ipBuckets[clientIP]
			if !exists {
				bucket = ratelimit.NewBucketWithRate(config.RateLimit.Rate, config.RateLimit.Capacity)
				ipBuckets[clientIP] = bucket
			}
			
			// 尝试获取令牌
			if bucket.TakeAvailable(1) < 1 {
				logger.Warn("IP速率限制触发",
					zap.String("ip", clientIP),
					zap.String("path", c.Request.URL.Path),
					zap.String("request_id", middleware.GetRequestID(c)),
				)
				
				c.AbortWithStatusJSON(429, gin.H{
					"success": false,
					"code":    "rate_limit_exceeded",
					"message": "请求频率过高，请稍后再试",
				})
				return
			}
		}
		
		// 应用全局速率限制
		if globalBucket.TakeAvailable(1) < 1 {
			logger.Warn("全局速率限制触发",
				zap.String("path", c.Request.URL.Path),
				zap.String("request_id", middleware.GetRequestID(c)),
			)
			
			c.AbortWithStatusJSON(429, gin.H{
				"success": false,
				"code":    "rate_limit_exceeded",
				"message": "服务器正忙，请稍后再试",
			})
			return
		}
		
		c.Next()
	}
}

// 内存使用监控中间件
func memoryUsageMonitorMiddleware(logger *zap.Logger) gin.HandlerFunc {
	// 内存警告阈值 (GB)
	const memoryWarnThreshold = 1.0 * 1024 * 1024 * 1024 // 1GB
	
	// 上次GC触发时间
	var lastGCTime time.Time
	
	return func(c *gin.Context) {
		c.Next()
		
		// 采样检查 - 每100个请求检查一次内存使用
		if c.Request.URL.Path != "/metrics" && c.Request.URL.Path != "/health" && 
		   c.Request.URL.Path != "/favicon.ico" && middleware.GetRequestID(c)[0] == 'a' {
			var mem runtime.MemStats
			runtime.ReadMemStats(&mem)
			
			// 检查内存用量是否超过警告阈值
			if mem.Alloc > memoryWarnThreshold {
				logger.Warn("内存使用量较高",
					zap.Uint64("allocated_mb", mem.Alloc/1024/1024),
					zap.Uint64("sys_mb", mem.Sys/1024/1024),
					zap.Uint32("num_gc", mem.NumGC),
				)
				
				// 如果距离上次GC已经超过30秒，触发一次GC
				if time.Since(lastGCTime) > 30*time.Second {
					go func() {
						startTime := time.Now()
						runtime.GC()
						lastGCTime = time.Now()
						
						logger.Info("手动触发GC完成",
							zap.Duration("duration", time.Since(startTime)),
						)
					}()
				}
			}
		}
	}
}