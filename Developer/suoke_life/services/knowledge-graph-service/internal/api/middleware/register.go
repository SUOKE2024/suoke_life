package middleware

import (
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

// RegisterMiddlewares 注册所有中间件
func RegisterMiddlewares(r *gin.Engine, logger *zap.Logger, jwtConfig JWTConfig) {
	// 恢复中间件 - 应该最先添加，确保panic能被捕获
	r.Use(RecoveryWithLogger(logger))
	
	// 请求跟踪中间件 - 为每个请求生成唯一ID
	r.Use(RequestTracker(logger))
	
	// CORS中间件 - 处理跨域请求
	r.Use(DefaultCORS())
	
	// JWT认证中间件 - 验证请求的认证信息
	r.Use(JWTAuth(jwtConfig, logger))
}

// RegisterAPIMiddlewares 为API路由组注册中间件
func RegisterAPIMiddlewares(r *gin.RouterGroup, logger *zap.Logger, jwtConfig JWTConfig) {
	// 请求跟踪中间件
	r.Use(RequestTracker(logger))
	
	// JWT认证中间件
	r.Use(JWTAuth(jwtConfig, logger))
}

// RegisterPublicMiddlewares 为公开路由组注册中间件
func RegisterPublicMiddlewares(r *gin.RouterGroup, logger *zap.Logger) {
	// 请求跟踪中间件
	r.Use(RequestTracker(logger))
}

// RegisterAdminMiddlewares 为管理员路由组注册中间件
func RegisterAdminMiddlewares(r *gin.RouterGroup, logger *zap.Logger, requiredRole string) {
	// 角色验证中间件
	r.Use(RequireRole(requiredRole, logger))
} 