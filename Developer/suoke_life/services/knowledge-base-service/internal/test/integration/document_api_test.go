package integration

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/interfaces/rest"
	"knowledge-base-service/internal/test/mocks"
)

func setupTestRouter() (chi.Router, *mocks.MockDocumentService) {
	r := chi.NewRouter()
	mockService := new(mocks.MockDocumentService)
	handler := rest.NewDocumentHandler(mockService)

	handler.RegisterRoutes(r)
	return r, mockService
}

func TestCreateDocument(t *testing.T) {
	// 仅在集成测试环境运行
	if testing.Short() {
		t.Skip("跳过集成测试")
	}

	// 设置路由和模拟服务
	r, mockService := setupTestRouter()

	// 创建测试请求体
	requestBody := map[string]interface{}{
		"title":        "测试文档",
		"content":      "测试内容",
		"content_type": "markdown",
		"author_id":    "00000000-0000-0000-0000-000000000001",
		"category_id":  "00000000-0000-0000-0000-000000000002",
		"tags":         []string{"测试", "示例"},
	}

	// 将请求体转换为JSON
	jsonBody, err := json.Marshal(requestBody)
	assert.NoError(t, err)

	// 创建HTTP请求
	req, err := http.NewRequest("POST", "/documents", bytes.NewBuffer(jsonBody))
	assert.NoError(t, err)
	req.Header.Set("Content-Type", "application/json")

	// 设置模拟响应
	mockDocument := &entity.Document{
		ID:          uuid.MustParse("00000000-0000-0000-0000-000000000003"),
		Title:       "测试文档",
		Content:     "测试内容",
		ContentType: entity.ContentTypeMarkdown,
		Status:      entity.StatusDraft,
		AuthorID:    uuid.MustParse("00000000-0000-0000-0000-000000000001"),
		CategoryID:  uuid.MustParse("00000000-0000-0000-0000-000000000002"),
		Tags:        []string{"测试", "示例"},
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	mockService.On("CreateDocument", mock.Anything, mock.Anything).Return(mockDocument, nil)

	// 执行请求
	rr := httptest.NewRecorder()
	r.ServeHTTP(rr, req)

	// 断言响应
	assert.Equal(t, http.StatusCreated, rr.Code)

	// 解析响应体
	var responseBody map[string]interface{}
	err = json.Unmarshal(rr.Body.Bytes(), &responseBody)
	assert.NoError(t, err)

	// 验证响应内容
	assert.Equal(t, "测试文档", responseBody["title"])
	assert.Equal(t, "00000000-0000-0000-0000-000000000003", responseBody["id"])

	// 验证模拟服务的调用
	mockService.AssertExpectations(t)
}

func TestGetDocument(t *testing.T) {
	// 仅在集成测试环境运行
	if testing.Short() {
		t.Skip("跳过集成测试")
	}

	// 设置路由和模拟服务
	r, mockService := setupTestRouter()

	// 创建测试文档
	mockDocument := &entity.Document{
		ID:          uuid.MustParse("00000000-0000-0000-0000-000000000001"),
		Title:       "测试文档",
		Content:     "测试内容",
		ContentType: entity.ContentTypeText,
		Status:      entity.StatusPublished,
		AuthorID:    uuid.MustParse("00000000-0000-0000-0000-000000000002"),
		CategoryID:  uuid.MustParse("00000000-0000-0000-0000-000000000003"),
		Tags:        []string{"测试"},
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	// 设置模拟服务行为
	mockService.On("GetDocumentByID", mock.Anything, uuid.MustParse("00000000-0000-0000-0000-000000000001")).Return(mockDocument, nil)

	// 创建HTTP请求
	req, err := http.NewRequest("GET", "/documents/00000000-0000-0000-0000-000000000001", nil)
	assert.NoError(t, err)

	// 执行请求
	rr := httptest.NewRecorder()
	r.ServeHTTP(rr, req)

	// 断言响应
	assert.Equal(t, http.StatusOK, rr.Code)

	// 解析响应体
	var responseBody map[string]interface{}
	err = json.Unmarshal(rr.Body.Bytes(), &responseBody)
	assert.NoError(t, err)

	// 验证响应内容
	assert.Equal(t, "测试文档", responseBody["title"])
	assert.Equal(t, "00000000-0000-0000-0000-000000000001", responseBody["id"])
	assert.Equal(t, "published", responseBody["status"])

	// 验证模拟服务的调用
	mockService.AssertExpectations(t)
}

func TestSemanticSearch(t *testing.T) {
	// 仅在集成测试环境运行
	if testing.Short() {
		t.Skip("跳过集成测试")
	}

	// 设置路由和模拟服务
	r, mockService := setupTestRouter()

	// 创建测试文档
	mockDocuments := []*entity.Document{
		{
			ID:          uuid.MustParse("00000000-0000-0000-0000-000000000001"),
			Title:       "测试文档1",
			Content:     "测试内容1",
			ContentType: entity.ContentTypeText,
			Status:      entity.StatusPublished,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		},
		{
			ID:          uuid.MustParse("00000000-0000-0000-0000-000000000002"),
			Title:       "测试文档2",
			Content:     "测试内容2",
			ContentType: entity.ContentTypeText,
			Status:      entity.StatusPublished,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		},
	}

	// 设置模拟服务行为
	mockService.On("SemanticSearch", mock.Anything, "健康生活", 10).Return(mockDocuments, nil)

	// 创建HTTP请求
	req, err := http.NewRequest("GET", "/documents/semantic-search?q=健康生活&limit=10", nil)
	assert.NoError(t, err)

	// 执行请求
	rr := httptest.NewRecorder()
	r.ServeHTTP(rr, req)

	// 断言响应
	assert.Equal(t, http.StatusOK, rr.Code)

	// 解析响应体
	var responseBody []interface{}
	err = json.Unmarshal(rr.Body.Bytes(), &responseBody)
	assert.NoError(t, err)

	// 验证响应内容
	assert.Equal(t, 2, len(responseBody))

	// 验证模拟服务的调用
	mockService.AssertExpectations(t)
}
