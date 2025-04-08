package tests

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/suoke-life/agent-coordinator-service/internal/handlers"
	"github.com/suoke-life/agent-coordinator-service/internal/models"
)

// 初始化测试用会话服务
func initTestSessionService() {
	handlers.InitSessionService()
}

// 创建测试用的Gin引擎
func setupTestRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.Use(gin.Recovery())
	
	// 初始化会话服务
	initTestSessionService()
	
	// 注册会话相关路由
	r.POST("/api/v1/sessions", handlers.CreateSession)
	r.GET("/api/v1/sessions", handlers.GetSessions)
	r.GET("/api/v1/sessions/:sessionId", handlers.GetSessionByID)
	
	return r
}

// TestSessionCreation 测试会话创建功能
func TestSessionCreation(t *testing.T) {
	r := setupTestRouter()
	
	// 创建请求体
	reqBody := models.CreateSessionRequest{
		UserID: "test-user-123",
		Title:  "测试会话",
	}
	jsonData, _ := json.Marshal(reqBody)
	
	// 创建请求
	req, _ := http.NewRequest("POST", "/api/v1/sessions", bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")
	
	// 执行请求
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	
	// 检查响应
	assert.Equal(t, http.StatusOK, w.Code)
	
	// 解析响应
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	
	// 验证
	assert.Nil(t, err)
	assert.Equal(t, "会话创建成功", response["message"])
	assert.NotNil(t, response["sessionId"])
	assert.NotNil(t, response["session"])
}

// TestSessionRetrieval 测试获取会话列表功能
func TestSessionRetrieval(t *testing.T) {
	r := setupTestRouter()
	
	// 先创建一个会话
	userID := "test-user-456"
	createSession(t, r, userID, "测试会话")
	
	// 请求会话列表
	req, _ := http.NewRequest("GET", fmt.Sprintf("/api/v1/sessions?userId=%s", userID), nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	
	// 检查响应
	assert.Equal(t, http.StatusOK, w.Code)
	
	// 解析响应
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	
	// 验证
	assert.Nil(t, err)
	assert.Equal(t, "获取会话列表成功", response["message"])
	assert.Equal(t, userID, response["userId"])
	
	// 检查会话列表
	sessions, ok := response["sessions"].([]interface{})
	assert.True(t, ok)
	assert.GreaterOrEqual(t, len(sessions), 1)
}

// TestSessionDetails 测试获取会话详情功能
func TestSessionDetails(t *testing.T) {
	r := setupTestRouter()
	
	// 创建一个会话并获取ID
	userID := "test-user-789"
	sessionID := createSession(t, r, userID, "详情测试会话")
	
	// 请求会话详情
	req, _ := http.NewRequest("GET", fmt.Sprintf("/api/v1/sessions/%s", sessionID), nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	
	// 检查响应
	assert.Equal(t, http.StatusOK, w.Code)
	
	// 解析响应
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	
	// 验证
	assert.Nil(t, err)
	assert.Equal(t, "获取会话详情成功", response["message"])
	
	// 验证会话和消息
	session, ok := response["session"].(map[string]interface{})
	assert.True(t, ok)
	assert.Equal(t, sessionID, session["id"])
	assert.Equal(t, userID, session["userId"])
	
	messages, ok := response["messages"].([]interface{})
	assert.True(t, ok)
	assert.NotNil(t, messages)
}

// TestInvalidSessionID 测试无效会话ID的情况
func TestInvalidSessionID(t *testing.T) {
	r := setupTestRouter()
	
	// 请求不存在的会话
	req, _ := http.NewRequest("GET", "/api/v1/sessions/non-existent-id", nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	
	// 检查响应
	assert.Equal(t, http.StatusNotFound, w.Code)
	
	// 解析响应
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	
	// 验证
	assert.Nil(t, err)
	assert.Equal(t, "SESSION_NOT_FOUND", response["code"])
}

// 辅助函数 - 创建会话并返回会话ID
func createSession(t *testing.T, r *gin.Engine, userID string, title string) string {
	// 创建请求体
	reqBody := models.CreateSessionRequest{
		UserID: userID,
		Title:  title,
	}
	jsonData, _ := json.Marshal(reqBody)
	
	// 创建请求
	req, _ := http.NewRequest("POST", "/api/v1/sessions", bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")
	
	// 执行请求
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	
	// 检查响应
	assert.Equal(t, http.StatusOK, w.Code)
	
	// 解析响应
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	
	// 返回会话ID
	return response["sessionId"].(string)
}