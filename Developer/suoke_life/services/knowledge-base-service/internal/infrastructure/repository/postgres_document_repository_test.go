package repository

import (
	"context"
	"os"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/infrastructure/database"
)

func setupTestDB(t *testing.T) database.DBManager {
	// 从环境变量获取连接字符串
	connStr := os.Getenv("TEST_DB_CONNECTION_STRING")
	if connStr == "" {
		// 使用默认测试连接 - 使用键值对格式，使用testuser账户
		connStr = "host=localhost port=5432 user=testuser password=testpassword dbname=knowledge_base_test sslmode=disable"
		// 如果testuser账户未配置，则尝试使用postgres账户
		t.Logf("未设置TEST_DB_CONNECTION_STRING环境变量，尝试使用testuser账户连接...")
	}

	// 尝试连接数据库
	db, err := database.NewPostgresDB(connStr)
	if err != nil {
		// 如果使用testuser失败，尝试使用postgres账户作为备选
		if connStr != "host=localhost port=5432 user=postgres password=postgres dbname=knowledge_base_test sslmode=disable" {
			t.Logf("使用testuser连接失败，尝试使用postgres账户...")
			connStr = "host=localhost port=5432 user=postgres password=postgres dbname=knowledge_base_test sslmode=disable"
			db, err = database.NewPostgresDB(connStr)
		}

		if err != nil {
			t.Fatalf("连接测试数据库失败: %v", err)
		}
	}

	// 初始化测试表
	_, err = db.Exec(context.Background(), `
		DROP TABLE IF EXISTS document_chunks;
		DROP TABLE IF EXISTS documents;
		DROP TABLE IF EXISTS categories;
		
		CREATE TABLE IF NOT EXISTS categories (
			id UUID PRIMARY KEY,
			name TEXT NOT NULL,
			path TEXT NOT NULL UNIQUE,
			description TEXT,
			parent_id UUID,
			created_at TIMESTAMP NOT NULL DEFAULT NOW(),
			updated_at TIMESTAMP NOT NULL DEFAULT NOW()
		);
		
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
			FOREIGN KEY (category_id) REFERENCES categories(id)
		);
	`)
	if err != nil {
		t.Fatalf("初始化测试表失败: %v", err)
	}

	return db
}

func insertTestCategory(t *testing.T, db database.DBManager) uuid.UUID {
	categoryID := uuid.New()
	_, err := db.Exec(context.Background(), `
		INSERT INTO categories (id, name, path, description, created_at, updated_at)
		VALUES ($1, $2, $3, $4, NOW(), NOW())
	`, categoryID, "测试分类", "/测试分类", "用于测试的分类")

	if err != nil {
		t.Fatalf("插入测试分类失败: %v", err)
	}

	return categoryID
}

func TestPostgresDocumentRepository_SaveAndFind(t *testing.T) {
	// 设置测试数据库
	db := setupTestDB(t)
	defer db.Close()

	// 创建测试分类
	categoryID := insertTestCategory(t, db)

	// 创建文档存储库
	repo := NewPostgresDocumentRepository(db, nil, nil)

	// 创建测试文档
	authorID := uuid.New()
	doc, err := entity.NewDocument(
		"测试文档",
		"这是一个测试文档的内容。",
		entity.ContentTypeText,
		authorID,
		categoryID,
	)
	assert.NoError(t, err)

	// 保存文档
	ctx := context.Background()
	err = repo.Save(ctx, doc)
	assert.NoError(t, err)
	assert.NotEqual(t, uuid.Nil, doc.ID, "文档ID应该不为空")

	// 查找文档
	foundDoc, err := repo.FindByID(ctx, doc.ID)
	assert.NoError(t, err)
	assert.NotNil(t, foundDoc, "应该找到保存的文档")
	assert.Equal(t, doc.ID, foundDoc.ID, "文档ID应该匹配")
	assert.Equal(t, doc.Title, foundDoc.Title, "文档标题应该匹配")
	assert.Equal(t, doc.Content, foundDoc.Content, "文档内容应该匹配")
}
