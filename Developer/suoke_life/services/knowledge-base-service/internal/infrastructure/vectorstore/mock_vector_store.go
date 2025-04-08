package vectorstore

import (
	"context"
	"fmt"
	"math"
	"sync"

	"github.com/google/uuid"
)

// result 排序用的结果结构体
type result struct {
	docID    string
	score    float32
	vectorID string
}

// MockVectorStore 模拟向量存储实现
// 用于测试，不需要外部依赖
type MockVectorStore struct {
	mu         sync.RWMutex
	vectors    map[string][]float32 // 向量ID到向量的映射
	docMapping map[string]string    // 向量ID到文档ID的映射
	docVectors map[string][]string  // 文档ID到向量ID列表的映射
}

// NewMockVectorStore 创建新的模拟向量存储
func NewMockVectorStore() *MockVectorStore {
	return &MockVectorStore{
		vectors:    make(map[string][]float32),
		docMapping: make(map[string]string),
		docVectors: make(map[string][]string),
	}
}

// StoreVector 存储向量
func (m *MockVectorStore) StoreVector(ctx context.Context, docID string, vector []float32) (string, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	// 生成唯一的向量ID
	vectorID := uuid.New().String()

	// 存储向量
	m.vectors[vectorID] = vector

	// 建立向量到文档的映射
	m.docMapping[vectorID] = docID

	// 建立文档到向量的映射
	if _, ok := m.docVectors[docID]; !ok {
		m.docVectors[docID] = []string{}
	}
	m.docVectors[docID] = append(m.docVectors[docID], vectorID)

	return vectorID, nil
}

// SearchVector 搜索向量
func (m *MockVectorStore) SearchVector(ctx context.Context, vector []float32, limit int) ([]string, []float32, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	// 如果没有向量，直接返回空结果
	if len(m.vectors) == 0 {
		return []string{}, []float32{}, nil
	}

	// 计算所有向量的相似度
	results := make([]result, 0, len(m.vectors))
	for vectorID, storedVector := range m.vectors {
		// 确保向量维度一致
		if len(storedVector) != len(vector) {
			return nil, nil, fmt.Errorf("向量维度不匹配: 存储(%d) != 查询(%d)", len(storedVector), len(vector))
		}

		// 计算余弦相似度
		similarity := cosineSimilarity(vector, storedVector)

		// 获取对应的文档ID
		docID := m.docMapping[vectorID]

		results = append(results, result{
			docID:    docID,
			score:    similarity,
			vectorID: vectorID,
		})
	}

	// 按相似度排序（降序）
	sort(results)

	// 限制结果数量
	if limit > 0 && limit < len(results) {
		results = results[:limit]
	}

	// 提取文档ID和分数
	docIDs := make([]string, len(results))
	scores := make([]float32, len(results))
	for i, res := range results {
		docIDs[i] = res.docID
		scores[i] = res.score
	}

	return docIDs, scores, nil
}

// DeleteVector 删除向量
func (m *MockVectorStore) DeleteVector(ctx context.Context, vectorID string) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	// 检查向量是否存在
	if _, ok := m.vectors[vectorID]; !ok {
		return fmt.Errorf("向量不存在: %s", vectorID)
	}

	// 获取对应的文档ID
	docID := m.docMapping[vectorID]

	// 从文档到向量的映射中删除
	if vectors, ok := m.docVectors[docID]; ok {
		newVectors := make([]string, 0, len(vectors)-1)
		for _, vid := range vectors {
			if vid != vectorID {
				newVectors = append(newVectors, vid)
			}
		}
		if len(newVectors) == 0 {
			delete(m.docVectors, docID)
		} else {
			m.docVectors[docID] = newVectors
		}
	}

	// 删除向量到文档的映射
	delete(m.docMapping, vectorID)

	// 删除向量
	delete(m.vectors, vectorID)

	return nil
}

// Close 关闭模拟向量存储
func (m *MockVectorStore) Close() error {
	m.mu.Lock()
	defer m.mu.Unlock()

	// 清空所有存储的数据
	m.vectors = make(map[string][]float32)
	m.docMapping = make(map[string]string)
	m.docVectors = make(map[string][]string)

	return nil
}

// Ping 检查模拟向量存储是否可用
func (m *MockVectorStore) Ping(ctx context.Context) error {
	// 模拟向量存储始终可用
	return nil
}

// 计算余弦相似度
func cosineSimilarity(a, b []float32) float32 {
	var dotProduct float32
	var normA float32
	var normB float32

	for i := 0; i < len(a); i++ {
		dotProduct += a[i] * b[i]
		normA += a[i] * a[i]
		normB += b[i] * b[i]
	}

	// 防止除以零
	if normA == 0 || normB == 0 {
		return 0
	}

	return dotProduct / float32(math.Sqrt(float64(normA))*math.Sqrt(float64(normB)))
}

// 对结果进行排序（按相似度降序）
func sort(results []result) {
	for i := 0; i < len(results); i++ {
		for j := i + 1; j < len(results); j++ {
			if results[i].score < results[j].score {
				results[i], results[j] = results[j], results[i]
			}
		}
	}
}
