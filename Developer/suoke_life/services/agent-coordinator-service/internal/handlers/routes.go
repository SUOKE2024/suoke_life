package handlers

import (
	"github.com/gin-gonic/gin"
	"github.com/suoke-life/agent-coordinator-service/internal/middleware"
)

// RegisterRoutes 注册所有HTTP路由
func RegisterRoutes(r *gin.Engine) {
	// 初始化会话服务
	InitSessionService()

	// 健康检查路由
	r.GET("/health", HealthCheck)
	r.GET("/healthz", HealthCheck)

	// API V1 路由组
	v1 := r.Group("/api/v1")
	{
		// 会话路由
		sessions := v1.Group("/sessions")
		{
			sessions.POST("", middleware.JWTAuthSkip(), CreateSession)
			sessions.GET("", middleware.JWTAuthSkip(), GetSessions)
			sessions.GET("/:sessionId", middleware.JWTAuthSkip(), GetSessionByID)
			// 暂时注释掉未实现的路由
			//sessions.PUT("/:sessionId", UpdateSession)
			//sessions.DELETE("/:sessionId", DeleteSession)
		}

		// 以下路由已被注释，等待实现
		/*
		// 会话消息路由
		sessions.GET("/:sessionId/messages", GetSessionMessages)
		sessions.POST("/:sessionId/messages", AddSessionMessage)

		// 工作流路由
		workflows := v1.Group("/workflows")
		{
			workflows.POST("", CreateWorkflow)
			workflows.GET("/:workflowId", GetWorkflow)
		}

		// 任务路由
		tasks := v1.Group("/tasks")
		{
			tasks.POST("", CreateTask)
			tasks.GET("/:taskId", GetTask)
			tasks.PUT("/:taskId", UpdateTask)
		}

		// 知识图谱路由
		knowledge := v1.Group("/knowledge")
		{
			knowledge.POST("/query", QueryKnowledge)
			knowledge.POST("/ingest", IngestKnowledge)
			knowledge.GET("/entities", ListEntities)
			knowledge.GET("/entities/:entityId", GetEntity)
		}
		*/
	}
}