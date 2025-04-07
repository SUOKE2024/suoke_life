package test

import (
	"context"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/google/uuid"

	"knowledge-base-service/internal/domain/entity"
)

func init() {
	// 初始化随机数生成器
	rand.Seed(time.Now().UnixNano())
}

// TestConfig 测试配置
type TestConfig struct {
	DBConnString string
	VectorHost   string
	VectorPort   int
	TestDataDir  string
}

// LoadTestConfig 加载测试配置
func LoadTestConfig() (*TestConfig, error) {
	// 从环境变量或默认值加载测试配置
	dbConnString := os.Getenv("TEST_DB_CONN_STRING")
	if dbConnString == "" {
		dbConnString = "postgres://postgres:postgres@localhost:5432/testdb?sslmode=disable"
	}

	vectorHost := os.Getenv("TEST_VECTOR_HOST")
	if vectorHost == "" {
		vectorHost = "localhost"
	}

	vectorPort := 19530 // Milvus默认端口
	if portStr := os.Getenv("TEST_VECTOR_PORT"); portStr != "" {
		fmt.Sscanf(portStr, "%d", &vectorPort)
	}

	testDataDir := os.Getenv("TEST_DATA_DIR")
	if testDataDir == "" {
		// 使用临时目录
		testDataDir = filepath.Join(os.TempDir(), "knowledge-base-service-test-data")
	}

	// 确保测试数据目录存在
	if err := os.MkdirAll(testDataDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create test data directory: %w", err)
	}

	return &TestConfig{
		DBConnString: dbConnString,
		VectorHost:   vectorHost,
		VectorPort:   vectorPort,
		TestDataDir:  testDataDir,
	}, nil
}

// GenerateTestDocument 生成测试文档
func GenerateTestDocument() *entity.Document {
	id := uuid.New()
	authorID := uuid.New()
	categoryID := uuid.New()

	doc, _ := entity.NewDocument(
		fmt.Sprintf("Test Document %s", id.String()[:8]),
		generateLoremIpsum(500),
		entity.ContentTypeText,
		authorID,
		categoryID,
	)

	doc.Description = fmt.Sprintf("Test description for document %s", id.String()[:8])
	doc.AddTag("test")
	doc.AddTag("sample")
	doc.AddMetadata("source", "test")
	doc.AddMetadata("priority", "low")

	return doc
}

// GenerateTestDocumentWithContent 生成带有特定内容的测试文档
func GenerateTestDocumentWithContent(title, content string) *entity.Document {
	authorID := uuid.New()
	categoryID := uuid.New()

	doc, _ := entity.NewDocument(
		title,
		content,
		entity.ContentTypeText,
		authorID,
		categoryID,
	)

	doc.Description = "Generated test document"
	doc.AddTag("test")
	
	return doc
}

// generateLoremIpsum 生成随机的Lorem Ipsum文本
func generateLoremIpsum(wordCount int) string {
	loremWords := []string{
		"lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
		"sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
		"magna", "aliqua", "ut", "enim", "ad", "minim", "veniam", "quis", "nostrud",
		"exercitation", "ullamco", "laboris", "nisi", "ut", "aliquip", "ex", "ea", "commodo",
		"consequat", "duis", "aute", "irure", "dolor", "in", "reprehenderit", "in",
		"voluptate", "velit", "esse", "cillum", "dolore", "eu", "fugiat", "nulla",
		"pariatur", "excepteur", "sint", "occaecat", "cupidatat", "non", "proident",
		"sunt", "in", "culpa", "qui", "officia", "deserunt", "mollit", "anim", "id", "est",
		"laborum",
	}

	var result []string
	for i := 0; i < wordCount; i++ {
		result = append(result, loremWords[rand.Intn(len(loremWords))])
		if i > 0 && i%15 == 0 {
			result = append(result, ".")
		}
	}

	return strings.Join(result, " ")
}

// WaitForContext 创建一个带有超时的上下文
func WaitForContext() (context.Context, context.CancelFunc) {
	return context.WithTimeout(context.Background(), 10*time.Second)
}

// CleanupTestData 清理测试数据
func CleanupTestData(testDataDir string) error {
	if testDataDir != "" && strings.Contains(testDataDir, "test-data") {
		return os.RemoveAll(testDataDir)
	}
	return nil
} 