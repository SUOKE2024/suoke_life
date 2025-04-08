package handlers

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"

	"knowledge-graph-service/internal/usecases"
	"knowledge-graph-service/internal/domain/repositories"
)

// RelationshipHandler 处理关系相关请求
type RelationshipHandler struct {
	relationshipUseCase *usecases.RelationshipUseCase
}

// NewRelationshipHandler 创建关系处理程序
func NewRelationshipHandler(relationshipUseCase *usecases.RelationshipUseCase) *RelationshipHandler {
	return &RelationshipHandler{
		relationshipUseCase: relationshipUseCase,
	}
}

// CreateRelationship 创建关系
func (h *RelationshipHandler) CreateRelationship(c *gin.Context) {
	var request struct {
		SourceNodeID string                 `json:"sourceNodeId" binding:"required"`
		TargetNodeID string                 `json:"targetNodeId" binding:"required"`
		RelType      string                 `json:"relType" binding:"required"`
		Properties   map[string]interface{} `json:"properties"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求体: " + err.Error(),
		})
		return
	}
	
	ctx := c.Request.Context()
	id, err := h.relationshipUseCase.CreateRelationship(
		ctx, 
		request.SourceNodeID,
		request.TargetNodeID,
		repositories.RelationshipType(request.RelType),
		request.Properties,
	)
	
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "创建关系失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusCreated, gin.H{
		"id": id,
		"message": "关系创建成功",
	})
}

// CreateBidirectionalRelationship 创建双向关系
func (h *RelationshipHandler) CreateBidirectionalRelationship(c *gin.Context) {
	var request struct {
		SourceNodeID string                 `json:"sourceNodeId" binding:"required"`
		TargetNodeID string                 `json:"targetNodeId" binding:"required"`
		RelType      string                 `json:"relType" binding:"required"`
		Properties   map[string]interface{} `json:"properties"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求体: " + err.Error(),
		})
		return
	}
	
	ctx := c.Request.Context()
	ids, err := h.relationshipUseCase.CreateBidirectionalRelationship(
		ctx, 
		request.SourceNodeID,
		request.TargetNodeID,
		repositories.RelationshipType(request.RelType),
		repositories.RelationshipType(fmt.Sprintf("REVERSE_%s", request.RelType)),
		request.Properties,
	)
	
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "创建双向关系失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusCreated, gin.H{
		"ids": ids,
		"message": "双向关系创建成功",
	})
}

// GetRelationship 获取关系
func (h *RelationshipHandler) GetRelationship(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "关系ID不能为空",
		})
		return
	}
	
	ctx := c.Request.Context()
	relationship, err := h.relationshipUseCase.GetRelationship(ctx, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": err.Error(),
		})
		return
	}
	
	if relationship == nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "未找到关系",
		})
		return
	}
	
	c.JSON(http.StatusOK, relationship)
}

// GetNodeRelationships 获取节点的所有关系
func (h *RelationshipHandler) GetNodeRelationships(c *gin.Context) {
	nodeID := c.Param("nodeId")
	if nodeID == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "节点ID不能为空",
		})
		return
	}
	
	direction := c.DefaultQuery("direction", "both")
	if direction != "in" && direction != "out" && direction != "both" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的方向参数，必须是 'in'、'out' 或 'both'",
		})
		return
	}
	
	var types []repositories.RelationshipType
	typesParam := c.Query("types")
	if typesParam != "" {
		typesList := []string{typesParam}
		types = make([]repositories.RelationshipType, len(typesList))
		for i, t := range typesList {
			types[i] = repositories.RelationshipType(t)
		}
	}
	
	ctx := c.Request.Context()
	relationships, err := h.relationshipUseCase.GetNodeRelationships(ctx, nodeID, direction, types)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"relationships": relationships,
		"count": len(relationships),
		"nodeId": nodeID,
		"direction": direction,
	})
}

// GetRelationshipsBetweenNodes 获取两个节点之间的关系
func (h *RelationshipHandler) GetRelationshipsBetweenNodes(c *gin.Context) {
	var request struct {
		SourceNodeID string   `json:"sourceNodeId" binding:"required"`
		TargetNodeID string   `json:"targetNodeId" binding:"required"`
		Types        []string `json:"types"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求体: " + err.Error(),
		})
		return
	}
	
	ctx := c.Request.Context()
	// 将[]string转换为[]repositories.RelationshipType
	relTypes := make([]repositories.RelationshipType, len(request.Types))
	for i, t := range request.Types {
		relTypes[i] = repositories.RelationshipType(t)
	}
	
	relationships, err := h.relationshipUseCase.GetRelationshipsBetweenNodes(
		ctx,
		request.SourceNodeID,
		request.TargetNodeID,
		relTypes,
	)
	
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"relationships": relationships,
		"count": len(relationships),
		"sourceNodeId": request.SourceNodeID,
		"targetNodeId": request.TargetNodeID,
	})
}

// UpdateRelationship 更新关系
func (h *RelationshipHandler) UpdateRelationship(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "关系ID不能为空",
		})
		return
	}
	
	var request struct {
		Properties map[string]interface{} `json:"properties" binding:"required"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求体: " + err.Error(),
		})
		return
	}
	
	ctx := c.Request.Context()
	err := h.relationshipUseCase.UpdateRelationship(ctx, id, request.Properties)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "更新关系失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"id": id,
		"message": "关系更新成功",
	})
}

// DeleteRelationship 删除关系
func (h *RelationshipHandler) DeleteRelationship(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "关系ID不能为空",
		})
		return
	}
	
	ctx := c.Request.Context()
	err := h.relationshipUseCase.DeleteRelationship(ctx, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "删除关系失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"id": id,
		"message": "关系删除成功",
	})
}

// DeleteRelationshipsBetweenNodes 删除两个节点之间的关系
func (h *RelationshipHandler) DeleteRelationshipsBetweenNodes(c *gin.Context) {
	var request struct {
		SourceNodeID string   `json:"sourceNodeId" binding:"required"`
		TargetNodeID string   `json:"targetNodeId" binding:"required"`
		Types        []string `json:"types"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求体: " + err.Error(),
		})
		return
	}
	
	ctx := c.Request.Context()
	// 将[]string转换为[]repositories.RelationshipType
	relTypes := make([]repositories.RelationshipType, len(request.Types))
	for i, t := range request.Types {
		relTypes[i] = repositories.RelationshipType(t)
	}
	
	count, err := h.relationshipUseCase.DeleteRelationshipsBetweenNodes(
		ctx,
		request.SourceNodeID,
		request.TargetNodeID,
		relTypes,
	)
	
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "删除关系失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"count": count,
		"sourceNodeId": request.SourceNodeID,
		"targetNodeId": request.TargetNodeID,
		"message": "关系删除成功",
	})
}

// FindPaths 查找路径
func (h *RelationshipHandler) FindPaths(c *gin.Context) {
	var request struct {
		StartNodeID string `json:"startNodeId" binding:"required"`
		EndNodeID   string `json:"endNodeId" binding:"required"`
		MaxDepth    int    `json:"maxDepth"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求体: " + err.Error(),
		})
		return
	}
	
	if request.MaxDepth <= 0 {
		request.MaxDepth = 3 // 默认最大深度
	}
	
	if request.MaxDepth > 10 {
		request.MaxDepth = 10 // 限制最大深度
	}
	
	ctx := c.Request.Context()
	paths, err := h.relationshipUseCase.FindPaths(
		ctx,
		request.StartNodeID,
		request.EndNodeID,
		request.MaxDepth,
	)
	
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "查找路径失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"paths": paths,
		"count": len(paths),
		"startNodeId": request.StartNodeID,
		"endNodeId": request.EndNodeID,
		"maxDepth": request.MaxDepth,
	})
}

// FindCommunities 查找社区
func (h *RelationshipHandler) FindCommunities(c *gin.Context) {
	var request struct {
		NodeIDs   []string `json:"nodeIds" binding:"required"`
		Algorithm string   `json:"algorithm"`
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
	
	if request.Algorithm == "" {
		request.Algorithm = "louvain" // 默认使用Louvain算法
	}
	
	ctx := c.Request.Context()
	communities, err := h.relationshipUseCase.FindCommunities(
		ctx,
		request.NodeIDs,
		request.Algorithm,
	)
	
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "查找社区失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"communities": communities,
		"count": len(communities),
		"algorithm": request.Algorithm,
	})
} 