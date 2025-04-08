package handlers

import (
	"fmt"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"

	"knowledge-graph-service/internal/usecases"
	"knowledge-graph-service/internal/logger"
)

// GraphHandler 图处理程序
type GraphHandler struct {
	useCase *usecases.GraphUseCase
	logger  *logger.Logger
}

// NewGraphHandler 创建新的图处理程序
func NewGraphHandler(useCase *usecases.GraphUseCase, logger *logger.Logger) *GraphHandler {
	return &GraphHandler{
		useCase: useCase,
		logger:  logger,
	}
}

// GetNeighbors 获取节点的邻居
func (h *GraphHandler) GetNeighbors(c *gin.Context) {
	nodeID := c.Query("nodeId")
	if nodeID == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "节点ID不能为空",
		})
		return
	}
	
	depthStr := c.DefaultQuery("depth", "1")
	depthInt, err := strconv.Atoi(depthStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "深度必须是整数",
		})
		return
	}
	
	direction := c.DefaultQuery("direction", "both")
	if direction != "in" && direction != "out" && direction != "both" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "方向必须是 'in'、'out' 或 'both'",
		})
		return
	}
	
	ctx := c.Request.Context()
	subgraph, err := h.useCase.GetNeighbors(ctx, nodeID, depthInt, direction)
	if err != nil {
		h.logger.Error(fmt.Sprintf("获取邻居节点失败: %v", err))
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "获取邻居节点失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"subgraph": subgraph,
		"nodeId": nodeID,
		"depth": depthInt,
		"direction": direction,
	})
}

// GetSubgraph 获取子图
func (h *GraphHandler) GetSubgraph(c *gin.Context) {
	var request struct {
		NodeIDs             []string `json:"nodeIds" binding:"required"`
		IncludeRelationships bool     `json:"includeRelationships"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求体: " + err.Error(),
		})
		return
	}
	
	if len(request.NodeIDs) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "节点ID列表不能为空",
		})
		return
	}
	
	ctx := c.Request.Context()
	subgraph, err := h.useCase.GetSubgraph(ctx, request.NodeIDs, request.IncludeRelationships)
	if err != nil {
		h.logger.Error(fmt.Sprintf("获取子图失败: %v", err))
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "获取子图失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"subgraph": subgraph,
		"nodeCount": len(request.NodeIDs),
	})
}

// GetRelationshipTypes 获取所有关系类型
func (h *GraphHandler) GetRelationshipTypes(c *gin.Context) {
	types, err := h.useCase.GetAllRelationshipTypes()
	if err != nil {
		h.logger.Error(fmt.Sprintf("获取关系类型失败: %v", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取关系类型失败"})
		return
	}

	c.JSON(http.StatusOK, types)
}

// GetNodeNeighborhood 获取节点周围的邻居
func (h *GraphHandler) GetNodeNeighborhood(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "节点ID不能为空"})
		return
	}

	depth := 1
	depthStr := c.DefaultQuery("depth", "1")
	if d, err := strconv.Atoi(depthStr); err == nil && d > 0 {
		depth = d
	}

	neighborhood, err := h.useCase.GetNodeNeighborhood(id, depth)
	if err != nil {
		h.logger.Error(fmt.Sprintf("获取节点邻居失败: %v", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取节点邻居失败"})
		return
	}

	c.JSON(http.StatusOK, neighborhood)
}

// SearchGraph 搜索图
func (h *GraphHandler) SearchGraph(c *gin.Context) {
	query := c.Query("q")
	if query == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "查询参数不能为空"})
		return
	}

	limit := 20
	limitStr := c.DefaultQuery("limit", "20")
	if l, err := strconv.Atoi(limitStr); err == nil && l > 0 {
		limit = l
	}

	nodeType := c.Query("type")

	results, err := h.useCase.SearchGraph(query, nodeType, limit)
	if err != nil {
		h.logger.Error(fmt.Sprintf("搜索图失败: %v", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "搜索图失败"})
		return
	}

	c.JSON(http.StatusOK, results)
}

// FindPath 查找路径
func (h *GraphHandler) FindPath(c *gin.Context) {
	sourceID := c.Query("source")
	targetID := c.Query("target")
	if sourceID == "" || targetID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "源节点ID和目标节点ID不能为空"})
		return
	}

	maxDepth := 4
	depthStr := c.DefaultQuery("max_depth", "4")
	if d, err := strconv.Atoi(depthStr); err == nil && d > 0 {
		maxDepth = d
	}

	paths, err := h.useCase.FindPaths(sourceID, targetID, maxDepth)
	if err != nil {
		h.logger.Error(fmt.Sprintf("查找路径失败: %v", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查找路径失败"})
		return
	}

	c.JSON(http.StatusOK, paths)
}

// GetTCMZangFuRelations 获取中医脏腑关系
func (h *GraphHandler) GetTCMZangFuRelations(c *gin.Context) {
	results, err := h.useCase.GetZangFuRelations()
	if err != nil {
		h.logger.Error(fmt.Sprintf("获取脏腑关系失败: %v", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取脏腑关系失败"})
		return
	}

	c.JSON(http.StatusOK, results)
}

// GetConstitutionZangFuRelations 获取体质与脏腑关系
func (h *GraphHandler) GetConstitutionZangFuRelations(c *gin.Context) {
	constitutionType := c.Query("type")
	
	results, err := h.useCase.GetConstitutionZangFuRelations(constitutionType)
	if err != nil {
		h.logger.Error(fmt.Sprintf("获取体质与脏腑关系失败: %v", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取体质与脏腑关系失败"})
		return
	}

	c.JSON(http.StatusOK, results)
}

// GetConstitutionSymptomRelations 获取体质与症状关系
func (h *GraphHandler) GetConstitutionSymptomRelations(c *gin.Context) {
	constitutionType := c.Query("type")
	
	results, err := h.useCase.GetConstitutionSymptomRelations(constitutionType)
	if err != nil {
		h.logger.Error(fmt.Sprintf("获取体质与症状关系失败: %v", err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取体质与症状关系失败"})
		return
	}

	c.JSON(http.StatusOK, results)
}

// ExportGraph 导出图表
func (h *GraphHandler) ExportGraph(c *gin.Context) {
	var request struct {
		NodeIDs []string `json:"nodeIds" binding:"required"`
		Format  string   `json:"format"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求体: " + err.Error(),
		})
		return
	}
	
	if len(request.NodeIDs) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "节点ID列表不能为空",
		})
		return
	}
	
	if request.Format == "" {
		request.Format = "json" // 默认格式
	}
	
	ctx := c.Request.Context()
	data, err := h.useCase.ExportGraph(ctx, request.NodeIDs, request.Format)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "导出图表失败: " + err.Error(),
		})
		return
	}
	
	if request.Format == "json" {
		c.JSON(http.StatusOK, data)
	} else {
		// 对于其他格式，以文件形式提供
		c.Header("Content-Disposition", "attachment; filename=graph-export."+request.Format)
		
		// 将data转为string类型（如果是其他格式，应该已经是字符串格式）
		dataStr, ok := data["content"].(string)
		if !ok {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": "导出的数据格式错误",
			})
			return
		}
		
		c.Data(http.StatusOK, "application/octet-stream", []byte(dataStr))
	}
} 