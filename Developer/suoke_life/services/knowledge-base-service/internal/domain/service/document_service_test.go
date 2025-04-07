package service_test

import (
	"context"
	"errors"
	"testing"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/domain/service"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

// 在测试包中定义DocumentOptions，避免循环导入问题
type DocumentOptions struct {
	Title       string
	Content     string
	Description string
	ContentType entity.ContentType
	AuthorID    uuid.UUID
	CategoryID  uuid.UUID
	Tags        []string
	Metadata    []entity.MetadataField
}

// 创建模拟对象
type MockDocumentRepository struct {
	mock.Mock
}

func (m *MockDocumentRepository) FindByID(ctx context.Context, id uuid.UUID) (*entity.Document, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entity.Document), args.Error(1)
}

func (m *MockDocumentRepository) FindByCategory(ctx context.Context, categoryID uuid.UUID) ([]*entity.Document, error) {
	args := m.Called(ctx, categoryID)
	return args.Get(0).([]*entity.Document), args.Error(1)
}

func (m *MockDocumentRepository) FindByTags(ctx context.Context, tags []string) ([]*entity.Document, error) {
	args := m.Called(ctx, tags)
	return args.Get(0).([]*entity.Document), args.Error(1)
}

func (m *MockDocumentRepository) Search(ctx context.Context, query string) ([]*entity.Document, error) {
	args := m.Called(ctx, query)
	return args.Get(0).([]*entity.Document), args.Error(1)
}

func (m *MockDocumentRepository) SemanticSearch(ctx context.Context, query string, limit int) ([]*entity.Document, error) {
	args := m.Called(ctx, query, limit)
	return args.Get(0).([]*entity.Document), args.Error(1)
}

func (m *MockDocumentRepository) Save(ctx context.Context, doc *entity.Document) error {
	args := m.Called(ctx, doc)
	return args.Error(0)
}

func (m *MockDocumentRepository) Update(ctx context.Context, doc *entity.Document) error {
	args := m.Called(ctx, doc)
	return args.Error(0)
}

func (m *MockDocumentRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockDocumentRepository) RegisterOnBlockchain(ctx context.Context, doc *entity.Document) (string, error) {
	args := m.Called(ctx, doc)
	return args.String(0), args.Error(1)
}

type MockCategoryRepository struct {
	mock.Mock
}

func (m *MockCategoryRepository) FindByID(ctx context.Context, id uuid.UUID) (*entity.Category, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entity.Category), args.Error(1)
}

func (m *MockCategoryRepository) FindAll(ctx context.Context) ([]*entity.Category, error) {
	args := m.Called(ctx)
	return args.Get(0).([]*entity.Category), args.Error(1)
}

func (m *MockCategoryRepository) FindByParent(ctx context.Context, parentID *uuid.UUID) ([]*entity.Category, error) {
	args := m.Called(ctx, parentID)
	return args.Get(0).([]*entity.Category), args.Error(1)
}

func (m *MockCategoryRepository) FindByPath(ctx context.Context, path string) (*entity.Category, error) {
	args := m.Called(ctx, path)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entity.Category), args.Error(1)
}

func (m *MockCategoryRepository) Save(ctx context.Context, category *entity.Category) error {
	args := m.Called(ctx, category)
	return args.Error(0)
}

func (m *MockCategoryRepository) Update(ctx context.Context, category *entity.Category) error {
	args := m.Called(ctx, category)
	return args.Error(0)
}

func (m *MockCategoryRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

type MockTextSplitter struct {
	mock.Mock
}

func (m *MockTextSplitter) Split(text string, metadata map[string]interface{}) ([]entity.Chunk, error) {
	args := m.Called(text, metadata)
	return args.Get(0).([]entity.Chunk), args.Error(1)
}

// MockEmbeddingService 嵌入服务的模拟实现
type MockEmbeddingService struct {
	mock.Mock
}

// GetEmbedding 获取单个文本的嵌入向量
func (m *MockEmbeddingService) GetEmbedding(ctx context.Context, text string) ([]float32, error) {
	args := m.Called(ctx, text)
	
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	
	return args.Get(0).([]float32), args.Error(1)
}

// GetBatchEmbeddings 批量获取文本的嵌入向量
func (m *MockEmbeddingService) GetBatchEmbeddings(ctx context.Context, texts []string) ([][]float32, error) {
	args := m.Called(ctx, texts)
	
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	
	return args.Get(0).([][]float32), args.Error(1)
}

// 模拟Category实体
func mockCategory() *entity.Category {
	return &entity.Category{
		ID:   uuid.New(),
		Name: "测试分类",
		Path: "test-category",
	}
}

// 测试CreateDocument方法
func TestDocumentService_CreateDocument(t *testing.T) {
	ctx := context.Background()
	authorID := uuid.New()
	categoryID := uuid.New()

	t.Run("创建成功", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)

		// 模拟分类存在
		category := mockCategory()
		category.ID = categoryID
		mockCatRepo.On("FindByID", ctx, categoryID).Return(category, nil)

		// 模拟文本分割
		mockTextSplitter.On("Split", mock.Anything, mock.Anything).Return([]entity.Chunk{
			{
				Content: "这是一个测试文档的内容",
			},
		}, nil)

		// 模拟嵌入向量
		vectors := [][]float32{
			{0.1, 0.2, 0.3},
		}
		mockEmbeddingService.On("GetBatchEmbeddings", ctx, mock.Anything).Return(vectors, nil)

		// 模拟保存文档
		mockDocRepo.On("Save", ctx, mock.Anything).Return(nil)

		// 创建服务
		svc := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)

		// 准备参数
		opts := DocumentOptions{
			Title:       "测试文档",
			Content:     "这是一个测试文档的内容",
			Description: "测试文档描述",
			ContentType: entity.ContentTypeMarkdown,
			AuthorID:    authorID,
			CategoryID:  categoryID,
			Tags:        []string{"测试", "文档"},
			Metadata: []entity.MetadataField{
				{
					Name:  "source",
					Value: "test",
				},
			},
		}

		// 转换为service.DocumentOptions
		serviceOpts := service.DocumentOptions{
			Title:       opts.Title,
			Content:     opts.Content,
			Description: opts.Description,
			ContentType: opts.ContentType,
			AuthorID:    opts.AuthorID,
			CategoryID:  opts.CategoryID,
			Tags:        opts.Tags,
			Metadata:    opts.Metadata,
		}

		// 执行方法
		doc, err := svc.CreateDocument(ctx, serviceOpts)

		// 断言
		assert.NoError(t, err)
		assert.NotNil(t, doc)
		assert.Equal(t, opts.Title, doc.Title)
		assert.Equal(t, opts.Content, doc.Content)
		assert.Equal(t, opts.Description, doc.Description)
		assert.Equal(t, opts.ContentType, doc.ContentType)
		assert.Equal(t, opts.AuthorID, doc.AuthorID)
		assert.Equal(t, opts.CategoryID, doc.CategoryID)
		assert.Equal(t, opts.Tags, doc.Tags)
		assert.Equal(t, entity.StatusDraft, doc.Status)
		assert.NotEmpty(t, doc.Chunks)

		// 验证模拟对象的调用
		mockCatRepo.AssertExpectations(t)
		mockTextSplitter.AssertExpectations(t)
		mockEmbeddingService.AssertExpectations(t)
		mockDocRepo.AssertExpectations(t)
	})

	t.Run("缺少必填参数", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)

		// 创建服务
		svc := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)

		// 测试缺少标题
		opts := DocumentOptions{
			Content:     "测试内容",
			AuthorID:    authorID,
			CategoryID:  categoryID,
			ContentType: entity.ContentTypeText,
		}

		serviceOpts := service.DocumentOptions{
			Content:     opts.Content,
			AuthorID:    opts.AuthorID,
			CategoryID:  opts.CategoryID,
			ContentType: opts.ContentType,
		}

		doc, err := svc.CreateDocument(ctx, serviceOpts)
		assert.Error(t, err)
		assert.Nil(t, doc)
		assert.Contains(t, err.Error(), "title is required")

		// 测试缺少内容
		opts = DocumentOptions{
			Title:       "测试标题",
			AuthorID:    authorID,
			CategoryID:  categoryID,
			ContentType: entity.ContentTypeText,
		}

		serviceOpts = service.DocumentOptions{
			Title:       opts.Title,
			AuthorID:    opts.AuthorID,
			CategoryID:  opts.CategoryID,
			ContentType: opts.ContentType,
		}

		doc, err = svc.CreateDocument(ctx, serviceOpts)
		assert.Error(t, err)
		assert.Nil(t, doc)
		assert.Contains(t, err.Error(), "content is required")

		// 测试缺少作者ID
		opts = DocumentOptions{
			Title:       "测试标题",
			Content:     "测试内容",
			CategoryID:  categoryID,
			ContentType: entity.ContentTypeText,
		}

		serviceOpts = service.DocumentOptions{
			Title:       opts.Title,
			Content:     opts.Content,
			CategoryID:  opts.CategoryID,
			ContentType: opts.ContentType,
		}

		doc, err = svc.CreateDocument(ctx, serviceOpts)
		assert.Error(t, err)
		assert.Nil(t, doc)
		assert.Contains(t, err.Error(), "author ID is required")

		// 测试缺少分类ID
		opts = DocumentOptions{
			Title:       "测试标题",
			Content:     "测试内容",
			AuthorID:    authorID,
			ContentType: entity.ContentTypeText,
		}

		serviceOpts = service.DocumentOptions{
			Title:       opts.Title,
			Content:     opts.Content,
			AuthorID:    opts.AuthorID,
			ContentType: opts.ContentType,
		}

		doc, err = svc.CreateDocument(ctx, serviceOpts)
		assert.Error(t, err)
		assert.Nil(t, doc)
		assert.Contains(t, err.Error(), "category ID is required")
	})

	t.Run("分类不存在", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)

		// 模拟分类不存在
		mockCatRepo.On("FindByID", ctx, categoryID).Return(nil, nil)

		// 创建服务
		svc := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)

		// 准备参数
		opts := DocumentOptions{
			Title:       "测试文档",
			Content:     "这是一个测试文档的内容",
			ContentType: entity.ContentTypeText,
			AuthorID:    authorID,
			CategoryID:  categoryID,
		}

		serviceOpts := service.DocumentOptions{
			Title:       opts.Title,
			Content:     opts.Content,
			ContentType: opts.ContentType,
			AuthorID:    opts.AuthorID,
			CategoryID:  opts.CategoryID,
		}

		// 执行方法
		doc, err := svc.CreateDocument(ctx, serviceOpts)

		// 断言
		assert.Error(t, err)
		assert.Nil(t, doc)
		assert.Contains(t, err.Error(), "category not found")

		// 验证模拟对象的调用
		mockCatRepo.AssertExpectations(t)
	})

	t.Run("分类查询失败", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)

		// 模拟分类查询失败
		mockCatRepo.On("FindByID", ctx, categoryID).Return(nil, errors.New("数据库错误"))

		// 创建服务
		svc := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)

		// 准备参数
		opts := DocumentOptions{
			Title:       "测试文档",
			Content:     "这是一个测试文档的内容",
			ContentType: entity.ContentTypeText,
			AuthorID:    authorID,
			CategoryID:  categoryID,
		}

		serviceOpts := service.DocumentOptions{
			Title:       opts.Title,
			Content:     opts.Content,
			ContentType: opts.ContentType,
			AuthorID:    opts.AuthorID,
			CategoryID:  opts.CategoryID,
		}

		// 执行方法
		doc, err := svc.CreateDocument(ctx, serviceOpts)

		// 断言
		assert.Error(t, err)
		assert.Nil(t, doc)
		assert.Contains(t, err.Error(), "failed to get category")

		// 验证模拟对象的调用
		mockCatRepo.AssertExpectations(t)
	})

	t.Run("文本分割失败", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)

		// 模拟分类存在
		category := mockCategory()
		category.ID = categoryID
		mockCatRepo.On("FindByID", ctx, categoryID).Return(category, nil)

		// 模拟文本分割失败
		mockTextSplitter.On("Split", mock.Anything, mock.Anything).Return([]entity.Chunk{}, errors.New("分割错误"))

		// 创建服务
		svc := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)

		// 准备参数
		opts := DocumentOptions{
			Title:       "测试文档",
			Content:     "这是一个测试文档的内容",
			ContentType: entity.ContentTypeText,
			AuthorID:    authorID,
			CategoryID:  categoryID,
		}

		serviceOpts := service.DocumentOptions{
			Title:       opts.Title,
			Content:     opts.Content,
			ContentType: opts.ContentType,
			AuthorID:    opts.AuthorID,
			CategoryID:  opts.CategoryID,
		}

		// 执行方法
		doc, err := svc.CreateDocument(ctx, serviceOpts)

		// 断言
		assert.Error(t, err)
		assert.Nil(t, doc)
		assert.Contains(t, err.Error(), "分割错误")

		// 验证模拟对象的调用
		mockCatRepo.AssertExpectations(t)
		mockTextSplitter.AssertExpectations(t)
	})

	t.Run("嵌入向量失败", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)

		// 模拟分类存在
		category := mockCategory()
		category.ID = categoryID
		mockCatRepo.On("FindByID", ctx, categoryID).Return(category, nil)

		// 模拟文本分割成功
		mockTextSplitter.On("Split", mock.Anything, mock.Anything).Return([]entity.Chunk{
			{
				Content: "测试内容块1",
			},
		}, nil)

		// 模拟嵌入向量失败
		mockEmbeddingService.On("GetBatchEmbeddings", ctx, mock.Anything).Return(nil, errors.New("嵌入错误"))

		// 创建服务
		svc := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)

		// 准备参数
		opts := DocumentOptions{
			Title:       "测试文档",
			Content:     "这是一个测试文档的内容",
			ContentType: entity.ContentTypeText,
			AuthorID:    authorID,
			CategoryID:  categoryID,
		}

		serviceOpts := service.DocumentOptions{
			Title:       opts.Title,
			Content:     opts.Content,
			ContentType: opts.ContentType,
			AuthorID:    opts.AuthorID,
			CategoryID:  opts.CategoryID,
		}

		// 执行方法
		doc, err := svc.CreateDocument(ctx, serviceOpts)

		// 断言
		assert.Error(t, err)
		assert.Nil(t, doc)
		assert.Contains(t, err.Error(), "嵌入错误")

		// 验证模拟对象的调用
		mockCatRepo.AssertExpectations(t)
		mockTextSplitter.AssertExpectations(t)
		mockEmbeddingService.AssertExpectations(t)
	})

	t.Run("保存文档失败", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)

		// 模拟分类存在
		category := mockCategory()
		category.ID = categoryID
		mockCatRepo.On("FindByID", ctx, categoryID).Return(category, nil)

		// 模拟文本分割
		mockTextSplitter.On("Split", mock.Anything, mock.Anything).Return([]entity.Chunk{
			{
				Content: "测试内容块1",
			},
		}, nil)

		// 模拟嵌入向量
		vectors := [][]float32{
			{0.1, 0.2, 0.3},
		}
		mockEmbeddingService.On("GetBatchEmbeddings", ctx, mock.Anything).Return(vectors, nil)

		// 模拟保存文档失败
		mockDocRepo.On("Save", ctx, mock.Anything).Return(errors.New("保存错误"))

		// 创建服务
		svc := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)

		// 准备参数
		opts := DocumentOptions{
			Title:       "测试文档",
			Content:     "这是一个测试文档的内容",
			ContentType: entity.ContentTypeText,
			AuthorID:    authorID,
			CategoryID:  categoryID,
		}

		serviceOpts := service.DocumentOptions{
			Title:       opts.Title,
			Content:     opts.Content,
			ContentType: opts.ContentType,
			AuthorID:    opts.AuthorID,
			CategoryID:  opts.CategoryID,
		}

		// 执行方法
		doc, err := svc.CreateDocument(ctx, serviceOpts)

		// 断言
		assert.Error(t, err)
		assert.Nil(t, doc)
		assert.Contains(t, err.Error(), "failed to save document")

		// 验证模拟对象的调用
		mockCatRepo.AssertExpectations(t)
		mockTextSplitter.AssertExpectations(t)
		mockEmbeddingService.AssertExpectations(t)
		mockDocRepo.AssertExpectations(t)
	})
}

// 测试GetDocumentByID方法
func TestDocumentService_GetDocumentByID(t *testing.T) {
	// 准备测试数据
	ctx := context.Background()
	docID := uuid.New()
	
	t.Run("获取文档成功", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)
		
		// 模拟文档存在
		doc := &entity.Document{
			ID:          docID,
			Title:       "测试文档",
			Content:     "这是一个测试文档的内容",
			ContentType: entity.ContentTypeText,
		}
		mockDocRepo.On("FindByID", ctx, docID).Return(doc, nil)
		
		// 创建服务
		service := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)
		
		// 执行方法
		result, err := service.GetDocumentByID(ctx, docID)
		
		// 断言
		assert.NoError(t, err)
		assert.NotNil(t, result)
		assert.Equal(t, doc, result)
		
		// 验证模拟对象的调用
		mockDocRepo.AssertExpectations(t)
	})
	
	t.Run("文档不存在", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)
		
		// 模拟文档不存在
		mockDocRepo.On("FindByID", ctx, docID).Return(nil, nil)
		
		// 创建服务
		service := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)
		
		// 执行方法
		result, err := service.GetDocumentByID(ctx, docID)
		
		// 断言
		assert.NoError(t, err)
		assert.Nil(t, result)
		
		// 验证模拟对象的调用
		mockDocRepo.AssertExpectations(t)
	})
	
	t.Run("查询错误", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)
		
		// 模拟查询错误
		mockDocRepo.On("FindByID", ctx, docID).Return(nil, errors.New("数据库错误"))
		
		// 创建服务
		service := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)
		
		// 执行方法
		result, err := service.GetDocumentByID(ctx, docID)
		
		// 断言
		assert.Error(t, err)
		assert.Nil(t, result)
		assert.Contains(t, err.Error(), "数据库错误")
		
		// 验证模拟对象的调用
		mockDocRepo.AssertExpectations(t)
	})
}

// 测试PublishDocument方法
func TestDocumentService_PublishDocument(t *testing.T) {
	// 准备测试数据
	ctx := context.Background()
	docID := uuid.New()
	
	t.Run("发布文档成功", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)
		
		// 模拟文档存在
		doc := &entity.Document{
			ID:          docID,
			Title:       "测试文档",
			Content:     "这是一个测试文档的内容",
			ContentType: entity.ContentTypeText,
			Status:      entity.StatusDraft,
		}
		mockDocRepo.On("FindByID", ctx, docID).Return(doc, nil)
		
		// 模拟更新文档
		mockDocRepo.On("Update", ctx, mock.MatchedBy(func(d *entity.Document) bool {
			return d.ID == docID && d.Status == entity.StatusPublished
		})).Return(nil)
		
		// 创建服务
		service := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)
		
		// 执行方法
		err := service.PublishDocument(ctx, docID)
		
		// 断言
		assert.NoError(t, err)
		
		// 验证模拟对象的调用
		mockDocRepo.AssertExpectations(t)
	})
	
	t.Run("文档不存在", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)
		
		// 模拟文档不存在
		mockDocRepo.On("FindByID", ctx, docID).Return(nil, nil)
		
		// 创建服务
		service := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)
		
		// 执行方法
		err := service.PublishDocument(ctx, docID)
		
		// 断言
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "文档不存在")
		
		// 验证模拟对象的调用
		mockDocRepo.AssertExpectations(t)
	})
	
	t.Run("更新失败", func(t *testing.T) {
		// 初始化模拟对象
		mockDocRepo := new(MockDocumentRepository)
		mockCatRepo := new(MockCategoryRepository)
		mockTextSplitter := new(MockTextSplitter)
		mockEmbeddingService := new(MockEmbeddingService)
		
		// 模拟文档存在
		doc := &entity.Document{
			ID:          docID,
			Title:       "测试文档",
			Content:     "这是一个测试文档的内容",
			ContentType: entity.ContentTypeText,
			Status:      entity.StatusDraft,
		}
		mockDocRepo.On("FindByID", ctx, docID).Return(doc, nil)
		
		// 模拟更新失败
		mockDocRepo.On("Update", ctx, mock.Anything).Return(errors.New("更新错误"))
		
		// 创建服务
		service := service.NewDocumentService(mockDocRepo, mockCatRepo, mockTextSplitter, mockEmbeddingService)
		
		// 执行方法
		err := service.PublishDocument(ctx, docID)
		
		// 断言
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "更新文档状态失败")
		
		// 验证模拟对象的调用
		mockDocRepo.AssertExpectations(t)
	})
} 