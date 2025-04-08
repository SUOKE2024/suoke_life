package usecases

import (
	"context"
	"errors"
	"time"

	"go.uber.org/zap"

	"knowledge-graph-service/internal/domain/entities"
	"knowledge-graph-service/internal/domain/repositories"
)

// ConstitutionUseCase 体质辨识用例
type ConstitutionUseCase struct {
	nodeRepo        repositories.NodeRepository
	relationshipRepo repositories.RelationshipRepository
	logger          *zap.Logger
}

// NewConstitutionUseCase 创建体质辨识用例
func NewConstitutionUseCase(
	nodeRepo repositories.NodeRepository,
	relationshipRepo repositories.RelationshipRepository,
	logger *zap.Logger,
) *ConstitutionUseCase {
	return &ConstitutionUseCase{
		nodeRepo:        nodeRepo,
		relationshipRepo: relationshipRepo,
		logger:          logger,
	}
}

// ConstitutionQueryParams 体质查询参数
type ConstitutionQueryParams struct {
	Type          string   `json:"type,omitempty"`
	Symptoms      []string `json:"symptoms,omitempty"`
	IncludeDetail bool     `json:"include_detail,omitempty"`
	Page          int      `json:"page,omitempty"`
	PageSize      int      `json:"page_size,omitempty"`
}

// ConstitutionWithRelations 带关联的体质
type ConstitutionWithRelations struct {
	Constitution    *entities.Node                 `json:"constitution"`
	RelatedSymptoms []*entities.Relationship       `json:"related_symptoms,omitempty"`
	RelatedHerbs    []*entities.Relationship       `json:"related_herbs,omitempty"`
	RelatedFoods    []*entities.Relationship       `json:"related_foods,omitempty"`
	Relations       map[string][]*entities.Relationship `json:"relations,omitempty"`
}

// CreateConstitution 创建体质节点
func (u *ConstitutionUseCase) CreateConstitution(ctx context.Context, constitutionData *entities.ConstitutionNode) (*entities.Node, error) {
	u.logger.Info("创建体质节点", zap.String("name", constitutionData.GetName()), zap.String("type", string(constitutionData.GetConstitutionType())))
	
	// 将体质节点转换为基础节点进行存储
	return u.nodeRepo.Create(ctx, constitutionData.Node)
}

// GetConstitutionByID 根据ID获取体质
func (u *ConstitutionUseCase) GetConstitutionByID(ctx context.Context, id string) (*entities.Node, error) {
	u.logger.Info("获取体质节点", zap.String("id", id))
	
	node, err := u.nodeRepo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}
	
	// 验证节点是否为体质类型
	if category, ok := node.GetProperty("category"); ok {
		if categoryStr, isString := category.(string); isString && categoryStr == "constitution" {
			return node, nil
		}
	}
	
	return nil, errors.New("节点不是体质类型")
}

// GetConstitutionWithRelations 获取带关系的体质信息
func (u *ConstitutionUseCase) GetConstitutionWithRelations(ctx context.Context, id string) (*ConstitutionWithRelations, error) {
	u.logger.Info("获取带关系的体质信息", zap.String("id", id))
	
	// 获取体质节点
	node, err := u.GetConstitutionByID(ctx, id)
	if err != nil {
		return nil, err
	}
	
	// 构建返回结构
	result := &ConstitutionWithRelations{
		Constitution: node,
		Relations:    make(map[string][]*entities.Relationship),
	}
	
	// 获取关联关系
	relations, err := u.relationshipRepo.GetRelationshipsByNodeID(ctx, id)
	if err != nil {
		u.logger.Error("获取体质关系失败", zap.Error(err))
		return result, nil // 即使获取关系失败，也返回基本节点信息
	}
	
	// 对关系进行分类
	for _, rel := range relations {
		relType := rel.GetType()
		result.Relations[relType] = append(result.Relations[relType], rel)
		
		// 按特定关系类型分类
		switch relType {
		case "HAS_SYMPTOM":
			result.RelatedSymptoms = append(result.RelatedSymptoms, rel)
		case "RECOMMENDS_HERB":
			result.RelatedHerbs = append(result.RelatedHerbs, rel)
		case "RECOMMENDS_FOOD":
			result.RelatedFoods = append(result.RelatedFoods, rel)
		}
	}
	
	return result, nil
}

// QueryConstitutions 查询体质列表
func (u *ConstitutionUseCase) QueryConstitutions(ctx context.Context, params *ConstitutionQueryParams) ([]*entities.Node, int, error) {
	u.logger.Info("查询体质列表", 
		zap.String("type", params.Type), 
		zap.Strings("symptoms", params.Symptoms),
		zap.Int("page", params.Page),
		zap.Int("pageSize", params.PageSize),
	)
	
	// 构建查询条件
	filters := map[string]interface{}{
		"category": "constitution",
	}
	
	if params.Type != "" {
		filters["type"] = params.Type
	}
	
	// 设置分页
	if params.Page <= 0 {
		params.Page = 1
	}
	
	if params.PageSize <= 0 || params.PageSize > 100 {
		params.PageSize = 10
	}
	
	// 查询节点
	nodes, total, err := u.nodeRepo.Query(ctx, filters, params.Page, params.PageSize)
	if err != nil {
		return nil, 0, err
	}
	
	// 如果有症状过滤，需要进一步处理
	if len(params.Symptoms) > 0 {
		// 在实际应用中，这里应该通过关系查询，为简化示例，仅记录日志
		u.logger.Info("需要按症状过滤体质", zap.Strings("symptoms", params.Symptoms))
		// 实际实现需要通过图查询语言筛选包含指定症状的体质
	}
	
	return nodes, total, nil
}

// FindSuitableConstitutionBySymptoms 根据症状查找适合的体质
func (u *ConstitutionUseCase) FindSuitableConstitutionBySymptoms(ctx context.Context, symptoms []string) ([]*entities.Node, error) {
	u.logger.Info("根据症状查找适合的体质", zap.Strings("symptoms", symptoms))
	
	if len(symptoms) == 0 {
		return nil, errors.New("症状列表不能为空")
	}
	
	// 这里需要使用NEO4J专门的图查询，示例代码仅作参考
	// 在实际实现中，应该通过图数据库查询找到与这些症状最相关的体质
	
	// 示例实现：简单返回空结果
	// 实际实现应该根据症状的匹配度计算最合适的体质类型
	return []*entities.Node{}, nil
}

// LinkConstitutionToSymptom 关联体质和症状
func (u *ConstitutionUseCase) LinkConstitutionToSymptom(ctx context.Context, constitutionID, symptomID string, properties map[string]interface{}) (*entities.Relationship, error) {
	u.logger.Info("关联体质和症状", 
		zap.String("constitutionID", constitutionID), 
		zap.String("symptomID", symptomID),
	)
	
	// 添加关系类型和时间戳
	if properties == nil {
		properties = make(map[string]interface{})
	}
	properties["created_at"] = time.Now()
	
	// 创建关系
	return u.relationshipRepo.CreateRelationship(ctx, constitutionID, symptomID, "HAS_SYMPTOM", properties)
}

// GetRelatedOrgans 获取体质相关脏腑
func (u *ConstitutionUseCase) GetRelatedOrgans(ctx context.Context, constitutionID string) ([]*entities.Node, error) {
	u.logger.Info("获取体质相关脏腑", zap.String("constitutionID", constitutionID))
	
	// 通过关系查询相关脏腑
	// 这里应该使用图数据库的关系查询功能
	
	// 示例实现：简单返回空结果
	return []*entities.Node{}, nil
}

// GetRelatedSuggestions 获取体质养生建议
func (u *ConstitutionUseCase) GetRelatedSuggestions(ctx context.Context, constitutionID string) (map[string]interface{}, error) {
	u.logger.Info("获取体质养生建议", zap.String("constitutionID", constitutionID))
	
	// 获取体质节点
	node, err := u.GetConstitutionByID(ctx, constitutionID)
	if err != nil {
		return nil, err
	}
	
	// 提取养生建议信息
	suggestions := make(map[string]interface{})
	
	// 提取食物建议
	if foods, ok := node.GetProperty("suitable_foods"); ok {
		suggestions["suitable_foods"] = foods
	}
	
	if foods, ok := node.GetProperty("unsuitable_foods"); ok {
		suggestions["unsuitable_foods"] = foods
	}
	
	// 提取生活调摄建议
	if lifestyle, ok := node.GetProperty("lifestyle_suggestions"); ok {
		suggestions["lifestyle"] = lifestyle
	}
	
	// 返回建议结果
	return suggestions, nil
} 