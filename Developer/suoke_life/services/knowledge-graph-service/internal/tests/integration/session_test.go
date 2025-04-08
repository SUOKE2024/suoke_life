package integration

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	
	"knowledge-graph-service/internal/config"
	"knowledge-graph-service/internal/api/handlers"
)

var (
	testServer *httptest.Server
	testClient *http.Client
)

func init() {
	// 初始化测试模式
	gin.SetMode(gin.TestMode)
	
	// 创建路由器
	router := gin.New()
	router.Use(gin.Recovery())
	
	// 注册API路由
	router.POST("/api/v1/sessions", handlers.CreateSession)
	
	// 创建测试服务器
	testServer = httptest.NewServer(router)
	testClient = testServer.Client()
}

// 测试创建会话API
func TestCreateSession(t *testing.T) {
	// 创建测试请求数据
	requestBody := map[string]interface{}{
		"userId": "test-user",
		"title":  "Test Session",
	}
	jsonData, _ := json.Marshal(requestBody)

	// 发送POST请求
	resp, err := testClient.Post(
		testServer.URL+"/api/v1/sessions",
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)

	// 验证响应
	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	resp.Body.Close()
	assert.NoError(t, err)
	assert.Contains(t, response, "message")
} 