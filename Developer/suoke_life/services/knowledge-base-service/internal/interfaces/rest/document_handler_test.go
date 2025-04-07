package rest_test

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/domain/service"
	"knowledge-base-service/internal/domain/service/interfaces"
	"knowledge-base-service/internal/interfaces/rest"
	"knowledge-base-service/internal/test"
)

// MockDocumentService 模拟文档服务
type MockDocumentService struct {
	mock.Mock
}

// 确保 MockDocumentService 实现了 interfaces.DocumentService 接口
var _ interfaces.DocumentService = (*MockDocumentService)(nil)

func (m *MockDocumentService) GetDocumentByID(ctx context.Context, id uuid.UUID) (*entity.Document, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entity.Document), args.Error(1)
}

func (m *MockDocumentService) GetDocumentsByCategory(ctx context.Context, categoryID uuid.UUID) ([]*entity.Document, error) {
	args := m.Called(ctx, categoryID)
	return args.Get(0).([]*entity.Document), args.Error(1)
}

func (m *MockDocumentService) GetDocumentsByTags(ctx context.Context, tags []string) ([]*entity.Document, error) {
	args := m.Called(ctx, tags)
	return args.Get(0).([]*entity.Document), args.Error(1)
}

func (m *MockDocumentService) SearchDocuments(ctx context.Context, query string) ([]*entity.Document, error) {
	args := m.Called(ctx, query)
	return args.Get(0).([]*entity.Document), args.Error(1)
}

func (m *MockDocumentService) SemanticSearch(ctx context.Context, query string, limit int) ([]*entity.Document, error) {
	args := m.Called(ctx, query, limit)
	return args.Get(0).([]*entity.Document), args.Error(1)
}

func (m *MockDocumentService) CreateDocument(ctx context.Context, opts service.DocumentOptions) (*entity.Document, error) {
	args := m.Called(ctx, opts)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entity.Document), args.Error(1)
}

func (m *MockDocumentService) UpdateDocument(ctx context.Context, id uuid.UUID, title, content, description string, contentType entity.ContentType, categoryID uuid.UUID, tags []string) (*entity.Document, error) {
	args := m.Called(ctx, id, title, content, description, contentType, categoryID, tags)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*entity.Document), args.Error(1)
}

func (m *MockDocumentService) PublishDocument(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockDocumentService) ArchiveDocument(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockDocumentService) DeleteDocument(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockDocumentService) RegisterDocumentOnBlockchain(ctx context.Context, id uuid.UUID) (string, error) {
	args := m.Called(ctx, id)
	return args.String(0), args.Error(1)
}

// 创建路由器和处理器
func setupTestRouter(mockService *MockDocumentService) *chi.Mux {
	r := chi.NewRouter()
	handler := rest.NewDocumentHandler(mockService)
	handler.RegisterRoutes(r)
	return r
}

// 测试用例

func TestDocumentHandler_GetDocument_Success(t *testing.T) {
	// 设置模拟服务
	mockService := new(MockDocumentService)
	router := setupTestRouter(mockService)

	// 测试数据
	docID := uuid.New()
	testDoc := test.GenerateTestDocument()
	testDoc.ID = docID

	// 设置期望行为
	mockService.On("GetDocumentByID", mock.Anything, docID).Return(testDoc, nil)

	// 创建请求
	req, _ := http.NewRequest("GET", fmt.Sprintf("/documents/%s", docID.String()), nil)
	rr := httptest.NewRecorder()

	// 处理请求
	router.ServeHTTP(rr, req)

	// 验证响应
	assert.Equal(t, http.StatusOK, rr.Code)

	var response map[string]interface{}
	err := json.Unmarshal(rr.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Equal(t, docID.String(), response["id"])
	assert.Equal(t, testDoc.Title, response["title"])
	mockService.AssertExpectations(t)
}

func TestDocumentHandler_GetDocument_NotFound(t *testing.T) {
	// 设置模拟服务
	mockService := new(MockDocumentService)
	router := setupTestRouter(mockService)

	// 测试数据
	docID := uuid.New()

	// 设置期望行为
	mockService.On("GetDocumentByID", mock.Anything, docID).Return(nil, nil)

	// 创建请求
	req, _ := http.NewRequest("GET", fmt.Sprintf("/documents/%s", docID.String()), nil)
	rr := httptest.NewRecorder()

	// 处理请求
	router.ServeHTTP(rr, req)

	// 验证响应
	assert.Equal(t, http.StatusNotFound, rr.Code)

	var response map[string]interface{}
	err := json.Unmarshal(rr.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Contains(t, response["error"], "文档不存在")
	mockService.AssertExpectations(t)
}

func TestDocumentHandler_GetDocument_InvalidID(t *testing.T) {
	// 设置模拟服务
	mockService := new(MockDocumentService)
	router := setupTestRouter(mockService)

	// 创建请求 - 使用无效的UUID格式
	req, _ := http.NewRequest("GET", "/documents/invalid-uuid", nil)
	rr := httptest.NewRecorder()

	// 处理请求
	router.ServeHTTP(rr, req)

	// 验证响应
	assert.Equal(t, http.StatusBadRequest, rr.Code)

	var response map[string]interface{}
	err := json.Unmarshal(rr.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Contains(t, response["error"], "无效的文档ID格式")
}

func TestDocumentHandler_CreateDocument_Success(t *testing.T) {
	// 设置模拟服务
	mockService := new(MockDocumentService)
	router := setupTestRouter(mockService)

	// 测试数据
	authorID := uuid.New()
	categoryID := uuid.New()
	docID := uuid.New()

	// 请求数据
	requestData := map[string]interface{}{
		"title":        "Test Document",
		"content":      "This is test content",
		"description":  "Test description",
		"content_type": "text",
		"author_id":    authorID.String(),
		"category_id":  categoryID.String(),
		"tags":         []string{"test", "api"},
	}

	// 预期的文档
	expectedDoc := test.GenerateTestDocumentWithContent("Test Document", "This is test content")
	expectedDoc.ID = docID
	expectedDoc.AuthorID = authorID
	expectedDoc.CategoryID = categoryID
	expectedDoc.Tags = []string{"test", "api"}
	expectedDoc.Description = "Test description"

	// 设置期望行为 - 匹配任何DocumentOptions参数
	mockService.On("CreateDocument", mock.Anything, mock.MatchedBy(func(opts service.DocumentOptions) bool {
		return opts.Title == "Test Document" &&
			opts.Content == "This is test content" &&
			opts.AuthorID == authorID &&
			opts.CategoryID == categoryID
	})).Return(expectedDoc, nil)

	// 创建请求
	requestBody, _ := json.Marshal(requestData)
	req, _ := http.NewRequest("POST", "/documents", bytes.NewBuffer(requestBody))
	req.Header.Set("Content-Type", "application/json")
	rr := httptest.NewRecorder()

	// 处理请求
	router.ServeHTTP(rr, req)

	// 验证响应
	assert.Equal(t, http.StatusCreated, rr.Code)

	var response map[string]interface{}
	err := json.Unmarshal(rr.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Equal(t, docID.String(), response["id"])
	assert.Equal(t, "Test Document", response["title"])
	assert.Equal(t, "Test description", response["description"])
	mockService.AssertExpectations(t)
}

func TestDocumentHandler_CreateDocument_MissingRequiredFields(t *testing.T) {
	// 设置模拟服务
	mockService := new(MockDocumentService)
	router := setupTestRouter(mockService)

	// 测试数据 - 缺少必填字段
	requestData := map[string]interface{}{
		"title":       "Test Document",
		// 缺少content
		"description": "Test description",
		// 缺少author_id
		"category_id": uuid.New().String(),
	}

	// 创建请求
	requestBody, _ := json.Marshal(requestData)
	req, _ := http.NewRequest("POST", "/documents", bytes.NewBuffer(requestBody))
	req.Header.Set("Content-Type", "application/json")
	rr := httptest.NewRecorder()

	// 处理请求
	router.ServeHTTP(rr, req)

	// 验证响应
	assert.Equal(t, http.StatusBadRequest, rr.Code)

	var response map[string]interface{}
	err := json.Unmarshal(rr.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Contains(t, response["error"].(string), "必填项")
}

func TestDocumentHandler_CreateDocument_InvalidUUID(t *testing.T) {
	// 设置模拟服务
	mockService := new(MockDocumentService)
	router := setupTestRouter(mockService)

	// 测试数据 - 无效的UUID
	requestData := map[string]interface{}{
		"title":       "Test Document",
		"content":     "This is test content",
		"author_id":   "invalid-uuid",
		"category_id": uuid.New().String(),
	}

	// 创建请求
	requestBody, _ := json.Marshal(requestData)
	req, _ := http.NewRequest("POST", "/documents", bytes.NewBuffer(requestBody))
	req.Header.Set("Content-Type", "application/json")
	rr := httptest.NewRecorder()

	// 处理请求
	router.ServeHTTP(rr, req)

	// 验证响应
	assert.Equal(t, http.StatusBadRequest, rr.Code)

	var response map[string]interface{}
	err := json.Unmarshal(rr.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Contains(t, response["error"].(string), "无效的作者ID格式")
}

func TestDocumentHandler_UpdateDocument_Success(t *testing.T) {
	// 设置模拟服务
	mockService := new(MockDocumentService)
	router := setupTestRouter(mockService)

	// 测试数据
	docID := uuid.New()
	categoryID := uuid.New()

	// 请求数据
	requestData := map[string]interface{}{
		"title":       "Updated Title",
		"content":     "Updated content",
		"category_id": categoryID.String(),
		"tags":        []string{"updated", "tag"},
	}

	// 预期的文档
	expectedDoc := test.GenerateTestDocumentWithContent("Updated Title", "Updated content")
	expectedDoc.ID = docID
	expectedDoc.CategoryID = categoryID
	expectedDoc.Tags = []string{"updated", "tag"}

	// 设置期望行为
	mockService.On(
		"UpdateDocument",
		mock.Anything,
		docID,
		"Updated Title",
		"Updated content",
		"",  // 空描述
		entity.ContentType(""),  // 使用正确的ContentType类型
		categoryID,
		[]string{"updated", "tag"},
	).Return(expectedDoc, nil)

	// 创建请求
	requestBody, _ := json.Marshal(requestData)
	req, _ := http.NewRequest("PUT", fmt.Sprintf("/documents/%s", docID.String()), bytes.NewBuffer(requestBody))
	req.Header.Set("Content-Type", "application/json")
	rr := httptest.NewRecorder()

	// 处理请求
	router.ServeHTTP(rr, req)

	// 验证响应
	assert.Equal(t, http.StatusOK, rr.Code)

	var response map[string]interface{}
	err := json.Unmarshal(rr.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Equal(t, docID.String(), response["id"])
	assert.Equal(t, "Updated Title", response["title"])
	mockService.AssertExpectations(t)
}

func TestDocumentHandler_DeleteDocument_Success(t *testing.T) {
	// 设置模拟服务
	mockService := new(MockDocumentService)
	router := setupTestRouter(mockService)

	// 测试数据
	docID := uuid.New()

	// 设置期望行为
	mockService.On("DeleteDocument", mock.Anything, docID).Return(nil)

	// 创建请求
	req, _ := http.NewRequest("DELETE", fmt.Sprintf("/documents/%s", docID.String()), nil)
	rr := httptest.NewRecorder()

	// 处理请求
	router.ServeHTTP(rr, req)

	// 验证响应
	assert.Equal(t, http.StatusNoContent, rr.Code)
	mockService.AssertExpectations(t)
}

func TestDocumentHandler_PublishDocument_Success(t *testing.T) {
	// 设置模拟服务
	mockService := new(MockDocumentService)
	router := setupTestRouter(mockService)

	// 测试数据
	docID := uuid.New()
	testDoc := test.GenerateTestDocument()
	testDoc.ID = docID
	testDoc.Publish() // 设置为已发布状态

	// 设置期望行为
	mockService.On("PublishDocument", mock.Anything, docID).Return(nil)
	mockService.On("GetDocumentByID", mock.Anything, docID).Return(testDoc, nil)

	// 创建请求
	req, _ := http.NewRequest("POST", fmt.Sprintf("/documents/%s/publish", docID.String()), nil)
	rr := httptest.NewRecorder()

	// 处理请求
	router.ServeHTTP(rr, req)

	// 验证响应
	assert.Equal(t, http.StatusOK, rr.Code)

	var response map[string]interface{}
	err := json.Unmarshal(rr.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Equal(t, docID.String(), response["id"])
	assert.Equal(t, string(entity.StatusPublished), response["status"])
	mockService.AssertExpectations(t)
}

func TestDocumentHandler_RegisterOnBlockchain_Success(t *testing.T) {
	// 设置模拟服务
	mockService := new(MockDocumentService)
	router := setupTestRouter(mockService)

	// 测试数据
	docID := uuid.New()
	txHash := "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"

	// 设置期望行为
	mockService.On("RegisterDocumentOnBlockchain", mock.Anything, docID).Return(txHash, nil)

	// 创建请求
	req, _ := http.NewRequest("POST", fmt.Sprintf("/documents/%s/blockchain", docID.String()), nil)
	rr := httptest.NewRecorder()

	// 处理请求
	router.ServeHTTP(rr, req)

	// 验证响应
	assert.Equal(t, http.StatusOK, rr.Code)

	var response map[string]interface{}
	err := json.Unmarshal(rr.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Equal(t, txHash, response["tx_hash"])
	assert.Contains(t, response["message"], "已在区块链上注册")
	mockService.AssertExpectations(t)
}

func TestDocumentHandler_SearchDocuments_Success(t *testing.T) {
	// 设置模拟服务
	mockService := new(MockDocumentService)
	router := setupTestRouter(mockService)

	// 测试数据
	query := "test query"
	testDocs := []*entity.Document{
		test.GenerateTestDocument(),
		test.GenerateTestDocument(),
	}

	// 设置期望行为
	mockService.On("SearchDocuments", mock.Anything, query).Return(testDocs, nil)

	// 创建请求
	req, _ := http.NewRequest("GET", "/documents/search?q="+query, nil)
	rr := httptest.NewRecorder()

	// 处理请求
	router.ServeHTTP(rr, req)

	// 验证响应
	assert.Equal(t, http.StatusOK, rr.Code)

	var response []map[string]interface{}
	err := json.Unmarshal(rr.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Len(t, response, 2)
	mockService.AssertExpectations(t)
}

func TestDocumentHandler_SemanticSearch_Success(t *testing.T) {
	// 设置模拟服务
	mockService := new(MockDocumentService)
	router := setupTestRouter(mockService)

	// 测试数据
	query := "semantic query"
	testDocs := []*entity.Document{
		test.GenerateTestDocument(),
		test.GenerateTestDocument(),
	}

	// 设置期望行为 - 使用默认限制10
	mockService.On("SemanticSearch", mock.Anything, query, 10).Return(testDocs, nil)

	// 创建请求
	req, _ := http.NewRequest("GET", "/documents/semantic-search?q="+query, nil)
	rr := httptest.NewRecorder()

	// 处理请求
	router.ServeHTTP(rr, req)

	// 验证响应
	assert.Equal(t, http.StatusOK, rr.Code)

	var response []map[string]interface{}
	err := json.Unmarshal(rr.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Len(t, response, 2)
	mockService.AssertExpectations(t)
}

func TestDocumentHandler_GetDocument(t *testing.T) {
	// 创建一个测试用的文档ID
	docID := uuid.New()
	
	t.Run("获取文档成功", func(t *testing.T) {
		// 创建模拟服务
		mockService := new(MockDocumentService)
		
		// 创建一个测试文档
		testDoc := &entity.Document{
			ID:          docID,
			Title:       "测试文档",
			Content:     "这是一个测试文档的内容",
			Description: "测试文档的描述",
			ContentType: entity.ContentTypeMarkdown,
			Status:      entity.StatusPublished,
			AuthorID:    uuid.New(),
			CategoryID:  uuid.New(),
			Tags:        []string{"测试", "文档"},
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}
		
		// 设置模拟行为
		mockService.On("GetDocumentByID", mock.Anything, docID).Return(testDoc, nil)
		
		// 创建处理器
		handler := rest.NewDocumentHandler(mockService)
		
		// 创建请求
		req, _ := http.NewRequest("GET", "/documents/"+docID.String(), nil)
		
		// 设置Chi路由上下文
		rctx := chi.NewRouteContext()
		rctx.URLParams.Add("id", docID.String())
		req = req.WithContext(context.WithValue(req.Context(), chi.RouteCtxKey, rctx))
		
		// 创建响应记录器
		rr := httptest.NewRecorder()
		
		// 调用处理器
		handler.GetDocument(rr, req)
		
		// 检查状态码
		assert.Equal(t, http.StatusOK, rr.Code)
		
		// 解析响应
		var response rest.DocumentResponse
		err := json.Unmarshal(rr.Body.Bytes(), &response)
		assert.NoError(t, err)
		
		// 验证响应内容
		assert.Equal(t, docID.String(), response.ID)
		assert.Equal(t, "测试文档", response.Title)
		assert.Equal(t, "这是一个测试文档的内容", response.Content)
		assert.Equal(t, "测试文档的描述", response.Description)
		assert.Equal(t, "markdown", response.ContentType)
		assert.Equal(t, "published", response.Status)
		
		// 验证模拟行为
		mockService.AssertExpectations(t)
	})
	
	t.Run("无效的ID格式", func(t *testing.T) {
		// 创建模拟服务
		mockService := new(MockDocumentService)
		
		// 创建处理器
		handler := rest.NewDocumentHandler(mockService)
		
		// 创建请求 - 使用无效的ID
		req, _ := http.NewRequest("GET", "/documents/invalid-id", nil)
		
		// 设置Chi路由上下文
		rctx := chi.NewRouteContext()
		rctx.URLParams.Add("id", "invalid-id")
		req = req.WithContext(context.WithValue(req.Context(), chi.RouteCtxKey, rctx))
		
		// 创建响应记录器
		rr := httptest.NewRecorder()
		
		// 调用处理器
		handler.GetDocument(rr, req)
		
		// 检查状态码
		assert.Equal(t, http.StatusBadRequest, rr.Code)
		
		// 解析响应
		var response rest.ErrorResponse
		err := json.Unmarshal(rr.Body.Bytes(), &response)
		assert.NoError(t, err)
		
		// 验证错误消息
		assert.Contains(t, response.Error, "无效的文档ID格式")
	})
	
	t.Run("文档不存在", func(t *testing.T) {
		// 创建模拟服务
		mockService := new(MockDocumentService)
		
		// 设置模拟行为 - 文档不存在
		mockService.On("GetDocumentByID", mock.Anything, docID).Return(nil, nil)
		
		// 创建处理器
		handler := rest.NewDocumentHandler(mockService)
		
		// 创建请求
		req, _ := http.NewRequest("GET", "/documents/"+docID.String(), nil)
		
		// 设置Chi路由上下文
		rctx := chi.NewRouteContext()
		rctx.URLParams.Add("id", docID.String())
		req = req.WithContext(context.WithValue(req.Context(), chi.RouteCtxKey, rctx))
		
		// 创建响应记录器
		rr := httptest.NewRecorder()
		
		// 调用处理器
		handler.GetDocument(rr, req)
		
		// 检查状态码
		assert.Equal(t, http.StatusNotFound, rr.Code)
		
		// 解析响应
		var response rest.ErrorResponse
		err := json.Unmarshal(rr.Body.Bytes(), &response)
		assert.NoError(t, err)
		
		// 验证错误消息
		assert.Contains(t, response.Error, "文档不存在")
		
		// 验证模拟行为
		mockService.AssertExpectations(t)
	})
	
	t.Run("服务错误", func(t *testing.T) {
		// 创建模拟服务
		mockService := new(MockDocumentService)
		
		// 设置模拟行为 - 服务返回错误
		mockService.On("GetDocumentByID", mock.Anything, docID).Return(nil, fmt.Errorf("数据库错误"))
		
		// 创建处理器
		handler := rest.NewDocumentHandler(mockService)
		
		// 创建请求
		req, _ := http.NewRequest("GET", "/documents/"+docID.String(), nil)
		
		// 设置Chi路由上下文
		rctx := chi.NewRouteContext()
		rctx.URLParams.Add("id", docID.String())
		req = req.WithContext(context.WithValue(req.Context(), chi.RouteCtxKey, rctx))
		
		// 创建响应记录器
		rr := httptest.NewRecorder()
		
		// 调用处理器
		handler.GetDocument(rr, req)
		
		// 检查状态码
		assert.Equal(t, http.StatusInternalServerError, rr.Code)
		
		// 解析响应
		var response rest.ErrorResponse
		err := json.Unmarshal(rr.Body.Bytes(), &response)
		assert.NoError(t, err)
		
		// 验证错误消息
		assert.Contains(t, response.Error, "获取文档失败")
		assert.Contains(t, response.Error, "数据库错误")
		
		// 验证模拟行为
		mockService.AssertExpectations(t)
	})
}

func TestDocumentHandler_CreateDocument(t *testing.T) {
	t.Run("创建文档成功", func(t *testing.T) {
		// 创建模拟服务
		mockService := new(MockDocumentService)
		
		// 准备测试数据
		authorID := uuid.New()
		categoryID := uuid.New()
		
		// 创建请求体
		reqBody := rest.CreateDocumentRequest{
			Title:       "测试文档",
			Description: "测试文档的描述",
			Content:     "这是一个测试文档的内容",
			ContentType: "markdown",
			AuthorID:    authorID.String(),
			CategoryID:  categoryID.String(),
			Tags:        []string{"测试", "文档"},
		}
		
		// 转换为JSON
		jsonBody, _ := json.Marshal(reqBody)
		
		// 创建一个测试文档用于模拟返回
		testDoc := &entity.Document{
			ID:          uuid.New(),
			Title:       reqBody.Title,
			Description: reqBody.Description,
			Content:     reqBody.Content,
			ContentType: entity.ContentType(reqBody.ContentType),
			Status:      entity.StatusDraft,
			AuthorID:    authorID,
			CategoryID:  categoryID,
			Tags:        reqBody.Tags,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}
		
		// 设置模拟行为 - 匹配DocumentOptions参数
		mockService.On("CreateDocument", mock.Anything, mock.MatchedBy(func(opts service.DocumentOptions) bool {
			return opts.Title == reqBody.Title &&
				opts.Description == reqBody.Description &&
				opts.Content == reqBody.Content &&
				string(opts.ContentType) == reqBody.ContentType &&
				opts.AuthorID == authorID &&
				opts.CategoryID == categoryID
		})).Return(testDoc, nil)
		
		// 创建处理器
		handler := rest.NewDocumentHandler(mockService)
		
		// 创建请求
		req, _ := http.NewRequest("POST", "/documents", bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
		
		// 创建响应记录器
		rr := httptest.NewRecorder()
		
		// 调用处理器
		handler.CreateDocument(rr, req)
		
		// 检查状态码
		assert.Equal(t, http.StatusCreated, rr.Code)
		
		// 解析响应
		var response rest.DocumentResponse
		err := json.Unmarshal(rr.Body.Bytes(), &response)
		assert.NoError(t, err)
		
		// 验证响应内容
		assert.Equal(t, testDoc.ID.String(), response.ID)
		assert.Equal(t, reqBody.Title, response.Title)
		assert.Equal(t, reqBody.Content, response.Content)
		assert.Equal(t, reqBody.Description, response.Description)
		assert.Equal(t, reqBody.ContentType, response.ContentType)
		assert.Equal(t, "draft", response.Status)
		assert.Equal(t, reqBody.AuthorID, response.AuthorID)
		assert.Equal(t, reqBody.CategoryID, response.CategoryID)
		
		// 验证模拟行为
		mockService.AssertExpectations(t)
	})
	
	t.Run("请求体解析失败", func(t *testing.T) {
		// 创建模拟服务
		mockService := new(MockDocumentService)
		
		// 创建处理器
		handler := rest.NewDocumentHandler(mockService)
		
		// 创建请求 - 无效的JSON
		req, _ := http.NewRequest("POST", "/documents", bytes.NewBufferString("invalid json"))
		req.Header.Set("Content-Type", "application/json")
		
		// 创建响应记录器
		rr := httptest.NewRecorder()
		
		// 调用处理器
		handler.CreateDocument(rr, req)
		
		// 检查状态码
		assert.Equal(t, http.StatusBadRequest, rr.Code)
		
		// 解析响应
		var response rest.ErrorResponse
		err := json.Unmarshal(rr.Body.Bytes(), &response)
		assert.NoError(t, err)
		
		// 验证错误消息
		assert.Contains(t, response.Error, "解析请求失败")
	})
	
	t.Run("缺少必填字段", func(t *testing.T) {
		// 创建模拟服务
		mockService := new(MockDocumentService)
		
		// 创建处理器
		handler := rest.NewDocumentHandler(mockService)
		
		// 创建请求体 - 缺少必填字段
		reqBody := rest.CreateDocumentRequest{
			Title:       "", // 缺少标题
			Content:     "内容",
			AuthorID:    uuid.New().String(),
			CategoryID:  uuid.New().String(),
			ContentType: "text",
		}
		
		// 转换为JSON
		jsonBody, _ := json.Marshal(reqBody)
		
		// 创建请求
		req, _ := http.NewRequest("POST", "/documents", bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
		
		// 创建响应记录器
		rr := httptest.NewRecorder()
		
		// 调用处理器
		handler.CreateDocument(rr, req)
		
		// 检查状态码
		assert.Equal(t, http.StatusBadRequest, rr.Code)
		
		// 解析响应
		var response rest.ErrorResponse
		err := json.Unmarshal(rr.Body.Bytes(), &response)
		assert.NoError(t, err)
		
		// 验证错误消息
		assert.Contains(t, response.Error, "标题、内容、作者ID和分类ID为必填项")
	})
	
	t.Run("无效的UUID格式", func(t *testing.T) {
		// 创建模拟服务
		mockService := new(MockDocumentService)
		
		// 创建处理器
		handler := rest.NewDocumentHandler(mockService)
		
		// 创建请求体 - 无效的UUID
		reqBody := rest.CreateDocumentRequest{
			Title:       "测试文档",
			Content:     "这是一个测试文档的内容",
			AuthorID:    "invalid-uuid", // 无效的UUID
			CategoryID:  uuid.New().String(),
			ContentType: "text",
		}
		
		// 转换为JSON
		jsonBody, _ := json.Marshal(reqBody)
		
		// 创建请求
		req, _ := http.NewRequest("POST", "/documents", bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
		
		// 创建响应记录器
		rr := httptest.NewRecorder()
		
		// 调用处理器
		handler.CreateDocument(rr, req)
		
		// 检查状态码
		assert.Equal(t, http.StatusBadRequest, rr.Code)
		
		// 解析响应
		var response rest.ErrorResponse
		err := json.Unmarshal(rr.Body.Bytes(), &response)
		assert.NoError(t, err)
		
		// 验证错误消息
		assert.Contains(t, response.Error, "无效的作者ID格式")
	})
	
	t.Run("服务错误", func(t *testing.T) {
		// 创建模拟服务
		mockService := new(MockDocumentService)
		
		// 准备测试数据
		authorID := uuid.New()
		categoryID := uuid.New()
		
		// 创建请求体
		reqBody := rest.CreateDocumentRequest{
			Title:       "测试文档",
			Description: "测试文档的描述",
			Content:     "这是一个测试文档的内容",
			ContentType: "markdown",
			AuthorID:    authorID.String(),
			CategoryID:  categoryID.String(),
			Tags:        []string{"测试", "文档"},
		}
		
		// 转换为JSON
		jsonBody, _ := json.Marshal(reqBody)
		
		// 设置模拟行为 - 服务返回错误
		mockService.On("CreateDocument", mock.Anything, mock.Anything).Return(nil, fmt.Errorf("创建文档错误"))
		
		// 创建处理器
		handler := rest.NewDocumentHandler(mockService)
		
		// 创建请求
		req, _ := http.NewRequest("POST", "/documents", bytes.NewBuffer(jsonBody))
		req.Header.Set("Content-Type", "application/json")
		
		// 创建响应记录器
		rr := httptest.NewRecorder()
		
		// 调用处理器
		handler.CreateDocument(rr, req)
		
		// 检查状态码
		assert.Equal(t, http.StatusInternalServerError, rr.Code)
		
		// 解析响应
		var response rest.ErrorResponse
		err := json.Unmarshal(rr.Body.Bytes(), &response)
		assert.NoError(t, err)
		
		// 验证错误消息
		assert.Contains(t, response.Error, "创建文档失败")
		assert.Contains(t, response.Error, "创建文档错误")
		
		// 验证模拟行为
		mockService.AssertExpectations(t)
	})
}

func TestDocumentHandler_PublishDocument(t *testing.T) {
	// 创建一个测试用的文档ID
	docID := uuid.New()
	
	t.Run("发布文档成功", func(t *testing.T) {
		// 创建模拟服务
		mockService := new(MockDocumentService)
		
		// 创建一个测试文档
		testDoc := &entity.Document{
			ID:          docID,
			Title:       "测试文档",
			Content:     "这是一个测试文档的内容",
			Status:      entity.StatusPublished, // 已发布状态
			AuthorID:    uuid.New(),
			CategoryID:  uuid.New(),
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}
		
		// 设置模拟行为
		mockService.On("PublishDocument", mock.Anything, docID).Return(nil)
		mockService.On("GetDocumentByID", mock.Anything, docID).Return(testDoc, nil)
		
		// 创建处理器
		handler := rest.NewDocumentHandler(mockService)
		
		// 创建请求
		req, _ := http.NewRequest("POST", "/documents/"+docID.String()+"/publish", nil)
		
		// 设置Chi路由上下文
		rctx := chi.NewRouteContext()
		rctx.URLParams.Add("id", docID.String())
		req = req.WithContext(context.WithValue(req.Context(), chi.RouteCtxKey, rctx))
		
		// 创建响应记录器
		rr := httptest.NewRecorder()
		
		// 调用处理器
		handler.PublishDocument(rr, req)
		
		// 检查状态码
		assert.Equal(t, http.StatusOK, rr.Code)
		
		// 解析响应
		var response rest.DocumentResponse
		err := json.Unmarshal(rr.Body.Bytes(), &response)
		assert.NoError(t, err)
		
		// 验证响应内容
		assert.Equal(t, docID.String(), response.ID)
		assert.Equal(t, "published", response.Status)
		
		// 验证模拟行为
		mockService.AssertExpectations(t)
	})
	
	t.Run("无效的ID格式", func(t *testing.T) {
		// 创建模拟服务
		mockService := new(MockDocumentService)
		
		// 创建处理器
		handler := rest.NewDocumentHandler(mockService)
		
		// 创建请求 - 使用无效的ID
		req, _ := http.NewRequest("POST", "/documents/invalid-id/publish", nil)
		
		// 设置Chi路由上下文
		rctx := chi.NewRouteContext()
		rctx.URLParams.Add("id", "invalid-id")
		req = req.WithContext(context.WithValue(req.Context(), chi.RouteCtxKey, rctx))
		
		// 创建响应记录器
		rr := httptest.NewRecorder()
		
		// 调用处理器
		handler.PublishDocument(rr, req)
		
		// 检查状态码
		assert.Equal(t, http.StatusBadRequest, rr.Code)
		
		// 解析响应
		var response rest.ErrorResponse
		err := json.Unmarshal(rr.Body.Bytes(), &response)
		assert.NoError(t, err)
		
		// 验证错误消息
		assert.Contains(t, response.Error, "无效的文档ID格式")
	})
	
	t.Run("发布文档失败", func(t *testing.T) {
		// 创建模拟服务
		mockService := new(MockDocumentService)
		
		// 设置模拟行为 - 发布失败
		mockService.On("PublishDocument", mock.Anything, docID).Return(fmt.Errorf("发布错误"))
		
		// 创建处理器
		handler := rest.NewDocumentHandler(mockService)
		
		// 创建请求
		req, _ := http.NewRequest("POST", "/documents/"+docID.String()+"/publish", nil)
		
		// 设置Chi路由上下文
		rctx := chi.NewRouteContext()
		rctx.URLParams.Add("id", docID.String())
		req = req.WithContext(context.WithValue(req.Context(), chi.RouteCtxKey, rctx))
		
		// 创建响应记录器
		rr := httptest.NewRecorder()
		
		// 调用处理器
		handler.PublishDocument(rr, req)
		
		// 检查状态码
		assert.Equal(t, http.StatusInternalServerError, rr.Code)
		
		// 解析响应
		var response rest.ErrorResponse
		err := json.Unmarshal(rr.Body.Bytes(), &response)
		assert.NoError(t, err)
		
		// 验证错误消息
		assert.Contains(t, response.Error, "发布文档失败")
		assert.Contains(t, response.Error, "发布错误")
		
		// 验证模拟行为
		mockService.AssertExpectations(t)
	})
} 