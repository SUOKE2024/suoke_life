package entity

import (
    "fmt"
    "time"
    
    "github.com/google/uuid"
)

// DocumentStatus 表示文档状态
type DocumentStatus string

const (
    // StatusDraft 草稿状态
    StatusDraft DocumentStatus = "draft"
    
    // StatusPublished 已发布状态
    StatusPublished DocumentStatus = "published"
    
    // StatusArchived 已归档状态
    StatusArchived DocumentStatus = "archived"
    
    // StatusDeleted 已删除状态
    StatusDeleted DocumentStatus = "deleted"
)

// ContentType 文档内容类型
type ContentType string

const (
    // ContentTypeText 纯文本类型
    ContentTypeText ContentType = "text"
    
    // ContentTypeMarkdown Markdown类型
    ContentTypeMarkdown ContentType = "markdown"
    
    // ContentTypeHTML HTML类型
    ContentTypeHTML ContentType = "html"
)

// MetadataField 元数据字段
type MetadataField struct {
    Name  string      `json:"name"`
    Value interface{} `json:"value"`
}

// Chunk 表示文档的一个小块
type Chunk struct {
    ID          uuid.UUID `json:"id"`
    DocumentID  uuid.UUID `json:"document_id"`
    Content     string    `json:"content"`
    Vector      []float32 `json:"vector,omitempty"`
    VectorID    string    `json:"vector_id,omitempty"`
    Metadata    []MetadataField `json:"metadata,omitempty"`
    TokenCount  int       `json:"token_count"`
    Offset      int       `json:"offset"`
    Length      int       `json:"length"`
    CreatedAt   time.Time `json:"created_at"`
}

// Document 表示知识库中的一个文档
type Document struct {
    ID          uuid.UUID      `json:"id"`
    Title       string         `json:"title"`
    Description string         `json:"description"`
    Content     string         `json:"content"`
    ContentType ContentType    `json:"content_type"`
    Status      DocumentStatus `json:"status"`
    AuthorID    uuid.UUID      `json:"author_id"`
    CategoryID  uuid.UUID      `json:"category_id"`
    Tags        []string       `json:"tags"`
    TxHash      string         `json:"tx_hash,omitempty"` // 区块链交易哈希
    Metadata    []MetadataField `json:"metadata,omitempty"`
    Chunks      []Chunk        `json:"chunks,omitempty"`
    CreatedAt   time.Time      `json:"created_at"`
    UpdatedAt   time.Time      `json:"updated_at"`
}

// NewDocument 创建新文档
func NewDocument(title, content string, contentType ContentType, authorID, categoryID uuid.UUID) (*Document, error) {
    if title == "" {
        return nil, fmt.Errorf("文档标题不能为空")
    }
    
    if content == "" {
        return nil, fmt.Errorf("文档内容不能为空")
    }
    
    now := time.Now()
    
    return &Document{
        ID:          uuid.New(),
        Title:       title,
        Content:     content,
        ContentType: contentType,
        Status:      StatusDraft,
        AuthorID:    authorID,
        CategoryID:  categoryID,
        Tags:        []string{},
        Metadata:    []MetadataField{},
        Chunks:      []Chunk{},
        CreatedAt:   now,
        UpdatedAt:   now,
    }, nil
}

// Publish 发布文档
func (d *Document) Publish() {
    d.Status = StatusPublished
    d.UpdatedAt = time.Now()
}

// Archive 归档文档
func (d *Document) Archive() {
    d.Status = StatusArchived
    d.UpdatedAt = time.Now()
}

// Delete 删除文档
func (d *Document) Delete() {
    d.Status = StatusDeleted
    d.UpdatedAt = time.Now()
}

// AddTag 添加标签
func (d *Document) AddTag(tag string) {
    // 检查标签是否已存在
    for _, t := range d.Tags {
        if t == tag {
            return
        }
    }
    
    d.Tags = append(d.Tags, tag)
    d.UpdatedAt = time.Now()
}

// RemoveTag 移除标签
func (d *Document) RemoveTag(tag string) {
    for i, t := range d.Tags {
        if t == tag {
            d.Tags = append(d.Tags[:i], d.Tags[i+1:]...)
            d.UpdatedAt = time.Now()
            return
        }
    }
}

// AddMetadata 添加元数据
func (d *Document) AddMetadata(name string, value interface{}) {
    // 检查是否存在同名元数据
    for i, m := range d.Metadata {
        if m.Name == name {
            d.Metadata[i].Value = value
            d.UpdatedAt = time.Now()
            return
        }
    }
    
    // 不存在则添加
    d.Metadata = append(d.Metadata, MetadataField{
        Name:  name,
        Value: value,
    })
    d.UpdatedAt = time.Now()
}

// GetMetadata 获取元数据
func (d *Document) GetMetadata(name string) (interface{}, bool) {
    for _, m := range d.Metadata {
        if m.Name == name {
            return m.Value, true
        }
    }
    return nil, false
}

// AddChunk 添加文档块
func (d *Document) AddChunk(content string, offset, length, tokenCount int, metadata []MetadataField) *Chunk {
    chunk := Chunk{
        ID:         uuid.New(),
        DocumentID: d.ID,
        Content:    content,
        Metadata:   metadata,
        TokenCount: tokenCount,
        Offset:     offset,
        Length:     length,
        CreatedAt:  time.Now(),
    }
    
    d.Chunks = append(d.Chunks, chunk)
    d.UpdatedAt = time.Now()
    
    return &d.Chunks[len(d.Chunks)-1]
}

// UpdateChunkVector 更新块的向量
func (d *Document) UpdateChunkVector(chunkID uuid.UUID, vector []float32, vectorID string) error {
    for i, chunk := range d.Chunks {
        if chunk.ID == chunkID {
            d.Chunks[i].Vector = vector
            d.Chunks[i].VectorID = vectorID
            d.UpdatedAt = time.Now()
            return nil
        }
    }
    return fmt.Errorf("未找到指定的块 ID: %s", chunkID)
}

// SetBlockchainTxHash 设置区块链交易哈希
func (d *Document) SetBlockchainTxHash(txHash string) {
    d.TxHash = txHash
    d.UpdatedAt = time.Now()
}

// IsRegisteredOnBlockchain 检查是否已在区块链上注册
func (d *Document) IsRegisteredOnBlockchain() bool {
    return d.TxHash != ""
}