package usecases

import (
	"context"
	"errors"
	"fmt"
	
	"go.uber.org/zap"
	
	"knowledge-graph-service/internal/domain/repositories"
)

// RelationshipUseCase 关系用例
type RelationshipUseCase struct {
	relationshipRepo repositories.RelationshipRepository
	logger           *zap.Logger
}

// NewRelationshipUseCase 创建关系用例
func NewRelationshipUseCase(relationshipRepo repositories.RelationshipRepository, logger *zap.Logger) *RelationshipUseCase {
	return &RelationshipUseCase{
		relationshipRepo: relationshipRepo,
		logger:           logger,
	}
}

// CreateRelationship 创建关系
func (uc *RelationshipUseCase) CreateRelationship(ctx context.Context, sourceNodeId, targetNodeId string, relType repositories.RelationshipType, properties map[string]interface{}) (string, error) {
	if sourceNodeId == "" || targetNodeId == "" {
		return "", errors.New("源节点ID和目标节点ID不能为空")
	}
	
	if relType == "" {
		return "", errors.New("关系类型不能为空")
	}
	
	if properties == nil {
		properties = map[string]interface{}{}
	}
	
	// 添加创建时间
	if _, ok := properties["created_at"]; !ok {
		properties["created_at"] = currentTimeISO()
	}
	
	// 添加更新时间
	properties["updated_at"] = currentTimeISO()
	
	id, err := uc.relationshipRepo.CreateRelationship(ctx, sourceNodeId, targetNodeId, relType, properties)
	if err != nil {
		uc.logger.Error("创建关系失败", 
			zap.Error(err), 
			zap.String("sourceNodeId", sourceNodeId), 
			zap.String("targetNodeId", targetNodeId), 
			zap.String("relType", string(relType)))
		return "", fmt.Errorf("创建关系失败: %w", err)
	}
	
	return id, nil
}

// CreateBidirectionalRelationship 创建双向关系
func (uc *RelationshipUseCase) CreateBidirectionalRelationship(ctx context.Context, sourceNodeId, targetNodeId string, sourceToTargetType, targetToSourceType repositories.RelationshipType, properties map[string]interface{}) ([]string, error) {
	if sourceNodeId == "" || targetNodeId == "" {
		return nil, errors.New("源节点ID和目标节点ID不能为空")
	}
	
	if sourceToTargetType == "" || targetToSourceType == "" {
		return nil, errors.New("关系类型不能为空")
	}
	
	if properties == nil {
		properties = map[string]interface{}{}
	}
	
	// 添加创建时间
	if _, ok := properties["created_at"]; !ok {
		properties["created_at"] = currentTimeISO()
	}
	
	// 添加更新时间
	properties["updated_at"] = currentTimeISO()
	
	ids, err := uc.relationshipRepo.CreateBidirectionalRelationship(ctx, sourceNodeId, targetNodeId, sourceToTargetType, targetToSourceType, properties)
	if err != nil {
		uc.logger.Error("创建双向关系失败", 
			zap.Error(err), 
			zap.String("sourceNodeId", sourceNodeId), 
			zap.String("targetNodeId", targetNodeId), 
			zap.String("sourceToTargetType", string(sourceToTargetType)),
			zap.String("targetToSourceType", string(targetToSourceType)))
		return nil, fmt.Errorf("创建双向关系失败: %w", err)
	}
	
	return ids, nil
}

// GetRelationship 获取关系
func (uc *RelationshipUseCase) GetRelationship(ctx context.Context, id string) (map[string]interface{}, error) {
	if id == "" {
		return nil, errors.New("关系ID不能为空")
	}
	
	rel, err := uc.relationshipRepo.GetRelationship(ctx, id)
	if err != nil {
		uc.logger.Error("获取关系失败", zap.Error(err), zap.String("id", id))
		return nil, fmt.Errorf("获取关系失败: %w", err)
	}
	
	return rel, nil
}

// GetNodeRelationships 获取节点的关系
func (uc *RelationshipUseCase) GetNodeRelationships(ctx context.Context, nodeId string, direction string, types []repositories.RelationshipType) ([]map[string]interface{}, error) {
	if nodeId == "" {
		return nil, errors.New("节点ID不能为空")
	}
	
	// 验证direction参数
	if direction != "outgoing" && direction != "incoming" && direction != "both" {
		direction = "both" // 默认为双向
	}
	
	rels, err := uc.relationshipRepo.GetNodeRelationships(ctx, nodeId, direction, types)
	if err != nil {
		uc.logger.Error("获取节点关系失败", 
			zap.Error(err), 
			zap.String("nodeId", nodeId), 
			zap.String("direction", direction))
		return nil, fmt.Errorf("获取节点关系失败: %w", err)
	}
	
	return rels, nil
}

// GetRelationshipsBetweenNodes 获取两个节点之间的关系
func (uc *RelationshipUseCase) GetRelationshipsBetweenNodes(ctx context.Context, sourceNodeId, targetNodeId string, types []repositories.RelationshipType) ([]map[string]interface{}, error) {
	if sourceNodeId == "" || targetNodeId == "" {
		return nil, errors.New("源节点ID和目标节点ID不能为空")
	}
	
	rels, err := uc.relationshipRepo.GetRelationshipsBetweenNodes(ctx, sourceNodeId, targetNodeId, types)
	if err != nil {
		uc.logger.Error("获取节点间关系失败", 
			zap.Error(err), 
			zap.String("sourceNodeId", sourceNodeId), 
			zap.String("targetNodeId", targetNodeId))
		return nil, fmt.Errorf("获取节点间关系失败: %w", err)
	}
	
	return rels, nil
}

// UpdateRelationship 更新关系
func (uc *RelationshipUseCase) UpdateRelationship(ctx context.Context, id string, properties map[string]interface{}) error {
	if id == "" {
		return errors.New("关系ID不能为空")
	}
	
	if len(properties) == 0 {
		return errors.New("更新属性不能为空")
	}
	
	// 添加更新时间
	properties["updated_at"] = currentTimeISO()
	
	err := uc.relationshipRepo.UpdateRelationship(ctx, id, properties)
	if err != nil {
		uc.logger.Error("更新关系失败", zap.Error(err), zap.String("id", id))
		return fmt.Errorf("更新关系失败: %w", err)
	}
	
	return nil
}

// DeleteRelationship 删除关系
func (uc *RelationshipUseCase) DeleteRelationship(ctx context.Context, id string) error {
	if id == "" {
		return errors.New("关系ID不能为空")
	}
	
	err := uc.relationshipRepo.DeleteRelationship(ctx, id)
	if err != nil {
		uc.logger.Error("删除关系失败", zap.Error(err), zap.String("id", id))
		return fmt.Errorf("删除关系失败: %w", err)
	}
	
	return nil
}

// DeleteRelationshipsBetweenNodes 删除两个节点之间的关系
func (uc *RelationshipUseCase) DeleteRelationshipsBetweenNodes(ctx context.Context, sourceNodeId, targetNodeId string, types []repositories.RelationshipType) (int, error) {
	if sourceNodeId == "" || targetNodeId == "" {
		return 0, errors.New("源节点ID和目标节点ID不能为空")
	}
	
	count, err := uc.relationshipRepo.DeleteRelationshipsBetweenNodes(ctx, sourceNodeId, targetNodeId, types)
	if err != nil {
		uc.logger.Error("删除节点间关系失败", 
			zap.Error(err), 
			zap.String("sourceNodeId", sourceNodeId), 
			zap.String("targetNodeId", targetNodeId))
		return 0, fmt.Errorf("删除节点间关系失败: %w", err)
	}
	
	return count, nil
}

// FindPaths 查找路径
func (uc *RelationshipUseCase) FindPaths(ctx context.Context, startNodeId, endNodeId string, maxDepth int) ([]map[string]interface{}, error) {
	if startNodeId == "" || endNodeId == "" {
		return nil, errors.New("起始节点ID和目标节点ID不能为空")
	}
	
	if maxDepth <= 0 {
		maxDepth = 3 // 默认最大深度为3
	}
	
	paths, err := uc.relationshipRepo.FindPaths(ctx, startNodeId, endNodeId, maxDepth)
	if err != nil {
		uc.logger.Error("查找路径失败", 
			zap.Error(err), 
			zap.String("startNodeId", startNodeId), 
			zap.String("endNodeId", endNodeId), 
			zap.Int("maxDepth", maxDepth))
		return nil, fmt.Errorf("查找路径失败: %w", err)
	}
	
	return paths, nil
}

// FindCommunities 查找社区
func (uc *RelationshipUseCase) FindCommunities(ctx context.Context, nodeIds []string, algorithm string) ([]map[string]interface{}, error) {
	if algorithm == "" {
		algorithm = "louvain" // 默认使用Louvain算法
	}
	
	communities, err := uc.relationshipRepo.FindCommunities(ctx, nodeIds, algorithm)
	if err != nil {
		uc.logger.Error("查找社区失败", 
			zap.Error(err), 
			zap.Strings("nodeIds", nodeIds), 
			zap.String("algorithm", algorithm))
		return nil, fmt.Errorf("查找社区失败: %w", err)
	}
	
	return communities, nil
} 