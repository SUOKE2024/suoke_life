package middleware

import (
	"errors"
	"log"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v4"
)

// JWTConfig JWT配置
type JWTConfig struct {
	SigningKey     string
	ExpirationTime time.Duration
	RefreshTime    time.Duration
	TokenLookup    string
	TokenHeadName  string
	AuthScheme     string
}

// JWTClaims JWT声明
type JWTClaims struct {
	UserID   string `json:"userId"`
	Username string `json:"username"`
	Role     string `json:"role"`
	jwt.RegisteredClaims
}

// DefaultJWTConfig 默认JWT配置
var DefaultJWTConfig = JWTConfig{
	SigningKey:     "suoke_jwt_secret_key", // 生产环境应使用环境变量
	ExpirationTime: 24 * time.Hour,
	RefreshTime:    12 * time.Hour,
	TokenLookup:    "header:Authorization",
	TokenHeadName:  "Bearer",
	AuthScheme:     "Bearer",
}

// JWTAuth JWT认证中间件
func JWTAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		config := DefaultJWTConfig
		token, err := extractToken(c, config)
		
		if err != nil {
			log.Printf("Token提取失败: %v", err)
			c.JSON(401, gin.H{
				"code":    "UNAUTHORIZED",
				"message": "未授权，请提供有效Token",
				"error":   err.Error(),
			})
			c.Abort()
			return
		}
		
		// 验证Token
		claims, err := validateToken(token, config.SigningKey)
		if err != nil {
			log.Printf("Token验证失败: %v", err)
			c.JSON(401, gin.H{
				"code":    "UNAUTHORIZED",
				"message": "Token无效或已过期",
				"error":   err.Error(),
			})
			c.Abort()
			return
		}
		
		// 将用户信息存入上下文
		c.Set("userId", claims.UserID)
		c.Set("username", claims.Username)
		c.Set("role", claims.Role)
		c.Set("claims", claims)
		
		c.Next()
	}
}

// 从请求中提取Token
func extractToken(c *gin.Context, config JWTConfig) (string, error) {
	authHeader := c.GetHeader("Authorization")
	if authHeader == "" {
		return "", errors.New("缺少Authorization头")
	}
	
	parts := strings.SplitN(authHeader, " ", 2)
	if !(len(parts) == 2 && parts[0] == config.AuthScheme) {
		return "", errors.New("Authorization头格式无效")
	}
	
	return parts[1], nil
}

// 验证Token
func validateToken(tokenString string, signingKey string) (*JWTClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
		// 验证签名方法
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("无效的签名方法")
		}
		return []byte(signingKey), nil
	})
	
	if err != nil {
		return nil, err
	}
	
	if claims, ok := token.Claims.(*JWTClaims); ok && token.Valid {
		return claims, nil
	}
	
	return nil, errors.New("无效的Token")
}

// 测试模式 - 跳过认证
func JWTAuthSkip() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 在测试环境中，直接设置测试用户ID
		c.Set("userId", "test-user-123")
		c.Set("username", "testuser")
		c.Set("role", "user")
		
		c.Next()
	}
}