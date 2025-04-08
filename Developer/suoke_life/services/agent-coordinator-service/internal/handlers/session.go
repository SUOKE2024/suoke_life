package handlers

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/suoke-life/agent-coordinator-service/internal/models"
	"github.com/suoke-life/agent-coordinator-service/internal/services"
)

// sessionService 全局会话服务实例
var sessionService services.SessionService

// InitSessionService 初始化会话服务
func InitSessionService() {
	sessionService = services.NewInMemorySessionService()
	log.Println("会话服务已初始化")
}

// CreateSession 创建新的会话
// @Summary 创建新的会话
// @Description 创建一个新的用户会话
// @Tags sessions
// @Accept json
// @Produce json
// @Param request body models.CreateSessionRequest true "会话创建请求"
// @Success 200 {object} map[string]interface{} "成功响应"
// @Failure 400 {object} map[string]interface{} "无效请求"
// @Failure 500 {object} map[string]interface{} "服务器错误"
// @Router /api/v1/sessions [post]
func CreateSession(c *gin.Context) {
	var request models.CreateSessionRequest

	if err := c.ShouldBindJSON(&request); err != nil {
		log.Printf("绑定JSON失败: %v", err)
		c.JSON(http.StatusBadRequest, gin.H{
			"message": "无效的请求参数",
			"error":   err.Error(),
			"code":    "INVALID_REQUEST",
		})
		return
	}

	// 调用会话服务创建会话
	session, err := sessionService.CreateSession(request)
	if err != nil {
		var statusCode int
		var errorCode string

		// 根据错误类型设置适当的状态码和错误代码
		switch err {
		case services.ErrInvalidSessionData:
			statusCode = http.StatusBadRequest
			errorCode = "INVALID_SESSION_DATA"
		default:
			statusCode = http.StatusInternalServerError
			errorCode = "SERVER_ERROR"
		}

		log.Printf("创建会话失败: %v", err)
		c.JSON(statusCode, gin.H{
			"message": "会话创建失败",
			"error":   err.Error(),
			"code":    errorCode,
		})
		return
	}

	// 返回成功响应
	log.Printf("会话创建成功: %s", session.ID)
	c.JSON(http.StatusOK, gin.H{
		"message":   "会话创建成功",
		"sessionId": session.ID,
		"session":   session,
	})
}

// GetSessions 获取用户会话列表
// @Summary 获取用户会话列表
// @Description 获取特定用户的所有会话
// @Tags sessions
// @Accept json
// @Produce json
// @Param userId query string true "用户ID"
// @Success 200 {object} map[string]interface{} "成功响应"
// @Failure 400 {object} map[string]interface{} "无效请求"
// @Failure 500 {object} map[string]interface{} "服务器错误"
// @Router /api/v1/sessions [get]
func GetSessions(c *gin.Context) {
	userId := c.Query("userId")
	if userId == "" {
		log.Println("获取会话失败: 缺少userId参数")
		c.JSON(http.StatusBadRequest, gin.H{
			"message": "缺少必要的userId参数",
			"code":    "MISSING_PARAMETER",
		})
		return
	}

	// 调用会话服务获取用户会话列表
	sessions, err := sessionService.GetSessionsByUserID(userId)
	if err != nil {
		log.Printf("获取会话列表失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"message": "获取会话列表失败",
			"error":   err.Error(),
			"code":    "SERVER_ERROR",
		})
		return
	}

	log.Printf("获取会话列表成功: 用户=%s, 会话数=%d", userId, len(sessions))
	c.JSON(http.StatusOK, gin.H{
		"message":  "获取会话列表成功",
		"userId":   userId,
		"sessions": sessions,
	})
}

// GetSessionByID 获取特定会话详情
// @Summary 获取会话详情
// @Description 获取特定会话的详细信息
// @Tags sessions
// @Accept json
// @Produce json
// @Param sessionId path string true "会话ID"
// @Success 200 {object} map[string]interface{} "成功响应"
// @Failure 400 {object} map[string]interface{} "无效请求"
// @Failure 404 {object} map[string]interface{} "会话不存在"
// @Failure 500 {object} map[string]interface{} "服务器错误"
// @Router /api/v1/sessions/{sessionId} [get]
func GetSessionByID(c *gin.Context) {
	sessionID := c.Param("sessionId")
	if sessionID == "" {
		log.Println("获取会话详情失败: 缺少sessionId参数")
		c.JSON(http.StatusBadRequest, gin.H{
			"message": "缺少必要的sessionId参数",
			"code":    "MISSING_PARAMETER",
		})
		return
	}

	// 调用会话服务获取会话详情
	session, err := sessionService.GetSessionByID(sessionID)
	if err != nil {
		var statusCode int
		var errorCode string

		// 根据错误类型设置适当的状态码和错误代码
		switch err {
		case services.ErrSessionNotFound:
			statusCode = http.StatusNotFound
			errorCode = "SESSION_NOT_FOUND"
		default:
			statusCode = http.StatusInternalServerError
			errorCode = "SERVER_ERROR"
		}

		log.Printf("获取会话详情失败: %v", err)
		c.JSON(statusCode, gin.H{
			"message": "获取会话详情失败",
			"error":   err.Error(),
			"code":    errorCode,
		})
		return
	}

	// 获取会话相关的消息
	messages, err := sessionService.GetSessionMessages(sessionID)
	if err != nil {
		log.Printf("获取会话消息失败: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"message": "获取会话消息失败",
			"error":   err.Error(),
			"code":    "SERVER_ERROR",
		})
		return
	}

	log.Printf("获取会话详情成功: %s", sessionID)
	c.JSON(http.StatusOK, gin.H{
		"message":  "获取会话详情成功",
		"session":  session,
		"messages": messages,
	})
}