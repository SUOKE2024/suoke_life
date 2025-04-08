package real

import (
	"context"
	"log"
	"math/rand"
	"sync"
	"time"
)

// MockVectorStore 是一个简单的模拟向量存储实现
type MockVectorStore struct {
	vectors map[string][]float32
	mu      sync.RWMutex
}

// NewMockVectorStore 创建一个新的模拟向量存储
func NewMockVectorStore() *MockVectorStore {
	log.Println("使用模拟向量存储进行测试")
	return &MockVectorStore{
		vectors: make(map[string][]float32),
	}
}

// StoreVector 存储一个向量并返回向量ID
func (m *MockVectorStore) StoreVector(ctx context.Context, docID string, vector []float32) (string, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.vectors[docID] = vector
	return docID, nil
}

// SearchVector 搜索最相似的向量
func (m *MockVectorStore) SearchVector(ctx context.Context, vector []float32, limit int) ([]string, []float32, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	// 简单实现，随机返回一些结果
	resultIDs := make([]string, 0, limit)
	similarities := make([]float32, 0, limit)

	r := rand.New(rand.NewSource(time.Now().UnixNano()))

	// 复制所有键到一个slice
	keys := make([]string, 0, len(m.vectors))
	for k := range m.vectors {
		keys = append(keys, k)
	}

	// 随机选择最多limit个元素
	count := min(limit, len(keys))
	for i := 0; i < count; i++ {
		if len(keys) == 0 {
			break
		}
		// 随机选择一个键
		idx := r.Intn(len(keys))
		resultIDs = append(resultIDs, keys[idx])
		// 生成一个0.5-1.0之间的相似度分数
		similarities = append(similarities, 0.5+0.5*r.Float32())

		// 从键列表中删除已选择的键
		keys[idx] = keys[len(keys)-1]
		keys = keys[:len(keys)-1]
	}

	return resultIDs, similarities, nil
}

// DeleteVector 删除一个向量
func (m *MockVectorStore) DeleteVector(ctx context.Context, vectorID string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	delete(m.vectors, vectorID)
	return nil
}

// Close 关闭向量存储连接
func (m *MockVectorStore) Close() error {
	// 对于模拟实现，这里不需要实际的关闭操作
	return nil
}

// Ping 检查向量存储是否可用
func (m *MockVectorStore) Ping(ctx context.Context) error {
	// 对于模拟实现，总是返回成功
	return nil
}

// min 返回两个整数中的较小值
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
