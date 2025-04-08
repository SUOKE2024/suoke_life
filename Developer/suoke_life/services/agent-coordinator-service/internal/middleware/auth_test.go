package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

// TestJWTAuthMiddleware 测试JWT身份验证中间件
func TestJWTAuthMiddleware(t *testing.T) {
	// 设置为测试模式
	gin.SetMode(gin.TestMode)

	// 测试场景1：没有提供Authorization头
	t.Run("NoAuthHeader", func(t *testing.T) {
		// 创建一个新的测试路由器
		router := gin.New()
		router.Use(JWTAuthMiddleware())
		
		// 添加一个测试路由
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"message": "access granted",
			})
		})
		
		// 创建一个测试请求
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		
		// 提交请求
		router.ServeHTTP(w, req)
		
		// 检查响应
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	// 测试场景2：提供无效的Token格式
	t.Run("InvalidTokenFormat", func(t *testing.T) {
		// 创建一个新的测试路由器
		router := gin.New()
		router.Use(JWTAuthMiddleware())
		
		// 添加一个测试路由
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"message": "access granted",
			})
		})
		
		// 创建一个测试请求
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set("Authorization", "InvalidFormat")
		
		// 提交请求
		router.ServeHTTP(w, req)
		
		// 检查响应
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	// 测试场景3：提供无效的Token
	t.Run("InvalidToken", func(t *testing.T) {
		// 创建一个新的测试路由器
		router := gin.New()
		router.Use(JWTAuthMiddleware())
		
		// 添加一个测试路由
		router.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"message": "access granted",
			})
		})
		
		// 创建一个测试请求
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set("Authorization", "Bearer invalid-token")
		
		// 提交请求
		router.ServeHTTP(w, req)
		
		// 检查响应
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	// 测试场景4：提供有效的Token
	t.Run("ValidToken", func(t *testing.T) {
		// 创建一个新的测试路由器
		router := gin.New()
		router.Use(JWTAuthMiddleware())
		
		// 添加一个测试路由
		router.GET("/test", func(c *gin.Context) {
			userId := c.GetString("userId")
			c.JSON(http.StatusOK, gin.H{
				"message": "access granted",
				"userId":  userId,
			})
		})
		
		// 创建一个测试请求
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set("Authorization", "Bearer test-token")
		
		// 提交请求
		router.ServeHTTP(w, req)
		
		// 检查响应
		assert.Equal(t, http.StatusOK, w.Code)
	})
}