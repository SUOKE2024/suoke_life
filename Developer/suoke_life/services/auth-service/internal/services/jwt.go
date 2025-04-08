package services

import (
	"fmt"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/suoke-life/auth-service/internal/models"
)

// JWTConfig JWT配置
type JWTConfig struct {
	SecretKey           string        // JWT签名密钥
	AccessTokenDuration time.Duration // 访问令牌有效期
	RefreshTokenDuration time.Duration // 刷新令牌有效期
	Issuer             string        // 令牌签发者
}

// DefaultJWTConfig 默认JWT配置
func DefaultJWTConfig() JWTConfig {
	return JWTConfig{
		SecretKey:           "suoke_super_secret_key_change_me_in_production",
		AccessTokenDuration: 15 * time.Minute,  // 15分钟
		RefreshTokenDuration: 7 * 24 * time.Hour, // 7天
		Issuer:             "suoke.life",
	}
}

// JWTService JWT服务
type JWTService struct {
	config JWTConfig
}

// NewJWTService 创建JWT服务
func NewJWTService(config JWTConfig) *JWTService {
	return &JWTService{
		config: config,
	}
}

// CustomClaims 自定义JWT声明
type CustomClaims struct {
	UserID   string       `json:"user_id"`
	Username string       `json:"username"`
	Email    string       `json:"email"`
	Role     models.Role  `json:"role"`
	jwt.StandardClaims
}

// GenerateTokens 生成访问令牌和刷新令牌
func (s *JWTService) GenerateTokens(user *models.User) (*models.TokenResponse, error) {
	// 创建访问令牌
	accessToken, err := s.generateAccessToken(user)
	if err != nil {
		return nil, fmt.Errorf("生成访问令牌失败: %w", err)
	}

	// 创建刷新令牌
	refreshToken, err := s.generateRefreshToken(user)
	if err != nil {
		return nil, fmt.Errorf("生成刷新令牌失败: %w", err)
	}

	return &models.TokenResponse{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		TokenType:    "Bearer",
		ExpiresIn:    int(s.config.AccessTokenDuration.Seconds()),
	}, nil
}

// ValidateAccessToken 验证访问令牌
func (s *JWTService) ValidateAccessToken(tokenString string) (*models.TokenClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &CustomClaims{}, func(token *jwt.Token) (interface{}, error) {
		// 验证签名算法
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("非预期的签名方法: %v", token.Header["alg"])
		}
		return []byte(s.config.SecretKey), nil
	})

	if err != nil {
		return nil, fmt.Errorf("解析令牌失败: %w", err)
	}

	if !token.Valid {
		return nil, fmt.Errorf("无效的令牌")
	}

	claims, ok := token.Claims.(*CustomClaims)
	if !ok {
		return nil, fmt.Errorf("无效的令牌声明")
	}

	// 转换为TokenClaims
	return &models.TokenClaims{
		UserID:   claims.UserID,
		Username: claims.Username,
		Email:    claims.Email,
		Role:     claims.Role,
	}, nil
}

// ValidateRefreshToken 验证刷新令牌
func (s *JWTService) ValidateRefreshToken(tokenString string) (*models.TokenClaims, error) {
	// 刷新令牌的验证逻辑与访问令牌类似，但可能有不同的声明处理
	// 这里简化实现，实际可能需要区别处理
	return s.ValidateAccessToken(tokenString)
}

// generateAccessToken 生成访问令牌
func (s *JWTService) generateAccessToken(user *models.User) (string, error) {
	now := time.Now()
	expirationTime := now.Add(s.config.AccessTokenDuration)

	claims := CustomClaims{
		UserID:   user.ID,
		Username: user.Username,
		Email:    user.Email,
		Role:     user.Role,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: expirationTime.Unix(),
			IssuedAt:  now.Unix(),
			Issuer:    s.config.Issuer,
			Subject:   user.ID,
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(s.config.SecretKey))
}

// generateRefreshToken 生成刷新令牌
func (s *JWTService) generateRefreshToken(user *models.User) (string, error) {
	now := time.Now()
	expirationTime := now.Add(s.config.RefreshTokenDuration)

	claims := CustomClaims{
		UserID:   user.ID,
		Username: user.Username,
		Email:    user.Email,
		Role:     user.Role,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: expirationTime.Unix(),
			IssuedAt:  now.Unix(),
			Issuer:    s.config.Issuer,
			Subject:   user.ID,
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(s.config.SecretKey))
} 