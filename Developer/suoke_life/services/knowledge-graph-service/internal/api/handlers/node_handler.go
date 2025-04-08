package handlers

import (
	"net/http"
	"strconv"
	
	"github.com/gin-gonic/gin"
	
	"knowledge-graph-service/internal/usecases"
)

// NodeHandler 处理节点相关请求
type NodeHandler struct {
	nodeUseCase *usecases.NodeUseCase
}

// NewNodeHandler 创建节点处理程序
func NewNodeHandler(nodeUseCase *usecases.NodeUseCase) *NodeHandler {
	return &NodeHandler{
		nodeUseCase: nodeUseCase,
	}
}

// GetNode 获取单个节点
func (h *NodeHandler) GetNode(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "节点ID不能为空",
		})
		return
	}
	
	ctx := c.Request.Context()
	node, err := h.nodeUseCase.GetNode(ctx, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": err.Error(),
		})
		return
	}
	
	if node == nil {
		c.JSON(http.StatusNotFound, gin.H{
			"error": "未找到节点",
		})
		return
	}
	
	c.JSON(http.StatusOK, node)
}

// GetNodes 获取多个节点
func (h *NodeHandler) GetNodes(c *gin.Context) {
	var requestBody struct {
		IDs []string `json:"ids" binding:"required"`
	}
	
	if err := c.ShouldBindJSON(&requestBody); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求体: " + err.Error(),
		})
		return
	}
	
	ctx := c.Request.Context()
	nodes, err := h.nodeUseCase.GetNodes(ctx, requestBody.IDs)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"nodes": nodes,
		"count": len(nodes),
	})
}

// GetNodesByCategory 按分类获取节点
func (h *NodeHandler) GetNodesByCategory(c *gin.Context) {
	category := c.Param("category")
	if category == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "分类参数不能为空",
		})
		return
	}
	
	// 获取分页参数
	pageStr := c.DefaultQuery("page", "1")
	pageSizeStr := c.DefaultQuery("pageSize", "20")
	
	page, err := strconv.Atoi(pageStr)
	if err != nil || page < 1 {
		page = 1
	}
	
	pageSize, err := strconv.Atoi(pageSizeStr)
	if err != nil || pageSize < 1 {
		pageSize = 20
	}
	
	if pageSize > 100 {
		pageSize = 100 // 限制最大页面大小
	}
	
	ctx := c.Request.Context()
	nodes, total, err := h.nodeUseCase.GetNodesByCategory(ctx, category, page, pageSize)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"nodes":     nodes,
		"count":     len(nodes),
		"total":     total,
		"page":      page,
		"pageSize":  pageSize,
		"category":  category,
	})
}

// CreateNode 创建节点
func (h *NodeHandler) CreateNode(c *gin.Context) {
	var nodeData map[string]interface{}
	
	if err := c.ShouldBindJSON(&nodeData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的节点数据: " + err.Error(),
		})
		return
	}
	
	ctx := c.Request.Context()
	id, err := h.nodeUseCase.CreateNode(ctx, nodeData)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "创建节点失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusCreated, gin.H{
		"id": id,
		"message": "节点创建成功",
	})
}

// BatchCreateNodes 批量创建节点
func (h *NodeHandler) BatchCreateNodes(c *gin.Context) {
	var request struct {
		Nodes []map[string]interface{} `json:"nodes" binding:"required"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求体: " + err.Error(),
		})
		return
	}
	
	if len(request.Nodes) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "节点列表不能为空",
		})
		return
	}
	
	ctx := c.Request.Context()
	ids, err := h.nodeUseCase.BatchCreateNodes(ctx, request.Nodes)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "批量创建节点失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusCreated, gin.H{
		"ids": ids,
		"count": len(ids),
		"message": "节点批量创建成功",
	})
}

// UpdateNode 更新节点
func (h *NodeHandler) UpdateNode(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "节点ID不能为空",
		})
		return
	}
	
	var nodeData map[string]interface{}
	
	if err := c.ShouldBindJSON(&nodeData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的节点数据: " + err.Error(),
		})
		return
	}
	
	ctx := c.Request.Context()
	err := h.nodeUseCase.UpdateNode(ctx, id, nodeData)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "更新节点失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"id": id,
		"message": "节点更新成功",
	})
}

// DeleteNode 删除节点
func (h *NodeHandler) DeleteNode(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "节点ID不能为空",
		})
		return
	}
	
	ctx := c.Request.Context()
	err := h.nodeUseCase.DeleteNode(ctx, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "删除节点失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"id": id,
		"message": "节点删除成功",
	})
}

// SearchNodes 搜索节点
func (h *NodeHandler) SearchNodes(c *gin.Context) {
	var request struct {
		Query     string                 `json:"query" binding:"required"`
		Params    map[string]interface{} `json:"params"`
		PageSize  int                    `json:"pageSize"`
		Page      int                    `json:"page"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求体: " + err.Error(),
		})
		return
	}
	
	if request.Query == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "查询语句不能为空",
		})
		return
	}
	
	if request.Page < 1 {
		request.Page = 1
	}
	
	if request.PageSize < 1 {
		request.PageSize = 20
	}
	
	if request.PageSize > 100 {
		request.PageSize = 100 // 限制最大页面大小
	}
	
	ctx := c.Request.Context()
	nodes, err := h.nodeUseCase.SearchNodes(ctx, request.Query, request.Params, request.Page, request.PageSize)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "搜索节点失败: " + err.Error(),
		})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"nodes":     nodes,
		"count":     len(nodes),
		"page":      request.Page,
		"pageSize":  request.PageSize,
		"query":     request.Query,
	})
} 