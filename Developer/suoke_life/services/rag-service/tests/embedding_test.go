package tests

import (
	"context"
	"testing"
	
	"github.com/suoke/suoke_life/services/rag-service/internal/embeddings"
	"github.com/stretchr/testify/assert"
)

func TestCreateEmbedder(t *testing.T) {
	// 创建配置
	options := embeddings.EmbeddingOptions{
		Model:        "mock",
		Dimensions:   384,
		BatchSize:    16,
		UseLocal:     true,
		LocalModelPath: "./models/test-model",
	}
	
	// 创建嵌入模型
	embedder, err := embeddings.CreateEmbedder(options)
	assert.NoError(t, err, "创建嵌入模型失败")
	assert.NotNil(t, embedder, "嵌入模型为空")
	
	// 验证基本属性
	assert.Equal(t, 384, embedder.GetDimensions(), "嵌入维度不正确")
	assert.Equal(t, "mock-embedder", embedder.GetModelName(), "模型名称不正确")
}

func TestLocalEmbedder(t *testing.T) {
	// 跳过需要资源的测试
	if testing.Short() {
		t.Skip("跳过需要资源的测试")
	}
	
	// 创建嵌入模型配置
	options := embeddings.EmbeddingOptions{
		Model:        "local",
		Dimensions:   384,
		BatchSize:    8,
		UseLocal:     true,
		LocalModelPath: "./models/test-model",
	}
	
	embedder, err := embeddings.NewLocalEmbedder(options)
	assert.NoError(t, err, "创建本地嵌入模型失败")
	
	// 创建上下文
	ctx := context.Background()
	
	// 测试单条文本嵌入
	query := "这是一个测试查询"
	vector, err := embedder.EmbedQuery(ctx, query)
	assert.NoError(t, err, "嵌入查询失败")
	assert.NotEmpty(t, vector, "嵌入向量为空")
	
	// 验证向量维度
	assert.Equal(t, 384, len(vector), "嵌入向量维度不正确")
	
	// 测试批量文本嵌入
	texts := []string{
		"第一个文档",
		"第二个文档",
	}
	
	vectors, err := embedder.EmbedDocuments(ctx, texts)
	assert.NoError(t, err, "嵌入文档失败")
	assert.Equal(t, 2, len(vectors), "嵌入向量数量不匹配")
	
	// 验证每个向量维度
	for _, vec := range vectors {
		assert.Equal(t, 384, len(vec), "嵌入向量维度不正确")
	}
	
	// 测试批处理大小
	assert.Equal(t, 8, embedder.BatchSize(), "批处理大小不正确")
	
	// 测试Close方法
	assert.NoError(t, embedder.Close(), "关闭模型失败")
}

func TestMockEmbedder(t *testing.T) {
	// 创建嵌入模型配置
	options := embeddings.EmbeddingOptions{
		Model:      "mock",
		Dimensions: 4,
	}
	
	// 创建嵌入模型
	embedder, err := embeddings.NewMockEmbedder(options)
	assert.NoError(t, err, "创建模拟嵌入模型失败")
	
	// 创建上下文
	ctx := context.Background()
	
	// 测试单条文本嵌入
	query := "测试查询"
	vector, err := embedder.EmbedQuery(ctx, query)
	assert.NoError(t, err, "嵌入查询失败")
	assert.Equal(t, 4, len(vector), "嵌入向量维度不正确")
	
	// 测试批量文本嵌入
	texts := []string{
		"文档1",
		"文档2",
	}
	
	vectors, err := embedder.EmbedDocuments(ctx, texts)
	assert.NoError(t, err, "嵌入文档失败")
	assert.Equal(t, 2, len(vectors), "嵌入向量数量不匹配")
	assert.Equal(t, 4, len(vectors[0]), "嵌入向量维度不正确")
	
	// 测试Token计数
	tokenCount := embedder.CountTokens("测试")
	assert.Greater(t, tokenCount, 0, "Token计数应该大于0")
} 