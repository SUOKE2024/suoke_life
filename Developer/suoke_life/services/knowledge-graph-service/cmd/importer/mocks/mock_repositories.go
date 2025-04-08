package mocks

import (
	"context"
	"fmt"
	"sync"
	"time"

	"go.uber.org/zap"
	"knowledge-graph-service/internal/domain/repositories"
)

// SimpleNodeRepository 简单的节点存储库实现，用于测试
type SimpleNodeRepository struct {
	nodes  map[string]map[string]interface{}
	mu     sync.RWMutex
	logger *zap.Logger
}

// NewSimpleNodeRepository 创建一个新的简单节点存储库
func NewSimpleNodeRepository(logger *zap.Logger) repositories.NodeRepository {
	if logger == nil {
		logger = zap.NewNop()
	}

	return &SimpleNodeRepository{
		nodes:  make(map[string]map[string]interface{}),
		logger: logger,
	}
}

// CreateNode 创建节点
func (r *SimpleNodeRepository) CreateNode(ctx context.Context, name string, category string, properties map[string]interface{}) (string, error) {
	r.mu.Lock()
	defer r.mu.Unlock()

	// 生成简单ID
	id := fmt.Sprintf("%s-%d", name, time.Now().UnixNano())

	// 创建节点数据
	nodeData := map[string]interface{}{
		"id":         id,
		"name":       name,
		"category":   category,
		"properties": properties,
		"created_at": time.Now(),
		"updated_at": time.Now(),
	}

	// 存储节点
	r.nodes[id] = nodeData
	r.logger.Info("Created node", zap.String("id", id), zap.String("name", name))

	return id, nil
}

// BatchCreateNodes 批量创建节点
func (r *SimpleNodeRepository) BatchCreateNodes(ctx context.Context, nodes []repositories.NodeData) ([]string, error) {
	var ids []string

	for _, node := range nodes {
		id, err := r.CreateNode(ctx, node.Name, node.Category, node.Properties)
		if err != nil {
			return ids, err
		}
		ids = append(ids, id)
	}

	r.logger.Info("Batch created nodes", zap.Int("count", len(ids)))
	return ids, nil
}

// GetNodeByID 通过ID获取节点
func (r *SimpleNodeRepository) GetNodeByID(ctx context.Context, id string) (map[string]interface{}, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	node, exists := r.nodes[id]
	if !exists {
		return nil, fmt.Errorf("node not found: %s", id)
	}

	return node, nil
}

// GetNodeByName 根据名称获取节点
func (r *SimpleNodeRepository) GetNodeByName(ctx context.Context, name string) (map[string]interface{}, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	for _, node := range r.nodes {
		if nodeName, ok := node["name"].(string); ok && nodeName == name {
			return node, nil
		}
	}

	return nil, fmt.Errorf("node not found with name: %s", name)
}

// QueryNodes 查询节点
func (r *SimpleNodeRepository) QueryNodes(ctx context.Context, params map[string]interface{}, limit, offset int) ([]map[string]interface{}, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var results []map[string]interface{}
	var count int
	for _, node := range r.nodes {
		match := true
		for key, value := range params {
			nodeValue, exists := node[key]
			if !exists || nodeValue != value {
				match = false
				break
			}
		}
		if match {
			// 应用偏移
			if count >= offset {
				results = append(results, node)
			}
			count++
			// 应用限制
			if len(results) >= limit && limit > 0 {
				break
			}
		}
	}

	return results, nil
}

// UpdateNode 更新节点
func (r *SimpleNodeRepository) UpdateNode(ctx context.Context, id string, properties map[string]interface{}) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	node, exists := r.nodes[id]
	if !exists {
		return fmt.Errorf("node not found: %s", id)
	}

	// 更新属性
	nodeProps, ok := node["properties"].(map[string]interface{})
	if !ok {
		nodeProps = make(map[string]interface{})
	}
	for k, v := range properties {
		nodeProps[k] = v
	}
	node["properties"] = nodeProps
	node["updated_at"] = time.Now()

	return nil
}

// DeleteNode 删除节点
func (r *SimpleNodeRepository) DeleteNode(ctx context.Context, id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, exists := r.nodes[id]; !exists {
		return fmt.Errorf("node not found: %s", id)
	}

	delete(r.nodes, id)
	return nil
}

// DeleteAllNodes 删除所有节点
func (r *SimpleNodeRepository) DeleteAllNodes(ctx context.Context) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.nodes = make(map[string]map[string]interface{})
	return nil
}

// SaveVector 保存向量
func (r *SimpleNodeRepository) SaveVector(ctx context.Context, id string, vector []float64) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	node, exists := r.nodes[id]
	if !exists {
		return fmt.Errorf("node not found: %s", id)
	}

	node["vector"] = vector
	return nil
}

// QuerySimilarNodes 查询相似节点
func (r *SimpleNodeRepository) QuerySimilarNodes(ctx context.Context, vector []float64, limit int) ([]map[string]interface{}, error) {
	// 简单实现，返回所有节点（实际应用中需要实现向量相似度计算）
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []map[string]interface{}
	for _, node := range r.nodes {
		result = append(result, node)
		if len(result) >= limit {
			break
		}
	}

	return result, nil
}

// GetNodeCount 获取节点数量
func (r *SimpleNodeRepository) GetNodeCount(ctx context.Context) (int64, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	return int64(len(r.nodes)), nil
}

// GetRelatedNodes 获取相关节点
func (r *SimpleNodeRepository) GetRelatedNodes(ctx context.Context, id string, relationshipType string, limit int) ([]map[string]interface{}, error) {
	// 简单实现，仅用于测试，返回空数组
	return []map[string]interface{}{}, nil
}

// GetNodesByCategory 根据类别获取节点
func (r *SimpleNodeRepository) GetNodesByCategory(ctx context.Context, category string, limit int, offset int) ([]map[string]interface{}, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var results []map[string]interface{}
	for _, node := range r.nodes {
		if cat, ok := node["category"].(string); ok && cat == category {
			results = append(results, node)
		}
	}

	// 应用分页
	if offset >= len(results) {
		return []map[string]interface{}{}, nil
	}

	end := offset + limit
	if end > len(results) || limit <= 0 {
		end = len(results)
	}

	return results[offset:end], nil
}

// SearchNodes 搜索节点
func (r *SimpleNodeRepository) SearchNodes(ctx context.Context, query string, limit int) ([]map[string]interface{}, error) {
	// 简单实现，只根据名称匹配
	r.mu.RLock()
	defer r.mu.RUnlock()

	var results []map[string]interface{}
	for _, node := range r.nodes {
		if name, ok := node["name"].(string); ok && (query == "" || name == query) {
			results = append(results, node)
			if len(results) >= limit && limit > 0 {
				break
			}
		}
	}

	return results, nil
}

// GetAllNodes 获取所有节点
func (r *SimpleNodeRepository) GetAllNodes(ctx context.Context, limit, offset int) ([]map[string]interface{}, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []map[string]interface{}
	for _, node := range r.nodes {
		result = append(result, node)
	}

	// 应用分页
	if offset >= len(result) {
		return []map[string]interface{}{}, nil
	}

	end := offset + limit
	if end > len(result) || limit <= 0 {
		end = len(result)
	}

	return result[offset:end], nil
}

// GetByName 通过名称获取节点
func (r *SimpleNodeRepository) GetByName(ctx context.Context, name string) ([]map[string]interface{}, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []map[string]interface{}
	for _, node := range r.nodes {
		if nodeName, ok := node["name"].(string); ok && nodeName == name {
			result = append(result, node)
		}
	}

	return result, nil
}

// GetNodesByProperty 通过属性获取节点
func (r *SimpleNodeRepository) GetNodesByProperty(ctx context.Context, propertyName string, propertyValue interface{}, limit, offset int) ([]map[string]interface{}, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []map[string]interface{}
	for _, node := range r.nodes {
		if props, ok := node["properties"].(map[string]interface{}); ok {
			if val, exists := props[propertyName]; exists && val == propertyValue {
				result = append(result, node)
			}
		}
	}

	// 应用分页
	if offset >= len(result) {
		return []map[string]interface{}{}, nil
	}

	end := offset + limit
	if end > len(result) || limit <= 0 {
		end = len(result)
	}

	return result[offset:end], nil
}

// GetNodesByVector 通过向量相似度获取节点
func (r *SimpleNodeRepository) GetNodesByVector(ctx context.Context, vector []float32, limit int) ([]map[string]interface{}, error) {
	// 简单实现，返回所有节点
	return r.GetAllNodes(ctx, limit, 0)
}

// UpdateNodeVector 更新节点向量
func (r *SimpleNodeRepository) UpdateNodeVector(ctx context.Context, id string, vector []float32) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	node, exists := r.nodes[id]
	if !exists {
		return fmt.Errorf("node not found: %s", id)
	}

	node["vector"] = vector
	return nil
}

// SimpleRelationshipRepository 简单的关系存储库实现，用于测试
type SimpleRelationshipRepository struct {
	relationships map[string]map[string]interface{}
	mu            sync.RWMutex
	logger        *zap.Logger
}

// NewSimpleRelationshipRepository 创建一个新的简单关系存储库
func NewSimpleRelationshipRepository(logger *zap.Logger) repositories.RelationshipRepository {
	if logger == nil {
		logger = zap.NewNop()
	}

	return &SimpleRelationshipRepository{
		relationships: make(map[string]map[string]interface{}),
		logger:        logger,
	}
}

// CreateRelationship 创建关系
func (r *SimpleRelationshipRepository) CreateRelationship(
	ctx context.Context,
	sourceID string,
	targetID string,
	relType repositories.RelationshipType,
	properties map[string]interface{},
) (string, error) {
	r.mu.Lock()
	defer r.mu.Unlock()

	// 生成简单ID
	id := fmt.Sprintf("rel-%s-%s-%s-%d", sourceID, targetID, relType, time.Now().UnixNano())

	// 创建关系数据
	relData := map[string]interface{}{
		"id":          id,
		"source_id":   sourceID,
		"target_id":   targetID,
		"type":        relType,
		"properties":  properties,
		"created_at":  time.Now(),
		"updated_at":  time.Now(),
	}

	// 存储关系
	r.relationships[id] = relData
	r.logger.Info("Created relationship", zap.String("id", id), zap.String("type", string(relType)))

	return id, nil
}

// BatchCreateRelationships 批量创建关系
func (r *SimpleRelationshipRepository) BatchCreateRelationships(
	ctx context.Context,
	relationships []repositories.RelationshipData,
) ([]string, error) {
	var ids []string

	for _, rel := range relationships {
		id, err := r.CreateRelationship(ctx, rel.SourceID, rel.TargetID, rel.Type, rel.Properties)
		if err != nil {
			return ids, err
		}
		ids = append(ids, id)
	}

	r.logger.Info("Batch created relationships", zap.Int("count", len(ids)))
	return ids, nil
}

// 定义一个简单的关系实现
type SimpleRelationship struct {
	ID         string
	SourceID   string
	TargetID   string
	Type       repositories.RelationshipType
	Properties map[string]interface{}
}

// GetID 获取关系ID
func (r *SimpleRelationship) GetID() string {
	return r.ID
}

// GetSourceID 获取源节点ID
func (r *SimpleRelationship) GetSourceID() string {
	return r.SourceID
}

// GetTargetID 获取目标节点ID
func (r *SimpleRelationship) GetTargetID() string {
	return r.TargetID
}

// GetType 获取关系类型
func (r *SimpleRelationship) GetType() repositories.RelationshipType {
	return r.Type
}

// GetProperties 获取所有属性
func (r *SimpleRelationship) GetProperties() map[string]interface{} {
	return r.Properties
}

// GetProperty 获取单个属性
func (r *SimpleRelationship) GetProperty(key string) (interface{}, bool) {
	val, ok := r.Properties[key]
	return val, ok
}

// GetRelationshipByID 通过ID获取关系
func (r *SimpleRelationshipRepository) GetRelationshipByID(ctx context.Context, id string) (repositories.Relationship, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	relData, ok := r.relationships[id]
	if !ok {
		return nil, fmt.Errorf("relationship not found: %s", id)
	}

	rel := &SimpleRelationship{
		ID:       id,
		SourceID: relData["source_id"].(string),
		TargetID: relData["target_id"].(string),
		Type:     relData["type"].(repositories.RelationshipType),
	}

	if props, ok := relData["properties"].(map[string]interface{}); ok {
		rel.Properties = props
	} else {
		rel.Properties = make(map[string]interface{})
	}

	return rel, nil
}

// GetRelationshipsBySourceID 通过源节点ID获取关系
func (r *SimpleRelationshipRepository) GetRelationshipsBySourceID(ctx context.Context, sourceID string, relType repositories.RelationshipType) ([]repositories.Relationship, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []repositories.Relationship
	
	for id, relData := range r.relationships {
		srcID, ok := relData["source_id"].(string)
		if !ok || srcID != sourceID {
			continue
		}

		rType, ok := relData["type"].(repositories.RelationshipType)
		if !ok || (relType != "" && rType != relType) {
			continue
		}

		rel, err := r.GetRelationshipByID(ctx, id)
		if err != nil {
			continue
		}

		result = append(result, rel)
	}

	return result, nil
}

// GetRelationshipsByTargetID 通过目标节点ID获取关系
func (r *SimpleRelationshipRepository) GetRelationshipsByTargetID(ctx context.Context, targetID string, relType repositories.RelationshipType) ([]repositories.Relationship, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []repositories.Relationship
	
	for id, relData := range r.relationships {
		tgtID, ok := relData["target_id"].(string)
		if !ok || tgtID != targetID {
			continue
		}

		rType, ok := relData["type"].(repositories.RelationshipType)
		if !ok || (relType != "" && rType != relType) {
			continue
		}

		rel, err := r.GetRelationshipByID(ctx, id)
		if err != nil {
			continue
		}

		result = append(result, rel)
	}

	return result, nil
}

// GetRelationshipsByType 通过关系类型获取关系
func (r *SimpleRelationshipRepository) GetRelationshipsByType(ctx context.Context, relType repositories.RelationshipType, limit, offset int) ([]repositories.Relationship, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var result []repositories.Relationship
	
	for id, relData := range r.relationships {
		rType, ok := relData["type"].(repositories.RelationshipType)
		if !ok || rType != relType {
			continue
		}

		rel, err := r.GetRelationshipByID(ctx, id)
		if err != nil {
			continue
		}

		result = append(result, rel)
	}

	// 应用分页
	if offset >= len(result) {
		return []repositories.Relationship{}, nil
	}

	end := offset + limit
	if end > len(result) || limit <= 0 {
		end = len(result)
	}

	return result[offset:end], nil
}

// UpdateRelationship 更新关系
func (r *SimpleRelationshipRepository) UpdateRelationship(ctx context.Context, id string, properties map[string]interface{}) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	rel, exists := r.relationships[id]
	if !exists {
		return fmt.Errorf("relationship not found: %s", id)
	}

	// 更新属性
	relProps, ok := rel["properties"].(map[string]interface{})
	if !ok {
		relProps = make(map[string]interface{})
	}
	for k, v := range properties {
		relProps[k] = v
	}
	rel["properties"] = relProps
	rel["updated_at"] = time.Now()

	return nil
}

// DeleteRelationship 删除关系
func (r *SimpleRelationshipRepository) DeleteRelationship(ctx context.Context, id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, exists := r.relationships[id]; !exists {
		return fmt.Errorf("relationship not found: %s", id)
	}

	delete(r.relationships, id)
	return nil
}

// DeleteRelationshipsBetweenNodes 删除节点间关系
func (r *SimpleRelationshipRepository) DeleteRelationshipsBetweenNodes(ctx context.Context, sourceID, targetID string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	var toDelete []string
	for id, rel := range r.relationships {
		srcID, srcOK := rel["source_id"].(string)
		tgtID, tgtOK := rel["target_id"].(string)
		if srcOK && tgtOK && srcID == sourceID && tgtID == targetID {
			toDelete = append(toDelete, id)
		}
	}

	for _, id := range toDelete {
		delete(r.relationships, id)
	}

	return nil
}

// DeleteAllRelationships 删除所有关系
func (r *SimpleRelationshipRepository) DeleteAllRelationships(ctx context.Context) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.relationships = make(map[string]map[string]interface{})
	return nil
}
