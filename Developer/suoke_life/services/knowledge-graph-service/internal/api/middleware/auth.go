package middleware

import (
	"errors"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v4"
	"go.uber.org/zap"
)

// Context键定义
type ContextKey string

const (
	// TokenHeader 认证头
	TokenHeader = "Authorization"
	
	// Bearer 认证方式前缀
	Bearer = "Bearer "
	
	// UserKey 用户信息的上下文键
	UserKey ContextKey = "user"
	
	// RequestIDKey 请求ID的上下文键
	RequestIDKey ContextKey = "request_id"
	
	// TraceIDKey 跟踪ID的上下文键
	TraceIDKey ContextKey = "trace_id"
	
	// StartTimeKey 请求开始时间的上下文键
	StartTimeKey ContextKey = "start_time"
	
	// RequestIDHeader 请求ID的HTTP头
	RequestIDHeader = "X-Request-ID"
	
	// TraceIDHeader 跟踪ID的HTTP头
	TraceIDHeader = "X-Trace-ID"
)

// GetRequestID 从上下文获取请求ID
func GetRequestID(c *gin.Context) string {
	if requestID, exists := c.Get(string(RequestIDKey)); exists {
		if id, ok := requestID.(string); ok {
			return id
		}
	}
	return ""
}

// GetTraceID 从上下文获取跟踪ID
func GetTraceID(c *gin.Context) string {
	if traceID, exists := c.Get(string(TraceIDKey)); exists {
		if id, ok := traceID.(string); ok {
			return id
		}
	}
	return ""
}

// JWTConfig JWT配置
type JWTConfig struct {
	SecretKey       string
	ExpireDuration  time.Duration
	RefreshDuration time.Duration
	Issuer          string
	Audience        string
	SkipPaths       []string
}

// DefaultJWTConfig 创建默认的JWT配置
func DefaultJWTConfig() JWTConfig {
	return JWTConfig{
		SecretKey:       "default-secret-key",
		ExpireDuration:  24 * time.Hour,
		RefreshDuration: 7 * 24 * time.Hour,
		Issuer:          "knowledge-graph-service",
		Audience:        "knowledge-graph-users",
		SkipPaths:       []string{"/health", "/auth/login", "/auth/register"},
	}
}

// UserClaims 用户JWT声明
type UserClaims struct {
	ID       string   `json:"id"`
	Username string   `json:"username"`
	Email    string   `json:"email"`
	Roles    []string `json:"roles"`
	jwt.RegisteredClaims
}

// JWTAuth JWT认证中间件
func JWTAuth(config JWTConfig, logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 检查是否跳过此路径
		if shouldSkipAuthPath(c.Request.URL.Path, config.SkipPaths) {
			c.Next()
			return
		}

		// 从请求头获取令牌
		authHeader := c.GetHeader(TokenHeader)
		if authHeader == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"code":    "unauthorized",
				"message": "缺少认证令牌",
			})
			return
		}

		// 检查前缀
		if !strings.HasPrefix(authHeader, Bearer) {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"code":    "unauthorized",
				"message": "认证令牌格式错误",
			})
			return
		}

		// 提取令牌
		tokenString := authHeader[len(Bearer):]

		// 解析令牌
		claims := &UserClaims{}
		token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
			// 验证签名算法
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
			}
			return []byte(config.SecretKey), nil
		})

		if err != nil {
			if errors.Is(err, jwt.ErrTokenExpired) {
				c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
					"success": false,
					"code":    "token_expired",
					"message": "认证令牌已过期",
				})
				return
			}
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"code":    "invalid_token",
				"message": "无效的认证令牌",
			})
			return
		}

		// 验证令牌
		if !token.Valid {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"code":    "invalid_token",
				"message": "无效的认证令牌",
			})
			return
		}

		// 验证发行者
		if claims.Issuer != config.Issuer {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"code":    "invalid_issuer",
				"message": "无效的令牌发行者",
			})
			return
		}

		// 验证受众
		if !contains(claims.Audience, config.Audience) {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"code":    "invalid_audience",
				"message": "无效的令牌受众",
			})
			return
		}

		// 将用户信息存储到上下文
		c.Set(string(UserKey), claims)

		// 记录认证信息
		logger.Debug("认证成功",
			zap.String("user_id", claims.ID),
			zap.String("username", claims.Username),
			zap.Strings("roles", claims.Roles),
			zap.String("request_id", GetRequestID(c)),
		)

		c.Next()
	}
}

// RequireRole 角色验证中间件
func RequireRole(requiredRole string, logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 从上下文获取用户信息
		userValue, exists := c.Get(string(UserKey))
		if !exists {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{
				"success": false,
				"code":    "unauthorized",
				"message": "用户未认证",
			})
			return
		}

		// 类型断言
		claims, ok := userValue.(*UserClaims)
		if !ok {
			c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
				"success": false,
				"code":    "internal_error",
				"message": "用户信息格式错误",
			})
			return
		}

		// 验证角色
		if !containsRole(claims.Roles, requiredRole) {
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{
				"success": false,
				"code":    "forbidden",
				"message": "权限不足",
				"details": fmt.Sprintf("需要角色: %s", requiredRole),
			})
			return
		}

		logger.Debug("角色验证通过",
			zap.String("user_id", claims.ID),
			zap.String("username", claims.Username),
			zap.String("required_role", requiredRole),
			zap.String("request_id", GetRequestID(c)),
		)

		c.Next()
	}
}

// GetCurrentUser 从上下文获取当前用户
func GetCurrentUser(c *gin.Context) (*UserClaims, bool) {
	// 从上下文获取用户信息
	userValue, exists := c.Get(string(UserKey))
	if !exists {
		return nil, false
	}

	// 类型断言
	claims, ok := userValue.(*UserClaims)
	if !ok {
		return nil, false
	}

	return claims, true
}

// IsAuthenticated 检查用户是否已认证
func IsAuthenticated(c *gin.Context) bool {
	_, exists := GetCurrentUser(c)
	return exists
}

// HasRole 检查用户是否有指定角色
func HasRole(c *gin.Context, role string) bool {
	user, exists := GetCurrentUser(c)
	if !exists {
		return false
	}
	return containsRole(user.Roles, role)
}

// 辅助函数

// shouldSkipAuthPath 检查是否应该跳过认证
func shouldSkipAuthPath(path string, skipPaths []string) bool {
	for _, skipPath := range skipPaths {
		if path == skipPath || strings.HasPrefix(path, skipPath) {
			return true
		}
	}
	return false
}

// contains 检查字符串数组是否包含指定值
func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

// containsRole 检查角色数组是否包含指定角色
func containsRole(roles []string, role string) bool {
	// 管理员角色拥有所有权限
	if contains(roles, "admin") {
		return true
	}
	return contains(roles, role)
}