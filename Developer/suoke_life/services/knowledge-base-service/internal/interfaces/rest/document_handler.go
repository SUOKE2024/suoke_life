package rest

import (
	"encoding/json"
	"net/http"
	"strconv"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/domain/service"
	"knowledge-base-service/internal/domain/service/interfaces"
	"knowledge-base-service/internal/interfaces/metrics"
	"knowledge-base-service/internal/interfaces/rest/helpers"
	"knowledge-base-service/pkg/errors"
	"knowledge-base-service/pkg/logger"
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
	ID          string                 `json:"id"`
	Title       string                 `json:"title"`
	Description string                 `json:"description"`
	Content     string                 `json:"content"`
	ContentType string                 `json:"content_type"`
	Status      string                 `json:"status"`
	AuthorID    string                 `json:"author_id"`
	CategoryID  string                 `json:"category_id"`
	Tags        []string               `json:"tags"`
	TxHash      string                 `json:"tx_hash,omitempty"`
	Metadata    []entity.MetadataField `json:"metadata,omitempty"`
	CreatedAt   string                 `json:"created_at"`
	UpdatedAt   string                 `json:"updated_at"`
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

// 处理程序方法

// ListDocuments 列出所有文档
func (h *DocumentHandler) ListDocuments(w http.ResponseWriter, r *http.Request) {
	log := logger.FromContext(r.Context())
	// 实际业务中这里应该分页，并支持各种过滤条件
	// 但为简化示例，这里简单地通过标签获取一些文档
	tags := r.URL.Query()["tag"]

	documents, err := h.documentService.GetDocumentsByTags(r.Context(), tags)
	if err != nil {
		log.Errorw("获取文档列表失败", "error", err, "tags", tags)
		helpers.RenderError(w, r, errors.InternalServerError("获取文档列表失败", err))
		return
	}

	// 转换为响应格式
	response := make([]DocumentResponse, len(documents))
	for i, doc := range documents {
		response[i] = mapDocumentToResponse(doc)
	}

	helpers.RenderJSON(w, r, http.StatusOK, response)
}

// GetDocument 获取单个文档
func (h *DocumentHandler) GetDocument(w http.ResponseWriter, r *http.Request) {
	id, err := helpers.ParseUUID(r, "id")
	if err != nil {
		helpers.RenderError(w, r, err)
		return
	}

	document, err := h.documentService.GetDocumentByID(r.Context(), id)
	if err != nil {
		helpers.RenderError(w, r, errors.InternalServerError("获取文档失败", err))
		return
	}

	if document == nil {
		helpers.RenderError(w, r, errors.NotFound("文档", nil))
		return
	}

	helpers.RenderJSON(w, r, http.StatusOK, mapDocumentToResponse(document))
}

// CreateDocument 创建文档
func (h *DocumentHandler) CreateDocument(w http.ResponseWriter, r *http.Request) {
	log := logger.FromContext(r.Context())

	var req CreateDocumentRequest
	if err := helpers.ParseRequestBody(r, &req); err != nil {
		helpers.RenderError(w, r, err)
		return
	}

	// 验证必填字段
	requiredFields := map[string]string{
		"标题":   req.Title,
		"内容":   req.Content,
		"作者ID": req.AuthorID,
		"分类ID": req.CategoryID,
	}
	if err := helpers.ValidateRequired(requiredFields); err != nil {
		helpers.RenderError(w, r, err)
		return
	}

	// 解析UUID
	authorID, err := uuid.Parse(req.AuthorID)
	if err != nil {
		helpers.RenderError(w, r, errors.BadRequest("无效的UUID格式", err))
		return
	}

	categoryID, err := uuid.Parse(req.CategoryID)
	if err != nil {
		helpers.RenderError(w, r, errors.BadRequest("无效的UUID格式", err))
		return
	}

	// 解析内容类型
	contentType := entity.ContentType(req.ContentType)

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

	// 记录指标
	metrics.IncrementDBCounter("document_create", true)

	// 创建文档
	document, err := h.documentService.CreateDocument(r.Context(), opts)
	if err != nil {
		metrics.IncrementDBCounter("document_create", false)
		log.Errorw("创建文档失败", "error", err, "title", req.Title)
		helpers.RenderError(w, r, errors.InternalServerError("创建文档失败", err))
		return
	}

	log.Infow("文档创建成功", "document_id", document.ID, "title", document.Title)
	helpers.RenderJSON(w, r, http.StatusCreated, mapDocumentToResponse(document))
}

// UpdateDocument 更新文档
func (h *DocumentHandler) UpdateDocument(w http.ResponseWriter, r *http.Request) {
	log := logger.FromContext(r.Context())

	// 解析文档ID
	id, err := helpers.ParseUUID(r, "id")
	if err != nil {
		helpers.RenderError(w, r, err)
		return
	}

	// 解析请求体
	var req UpdateDocumentRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		helpers.RenderError(w, r, errors.BadRequest("无效的请求体", err))
		return
	}

	// 验证必填字段
	if req.Title == "" {
		helpers.RenderError(w, r, errors.BadRequest("标题不能为空", nil))
		return
	}

	// 解析分类ID，如果提供了的话
	var categoryID uuid.UUID
	if req.CategoryID != "" {
		categoryID, err = uuid.Parse(req.CategoryID)
		if err != nil {
			helpers.RenderError(w, r, errors.BadRequest("无效的分类ID", err))
			return
		}
	}

	// 解析内容类型
	contentType := entity.ContentType(req.ContentType)

	// 记录指标
	metrics.IncrementDBCounter("document_update", true)

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
		metrics.IncrementDBCounter("document_update", false)
		log.Errorw("更新文档失败", "error", err, "document_id", id)
		helpers.RenderError(w, r, errors.InternalServerError("更新文档失败", err))
		return
	}

	if document == nil {
		helpers.RenderError(w, r, errors.NotFound("文档", nil))
		return
	}

	log.Infow("文档更新成功", "document_id", document.ID)
	helpers.RenderJSON(w, r, http.StatusOK, mapDocumentToResponse(document))
}

// DeleteDocument 删除文档
func (h *DocumentHandler) DeleteDocument(w http.ResponseWriter, r *http.Request) {
	log := logger.FromContext(r.Context())

	id, err := helpers.ParseUUID(r, "id")
	if err != nil {
		helpers.RenderError(w, r, err)
		return
	}

	// 记录指标
	metrics.IncrementDBCounter("document_delete", true)

	err = h.documentService.DeleteDocument(r.Context(), id)
	if err != nil {
		metrics.IncrementDBCounter("document_delete", false)
		log.Errorw("删除文档失败", "error", err, "document_id", id)
		helpers.RenderError(w, r, errors.InternalServerError("删除文档失败", err))
		return
	}

	log.Infow("文档删除成功", "document_id", id)
	w.WriteHeader(http.StatusNoContent)
}

// PublishDocument 发布文档
func (h *DocumentHandler) PublishDocument(w http.ResponseWriter, r *http.Request) {
	log := logger.FromContext(r.Context())

	id, err := helpers.ParseUUID(r, "id")
	if err != nil {
		helpers.RenderError(w, r, err)
		return
	}

	err = h.documentService.PublishDocument(r.Context(), id)
	if err != nil {
		log.Errorw("发布文档失败", "error", err, "document_id", id)
		helpers.RenderError(w, r, errors.InternalServerError("发布文档失败", err))
		return
	}

	// 获取最新的文档信息
	document, err := h.documentService.GetDocumentByID(r.Context(), id)
	if err != nil {
		log.Errorw("获取已发布文档失败", "error", err, "document_id", id)
		helpers.RenderError(w, r, errors.InternalServerError("获取已发布文档失败", err))
		return
	}

	log.Infow("文档发布成功", "document_id", id)
	helpers.RenderJSON(w, r, http.StatusOK, mapDocumentToResponse(document))
}

// ArchiveDocument 归档文档
func (h *DocumentHandler) ArchiveDocument(w http.ResponseWriter, r *http.Request) {
	log := logger.FromContext(r.Context())

	id, err := helpers.ParseUUID(r, "id")
	if err != nil {
		helpers.RenderError(w, r, err)
		return
	}

	err = h.documentService.ArchiveDocument(r.Context(), id)
	if err != nil {
		log.Errorw("归档文档失败", "error", err, "document_id", id)
		helpers.RenderError(w, r, errors.InternalServerError("归档文档失败", err))
		return
	}

	log.Infow("文档归档成功", "document_id", id)
	helpers.RenderSuccess(w, r, http.StatusOK, "文档归档成功", map[string]string{
		"id": id.String(),
	})
}

// RegisterOnBlockchain 在区块链上注册文档
func (h *DocumentHandler) RegisterOnBlockchain(w http.ResponseWriter, r *http.Request) {
	log := logger.FromContext(r.Context())

	id, err := helpers.ParseUUID(r, "id")
	if err != nil {
		helpers.RenderError(w, r, err)
		return
	}

	txHash, err := h.documentService.RegisterDocumentOnBlockchain(r.Context(), id)
	if err != nil {
		log.Errorw("在区块链上注册文档失败", "error", err, "document_id", id)
		helpers.RenderError(w, r, errors.InternalServerError("在区块链上注册文档失败", err))
		return
	}

	log.Infow("文档在区块链上注册成功", "document_id", id, "tx_hash", txHash)
	helpers.RenderJSON(w, r, http.StatusOK, map[string]interface{}{
		"id":      id.String(),
		"tx_hash": txHash,
		"message": "文档已在区块链上注册成功",
	})
}

// GetDocumentsByCategory 获取分类下的文档
func (h *DocumentHandler) GetDocumentsByCategory(w http.ResponseWriter, r *http.Request) {
	categoryID, err := helpers.ParseUUID(r, "categoryId")
	if err != nil {
		helpers.RenderError(w, r, err)
		return
	}

	documents, err := h.documentService.GetDocumentsByCategory(r.Context(), categoryID)
	if err != nil {
		helpers.RenderError(w, r, errors.InternalServerError("获取分类文档列表失败", err))
		return
	}

	// 转换为响应格式
	response := make([]DocumentResponse, len(documents))
	for i, doc := range documents {
		response[i] = mapDocumentToResponse(doc)
	}

	helpers.RenderJSON(w, r, http.StatusOK, response)
}

// SearchDocuments 全文搜索文档
func (h *DocumentHandler) SearchDocuments(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")

	if query == "" {
		helpers.RenderError(w, r, errors.BadRequest("搜索查询不能为空", nil))
		return
	}

	documents, err := h.documentService.SearchDocuments(r.Context(), query)
	if err != nil {
		helpers.RenderError(w, r, errors.InternalServerError("搜索文档失败", err))
		return
	}

	// 转换为响应格式
	response := make([]DocumentResponse, len(documents))
	for i, doc := range documents {
		response[i] = mapDocumentToResponse(doc)
	}

	helpers.RenderJSON(w, r, http.StatusOK, response)
}

// SemanticSearch 语义搜索
func (h *DocumentHandler) SemanticSearch(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")

	if query == "" {
		helpers.RenderError(w, r, errors.BadRequest("搜索查询不能为空", nil))
		return
	}

	// 获取limit参数，默认为10
	limitStr := r.URL.Query().Get("limit")
	limit := 10
	if limitStr != "" {
		var err error
		limit, err = strconv.Atoi(limitStr)
		if err != nil || limit <= 0 {
			helpers.RenderError(w, r, errors.BadRequest("无效的limit参数", err))
			return
		}
	}

	// 记录指标
	metrics.IncrementVectorSearchCounter(true)

	documents, err := h.documentService.SemanticSearch(r.Context(), query, limit)
	if err != nil {
		metrics.IncrementVectorSearchCounter(false)
		helpers.RenderError(w, r, errors.InternalServerError("语义搜索失败", err))
		return
	}

	// 转换为响应格式
	response := make([]DocumentResponse, len(documents))
	for i, doc := range documents {
		response[i] = mapDocumentToResponse(doc)
	}

	helpers.RenderJSON(w, r, http.StatusOK, response)
}

// mapDocumentToResponse 将领域实体映射为响应格式
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
