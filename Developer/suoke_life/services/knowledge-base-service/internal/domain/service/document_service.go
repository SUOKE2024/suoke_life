package service

import (
    "context"
    "fmt"
    "time"
    
    "github.com/google/uuid"
    
    "knowledge-base-service/internal/domain/entity"
    "knowledge-base-service/internal/domain/repository"
    "knowledge-base-service/internal/interfaces/ai"
)

// DocumentOptions 文档选项
type DocumentOptions struct {
    Title       string
    Content     string
    Description string
    ContentType entity.ContentType
    AuthorID    uuid.UUID
    CategoryID  uuid.UUID
    Tags        []string
    Metadata    []entity.MetadataField
}

// DocumentService 文档服务
type DocumentService struct {
    documentRepo    repository.DocumentRepository
    categoryRepo    repository.CategoryRepository
    textSplitter    ai.TextSplitter
    embeddingService ai.EmbeddingService
}

// NewDocumentService 创建文档服务
func NewDocumentService(
    documentRepo repository.DocumentRepository,
    categoryRepo repository.CategoryRepository,
    textSplitter ai.TextSplitter,
    embeddingService ai.EmbeddingService,
) *DocumentService {
    return &DocumentService{
        documentRepo:    documentRepo,
        categoryRepo:    categoryRepo,
        textSplitter:    textSplitter,
        embeddingService: embeddingService,
    }
}

// GetDocumentByID 通过ID获取文档
func (s *DocumentService) GetDocumentByID(ctx context.Context, id uuid.UUID) (*entity.Document, error) {
    return s.documentRepo.FindByID(ctx, id)
}

// GetDocumentsByCategory 获取分类下的所有文档
func (s *DocumentService) GetDocumentsByCategory(ctx context.Context, categoryID uuid.UUID) ([]*entity.Document, error) {
    return s.documentRepo.FindByCategory(ctx, categoryID)
}

// GetDocumentsByTags 通过标签获取文档
func (s *DocumentService) GetDocumentsByTags(ctx context.Context, tags []string) ([]*entity.Document, error) {
    return s.documentRepo.FindByTags(ctx, tags)
}

// SearchDocuments 搜索文档
func (s *DocumentService) SearchDocuments(ctx context.Context, query string) ([]*entity.Document, error) {
    return s.documentRepo.Search(ctx, query)
}

// SemanticSearch 语义搜索文档
func (s *DocumentService) SemanticSearch(ctx context.Context, query string, limit int) ([]*entity.Document, error) {
    if limit <= 0 {
        limit = 10 // 默认限制10条
    }
    return s.documentRepo.SemanticSearch(ctx, query, limit)
}

// CreateDocument 创建文档
func (s *DocumentService) CreateDocument(ctx context.Context, opts DocumentOptions) (*entity.Document, error) {
    // 验证必填项
    if opts.Title == "" {
        return nil, fmt.Errorf("title is required")
    }
    if opts.Content == "" {
        return nil, fmt.Errorf("content is required")
    }
    if opts.AuthorID == uuid.Nil {
        return nil, fmt.Errorf("author ID is required")
    }
    if opts.CategoryID == uuid.Nil {
        return nil, fmt.Errorf("category ID is required")
    }

    // 验证分类ID是否存在
    category, err := s.categoryRepo.FindByID(ctx, opts.CategoryID)
    if err != nil {
        return nil, fmt.Errorf("failed to get category: %w", err)
    }
    
    if category == nil {
        return nil, fmt.Errorf("category not found: %s", opts.CategoryID)
    }
    
    // 创建文档实体
    doc, err := entity.NewDocument(opts.Title, opts.Content, opts.ContentType, opts.AuthorID, opts.CategoryID)
    if err != nil {
        return nil, err
    }
    
    // 设置描述
    if opts.Description != "" {
        doc.Description = opts.Description
    }
    
    // 添加标签
    for _, tag := range opts.Tags {
        doc.AddTag(tag)
    }
    
    // 添加元数据
    for _, meta := range opts.Metadata {
        doc.AddMetadata(meta.Name, meta.Value)
    }
    
    // 处理文档分块
    err = s.processDocumentChunks(ctx, doc)
    if err != nil {
        return nil, err
    }
    
    // 保存文档
    err = s.documentRepo.Save(ctx, doc)
    if err != nil {
        return nil, fmt.Errorf("failed to save document: %w", err)
    }
    
    return doc, nil
}

// UpdateDocument 更新文档
func (s *DocumentService) UpdateDocument(
    ctx context.Context,
    id uuid.UUID,
    title, content, description string,
    contentType entity.ContentType,
    categoryID uuid.UUID,
    tags []string,
) (*entity.Document, error) {
    // 获取现有文档
    doc, err := s.documentRepo.FindByID(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("获取文档失败: %w", err)
    }
    
    if doc == nil {
        return nil, fmt.Errorf("文档不存在: %s", id)
    }
    
    // 验证分类ID是否存在
    if categoryID != doc.CategoryID {
        category, err := s.categoryRepo.FindByID(ctx, categoryID)
        if err != nil {
            return nil, fmt.Errorf("获取分类失败: %w", err)
        }
        
        if category == nil {
            return nil, fmt.Errorf("分类不存在: %s", categoryID)
        }
        
        doc.CategoryID = categoryID
    }
    
    // 更新文档信息
    if title != "" && title != doc.Title {
        doc.Title = title
    }
    
    if description != "" && description != doc.Description {
        doc.Description = description
    }
    
    if content != "" && content != doc.Content {
        doc.Content = content
        doc.Chunks = nil // 内容改变，清空现有块
    }
    
    if contentType != "" && contentType != doc.ContentType {
        doc.ContentType = contentType
    }
    
    // 更新标签
    if len(tags) > 0 {
        doc.Tags = tags
    }
    
    // 设置更新时间
    doc.UpdatedAt = time.Now()
    
    // 处理文档分块（仅在内容变更时）
    if doc.Chunks == nil {
        err = s.processDocumentChunks(ctx, doc)
        if err != nil {
            return nil, err
        }
    }
    
    // 保存文档
    err = s.documentRepo.Update(ctx, doc)
    if err != nil {
        return nil, fmt.Errorf("更新文档失败: %w", err)
    }
    
    return doc, nil
}

// PublishDocument 发布文档
func (s *DocumentService) PublishDocument(ctx context.Context, id uuid.UUID) error {
    doc, err := s.documentRepo.FindByID(ctx, id)
    if err != nil {
        return fmt.Errorf("获取文档失败: %w", err)
    }
    
    if doc == nil {
        return fmt.Errorf("文档不存在: %s", id)
    }
    
    // 发布文档
    doc.Publish()
    
    // 保存文档
    err = s.documentRepo.Update(ctx, doc)
    if err != nil {
        return fmt.Errorf("更新文档状态失败: %w", err)
    }
    
    return nil
}

// ArchiveDocument 归档文档
func (s *DocumentService) ArchiveDocument(ctx context.Context, id uuid.UUID) error {
    doc, err := s.documentRepo.FindByID(ctx, id)
    if err != nil {
        return fmt.Errorf("获取文档失败: %w", err)
    }
    
    if doc == nil {
        return fmt.Errorf("文档不存在: %s", id)
    }
    
    // 归档文档
    doc.Archive()
    
    // 保存文档
    err = s.documentRepo.Update(ctx, doc)
    if err != nil {
        return fmt.Errorf("更新文档状态失败: %w", err)
    }
    
    return nil
}

// DeleteDocument 删除文档
func (s *DocumentService) DeleteDocument(ctx context.Context, id uuid.UUID) error {
    // 验证文档是否存在
    doc, err := s.documentRepo.FindByID(ctx, id)
    if err != nil {
        return fmt.Errorf("获取文档失败: %w", err)
    }
    
    if doc == nil {
        return fmt.Errorf("文档不存在: %s", id)
    }
    
    // 删除文档
    return s.documentRepo.Delete(ctx, id)
}

// RegisterDocumentOnBlockchain 在区块链上注册文档
func (s *DocumentService) RegisterDocumentOnBlockchain(ctx context.Context, id uuid.UUID) (string, error) {
    // 获取文档
    doc, err := s.documentRepo.FindByID(ctx, id)
    if err != nil {
        return "", fmt.Errorf("获取文档失败: %w", err)
    }
    
    if doc == nil {
        return "", fmt.Errorf("文档不存在: %s", id)
    }
    
    // 检查文档状态
    if doc.Status != entity.StatusPublished {
        return "", fmt.Errorf("只有已发布的文档才能在区块链上注册")
    }
    
    // 调用存储库方法注册
    return s.documentRepo.RegisterOnBlockchain(ctx, doc)
}

// 处理文档分块和向量化
func (s *DocumentService) processDocumentChunks(ctx context.Context, doc *entity.Document) error {
    // 如果已有块，则跳过处理
    if len(doc.Chunks) > 0 {
        return nil
    }
    
    // 将文档转换为元数据映射
    metadata := make(map[string]interface{})
    metadata["document_id"] = doc.ID.String()
    metadata["title"] = doc.Title
    
    for _, m := range doc.Metadata {
        metadata[m.Name] = m.Value
    }
    
    // 使用文本分割器分割文档
    chunks, err := s.textSplitter.Split(doc.Content, metadata)
    if err != nil {
        return fmt.Errorf("文档分块失败: %w", err)
    }
    
    // 没有块则直接返回
    if len(chunks) == 0 {
        return nil
    }
    
    // 提取块文本用于向量化
    texts := make([]string, len(chunks))
    for i, chunk := range chunks {
        texts[i] = chunk.Content
    }
    
    // 获取块的向量表示
    vectors, err := s.embeddingService.GetBatchEmbeddings(ctx, texts)
    if err != nil {
        return fmt.Errorf("获取文本向量失败: %w", err)
    }
    
    // 将块添加到文档
    for i, chunk := range chunks {
        // 添加块到文档
        chunkEntity := doc.AddChunk(
            chunk.Content,
            chunk.Offset,
            chunk.Length,
            chunk.TokenCount,
            chunk.Metadata,
        )
        
        // 设置向量（将在数据库中存储）
        if i < len(vectors) {
            _ = doc.UpdateChunkVector(chunkEntity.ID, vectors[i], "")
        }
    }
    
    return nil
}