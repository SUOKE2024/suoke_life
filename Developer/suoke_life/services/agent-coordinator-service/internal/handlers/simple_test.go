package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

// TestHealthCheck 测试健康检查API
func TestHealthCheck(t *testing.T) {
	// 设置为测试模式
	gin.SetMode(gin.TestMode)

	// 创建一个新的Gin引擎
	router := gin.New()
	router.GET("/health", HealthCheck)

	// 创建一个测试请求
	req, _ := http.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()

	// 提交请求
	router.ServeHTTP(w, req)

	// 检查响应
	assert.Equal(t, http.StatusOK, w.Code)
	assert.Contains(t, w.Body.String(), "ok")
	assert.Contains(t, w.Body.String(), "version")
}

// TestCreateSession 测试创建会话API
func TestCreateSession(t *testing.T) {
	// 设置为测试模式
	gin.SetMode(gin.TestMode)

	// 创建一个新的Gin引擎
	router := gin.New()
	router.POST("/api/v1/sessions", CreateSession)

	// 准备请求数据
	requestData := map[string]interface{}{
		"userId": "test-user",
		"title":  "Test Session",
	}
	jsonData, _ := json.Marshal(requestData)

	// 创建一个测试请求
	req, _ := http.NewRequest("POST", "/api/v1/sessions", bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	// 提交请求
	router.ServeHTTP(w, req)

	// 检查响应
	assert.Equal(t, http.StatusOK, w.Code)
	
	// 验证响应内容
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Contains(t, response, "message")
	assert.Contains(t, response, "sessionId")
}

// TestGetSessions 测试获取会话列表API
func TestGetSessions(t *testing.T) {
	// 设置为测试模式
	gin.SetMode(gin.TestMode)

	// 创建一个新的Gin引擎
	router := gin.New()
	router.GET("/api/v1/sessions", GetSessions)

	// 创建一个测试请求
	req, _ := http.NewRequest("GET", "/api/v1/sessions?userId=test-user", nil)
	w := httptest.NewRecorder()

	// 提交请求
	router.ServeHTTP(w, req)

	// 检查响应
	assert.Equal(t, http.StatusOK, w.Code)
	
	// 验证响应内容
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Contains(t, response, "message")
	assert.Contains(t, response, "userId")
	assert.Contains(t, response, "sessions")
	
	// 验证userId
	assert.Equal(t, "test-user", response["userId"])
	
	// 验证sessions数组
	sessions, ok := response["sessions"].([]interface{})
	assert.True(t, ok)
	assert.NotEmpty(t, sessions)
}

// TestGetSessionsWithoutUserId 测试获取会话列表API（缺少userId参数）
func TestGetSessionsWithoutUserId(t *testing.T) {
	// 设置为测试模式
	gin.SetMode(gin.TestMode)

	// 创建一个新的Gin引擎
	router := gin.New()
	router.GET("/api/v1/sessions", GetSessions)

	// 创建一个测试请求（不含userId参数）
	req, _ := http.NewRequest("GET", "/api/v1/sessions", nil)
	w := httptest.NewRecorder()

	// 提交请求
	router.ServeHTTP(w, req)

	// 检查响应
	assert.Equal(t, http.StatusBadRequest, w.Code)
	
	// 验证响应内容
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Contains(t, response, "message")
	assert.Contains(t, response["message"], "缺少必要的userId参数")
}
