package vector_store

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"sync"

	"github.com/google/uuid"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/logger"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/vecutil"
)

// LocalStore 是本地向量存储的实现
type LocalStore struct {
	dataPath  string
	dimensions int
	mutex     sync.RWMutex
	collections map[string]bool
}

// NewLocalStore 创建本地向量存储
func NewLocalStore(dataPath string, dimensions int) (*LocalStore, error) {
	// 确保数据目录存在
	if err := os.MkdirAll(dataPath, 0755); err != nil {
		return nil, fmt.Errorf("创建数据目录失败: %w", err)
	}

	store := &LocalStore{
		dataPath:    dataPath,
		dimensions:  dimensions,
		collections: make(map[string]bool),
	}

	// 加载已有集合
	entries, err := os.ReadDir(dataPath)
	if err != nil {
		return nil, fmt.Errorf("读取数据目录失败: %w", err)
	}

	for _, entry := range entries {
		if entry.IsDir() {
			store.collections[entry.Name()] = true
		}
	}

	return store, nil
}

// 获取集合路径
func (s *LocalStore) getCollectionPath(collection string) string {
	return filepath.Join(s.dataPath, collection)
}

// 获取文档路径
func (s *LocalStore) getDocumentPath(collection, documentID string) string {
	return filepath.Join(s.getCollectionPath(collection), documentID+".json")
}

// Search 搜索集合中的文档
func (s *LocalStore) Search(ctx context.Context, collection string, vector []float32, limit int, filters map[string]interface{}) ([]models.SearchResult, error) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	// 检查集合是否存在
	if !s.collections[collection] {
		return nil, fmt.Errorf("集合不存在: %s", collection)
	}

	collectionPath := s.getCollectionPath(collection)
	entries, err := os.ReadDir(collectionPath)
	if err != nil {
		return nil, fmt.Errorf("读取集合目录失败: %w", err)
	}

	// 存储搜索结果
	var results []models.SearchResult

	// 处理每个文档
	for _, entry := range entries {
		if entry.IsDir() || filepath.Ext(entry.Name()) != ".json" {
			continue
		}

		// 读取文档
		docPath := filepath.Join(collectionPath, entry.Name())
		docData, err := os.ReadFile(docPath)
		if err != nil {
			logger.Warnf("读取文档失败: %v", err)
			continue
		}

		// 解析文档
		var doc models.Document
		if err := json.Unmarshal(docData, &doc); err != nil {
			logger.Warnf("解析文档失败: %v", err)
			continue
		}

		// 检查过滤器
		if !s.matchesFilters(doc.Metadata, filters) {
			continue
		}

		// 计算相似度
		similarity := vecutil.CosineSimilarity(vector, doc.Vector)

		// 添加到结果
		results = append(results, models.SearchResult{
			ID:         doc.ID,
			Content:    doc.Content,
			Metadata:   doc.Metadata,
			Score:      similarity,
		})
	}

	// 按相似度排序
	sort.Slice(results, func(i, j int) bool {
		return results[i].Score > results[j].Score
	})

	// 限制结果数量
	if limit > 0 && len(results) > limit {
		results = results[:limit]
	}

	return results, nil
}

// 检查是否匹配过滤器
func (s *LocalStore) matchesFilters(metadata map[string]interface{}, filters map[string]interface{}) bool {
	if len(filters) == 0 {
		return true
	}

	for key, value := range filters {
		metaValue, exists := metadata[key]
		if !exists {
			return false
		}

		// 简单比较，可以扩展为更复杂的过滤逻辑
		if metaValue != value {
			return false
		}
	}

	return true
}

// AddDocuments 添加文档到集合
func (s *LocalStore) AddDocuments(ctx context.Context, collection string, documents []models.Document) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	// 确保集合存在
	collectionPath := s.getCollectionPath(collection)
	if err := os.MkdirAll(collectionPath, 0755); err != nil {
		return fmt.Errorf("创建集合目录失败: %w", err)
	}

	// 标记集合存在
	s.collections[collection] = true

	// 添加每个文档
	for _, doc := range documents {
		// 如果没有ID，生成一个
		if doc.ID == "" {
			doc.ID = uuid.New().String()
		}

		// 序列化文档
		docData, err := json.Marshal(doc)
		if err != nil {
			return fmt.Errorf("序列化文档失败: %w", err)
		}

		// 写入文件
		docPath := s.getDocumentPath(collection, doc.ID)
		if err := os.WriteFile(docPath, docData, 0644); err != nil {
			return fmt.Errorf("写入文档失败: %w", err)
		}
	}

	return nil
}

// DeleteDocuments 从集合中删除文档
func (s *LocalStore) DeleteDocuments(ctx context.Context, collection string, documentIDs []string) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	// 检查集合是否存在
	if !s.collections[collection] {
		return fmt.Errorf("集合不存在: %s", collection)
	}

	// 删除每个文档
	for _, docID := range documentIDs {
		docPath := s.getDocumentPath(collection, docID)
		if err := os.Remove(docPath); err != nil && !os.IsNotExist(err) {
			return fmt.Errorf("删除文档失败: %w", err)
		}
	}

	return nil
}

// ListCollections 列出所有集合
func (s *LocalStore) ListCollections(ctx context.Context) ([]string, error) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	var collections []string
	for collection := range s.collections {
		collections = append(collections, collection)
	}

	return collections, nil
}

// CreateCollection 创建新集合
func (s *LocalStore) CreateCollection(ctx context.Context, collection string, dimensions int) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	// 检查集合是否已存在
	if s.collections[collection] {
		return fmt.Errorf("集合已存在: %s", collection)
	}

	// 创建集合目录
	collectionPath := s.getCollectionPath(collection)
	if err := os.MkdirAll(collectionPath, 0755); err != nil {
		return fmt.Errorf("创建集合目录失败: %w", err)
	}

	// 标记集合存在
	s.collections[collection] = true

	return nil
}

// DeleteCollection 删除集合
func (s *LocalStore) DeleteCollection(ctx context.Context, collection string) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	// 检查集合是否存在
	if !s.collections[collection] {
		return fmt.Errorf("集合不存在: %s", collection)
	}

	// 删除集合目录
	collectionPath := s.getCollectionPath(collection)
	if err := os.RemoveAll(collectionPath); err != nil {
		return fmt.Errorf("删除集合目录失败: %w", err)
	}

	// 移除集合标记
	delete(s.collections, collection)

	return nil
}

// CollectionExists 检查集合是否存在
func (s *LocalStore) CollectionExists(ctx context.Context, collection string) (bool, error) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	return s.collections[collection], nil
}

// DocumentCount 获取集合中的文档数量
func (s *LocalStore) DocumentCount(ctx context.Context, collection string) (int, error) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	// 检查集合是否存在
	if !s.collections[collection] {
		return 0, fmt.Errorf("集合不存在: %s", collection)
	}

	// 获取集合目录中的文件数量
	collectionPath := s.getCollectionPath(collection)
	entries, err := os.ReadDir(collectionPath)
	if err != nil {
		return 0, fmt.Errorf("读取集合目录失败: %w", err)
	}

	// 只计算JSON文件
	count := 0
	for _, entry := range entries {
		if !entry.IsDir() && filepath.Ext(entry.Name()) == ".json" {
			count++
		}
	}

	return count, nil
}

// GetDocument 获取文档
func (s *LocalStore) GetDocument(ctx context.Context, collection string, documentID string) (models.Document, error) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	// 检查集合是否存在
	if !s.collections[collection] {
		return models.Document{}, fmt.Errorf("集合不存在: %s", collection)
	}

	// 读取文档
	docPath := s.getDocumentPath(collection, documentID)
	docData, err := os.ReadFile(docPath)
	if err != nil {
		if os.IsNotExist(err) {
			return models.Document{}, fmt.Errorf("文档不存在: %s", documentID)
		}
		return models.Document{}, fmt.Errorf("读取文档失败: %w", err)
	}

	// 解析文档
	var doc models.Document
	if err := json.Unmarshal(docData, &doc); err != nil {
		return models.Document{}, fmt.Errorf("解析文档失败: %w", err)
	}

	return doc, nil
}

// IsHealthy 健康检查
func (s *LocalStore) IsHealthy(ctx context.Context) bool {
	// 尝试访问数据目录
	_, err := os.Stat(s.dataPath)
	return err == nil
} 