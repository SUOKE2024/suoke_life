package handlers

import (
	"github.com/suoke/suoke_life/services/rag-service/internal/config"
	"github.com/suoke/suoke_life/services/rag-service/internal/embeddings"
	"github.com/suoke/suoke_life/services/rag-service/internal/rag"
	"github.com/suoke/suoke_life/services/rag-service/internal/storage/vector_store"
)

// NewRAGHandler 创建新的RAG处理器
func NewRAGHandler(cfg *config.Config) RAGHandler {
	// 创建指标处理器
	metricsHandler := NewMetricsHandler()

	// 创建嵌入模型
	var embedder embeddings.TextEmbedder
	if cfg.EmbeddingConfig.UseLocal {
		// 使用本地嵌入模型
		embedder, _ = embeddings.NewLocalEmbedder(
			cfg.EmbeddingConfig.LocalModelPath,
			cfg.EmbeddingConfig.ModelName,
			cfg.EmbeddingConfig.Dimensions,
			cfg.AppConfig.TempDir,
		)
	} else {
		// 使用OpenAI嵌入模型
		embedder, _ = embeddings.NewOpenAIEmbedder(
			cfg.EmbeddingConfig.OpenAIKey,
			cfg.EmbeddingConfig.ModelName,
			cfg.EmbeddingConfig.Dimensions,
		)
	}

	// 创建向量存储
	var vectorStore vector_store.VectorStore
	if cfg.VectorConfig.Type == "milvus" {
		// 使用Milvus向量存储
		vectorStore, _ = vector_store.NewMilvusStore(
			cfg.VectorConfig.Host,
			cfg.VectorConfig.Port,
			cfg.VectorConfig.Username,
			cfg.VectorConfig.Password,
			embedder.GetDimensions(),
		)
	} else {
		// 使用本地向量存储
		vectorStore, _ = vector_store.NewLocalStore(
			cfg.VectorConfig.DataPath,
			embedder.GetDimensions(),
		)
	}

	// 创建RAG服务
	ragService := rag.NewDefaultRAGService(
		vectorStore,
		embedder,
		cfg.RagConfig.TopK,
		cfg.RagConfig.ContextWindow,
		metricsHandler,
	)

	// 创建RAG处理器
	return newRAGHandler(ragService, metricsHandler)
}

// NewEmbeddingHandler 创建新的嵌入模型处理器
func NewEmbeddingHandler(cfg *config.Config) EmbeddingHandler {
	// 创建指标处理器
	metricsHandler := NewMetricsHandler()

	// 创建嵌入模型列表
	embedders := make(map[string]embeddings.TextEmbedder)

	// 添加OpenAI嵌入模型
	if cfg.EmbeddingConfig.OpenAIKey != "" {
		// OpenAI小模型
		smallEmbedder, _ := embeddings.NewOpenAIEmbedder(
			cfg.EmbeddingConfig.OpenAIKey,
			"text-embedding-3-small",
			1536,
		)
		embedders["text-embedding-3-small"] = smallEmbedder

		// OpenAI大模型
		largeEmbedder, _ := embeddings.NewOpenAIEmbedder(
			cfg.EmbeddingConfig.OpenAIKey,
			"text-embedding-3-large",
			3072,
		)
		embedders["text-embedding-3-large"] = largeEmbedder

		// OpenAI Ada模型(兼容性)
		adaEmbedder, _ := embeddings.NewOpenAIEmbedder(
			cfg.EmbeddingConfig.OpenAIKey,
			"text-embedding-ada-002",
			1536,
		)
		embedders["text-embedding-ada-002"] = adaEmbedder
	}

	// 添加本地嵌入模型
	if cfg.EmbeddingConfig.UseLocal {
		localEmbedder, _ := embeddings.NewLocalEmbedder(
			cfg.EmbeddingConfig.LocalModelPath,
			"all-MiniLM-L6-v2",
			384,
			cfg.AppConfig.TempDir,
		)
		embedders["all-MiniLM-L6-v2"] = localEmbedder
	}

	// 创建嵌入模型处理器
	return newEmbeddingHandler(embedders, cfg.EmbeddingConfig.ModelName, metricsHandler)
} 