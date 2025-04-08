package benchmark

import (
	"context"
	"math/rand"
	"strings"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/domain/service"
	"knowledge-base-service/internal/test/mocks"
)

// 基准测试语义搜索功能
func BenchmarkSemanticSearch(b *testing.B) {
	ctx := context.Background()

	// 创建文档服务
	docService, teardown, _ := setupSemanticSearchTestEnv(ctx)
	defer teardown()

	// 准备测试数据 - 创建有足够语义内容的文档
	titles := []string{
		"中医养生理论概述",
		"艾灸疗法的应用与研究",
		"经络学说的现代价值",
		"针灸治疗常见病",
		"中药材的功效分类",
	}

	contents := []string{
		"中医养生是中国传统医学的重要组成部分，强调天人合一、阴阳平衡等理念。通过调整饮食起居、情志调摄、运动导引等方法，达到防病治病、延年益寿的目的。",
		"艾灸是中医传统外治疗法，利用艾叶燃烧产生的热力和药性，通过穴位熏灼，起到温经通络、驱寒除湿、补虚扶阳等作用。现代研究表明，艾灸具有调节免疫、改善微循环等功效。",
		"经络学说是中医理论体系的核心之一，阐述了人体内气血运行的通路和规律。现代科学研究发现，经络循行路线与神经、血管分布有一定相关性，对疾病诊断和治疗具有重要指导意义。",
		"针灸治疗是基于经络理论，通过在特定穴位刺入针具，调节人体气血平衡，广泛应用于内科、妇科、儿科等疾病的治疗。对疼痛、瘫痪等症状尤其有效。",
		"中药材根据其性味归经和功效，可分为解表、清热、泻下、温里、化湿、利水渗湿等类别。不同类别的中药在临床上有针对性地应用于不同的症候。",
	}

	categoryID := uuid.New()
	authorID := uuid.New()

	// 创建测试文档
	for i := 0; i < len(titles); i++ {
		opts := service.DocumentOptions{
			Title:       titles[i],
			Description: "基准测试用中医文档",
			Content:     contents[i],
			ContentType: entity.ContentTypeMarkdown,
			CategoryID:  categoryID,
			AuthorID:    authorID,
			Tags:        []string{"中医", "养生", "测试"},
		}

		_, err := docService.CreateDocument(ctx, opts)
		if err != nil {
			b.Fatal(err)
		}
	}

	// 准备语义搜索查询
	queries := []string{
		"传统中医理论的核心观点",
		"艾灸有什么治疗作用",
		"经络和现代医学的关系",
		"针灸能治疗哪些疾病",
		"中药分类方法",
	}

	b.ResetTimer()

	// 执行基准测试
	for i := 0; i < b.N; i++ {
		query := queries[i%len(queries)]
		// 使用正确的SemanticSearch方法签名
		results, err := docService.SemanticSearch(ctx, query, 3)
		if err != nil {
			b.Fatal(err)
		}

		// 验证结果不为空
		assert.NotEmpty(b, results)
	}
}

// 生成指定长度的中文测试文本
func generateLongChineseText(length int) string {
	// 一些中医相关的中文短语，作为随机文本的基础
	phrases := []string{
		"中医学强调整体观念，认为人体是一个有机的整体，",
		"阴阳五行学说是中医理论的基础，阴阳相互对立又相互依存，",
		"气血津液是人体重要的物质基础，气为血之帅，血为气之母，",
		"经络是运行气血的通道，连接脏腑肢节，沟通内外，",
		"脏腑是中医解释人体生理病理的重要概念，包括五脏六腑，",
		"中药材的四气五味反映了药物的性能和作用特点，",
		"针灸治疗基于经络理论，通过刺激特定穴位调节人体功能，",
		"中医诊断依据四诊法：望闻问切，全面收集患者信息，",
		"治未病是中医防治疾病的重要理念，预防重于治疗，",
		"中医养生讲究顺应自然，调和阴阳，平衡五脏，",
	}

	// 初始化随机数生成器
	rand.Seed(time.Now().UnixNano())

	// 构建足够长度的文本
	var builder strings.Builder
	for builder.Len() < length {
		// 随机选择一个短语
		phrase := phrases[rand.Intn(len(phrases))]
		builder.WriteString(phrase)
	}

	// 如果生成的文本超过指定长度，截断到指定长度
	result := builder.String()
	if len(result) > length {
		result = result[:length]
	}

	return result
}

// 批量文档创建基准测试
func BenchmarkBatchDocumentCreation(b *testing.B) {
	ctx := context.Background()

	// 创建文档服务
	docService, teardown, _ := setupSemanticSearchTestEnv(ctx)
	defer teardown()

	// 准备不同长度的文档内容进行测试
	shortContent := "这是一个短文档，用于测试文档创建性能。"
	mediumContent := generateLongChineseText(1000) // 1000字的中等长度文档
	longContent := generateLongChineseText(5000)   // 5000字的长文档

	categoryID := uuid.New()
	authorID := uuid.New()

	b.Run("ShortDocument", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			opts := service.DocumentOptions{
				Title:       "短文档测试 " + uuid.New().String(),
				Description: "短文档描述",
				Content:     shortContent,
				ContentType: entity.ContentTypeMarkdown,
				CategoryID:  categoryID,
				AuthorID:    authorID,
				Tags:        []string{"短文档", "测试"},
			}

			_, err := docService.CreateDocument(ctx, opts)
			if err != nil {
				b.Fatal(err)
			}
		}
	})

	b.Run("MediumDocument", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			opts := service.DocumentOptions{
				Title:       "中等长度文档测试 " + uuid.New().String(),
				Description: "中等长度文档描述",
				Content:     mediumContent,
				ContentType: entity.ContentTypeMarkdown,
				CategoryID:  categoryID,
				AuthorID:    authorID,
				Tags:        []string{"中等文档", "测试"},
			}

			_, err := docService.CreateDocument(ctx, opts)
			if err != nil {
				b.Fatal(err)
			}
		}
	})

	b.Run("LongDocument", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			opts := service.DocumentOptions{
				Title:       "长文档测试 " + uuid.New().String(),
				Description: "长文档描述",
				Content:     longContent,
				ContentType: entity.ContentTypeMarkdown,
				CategoryID:  categoryID,
				AuthorID:    authorID,
				Tags:        []string{"长文档", "测试"},
			}

			_, err := docService.CreateDocument(ctx, opts)
			if err != nil {
				b.Fatal(err)
			}
		}
	})
}

// 设置语义搜索测试环境
func setupSemanticSearchTestEnv(ctx context.Context) (*service.DocumentService, func(), error) {
	// 创建mock对象
	repo := &mocks.MockDocumentRepository{}
	// 配置mock方法返回
	repo.On("FindByID", ctx, mock.Anything).Return(&entity.Document{
		ID:          uuid.New(),
		Title:       "中医养生理论概述",
		Content:     "中医养生是中国传统医学的重要组成部分",
		Description: "中医养生知识介绍",
		ContentType: entity.ContentTypeMarkdown,
		Status:      entity.StatusPublished,
		AuthorID:    uuid.New(),
		CategoryID:  uuid.New(),
		Tags:        []string{"中医", "养生"},
	}, nil)

	repo.On("Save", ctx, mock.Anything).Return(nil)
	repo.On("Search", ctx, mock.Anything).Return([]*entity.Document{}, nil)
	repo.On("SemanticSearch", ctx, mock.Anything, mock.Anything).Return([]*entity.Document{
		{
			ID:          uuid.New(),
			Title:       "中医养生理论概述",
			Content:     "中医养生是中国传统医学的重要组成部分",
			Description: "中医养生知识介绍",
			Status:      entity.StatusPublished,
		},
		{
			ID:          uuid.New(),
			Title:       "艾灸疗法的应用与研究",
			Content:     "艾灸是中医传统外治疗法",
			Description: "艾灸治疗方法介绍",
			Status:      entity.StatusPublished,
		},
	}, nil)

	categoryRepo := &mocks.MockCategoryRepository{}
	// 添加一个测试分类
	categoryID := uuid.New()
	categoryRepo.On("FindByID", ctx, mock.Anything).Return(&entity.Category{
		ID:          categoryID,
		Name:        "中医知识库",
		Description: "包含中医理论、经络、穴位、治疗方法等内容",
	}, nil)

	// 配置FindByParent方法
	categoryRepo.On("FindByParent", ctx, mock.Anything).Return([]*entity.Category{}, nil)
	categoryRepo.On("FindByPath", ctx, mock.Anything).Return(&entity.Category{}, nil)

	// 使用已有的文本分割器mock
	textSplitter := &mocks.MockTextSplitter{}
	// 配置Split方法返回
	textSplitter.On("Split", mock.Anything, mock.Anything).Return([]entity.Chunk{
		{
			ID:         uuid.New(),
			DocumentID: uuid.New(),
			Content:    "中医养生是中国传统医学的重要组成部分",
			Metadata:   []entity.MetadataField{{Name: "index", Value: 0}},
			TokenCount: 15,
			Offset:     0,
			Length:     len("中医养生是中国传统医学的重要组成部分"),
		},
	}, nil)

	// 使用已有的嵌入服务mock
	embedService := &mocks.MockEmbeddingService{}
	// 配置GetEmbedding和GetBatchEmbeddings方法返回
	embedService.On("GetEmbedding", ctx, mock.Anything).Return([]float32{0.1, 0.2, 0.3, 0.4, 0.5}, nil)
	embedService.On("GetBatchEmbeddings", ctx, mock.Anything).Return([][]float32{
		{0.1, 0.2, 0.3, 0.4, 0.5},
		{0.5, 0.4, 0.3, 0.2, 0.1},
	}, nil)

	// 创建文档服务
	docService := service.NewDocumentService(repo, categoryRepo, textSplitter, embedService)

	// 清理函数
	cleanup := func() {
		// 清理资源，对于mock对象可以不做任何操作
	}

	return docService, cleanup, nil
}
