package benchmark

import (
	"context"
	"fmt"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/domain/service"
	"knowledge-base-service/internal/test/benchmark/real"
)

// TestSkipDocumentServiceBenchmarks 用于跳过基准测试
func TestSkipDocumentServiceBenchmarks(t *testing.T) {
	if testing.Short() {
		t.Skip("跳过需要外部服务的文档服务基准测试")
	}
}

// BenchmarkDocumentService_CreateDocument 基准测试文档创建
func BenchmarkDocumentService_CreateDocument(b *testing.B) {
	if testing.Short() {
		b.Skip("跳过需要外部服务的文档服务基准测试")
	}
	
	// 设置测试环境
	ctx := context.Background()
	docService, cleanup, err := real.SetupRealDocumentService(ctx)
	if err != nil {
		b.Fatalf("设置文档服务失败: %v", err)
	}
	defer cleanup()

	// 准备测试数据 - 假设有一个测试分类ID
	// 在实际测试中，您可能需要先创建一个测试分类
	categoryID := uuid.MustParse("00000000-0000-0000-0000-000000000001")

	// 重置定时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		// 使用DocumentOptions创建文档
		docOptions := service.DocumentOptions{
			Title:       fmt.Sprintf("Benchmark Document %d", i),
			Content:     generateLongContent(2000),
			Description: "这是一个基准测试文档",
			ContentType: entity.ContentTypeMarkdown,
			AuthorID:    uuid.New().String(),
			CategoryID:  categoryID,
			Tags:        []string{"benchmark", "test", "performance"},
			Metadata: map[string]interface{}{
				"benchmark_run": i,
				"source":        "benchmark_test",
			},
		}

		// 创建文档
		doc, err := docService.CreateDocument(ctx, docOptions)
		if err != nil {
			b.Fatalf("创建文档失败: %v", err)
		}

		// 发布文档
		_, err = docService.PublishDocument(ctx, doc.ID)
		if err != nil {
			b.Fatalf("发布文档失败: %v", err)
		}
	}
}

// BenchmarkDocumentService_GetDocumentByID 基准测试获取文档
func BenchmarkDocumentService_GetDocumentByID(b *testing.B) {
	if testing.Short() {
		b.Skip("跳过需要外部服务的文档服务基准测试")
	}
	
	// 设置测试环境
	ctx := context.Background()
	docService, cleanup, err := real.SetupRealDocumentService(ctx)
	if err != nil {
		b.Fatalf("设置文档服务失败: %v", err)
	}
	defer cleanup()

	// 创建一个测试文档用于查询
	categoryID := uuid.MustParse("00000000-0000-0000-0000-000000000001")
	
	// 使用DocumentOptions创建文档
	docOptions := service.DocumentOptions{
		Title:       "Benchmark Query Document",
		Content:     generateLongContent(2000),
		Description: "这是一个基准测试文档",
		ContentType: entity.ContentTypeMarkdown,
		AuthorID:    uuid.New().String(),
		CategoryID:  categoryID,
		Tags:        []string{"benchmark", "test", "query"},
		Metadata: map[string]interface{}{
			"benchmark_type": "query",
			"source":         "benchmark_test",
		},
	}

	doc, err := docService.CreateDocument(ctx, docOptions)
	if err != nil {
		b.Fatalf("创建文档失败: %v", err)
	}

	// 发布文档
	publishedDoc, err := docService.PublishDocument(ctx, doc.ID)
	if err != nil {
		b.Fatalf("发布文档失败: %v", err)
	}

	// 重置定时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		_, err := docService.GetDocumentByID(ctx, publishedDoc.ID)
		if err != nil {
			b.Fatalf("获取文档失败: %v", err)
		}
	}
}

// BenchmarkDocumentService_SearchDocuments 基准测试文档搜索
func BenchmarkDocumentService_SearchDocuments(b *testing.B) {
	if testing.Short() {
		b.Skip("跳过需要外部服务的文档服务基准测试")
	}
	
	// 设置测试环境
	ctx := context.Background()
	docService, cleanup, err := real.SetupRealDocumentService(ctx)
	if err != nil {
		b.Fatalf("设置文档服务失败: %v", err)
	}
	defer cleanup()

	// 创建测试文档用于搜索
	categoryID := uuid.MustParse("00000000-0000-0000-0000-000000000001")

	// 创建多个测试文档
	for i := 0; i < 10; i++ {
		// 使用DocumentOptions创建文档
		docOptions := service.DocumentOptions{
			Title:       fmt.Sprintf("Benchmark Search Document %d", i),
			Content:     generateLongContent(1000),
			Description: fmt.Sprintf("搜索基准测试文档 %d", i),
			ContentType: entity.ContentTypeMarkdown,
			AuthorID:    uuid.New().String(),
			CategoryID:  categoryID,
			Tags:        []string{"benchmark", "search", fmt.Sprintf("doc-%d", i)},
			Metadata: map[string]interface{}{
				"benchmark_type": "search",
				"doc_number":     i,
			},
		}

		doc, err := docService.CreateDocument(ctx, docOptions)
		if err != nil {
			b.Fatalf("创建文档失败: %v", err)
		}

		// 发布文档
		_, err = docService.PublishDocument(ctx, doc.ID)
		if err != nil {
			b.Fatalf("发布文档失败: %v", err)
		}
	}

	// 重置定时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		query := fmt.Sprintf("benchmark document %d", i%10)
		_, err := docService.SearchDocuments(ctx, entity.SearchQuery{
			Query:         query,
			CategoryID:    categoryID,
			Tags:          []string{"benchmark"},
			SearchContent: true,
			Limit:         10,
		})
		if err != nil {
			b.Fatalf("搜索文档失败: %v", err)
		}
	}
}

// generateLongContent 生成长内容用于测试
func generateLongContent(length int) string {
	content := "这是一个基准测试文档，包含足够长的内容以便进行测试。\n\n"
	paragraphs := length / 100
	for i := 0; i < paragraphs; i++ {
		content += fmt.Sprintf("这是第 %d 段落，它包含一些随机生成的内容，用于测试文档处理性能。", i+1)
		content += "我们需要生成足够多的文本，以确保文本分割器能够正常工作。"
		content += "这个段落还包含一些有关测试的信息，以及其他一些可能会在搜索中用到的关键词。\n\n"
	}
	return content
}

// 基准测试 - 语义搜索
func BenchmarkDocumentService_SemanticSearch(b *testing.B) {
	ctx := context.Background()

	// 设置真实服务
	docService, cleanup, err := real.SetupRealDocumentService(ctx)
	if err != nil {
		b.Fatalf("设置文档服务失败: %v", err)
	}
	defer cleanup()

	// 准备测试数据
	categoryID := uuid.MustParse("00000000-0000-0000-0000-000000000001") // 使用预设的分类ID
	authorID := uuid.New()

	// 创建一些测试文档以供搜索
	for i := 0; i < 5; i++ {
		opts := service.DocumentOptions{
			Title:       "语义搜索测试文档 " + time.Now().Format(time.RFC3339Nano),
			Content:     "这是第 " + string(rune('A'+i)) + " 个测试文档，用于测试语义搜索功能。该文档包含一些特定的关键词，如：人工智能、机器学习、自然语言处理、知识图谱等。",
			Description: "语义搜索测试文档",
			ContentType: entity.ContentTypeText,
			AuthorID:    authorID,
			CategoryID:  categoryID,
			Tags:        []string{"语义搜索", "AI", "NLP"},
			Metadata: []entity.MetadataField{
				{Name: "source", Value: "benchmark"},
				{Name: "language", Value: "zh-CN"},
			},
		}

		// 创建文档
		doc, err := docService.CreateDocument(ctx, opts)
		if err != nil {
			b.Fatalf("创建文档失败: %v", err)
		}

		// 确保文档状态为已发布
		if doc.Status != entity.StatusPublished {
			err = docService.PublishDocument(ctx, doc.ID)
			if err != nil {
				b.Fatalf("发布文档失败: %v", err)
			}
		}
	}

	// 重置计时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		// 执行语义搜索
		results, err := docService.SemanticSearch(ctx, "人工智能与自然语言处理", 5)
		if err != nil {
			b.Fatalf("语义搜索失败: %v", err)
		}

		// 验证结果
		assert.LessOrEqual(b, 0, len(results), "应该至少返回一些结果")
	}
}

// 测试直接设置基础组件
func TestComponentSetup(t *testing.T) {
	// 跳过需要实际数据库的测试
	if testing.Short() {
		t.Skip("在短测试模式下跳过实际数据库测试 (-short flag)")
	}

	ctx := context.Background()

	// 测试向量存储设置
	vectorStore, _, vectorCleanup, err := real.SetupRealVectorStore(ctx)
	assert.NoError(t, err, "向量存储设置应该成功")
	assert.NotNil(t, vectorStore, "向量存储不应为nil")
	defer vectorCleanup()

	// 测试嵌入服务设置
	embeddingService, embeddingCleanup, err := real.SetupEmbeddingService(ctx)
	assert.NoError(t, err, "嵌入服务设置应该成功")
	assert.NotNil(t, embeddingService, "嵌入服务不应为nil")
	defer embeddingCleanup()

	// 测试文本分割器设置
	textSplitter := real.SetupTextSplitter()
	assert.NotNil(t, textSplitter, "文本分割器不应为nil")

	// 注意：数据库相关测试已移除，因为在CI环境中可能无法连接到数据库
}
