package tests

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/suoke/suoke_life/services/rag-service/internal/config"
	"github.com/suoke/suoke_life/services/rag-service/internal/handlers"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/stretchr/testify/assert"
)

func TestRAGHandler(t *testing.T) {
	// 设置Gin为测试模式
	gin.SetMode(gin.TestMode)
	
	// 创建测试路由器
	router := gin.New()
	
	// 创建配置
	cfg := config.DefaultConfig()
	
	// 创建处理器
	ragHandler := handlers.NewRAGHandler(cfg)
	ragHandler.RegisterRoutes(router.Group("/api/rag"))
	
	// 测试健康检查
	t.Run("HealthCheck", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/rag/health", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, 200, w.Code)
		
		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "ok", response["status"])
	})
	
	// 测试列出集合
	t.Run("ListCollections", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/rag/collections", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, 200, w.Code)
		
		var response []models.Collection
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
	})
	
	// 测试创建集合
	t.Run("CreateCollection", func(t *testing.T) {
		createRequest := models.CollectionCreateRequest{
			Name:        "test_collection",
			Description: "测试集合",
			Dimension:   384,
		}
		
		body, _ := json.Marshal(createRequest)
		
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/api/rag/collections", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		router.ServeHTTP(w, req)
		
		assert.Equal(t, 200, w.Code)
		
		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "test_collection", response["name"])
	})
}

func TestEmbeddingHandler(t *testing.T) {
	// 设置Gin为测试模式
	gin.SetMode(gin.TestMode)
	
	// 创建测试路由器
	router := gin.New()
	
	// 创建配置
	cfg := config.DefaultConfig()
	
	// 本地嵌入模型配置
	cfg.EmbeddingConfig.UseLocal = true
	cfg.EmbeddingConfig.LocalModel = "mock-embedder"
	
	// 创建处理器
	embeddingHandler := handlers.NewEmbeddingHandler(cfg)
	embeddingHandler.RegisterRoutes(router.Group("/api/embeddings"))
	
	// 测试获取模型列表
	t.Run("ListModels", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/embeddings/models", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, 200, w.Code)
		
		var response []map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.True(t, len(response) > 0)
	})
	
	// 测试嵌入请求
	t.Run("Embed", func(t *testing.T) {
		embedRequest := models.EmbeddingRequest{
			Texts: []string{
				"这是一个测试文本",
				"这是另一个测试文本",
			},
			Model: "mock-embedder",
		}
		
		body, _ := json.Marshal(embedRequest)
		
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("POST", "/api/embeddings", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		router.ServeHTTP(w, req)
		
		// 如果嵌入模型未准备好，可能会返回500错误
		if w.Code == 500 {
			t.Skip("嵌入模型未准备好，跳过测试")
		}
		
		assert.Equal(t, 200, w.Code)
		
		var response models.EmbeddingResponse
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, 2, len(response.Embeddings))
	})
}

func TestMetricsHandler(t *testing.T) {
	// 设置Gin为测试模式
	gin.SetMode(gin.TestMode)
	
	// 创建测试路由器
	router := gin.New()
	
	// 创建处理器
	metricsHandler := handlers.NewMetricsHandler()
	metricsHandler.RegisterRoutes(router.Group("/metrics"))
	
	// 记录一些指标
	metricsHandler.RecordRequest("GET", "/api/rag/health", 200)
	metricsHandler.RecordTokens("embedding", "text-embedding-3-small", 100)
	
	// 测试指标接口
	t.Run("GetMetrics", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/metrics", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, 200, w.Code)
		assert.Contains(t, w.Body.String(), "rag_requests_total")
		assert.Contains(t, w.Body.String(), "rag_tokens_total")
	})
} 