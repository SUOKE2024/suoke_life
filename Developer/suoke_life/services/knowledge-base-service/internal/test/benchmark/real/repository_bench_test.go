package real

import (
	"context"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"

	"knowledge-base-service/internal/domain/entity"
)

// 基准测试文档存储库性能
func BenchmarkDocumentRepositorySave(b *testing.B) {
	// 检查环境变量是否设置了跳过真实数据库测试
	if testing.Short() {
		b.Skip("在短测试模式下跳过实际数据库测试 (-short flag)")
	}

	ctx := context.Background()

	// 设置数据库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		b.Fatalf("设置数据库失败: %v", err)
	}
	defer dbCleanup()

	// 设置向量存储
	vectorStore, _, vectorCleanup, err := SetupRealVectorStore(ctx)
	if err != nil {
		b.Fatalf("设置向量存储失败: %v", err)
	}
	defer vectorCleanup()

	// 设置文档存储库
	docRepo, err := SetupRealDocumentRepository(ctx, db, vectorStore)
	if err != nil {
		b.Fatalf("设置文档存储库失败: %v", err)
	}

	// 设置分类存储库并获取测试分类
	catRepo, err := SetupRealCategoryRepository(ctx, db)
	if err != nil {
		b.Fatalf("设置分类存储库失败: %v", err)
	}

	// 获取测试分类
	categories, err := catRepo.FindAll(ctx)
	if err != nil {
		b.Fatalf("获取分类失败: %v", err)
	}

	if len(categories) == 0 {
		b.Fatal("没有找到测试分类")
	}

	// 准备测试作者ID
	authorID := uuid.New()

	b.ResetTimer()

	// 执行基准测试
	for i := 0; i < b.N; i++ {
		// 每次测试创建一个新文档
		doc, err := entity.NewDocument(
			"基准测试文档 "+uuid.New().String(),
			"这是用于基准测试的文档内容，包含足够的文本以测试性能。"+
				"这是用于基准测试的文档内容，包含足够的文本以测试性能。",
			entity.ContentTypeMarkdown,
			authorID,
			categories[0].ID,
		)
		if err != nil {
			b.Fatalf("创建文档失败: %v", err)
		}

		// 测试存储库的Save方法
		err = docRepo.Save(ctx, doc)
		if err != nil {
			b.Fatalf("保存文档失败: %v", err)
		}
	}
}

// 基准测试文档查询性能
func BenchmarkDocumentRepositoryFindByID(b *testing.B) {
	// 检查环境变量是否设置了跳过真实数据库测试
	if testing.Short() {
		b.Skip("在短测试模式下跳过实际数据库测试 (-short flag)")
	}

	ctx := context.Background()

	// 设置数据库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		b.Fatalf("设置数据库失败: %v", err)
	}
	defer dbCleanup()

	// 设置向量存储
	vectorStore, _, vectorCleanup, err := SetupRealVectorStore(ctx)
	if err != nil {
		b.Fatalf("设置向量存储失败: %v", err)
	}
	defer vectorCleanup()

	// 设置文档存储库
	docRepo, err := SetupRealDocumentRepository(ctx, db, vectorStore)
	if err != nil {
		b.Fatalf("设置文档存储库失败: %v", err)
	}

	// 设置分类存储库并获取测试分类
	catRepo, err := SetupRealCategoryRepository(ctx, db)
	if err != nil {
		b.Fatalf("设置分类存储库失败: %v", err)
	}

	// 获取测试分类
	categories, err := catRepo.FindAll(ctx)
	if err != nil {
		b.Fatalf("获取分类失败: %v", err)
	}

	if len(categories) == 0 {
		b.Fatal("没有找到测试分类")
	}

	// 准备测试作者ID和测试文档
	authorID := uuid.New()

	// 创建一个测试文档
	doc, err := entity.NewDocument(
		"查询性能测试文档",
		"这是用于测试文档查询性能的内容。将重复查询这个文档ID来测量数据库性能。",
		entity.ContentTypeMarkdown,
		authorID,
		categories[0].ID,
	)
	if err != nil {
		b.Fatalf("创建文档失败: %v", err)
	}

	// 保存文档
	err = docRepo.Save(ctx, doc)
	if err != nil {
		b.Fatalf("保存文档失败: %v", err)
	}

	// 确保文档已保存
	savedDoc, err := docRepo.FindByID(ctx, doc.ID)
	if err != nil {
		b.Fatalf("获取保存的文档失败: %v", err)
	}

	assert.NotNil(b, savedDoc, "保存的文档不应为nil")

	b.ResetTimer()

	// 执行基准测试
	for i := 0; i < b.N; i++ {
		// 测试查询性能
		_, err := docRepo.FindByID(ctx, doc.ID)
		if err != nil {
			b.Fatalf("查询文档失败: %v", err)
		}
	}
}

// 基准测试文档更新性能
func BenchmarkDocumentRepositoryUpdate(b *testing.B) {
	// 检查环境变量是否设置了跳过真实数据库测试
	if testing.Short() {
		b.Skip("在短测试模式下跳过实际数据库测试 (-short flag)")
	}

	ctx := context.Background()

	// 设置数据库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		b.Fatalf("设置数据库失败: %v", err)
	}
	defer dbCleanup()

	// 设置向量存储
	vectorStore, _, vectorCleanup, err := SetupRealVectorStore(ctx)
	if err != nil {
		b.Fatalf("设置向量存储失败: %v", err)
	}
	defer vectorCleanup()

	// 设置文档存储库
	docRepo, err := SetupRealDocumentRepository(ctx, db, vectorStore)
	if err != nil {
		b.Fatalf("设置文档存储库失败: %v", err)
	}

	// 设置分类存储库并获取测试分类
	catRepo, err := SetupRealCategoryRepository(ctx, db)
	if err != nil {
		b.Fatalf("设置分类存储库失败: %v", err)
	}

	// 获取测试分类
	categories, err := catRepo.FindAll(ctx)
	if err != nil {
		b.Fatalf("获取分类失败: %v", err)
	}

	if len(categories) == 0 {
		b.Fatal("没有找到测试分类")
	}

	// 准备测试作者ID和测试文档
	authorID := uuid.New()

	// 创建一个测试文档
	doc, err := entity.NewDocument(
		"更新性能测试文档",
		"这是用于测试文档更新性能的原始内容。将反复更新这个文档来测量数据库性能。",
		entity.ContentTypeMarkdown,
		authorID,
		categories[0].ID,
	)
	if err != nil {
		b.Fatalf("创建文档失败: %v", err)
	}

	// 保存文档
	err = docRepo.Save(ctx, doc)
	if err != nil {
		b.Fatalf("保存文档失败: %v", err)
	}

	b.ResetTimer()

	// 执行基准测试
	for i := 0; i < b.N; i++ {
		// 更新文档内容
		doc.Content = "这是更新后的内容 " + uuid.New().String()
		doc.Title = "更新的标题 " + uuid.New().String()

		// 测试更新性能
		err = docRepo.Update(ctx, doc)
		if err != nil {
			b.Fatalf("更新文档失败: %v", err)
		}
	}
}

// 基准测试 - PostgresDocumentRepository 保存文档
func BenchmarkPostgresDocumentRepository_Save(b *testing.B) {
	ctx := context.Background()

	// 设置数据库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		b.Fatalf("设置数据库失败: %v", err)
	}
	defer dbCleanup()

	// 设置向量存储
	vectorStore, _, vectorCleanup, err := SetupRealVectorStore(ctx)
	if err != nil {
		b.Fatalf("设置向量存储失败: %v", err)
	}
	defer vectorCleanup()

	// 设置文档存储库
	docRepo, err := SetupRealDocumentRepository(ctx, db, vectorStore)
	if err != nil {
		b.Fatalf("设置文档存储库失败: %v", err)
	}

	// 准备测试数据
	categoryID := uuid.MustParse("00000000-0000-0000-0000-000000000001")
	authorID := uuid.New()

	doc, err := entity.NewDocument(
		"基准测试文档",
		"这是一份用于基准测试的文档内容，包含足够的文本以便进行测试。",
		entity.ContentTypeText,
		authorID,
		categoryID,
	)
	if err != nil {
		b.Fatalf("创建文档失败: %v", err)
	}

	// 设置附加信息
	doc.AddMetadata("source", "benchmark")
	doc.AddMetadata("language", "zh-CN")

	// 重置计时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		// 每次使用不同的ID避免冲突
		newDoc := *doc // 复制文档
		newDoc.ID = uuid.New()

		err := docRepo.Save(ctx, &newDoc)
		if err != nil {
			b.Fatalf("保存文档失败: %v", err)
		}
	}
}

// 基准测试 - PostgresDocumentRepository 根据ID查找文档
func BenchmarkPostgresDocumentRepository_FindByID(b *testing.B) {
	ctx := context.Background()

	// 设置数据库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		b.Fatalf("设置数据库失败: %v", err)
	}
	defer dbCleanup()

	// 设置向量存储
	vectorStore, _, vectorCleanup, err := SetupRealVectorStore(ctx)
	if err != nil {
		b.Fatalf("设置向量存储失败: %v", err)
	}
	defer vectorCleanup()

	// 设置文档存储库
	docRepo, err := SetupRealDocumentRepository(ctx, db, vectorStore)
	if err != nil {
		b.Fatalf("设置文档存储库失败: %v", err)
	}

	// 准备测试数据 - 先保存一个文档
	categoryID := uuid.MustParse("00000000-0000-0000-0000-000000000001")
	authorID := uuid.New()

	doc, err := entity.NewDocument(
		"基准测试文档",
		"这是一份用于基准测试的文档内容，包含足够的文本以便进行测试。",
		entity.ContentTypeText,
		authorID,
		categoryID,
	)
	if err != nil {
		b.Fatalf("创建文档失败: %v", err)
	}

	// 添加元数据
	doc.AddMetadata("source", "benchmark")
	doc.AddMetadata("language", "zh-CN")

	err = docRepo.Save(ctx, doc)
	if err != nil {
		b.Fatalf("保存测试文档失败: %v", err)
	}

	// 重置计时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		_, err := docRepo.FindByID(ctx, doc.ID)
		if err != nil {
			b.Fatalf("查找文档失败: %v", err)
		}
	}
}

// 基准测试 - PostgresDocumentRepository 文档搜索
func BenchmarkPostgresDocumentRepository_Search(b *testing.B) {
	ctx := context.Background()

	// 设置数据库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		b.Fatalf("设置数据库失败: %v", err)
	}
	defer dbCleanup()

	// 设置向量存储
	vectorStore, _, vectorCleanup, err := SetupRealVectorStore(ctx)
	if err != nil {
		b.Fatalf("设置向量存储失败: %v", err)
	}
	defer vectorCleanup()

	// 设置文档存储库
	docRepo, err := SetupRealDocumentRepository(ctx, db, vectorStore)
	if err != nil {
		b.Fatalf("设置文档存储库失败: %v", err)
	}

	// 准备测试数据 - 保存多个文档
	categoryID := uuid.MustParse("00000000-0000-0000-0000-000000000001")
	authorID := uuid.New()

	for i := 0; i < 5; i++ {
		doc, err := entity.NewDocument(
			"基准测试文档 "+string(rune('A'+i)),
			"这是一份用于基准测试的文档内容，包含关键词如：测试、基准、性能。",
			entity.ContentTypeText,
			authorID,
			categoryID,
		)
		if err != nil {
			b.Fatalf("创建文档失败: %v", err)
		}

		// 设置状态为已发布
		doc.Publish()

		// 添加元数据
		doc.AddMetadata("source", "benchmark")
		doc.AddMetadata("language", "zh-CN")

		err = docRepo.Save(ctx, doc)
		if err != nil {
			b.Fatalf("保存测试文档失败: %v", err)
		}
	}

	// 重置计时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		_, err := docRepo.Search(ctx, "基准测试")
		if err != nil {
			b.Fatalf("搜索文档失败: %v", err)
		}
	}
}

// 测试设置PostgreSQL文档存储库
func TestSetupPostgresDocumentRepository(t *testing.T) {
	// 在短测试模式下跳过
	if testing.Short() {
		t.Skip("跳过实际数据库测试 (-short flag)")

		// 使用模拟向量存储进行基本测试
		ctx := context.Background()
		vectorStore := NewMockVectorStore()

		// 确保模拟向量存储能正常工作
		docID := uuid.New().String()
		vector := []float32{0.1, 0.2, 0.3, 0.4, 0.5}

		// 存储向量
		vectorID, err := vectorStore.StoreVector(ctx, docID, vector)
		assert.NoError(t, err, "存储向量应成功")
		assert.Equal(t, docID, vectorID, "返回的向量ID应与文档ID相同")

		// 搜索向量
		ids, scores, err := vectorStore.SearchVector(ctx, vector, 5)
		assert.NoError(t, err, "搜索向量应成功")
		assert.NotEmpty(t, ids, "搜索结果不应为空")
		assert.NotEmpty(t, scores, "相似度分数不应为空")

		// 删除向量
		err = vectorStore.DeleteVector(ctx, vectorID)
		assert.NoError(t, err, "删除向量应成功")

		t.Log("模拟向量存储测试通过")
		return
	}

	ctx := context.Background()

	// 设置数据库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	assert.NoError(t, err, "设置数据库应成功")
	assert.NotNil(t, db, "数据库管理器不应为nil")
	defer dbCleanup()

	// 设置向量存储
	vectorStore, _, vectorCleanup, err := SetupRealVectorStore(ctx)
	assert.NoError(t, err, "设置向量存储应成功")
	assert.NotNil(t, vectorStore, "向量存储不应为nil")
	defer vectorCleanup()

	// 设置文档存储库
	docRepo, err := SetupRealDocumentRepository(ctx, db, vectorStore)
	assert.NoError(t, err, "设置文档存储库应成功")
	assert.NotNil(t, docRepo, "文档存储库不应为nil")
}
