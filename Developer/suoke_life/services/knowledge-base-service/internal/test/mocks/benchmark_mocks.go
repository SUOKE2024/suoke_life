package mocks

import (
	"context"
	"time"

	"github.com/google/uuid"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/domain/service"
)

// 性能测试专用的模拟对象

// BatchDocumentOption 文档批量创建选项
type BatchDocumentOption struct {
	Title       string
	Content     string
	Description string
	ContentType entity.ContentType
	CategoryID  uuid.UUID
	AuthorID    uuid.UUID
	Tags        []string
}

// GenerateTestDocumentOptions 生成测试文档选项
func GenerateTestDocumentOptions() BatchDocumentOption {
	return BatchDocumentOption{
		Title:       "测试文档标题 " + uuid.New().String(),
		Content:     "这是测试文档的内容。它包含足够的文本以便进行测试。",
		Description: "测试文档描述",
		ContentType: entity.ContentTypeMarkdown,
		CategoryID:  uuid.New(),
		AuthorID:    uuid.New(),
		Tags:        []string{"测试", "基准测试"},
	}
}

// MockBenchDocumentRepository 是一个性能测试专用的文档仓库模拟
type MockBenchDocumentRepository struct {
	Documents []*entity.Document
}

// FindByID 查找文档
func (m *MockBenchDocumentRepository) FindByID(ctx context.Context, id uuid.UUID) (*entity.Document, error) {
	for _, doc := range m.Documents {
		if doc.ID == id {
			return doc, nil
		}
	}
	return nil, nil
}

// Save 保存文档
func (m *MockBenchDocumentRepository) Save(ctx context.Context, doc *entity.Document) error {
	m.Documents = append(m.Documents, doc)
	return nil
}

// Update 更新文档
func (m *MockBenchDocumentRepository) Update(ctx context.Context, doc *entity.Document) (*entity.Document, error) {
	for i, existingDoc := range m.Documents {
		if existingDoc.ID == doc.ID {
			m.Documents[i] = doc
			return doc, nil
		}
	}
	return nil, nil
}

// Delete 删除文档
func (m *MockBenchDocumentRepository) Delete(ctx context.Context, id uuid.UUID) error {
	for i, doc := range m.Documents {
		if doc.ID == id {
			m.Documents = append(m.Documents[:i], m.Documents[i+1:]...)
			return nil
		}
	}
	return nil
}

// SearchByText 文本搜索
func (m *MockBenchDocumentRepository) SearchByText(ctx context.Context, query string) ([]*entity.Document, error) {
	// 简单实现，返回所有文档
	return m.Documents, nil
}

// SemanticSearch 语义搜索
func (m *MockBenchDocumentRepository) SemanticSearch(ctx context.Context, query string, limit int) ([]*entity.Document, error) {
	// 简单实现，返回所有文档，但最多limit个
	if len(m.Documents) <= limit {
		return m.Documents, nil
	}
	return m.Documents[:limit], nil
}

// UpdateStatus 更新状态
func (m *MockBenchDocumentRepository) UpdateStatus(ctx context.Context, id uuid.UUID, status entity.DocumentStatus) error {
	for _, doc := range m.Documents {
		if doc.ID == id {
			doc.Status = status
			return nil
		}
	}
	return nil
}

// FindByStatus 按状态查找
func (m *MockBenchDocumentRepository) FindByStatus(ctx context.Context, status entity.DocumentStatus) ([]*entity.Document, error) {
	var result []*entity.Document
	for _, doc := range m.Documents {
		if doc.Status == status {
			result = append(result, doc)
		}
	}
	return result, nil
}

// SaveWithEmbeddings 保存文档和嵌入
func (m *MockBenchDocumentRepository) SaveWithEmbeddings(ctx context.Context, doc *entity.Document, embeddings [][]float32) error {
	m.Documents = append(m.Documents, doc)
	return nil
}

// SaveBatch 批量保存
func (m *MockBenchDocumentRepository) SaveBatch(ctx context.Context, docs []*entity.Document, embeddings [][][]float32) error {
	m.Documents = append(m.Documents, docs...)
	return nil
}

// UpdateTxHash 更新交易哈希
func (m *MockBenchDocumentRepository) UpdateTxHash(ctx context.Context, id uuid.UUID, txHash string) error {
	for _, doc := range m.Documents {
		if doc.ID == id {
			doc.SetBlockchainTxHash(txHash)
			return nil
		}
	}
	return nil
}

// MockBenchEmbeddingService 是一个性能测试专用的嵌入服务模拟
type MockBenchEmbeddingService struct {
	VectorDimension int
}

// EmbedTexts 嵌入文本
func (m *MockBenchEmbeddingService) EmbedTexts(ctx context.Context, texts []string) ([][]float32, error) {
	// 为每个文本生成一个固定大小的向量
	embeddings := make([][]float32, len(texts))
	for i := range texts {
		embeddings[i] = make([]float32, m.VectorDimension)
		// 简单填充，避免全零向量
		for j := 0; j < m.VectorDimension; j++ {
			embeddings[i][j] = float32(i*j) / float32(m.VectorDimension)
		}
	}
	return embeddings, nil
}

// GetModelDimension 获取模型维度
func (m *MockBenchEmbeddingService) GetModelDimension() int {
	return m.VectorDimension
}

// NewMockBenchDocumentService 创建一个用于基准测试的文档服务
func NewMockBenchDocumentService(repo *MockBenchDocumentRepository, textSplitter interface{}, embeddingService *MockBenchEmbeddingService) *MockBenchDocumentService {
	return &MockBenchDocumentService{
		repo:             repo,
		textSplitter:     textSplitter,
		embeddingService: embeddingService,
	}
}

// MockBenchDocumentService 是一个性能测试专用的文档服务模拟
type MockBenchDocumentService struct {
	repo             *MockBenchDocumentRepository
	textSplitter     interface{}
	embeddingService *MockBenchEmbeddingService
}

// CreateDocument 创建文档
func (s *MockBenchDocumentService) CreateDocument(ctx context.Context, opts service.DocumentOptions) (*entity.Document, error) {
	doc := &entity.Document{
		ID:          uuid.New(),
		Title:       opts.Title,
		Content:     opts.Content,
		Description: opts.Description,
		ContentType: opts.ContentType,
		Status:      entity.StatusDraft,
		AuthorID:    opts.AuthorID,
		CategoryID:  opts.CategoryID,
		Tags:        opts.Tags,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	// 简化嵌入流程
	embeddings, _ := s.embeddingService.EmbedTexts(ctx, []string{opts.Content})
	_ = s.repo.SaveWithEmbeddings(ctx, doc, embeddings)

	return doc, nil
}

// BatchCreateDocuments 批量创建文档
func (s *MockBenchDocumentService) BatchCreateDocuments(ctx context.Context, opts []BatchDocumentOption) ([]*entity.Document, error) {
	docs := make([]*entity.Document, len(opts))
	allTexts := make([]string, len(opts))

	for i, opt := range opts {
		docs[i] = &entity.Document{
			ID:          uuid.New(),
			Title:       opt.Title,
			Content:     opt.Content,
			Description: opt.Description,
			ContentType: opt.ContentType,
			Status:      entity.StatusDraft,
			AuthorID:    opt.AuthorID,
			CategoryID:  opt.CategoryID,
			Tags:        opt.Tags,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}
		allTexts[i] = opt.Content
	}

	// 批量生成嵌入
	embeddings, _ := s.embeddingService.EmbedTexts(ctx, allTexts)

	// 构造嵌入数组
	embeddingsArray := make([][][]float32, len(docs))
	for i := range docs {
		embeddingsArray[i] = [][]float32{embeddings[i]}
	}

	// 批量保存
	_ = s.repo.SaveBatch(ctx, docs, embeddingsArray)

	return docs, nil
}

// SemanticSearch 语义搜索
func (s *MockBenchDocumentService) SemanticSearch(ctx context.Context, query string, limit int) ([]*entity.Document, error) {
	// 执行搜索，这里简化处理
	return s.repo.SemanticSearch(ctx, query, limit)
}

// GenerateLoremIpsum 生成指定长度的中文测试文本
func GenerateLoremIpsum(wordCount int) string {
	// 简单实现，返回固定文本
	text := "这是一段测试文本，用于生成指定长度的中文内容。"
	if wordCount <= 10 {
		return text[:wordCount*3]
	}
	result := ""
	for i := 0; i < wordCount/10; i++ {
		result += text
	}
	return result
}
