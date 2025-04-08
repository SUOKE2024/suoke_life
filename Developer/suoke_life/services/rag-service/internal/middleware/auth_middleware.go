package middleware

import (
	"crypto/subtle"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v4"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/logger"
)

// APIKey 表示API密钥结构
type APIKey struct {
	Key         string    `json:"key"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Roles       []string  `json:"roles"`
	CreatedAt   time.Time `json:"created_at"`
	ExpiresAt   time.Time `json:"expires_at,omitempty"`
}

// apiKeys 存储所有已加载的API密钥
var (
	apiKeys     = make(map[string]APIKey)
	apiKeyMutex = &sync.RWMutex{}
)

// LoadAPIKeys 从文件加载API密钥
func LoadAPIKeys(filePath string) error {
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("读取API密钥文件失败: %w", err)
	}

	var keys []APIKey
	if err := json.Unmarshal(data, &keys); err != nil {
		return fmt.Errorf("解析API密钥文件失败: %w", err)
	}

	apiKeyMutex.Lock()
	defer apiKeyMutex.Unlock()

	// 清除旧密钥
	apiKeys = make(map[string]APIKey)

	// 加载新密钥
	now := time.Now()
	for _, key := range keys {
		// 跳过过期密钥
		if !key.ExpiresAt.IsZero() && key.ExpiresAt.Before(now) {
			logger.Infof("跳过已过期的API密钥: %s", key.Name)
			continue
		}
		apiKeys[key.Key] = key
	}

	logger.Infof("已加载 %d 个有效API密钥", len(apiKeys))
	return nil
}

// APIKeyAuthMiddleware 实现API密钥认证中间件
func APIKeyAuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 从请求头获取API密钥
		apiKey := c.GetHeader("X-Api-Key")
		if apiKey == "" {
			// 尝试从查询参数获取
			apiKey = c.Query("api_key")
		}

		if apiKey == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
				Error:     *UnauthorizedError("缺少API密钥"),
				Timestamp: getTimestamp(),
			})
			return
		}

		// 验证API密钥
		apiKeyMutex.RLock()
		key, exists := apiKeys[apiKey]
		apiKeyMutex.RUnlock()

		if !exists {
			logger.Warnf("无效的API密钥尝试访问: %s", maskString(apiKey))
			c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
				Error:     *UnauthorizedError("无效的API密钥"),
				Timestamp: getTimestamp(),
			})
			return
		}

		// 检查过期时间
		if !key.ExpiresAt.IsZero() && key.ExpiresAt.Before(time.Now()) {
			logger.Warnf("使用已过期的API密钥: %s", key.Name)
			c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
				Error:     *UnauthorizedError("API密钥已过期"),
				Timestamp: getTimestamp(),
			})
			return
		}

		// 将API密钥信息存储在上下文中供后续使用
		c.Set("apiKey", key)
		c.Set("apiKeyName", key.Name)
		c.Set("apiKeyRoles", key.Roles)

		c.Next()
	}
}

// JWTAuthMiddleware 实现JWT认证中间件
func JWTAuthMiddleware(jwtSecret string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 从请求头获取JWT令牌
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
				Error:     *UnauthorizedError("缺少授权令牌"),
				Timestamp: getTimestamp(),
			})
			return
		}

		// 验证Bearer前缀
		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
				Error:     *UnauthorizedError("无效的授权格式"),
				Timestamp: getTimestamp(),
			})
			return
		}

		tokenString := parts[1]

		// 解析JWT令牌
		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			// 验证签名算法
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("意外的签名方法: %v", token.Header["alg"])
			}
			return []byte(jwtSecret), nil
		})

		if err != nil {
			logger.Warnf("JWT解析失败: %v", err)
			c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
				Error:     *UnauthorizedError("无效的授权令牌"),
				Timestamp: getTimestamp(),
			})
			return
		}

		// 验证令牌有效性
		if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
			// 检查过期时间
			if exp, ok := claims["exp"].(float64); ok {
				if time.Now().Unix() > int64(exp) {
					c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
						Error:     *UnauthorizedError("令牌已过期"),
						Timestamp: getTimestamp(),
					})
					return
				}
			}

			// 将令牌声明存储在上下文中
			c.Set("userId", claims["sub"])
			c.Set("jwtClaims", claims)
			c.Next()
		} else {
			c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
				Error:     *UnauthorizedError("无效的授权令牌"),
				Timestamp: getTimestamp(),
			})
			return
		}
	}
}

// AdminAuthMiddleware 实现管理员身份验证中间件
func AdminAuthMiddleware(username, passwordHash string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 获取基本认证凭据
		user, pass, hasAuth := c.Request.BasicAuth()
		if !hasAuth {
			c.Header("WWW-Authenticate", "Basic realm=Admin Required")
			c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
				Error:     *UnauthorizedError("需要管理员身份验证"),
				Timestamp: getTimestamp(),
			})
			return
		}

		// 验证用户名（使用常数时间比较避免计时攻击）
		if subtle.ConstantTimeCompare([]byte(user), []byte(username)) != 1 {
			c.Header("WWW-Authenticate", "Basic realm=Admin Required")
			c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
				Error:     *UnauthorizedError("无效的管理员凭据"),
				Timestamp: getTimestamp(),
			})
			return
		}

		// 验证密码哈希（在实际实现中应该使用bcrypt或类似算法）
		// 这里仅作示例，实际应用中请使用bcrypt等安全哈希
		if subtle.ConstantTimeCompare([]byte(pass), []byte(passwordHash)) != 1 {
			logger.Warnf("管理员验证失败: 用户名 %s", username)
			c.Header("WWW-Authenticate", "Basic realm=Admin Required")
			c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
				Error:     *UnauthorizedError("无效的管理员凭据"),
				Timestamp: getTimestamp(),
			})
			return
		}

		// 验证通过
		c.Set("isAdmin", true)
		c.Next()
	}
}

// RequireRoles 检查API密钥是否有指定的角色
func RequireRoles(roles ...string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 获取API密钥角色
		apiKeyRoles, exists := c.Get("apiKeyRoles")
		if !exists {
			c.AbortWithStatusJSON(http.StatusForbidden, ErrorResponse{
				Error:     *ForbiddenError("无法验证访问权限"),
				Timestamp: getTimestamp(),
			})
			return
		}

		keyRoles, ok := apiKeyRoles.([]string)
		if !ok {
			c.AbortWithStatusJSON(http.StatusInternalServerError, ErrorResponse{
				Error:     *InternalServerError("访问权限验证错误", nil),
				Timestamp: getTimestamp(),
			})
			return
		}

		// 检查是否有所需角色
		hasRequiredRole := false
		for _, requiredRole := range roles {
			for _, keyRole := range keyRoles {
				if keyRole == requiredRole {
					hasRequiredRole = true
					break
				}
			}
			if hasRequiredRole {
				break
			}
		}

		if !hasRequiredRole {
			apiKeyName, _ := c.Get("apiKeyName")
			logger.Warnf("API密钥 %s 权限不足", apiKeyName)
			c.AbortWithStatusJSON(http.StatusForbidden, ErrorResponse{
				Error:     *ForbiddenError("权限不足"),
				Timestamp: getTimestamp(),
			})
			return
		}

		c.Next()
	}
}

// 遮蔽字符串，只显示前4位和后4位，中间用*替代
func maskString(s string) string {
	if len(s) <= 8 {
		return strings.Repeat("*", len(s))
	}
	return s[:4] + strings.Repeat("*", len(s)-8) + s[len(s)-4:]
} 