package rest

import (
    "encoding/json"
    "fmt"
    "net/http"
    "time"
    
    "github.com/go-chi/chi/v5"
    "github.com/go-chi/render"
    "github.com/google/uuid"
    
    "knowledge-base-service/internal/domain/entity"
    "knowledge-base-service/internal/domain/service"
    "knowledge-base-service/internal/domain/service/interfaces"
)

// DocumentHandler 处理文档相关的API请求
type DocumentHandler struct {
    documentService interfaces.DocumentService
}

// NewDocumentHandler 创建文档处理器
func NewDocumentHandler(documentService interfaces.DocumentService) *DocumentHandler {
    return &DocumentHandler{
        documentService: documentService,
    }
}

// RegisterRoutes 注册路由
func (h *DocumentHandler) RegisterRoutes(r chi.Router) {
    r.Route("/documents", func(r chi.Router) {
        r.Get("/", h.ListDocuments)
        r.Post("/", h.CreateDocument)
        r.Get("/{id}", h.GetDocument)
        r.Put("/{id}", h.UpdateDocument)
        r.Delete("/{id}", h.DeleteDocument)
        r.Post("/{id}/publish", h.PublishDocument)
        r.Post("/{id}/archive", h.ArchiveDocument)
        r.Post("/{id}/blockchain", h.RegisterOnBlockchain)
        r.Get("/category/{categoryId}", h.GetDocumentsByCategory)
        r.Get("/search", h.SearchDocuments)
        r.Get("/semantic-search", h.SemanticSearch)
    })
}

// 请求和响应结构体

// DocumentResponse 文档响应
type DocumentResponse struct {
    ID          string              `json:"id"`
    Title       string              `json:"title"`
    Description string              `json:"description"`
    Content     string              `json:"content"`
    ContentType string              `json:"content_type"`
    Status      string              `json:"status"`
    AuthorID    string              `json:"author_id"`
    CategoryID  string              `json:"category_id"`
    Tags        []string            `json:"tags"`
    TxHash      string              `json:"tx_hash,omitempty"`
    Metadata    []entity.MetadataField `json:"metadata,omitempty"`
    CreatedAt   string              `json:"created_at"`
    UpdatedAt   string              `json:"updated_at"`
}

// CreateDocumentRequest 创建文档请求
type CreateDocumentRequest struct {
    Title       string   `json:"title"`
    Description string   `json:"description"`
    Content     string   `json:"content"`
    ContentType string   `json:"content_type"`
    AuthorID    string   `json:"author_id"`
    CategoryID  string   `json:"category_id"`
    Tags        []string `json:"tags"`
}

// UpdateDocumentRequest 更新文档请求
type UpdateDocumentRequest struct {
    Title       string   `json:"title"`
    Description string   `json:"description"`
    Content     string   `json:"content"`
    ContentType string   `json:"content_type"`
    CategoryID  string   `json:"category_id"`
    Tags        []string `json:"tags"`
}

// ErrorResponse 错误响应
type ErrorResponse struct {
    Error string `json:"error"`
}

// 处理程序方法

// ListDocuments 列出所有文档
func (h *DocumentHandler) ListDocuments(w http.ResponseWriter, r *http.Request) {
    // 实际业务中这里应该分页，并支持各种过滤条件
    // 但为简化示例，这里简单地通过标签获取一些文档
    tags := r.URL.Query()["tag"]
    
    documents, err := h.documentService.GetDocumentsByTags(r.Context(), tags)
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "获取文档列表失败: " + err.Error()})
        return
    }
    
    // 转换为响应格式
    response := make([]DocumentResponse, len(documents))
    for i, doc := range documents {
        response[i] = mapDocumentToResponse(doc)
    }
    
    render.JSON(w, r, response)
}

// GetDocument 获取单个文档
func (h *DocumentHandler) GetDocument(w http.ResponseWriter, r *http.Request) {
    idStr := chi.URLParam(r, "id")
    id, err := uuid.Parse(idStr)
    if err != nil {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "无效的文档ID格式"})
        return
    }
    
    document, err := h.documentService.GetDocumentByID(r.Context(), id)
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "获取文档失败: " + err.Error()})
        return
    }
    
    if document == nil {
        render.Status(r, http.StatusNotFound)
        render.JSON(w, r, ErrorResponse{Error: "文档不存在"})
        return
    }
    
    render.JSON(w, r, mapDocumentToResponse(document))
}

// CreateDocument 创建文档
func (h *DocumentHandler) CreateDocument(w http.ResponseWriter, r *http.Request) {
    var req CreateDocumentRequest
    err := json.NewDecoder(r.Body).Decode(&req)
    if err != nil {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "解析请求失败: " + err.Error()})
        return
    }
    
    // 验证必填字段
    if req.Title == "" || req.Content == "" || req.AuthorID == "" || req.CategoryID == "" {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "标题、内容、作者ID和分类ID为必填项"})
        return
    }
    
    // 解析UUID
    authorID, err := uuid.Parse(req.AuthorID)
    if err != nil {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "无效的作者ID格式"})
        return
    }
    
    categoryID, err := uuid.Parse(req.CategoryID)
    if err != nil {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "无效的分类ID格式"})
        return
    }
    
    // 解析内容类型
    contentType := entity.ContentTypeText
    if req.ContentType != "" {
        contentType = entity.ContentType(req.ContentType)
    }
    
    // 创建文档选项
    opts := service.DocumentOptions{
        Title:       req.Title,
        Content:     req.Content,
        Description: req.Description,
        ContentType: contentType,
        AuthorID:    authorID,
        CategoryID:  categoryID,
        Tags:        req.Tags,
        Metadata:    []entity.MetadataField{}, // 如果API需要支持元数据，这里可以从请求中解析
    }
    
    // 创建文档
    document, err := h.documentService.CreateDocument(r.Context(), opts)
    
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "创建文档失败: " + err.Error()})
        return
    }
    
    render.Status(r, http.StatusCreated)
    render.JSON(w, r, mapDocumentToResponse(document))
}

// UpdateDocument 更新文档
func (h *DocumentHandler) UpdateDocument(w http.ResponseWriter, r *http.Request) {
    idStr := chi.URLParam(r, "id")
    id, err := uuid.Parse(idStr)
    if err != nil {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "无效的文档ID格式"})
        return
    }
    
    var req UpdateDocumentRequest
    err = json.NewDecoder(r.Body).Decode(&req)
    if err != nil {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "解析请求失败: " + err.Error()})
        return
    }
    
    // 确保至少有一项需要更新
    if req.Title == "" && req.Description == "" && req.Content == "" && 
       req.ContentType == "" && req.CategoryID == "" && len(req.Tags) == 0 {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "请提供至少一项需要更新的内容"})
        return
    }
    
    // 解析分类ID（如果提供）
    var categoryID uuid.UUID
    if req.CategoryID != "" {
        categoryID, err = uuid.Parse(req.CategoryID)
        if err != nil {
            render.Status(r, http.StatusBadRequest)
            render.JSON(w, r, ErrorResponse{Error: "无效的分类ID格式"})
            return
        }
    }
    
    // 解析内容类型
    contentType := entity.ContentType(req.ContentType)
    
    // 更新文档
    document, err := h.documentService.UpdateDocument(
        r.Context(),
        id,
        req.Title,
        req.Content,
        req.Description,
        contentType,
        categoryID,
        req.Tags,
    )
    
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "更新文档失败: " + err.Error()})
        return
    }
    
    render.JSON(w, r, mapDocumentToResponse(document))
}

// DeleteDocument 删除文档
func (h *DocumentHandler) DeleteDocument(w http.ResponseWriter, r *http.Request) {
    idStr := chi.URLParam(r, "id")
    id, err := uuid.Parse(idStr)
    if err != nil {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "无效的文档ID格式"})
        return
    }
    
    err = h.documentService.DeleteDocument(r.Context(), id)
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "删除文档失败: " + err.Error()})
        return
    }
    
    w.WriteHeader(http.StatusNoContent)
}

// PublishDocument 发布文档
func (h *DocumentHandler) PublishDocument(w http.ResponseWriter, r *http.Request) {
    idStr := chi.URLParam(r, "id")
    id, err := uuid.Parse(idStr)
    if err != nil {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "无效的文档ID格式"})
        return
    }
    
    err = h.documentService.PublishDocument(r.Context(), id)
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "发布文档失败: " + err.Error()})
        return
    }
    
    // 返回更新后的文档
    document, err := h.documentService.GetDocumentByID(r.Context(), id)
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "获取更新后的文档失败: " + err.Error()})
        return
    }
    
    render.JSON(w, r, mapDocumentToResponse(document))
}

// ArchiveDocument 归档文档
func (h *DocumentHandler) ArchiveDocument(w http.ResponseWriter, r *http.Request) {
    idStr := chi.URLParam(r, "id")
    id, err := uuid.Parse(idStr)
    if err != nil {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "无效的文档ID格式"})
        return
    }
    
    err = h.documentService.ArchiveDocument(r.Context(), id)
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "归档文档失败: " + err.Error()})
        return
    }
    
    // 返回更新后的文档
    document, err := h.documentService.GetDocumentByID(r.Context(), id)
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "获取更新后的文档失败: " + err.Error()})
        return
    }
    
    render.JSON(w, r, mapDocumentToResponse(document))
}

// RegisterOnBlockchain 在区块链上注册文档
func (h *DocumentHandler) RegisterOnBlockchain(w http.ResponseWriter, r *http.Request) {
    idStr := chi.URLParam(r, "id")
    id, err := uuid.Parse(idStr)
    if err != nil {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "无效的文档ID格式"})
        return
    }
    
    txHash, err := h.documentService.RegisterDocumentOnBlockchain(r.Context(), id)
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "区块链注册失败: " + err.Error()})
        return
    }
    
    render.JSON(w, r, map[string]string{
        "tx_hash": txHash,
        "message": "文档已在区块链上注册",
    })
}

// GetDocumentsByCategory 根据分类获取文档
func (h *DocumentHandler) GetDocumentsByCategory(w http.ResponseWriter, r *http.Request) {
    categoryIDStr := chi.URLParam(r, "categoryId")
    categoryID, err := uuid.Parse(categoryIDStr)
    if err != nil {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "无效的分类ID格式"})
        return
    }
    
    documents, err := h.documentService.GetDocumentsByCategory(r.Context(), categoryID)
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "获取分类文档失败: " + err.Error()})
        return
    }
    
    // 转换为响应格式
    response := make([]DocumentResponse, len(documents))
    for i, doc := range documents {
        response[i] = mapDocumentToResponse(doc)
    }
    
    render.JSON(w, r, response)
}

// SearchDocuments 全文搜索文档
func (h *DocumentHandler) SearchDocuments(w http.ResponseWriter, r *http.Request) {
    query := r.URL.Query().Get("q")
    if query == "" {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "搜索查询不能为空"})
        return
    }
    
    documents, err := h.documentService.SearchDocuments(r.Context(), query)
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "搜索文档失败: " + err.Error()})
        return
    }
    
    // 转换为响应格式
    response := make([]DocumentResponse, len(documents))
    for i, doc := range documents {
        response[i] = mapDocumentToResponse(doc)
    }
    
    render.JSON(w, r, response)
}

// SemanticSearch 语义搜索文档
func (h *DocumentHandler) SemanticSearch(w http.ResponseWriter, r *http.Request) {
    query := r.URL.Query().Get("q")
    if query == "" {
        render.Status(r, http.StatusBadRequest)
        render.JSON(w, r, ErrorResponse{Error: "搜索查询不能为空"})
        return
    }
    
    // 解析限制参数
    limitStr := r.URL.Query().Get("limit")
    limit := 10 // 默认限制
    if limitStr != "" {
        var limitVal int
        _, err := fmt.Sscanf(limitStr, "%d", &limitVal)
        if err == nil && limitVal > 0 {
            limit = limitVal
        }
    }
    
    documents, err := h.documentService.SemanticSearch(r.Context(), query, limit)
    if err != nil {
        render.Status(r, http.StatusInternalServerError)
        render.JSON(w, r, ErrorResponse{Error: "语义搜索失败: " + err.Error()})
        return
    }
    
    // 转换为响应格式
    response := make([]DocumentResponse, len(documents))
    for i, doc := range documents {
        response[i] = mapDocumentToResponse(doc)
    }
    
    render.JSON(w, r, response)
}

// 辅助方法

// mapDocumentToResponse 将文档实体映射到响应结构
func mapDocumentToResponse(doc *entity.Document) DocumentResponse {
    return DocumentResponse{
        ID:          doc.ID.String(),
        Title:       doc.Title,
        Description: doc.Description,
        Content:     doc.Content,
        ContentType: string(doc.ContentType),
        Status:      string(doc.Status),
        AuthorID:    doc.AuthorID.String(),
        CategoryID:  doc.CategoryID.String(),
        Tags:        doc.Tags,
        TxHash:      doc.TxHash,
        Metadata:    doc.Metadata,
        CreatedAt:   doc.CreatedAt.Format(time.RFC3339),
        UpdatedAt:   doc.UpdatedAt.Format(time.RFC3339),
    }
}