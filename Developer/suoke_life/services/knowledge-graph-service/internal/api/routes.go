package api

import (
	"github.com/gin-gonic/gin"
	
	"knowledge-graph-service/internal/api/handlers"
	"knowledge-graph-service/internal/api/middleware"
)

// SetupRoutes 配置API路由
func SetupRoutes(
	router *gin.Engine,
	nodeHandler *handlers.NodeHandler,
	relationshipHandler *handlers.RelationshipHandler,
	graphHandler *handlers.GraphHandler,
	constitutionHandler *handlers.ConstitutionHandler,
) {
	// 添加全局中间件
	router.Use(middleware.Logger())
	router.Use(middleware.ErrorHandler())
	router.Use(middleware.Cors())
	
	// 健康检查 - 已移至main.go处理，避免重复注册路由
	// router.GET("/health", func(c *gin.Context) {
	// 	c.JSON(200, gin.H{
	// 		"status": "up",
	// 		"service": "knowledge-graph-service",
	// 	})
	// })
	
	// API版本
	v1 := router.Group("/api/v1")
	{
		// 节点相关路由
		nodes := v1.Group("/nodes")
		{
			nodes.GET("", nodeHandler.QueryNodes)
			nodes.POST("", nodeHandler.CreateNode)
			nodes.GET("/:id", nodeHandler.GetNode)
			nodes.PUT("/:id", nodeHandler.UpdateNode)
			nodes.DELETE("/:id", nodeHandler.DeleteNode)
			nodes.GET("/search", nodeHandler.SearchNodes)
		}
		
		// 关系相关路由
		relationships := v1.Group("/relationships")
		{
			relationships.POST("", relationshipHandler.CreateRelationship)
			relationships.GET("/:id", relationshipHandler.GetRelationship)
			relationships.PUT("/:id", relationshipHandler.UpdateRelationship)
			relationships.DELETE("/:id", relationshipHandler.DeleteRelationship)
			relationships.GET("/nodes/:nodeId", relationshipHandler.GetRelationshipsByNodeID)
		}
		
		// 图表相关路由
		graph := v1.Group("/graph")
		{
			graph.GET("/relationships", graphHandler.GetRelationshipTypes)
			graph.GET("/nodes/:id/neighborhood", graphHandler.GetNodeNeighborhood)
			graph.GET("/search", graphHandler.SearchGraph)
			graph.GET("/path", graphHandler.FindPath)
		}
		
		// 体质相关路由
		constitutions := v1.Group("/constitutions")
		{
			constitutions.POST("", constitutionHandler.CreateConstitution)
			constitutions.GET("", constitutionHandler.QueryConstitutions)
			constitutions.GET("/:id", constitutionHandler.GetConstitution)
			constitutions.GET("/:id/details", constitutionHandler.GetConstitutionWithRelations)
			constitutions.POST("/find", constitutionHandler.FindSuitableConstitutionBySymptoms)
			constitutions.POST("/:id/symptoms", constitutionHandler.LinkConstitutionToSymptom)
			constitutions.GET("/:id/organs", constitutionHandler.GetRelatedOrgans)
			constitutions.GET("/:id/suggestions", constitutionHandler.GetSuggestions)
		}
		
		// 中医特色API 
		tcm := v1.Group("/tcm")
		{
			// 脏腑之间的关系
			tcm.GET("/zangfu", graphHandler.GetTCMZangFuRelations)
			
			// 体质与脏腑的关系
			tcm.GET("/constitutions/zangfu", graphHandler.GetConstitutionZangFuRelations)
			
			// 体质与症状的关系
			tcm.GET("/constitutions/symptoms", graphHandler.GetConstitutionSymptomRelations)
		}
	}
} 