package services

import (
	"testing"
	"time"

	"github.com/golang-jwt/jwt"
	"github.com/stretchr/testify/assert"
	"github.com/suoke-life/auth-service/internal/models"
)

func TestJWTService_GenerateToken(t *testing.T) {
	// 创建JWT服务
	jwtConfig := &JWTConfig{
		SecretKey:           "test-secret-key",
		AccessTokenExpiry:   time.Minute * 15,
		RefreshTokenExpiry:  time.Hour * 24 * 7,
		AccessTokenIssuer:   "suoke-auth-service-test",
		RefreshTokenIssuer:  "suoke-auth-service-test",
		AccessTokenAudience: "suoke-api-test",
		RefreshTokenAudience: "suoke-api-test",
	}
	jwtService := NewJWTService(jwtConfig)

	// 测试用户
	user := &models.User{
		ID:       "test-user-id",
		Username: "testuser",
		Email:    "test@example.com",
		Role:     "user",
	}

	// 生成令牌
	tokenResponse, err := jwtService.GenerateTokens(user)
	
	// 验证
	assert.NoError(t, err, "应该成功生成令牌")
	assert.NotEmpty(t, tokenResponse.AccessToken, "应该生成访问令牌")
	assert.NotEmpty(t, tokenResponse.RefreshToken, "应该生成刷新令牌")
	assert.Greater(t, tokenResponse.ExpiresIn, int64(0), "过期时间应该大于0")

	// 验证访问令牌
	accessToken, err := jwt.Parse(tokenResponse.AccessToken, func(token *jwt.Token) (interface{}, error) {
		return []byte(jwtConfig.SecretKey), nil
	})
	
	assert.NoError(t, err, "应该成功解析访问令牌")
	assert.True(t, accessToken.Valid, "访问令牌应该有效")
	
	accessClaims := accessToken.Claims.(jwt.MapClaims)
	assert.Equal(t, user.ID, accessClaims["sub"], "主题应该是用户ID")
	assert.Equal(t, user.Username, accessClaims["username"], "用户名应该匹配")
	assert.Equal(t, user.Role, accessClaims["role"], "角色应该匹配")
	assert.Equal(t, jwtConfig.AccessTokenIssuer, accessClaims["iss"], "颁发者应该匹配")
	assert.Equal(t, jwtConfig.AccessTokenAudience, accessClaims["aud"], "受众应该匹配")

	// 验证刷新令牌
	refreshToken, err := jwt.Parse(tokenResponse.RefreshToken, func(token *jwt.Token) (interface{}, error) {
		return []byte(jwtConfig.SecretKey), nil
	})
	
	assert.NoError(t, err, "应该成功解析刷新令牌")
	assert.True(t, refreshToken.Valid, "刷新令牌应该有效")
	
	refreshClaims := refreshToken.Claims.(jwt.MapClaims)
	assert.Equal(t, user.ID, refreshClaims["sub"], "主题应该是用户ID")
	assert.Equal(t, jwtConfig.RefreshTokenIssuer, refreshClaims["iss"], "颁发者应该匹配")
	assert.Equal(t, jwtConfig.RefreshTokenAudience, refreshClaims["aud"], "受众应该匹配")
}

func TestJWTService_ValidateToken(t *testing.T) {
	// 创建JWT服务
	jwtConfig := &JWTConfig{
		SecretKey:           "test-secret-key",
		AccessTokenExpiry:   time.Minute * 15,
		RefreshTokenExpiry:  time.Hour * 24 * 7,
		AccessTokenIssuer:   "suoke-auth-service-test",
		RefreshTokenIssuer:  "suoke-auth-service-test",
		AccessTokenAudience: "suoke-api-test",
		RefreshTokenAudience: "suoke-api-test",
	}
	jwtService := NewJWTService(jwtConfig)

	// 测试用户
	user := &models.User{
		ID:       "test-user-id",
		Username: "testuser",
		Email:    "test@example.com",
		Role:     "user",
	}

	// 生成令牌
	tokenResponse, err := jwtService.GenerateTokens(user)
	assert.NoError(t, err, "应该成功生成令牌")

	// 测试1: 验证有效的访问令牌
	claims, err := jwtService.ValidateToken(tokenResponse.AccessToken)
	assert.NoError(t, err, "应该成功验证有效的访问令牌")
	assert.Equal(t, user.ID, claims.Subject, "主题应该是用户ID")
	assert.Equal(t, user.Username, claims.Username, "用户名应该匹配")
	assert.Equal(t, user.Role, claims.Role, "角色应该匹配")

	// 测试2: 验证无效的令牌
	_, err = jwtService.ValidateToken("invalid-token")
	assert.Error(t, err, "应该拒绝无效的令牌")

	// 测试3: 验证过期的令牌
	expiredConfig := &JWTConfig{
		SecretKey:           "test-secret-key",
		AccessTokenExpiry:   time.Nanosecond, // 立即过期
		RefreshTokenExpiry:  time.Nanosecond,
		AccessTokenIssuer:   "suoke-auth-service-test",
		RefreshTokenIssuer:  "suoke-auth-service-test",
		AccessTokenAudience: "suoke-api-test",
		RefreshTokenAudience: "suoke-api-test",
	}
	expiredService := NewJWTService(expiredConfig)
	expiredToken, _ := expiredService.GenerateTokens(user)
	time.Sleep(time.Millisecond) // 确保令牌已过期
	_, err = expiredService.ValidateToken(expiredToken.AccessToken)
	assert.Error(t, err, "应该拒绝过期的令牌")
} 