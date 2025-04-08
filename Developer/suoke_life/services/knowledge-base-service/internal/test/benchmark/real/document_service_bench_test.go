package real

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/google/uuid"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/domain/service"
)

// 使用实际数据库和向量存储的文档服务基准测试
func BenchmarkRealDocumentServiceCreate(b *testing.B) {
	ctx := context.Background()

	// 设置文档服务
	docService, cleanup, err := SetupRealDocumentService(ctx)
	if err != nil {
		b.Fatalf("设置文档服务失败: %v", err)
	}
	defer cleanup()

	// 获取测试分类ID
	// 先设置分类存储库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		b.Fatalf("设置数据库失败: %v", err)
	}
	defer dbCleanup()

	catRepo, err := SetupRealCategoryRepository(ctx, db)
	if err != nil {
		b.Fatalf("设置分类存储库失败: %v", err)
	}

	categories, err := catRepo.FindAll(ctx)
	if err != nil || len(categories) == 0 {
		b.Fatalf("获取分类失败: %v", err)
	}
	categoryID := categories[0].ID

	// 创建测试作者ID
	authorID := uuid.New()

	// 准备测试内容
	testContent := generateTestText(5000)

	// 重置计时器，开始测量真正的基准测试部分
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		titlePrefix := fmt.Sprintf("基准测试文档 %s", getTimeStamp())
		benchmarkCreateDocument(b, ctx, docService, titlePrefix, testContent, categoryID, authorID)
	}
}

// 使用实际数据库和向量存储测试语义搜索性能
func BenchmarkRealSemanticSearch(b *testing.B) {
	ctx := context.Background()

	// 设置文档服务
	docService, cleanup, err := SetupRealDocumentService(ctx)
	if err != nil {
		b.Fatalf("设置文档服务失败: %v", err)
	}
	defer cleanup()

	// 获取测试分类ID
	// 先设置分类存储库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		b.Fatalf("设置数据库失败: %v", err)
	}
	defer dbCleanup()

	catRepo, err := SetupRealCategoryRepository(ctx, db)
	if err != nil {
		b.Fatalf("设置分类存储库失败: %v", err)
	}

	categories, err := catRepo.FindAll(ctx)
	if err != nil || len(categories) == 0 {
		b.Fatalf("获取分类失败: %v", err)
	}
	categoryID := categories[0].ID

	// 创建测试作者ID
	authorID := uuid.New()

	// 准备测试数据，创建一批测试文档进行语义搜索
	// 注意：这一步不计入基准测试时间
	b.StopTimer()
	numDocs := 10
	testContent := generateTestText(3000)
	for i := 0; i < numDocs; i++ {
		titlePrefix := fmt.Sprintf("语义搜索测试文档 %d", i)
		benchmarkCreateDocument(b, ctx, docService, titlePrefix, testContent, categoryID, authorID)
	}
	b.StartTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		// 执行语义搜索
		query := "中医如何调理亚健康状态"
		result, err := docService.SemanticSearch(ctx, query, 5)
		if err != nil {
			b.Fatalf("语义搜索失败: %v", err)
		}

		// 确保返回了结果
		if len(result) == 0 {
			b.Logf("警告: 语义搜索未返回任何结果")
		}
	}
}

// 帮助函数：创建单个文档进行基准测试
func benchmarkCreateDocument(b *testing.B, ctx context.Context, docService *service.DocumentService, titlePrefix, content string, categoryID, authorID uuid.UUID) {
	// 创建文档
	// 从 map 转换为 MetadataField 数组
	metadata := []entity.MetadataField{
		{Name: "testType", Value: "benchmark"},
		{Name: "createdBy", Value: "benchmark_test"},
	}

	opts := service.DocumentOptions{
		Title:       titlePrefix,
		Content:     content,
		Description: "用于基准测试的文档描述",
		ContentType: "text/markdown",
		AuthorID:    authorID,
		CategoryID:  categoryID,
		Tags:        []string{"测试", "基准测试", "中医"},
		Metadata:    metadata,
	}

	_, err := docService.CreateDocument(ctx, opts)
	if err != nil {
		b.Fatalf("创建文档失败: %v", err)
	}
}

// 生成测试文本
func generateTestText(length int) string {
	// 中医理论相关的示例文本
	baseText := `
中医学是中国传统医学，其理论体系建立在中国传统哲学、古代的物质观念等方面的基础上，强调整体观念、辨证论治。中医学认为人体是一个统一的整体，同时人又与自然、社会环境有着密切的关系，通过经络系统沟通内外，联络上下及脏腑之间的生理病理变化。在中医看来，人体内气血是恒常运行不息的，气血通过经络运行全身，濡养周身。中医认为疾病的产生主要是由多种因素引起的，主要包括外感六淫、内伤七情、不内外因三者。外感六淫指风、寒、暑、湿、燥、火。内伤七情指喜、怒、忧、思、悲、恐、惊。不内外因指饮食不节、劳逸过度、跌打损伤、虫兽伤害、火热烧灼等。疾病的发生、发展与诊断相对于西医，中医更加重视人体整体生理病理的变化、更加重视机体功能的调整和调理，相对于西医，中医在某些疾病的治疗和作用上比西医更加具有优势，例如，中医在治疗普通感冒和调理亚健康状态以及一些疑难杂症方面有一定的优势，特别是中医不良反应更少，适合长期服用，没有毒副作用，对身体的各方面都能够产生比较好的保健效果。在当今西医占主导地位的社会，中医作为传统医学，临床价值依然不可低估，中医与西医各有所长、相互补充，构成了我国医疗卫生事业的特色。

中医诊断方法：四诊是中医的诊断方法，即望、闻、问、切四种诊法的总称。四诊合参是诊断疾病的基本方法。望诊是运用医生视觉去观察患者全身以及局部的形态、精神、颜色、状态等的诊察方法。包括：望神色（精神、气色）、望形体（体型、姿态、动作）、望五官（眼、鼻、耳、口、唇、齿等）、望皮肤、望排泄物（痰液、呕吐物、尿、便等）、望舌象。闻诊指医生运用听觉和嗅觉，了解患者声音、气息、呼吸变化的诊察方法。包括：闻声音（音哑、语謇、谵语、譫妄、鼾声等）、闻气味：闻口气和闻体臭。问诊是医生向患者及其家属询问病情和有关疾病发生、发展情况的诊察方法。包括询问主诉、发病情况、现病史、既往史、个人史、婚育史、家族史等。切诊是医生运用触诊的方法，通过按、摸、推、叩等手法，诊察患者全身以及局部的情况的诊察方法。包括脉诊和按诊（腹诊、肤诊、背诊等）。
	`

	// 确保文本长度达到要求
	for len(baseText) < length {
		baseText += baseText
	}

	// 截取指定长度
	return baseText[:length]
}

func BenchmarkRealGetDocumentByID(b *testing.B) {
	ctx := context.Background()
	docService, cleanup, err := SetupRealDocumentService(ctx)
	if err != nil {
		b.Fatalf("设置文档服务失败: %v", err)
	}
	defer cleanup()

	// 创建一个文档用于测试
	doc := createTestDocument(ctx, b, docService)

	// 重置计时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		_, err := docService.GetDocumentByID(ctx, doc.ID)
		if err != nil {
			b.Fatalf("获取文档失败: %v", err)
		}
	}
}

func BenchmarkRealGetDocumentsByCategory(b *testing.B) {
	ctx := context.Background()
	docService, cleanup, err := SetupRealDocumentService(ctx)
	if err != nil {
		b.Fatalf("设置文档服务失败: %v", err)
	}
	defer cleanup()

	// 获取第一个分类
	// 先设置分类存储库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		b.Fatalf("设置数据库失败: %v", err)
	}
	defer dbCleanup()

	catRepo, err := SetupRealCategoryRepository(ctx, db)
	if err != nil {
		b.Fatalf("设置分类存储库失败: %v", err)
	}

	categories, err := catRepo.FindAll(ctx)
	if err != nil || len(categories) == 0 {
		b.Fatalf("获取分类失败: %v", err)
	}

	categoryID := categories[0].ID

	// 创建多个文档用于测试
	for i := 0; i < 10; i++ {
		createTestDocumentInCategory(ctx, b, docService, categoryID)
	}

	// 重置计时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		_, err := docService.GetDocumentsByCategory(ctx, categoryID)
		if err != nil {
			b.Fatalf("获取分类文档失败: %v", err)
		}
	}
}

func BenchmarkRealSearchDocuments(b *testing.B) {
	ctx := context.Background()
	docService, cleanup, err := SetupRealDocumentService(ctx)
	if err != nil {
		b.Fatalf("设置文档服务失败: %v", err)
	}
	defer cleanup()

	// 创建一批测试文档
	createMultipleTestDocuments(ctx, b, docService, 20)

	// 重置计时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		_, err := docService.SearchDocuments(ctx, "中医")
		if err != nil {
			b.Fatalf("搜索文档失败: %v", err)
		}
	}
}

func BenchmarkRealCreateDocument(b *testing.B) {
	ctx := context.Background()
	docService, cleanup, err := SetupRealDocumentService(ctx)
	if err != nil {
		b.Fatalf("设置文档服务失败: %v", err)
	}
	defer cleanup()

	// 获取一个分类ID
	// 先设置分类存储库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		b.Fatalf("设置数据库失败: %v", err)
	}
	defer dbCleanup()

	catRepo, err := SetupRealCategoryRepository(ctx, db)
	if err != nil {
		b.Fatalf("设置分类存储库失败: %v", err)
	}

	categories, err := catRepo.FindAll(ctx)
	if err != nil || len(categories) == 0 {
		b.Fatalf("获取分类失败: %v", err)
	}

	categoryID := categories[0].ID

	// 重置计时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		// 从 map 转换为 MetadataField 数组
		metadata := []entity.MetadataField{
			{Name: "testType", Value: "benchmark"},
			{Name: "createdBy", Value: "benchmark_test"},
			{Name: "index", Value: fmt.Sprintf("%d", i)},
		}

		opts := service.DocumentOptions{
			Title:       fmt.Sprintf("测试文档 %d", i),
			Content:     generateTestContent(1000),
			Description: "这是一个用于基准测试的文档",
			ContentType: "text/markdown",
			AuthorID:    uuid.New(),
			CategoryID:  categoryID,
			Tags:        []string{"测试", "基准测试", "中医"},
			Metadata:    metadata,
		}

		_, err := docService.CreateDocument(ctx, opts)
		if err != nil {
			b.Fatalf("创建文档失败: %v", err)
		}
	}
}

func BenchmarkRealUpdateDocument(b *testing.B) {
	ctx := context.Background()
	docService, cleanup, err := SetupRealDocumentService(ctx)
	if err != nil {
		b.Fatalf("设置文档服务失败: %v", err)
	}
	defer cleanup()

	// 创建一个文档用于测试
	doc := createTestDocument(ctx, b, docService)

	// 重置计时器
	b.ResetTimer()

	// 运行基准测试
	for i := 0; i < b.N; i++ {
		title := fmt.Sprintf("更新后的测试文档 %d", i)
		content := generateTestContent(1200)
		description := "这是一个更新后的测试文档"
		contentType := entity.ContentTypeMarkdown
		tags := []string{"测试", "已更新", "中医理论"}

		// 使用原始分类ID
		_, err := docService.UpdateDocument(ctx, doc.ID, title, content, description, contentType, doc.CategoryID, tags)
		if err != nil {
			b.Fatalf("更新文档失败: %v", err)
		}
	}
}

// 帮助函数 - 创建测试文档
func createTestDocument(ctx context.Context, b *testing.B, docService *service.DocumentService) *entity.Document {
	// 获取一个分类ID
	// 先设置分类存储库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		b.Fatalf("设置数据库失败: %v", err)
	}
	defer dbCleanup()

	catRepo, err := SetupRealCategoryRepository(ctx, db)
	if err != nil {
		b.Fatalf("设置分类存储库失败: %v", err)
	}

	categories, err := catRepo.FindAll(ctx)
	if err != nil || len(categories) == 0 {
		b.Fatalf("获取分类失败: %v", err)
	}

	categoryID := categories[0].ID

	// 从 map 转换为 MetadataField 数组
	metadata := []entity.MetadataField{
		{Name: "testType", Value: "benchmark"},
		{Name: "createdBy", Value: "benchmark_test"},
	}

	opts := service.DocumentOptions{
		Title:       "基准测试文档",
		Content:     generateTestContent(2000),
		Description: "这是一个用于基准测试的文档",
		ContentType: "text/markdown",
		AuthorID:    uuid.New(),
		CategoryID:  categoryID,
		Tags:        []string{"测试", "基准测试", "中医"},
		Metadata:    metadata,
	}

	doc, err := docService.CreateDocument(ctx, opts)
	if err != nil {
		b.Fatalf("创建测试文档失败: %v", err)
	}

	return doc
}

// 在指定分类中创建测试文档
func createTestDocumentInCategory(ctx context.Context, b *testing.B, docService *service.DocumentService, categoryID uuid.UUID) *entity.Document {
	// 从 map 转换为 MetadataField 数组
	metadata := []entity.MetadataField{
		{Name: "testType", Value: "categoryTest"},
		{Name: "createdBy", Value: "benchmark_test"},
	}

	opts := service.DocumentOptions{
		Title:       fmt.Sprintf("分类测试文档 %s", uuid.New().String()[0:8]),
		Content:     generateTestContent(1500),
		Description: "这是一个用于分类测试的文档",
		ContentType: "text/markdown",
		AuthorID:    uuid.New(),
		CategoryID:  categoryID,
		Tags:        []string{"测试", "分类测试", "中医"},
		Metadata:    metadata,
	}

	doc, err := docService.CreateDocument(ctx, opts)
	if err != nil {
		b.Fatalf("创建分类测试文档失败: %v", err)
	}

	return doc
}

// 创建多个测试文档
func createMultipleTestDocuments(ctx context.Context, b *testing.B, docService *service.DocumentService, count int) {
	// 获取所有分类
	// 先设置分类存储库
	db, dbCleanup, err := SetupRealDatabase(ctx)
	if err != nil {
		b.Fatalf("设置数据库失败: %v", err)
	}
	defer dbCleanup()

	catRepo, err := SetupRealCategoryRepository(ctx, db)
	if err != nil {
		b.Fatalf("设置分类存储库失败: %v", err)
	}

	categories, err := catRepo.FindAll(ctx)
	if err != nil || len(categories) == 0 {
		b.Fatalf("获取分类失败: %v", err)
	}

	// 为每个分类创建一些文档
	for i := 0; i < count; i++ {
		categoryID := categories[i%len(categories)].ID

		// 从 map 转换为 MetadataField 数组
		metadata := []entity.MetadataField{
			{Name: "testType", Value: "batchTest"},
			{Name: "createdBy", Value: "benchmark_test"},
			{Name: "index", Value: fmt.Sprintf("%d", i)},
		}

		opts := service.DocumentOptions{
			Title:       fmt.Sprintf("批量测试文档 %d", i),
			Content:     generateTestContent(1000 + i*100),
			Description: fmt.Sprintf("这是批量测试文档 %d", i),
			ContentType: "text/markdown",
			AuthorID:    uuid.New(),
			CategoryID:  categoryID,
			Tags:        []string{"测试", "批量测试", fmt.Sprintf("标签%d", i%5)},
			Metadata:    metadata,
		}

		_, err := docService.CreateDocument(ctx, opts)
		if err != nil {
			b.Fatalf("创建批量测试文档失败: %v", err)
		}
	}
}

// 生成测试内容
func generateTestContent(length int) string {
	// 中医理论相关的示例句子
	sentences := []string{
		"中医学是研究人体生理、病理以及疾病的诊断和防治等的一门传统医学，其基本理论包括阴阳五行、藏象、气血津液、经络等学说。",
		"阴阳学说认为，自然界的事物和现象都可以划分为阴和阳两大类，它们相互对立又相互依存、相互消长又相互转化。",
		"五行学说认为，自然界是由木、火、土、金、水五种基本物质组成的，它们之间相互资生、相互制约，维持着整体的平衡。",
		"藏象学说主要研究人体脏腑的生理功能、病理变化及其相互关系。中医将人体脏腑分为五脏（心、肝、脾、肺、肾）和六腑（胆、胃、小肠、大肠、膀胱、三焦）。",
		"气血津液是构成人体和维持人体生命活动的基本物质。气是人体最基本的物质，具有推动、温煦、防御、固摄、气化等作用。",
		"经络学说认为，经络是运行气血、联系脏腑、沟通上下内外的通道。它由十二经脉、奇经八脉、十五络脉、十二经别、十二经筋和十二皮部组成。",
		"中医诊断方法主要包括望、闻、问、切四诊。望诊是观察患者的精神状态、面色、舌苔等；闻诊是听患者的声音和嗅其气味；问诊是询问患者的病情；切诊是切脉和按压患处。",
		"中医治疗方法多种多样，主要包括中药、针灸、推拿、拔罐、刮痧、气功等。中药治疗讲究君臣佐使，针灸治疗讲究经络穴位。",
		"中医养生强调\"正气存内，邪不可干\"，注重保养正气、调神养心、饮食有节、起居有常、适当运动等。",
		"中医\"治未病\"思想是防病于未然，在疾病发生前进行预防，或在疾病早期进行干预，防止疾病进一步发展。",
	}

	// 根据指定长度生成内容
	content := ""
	sentenceIndex := 0

	for len(content) < length {
		content += sentences[sentenceIndex%len(sentences)] + " "
		sentenceIndex++
	}

	return content[:length]
}

// 生成当前时间戳
func getTimeStamp() string {
	return time.Now().Format("20060102150405")
}
