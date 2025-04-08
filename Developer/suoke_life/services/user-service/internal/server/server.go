package server

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/suoke-life/shared/pkg/logger"
	"github.com/suoke-life/user-service/internal/config"
	"github.com/suoke-life/user-service/internal/controllers"
	"github.com/suoke-life/user-service/internal/services"
)

// Server 表示HTTP服务器
type Server struct {
	router         *gin.Engine
	httpServer     *http.Server
	config         *config.Config
	logger         logger.Logger
	userController *controllers.UserController
}

// NewServer 创建一个新的服务器实例
func NewServer(config *config.Config, userService services.UserService, log logger.Logger) *Server {
	router := gin.New()
	server := &Server{
		router: router,
		config: config,
		logger: log.With("component", "server"),
		userController: controllers.NewUserController(userService, log),
	}

	server.setupRouter()
	return server
}

// setupRouter 配置路由
func (s *Server) setupRouter() {
	// 中间件
	s.router.Use(gin.Recovery())
	s.router.Use(s.loggerMiddleware())
	
	// CORS设置
	s.router.Use(cors.New(cors.Config{
		AllowOrigins:     s.config.Server.CorsAllowOrigins,
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))
	
	// 健康检查
	s.router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "ok",
			"service": "user-service",
			"timestamp": time.Now().Format(time.RFC3339),
		})
	})
	
	// API路由组
	api := s.router.Group("/api/v1")
	{
		// 用户相关路由
		users := api.Group("/users")
		{
			users.POST("", s.userController.CreateUser)
			users.GET("", s.userController.ListUsers)
			users.GET("/:id", s.userController.GetUser)
			users.GET("/username/:username", s.userController.GetUserByUsername)
			users.PUT("/:id", s.userController.UpdateUser)
			users.DELETE("/:id", s.userController.DeleteUser)
			users.PUT("/:id/preferences", s.userController.UpdateUserPreferences)
			users.PUT("/:id/last-seen", s.userController.UpdateLastSeen)
		}
	}
}

// loggerMiddleware 创建日志中间件
func (s *Server) loggerMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		query := c.Request.URL.RawQuery
		
		c.Next()
		
		latency := time.Since(start)
		status := c.Writer.Status()
		
		if query != "" {
			path = path + "?" + query
		}
		
		s.logger.Info("HTTP请求",
			"method", c.Request.Method,
			"path", path,
			"status", status,
			"latency", latency,
			"ip", c.ClientIP(),
			"user-agent", c.Request.UserAgent(),
		)
	}
}

// Start 启动HTTP服务器
func (s *Server) Start() error {
	s.httpServer = &http.Server{
		Addr:    fmt.Sprintf("%s:%d", s.config.Server.Host, s.config.Server.Port),
		Handler: s.router,
	}
	
	s.logger.Info("启动HTTP服务器", "addr", s.httpServer.Addr)
	if err := s.httpServer.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		return fmt.Errorf("服务器启动失败: %w", err)
	}
	
	return nil
}

// Shutdown 优雅地关闭HTTP服务器
func (s *Server) Shutdown(ctx context.Context) error {
	s.logger.Info("正在关闭HTTP服务器")
	
	if s.httpServer != nil {
		if err := s.httpServer.Shutdown(ctx); err != nil {
			return fmt.Errorf("服务器关闭失败: %w", err)
		}
	}
	
	return nil
} 