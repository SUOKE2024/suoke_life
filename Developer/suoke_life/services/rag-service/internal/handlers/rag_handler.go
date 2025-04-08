package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/rag"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/logger"
)

// DefaultRAGHandler 默认RAG处理器
type DefaultRAGHandler struct {
	service     rag.RAGService
	metrics     MetricsHandler
}

// NewRAGHandler 创建新的RAG处理器
func NewRAGHandler(service rag.RAGService, metrics MetricsHandler) RAGHandler {
	return &DefaultRAGHandler{
		service: service,
		metrics: metrics,
	}
}

// Register 注册路由
func (h *DefaultRAGHandler) Register(router interface{}) {
	r, ok := router.(*chi.Mux)
	if !ok {
		panic("router不是chi.Mux类型")
	}

	// 注册路由
	r.Group(func(r chi.Router) {
		r.Post("/api/v1/rag/query", h.QueryHandler)
		r.Post("/api/v1/rag/stream", h.StreamQueryHandler)
		r.Post("/api/v1/rag/documents", h.UploadDocumentHandler)
		r.Delete("/api/v1/rag/documents/{collection}/{id}", h.DeleteDocumentHandler)
		r.Get("/api/v1/rag/documents/{collection}/{id}", h.GetDocumentHandler)
		r.Post("/api/v1/rag/collections", h.CreateCollectionHandler)
		r.Delete("/api/v1/rag/collections/{name}", h.DeleteCollectionHandler)
		r.Get("/api/v1/rag/collections", h.ListCollectionsHandler)
		r.Get("/api/v1/rag/collections/{name}", h.GetCollectionHandler)
		r.Post("/api/v1/rag/search", h.SearchHandler)
		r.Get("/api/v1/rag/health", h.HealthCheckHandler)
	})
}

// QueryHandler 查询处理
func (h *DefaultRAGHandler) QueryHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 解析请求
	var request models.QueryRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		respondWithError(w, http.StatusBadRequest, "无效的请求参数", err)
		return
	}
	
	// 设置上下文
	ctx := r.Context()
	
	// 调用服务
	result, err := h.service.Query(ctx, request)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "查询处理失败", err)
		return
	}
	
	// 记录指标
	h.metrics.RecordRequestDuration("rag", "query", time.Since(start).Seconds())
	
	// 响应结果
	respondWithJSON(w, http.StatusOK, result)
}

// StreamQueryHandler 流式查询处理
func (h *DefaultRAGHandler) StreamQueryHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 解析请求
	var request models.QueryRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		respondWithError(w, http.StatusBadRequest, "无效的请求参数", err)
		return
	}
	
	// 设置请求为流式
	request.Stream = true
	
	// 设置响应头
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	
	// 创建数据刷新的写入器
	flusher, ok := w.(http.Flusher)
	if !ok {
		respondWithError(w, http.StatusInternalServerError, "不支持流式响应", nil)
		return
	}
	
	// 设置上下文
	ctx := r.Context()
	
	// 调用服务的流式查询方法
	err := h.service.StreamQuery(ctx, request, w)
	if err != nil {
		// 在流式响应中发送错误消息
		errorMsg := models.StreamMessage{
			Event: "error",
			Error: err.Error(),
		}
		if data, err := json.Marshal(errorMsg); err == nil {
			w.Write(data)
			w.Write([]byte("\n"))
			flusher.Flush()
		}
	}
	
	// 记录指标
	h.metrics.RecordRequestDuration("rag", "stream_query", time.Since(start).Seconds())
}

// UploadDocumentHandler 上传文档处理
func (h *DefaultRAGHandler) UploadDocumentHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 解析请求
	var request models.DocumentUploadRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		respondWithError(w, http.StatusBadRequest, "无效的请求参数", err)
		return
	}
	
	// 设置上下文
	ctx := r.Context()
	
	// 调用服务
	response, err := h.service.UploadDocument(ctx, request)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "上传文档失败", err)
		return
	}
	
	// 记录指标
	h.metrics.RecordRequestDuration("rag", "upload_document", time.Since(start).Seconds())
	
	// 响应结果
	respondWithJSON(w, http.StatusOK, response)
}

// DeleteDocumentHandler 删除文档
func (h *DefaultRAGHandler) DeleteDocumentHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 从URL获取参数
	collection := chi.URLParam(r, "collection")
	documentID := chi.URLParam(r, "id")
	
	// 设置上下文
	ctx := r.Context()
	
	// 调用服务
	err := h.service.DeleteDocument(ctx, collection, documentID)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "删除文档失败", err)
		return
	}
	
	// 记录指标
	h.metrics.RecordRequestDuration("rag", "delete_document", time.Since(start).Seconds())
	
	// 响应结果
	respondWithJSON(w, http.StatusOK, map[string]interface{}{
		"success": true,
		"message": "文档删除成功",
	})
}

// GetDocumentHandler 获取文档
func (h *DefaultRAGHandler) GetDocumentHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 从URL获取参数
	collection := chi.URLParam(r, "collection")
	documentID := chi.URLParam(r, "id")
	
	// 设置上下文
	ctx := r.Context()
	
	// 调用服务
	document, err := h.service.GetDocument(ctx, collection, documentID)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "获取文档失败", err)
		return
	}
	
	// 记录指标
	h.metrics.RecordRequestDuration("rag", "get_document", time.Since(start).Seconds())
	
	// 响应结果
	respondWithJSON(w, http.StatusOK, document)
}

// CreateCollectionHandler 创建集合
func (h *DefaultRAGHandler) CreateCollectionHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 解析请求
	var request models.CollectionCreateRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		respondWithError(w, http.StatusBadRequest, "无效的请求参数", err)
		return
	}
	
	// 设置上下文
	ctx := r.Context()
	
	// 调用服务
	collection, err := h.service.CreateCollection(ctx, request)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "创建集合失败", err)
		return
	}
	
	// 记录指标
	h.metrics.RecordRequestDuration("rag", "create_collection", time.Since(start).Seconds())
	
	// 响应结果
	respondWithJSON(w, http.StatusCreated, collection)
}

// DeleteCollectionHandler 删除集合
func (h *DefaultRAGHandler) DeleteCollectionHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 从URL获取参数
	name := chi.URLParam(r, "name")
	
	// 设置上下文
	ctx := r.Context()
	
	// 调用服务
	err := h.service.DeleteCollection(ctx, name)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "删除集合失败", err)
		return
	}
	
	// 记录指标
	h.metrics.RecordRequestDuration("rag", "delete_collection", time.Since(start).Seconds())
	
	// 响应结果
	respondWithJSON(w, http.StatusOK, map[string]interface{}{
		"success": true,
		"message": "集合删除成功",
	})
}

// ListCollectionsHandler 列出集合
func (h *DefaultRAGHandler) ListCollectionsHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 设置上下文
	ctx := r.Context()
	
	// 调用服务
	collections, err := h.service.ListCollections(ctx)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "获取集合列表失败", err)
		return
	}
	
	// 记录指标
	h.metrics.RecordRequestDuration("rag", "list_collections", time.Since(start).Seconds())
	
	// 响应结果
	respondWithJSON(w, http.StatusOK, collections)
}

// GetCollectionHandler 获取集合信息
func (h *DefaultRAGHandler) GetCollectionHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 从URL获取参数
	name := chi.URLParam(r, "name")
	
	// 设置上下文
	ctx := r.Context()
	
	// 调用服务
	collection, err := h.service.GetCollection(ctx, name)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "获取集合信息失败", err)
		return
	}
	
	// 记录指标
	h.metrics.RecordRequestDuration("rag", "get_collection", time.Since(start).Seconds())
	
	// 响应结果
	respondWithJSON(w, http.StatusOK, collection)
}

// SearchHandler 搜索处理
func (h *DefaultRAGHandler) SearchHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 解析请求
	var request models.DocumentSearchRequest
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		respondWithError(w, http.StatusBadRequest, "无效的请求参数", err)
		return
	}
	
	// 设置上下文
	ctx := r.Context()
	
	// 调用服务
	docs, err := h.service.Search(ctx, request.CollectionName, request.Query, request.TopK, request.Filter)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "搜索失败", err)
		return
	}
	
	// 构建响应
	response := models.DocumentSearchResponse{
		Results:        make([]models.SearchResult, 0, len(docs)),
		CollectionName: request.CollectionName,
		TotalMatches:   len(docs),
	}
	
	// 构建搜索结果
	for _, doc := range docs {
		result := models.SearchResult{
			Document: doc,
			Score:    float32(doc.Score),
		}
		response.Results = append(response.Results, result)
	}
	
	// 记录指标
	h.metrics.RecordRequestDuration("rag", "search", time.Since(start).Seconds())
	
	// 响应结果
	respondWithJSON(w, http.StatusOK, response)
}

// HealthCheckHandler 健康检查
func (h *DefaultRAGHandler) HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	
	// 设置上下文
	ctx := r.Context()
	
	// 调用服务
	err := h.service.HealthCheck(ctx)
	if err != nil {
		respondWithError(w, http.StatusServiceUnavailable, "健康检查失败", err)
		return
	}
	
	// 记录指标
	h.metrics.RecordRequestDuration("rag", "health_check", time.Since(start).Seconds())
	
	// 响应结果
	respondWithJSON(w, http.StatusOK, map[string]interface{}{
		"status":   "healthy",
		"version":  "1.0",
		"timestamp": time.Now(),
	})
}

// respondWithJSON 以JSON格式响应
func respondWithJSON(w http.ResponseWriter, code int, payload interface{}) {
	response, _ := json.Marshal(payload)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	w.Write(response)
}

// respondWithError 响应错误信息
func respondWithError(w http.ResponseWriter, code int, message string, err error) {
	errorMessage := message
	if err != nil {
		errorMessage = fmt.Sprintf("%s: %v", message, err)
	}
	
	response := models.ErrorResponse{
		Error:   message,
		Code:    code,
		Message: errorMessage,
	}
	
	respondWithJSON(w, code, response)
} 