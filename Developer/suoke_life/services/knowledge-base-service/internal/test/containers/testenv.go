package containers

import (
	"context"
	"fmt"
	"log"
	"os"
	"strconv"
	"sync"

	domainRepo "knowledge-base-service/internal/domain/repository"
	"knowledge-base-service/internal/infrastructure/database"
	infraRepo "knowledge-base-service/internal/infrastructure/repository"
	"knowledge-base-service/internal/infrastructure/vectorstore"
	"knowledge-base-service/internal/test/benchmark/real"
)

var (
	// 单例模式实现
	testEnv     *TestEnvironment
	testEnvOnce sync.Once
)

// TestEnvironment 封装测试环境，管理所有测试容器和资源
type TestEnvironment struct {
	ctx           context.Context
	cancel        context.CancelFunc
	postgres      *PostgresContainer
	milvus        *MilvusContainer
	db            database.DBManager
	vectorStore   vectorstore.VectorStore
	milvusClient  *vectorstore.MilvusClient
	docRepository domainRepo.DocumentRepository
	initialized   bool
	mu            sync.Mutex
}

// GetTestEnvironment 获取测试环境单例
func GetTestEnvironment() *TestEnvironment {
	testEnvOnce.Do(func() {
		ctx, cancel := context.WithCancel(context.Background())
		testEnv = &TestEnvironment{
			ctx:         ctx,
			cancel:      cancel,
			initialized: false,
		}
	})
	return testEnv
}

// Initialize 初始化测试环境
func (te *TestEnvironment) Initialize() error {
	te.mu.Lock()
	defer te.mu.Unlock()

	if te.initialized {
		return nil
	}

	var err error

	// 启动PostgreSQL容器
	te.postgres, err = StartPostgresContainer(te.ctx)
	if err != nil {
		return fmt.Errorf("初始化PostgreSQL容器失败: %w", err)
	}

	// 设置环境变量
	os.Setenv("TEST_DB_CONNECTION_STRING", te.postgres.ConnectionString())

	// 连接数据库
	te.db, err = database.NewPostgresDB(te.postgres.ConnectionString())
	if err != nil {
		return fmt.Errorf("连接测试数据库失败: %w", err)
	}

	// 初始化数据库架构
	if err := te.initTestSchema(); err != nil {
		return fmt.Errorf("初始化测试数据库架构失败: %w", err)
	}

	// 启动Milvus容器
	te.milvus, err = StartMilvusContainer(te.ctx)
	if err != nil {
		log.Printf("警告: 初始化Milvus容器失败: %v，将使用模拟向量存储", err)
		te.vectorStore = real.NewMockVectorStore()
	} else {
		// 连接Milvus
		portNum, _ := strconv.Atoi(te.milvus.Port())
		te.milvusClient, err = vectorstore.NewMilvusClient(te.milvus.Host(), portNum)
		if err != nil {
			log.Printf("警告: 连接Milvus失败: %v，将使用模拟向量存储", err)
			te.vectorStore = real.NewMockVectorStore()
		} else {
			te.milvusClient.SetCollectionName("test_documents")
			te.vectorStore = te.milvusClient
		}
	}

	// 初始化文档存储库
	te.docRepository = infraRepo.NewPostgresDocumentRepository(te.db, te.milvusClient, nil)

	te.initialized = true
	log.Println("测试环境已初始化完成")

	return nil
}

// DB 获取数据库管理器
func (te *TestEnvironment) DB() database.DBManager {
	return te.db
}

// VectorStore 获取向量存储
func (te *TestEnvironment) VectorStore() vectorstore.VectorStore {
	return te.vectorStore
}

// MilvusClient 获取Milvus客户端
func (te *TestEnvironment) MilvusClient() *vectorstore.MilvusClient {
	return te.milvusClient
}

// DocumentRepository 获取文档存储库
func (te *TestEnvironment) DocumentRepository() domainRepo.DocumentRepository {
	return te.docRepository
}

// ConnectionString 获取数据库连接字符串
func (te *TestEnvironment) ConnectionString() string {
	if te.postgres != nil {
		return te.postgres.ConnectionString()
	}
	return ""
}

// Cleanup 清理测试环境
func (te *TestEnvironment) Cleanup() {
	te.mu.Lock()
	defer te.mu.Unlock()

	if !te.initialized {
		return
	}

	// 关闭数据库连接
	if te.db != nil {
		if err := te.db.Close(); err != nil {
			log.Printf("警告: 关闭数据库连接时出错: %v", err)
		}
	}

	// 停止PostgreSQL容器
	if te.postgres != nil {
		if err := te.postgres.Stop(te.ctx); err != nil {
			log.Printf("警告: 停止PostgreSQL容器时出错: %v", err)
		}
	}

	// 停止Milvus容器
	if te.milvus != nil {
		if err := te.milvus.Stop(te.ctx); err != nil {
			log.Printf("警告: 停止Milvus容器时出错: %v", err)
		}
	}

	// 取消上下文
	te.cancel()
	te.initialized = false

	log.Println("测试环境已清理完成")
}

// initTestSchema 初始化测试数据库架构
func (te *TestEnvironment) initTestSchema() error {
	// 创建数据库架构
	schema := `
	-- 删除现有表
	DROP TABLE IF EXISTS document_chunks;
	DROP TABLE IF EXISTS documents;
	DROP TABLE IF EXISTS categories;
	
	-- 创建分类表
	CREATE TABLE IF NOT EXISTS categories (
		id UUID PRIMARY KEY,
		name TEXT NOT NULL,
		path TEXT NOT NULL UNIQUE,
		description TEXT,
		parent_id UUID,
		created_at TIMESTAMP NOT NULL DEFAULT NOW(),
		updated_at TIMESTAMP NOT NULL DEFAULT NOW()
	);
	
	-- 创建文档表
	CREATE TABLE IF NOT EXISTS documents (
		id UUID PRIMARY KEY,
		title TEXT NOT NULL,
		content TEXT,
		description TEXT,
		content_type TEXT DEFAULT 'text/markdown',
		metadata JSONB,
		status TEXT DEFAULT 'draft',
		author_id UUID,
		category_id UUID,
		tags TEXT[],
		vector_ids TEXT[],
		created_at TIMESTAMP NOT NULL DEFAULT NOW(),
		updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
		published_at TIMESTAMP,
		CONSTRAINT fk_category
			FOREIGN KEY(category_id)
			REFERENCES categories(id)
			ON DELETE SET NULL
	);
	
	-- 创建文档块表
	CREATE TABLE IF NOT EXISTS document_chunks (
		id UUID PRIMARY KEY,
		document_id UUID NOT NULL,
		content TEXT NOT NULL,
		metadata JSONB,
		vector_id TEXT,
		chunk_index INTEGER,
		created_at TIMESTAMP NOT NULL DEFAULT NOW(),
		updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
		CONSTRAINT fk_document
			FOREIGN KEY(document_id)
			REFERENCES documents(id)
			ON DELETE CASCADE
	);
	
	-- 创建索引
	CREATE INDEX idx_documents_category_id ON documents(category_id);
	CREATE INDEX idx_documents_status ON documents(status);
	CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
	`

	_, err := te.db.Exec(te.ctx, schema)
	return err
}
