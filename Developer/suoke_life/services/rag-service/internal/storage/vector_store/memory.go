package vector_store

import (
	"context"
	"errors"
	"fmt"
	"sort"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/logger"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/vecutil"
)

// InMemoryVectorStore 内存向量存储实现，主要用于测试
type InMemoryVectorStore struct {
	sync.RWMutex
	collections map[string]*Collection
}

// Collection 内存集合
type Collection struct {
	Name        string
	Description string
	Dimension   int
	Documents   map[string]models.Document
	CreatedAt   time.Time
	UpdatedAt   time.Time
}

// NewInMemoryVectorStore 创建新内存向量存储
func NewInMemoryVectorStore() *InMemoryVectorStore {
	return &InMemoryVectorStore{
		collections: make(map[string]*Collection),
	}
}

// Initialize 初始化向量存储
func (s *InMemoryVectorStore) Initialize(ctx context.Context) error {
	// 内存存储不需要初始化
	return nil
}

// CreateCollection 创建集合
func (s *InMemoryVectorStore) CreateCollection(ctx context.Context, name string, dimension int, description string) error {
	s.Lock()
	defer s.Unlock()

	if _, exists := s.collections[name]; exists {
		return fmt.Errorf("集合 %s 已存在", name)
	}

	s.collections[name] = &Collection{
		Name:        name,
		Description: description,
		Dimension:   dimension,
		Documents:   make(map[string]models.Document),
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	logger.Infof("创建集合: %s", name)
	return nil
}

// DeleteCollection 删除集合
func (s *InMemoryVectorStore) DeleteCollection(ctx context.Context, name string) error {
	s.Lock()
	defer s.Unlock()

	if _, exists := s.collections[name]; !exists {
		return fmt.Errorf("集合 %s 不存在", name)
	}

	delete(s.collections, name)
	logger.Infof("删除集合: %s", name)
	return nil
}

// ListCollections 获取集合列表
func (s *InMemoryVectorStore) ListCollections(ctx context.Context) ([]models.Collection, error) {
	s.RLock()
	defer s.RUnlock()

	result := make([]models.Collection, 0, len(s.collections))
	for _, col := range s.collections {
		result = append(result, models.Collection{
			Name:        col.Name,
			Description: col.Description,
			Count:       len(col.Documents),
			CreatedAt:   col.CreatedAt,
			UpdatedAt:   col.UpdatedAt,
			Dimension:   col.Dimension,
			Status:      "active",
		})
	}

	return result, nil
}

// GetCollection 获取指定集合信息
func (s *InMemoryVectorStore) GetCollection(ctx context.Context, name string) (*models.Collection, error) {
	s.RLock()
	defer s.RUnlock()

	col, exists := s.collections[name]
	if !exists {
		return nil, fmt.Errorf("集合 %s 不存在", name)
	}

	result := &models.Collection{
		Name:        col.Name,
		Description: col.Description,
		Count:       len(col.Documents),
		CreatedAt:   col.CreatedAt,
		UpdatedAt:   col.UpdatedAt,
		Dimension:   col.Dimension,
		Status:      "active",
	}

	return result, nil
}

// CollectionExists 检查集合是否存在
func (s *InMemoryVectorStore) CollectionExists(ctx context.Context, name string) (bool, error) {
	s.RLock()
	defer s.RUnlock()

	_, exists := s.collections[name]
	return exists, nil
}

// GetCollectionCount 获取集合文档数量
func (s *InMemoryVectorStore) GetCollectionCount(name string) (int, error) {
	s.RLock()
	defer s.RUnlock()

	col, exists := s.collections[name]
	if !exists {
		return 0, fmt.Errorf("集合 %s 不存在", name)
	}

	return len(col.Documents), nil
}

// UpsertDocuments 批量更新或插入文档
func (s *InMemoryVectorStore) UpsertDocuments(ctx context.Context, collectionName string, documents []models.Document) ([]string, error) {
	if len(documents) == 0 {
		return nil, errors.New("文档列表为空")
	}

	s.Lock()
	defer s.Unlock()

	col, exists := s.collections[collectionName]
	if !exists {
		return nil, fmt.Errorf("集合 %s 不存在", collectionName)
	}

	ids := make([]string, len(documents))
	for i, doc := range documents {
		if len(doc.Vector) != col.Dimension {
			return nil, fmt.Errorf("向量维度不匹配，期望 %d，实际 %d", col.Dimension, len(doc.Vector))
		}

		// 如果没有ID，创建一个新的UUID
		if doc.ID == "" {
			doc.ID = uuid.New().String()
		}
		ids[i] = doc.ID

		// 确保时间戳存在
		if doc.CreatedAt.IsZero() {
			doc.CreatedAt = time.Now()
		}
		doc.UpdatedAt = time.Now()
		doc.Collection = collectionName

		col.Documents[doc.ID] = doc
	}

	col.UpdatedAt = time.Now()
	logger.Infof("更新或插入 %d 个文档到集合 %s", len(documents), collectionName)
	return ids, nil
}

// UpsertDocument 更新或插入单个文档
func (s *InMemoryVectorStore) UpsertDocument(ctx context.Context, collectionName string, document models.Document) (string, error) {
	ids, err := s.UpsertDocuments(ctx, collectionName, []models.Document{document})
	if err != nil {
		return "", err
	}
	return ids[0], nil
}

// AddDocuments 添加文档
func (s *InMemoryVectorStore) AddDocuments(documents []models.Document) error {
	if len(documents) == 0 {
		return errors.New("文档列表为空")
	}

	s.Lock()
	defer s.Unlock()

	for _, doc := range documents {
		collectionName := doc.Collection
		col, exists := s.collections[collectionName]
		if !exists {
			return fmt.Errorf("集合 %s 不存在", collectionName)
		}

		if len(doc.Vector) != col.Dimension {
			return fmt.Errorf("向量维度不匹配，期望 %d，实际 %d", col.Dimension, len(doc.Vector))
		}

		// 如果没有ID，创建一个新的UUID
		if doc.ID == "" {
			doc.ID = uuid.New().String()
		}

		// 确保时间戳存在
		if doc.CreatedAt.IsZero() {
			doc.CreatedAt = time.Now()
		}
		if doc.UpdatedAt.IsZero() {
			doc.UpdatedAt = time.Now()
		}

		col.Documents[doc.ID] = doc
		col.UpdatedAt = time.Now()
	}

	logger.Infof("添加 %d 个文档", len(documents))
	return nil
}

// DeleteDocument 删除文档
func (s *InMemoryVectorStore) DeleteDocument(ctx context.Context, collectionName string, documentID string) error {
	s.Lock()
	defer s.Unlock()

	col, exists := s.collections[collectionName]
	if !exists {
		return fmt.Errorf("集合 %s 不存在", collectionName)
	}

	if _, exists := col.Documents[documentID]; !exists {
		return fmt.Errorf("文档 %s 不存在", documentID)
	}

	delete(col.Documents, documentID)
	col.UpdatedAt = time.Now()

	logger.Infof("删除文档: %s 从集合 %s", documentID, collectionName)
	return nil
}

// DeleteDocuments 批量删除文档
func (s *InMemoryVectorStore) DeleteDocuments(ctx context.Context, collectionName string, documentIDs []string) error {
	s.Lock()
	defer s.Unlock()

	col, exists := s.collections[collectionName]
	if !exists {
		return fmt.Errorf("集合 %s 不存在", collectionName)
	}

	for _, id := range documentIDs {
		if _, exists := col.Documents[id]; exists {
			delete(col.Documents, id)
		}
	}

	col.UpdatedAt = time.Now()
	logger.Infof("删除 %d 个文档从集合 %s", len(documentIDs), collectionName)
	return nil
}

// DeleteDocumentsByFilter 根据过滤条件删除文档
func (s *InMemoryVectorStore) DeleteDocumentsByFilter(ctx context.Context, collectionName string, filter map[string]interface{}) error {
	s.Lock()
	defer s.Unlock()

	col, exists := s.collections[collectionName]
	if !exists {
		return fmt.Errorf("集合 %s 不存在", collectionName)
	}

	deletedCount := 0
	for id, doc := range col.Documents {
		if matchesFilter(doc, filter) {
			delete(col.Documents, id)
			deletedCount++
		}
	}

	col.UpdatedAt = time.Now()
	logger.Infof("根据过滤条件删除 %d 个文档从集合 %s", deletedCount, collectionName)
	return nil
}

// GetDocument 获取文档
func (s *InMemoryVectorStore) GetDocument(ctx context.Context, collectionName string, documentID string) (*models.Document, error) {
	s.RLock()
	defer s.RUnlock()

	col, exists := s.collections[collectionName]
	if !exists {
		return nil, fmt.Errorf("集合 %s 不存在", collectionName)
	}

	doc, exists := col.Documents[documentID]
	if !exists {
		return nil, fmt.Errorf("文档 %s 不存在", documentID)
	}

	return &doc, nil
}

// GetDocumentBatch 批量获取文档
func (s *InMemoryVectorStore) GetDocumentBatch(ctx context.Context, collectionName string, documentIDs []string) ([]models.Document, error) {
	s.RLock()
	defer s.RUnlock()

	col, exists := s.collections[collectionName]
	if !exists {
		return nil, fmt.Errorf("集合 %s 不存在", collectionName)
	}

	result := make([]models.Document, 0, len(documentIDs))
	for _, id := range documentIDs {
		if doc, exists := col.Documents[id]; exists {
			result = append(result, doc)
		}
	}

	return result, nil
}

// SimilaritySearch 相似度搜索
func (s *InMemoryVectorStore) SimilaritySearch(
	ctx context.Context,
	collectionName string,
	queryVector []float32,
	limit int,
	filter map[string]interface{},
	includeVector bool,
) ([]models.Document, error) {
	return s.Search(ctx, collectionName, queryVector, models.QueryTypeSimilarity, limit, filter, includeVector, nil)
}

// SimilaritySearchByText 通过文本进行相似度搜索
func (s *InMemoryVectorStore) SimilaritySearchByText(
	ctx context.Context,
	collectionName string,
	query string,
	limit int,
	filter map[string]interface{},
	includeVector bool,
) ([]models.Document, error) {
	// 这个方法需要嵌入模型将文本转换为向量
	// 在内存实现中，我们无法直接支持
	return nil, errors.New("内存存储不支持通过文本搜索，请使用向量搜索")
}

// MMRSearch 最大边缘相关性搜索
func (s *InMemoryVectorStore) MMRSearch(
	ctx context.Context,
	collectionName string,
	queryVector []float32,
	limit int,
	lambdaMultiplier float64,
	filter map[string]interface{},
	includeVector bool,
) ([]models.Document, error) {
	// 这里应该实现MMR算法，但简单起见，我们先用普通相似度搜索
	return s.SimilaritySearch(ctx, collectionName, queryVector, limit, filter, includeVector)
}

// CountDocuments 计算文档数量
func (s *InMemoryVectorStore) CountDocuments(ctx context.Context, collectionName string, filter map[string]interface{}) (int, error) {
	s.RLock()
	defer s.RUnlock()

	col, exists := s.collections[collectionName]
	if !exists {
		return 0, fmt.Errorf("集合 %s 不存在", collectionName)
	}

	if filter == nil {
		return len(col.Documents), nil
	}

	count := 0
	for _, doc := range col.Documents {
		if matchesFilter(doc, filter) {
			count++
		}
	}

	return count, nil
}

// Search 搜索文档
func (s *InMemoryVectorStore) Search(
	ctx context.Context,
	collectionName string,
	queryVector []float32,
	queryType models.QueryType,
	limit int,
	filter map[string]interface{},
	includeVector bool,
	options map[string]interface{},
) ([]models.Document, error) {
	s.RLock()
	defer s.RUnlock()

	col, exists := s.collections[collectionName]
	if !exists {
		return nil, fmt.Errorf("集合 %s 不存在", collectionName)
	}

	if len(queryVector) != col.Dimension {
		return nil, fmt.Errorf("向量维度不匹配，期望 %d，实际 %d", col.Dimension, len(queryVector))
	}

	if limit <= 0 {
		limit = 10 // 默认最多返回10个结果
	}

	// 计算所有文档的相似度
	type docScore struct {
		doc   models.Document
		score float64
	}

	results := make([]docScore, 0, len(col.Documents))
	for _, doc := range col.Documents {
		// 如果有过滤器，检查是否匹配
		if filter != nil && !matchesFilter(doc, filter) {
			continue
		}

		// 根据查询类型计算相似度
		var similarity float64
		switch queryType {
		case models.QueryTypeSimilarity:
			similarity = float64(vecutil.CosineSimilarity(queryVector, doc.Vector))
		case models.QueryTypeMMR:
			// MMR需要更复杂的算法，简单起见，我们先用余弦相似度
			similarity = float64(vecutil.CosineSimilarity(queryVector, doc.Vector))
		default:
			similarity = float64(vecutil.CosineSimilarity(queryVector, doc.Vector))
		}

		// 复制文档并设置评分
		docCopy := doc
		docCopy.Score = similarity

		// 如果不包含向量，则清空向量
		if !includeVector {
			docCopy.Vector = nil
		}

		results = append(results, docScore{
			doc:   docCopy,
			score: similarity,
		})
	}

	// 按相似度排序
	sort.Slice(results, func(i, j int) bool {
		return results[i].score > results[j].score
	})

	// 限制结果数量
	if len(results) > limit {
		results = results[:limit]
	}

	// 转换为文档列表
	docs := make([]models.Document, len(results))
	for i, res := range results {
		docs[i] = res.doc
	}

	return docs, nil
}

// SimilaritySearchWithScore 带分数的相似度搜索
func (s *InMemoryVectorStore) SimilaritySearchWithScore(
	ctx context.Context,
	collectionName string,
	queryVector []float32,
	limit int,
	filter map[string]interface{},
	includeVector bool,
) ([]models.Document, error) {
	// 这个方法直接调用SimilaritySearch即可，因为我们已经在Document中添加了Score字段
	return s.SimilaritySearch(ctx, collectionName, queryVector, limit, filter, includeVector)
}

// 检查文档是否匹配过滤器
func matchesFilter(doc models.Document, filter map[string]interface{}) bool {
	for key, value := range filter {
		// 检查文档元数据中是否有对应键
		metaValue, exists := doc.Metadata[key]
		if !exists || metaValue != value {
			return false
		}
	}
	return true
}

// Status 检查向量存储状态
func (s *InMemoryVectorStore) Status() (bool, error) {
	return true, nil // 内存存储总是可用
}

// Close 关闭向量存储
func (s *InMemoryVectorStore) Close() error {
	return nil // 无需关闭资源
} 