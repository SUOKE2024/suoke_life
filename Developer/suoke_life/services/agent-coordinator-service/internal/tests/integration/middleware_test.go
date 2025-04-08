package integration

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"

	"github.com/suoke-life/agent-coordinator-service/internal/middleware"
)

// TestJWTAuthMiddleware 测试JWT身份验证中间件
func TestJWTAuthMiddleware(t *testing.T) {
	// 创建一个新的测试路由器
	gin.SetMode(gin.TestMode)
	router := gin.New()
	router.Use(middleware.JWTAuthMiddleware())
	
	// 添加一个测试路由
	router.GET("/protected", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "访问成功",
			"userId":  c.GetString("userId"),
		})
	})
	
	// 创建测试服务器
	server := httptest.NewServer(router)
	defer server.Close()
	client := server.Client()

	// 测试场景1：没有提供Authorization头
	t.Run("NoAuthHeader", func(t *testing.T) {
		req, _ := http.NewRequest("GET", server.URL+"/protected", nil)
		resp, err := client.Do(req)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
		resp.Body.Close()
	})

	// 测试场景2：提供无效的Token格式
	t.Run("InvalidTokenFormat", func(t *testing.T) {
		req, _ := http.NewRequest("GET", server.URL+"/protected", nil)
		req.Header.Set("Authorization", "InvalidFormat")
		resp, err := client.Do(req)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
		resp.Body.Close()
	})

	// 测试场景3：提供无效的Token
	t.Run("InvalidToken", func(t *testing.T) {
		req, _ := http.NewRequest("GET", server.URL+"/protected", nil)
		req.Header.Set("Authorization", "Bearer invalid-token")
		resp, err := client.Do(req)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusUnauthorized, resp.StatusCode)
		resp.Body.Close()
	})

	// 测试场景4：提供有效的Token
	t.Run("ValidToken", func(t *testing.T) {
		req, _ := http.NewRequest("GET", server.URL+"/protected", nil)
		req.Header.Set("Authorization", "Bearer test-token")
		resp, err := client.Do(req)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, resp.StatusCode)
		
		// 解析响应
		var response map[string]interface{}
		err = json.NewDecoder(resp.Body).Decode(&response)
		resp.Body.Close()
		assert.NoError(t, err)
		assert.Equal(t, "访问成功", response["message"])
		assert.Equal(t, "auth-user-id", response["userId"])
	})
}