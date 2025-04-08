package tests

import (
	"context"
	"testing"
	"time"

	"github.com/suoke/suoke_life/services/rag-service/go-src/embeddings"
	"github.com/suoke/suoke_life/services/rag-service/go-src/models"
	"github.com/suoke/suoke_life/services/rag-service/go-src/vector_store"
	"github.com/stretchr/testify/assert"
)

func TestInMemoryVectorStore(t *testing.T) {
	// 创建内存向量存储
	inMemoryStore := vector_store.NewInMemoryVectorStore()
	assert.NotNil(t, inMemoryStore, "创建内存向量存储失败")
	
	// 创建嵌入模型
	options := embeddings.EmbeddingOptions{
		Dimensions: 4,
	}
	mockEmbedder, err := embeddings.NewMockEmbedder(options)
	assert.NoError(t, err, "创建嵌入模型失败")
	
	// 创建上下文
	ctx := context.Background()
	
	// 初始化向量存储
	err = inMemoryStore.Initialize(ctx)
	assert.NoError(t, err, "初始化向量存储失败")
	
	// 测试集合创建
	err = inMemoryStore.CreateCollection(ctx, "test_collection", 4, "测试集合")
	assert.NoError(t, err, "创建集合失败")
	
	// 检查集合列表
	collections, err := inMemoryStore.ListCollections(ctx)
	assert.NoError(t, err, "获取集合列表失败")
	assert.Len(t, collections, 1, "集合数量不正确")
	assert.Equal(t, "test_collection", collections[0].Name, "集合名称不正确")
	
	// 检查集合是否存在
	exists, err := inMemoryStore.CollectionExists(ctx, "test_collection")
	assert.NoError(t, err, "检查集合存在失败")
	assert.True(t, exists, "集合应该存在")
	
	// 获取集合信息
	collection, err := inMemoryStore.GetCollection(ctx, "test_collection")
	assert.NoError(t, err, "获取集合信息失败")
	assert.Equal(t, "test_collection", collection.Name, "集合名称不正确")
	assert.Equal(t, 4, collection.Dimension, "集合维度不正确")
	
	// 创建测试文档
	docs := []models.Document{
		{
			ID:         "doc1",
			Content:    "这是第一个测试文档",
			Collection: "test_collection",
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
			Metadata: map[string]interface{}{
				"type": "test",
			},
		},
		{
			ID:         "doc2",
			Content:    "这是第二个测试文档",
			Collection: "test_collection",
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
			Metadata: map[string]interface{}{
				"type": "test",
			},
		},
	}
	
	// 为文档生成嵌入向量
	for i := range docs {
		vector, err := mockEmbedder.EmbedQuery(ctx, docs[i].Content)
		assert.NoError(t, err, "生成文档向量失败")
		docs[i].Vector = vector
	}
	
	// 添加文档
	ids, err := inMemoryStore.UpsertDocuments(ctx, "test_collection", docs)
	assert.NoError(t, err, "添加文档失败")
	assert.Len(t, ids, 2, "返回的文档ID数量不正确")
	
	// 获取单个文档
	doc, err := inMemoryStore.GetDocument(ctx, "test_collection", "doc1")
	assert.NoError(t, err, "获取文档失败")
	assert.Equal(t, "doc1", doc.ID, "文档ID不正确")
	
	// 查询向量
	queryText := "测试文档"
	queryVector, err := mockEmbedder.EmbedQuery(ctx, queryText)
	assert.NoError(t, err, "生成查询向量失败")
	
	// 执行相似性搜索
	results, err := inMemoryStore.SimilaritySearch(ctx, "test_collection", queryVector, 2, nil, true)
	assert.NoError(t, err, "搜索失败")
	assert.Len(t, results, 2, "搜索结果数量不正确")
	
	// 执行带分数的相似性搜索
	resultsWithScore, err := inMemoryStore.SimilaritySearchWithScore(ctx, "test_collection", queryVector, 2, nil, true)
	assert.NoError(t, err, "带分数搜索失败")
	assert.Len(t, resultsWithScore, 2, "带分数搜索结果数量不正确")
	
	// 检查文档数量
	count, err := inMemoryStore.CountDocuments(ctx, "test_collection", nil)
	assert.NoError(t, err, "获取集合文档数量失败")
	assert.Equal(t, 2, count, "文档数量不正确")
	
	// 删除文档
	err = inMemoryStore.DeleteDocument(ctx, "test_collection", "doc1")
	assert.NoError(t, err, "删除文档失败")
	
	// 再次检查文档数量
	count, err = inMemoryStore.CountDocuments(ctx, "test_collection", nil)
	assert.NoError(t, err, "获取集合文档数量失败")
	assert.Equal(t, 1, count, "删除后文档数量不正确")
	
	// 删除集合
	err = inMemoryStore.DeleteCollection(ctx, "test_collection")
	assert.NoError(t, err, "删除集合失败")
	
	// 最终检查集合列表
	collections, err = inMemoryStore.ListCollections(ctx)
	assert.NoError(t, err, "获取集合列表失败")
	assert.Len(t, collections, 0, "集合删除后列表不为空")
	
	// 关闭向量存储
	err = inMemoryStore.Close()
	assert.NoError(t, err, "关闭向量存储失败")
}

func TestInMemoryVectorStoreMetadataFilter(t *testing.T) {
	// 创建内存向量存储
	inMemoryStore := vector_store.NewInMemoryVectorStore()
	
	// 创建嵌入模型
	options := embeddings.EmbeddingOptions{
		Dimensions: 4,
	}
	mockEmbedder, err := embeddings.NewMockEmbedder(options)
	assert.NoError(t, err, "创建嵌入模型失败")
	
	// 创建上下文
	ctx := context.Background()
	
	// 初始化向量存储
	err = inMemoryStore.Initialize(ctx)
	assert.NoError(t, err, "初始化向量存储失败")
	
	// 创建集合
	err = inMemoryStore.CreateCollection(ctx, "test_filter", 4, "测试过滤集合")
	assert.NoError(t, err, "创建集合失败")
	
	// 创建测试文档（带不同元数据）
	docs := []models.Document{
		{
			ID:         "doc1",
			Content:    "苹果是一种常见水果",
			Collection: "test_filter",
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
			Metadata: map[string]interface{}{
				"category": "水果",
				"color":    "红色",
			},
		},
		{
			ID:         "doc2",
			Content:    "香蕉是一种常见水果",
			Collection: "test_filter",
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
			Metadata: map[string]interface{}{
				"category": "水果",
				"color":    "黄色",
			},
		},
		{
			ID:         "doc3",
			Content:    "西红柿可以用来做沙拉",
			Collection: "test_filter",
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
			Metadata: map[string]interface{}{
				"category": "蔬菜",
				"color":    "红色",
			},
		},
	}
	
	// 为文档生成嵌入向量
	for i := range docs {
		vector, err := mockEmbedder.EmbedQuery(ctx, docs[i].Content)
		assert.NoError(t, err, "生成文档向量失败")
		docs[i].Vector = vector
	}
	
	// 添加文档
	_, err = inMemoryStore.UpsertDocuments(ctx, "test_filter", docs)
	assert.NoError(t, err, "添加文档失败")
	
	// 查询向量
	queryText := "水果"
	queryVector, err := mockEmbedder.EmbedQuery(ctx, queryText)
	assert.NoError(t, err, "生成查询向量失败")
	
	// 测试元数据过滤 - 只返回红色水果
	filter := map[string]interface{}{
		"category": "水果",
		"color":    "红色",
	}
	
	results, err := inMemoryStore.SimilaritySearch(ctx, "test_filter", queryVector, 10, filter, true)
	assert.NoError(t, err, "搜索失败")
	assert.Len(t, results, 1, "过滤结果数量不正确")
	assert.Equal(t, "doc1", results[0].ID, "过滤后的文档不正确")
	
	// 测试元数据过滤 - 只返回红色物品（不分水果蔬菜）
	filter = map[string]interface{}{
		"color": "红色",
	}
	
	results, err = inMemoryStore.SimilaritySearch(ctx, "test_filter", queryVector, 10, filter, true)
	assert.NoError(t, err, "搜索失败")
	assert.Len(t, results, 2, "过滤结果数量不正确")
	
	// 使用高级搜索接口
	options := map[string]interface{}{
		"search_type": "similarity",
	}
	results, err = inMemoryStore.Search(ctx, "test_filter", queryVector, models.QueryTypeSimilarity, 10, filter, true, options)
	assert.NoError(t, err, "高级搜索失败")
	assert.Len(t, results, 2, "高级搜索过滤结果数量不正确")
	
	// 关闭向量存储
	err = inMemoryStore.Close()
	assert.NoError(t, err, "关闭向量存储失败")
} 