package router

import (
	"net/http"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/suoke-life/api-gateway/internal/configs"
	"github.com/suoke-life/api-gateway/internal/middleware"
	"github.com/suoke-life/api-gateway/internal/logger"
)

// SetupRouter 配置所有路由
func SetupRouter(config *configs.Config) *gin.Engine {
	// 设置Gin运行模式
	if config.Logging.Level == "debug" {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	// 创建Gin引擎
	router := gin.New()

	// 设置日志记录器
	loggerInstance, _ := logger.NewLogger(config.Logging)
	defer loggerInstance.Sync()

	// 使用中间件
	router.Use(middleware.Logger(loggerInstance))
	router.Use(gin.Recovery())
	router.Use(middleware.RateLimit(config))
	router.Use(middleware.Cache(config))

	// 配置CORS
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"},
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization", "X-Requested-With"},
		ExposeHeaders:    []string{"Content-Length", "X-New-Token", "X-Cache"},
		AllowCredentials: true,
		MaxAge:           86400,
	}))

	// 添加健康检查路由
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "UP",
		})
	})

	// 添加指标路由（如果已启用）
	if config.Metrics.Enabled {
		router.GET(config.Metrics.Path, gin.WrapH(promhttp.Handler()))
	}

	// API路由组 v1
	v1 := router.Group("/api/v1")
	{
		// 认证路由 - 不需要认证
		auth := v1.Group("/auth")
		{
			auth.POST("/login", func(c *gin.Context) {
				// 临时处理
				c.JSON(http.StatusOK, gin.H{
					"message": "登录API - 尚未实现",
					"token":   "sample_jwt_token",
				})
			})
			auth.POST("/register", func(c *gin.Context) {
				// 临时处理
				c.JSON(http.StatusOK, gin.H{
					"message": "注册API - 尚未实现",
				})
			})
		}

		// 需要认证的路由组
		authorized := v1.Group("")
		// 配置JWT认证
		jwtConfig := middleware.JWTConfig{
			SigningKey:         config.Server.JWTSecret,
			ExpirationTime:     time.Duration(config.Server.JWTExpiration) * time.Hour,
			RefreshTime:        time.Duration(config.Server.JWTRefreshTime) * time.Hour,
			TokenLookup:        "header:Authorization",
			TokenHeadName:      "Bearer",
			AuthScheme:         "Bearer",
			UseRemoteAuth:      config.Services.AuthEnabled,
			AuthServiceURL:     config.Services.AuthService.URL,
			AuthServiceTimeout: time.Duration(config.Services.AuthService.Timeout) * time.Second,
		}
		authorized.Use(middleware.JWTAuth(jwtConfig, loggerInstance))
		{
			// 登出需要认证
			authorized.POST("/auth/logout", func(c *gin.Context) {
				// 临时处理
				c.JSON(http.StatusOK, gin.H{
					"message": "登出API - 尚未实现",
				})
			})

			// 用户路由
			users := authorized.Group("/users")
			{
				users.GET("/", func(c *gin.Context) {
					// 临时处理
					c.JSON(http.StatusOK, gin.H{
						"message": "获取用户列表API - 尚未实现",
					})
				})
				users.GET("/:id", func(c *gin.Context) {
					id := c.Param("id")
					c.JSON(http.StatusOK, gin.H{
						"message": "获取用户详情API - 尚未实现",
						"id":      id,
					})
				})
			}

			// RAG服务路由
			rag := authorized.Group("/rag")
			{
				rag.POST("/query", func(c *gin.Context) {
					// 临时处理
					c.JSON(http.StatusOK, gin.H{
						"message": "RAG查询API - 尚未实现",
					})
				})
			}

			// 知识图谱路由
			kg := authorized.Group("/knowledge")
			{
				kg.GET("/search", func(c *gin.Context) {
					// 临时处理
					c.JSON(http.StatusOK, gin.H{
						"message": "知识图谱搜索API - 尚未实现",
					})
				})
			}
		}
	}

	// 首页路由
	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "索克生活API网关",
			"status":  "正常运行",
			"version": "1.0.0",
		})
	})

	return router
}