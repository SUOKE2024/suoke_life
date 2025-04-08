package server

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/suoke-life/auth-service/internal/controllers"
	"github.com/suoke-life/auth-service/internal/services"
	"github.com/suoke-life/shared/pkg/logger"
)

// Config 服务器配置
type Config struct {
	Port            int               `json:"port"`
	Host            string            `json:"host"`
	ReadTimeout     int               `json:"read_timeout"`
	WriteTimeout    int               `json:"write_timeout"`
	ShutdownTimeout int               `json:"shutdown_timeout"`
	JWT             services.JWTConfig `json:"jwt"`
}

// DefaultConfig 默认配置
func DefaultConfig() *Config {
	return &Config{
		Port:            8081,
		Host:            "0.0.0.0",
		ReadTimeout:     15,
		WriteTimeout:    15,
		ShutdownTimeout: 10,
		JWT:             services.DefaultJWTConfig(),
	}
}

// Server 认证服务器
type Server struct {
	router         *gin.Engine
	server         *http.Server
	logger         logger.Logger
	config         *Config
	authController *controllers.AuthController
}

// NewServer 创建新的认证服务器
func NewServer(cfg *Config, log logger.Logger, authController *controllers.AuthController) *Server {
	gin.SetMode(getGinMode())
	router := gin.New()

	// 创建服务器
	server := &Server{
		router: router,
		logger: log,
		config: cfg,
		server: &http.Server{
			Addr:         fmt.Sprintf("%s:%d", cfg.Host, cfg.Port),
			Handler:      router,
			ReadTimeout:  time.Duration(cfg.ReadTimeout) * time.Second,
			WriteTimeout: time.Duration(cfg.WriteTimeout) * time.Second,
		},
		authController: authController,
	}

	// 设置路由
	server.setupRoutes()
	return server
}

// Start 启动服务器
func (s *Server) Start() error {
	s.logger.Info("认证服务启动", "address", s.server.Addr)
	return s.server.ListenAndServe()
}

// Shutdown 优雅关闭服务器
func (s *Server) Shutdown(ctx context.Context) error {
	s.logger.Info("认证服务关闭中...")
	return s.server.Shutdown(ctx)
}

// setupRoutes 设置API路由
func (s *Server) setupRoutes() {
	// 添加中间件
	s.router.Use(gin.Recovery())
	s.router.Use(LoggerMiddleware(s.logger))
	s.router.Use(CORSMiddleware())

	// 健康检查端点
	s.router.GET("/health", s.healthCheck)

	// API路由组
	api := s.router.Group("/auth")
	{
		// 公开端点
		api.POST("/register", s.authController.Register)
		api.POST("/login", s.authController.Login)
		api.POST("/refresh", s.authController.RefreshToken)
		api.POST("/validate", s.authController.ValidateTokenForGateway)
		
		// 有保护的端点
		protected := api.Group("")
		protected.Use(s.JWTMiddleware())
		protected.GET("/validate", s.authController.ValidateToken)
	}
}

// healthCheck 健康检查处理函数
func (s *Server) healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": "ok",
		"service": "auth-service",
		"time": time.Now().Format(time.RFC3339),
	})
}

// LoggerMiddleware 日志中间件
func LoggerMiddleware(log logger.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		method := c.Request.Method

		// 请求前
		c.Next()

		// 请求后
		latency := time.Since(start)
		statusCode := c.Writer.Status()

		log.Info("API请求",
			"method", method,
			"path", path,
			"status", statusCode,
			"latency", latency,
			"client_ip", c.ClientIP(),
		)
	}
}

// CORSMiddleware CORS中间件
func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

// JWTMiddleware JWT验证中间件
func (s *Server) JWTMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "未提供认证令牌",
			})
			c.Abort()
			return
		}

		// 从Authorization头部提取令牌
		if len(authHeader) < 7 || authHeader[:7] != "Bearer " {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "认证令牌格式不正确",
			})
			c.Abort()
			return
		}
		tokenString := authHeader[7:]

		// 使用AuthController的VerifyToken方法验证令牌
		claims, err := s.authController.VerifyToken(tokenString)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "无效的令牌",
				"details": err.Error(),
			})
			c.Abort()
			return
		}

		// 将用户信息设置到上下文
		c.Set("user_id", claims.UserID)
		c.Set("user_role", claims.Role)
		
		c.Next()
	}
}

// getGinMode 根据环境返回Gin模式
func getGinMode() string {
	env := gin.ReleaseMode // 默认生产模式
	if mode := gin.DebugMode; mode == "debug" {
		env = gin.DebugMode
	}
	return env
} 