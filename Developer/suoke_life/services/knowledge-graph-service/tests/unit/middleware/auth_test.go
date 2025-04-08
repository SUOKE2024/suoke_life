package middleware_test

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v4"
	"github.com/stretchr/testify/assert"
	"go.uber.org/zap"

	"knowledge-graph-service/internal/api/middleware"
)

func TestJWTAuth(t *testing.T) {
	// 设置测试环境
	gin.SetMode(gin.TestMode)
	logger, _ := zap.NewDevelopment()

	// 创建一个有效的令牌
	validToken := createValidToken(t, "test-key")

	// 测试用例
	tests := []struct {
		name          string
		path          string
		token         string
		exemptPaths   []string
		expectedCode  int
		expectedAbort bool
	}{
		{
			name:          "无认证令牌",
			path:          "/api/v1/data",
			token:         "",
			exemptPaths:   []string{},
			expectedCode:  http.StatusUnauthorized,
			expectedAbort: true,
		},
		{
			name:          "无效格式令牌",
			path:          "/api/v1/data",
			token:         "Invalid-Token",
			exemptPaths:   []string{},
			expectedCode:  http.StatusUnauthorized,
			expectedAbort: true,
		},
		{
			name:          "有效令牌",
			path:          "/api/v1/data",
			token:         "Bearer " + validToken,
			exemptPaths:   []string{},
			expectedCode:  http.StatusOK,
			expectedAbort: false,
		},
		{
			name:          "豁免路径无需认证",
			path:          "/api/v1/auth/login",
			token:         "",
			exemptPaths:   []string{"/api/v1/auth/login"},
			expectedCode:  http.StatusOK,
			expectedAbort: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 创建测试上下文
			w := httptest.NewRecorder()
			c, _ := gin.CreateTestContext(w)
			c.Request = httptest.NewRequest("GET", tt.path, nil)

			if tt.token != "" {
				c.Request.Header.Set("Authorization", tt.token)
			}

			// 配置中间件
			jwtConfig := middleware.JWTConfig{
				SigningKey:  "test-key",
				ExemptPaths: tt.exemptPaths,
			}

			// 调用中间件
			middleware.JWTAuth(jwtConfig, logger)(c)

			// 验证结果
			if tt.expectedAbort {
				assert.True(t, c.IsAborted())
				assert.Equal(t, tt.expectedCode, w.Code)
			} else {
				assert.False(t, c.IsAborted())
			}
		})
	}
}

// 创建有效的JWT令牌用于测试
func createValidToken(t *testing.T, key string) string {
	claims := jwt.MapClaims{
		"user_id": "test-user-id",
		"roles":   []string{"user"},
		"exp":     time.Now().Add(time.Hour).Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte(key))
	assert.NoError(t, err)

	return tokenString
}

func TestRequireRole(t *testing.T) {
	// 设置测试环境
	gin.SetMode(gin.TestMode)
	logger, _ := zap.NewDevelopment()

	// 测试用例
	tests := []struct {
		name          string
		userRole      string
		requiredRole  string
		expectedCode  int
		expectedAbort bool
	}{
		{
			name:          "有所需角色权限",
			userRole:      "admin",
			requiredRole:  "admin",
			expectedCode:  http.StatusOK,
			expectedAbort: false,
		},
		{
			name:          "无所需角色权限",
			userRole:      "user",
			requiredRole:  "admin",
			expectedCode:  http.StatusForbidden,
			expectedAbort: true,
		},
		{
			name:          "上下文中无角色信息",
			userRole:      "",
			requiredRole:  "admin",
			expectedCode:  http.StatusUnauthorized,
			expectedAbort: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 创建测试上下文
			w := httptest.NewRecorder()
			c, _ := gin.CreateTestContext(w)
			c.Request = httptest.NewRequest("GET", "/api/v1/admin", nil)

			// 设置用户角色
			if tt.userRole != "" {
				c.Set(middleware.UserRolesKey, []string{tt.userRole})
			}

			// 调用中间件
			middleware.RequireRole(tt.requiredRole, logger)(c)

			// 验证结果
			if tt.expectedAbort {
				assert.True(t, c.IsAborted())
				assert.Equal(t, tt.expectedCode, w.Code)
			} else {
				assert.False(t, c.IsAborted())
			}
		})
	}
} 