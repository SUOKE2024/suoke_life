package real

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/google/uuid"

	"knowledge-base-service/internal/domain/entity"
	domainrepo "knowledge-base-service/internal/domain/repository"
	"knowledge-base-service/internal/domain/service"
	"knowledge-base-service/internal/infrastructure/database"
	"knowledge-base-service/internal/infrastructure/repository"
	"knowledge-base-service/internal/infrastructure/vectorstore"
	"knowledge-base-service/internal/interfaces/ai"
	"testing"
)

// 设置实际的数据库连接
func SetupRealDatabase(ctx context.Context) (database.DBManager, func(), error) {
	// 从环境变量或配置文件中获取连接字符串
	connStr := os.Getenv("TEST_DB_CONNECTION_STRING")
	if connStr == "" {
		// 尝试使用testuser账户
		connStr = "host=localhost port=5432 user=testuser password=testpassword dbname=knowledge_base_test sslmode=disable"
		log.Printf("警告: 未设置TEST_DB_CONNECTION_STRING环境变量，尝试使用testuser账户: %s", connStr)
	} else {
		log.Printf("使用环境变量中的连接字符串: %s", connStr)
	}

	// 连接数据库
	log.Printf("尝试连接数据库...")
	db, err := database.NewPostgresDB(connStr)
	if err != nil {
		// 如果使用testuser失败，尝试使用postgres账户作为备选
		if connStr != "host=localhost port=5432 user=postgres password=postgres dbname=knowledge_base_test sslmode=disable" {
			log.Printf("使用testuser连接失败，尝试使用postgres账户...")
			connStr = "host=localhost port=5432 user=postgres password=postgres dbname=knowledge_base_test sslmode=disable"
			db, err = database.NewPostgresDB(connStr)
		}

		if err != nil {
			return nil, nil, fmt.Errorf("连接数据库失败: %w", err)
		}
	}
	log.Printf("数据库连接成功")

	// 初始化 schema
	// 注意: 对于测试，我们可能希望每次都重置数据库
	if err := initTestSchema(ctx, db); err != nil {
		db.Close()
		return nil, nil, fmt.Errorf("初始化测试数据库失败: %w", err)
	}

	cleanup := func() {
		// 测试完成后断开连接
		if err := db.Close(); err != nil {
			log.Printf("警告: 关闭数据库连接时出错: %v", err)
		}
	}

	return db, cleanup, nil
}

// 设置实际的向量存储
func SetupRealVectorStore(ctx context.Context) (vectorstore.VectorStore, *vectorstore.MilvusClient, func(), error) {
	// 检查是否使用模拟向量存储
	useMock := os.Getenv("VECTOR_STORE_USE_MOCK")
	if useMock == "true" || testing.Short() {
		log.Printf("使用模拟向量存储进行测试")
		mockStore := NewMockVectorStore()
		return mockStore, nil, func() {}, nil
	}

	// 从环境变量或配置文件中获取Milvus连接信息
	host := os.Getenv("VECTOR_STORE_HOST")
	if host == "" {
		host = "localhost"
	}

	port := 19530 // 使用默认端口，因为实际容器未映射到19531

	// 连接向量存储
	log.Printf("尝试连接Milvus向量存储: %s:%d", host, port)
	milvusClient, err := vectorstore.NewMilvusClient(host, port)
	if err != nil {
		log.Printf("警告: 连接Milvus失败: %v，将尝试使用模拟向量存储", err)
		mockStore := NewMockVectorStore()
		return mockStore, nil, func() {}, nil
	}

	// 设置集合名称
	collectionName := os.Getenv("VECTOR_STORE_COLLECTION")
	if collectionName == "" {
		collectionName = "test_documents"
	}
	milvusClient.SetCollectionName(collectionName)

	cleanup := func() {
		// 测试完成后断开连接
		if err := milvusClient.Close(); err != nil {
			log.Printf("警告: 关闭向量存储连接时出错: %v", err)
		}
	}

	return milvusClient, milvusClient, cleanup, nil
}

// 设置嵌入服务
func SetupEmbeddingService(ctx context.Context) (ai.EmbeddingService, func(), error) {
	// 从环境变量或配置文件中获取嵌入模型URL
	modelURL := os.Getenv("EMBEDDING_MODEL_URL")
	if modelURL == "" {
		modelURL = "http://localhost:8000/embed" // 使用映射到8000端口的嵌入服务
	}

	// 创建嵌入服务实例
	embeddingService := &ai.HTTPEmbeddingService{
		URL: modelURL,
	}

	// 这个服务不需要清理
	cleanup := func() {}

	return embeddingService, cleanup, nil
}

// 设置文档存储库
func SetupRealDocumentRepository(ctx context.Context, db database.DBManager, vectorStore vectorstore.VectorStore) (domainrepo.DocumentRepository, error) {
	// 判断向量存储类型并适当转换
	var milvusClient *vectorstore.MilvusClient

	// 尝试类型断言
	if client, ok := vectorStore.(*vectorstore.MilvusClient); ok {
		milvusClient = client
	} else {
		// 如果不是MilvusClient类型，则使用nil
		log.Printf("警告: 向量存储不是MilvusClient类型，文档存储库将使用nil作为向量存储")
	}

	// 创建文档存储库实例
	docRepo := repository.NewPostgresDocumentRepository(db, milvusClient, nil)

	return docRepo, nil
}

// 设置分类存储库
func SetupRealCategoryRepository(ctx context.Context, db database.DBManager) (domainrepo.CategoryRepository, error) {
	// 创建分类存储库实例
	catRepo := repository.NewCategoryRepository(db)

	// 初始化一些测试分类
	if err := initTestCategories(ctx, catRepo); err != nil {
		return nil, fmt.Errorf("初始化测试分类失败: %w", err)
	}

	return catRepo, nil
}

// 设置文本分割器
func SetupTextSplitter() ai.TextSplitter {
	return &ai.ChineseTextSplitter{
		ChunkSize:    500,
		ChunkOverlap: 50,
	}
}

// 设置完整的文档服务
func SetupRealDocumentService(ctx context.Context) (*service.DocumentService, func(), error) {
	// 设置数据库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		return nil, nil, err
	}

	// 设置向量存储
	vectorStore, _, vectorStoreCleanup, err := SetupRealVectorStore(ctx)
	if err != nil {
		dbCleanup()
		return nil, nil, err
	}

	// 设置嵌入服务
	embeddingService, embeddingCleanup, err := SetupEmbeddingService(ctx)
	if err != nil {
		vectorStoreCleanup()
		dbCleanup()
		return nil, nil, err
	}

	// 设置文档存储库
	docRepo, err := SetupRealDocumentRepository(ctx, db, vectorStore)
	if err != nil {
		embeddingCleanup()
		vectorStoreCleanup()
		dbCleanup()
		return nil, nil, err
	}

	// 设置分类存储库
	catRepo, err := SetupRealCategoryRepository(ctx, db)
	if err != nil {
		embeddingCleanup()
		vectorStoreCleanup()
		dbCleanup()
		return nil, nil, err
	}

	// 设置文本分割器
	textSplitter := SetupTextSplitter()

	// 创建文档服务
	docService := service.NewDocumentService(docRepo, catRepo, textSplitter, embeddingService)

	// 合并清理函数
	cleanup := func() {
		embeddingCleanup()
		vectorStoreCleanup()
		dbCleanup()
	}

	return docService, cleanup, nil
}

// 初始化测试数据库架构
func initTestSchema(ctx context.Context, db database.DBManager) error {
	// 在测试开始前清理现有表
	dropSchema := `
	DROP TABLE IF EXISTS document_chunks;
	DROP TABLE IF EXISTS documents;
	DROP TABLE IF EXISTS categories;
	`
	_, err := db.Exec(ctx, dropSchema)
	if err != nil {
		return fmt.Errorf("删除现有表失败: %w", err)
	}

	// 创建分类表
	createCategoryTable := `
	CREATE TABLE IF NOT EXISTS categories (
		id UUID PRIMARY KEY,
		name TEXT NOT NULL,
		path TEXT NOT NULL UNIQUE,
		description TEXT,
		parent_id UUID,
		created_at TIMESTAMP NOT NULL DEFAULT NOW(),
		updated_at TIMESTAMP NOT NULL DEFAULT NOW()
	);
	
	CREATE INDEX IF NOT EXISTS idx_categories_path ON categories(path);
	CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);
	`
	_, err = db.Exec(ctx, createCategoryTable)
	if err != nil {
		return fmt.Errorf("创建分类表失败: %w", err)
	}

	// 创建文档表
	createDocumentTable := `
	CREATE TABLE IF NOT EXISTS documents (
		id UUID PRIMARY KEY,
		title TEXT NOT NULL,
		description TEXT,
		content TEXT NOT NULL,
		content_type TEXT NOT NULL,
		status TEXT NOT NULL,
		author_id UUID NOT NULL,
		category_id UUID NOT NULL,
		tags TEXT[] DEFAULT '{}',
		tx_hash TEXT,
		metadata JSONB DEFAULT '{}',
		created_at TIMESTAMP NOT NULL DEFAULT NOW(),
		updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
		CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES categories(id)
	);
	
	CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category_id);
	CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
	CREATE INDEX IF NOT EXISTS idx_documents_author ON documents(author_id);
	CREATE INDEX IF NOT EXISTS idx_documents_content ON documents USING GIN(to_tsvector('chinese', content));
	CREATE INDEX IF NOT EXISTS idx_documents_tags ON documents USING GIN(tags);
	`
	_, err = db.Exec(ctx, createDocumentTable)
	if err != nil {
		return fmt.Errorf("创建文档表失败: %w", err)
	}

	// 创建文档块表
	createChunkTable := `
	CREATE TABLE IF NOT EXISTS document_chunks (
		id UUID PRIMARY KEY,
		document_id UUID NOT NULL,
		content TEXT NOT NULL,
		token_count INT NOT NULL,
		vector_id TEXT,
		offset INT NOT NULL,
		length INT NOT NULL,
		metadata JSONB DEFAULT '{}',
		created_at TIMESTAMP NOT NULL DEFAULT NOW(),
		CONSTRAINT fk_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
	);
	
	CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id);
	`
	_, err = db.Exec(ctx, createChunkTable)
	if err != nil {
		return fmt.Errorf("创建文档块表失败: %w", err)
	}

	return nil
}

// 初始化测试分类
func initTestCategories(ctx context.Context, catRepo domainrepo.CategoryRepository) error {
	// 创建根分类
	rootCategory := &entity.Category{
		ID:          uuid.New(),
		Name:        "测试知识库",
		Path:        "/测试知识库",
		Description: "用于基准测试的知识库",
		ParentID:    nil,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	if err := catRepo.Save(ctx, rootCategory); err != nil {
		return fmt.Errorf("创建根分类失败: %w", err)
	}

	// 创建子分类
	subCategories := []*entity.Category{
		{
			ID:          uuid.New(),
			Name:        "中医理论",
			Path:        "/测试知识库/中医理论",
			Description: "中医基础理论知识",
			ParentID:    &rootCategory.ID,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		},
		{
			ID:          uuid.New(),
			Name:        "针灸技术",
			Path:        "/测试知识库/针灸技术",
			Description: "针灸疗法相关知识",
			ParentID:    &rootCategory.ID,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		},
		{
			ID:          uuid.New(),
			Name:        "中药学",
			Path:        "/测试知识库/中药学",
			Description: "中药材与方剂学知识",
			ParentID:    &rootCategory.ID,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		},
	}

	for _, category := range subCategories {
		if err := catRepo.Save(ctx, category); err != nil {
			return fmt.Errorf("创建子分类失败: %w", err)
		}
	}

	return nil
}
