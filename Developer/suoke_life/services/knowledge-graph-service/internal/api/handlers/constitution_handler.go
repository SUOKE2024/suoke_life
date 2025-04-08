package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"knowledge-graph-service/internal/domain/entities"
	"knowledge-graph-service/internal/usecases"
)

// ConstitutionHandler 体质处理器
type ConstitutionHandler struct {
	constitutionUseCase *usecases.ConstitutionUseCase
	logger              *zap.Logger
}

// NewConstitutionHandler 创建体质处理器
func NewConstitutionHandler(constitutionUseCase *usecases.ConstitutionUseCase, logger *zap.Logger) *ConstitutionHandler {
	return &ConstitutionHandler{
		constitutionUseCase: constitutionUseCase,
		logger:              logger,
	}
}

// CreateConstitution 创建体质
func (h *ConstitutionHandler) CreateConstitution(c *gin.Context) {
	var request struct {
		Name         string                           `json:"name" binding:"required"`
		Type         string                           `json:"type" binding:"required"`
		Description  string                           `json:"description"`
		Features     *entities.ConstitutionFeatures   `json:"features"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 创建体质节点
	constitutionType := entities.ConstitutionType(request.Type)
	constitutionNode := entities.NewConstitutionNode(request.Name, constitutionType, request.Description)
	
	// 设置特征
	if request.Features != nil {
		constitutionNode.SetFeatures(request.Features)
	}

	// 保存到数据库
	node, err := h.constitutionUseCase.CreateConstitution(c.Request.Context(), constitutionNode)
	if err != nil {
		h.logger.Error("创建体质失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "创建体质失败"})
		return
	}

	c.JSON(http.StatusCreated, node)
}

// GetConstitution 获取体质
func (h *ConstitutionHandler) GetConstitution(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少ID参数"})
		return
	}

	// 获取体质节点
	node, err := h.constitutionUseCase.GetConstitutionByID(c.Request.Context(), id)
	if err != nil {
		h.logger.Error("获取体质失败", zap.Error(err), zap.String("id", id))
		c.JSON(http.StatusNotFound, gin.H{"error": "获取体质失败或节点不存在"})
		return
	}

	c.JSON(http.StatusOK, node)
}

// GetConstitutionWithRelations 获取带关系的体质
func (h *ConstitutionHandler) GetConstitutionWithRelations(c *gin.Context) {
	id := c.Param("id")
	if id == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少ID参数"})
		return
	}

	// 获取带关系的体质
	result, err := h.constitutionUseCase.GetConstitutionWithRelations(c.Request.Context(), id)
	if err != nil {
		h.logger.Error("获取体质关系失败", zap.Error(err), zap.String("id", id))
		c.JSON(http.StatusNotFound, gin.H{"error": "获取体质关系失败或节点不存在"})
		return
	}

	c.JSON(http.StatusOK, result)
}

// QueryConstitutions 查询体质列表
func (h *ConstitutionHandler) QueryConstitutions(c *gin.Context) {
	var params usecases.ConstitutionQueryParams

	// 从查询参数中获取过滤条件
	params.Type = c.Query("type")
	if symptoms := c.QueryArray("symptom"); len(symptoms) > 0 {
		params.Symptoms = symptoms
	}
	
	// 处理分页参数
	if page, err := parseInt(c.Query("page"), 1); err == nil {
		params.Page = page
	}
	
	if pageSize, err := parseInt(c.Query("page_size"), 10); err == nil {
		params.PageSize = pageSize
	}
	
	// 是否包含详情
	params.IncludeDetail = c.Query("include_detail") == "true"

	// 查询体质
	nodes, total, err := h.constitutionUseCase.QueryConstitutions(c.Request.Context(), &params)
	if err != nil {
		h.logger.Error("查询体质列表失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "查询体质列表失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": nodes,
		"total": total,
		"page": params.Page,
		"page_size": params.PageSize,
	})
}

// FindSuitableConstitutionBySymptoms 根据症状查找合适的体质
func (h *ConstitutionHandler) FindSuitableConstitutionBySymptoms(c *gin.Context) {
	var request struct {
		Symptoms []string `json:"symptoms" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 查询合适的体质
	constitutions, err := h.constitutionUseCase.FindSuitableConstitutionBySymptoms(c.Request.Context(), request.Symptoms)
	if err != nil {
		h.logger.Error("根据症状查找体质失败", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "根据症状查找体质失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": constitutions,
		"count": len(constitutions),
	})
}

// LinkConstitutionToSymptom 关联体质和症状
func (h *ConstitutionHandler) LinkConstitutionToSymptom(c *gin.Context) {
	constitutionID := c.Param("id")
	if constitutionID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少体质ID参数"})
		return
	}

	var request struct {
		SymptomID  string                 `json:"symptom_id" binding:"required"`
		Properties map[string]interface{} `json:"properties"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 创建关联
	relationship, err := h.constitutionUseCase.LinkConstitutionToSymptom(
		c.Request.Context(), 
		constitutionID, 
		request.SymptomID, 
		request.Properties,
	)
	if err != nil {
		h.logger.Error("关联体质和症状失败", 
			zap.Error(err), 
			zap.String("constitutionID", constitutionID),
			zap.String("symptomID", request.SymptomID),
		)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "关联体质和症状失败"})
		return
	}

	c.JSON(http.StatusCreated, relationship)
}

// GetRelatedOrgans 获取体质相关脏腑
func (h *ConstitutionHandler) GetRelatedOrgans(c *gin.Context) {
	constitutionID := c.Param("id")
	if constitutionID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少体质ID参数"})
		return
	}

	// 获取相关脏腑
	organs, err := h.constitutionUseCase.GetRelatedOrgans(c.Request.Context(), constitutionID)
	if err != nil {
		h.logger.Error("获取体质相关脏腑失败", zap.Error(err), zap.String("constitutionID", constitutionID))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取体质相关脏腑失败"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": organs,
		"count": len(organs),
	})
}

// GetSuggestions 获取体质养生建议
func (h *ConstitutionHandler) GetSuggestions(c *gin.Context) {
	constitutionID := c.Param("id")
	if constitutionID == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "缺少体质ID参数"})
		return
	}

	// 获取养生建议
	suggestions, err := h.constitutionUseCase.GetRelatedSuggestions(c.Request.Context(), constitutionID)
	if err != nil {
		h.logger.Error("获取体质养生建议失败", zap.Error(err), zap.String("constitutionID", constitutionID))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "获取体质养生建议失败"})
		return
	}

	c.JSON(http.StatusOK, suggestions)
} 