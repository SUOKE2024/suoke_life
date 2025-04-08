package real

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

// 测试向量存储跳过
func TestSkipVectorStoreTests(t *testing.T) {
	t.Skip("向量存储测试被跳过 - 需要正确的向量存储实现，请使用real包中的实现")
}

// 基准测试 - 向量存储 保存嵌入
func BenchmarkVectorStore_StoreVector(b *testing.B) {
	ctx := context.Background()

	// 设置向量存储
	vectorStore, _, vectorCleanup, err := SetupRealVectorStore(ctx)
	if err != nil {
		b.Fatalf("设置向量存储失败: %v", err)
	}
	defer vectorCleanup()

	// 准备测试数据
	docID := uuid.New().String()

	// 生成随机嵌入向量
	testEmbedding := []float32{0.1, 0.2, 0.3, 0.4, 0.5}

	// 重置计时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		// 每次使用不同的文档ID避免冲突
		currentDocID := docID + "-" + uuid.New().String()
		_, err := vectorStore.StoreVector(ctx, currentDocID, testEmbedding)
		if err != nil {
			b.Fatalf("保存向量失败: %v", err)
		}
	}
}

// 基准测试 - 向量存储 搜索相似向量
func BenchmarkVectorStore_SearchVector(b *testing.B) {
	ctx := context.Background()

	// 设置向量存储
	vectorStore, _, vectorCleanup, err := SetupRealVectorStore(ctx)
	if err != nil {
		b.Fatalf("设置向量存储失败: %v", err)
	}
	defer vectorCleanup()

	// 准备测试数据 - 先存储一些向量
	docIDs := []string{
		"test-doc-1-" + uuid.New().String(),
		"test-doc-2-" + uuid.New().String(),
	}

	testEmbeddings := [][]float32{
		{0.1, 0.2, 0.3, 0.4, 0.5},
		{0.2, 0.3, 0.4, 0.5, 0.6},
	}

	// 先保存一些向量用于测试
	for i, docID := range docIDs {
		_, err := vectorStore.StoreVector(ctx, docID, testEmbeddings[i])
		if err != nil {
			b.Fatalf("准备测试数据失败: %v", err)
		}
	}

	// 查询向量
	queryVector := []float32{0.15, 0.25, 0.35, 0.45, 0.55}

	// 重置计时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		_, _, err := vectorStore.SearchVector(ctx, queryVector, 5)
		if err != nil {
			b.Fatalf("搜索相似向量失败: %v", err)
		}
	}
}

// 基准测试 - 向量存储 删除向量
func BenchmarkVectorStore_DeleteVector(b *testing.B) {
	ctx := context.Background()

	// 设置向量存储
	vectorStore, _, vectorCleanup, err := SetupRealVectorStore(ctx)
	if err != nil {
		b.Fatalf("设置向量存储失败: %v", err)
	}
	defer vectorCleanup()

	// 重置计时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		// 创建一个新的向量
		docID := "test-doc-delete-" + uuid.New().String()
		vectorID, err := vectorStore.StoreVector(ctx, docID, []float32{0.1, 0.2, 0.3, 0.4, 0.5})
		if err != nil {
			b.Fatalf("存储向量失败: %v", err)
		}

		// 测试删除向量性能
		err = vectorStore.DeleteVector(ctx, vectorID)
		if err != nil {
			b.Fatalf("删除向量失败: %v", err)
		}
	}
}

// 测试向量存储设置
func TestVectorStoreSetup(t *testing.T) {
	ctx := context.Background()

	// 测试向量存储设置
	vectorStore, _, vectorCleanup, err := SetupRealVectorStore(ctx)
	assert.NoError(t, err, "向量存储设置应该成功")
	assert.NotNil(t, vectorStore, "向量存储不应为nil")
	defer vectorCleanup()
}
