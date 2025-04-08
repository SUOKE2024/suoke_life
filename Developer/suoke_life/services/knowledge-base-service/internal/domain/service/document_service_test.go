package service_test

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/domain/service"
	"knowledge-base-service/internal/test/mocks"
)

func TestDocumentService_GetDocumentByID(t *testing.T) {
	// 设置测试用例
	testCases := []struct {
		name          string
		documentID    uuid.UUID
		mockSetup     func(*mocks.MockDocumentRepository)
		expectedError bool
		expectedDoc   *entity.Document
	}{
		{
			name:       "成功获取文档",
			documentID: uuid.New(),
			mockSetup: func(repo *mocks.MockDocumentRepository) {
				doc := &entity.Document{
					ID:        uuid.New(),
					Title:     "测试文档",
					Content:   "测试内容",
					Status:    entity.StatusPublished,
					CreatedAt: time.Now(),
					UpdatedAt: time.Now(),
				}

				repo.On("FindByID", mock.Anything, mock.Anything).Return(doc, nil)
			},
			expectedError: false,
			expectedDoc:   &entity.Document{}, // 添加期望的文档，而不是nil
		},
		{
			name:       "文档不存在",
			documentID: uuid.New(),
			mockSetup: func(repo *mocks.MockDocumentRepository) {
				repo.On("FindByID", mock.Anything, mock.Anything).Return(nil, nil)
			},
			expectedError: false,
			expectedDoc:   nil,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// 初始化模拟对象
			mockRepo := new(mocks.MockDocumentRepository)
			mockCategoryRepo := new(mocks.MockCategoryRepository)
			mockTextSplitter := new(mocks.MockTextSplitter)
			mockEmbeddingService := new(mocks.MockEmbeddingService)

			// 设置模拟行为
			tc.mockSetup(mockRepo)

			// 创建服务实例
			svc := service.NewDocumentService(
				mockRepo,
				mockCategoryRepo,
				mockTextSplitter,
				mockEmbeddingService,
			)

			// 执行测试函数
			doc, err := svc.GetDocumentByID(context.Background(), tc.documentID)

			// 断言结果
			if tc.expectedError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				if tc.expectedDoc == nil {
					assert.Nil(t, doc)
				} else {
					assert.NotNil(t, doc)
				}
			}

			// 验证模拟对象的方法是否按预期被调用
			mockRepo.AssertExpectations(t)
		})
	}
}

func TestDocumentService_CreateDocument(t *testing.T) {
	// 设置测试用例
	testCases := []struct {
		name          string
		options       service.DocumentOptions
		mockSetup     func(*mocks.MockDocumentRepository, *mocks.MockCategoryRepository, *mocks.MockTextSplitter, *mocks.MockEmbeddingService)
		expectedError bool
	}{
		{
			name: "成功创建文档",
			options: service.DocumentOptions{
				Title:       "测试文档",
				Content:     "测试内容",
				ContentType: entity.ContentTypeText,
				AuthorID:    uuid.New(),
				CategoryID:  uuid.New(),
				Tags:        []string{"测试"},
			},
			mockSetup: func(repo *mocks.MockDocumentRepository, categoryRepo *mocks.MockCategoryRepository, splitter *mocks.MockTextSplitter, embedder *mocks.MockEmbeddingService) {
				// 设置分类查询行为
				category := &entity.Category{
					ID:   uuid.New(),
					Name: "测试分类",
				}
				categoryRepo.On("FindByID", mock.Anything, mock.Anything).Return(category, nil)

				// 设置文本分割行为
				chunks := []entity.Chunk{
					{
						Content:    "测试内容",
						Offset:     0,
						Length:     12,
						TokenCount: 4,
					},
				}
				splitter.On("Split", mock.Anything, mock.Anything).Return(chunks, nil)

				// 设置嵌入行为
				embedder.On("GetBatchEmbeddings", mock.Anything, []string{"测试内容"}).Return([][]float32{{0.1, 0.2, 0.3}}, nil)

				// 设置保存行为
				repo.On("Save", mock.Anything, mock.Anything).Return(nil)
			},
			expectedError: false,
		},
		{
			name: "标题为空",
			options: service.DocumentOptions{
				Title:       "",
				Content:     "测试内容",
				ContentType: entity.ContentTypeText,
				AuthorID:    uuid.New(),
				CategoryID:  uuid.New(),
			},
			mockSetup: func(repo *mocks.MockDocumentRepository, categoryRepo *mocks.MockCategoryRepository, splitter *mocks.MockTextSplitter, embedder *mocks.MockEmbeddingService) {
				// 不设置任何行为，因为应该在验证阶段失败
			},
			expectedError: true,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// 初始化模拟对象
			mockRepo := new(mocks.MockDocumentRepository)
			mockCategoryRepo := new(mocks.MockCategoryRepository)
			mockTextSplitter := new(mocks.MockTextSplitter)
			mockEmbeddingService := new(mocks.MockEmbeddingService)

			// 设置模拟行为
			tc.mockSetup(mockRepo, mockCategoryRepo, mockTextSplitter, mockEmbeddingService)

			// 创建服务实例
			svc := service.NewDocumentService(
				mockRepo,
				mockCategoryRepo,
				mockTextSplitter,
				mockEmbeddingService,
			)

			// 执行测试函数
			doc, err := svc.CreateDocument(context.Background(), tc.options)

			// 断言结果
			if tc.expectedError {
				assert.Error(t, err)
				assert.Nil(t, doc)
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, doc)
				assert.Equal(t, tc.options.Title, doc.Title)
				assert.Equal(t, tc.options.Content, doc.Content)
				assert.Equal(t, tc.options.ContentType, doc.ContentType)
				assert.Equal(t, tc.options.AuthorID, doc.AuthorID)
				assert.Equal(t, tc.options.CategoryID, doc.CategoryID)
				assert.Equal(t, tc.options.Tags, doc.Tags)
				assert.Equal(t, entity.StatusDraft, doc.Status)
			}
		})
	}
}

func TestDocumentService_SemanticSearch(t *testing.T) {
	// 设置测试用例
	mockDocuments := []*entity.Document{
		{
			ID:          uuid.New(),
			Title:       "测试文档1",
			Content:     "测试内容1",
			ContentType: entity.ContentTypeText,
			Status:      entity.StatusPublished,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		},
		{
			ID:          uuid.New(),
			Title:       "测试文档2",
			Content:     "测试内容2",
			ContentType: entity.ContentTypeText,
			Status:      entity.StatusPublished,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		},
	}

	// 创建测试上下文
	ctx := context.Background()

	// 初始化模拟对象
	mockRepo := new(mocks.MockDocumentRepository)
	mockCategoryRepo := new(mocks.MockCategoryRepository)
	mockTextSplitter := new(mocks.MockTextSplitter)
	mockEmbeddingService := new(mocks.MockEmbeddingService)

	// 设置模拟行为
	mockRepo.On("SemanticSearch", mock.Anything, "健康生活", 5).Return(mockDocuments, nil)

	// 创建服务实例
	svc := service.NewDocumentService(
		mockRepo,
		mockCategoryRepo,
		mockTextSplitter,
		mockEmbeddingService,
	)

	// 执行测试函数
	docs, err := svc.SemanticSearch(ctx, "健康生活", 5)

	// 断言结果
	assert.NoError(t, err)
	assert.NotNil(t, docs)
	assert.Equal(t, 2, len(docs))
	assert.Equal(t, mockDocuments[0].Title, docs[0].Title)
	assert.Equal(t, mockDocuments[1].Title, docs[1].Title)

	// 验证模拟对象的方法是否按预期被调用
	mockRepo.AssertExpectations(t)
}
