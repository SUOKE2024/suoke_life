package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/neo4j/neo4j-go-driver/v4/neo4j"
)

type KnowledgeNode struct {
	ID        string   `json:"id"`
	Name      string   `json:"name"`
	Type      string   `json:"type"`
	Attributes map[string]interface{} `json:"attributes"`
	Relations []Relation `json:"relations,omitempty"`
}

type Relation struct {
	Type string `json:"type"`
	TargetID string `json:"targetId"`
	TargetName string `json:"targetName"`
	Properties map[string]interface{} `json:"properties,omitempty"`
}

type Neo4jConfig struct {
	URI      string
	Username string
	Password string
}

func main() {
	// 设置Gin模式
	gin.SetMode(gin.ReleaseMode)

	// 创建路由
	r := gin.Default()

	// 健康检查
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status": "ok",
			"service": "knowledge-graph-service",
			"version": "1.0.0",
		})
	})

	// Neo4j配置
	neo4jConfig := Neo4jConfig{
		URI:      getEnvOrDefault("NEO4J_URI", "neo4j://localhost:7687"),
		Username: getEnvOrDefault("NEO4J_USERNAME", "neo4j"),
		Password: getEnvOrDefault("NEO4J_PASSWORD", "password"),
	}

	// API组
	api := r.Group("/api")
	{
		// 中医知识节点相关接口
		api.GET("/tcm/nodes", func(c *gin.Context) {
			nodes := []KnowledgeNode{
				{
					ID:   "1",
					Name: "肝",
					Type: "脏腑",
					Attributes: map[string]interface{}{
						"description": "肝藏血，主疏泄",
						"category": "五脏",
					},
				},
				{
					ID:   "2",
					Name: "心",
					Type: "脏腑",
					Attributes: map[string]interface{}{
						"description": "心主血脉，藏神",
						"category": "五脏",
					},
				},
			}
			c.JSON(200, nodes)
		})

		// 获取单个知识节点
		api.GET("/nodes/:id", func(c *gin.Context) {
			id := c.Param("id")
			
			// 模拟从数据库获取节点
			node := KnowledgeNode{
				ID:   id,
				Name: "示例节点-" + id,
				Type: "中医概念",
				Attributes: map[string]interface{}{
					"description": "这是一个示例节点",
				},
				Relations: []Relation{
					{
						Type: "关联",
						TargetID: "related-1",
						TargetName: "相关概念1",
					},
				},
			}
			
			c.JSON(200, node)
		})

		// 创建知识节点
		api.POST("/nodes", func(c *gin.Context) {
			var node KnowledgeNode
			if err := c.ShouldBindJSON(&node); err != nil {
				c.JSON(400, gin.H{"error": err.Error()})
				return
			}

			// 模拟创建节点
			node.ID = "new-id-123"
			
			c.JSON(201, node)
		})
	}

	// 启动服务器
	port := getEnvOrDefault("PORT", "8080")
	log.Printf("知识图谱服务启动于端口: %s\n", port)
	if err := r.Run(":" + port); err != nil {
		log.Fatalf("无法启动服务器: %v", err)
	}
}

// 从环境变量获取配置，如果不存在则使用默认值
func getEnvOrDefault(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

// 创建Neo4j会话 - 实际项目中会使用
func createNeo4jSession(config Neo4jConfig) (neo4j.Session, error) {
	driver, err := neo4j.NewDriver(
		config.URI,
		neo4j.BasicAuth(config.Username, config.Password, ""),
	)
	if err != nil {
		return nil, fmt.Errorf("无法创建Neo4j驱动: %w", err)
	}
	
	return driver.NewSession(neo4j.SessionConfig{
		AccessMode: neo4j.AccessModeWrite,
	}), nil
} 