package repositories

import (
	"context"
)

// RelationshipType 关系类型
type RelationshipType string

// 常见关系类型定义
const (
	RelationshipTypeContains      RelationshipType = "CONTAINS"
	RelationshipTypePartOf        RelationshipType = "PART_OF"
	RelationshipTypeRelatedTo     RelationshipType = "RELATED_TO"
	RelationshipTypeTreats        RelationshipType = "TREATS"
	RelationshipTypeCauseBy       RelationshipType = "CAUSED_BY"
	RelationshipTypeSimilarTo     RelationshipType = "SIMILAR_TO"
	RelationshipTypeHas           RelationshipType = "HAS"
	RelationshipTypeBelongsTo     RelationshipType = "BELONGS_TO"
	RelationshipTypeAssociatedWith RelationshipType = "ASSOCIATED_WITH"
)

// RelationshipRepository 定义了关系操作的接口
type RelationshipRepository interface {
	// 创建关系
	CreateRelationship(ctx context.Context, sourceNodeId, targetNodeId string, relType RelationshipType, properties map[string]interface{}) (string, error)
	
	// 创建双向关系(两个节点之间创建相反的两个关系)
	CreateBidirectionalRelationship(ctx context.Context, sourceNodeId, targetNodeId string, sourceToTargetType, targetToSourceType RelationshipType, properties map[string]interface{}) ([]string, error)
	
	// 获取关系
	GetRelationship(ctx context.Context, id string) (map[string]interface{}, error)
	
	// 获取节点的所有关系
	GetNodeRelationships(ctx context.Context, nodeId string, direction string, types []RelationshipType) ([]map[string]interface{}, error)
	
	// 获取两个节点之间的关系
	GetRelationshipsBetweenNodes(ctx context.Context, sourceNodeId, targetNodeId string, types []RelationshipType) ([]map[string]interface{}, error)
	
	// 更新关系属性
	UpdateRelationship(ctx context.Context, id string, properties map[string]interface{}) error
	
	// 删除关系
	DeleteRelationship(ctx context.Context, id string) error
	DeleteRelationshipsBetweenNodes(ctx context.Context, sourceNodeId, targetNodeId string, types []RelationshipType) (int, error)
	
	// 查询路径
	FindPaths(ctx context.Context, startNodeId, endNodeId string, maxDepth int) ([]map[string]interface{}, error)
	
	// 查询社区
	FindCommunities(ctx context.Context, nodeIds []string, algorithm string) ([]map[string]interface{}, error)
} 