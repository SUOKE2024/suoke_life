package routes

import (
	"knowledge-graph-service/internal/api/handlers"
	"knowledge-graph-service/internal/api/middleware"
	"knowledge-graph-service/pkg/logger"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

// RegisterRoutes 注册所有API路由
func RegisterRoutes(router *gin.Engine, logger *zap.Logger) {
	// 全局中间件
	router.Use(middleware.RequestTracker(logger))
	router.Use(middleware.RecoveryWithLogger(logger))
	router.Use(middleware.CustomErrorHandler(logger))
	router.Use(middleware.CORSMiddleware())

	// 健康检查路由
	router.GET("/health", handlers.HealthCheck)

	// API版本路由组
	v1 := router.Group("/api/v1")
	{
		// 知识节点相关路由
		nodes := v1.Group("/nodes")
		{
			// JWT认证中间件
			jwtConfig := middleware.DefaultJWTConfig()
			authMiddleware := middleware.JWTAuth(jwtConfig, logger)
			
			// 公开路由
			nodes.GET("", handlers.ListNodes)
			nodes.GET("/:id", handlers.GetNodeByID)
			nodes.GET("/search", handlers.SearchNodes)
			
			// 需要认证的路由
			nodes.Use(authMiddleware)
			nodes.POST("", handlers.CreateNode)
			nodes.PUT("/:id", handlers.UpdateNode)
			nodes.DELETE("/:id", handlers.DeleteNode)
			
			// 需要管理员权限的路由
			adminRoutes := nodes.Group("/admin")
			adminRoutes.Use(middleware.RequireRole("admin", logger))
			adminRoutes.POST("/batch", handlers.BatchCreateNodes)
			adminRoutes.DELETE("/batch", handlers.BatchDeleteNodes)
		}

		// 知识关系相关路由
		relations := v1.Group("/relations")
		{
			// JWT认证中间件
			jwtConfig := middleware.DefaultJWTConfig()
			authMiddleware := middleware.JWTAuth(jwtConfig, logger)
			
			// 公开路由
			relations.GET("", handlers.ListRelations)
			relations.GET("/:id", handlers.GetRelationByID)
			relations.GET("/search", handlers.SearchRelations)
			
			// 需要认证的路由
			relations.Use(authMiddleware)
			relations.POST("", handlers.CreateRelation)
			relations.PUT("/:id", handlers.UpdateRelation)
			relations.DELETE("/:id", handlers.DeleteRelation)
			
			// 需要管理员权限的路由
			adminRoutes := relations.Group("/admin")
			adminRoutes.Use(middleware.RequireRole("admin", logger))
			adminRoutes.POST("/batch", handlers.BatchCreateRelations)
			adminRoutes.DELETE("/batch", handlers.BatchDeleteRelations)
		}

		// 知识图谱相关路由
		graphs := v1.Group("/graphs")
		{
			// JWT认证中间件
			jwtConfig := middleware.DefaultJWTConfig()
			authMiddleware := middleware.JWTAuth(jwtConfig, logger)
			
			// 公开路由
			graphs.GET("/:id", handlers.GetGraphByID)
			graphs.GET("/search", handlers.SearchGraphs)
			
			// 需要认证的路由
			graphs.Use(authMiddleware)
			graphs.POST("", handlers.CreateGraph)
			graphs.PUT("/:id", handlers.UpdateGraph)
			graphs.DELETE("/:id", handlers.DeleteGraph)
			
			// 图谱查询和分析路由
			query := graphs.Group("/:id/query")
			query.GET("/path", handlers.FindPath)
			query.GET("/neighbors", handlers.GetNeighbors)
			query.GET("/subgraph", handlers.GetSubgraph)
		}

		// 用户认证路由
		auth := v1.Group("/auth")
		{
			auth.POST("/login", handlers.Login)
			auth.POST("/register", handlers.Register)
			
			// 需要认证的路由
			jwtConfig := middleware.DefaultJWTConfig()
			authMiddleware := middleware.JWTAuth(jwtConfig, logger)
			auth.Use(authMiddleware)
			auth.POST("/refresh", handlers.RefreshToken)
			auth.POST("/logout", handlers.Logout)
		}

		// 用户管理路由
		users := v1.Group("/users")
		{
			// JWT认证中间件
			jwtConfig := middleware.DefaultJWTConfig()
			authMiddleware := middleware.JWTAuth(jwtConfig, logger)
			
			users.Use(authMiddleware)
			users.GET("/me", handlers.GetCurrentUser)
			users.PUT("/me", handlers.UpdateCurrentUser)
			
			// 管理员路由
			adminRoutes := users.Group("/admin")
			adminRoutes.Use(middleware.RequireRole("admin", logger))
			adminRoutes.GET("", handlers.ListUsers)
			adminRoutes.GET("/:id", handlers.GetUserByID)
			adminRoutes.POST("", handlers.CreateUser)
			adminRoutes.PUT("/:id", handlers.UpdateUser)
			adminRoutes.DELETE("/:id", handlers.DeleteUser)
		}

		// 知识查询路由
		query := v1.Group("/query")
		{
			query.POST("/semantic", handlers.SemanticSearch)
			query.POST("/vector", handlers.VectorSearch)
			query.POST("/cypher", handlers.CypherQuery)
		}
	}
}

// SetupSwagger 设置Swagger文档
func SetupSwagger(router *gin.Engine) {
	// Swagger路由
	router.GET("/swagger/*any", handlers.Swagger)
}

// SetupLogging 设置日志
func SetupLogging() *zap.Logger {
	return logger.NewLogger(true)
} 