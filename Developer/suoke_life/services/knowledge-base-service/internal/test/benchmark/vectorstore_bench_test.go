package benchmark

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"knowledge-base-service/internal/infrastructure/vectorstore"
	"knowledge-base-service/internal/test/benchmark/real"
)

// TestSkipVectorStoreTests 跳过向量存储测试
func TestSkipVectorStoreTests(t *testing.T) {
	t.Log("向量存储测试被跳过 - 需要正确的向量存储实现，请使用real包中的实现")
}

// BenchmarkVectorStoreSkipped 跳过向量存储基准测试
// 如果需要运行真实向量存储基准测试，请执行:
// go test -bench=. ./internal/test/benchmark/real/
func BenchmarkVectorStoreSkipped(b *testing.B) {
	b.Skip("向量存储基准测试已跳过 - 需要正确的向量存储实现，请使用 real 包中的实现")
}

// 添加测试跳过函数
func TestSkipVectorStoreBenchmarks(t *testing.T) {
	if testing.Short() {
		t.Skip("跳过需要外部服务的向量存储基准测试")
	}
}

// BenchmarkVectorStore_StoreVector 基准测试向量存储
func BenchmarkVectorStore_StoreVector(b *testing.B) {
	if testing.Short() {
		b.Skip("跳过需要外部服务的向量存储基准测试")
	}

	// 设置测试
	ctx := context.Background()
	vs, _, cleanup, err := real.SetupRealVectorStore(ctx)
	if err != nil {
		b.Fatalf("设置向量存储失败: %v", err)
	}
	defer cleanup()

	// 准备测试向量
	vector := make([]float32, 1536)
	for i := range vector {
		vector[i] = float32(i) / 1536.0
	}

	// 重置定时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		docID := uuid.New().String()
		_, err := vs.StoreVector(ctx, docID, vector)
		if err != nil {
			b.Fatalf("存储向量失败: %v", err)
		}
	}
}

// BenchmarkVectorStore_SearchVector 基准测试向量搜索
func BenchmarkVectorStore_SearchVector(b *testing.B) {
	if testing.Short() {
		b.Skip("跳过需要外部服务的向量存储基准测试")
	}

	// 设置测试
	ctx := context.Background()
	vs, _, cleanup, err := real.SetupRealVectorStore(ctx)
	if err != nil {
		b.Fatalf("设置向量存储失败: %v", err)
	}
	defer cleanup()

	// 准备测试向量
	vector := make([]float32, 1536)
	for i := range vector {
		vector[i] = float32(i) / 1536.0
	}

	// 存储一些向量用于搜索
	docIDs := make([]string, 10)
	for i := 0; i < 10; i++ {
		docID := uuid.New().String()
		docIDs[i] = docID
		_, err := vs.StoreVector(ctx, docID, vector)
		if err != nil {
			b.Fatalf("存储向量失败: %v", err)
		}
	}

	// 等待索引建立
	time.Sleep(1 * time.Second)

	// 重置定时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		_, _, err := vs.SearchVector(ctx, vector, 5)
		if err != nil {
			b.Fatalf("搜索向量失败: %v", err)
		}
	}
}
