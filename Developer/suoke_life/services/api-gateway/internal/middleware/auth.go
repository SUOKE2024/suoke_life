package middleware

import (
	"errors"
	"net/http"
	"strings"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/gin-gonic/gin"
	"github.com/suoke-life/api-gateway/internal/clients"
	"github.com/suoke-life/api-gateway/internal/logger"
)

// JWTConfig JWT配置
type JWTConfig struct {
	SigningKey       string        // JWT签名密钥
	ExpirationTime   time.Duration // JWT过期时间
	RefreshTime      time.Duration // JWT刷新时间
	TokenLookup      string        // 查找token的方式，如"header:Authorization"
	TokenHeadName    string        // Token头名称，如"Bearer"
	AuthScheme       string        // 认证方案，如"Bearer"
	UseRemoteAuth    bool          // 是否使用远程验证
	AuthServiceURL   string        // 认证服务URL
	AuthServiceTimeout time.Duration // 认证服务超时
}

// DefaultJWTConfig 默认JWT配置
var DefaultJWTConfig = JWTConfig{
	SigningKey:     "suoke_life_secret_key", // 生产环境应从环境变量或配置中读取
	ExpirationTime: 24 * time.Hour,
	RefreshTime:    12 * time.Hour,
	TokenLookup:    "header:Authorization",
	TokenHeadName:  "Bearer",
	AuthScheme:     "Bearer",
	UseRemoteAuth:  false,
	AuthServiceURL: "http://auth-service:8081",
	AuthServiceTimeout: 5 * time.Second,
}

// JWTClaims JWT声明
type JWTClaims struct {
	UserID   string `json:"user_id"`
	Username string `json:"username,omitempty"`
	Email    string `json:"email,omitempty"`
	Role     string `json:"role"`
	jwt.StandardClaims
}

// JWTAuth JWT认证中间件
func JWTAuth(config JWTConfig, log logger.Logger) gin.HandlerFunc {
	if config.SigningKey == "" {
		config = DefaultJWTConfig
	}

	var authClient *clients.AuthClient
	if config.UseRemoteAuth {
		authClient = clients.NewAuthClient(config.AuthServiceURL, config.AuthServiceTimeout, log)
	}

	return func(c *gin.Context) {
		token, err := extractToken(c, config)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "未授权访问: " + err.Error(),
			})
			c.Abort()
			return
		}

		var claims *JWTClaims
		var tokenClaims *clients.TokenClaims

		// 尝试使用远程验证
		if config.UseRemoteAuth && authClient != nil {
			tokenClaims, err = authClient.ValidateToken(token)
			if err == nil && tokenClaims != nil {
				// 远程验证成功，创建本地Claims
				claims = &JWTClaims{
					UserID:   tokenClaims.UserID,
					Username: tokenClaims.Username,
					Email:    tokenClaims.Email,
					Role:     tokenClaims.Role,
				}
			} else {
				log.Warn("远程令牌验证失败，尝试本地验证: " + err.Error())
				// 远程验证失败，尝试本地验证
				claims, err = validateToken(token, config.SigningKey)
			}
		} else {
			// 直接使用本地验证
			claims, err = validateToken(token, config.SigningKey)
		}

		if err != nil || claims == nil {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "无效的令牌: " + err.Error(),
			})
			c.Abort()
			return
		}

		// 将用户信息存储在上下文中
		c.Set("userID", claims.UserID)
		c.Set("role", claims.Role)
		if claims.Username != "" {
			c.Set("username", claims.Username)
		}
		if claims.Email != "" {
			c.Set("email", claims.Email)
		}

		// 检查是否需要刷新令牌
		if shouldRefreshToken(claims, config.RefreshTime) {
			// 创建一个新的令牌
			newToken, err := generateToken(claims.UserID, claims.Role, config)
			if err == nil {
				c.Header("X-New-Token", newToken)
			}
		}

		c.Next()
	}
}

// 从请求中提取令牌
func extractToken(c *gin.Context, config JWTConfig) (string, error) {
	parts := strings.Split(config.TokenLookup, ":")
	if len(parts) != 2 {
		return "", errors.New("无效的token查找配置")
	}

	extractor := parts[0]
	lookup := parts[1]

	switch extractor {
	case "header":
		auth := c.GetHeader(lookup)
		if auth == "" {
			return "", errors.New("未提供认证令牌")
		}
		if config.TokenHeadName != "" {
			authParts := strings.SplitN(auth, " ", 2)
			if len(authParts) != 2 || authParts[0] != config.TokenHeadName {
				return "", errors.New("无效的认证方案")
			}
			return authParts[1], nil
		}
		return auth, nil
	case "query":
		return c.Query(lookup), nil
	case "cookie":
		return c.Cookie(lookup)
	default:
		return "", errors.New("不支持的token提取方式")
	}
}

// 验证令牌
func validateToken(tokenString, signingKey string) (*JWTClaims, error) {
	if tokenString == "" {
		return nil, errors.New("令牌为空")
	}

	token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("意外的签名方法")
		}
		return []byte(signingKey), nil
	})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(*JWTClaims); ok && token.Valid {
		return claims, nil
	}

	return nil, errors.New("无效的令牌")
}

// 生成令牌
func generateToken(userID, role string, config JWTConfig) (string, error) {
	claims := JWTClaims{
		UserID: userID,
		Role:   role,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: time.Now().Add(config.ExpirationTime).Unix(),
			IssuedAt:  time.Now().Unix(),
			Issuer:    "suoke-life-api-gateway",
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(config.SigningKey))
}

// 检查是否应该刷新令牌
func shouldRefreshToken(claims *JWTClaims, refreshTime time.Duration) bool {
	expiresAt := time.Unix(claims.ExpiresAt, 0)
	refreshAt := expiresAt.Add(-refreshTime)
	return time.Now().After(refreshAt)
}