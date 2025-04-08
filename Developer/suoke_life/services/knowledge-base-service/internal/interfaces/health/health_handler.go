package health

import (
	"context"
	"encoding/json"
	"net/http"
	"runtime"
	"time"

	"github.com/go-chi/chi/v5"

	"knowledge-base-service/internal/infrastructure/database"
	"knowledge-base-service/internal/infrastructure/vectorstore"
)

// HealthHandler 健康检查处理器
type HealthHandler struct {
	db          *database.PostgresDB
	vectorStore vectorstore.VectorStore
	startTime   time.Time
	version     string
}

// HealthResponse 健康检查响应
type HealthResponse struct {
	Status    string            `json:"status"`
	Version   string            `json:"version"`
	Uptime    string            `json:"uptime"`
	Timestamp string            `json:"timestamp"`
	GoVersion string            `json:"go_version"`
	Services  map[string]string `json:"services"`
}

// NewHealthHandler 创建健康检查处理器
func NewHealthHandler(db *database.PostgresDB, vectorStore vectorstore.VectorStore, version string) *HealthHandler {
	return &HealthHandler{
		db:          db,
		vectorStore: vectorStore,
		startTime:   time.Now(),
		version:     version,
	}
}

// RegisterRoutes 注册路由
func (h *HealthHandler) RegisterRoutes(r chi.Router) {
	r.Get("/health", h.GetHealth)
	r.Get("/health/liveness", h.GetLiveness)
	r.Get("/health/readiness", h.GetReadiness)
}

// GetHealth 获取综合健康状态
func (h *HealthHandler) GetHealth(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()

	statusCode := http.StatusOK
	services := make(map[string]string)

	// 检查数据库连接
	if err := h.db.Ping(ctx); err != nil {
		services["database"] = "down"
		statusCode = http.StatusServiceUnavailable
	} else {
		services["database"] = "up"
	}

	// 检查向量存储连接
	if err := h.vectorStore.Ping(ctx); err != nil {
		services["vector_store"] = "down"
		statusCode = http.StatusServiceUnavailable
	} else {
		services["vector_store"] = "up"
	}

	// 构建响应
	response := HealthResponse{
		Status:    "healthy",
		Version:   h.version,
		Uptime:    time.Since(h.startTime).String(),
		Timestamp: time.Now().Format(time.RFC3339),
		GoVersion: runtime.Version(),
		Services:  services,
	}

	if statusCode != http.StatusOK {
		response.Status = "degraded"
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(response)
}

// GetLiveness 获取活跃状态（容器健康检查）
func (h *HealthHandler) GetLiveness(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "alive"})
}

// GetReadiness 获取就绪状态（容器就绪检查）
func (h *HealthHandler) GetReadiness(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()

	// 检查数据库连接
	if err := h.db.Ping(ctx); err != nil {
		w.WriteHeader(http.StatusServiceUnavailable)
		json.NewEncoder(w).Encode(map[string]string{"status": "not ready", "reason": "database connection failed"})
		return
	}

	// 检查向量存储连接
	if err := h.vectorStore.Ping(ctx); err != nil {
		w.WriteHeader(http.StatusServiceUnavailable)
		json.NewEncoder(w).Encode(map[string]string{"status": "not ready", "reason": "vector store connection failed"})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "ready"})
}
