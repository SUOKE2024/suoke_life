package profiling

import (
	"fmt"
	"net/http"
	"net/http/pprof"
	"os"
	"runtime"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

var (
	// 环境变量控制是否启用性能分析
	// ENABLE_PPROF=true 时启用性能分析
	// CPU_PROFILE_RATE 控制CPU profile的采样率 (默认100)
	// BLOCK_PROFILE_RATE 控制阻塞profile的采样率 (默认1)
	// MUTEX_PROFILE_FRACTION 控制互斥锁profile的采样比例 (默认0)
	enablePprof          = os.Getenv("ENABLE_PPROF") == "true"
	cpuProfileRate       = getEnvInt("CPU_PROFILE_RATE", 100)
	blockProfileRate     = getEnvInt("BLOCK_PROFILE_RATE", 1)
	mutexProfileFraction = getEnvInt("MUTEX_PROFILE_FRACTION", 0)
)

// 从环境变量获取整数值，如果环境变量不存在或无效，返回默认值
func getEnvInt(key string, defaultVal int) int {
	val := os.Getenv(key)
	if val == "" {
		return defaultVal
	}
	var result int
	_, err := fmt.Sscanf(val, "%d", &result)
	if err != nil {
		return defaultVal
	}
	return result
}

// 初始化性能分析配置
func init() {
	if enablePprof {
		// 设置CPU性能分析采样率
		runtime.SetCPUProfileRate(cpuProfileRate)
		
		// 设置阻塞分析采样率 (每n次阻塞事件采样一次)
		runtime.SetBlockProfileRate(blockProfileRate)
		
		// 设置互斥锁分析比例 (1/n的互斥锁事件被记录)
		runtime.SetMutexProfileFraction(mutexProfileFraction)
	}
}

// RegisterPprofRoutes 注册pprof HTTP路由
// 仅在enablePprof为true时生效
func RegisterPprofRoutes(router *gin.Engine, logger *zap.Logger) {
	if !enablePprof {
		logger.Info("性能分析功能未启用. 设置环境变量 ENABLE_PPROF=true 以启用")
		return
	}
	
	logger.Info("注册性能分析路由",
		zap.Int("cpuProfileRate", cpuProfileRate),
		zap.Int("blockProfileRate", blockProfileRate),
		zap.Int("mutexProfileFraction", mutexProfileFraction),
	)
	
	pprofGroup := router.Group("/debug/pprof")
	{
		pprofGroup.GET("/", gin.WrapF(pprof.Index))
		pprofGroup.GET("/cmdline", gin.WrapF(pprof.Cmdline))
		pprofGroup.GET("/profile", gin.WrapF(pprof.Profile))
		pprofGroup.POST("/symbol", gin.WrapF(pprof.Symbol))
		pprofGroup.GET("/symbol", gin.WrapF(pprof.Symbol))
		pprofGroup.GET("/trace", gin.WrapF(pprof.Trace))
		pprofGroup.GET("/allocs", gin.WrapH(pprof.Handler("allocs")))
		pprofGroup.GET("/block", gin.WrapH(pprof.Handler("block")))
		pprofGroup.GET("/goroutine", gin.WrapH(pprof.Handler("goroutine")))
		pprofGroup.GET("/heap", gin.WrapH(pprof.Handler("heap")))
		pprofGroup.GET("/mutex", gin.WrapH(pprof.Handler("mutex")))
		pprofGroup.GET("/threadcreate", gin.WrapH(pprof.Handler("threadcreate")))
	}
	
	// 添加内存统计端点
	router.GET("/debug/mem", func(c *gin.Context) {
		var mem runtime.MemStats
		runtime.ReadMemStats(&mem)
		
		c.JSON(http.StatusOK, gin.H{
			"alloc":        mem.Alloc,
			"totalAlloc":   mem.TotalAlloc,
			"sys":          mem.Sys,
			"numGC":        mem.NumGC,
			"pauseTotalNs": mem.PauseTotalNs,
			"numGoroutine": runtime.NumGoroutine(),
		})
	})
	
	// 添加GC控制端点
	router.POST("/debug/gc", func(c *gin.Context) {
		startTime := time.Now()
		
		// 手动触发GC
		runtime.GC()
		
		duration := time.Since(startTime)
		
		var mem runtime.MemStats
		runtime.ReadMemStats(&mem)
		
		c.JSON(http.StatusOK, gin.H{
			"message":     "垃圾回收已完成",
			"duration_ms": duration.Milliseconds(),
			"numGC":       mem.NumGC,
			"allocated":   mem.Alloc,
		})
	})
}

// CPUProfileMiddleware 生成CPU性能分析中间件
// 对指定的请求路径进行CPU分析
func CPUProfileMiddleware(duration time.Duration, logger *zap.Logger) gin.HandlerFunc {
	if !enablePprof {
		return func(c *gin.Context) {
			c.Next()
		}
	}
	
	return func(c *gin.Context) {
		// 从请求参数中获取采样时间 (默认使用传入的duration)
		durationStr := c.Query("duration")
		profileDuration := duration
		
		if durationStr != "" {
			if parsedDuration, err := time.ParseDuration(durationStr); err == nil {
				// 限制最大采样时间
				if parsedDuration > 30*time.Second {
					profileDuration = 30 * time.Second
				} else {
					profileDuration = parsedDuration
				}
			}
		}
		
		logger.Info("开始CPU性能分析", 
			zap.Duration("duration", profileDuration),
			zap.String("path", c.Request.URL.Path),
		)
		
		// 创建临时文件保存性能分析数据
		f, err := os.CreateTemp("", "cpu_profile_*.pprof")
		if err != nil {
			logger.Error("创建CPU性能分析文件失败", zap.Error(err))
			c.Next()
			return
		}
		defer f.Close()
		
		// 启动CPU性能分析
		if err := pprof.StartCPUProfile(f); err != nil {
			logger.Error("启动CPU性能分析失败", zap.Error(err))
			c.Next()
			return
		}
		
		// 确保在处理完请求后停止分析
		defer pprof.StopCPUProfile()
		
		// 继续处理请求
		c.Next()
		
		logger.Info("CPU性能分析已完成",
			zap.String("profile_file", f.Name()),
			zap.String("path", c.Request.URL.Path),
			zap.Int("status", c.Writer.Status()),
		)
	}
}

// MemoryProfileHandler 返回一个处理函数，用于生成内存分析快照
func MemoryProfileHandler(logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 创建临时文件保存内存分析数据
		f, err := os.CreateTemp("", "mem_profile_*.pprof")
		if err != nil {
			logger.Error("创建内存性能分析文件失败", zap.Error(err))
			c.JSON(http.StatusInternalServerError, gin.H{"error": "创建分析文件失败"})
			return
		}
		defer f.Close()
		
		// 手动运行一次GC以获得更准确的内存分析
		runtime.GC()
		
		// 写入内存分析数据
		if err := pprof.WriteHeapProfile(f); err != nil {
			logger.Error("写入内存分析数据失败", zap.Error(err))
			c.JSON(http.StatusInternalServerError, gin.H{"error": "写入分析数据失败"})
			return
		}
		
		logger.Info("内存分析完成", zap.String("profile_file", f.Name()))
		
		c.JSON(http.StatusOK, gin.H{
			"message":      "内存分析完成",
			"profile_file": f.Name(),
		})
	}
}

// RegisterProfiler 将所有性能分析工具注册到路由
func RegisterProfiler(router *gin.Engine, logger *zap.Logger) {
	// 注册标准pprof路由
	RegisterPprofRoutes(router, logger)
	
	// 注册自定义性能分析端点
	if enablePprof {
		// 内存分析快照端点
		router.GET("/debug/profile/memory", MemoryProfileHandler(logger))
		
		// 对特定API进行CPU分析的演示
		router.GET("/api/v1/profile-test", CPUProfileMiddleware(5*time.Second, logger), func(c *gin.Context) {
			// 模拟耗时操作
			time.Sleep(200 * time.Millisecond)
			
			// 做一些CPU密集型计算
			result := 0
			for i := 0; i < 1000000; i++ {
				result += i
			}
			
			c.JSON(http.StatusOK, gin.H{
				"message": "性能测试API",
				"result":  result,
			})
		})
	}
}