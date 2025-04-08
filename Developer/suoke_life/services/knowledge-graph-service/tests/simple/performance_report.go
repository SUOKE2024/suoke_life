package simple

import (
	"fmt"
	"math/rand"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
)

// 全面性能测试
func BenchmarkFullPerformanceComparison(b *testing.B) {
	// 创建四种路由：标准、UUID优化、响应优化、全优化
	standardRouter := setupStandardRouter()
	uuidOptimizedRouter := setupUUIDOptimizedRouter()
	responseOptimizedRouter := setupResponseOptimizedRouter()
	fullyOptimizedRouter := setupFullyOptimizedRouter()

	// 准备请求
	req := httptest.NewRequest(http.MethodGet, "/api/test?param=value", nil)
	req.Header.Set("User-Agent", "BenchmarkClient")

	// 标准路由测试
	b.Run("Standard", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			standardRouter.ServeHTTP(w, req)
		}
	})

	// UUID优化路由测试
	b.Run("UUIDOptimized", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			uuidOptimizedRouter.ServeHTTP(w, req)
		}
	})

	// 响应优化路由测试
	b.Run("ResponseOptimized", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			responseOptimizedRouter.ServeHTTP(w, req)
		}
	})

	// 全优化路由测试
	b.Run("FullyOptimized", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			fullyOptimizedRouter.ServeHTTP(w, req)
		}
	})
}

// 设置标准路由
func setupStandardRouter() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.Use(standardRequestTracker())
	
	router.GET("/api/test", func(c *gin.Context) {
		data := generateTestData()
		standardSuccess(c, data)
	})
	
	return router
}

// 设置UUID优化路由
func setupUUIDOptimizedRouter() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.Use(optimizedRequestTracker())
	
	router.GET("/api/test", func(c *gin.Context) {
		data := generateTestData()
		standardSuccess(c, data)
	})
	
	return router
}

// 设置响应优化路由
func setupResponseOptimizedRouter() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.Use(standardRequestTracker())
	
	router.GET("/api/test", func(c *gin.Context) {
		data := generateTestData()
		optimizedSuccess(c, data)
	})
	
	return router
}

// 设置全优化路由
func setupFullyOptimizedRouter() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.Use(optimizedRequestTracker())
	
	router.GET("/api/test", func(c *gin.Context) {
		data := generateTestData()
		optimizedSuccess(c, data)
	})
	
	return router
}

// 生成测试数据
func generateTestData() interface{} {
	return map[string]interface{}{
		"id":        rand.Intn(1000),
		"name":      fmt.Sprintf("Item-%d", rand.Intn(100)),
		"status":    "active",
		"timestamp": time.Now().Unix(),
		"tags":      []string{"test", "performance", "api"},
	}
}

// 高负载压力测试
func BenchmarkHighLoadScenario(b *testing.B) {
	// 设置标准和优化后的路由
	standardRouter := setupStandardRouter()
	optimizedRouter := setupFullyOptimizedRouter()
	
	// 准备不同类型的请求
	reqSmall := httptest.NewRequest(http.MethodGet, "/api/test?size=small", nil)
	reqMedium := httptest.NewRequest(http.MethodGet, "/api/test?size=medium", nil)
	reqLarge := httptest.NewRequest(http.MethodGet, "/api/test?size=large", nil)
	
	// 小数据量请求
	b.Run("Standard_SmallData", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			standardRouter.ServeHTTP(w, reqSmall)
		}
	})
	
	b.Run("Optimized_SmallData", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			optimizedRouter.ServeHTTP(w, reqSmall)
		}
	})
	
	// 中等数据量请求
	b.Run("Standard_MediumData", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			standardRouter.ServeHTTP(w, reqMedium)
		}
	})
	
	b.Run("Optimized_MediumData", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			optimizedRouter.ServeHTTP(w, reqMedium)
		}
	})
	
	// 大数据量请求
	b.Run("Standard_LargeData", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			standardRouter.ServeHTTP(w, reqLarge)
		}
	})
	
	b.Run("Optimized_LargeData", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			optimizedRouter.ServeHTTP(w, reqLarge)
		}
	})
}

// 并发处理测试
func BenchmarkConcurrentRequests(b *testing.B) {
	// 设置并发数
	concurrency := 10
	
	// 设置标准和优化后的路由
	standardRouter := setupStandardRouter()
	optimizedRouter := setupFullyOptimizedRouter()
	
	// 准备请求
	req := httptest.NewRequest(http.MethodGet, "/api/test", nil)
	
	b.Run("Standard_Concurrent", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		
		// 并发测试
		b.RunParallel(func(pb *testing.PB) {
			for pb.Next() {
				w := httptest.NewRecorder()
				standardRouter.ServeHTTP(w, req)
			}
		})
	})
	
	b.Run("Optimized_Concurrent", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		
		// 并发测试
		b.RunParallel(func(pb *testing.PB) {
			for pb.Next() {
				w := httptest.NewRecorder()
				optimizedRouter.ServeHTTP(w, req)
			}
		})
	})
	
	// 模拟更复杂的并发场景
	b.Run("Standard_ComplexConcurrent", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		
		b.SetParallelism(concurrency)
		
		var wg sync.WaitGroup
		wg.Add(concurrency)
		
		for i := 0; i < concurrency; i++ {
			go func() {
				defer wg.Done()
				for j := 0; j < b.N/concurrency; j++ {
					w := httptest.NewRecorder()
					standardRouter.ServeHTTP(w, req)
				}
			}()
		}
		
		wg.Wait()
	})
	
	b.Run("Optimized_ComplexConcurrent", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		
		b.SetParallelism(concurrency)
		
		var wg sync.WaitGroup
		wg.Add(concurrency)
		
		for i := 0; i < concurrency; i++ {
			go func() {
				defer wg.Done()
				for j := 0; j < b.N/concurrency; j++ {
					w := httptest.NewRecorder()
					optimizedRouter.ServeHTTP(w, req)
				}
			}()
		}
		
		wg.Wait()
	})
}

// 测试异常处理场景
func BenchmarkErrorHandling(b *testing.B) {
	// 设置标准和优化后的路由
	standardRouter := gin.New()
	standardRouter.Use(standardRequestTracker())
	standardRouter.GET("/api/error", func(c *gin.Context) {
		c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"message": "Internal Server Error",
		})
	})
	
	optimizedRouter := gin.New()
	optimizedRouter.Use(optimizedRequestTracker())
	optimizedRouter.GET("/api/error", func(c *gin.Context) {
		resp := responsePool.Get().(*standardResponse)
		defer responsePool.Put(resp)
		
		*resp = standardResponse{
			Success: false,
			Code:    "internal_error",
			Message: "Internal Server Error",
		}
		
		c.JSON(http.StatusInternalServerError, resp)
	})
	
	// 准备请求
	req := httptest.NewRequest(http.MethodGet, "/api/error", nil)
	
	b.Run("Standard_ErrorHandling", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			standardRouter.ServeHTTP(w, req)
		}
	})
	
	b.Run("Optimized_ErrorHandling", func(b *testing.B) {
		b.ReportAllocs()
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			optimizedRouter.ServeHTTP(w, req)
		}
	})
} 