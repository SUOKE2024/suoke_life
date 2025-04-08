package e2e

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"knowledge-base-service/config"
	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/domain/service"
	"knowledge-base-service/internal/infrastructure/database"
	"knowledge-base-service/internal/infrastructure/nlp"
	"knowledge-base-service/internal/infrastructure/repository"
	"knowledge-base-service/internal/infrastructure/vectorstore"
	"knowledge-base-service/internal/interfaces/rest"
	"knowledge-base-service/internal/test"
	"knowledge-base-service/pkg/logger"
)

var (
	testDB          *database.PostgresDB
	testVectorStore *vectorstore.MilvusClient
	testRouter      *chi.Mux
	testService     *service.DocumentService
)

// TestMain 设置和清理测试环境
func TestMain(m *testing.M) {
	// 检查是否处于端到端测试模式
	if os.Getenv("TEST_MODE") != "e2e" {
		fmt.Println("跳过端到端测试，设置TEST_MODE=e2e以运行")
		os.Exit(0)
	}

	// 设置测试环境
	if err := setupTestEnvironment(); err != nil {
		fmt.Printf("设置测试环境失败: %v\n", err)
		os.Exit(1)
	}

	// 运行测试
	exitCode := m.Run()

	// 清理测试环境
	if err := cleanupTestEnvironment(); err != nil {
		fmt.Printf("清理测试环境失败: %v\n", err)
	}

	os.Exit(exitCode)
}

// 设置测试环境
func setupTestEnvironment() error {
	var err error

	// 初始化日志
	log := logger.NewStructuredLogger()

	// 加载测试配置
	cfg := &config.Config{
		Database: config.DatabaseConfig{
			ConnString: os.Getenv("DB_CONNECTION_STRING"),
		},
		VectorStore: config.VectorStoreConfig{
			Host:       os.Getenv("VECTOR_STORE_HOST"),
			Port:       19530, // 默认端口
			Collection: os.Getenv("VECTOR_STORE_COLLECTION"),
		},
		Embedding: config.EmbeddingConfig{
			ModelURL:    os.Getenv("EMBEDDING_MODEL_URL"),
			Dimensions:  1536,
			BatchSize:   10,
			ContextSize: 4096,
		},
		TextSplitter: config.TextSplitterConfig{
			ChunkSize:    512,
			ChunkOverlap: 128,
		},
	}

	// 如果环境变量未设置，使用测试默认值
	if cfg.Database.ConnString == "" {
		cfg.Database.ConnString = "postgres://test:test@localhost:5433/test_kb?sslmode=disable"
	}
	if cfg.VectorStore.Host == "" {
		cfg.VectorStore.Host = "localhost"
	}
	if cfg.VectorStore.Collection == "" {
		cfg.VectorStore.Collection = "test_documents"
	}
	if cfg.Embedding.ModelURL == "" {
		cfg.Embedding.ModelURL = "http://localhost:8001/embed"
	}

	// 连接数据库
	testDB, err = database.NewPostgresDB(cfg.Database.ConnString)
	if err != nil {
		return fmt.Errorf("连接测试数据库失败: %w", err)
	}

	// 初始化数据库架构
	if err = testDB.InitSchema(); err != nil {
		return fmt.Errorf("初始化测试数据库架构失败: %w", err)
	}

	// 连接向量存储
	testVectorStore, err = vectorstore.NewMilvusClient(cfg.VectorStore.Host, cfg.VectorStore.Port)
	if err != nil {
		return fmt.Errorf("连接测试向量存储失败: %w", err)
	}

	// 设置集合名称
	testVectorStore.SetCollectionName(cfg.VectorStore.Collection)

	// 创建文本分割器
	textSplitter := nlp.NewChineseTextSplitter(
		cfg.TextSplitter.ChunkSize,
		cfg.TextSplitter.ChunkOverlap,
		true,
	)

	// 创建HTTP客户端
	httpClient := &http.Client{
		Timeout: 30 * time.Second,
	}

	// 创建嵌入服务
	embeddingService := nlp.NewChineseEmbeddingService(
		nlp.EmbeddingOptions{
			ModelURL:    cfg.Embedding.ModelURL,
			APIToken:    cfg.Embedding.APIToken,
			ContextSize: cfg.Embedding.ContextSize,
			Dimension:   cfg.Embedding.Dimensions,
			BatchSize:   cfg.Embedding.BatchSize,
		},
		httpClient,
	)

	// 创建仓库
	documentRepo := repository.NewPostgresDocumentRepository(testDB, testVectorStore, nil)
	categoryRepo := repository.NewPostgresCategoryRepository(testDB)

	// 创建文档服务
	testService = service.NewDocumentService(
		documentRepo,
		categoryRepo,
		textSplitter,
		embeddingService,
	)

	// 创建处理器
	documentHandler := rest.NewDocumentHandler(testService)

	// 设置路由
	testRouter = chi.NewRouter()

	// 注册路由
	documentHandler.RegisterRoutes(testRouter)

	log.Info("测试环境设置完成")

	return nil
}

// 清理测试环境
func cleanupTestEnvironment() error {
	// 关闭连接
	if testVectorStore != nil {
		testVectorStore.Close()
	}

	if testDB != nil {
		testDB.Close()
	}

	return nil
}

// TestDocumentLifecycle 测试文档完整生命周期
func TestDocumentLifecycle(t *testing.T) {
	// 跳过测试如果不在端到端测试模式
	if os.Getenv("TEST_MODE") != "e2e" {
		t.Skip("跳过端到端测试，设置TEST_MODE=e2e以运行")
	}

	// 1. 创建文档
	docID := createTestDocument(t)

	// 2. 获取文档
	doc := getTestDocument(t, docID)
	assert.Equal(t, "端到端测试文档", doc.Title)

	// 3. 更新文档
	updateTestDocument(t, docID)

	// 4. 再次获取文档并验证更新
	updatedDoc := getTestDocument(t, docID)
	assert.Equal(t, "更新后的测试文档", updatedDoc.Title)

	// 5. 发布文档
	publishTestDocument(t, docID)

	// 6. 验证文档已发布
	publishedDoc := getTestDocument(t, docID)
	assert.Equal(t, "published", publishedDoc.Status)

	// 7. 语义搜索
	searchResults := semanticSearchDocuments(t, "测试文档")
	assert.True(t, len(searchResults) > 0, "语义搜索应返回结果")

	foundDoc := false
	for _, result := range searchResults {
		if result.ID == docID.String() {
			foundDoc = true
			break
		}
	}
	assert.True(t, foundDoc, "语义搜索应返回创建的文档")

	// 8. 归档文档
	archiveTestDocument(t, docID)

	// 9. 验证文档已归档
	archivedDoc := getTestDocument(t, docID)
	assert.Equal(t, "archived", archivedDoc.Status)

	// 10. 删除文档
	deleteTestDocument(t, docID)

	// 11. 验证文档已删除
	resp := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", fmt.Sprintf("/documents/%s", docID), nil)
	testRouter.ServeHTTP(resp, req)
	assert.Equal(t, http.StatusNotFound, resp.Code)
}

// 创建测试文档
func createTestDocument(t *testing.T) uuid.UUID {
	// 创建测试请求体
	requestBody := map[string]interface{}{
		"title":        "端到端测试文档",
		"content":      "这是一个用于端到端测试的文档内容。" + test.GenerateLoremIpsum(200),
		"description":  "端到端测试描述",
		"content_type": "markdown",
		"author_id":    uuid.New().String(),
		"tags":         []string{"端到端", "测试", "索克生活"},
	}

	// 将请求体转换为JSON
	jsonBody, err := json.Marshal(requestBody)
	require.NoError(t, err)

	// 创建请求
	req, err := http.NewRequest("POST", "/documents", bytes.NewBuffer(jsonBody))
	require.NoError(t, err)
	req.Header.Set("Content-Type", "application/json")

	// 记录响应
	resp := httptest.NewRecorder()

	// 处理请求
	testRouter.ServeHTTP(resp, req)

	// 验证响应状态码
	require.Equal(t, http.StatusCreated, resp.Code)

	// 解析响应体
	var response map[string]interface{}
	err = json.Unmarshal(resp.Body.Bytes(), &response)
	require.NoError(t, err)

	// 获取文档ID
	docIDStr, ok := response["id"].(string)
	require.True(t, ok, "响应应包含文档ID")

	docID, err := uuid.Parse(docIDStr)
	require.NoError(t, err)

	return docID
}

// 获取测试文档
func getTestDocument(t *testing.T, docID uuid.UUID) rest.DocumentResponse {
	// 创建请求
	req, err := http.NewRequest("GET", fmt.Sprintf("/documents/%s", docID), nil)
	require.NoError(t, err)

	// 记录响应
	resp := httptest.NewRecorder()

	// 处理请求
	testRouter.ServeHTTP(resp, req)

	// 验证响应状态码
	require.Equal(t, http.StatusOK, resp.Code)

	// 解析响应体
	var document rest.DocumentResponse
	err = json.Unmarshal(resp.Body.Bytes(), &document)
	require.NoError(t, err)

	return document
}

// 更新测试文档
func updateTestDocument(t *testing.T, docID uuid.UUID) {
	// 创建测试请求体
	requestBody := map[string]interface{}{
		"title":        "更新后的测试文档",
		"content":      "这是更新后的文档内容。" + test.GenerateLoremIpsum(200),
		"description":  "更新后的描述",
		"content_type": "markdown",
		"tags":         []string{"端到端", "测试", "更新", "索克生活"},
	}

	// 将请求体转换为JSON
	jsonBody, err := json.Marshal(requestBody)
	require.NoError(t, err)

	// 创建请求
	req, err := http.NewRequest("PUT", fmt.Sprintf("/documents/%s", docID), bytes.NewBuffer(jsonBody))
	require.NoError(t, err)
	req.Header.Set("Content-Type", "application/json")

	// 记录响应
	resp := httptest.NewRecorder()

	// 处理请求
	testRouter.ServeHTTP(resp, req)

	// 验证响应状态码
	require.Equal(t, http.StatusOK, resp.Code)
}

// 发布测试文档
func publishTestDocument(t *testing.T, docID uuid.UUID) {
	// 创建请求
	req, err := http.NewRequest("PUT", fmt.Sprintf("/documents/%s/publish", docID), nil)
	require.NoError(t, err)

	// 记录响应
	resp := httptest.NewRecorder()

	// 处理请求
	testRouter.ServeHTTP(resp, req)

	// 验证响应状态码
	require.Equal(t, http.StatusOK, resp.Code)
}

// 归档测试文档
func archiveTestDocument(t *testing.T, docID uuid.UUID) {
	// 创建请求
	req, err := http.NewRequest("PUT", fmt.Sprintf("/documents/%s/archive", docID), nil)
	require.NoError(t, err)

	// 记录响应
	resp := httptest.NewRecorder()

	// 处理请求
	testRouter.ServeHTTP(resp, req)

	// 验证响应状态码
	require.Equal(t, http.StatusOK, resp.Code)
}

// 删除测试文档
func deleteTestDocument(t *testing.T, docID uuid.UUID) {
	// 创建请求
	req, err := http.NewRequest("DELETE", fmt.Sprintf("/documents/%s", docID), nil)
	require.NoError(t, err)

	// 记录响应
	resp := httptest.NewRecorder()

	// 处理请求
	testRouter.ServeHTTP(resp, req)

	// 验证响应状态码
	require.Equal(t, http.StatusOK, resp.Code)
}

// 语义搜索文档
func semanticSearchDocuments(t *testing.T, query string) []rest.DocumentResponse {
	// 创建请求
	req, err := http.NewRequest("GET", fmt.Sprintf("/documents/semantic-search?q=%s", query), nil)
	require.NoError(t, err)

	// 记录响应
	resp := httptest.NewRecorder()

	// 处理请求
	testRouter.ServeHTTP(resp, req)

	// 验证响应状态码
	require.Equal(t, http.StatusOK, resp.Code)

	// 解析响应体
	var documents []rest.DocumentResponse
	err = json.Unmarshal(resp.Body.Bytes(), &documents)
	require.NoError(t, err)

	return documents
}

// TestDatabaseOperations 测试数据库操作
func TestDatabaseOperations(t *testing.T) {
	// 跳过测试如果不在端到端测试模式
	if os.Getenv("TEST_MODE") != "e2e" {
		t.Skip("跳过端到端测试，设置TEST_MODE=e2e以运行")
	}

	// 创建上下文
	ctx := context.Background()

	// 测试事务操作
	err := testDB.BeginTransaction(ctx, func(tx interface{}) error {
		// 在事务中创建文档
		doc := &entity.Document{
			ID:          uuid.New(),
			Title:       "事务测试文档",
			Content:     "这是一个事务测试文档",
			Description: "事务测试",
			ContentType: entity.ContentTypeText,
			Status:      entity.StatusDraft,
			AuthorID:    uuid.New(),
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}

		// 使用原始SQL执行插入
		_, err := tx.(*database.Transaction).Exec(
			"INSERT INTO documents (id, title, content, description, content_type, status, author_id, created_at, updated_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
			doc.ID, doc.Title, doc.Content, doc.Description, doc.ContentType, doc.Status, doc.AuthorID, doc.CreatedAt, doc.UpdatedAt,
		)
		if err != nil {
			return err
		}

		return nil
	})

	require.NoError(t, err)
}

// TestConcurrentOperations 测试并发操作
func TestConcurrentOperations(t *testing.T) {
	// 跳过测试如果不在端到端测试模式
	if os.Getenv("TEST_MODE") != "e2e" {
		t.Skip("跳过端到端测试，设置TEST_MODE=e2e以运行")
	}

	// 并发数量
	const concurrency = 5

	// 并发创建文档
	var docIDs []uuid.UUID
	errCh := make(chan error, concurrency)
	idCh := make(chan uuid.UUID, concurrency)

	for i := 0; i < concurrency; i++ {
		go func(index int) {
			// 创建测试请求体
			requestBody := map[string]interface{}{
				"title":        fmt.Sprintf("并发测试文档 %d", index),
				"content":      fmt.Sprintf("这是并发测试文档 %d 的内容。%s", index, test.GenerateLoremIpsum(100)),
				"description":  fmt.Sprintf("并发测试描述 %d", index),
				"content_type": "markdown",
				"author_id":    uuid.New().String(),
				"tags":         []string{"并发", "测试", fmt.Sprintf("索引-%d", index)},
			}

			// 将请求体转换为JSON
			jsonBody, err := json.Marshal(requestBody)
			if err != nil {
				errCh <- err
				idCh <- uuid.Nil
				return
			}

			// 创建请求
			req, err := http.NewRequest("POST", "/documents", bytes.NewBuffer(jsonBody))
			if err != nil {
				errCh <- err
				idCh <- uuid.Nil
				return
			}
			req.Header.Set("Content-Type", "application/json")

			// 记录响应
			resp := httptest.NewRecorder()

			// 处理请求
			testRouter.ServeHTTP(resp, req)

			// 验证响应状态码
			if resp.Code != http.StatusCreated {
				errCh <- fmt.Errorf("创建文档失败，状态码: %d", resp.Code)
				idCh <- uuid.Nil
				return
			}

			// 解析响应体
			var response map[string]interface{}
			if err := json.Unmarshal(resp.Body.Bytes(), &response); err != nil {
				errCh <- err
				idCh <- uuid.Nil
				return
			}

			// 获取文档ID
			docIDStr, ok := response["id"].(string)
			if !ok {
				errCh <- fmt.Errorf("响应中无法获取文档ID")
				idCh <- uuid.Nil
				return
			}

			docID, err := uuid.Parse(docIDStr)
			if err != nil {
				errCh <- err
				idCh <- uuid.Nil
				return
			}

			errCh <- nil
			idCh <- docID
		}(i)
	}

	// 收集结果
	for i := 0; i < concurrency; i++ {
		err := <-errCh
		id := <-idCh

		if err != nil {
			t.Errorf("并发创建文档错误: %v", err)
		} else if id == uuid.Nil {
			t.Error("并发创建文档返回了无效ID")
		} else {
			docIDs = append(docIDs, id)
		}
	}

	// 验证所有文档都创建成功
	assert.Equal(t, concurrency, len(docIDs), "应该成功创建所有文档")

	// 清理测试数据
	for _, id := range docIDs {
		deleteTestDocument(t, id)
	}
}
