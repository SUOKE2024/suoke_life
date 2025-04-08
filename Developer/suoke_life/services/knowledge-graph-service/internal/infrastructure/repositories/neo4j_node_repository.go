package repositories

import (
	"context"
	"fmt"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"go.uber.org/zap"

	"knowledge-graph-service/internal/domain/repositories"
)

// Neo4jNodeRepository Neo4j节点仓库实现
type Neo4jNodeRepository struct {
	driver neo4j.DriverWithContext
	logger *zap.Logger
}

// NewNeo4jNodeRepository 创建Neo4j节点仓库
func NewNeo4jNodeRepository(driver neo4j.DriverWithContext, logger *zap.Logger) repositories.NodeRepository {
	return &Neo4jNodeRepository{
		driver: driver,
		logger: logger,
	}
}

// GetNode 通过ID获取节点
func (r *Neo4jNodeRepository) GetNode(ctx context.Context, id string) (map[string]interface{}, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	query := `
		MATCH (n)
		WHERE id(n) = $id OR n.id = $id
		RETURN n
	`
	result, err := session.Run(ctx, query, map[string]interface{}{"id": id})
	if err != nil {
		r.logger.Error("Failed to execute query", zap.Error(err), zap.String("id", id))
		return nil, fmt.Errorf("执行查询失败: %w", err)
	}

	if result.Next(ctx) {
		record := result.Record()
		nodeValue, found := record.Get("n")
		if !found {
			return nil, fmt.Errorf("未能从记录中获取节点")
		}

		node, ok := nodeValue.(neo4j.Node)
		if !ok {
			return nil, fmt.Errorf("无法转换为Neo4j节点")
		}

		return mapNodeToMap(node), nil
	}

	return nil, fmt.Errorf("未找到ID为 %s 的节点", id)
}

// GetNodes 通过ID列表获取多个节点
func (r *Neo4jNodeRepository) GetNodes(ctx context.Context, ids []string) ([]map[string]interface{}, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	query := `
		MATCH (n)
		WHERE n.id IN $ids
		RETURN n
	`
	result, err := session.Run(ctx, query, map[string]interface{}{"ids": ids})
	if err != nil {
		r.logger.Error("Failed to execute query", zap.Error(err), zap.Strings("ids", ids))
		return nil, fmt.Errorf("执行查询失败: %w", err)
	}

	nodes := make([]map[string]interface{}, 0)
	for result.Next(ctx) {
		record := result.Record()
		nodeValue, found := record.Get("n")
		if !found {
			continue
		}

		node, ok := nodeValue.(neo4j.Node)
		if !ok {
			continue
		}

		nodes = append(nodes, mapNodeToMap(node))
	}

	return nodes, nil
}

// GetNodesByProperty 通过属性获取节点
func (r *Neo4jNodeRepository) GetNodesByProperty(ctx context.Context, property string, value interface{}) ([]map[string]interface{}, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	query := fmt.Sprintf(`
		MATCH (n)
		WHERE n.%s = $value
		RETURN n
	`, property)
	
	result, err := session.Run(ctx, query, map[string]interface{}{"value": value})
	if err != nil {
		r.logger.Error("Failed to execute query", zap.Error(err), zap.String("property", property))
		return nil, fmt.Errorf("执行查询失败: %w", err)
	}

	nodes := make([]map[string]interface{}, 0)
	for result.Next(ctx) {
		record := result.Record()
		nodeValue, found := record.Get("n")
		if !found {
			continue
		}

		node, ok := nodeValue.(neo4j.Node)
		if !ok {
			continue
		}

		nodes = append(nodes, mapNodeToMap(node))
	}

	return nodes, nil
}

// GetNodesByCategory 通过分类获取节点，支持分页
func (r *Neo4jNodeRepository) GetNodesByCategory(ctx context.Context, category string, limit, offset int) ([]map[string]interface{}, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	if limit <= 0 {
		limit = 10
	}

	query := `
		MATCH (n)
		WHERE n.category = $category
		RETURN n
		ORDER BY n.name
		SKIP $offset
		LIMIT $limit
	`
	
	result, err := session.Run(ctx, query, map[string]interface{}{
		"category": category,
		"limit": limit,
		"offset": offset,
	})
	if err != nil {
		r.logger.Error("Failed to execute query", zap.Error(err), zap.String("category", category))
		return nil, fmt.Errorf("执行查询失败: %w", err)
	}

	nodes := make([]map[string]interface{}, 0)
	for result.Next(ctx) {
		record := result.Record()
		nodeValue, found := record.Get("n")
		if !found {
			continue
		}

		node, ok := nodeValue.(neo4j.Node)
		if !ok {
			continue
		}

		nodes = append(nodes, mapNodeToMap(node))
	}

	return nodes, nil
}

// CreateNode 创建新节点
func (r *Neo4jNodeRepository) CreateNode(ctx context.Context, nodeData map[string]interface{}) (string, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

	// 提取标签(等同于neo4j中的节点类型)
	var labels []string
	if labelValue, exists := nodeData["labels"]; exists {
		if labelsArray, ok := labelValue.([]string); ok {
			labels = labelsArray
			delete(nodeData, "labels") // 从属性中移除标签
		}
	}

	if len(labels) == 0 {
		// 如果没有指定标签，使用默认标签
		if category, exists := nodeData["category"]; exists {
			if categoryStr, ok := category.(string); ok {
				labels = []string{categoryStr}
			}
		}
		if len(labels) == 0 {
			labels = []string{"Node"}
		}
	}

	// 构建创建语句
	labelsStr := ""
	for i, label := range labels {
		if i > 0 {
			labelsStr += ":"
		}
		labelsStr += label
	}

	query := fmt.Sprintf(`
		CREATE (n:%s $props)
		RETURN n, id(n) as id
	`, labelsStr)

	result, err := session.Run(ctx, query, map[string]interface{}{
		"props": nodeData,
	})
	if err != nil {
		r.logger.Error("Failed to create node", zap.Error(err))
		return "", fmt.Errorf("创建节点失败: %w", err)
	}

	if result.Next(ctx) {
		record := result.Record()
		idValue, found := record.Get("id")
		if !found {
			return "", fmt.Errorf("创建节点后未能获取ID")
		}

		id, ok := idValue.(int64)
		if !ok {
			return "", fmt.Errorf("无法将节点ID转换为整数")
		}

		return fmt.Sprintf("%d", id), nil
	}

	return "", fmt.Errorf("创建节点失败，无返回结果")
}

// BatchCreateNodes 批量创建节点
func (r *Neo4jNodeRepository) BatchCreateNodes(ctx context.Context, nodes []map[string]interface{}) ([]string, error) {
	// 为简化实现，这里逐个调用CreateNode
	ids := make([]string, 0, len(nodes))
	for _, node := range nodes {
		id, err := r.CreateNode(ctx, node)
		if err != nil {
			r.logger.Error("Failed to create node in batch", zap.Error(err))
			return ids, err
		}
		ids = append(ids, id)
	}
	return ids, nil
}

// UpdateNode 更新节点属性
func (r *Neo4jNodeRepository) UpdateNode(ctx context.Context, id string, nodeData map[string]interface{}) error {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

	query := `
		MATCH (n)
		WHERE id(n) = $id OR n.id = $id
		SET n += $props
		RETURN n
	`

	result, err := session.Run(ctx, query, map[string]interface{}{
		"id": id,
		"props": nodeData,
	})
	if err != nil {
		r.logger.Error("Failed to update node", zap.Error(err), zap.String("id", id))
		return fmt.Errorf("更新节点失败: %w", err)
	}

	if !result.Next(ctx) {
		return fmt.Errorf("未找到ID为 %s 的节点", id)
	}

	return nil
}

// DeleteNode 删除节点
func (r *Neo4jNodeRepository) DeleteNode(ctx context.Context, id string) error {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

	query := `
		MATCH (n)
		WHERE id(n) = $id OR n.id = $id
		DETACH DELETE n
		RETURN count(n) as count
	`

	result, err := session.Run(ctx, query, map[string]interface{}{
		"id": id,
	})
	if err != nil {
		r.logger.Error("Failed to delete node", zap.Error(err), zap.String("id", id))
		return fmt.Errorf("删除节点失败: %w", err)
	}

	if result.Next(ctx) {
		record := result.Record()
		countValue, found := record.Get("count")
		if !found {
			return fmt.Errorf("删除节点后未能获取计数")
		}

		count, ok := countValue.(int64)
		if !ok {
			return fmt.Errorf("无法将节点计数转换为整数")
		}

		if count == 0 {
			return fmt.Errorf("未找到ID为 %s 的节点", id)
		}
	}

	return nil
}

// QueryNodes 执行自定义查询
func (r *Neo4jNodeRepository) QueryNodes(ctx context.Context, query string, params map[string]interface{}, limit, offset int) ([]map[string]interface{}, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	if params == nil {
		params = map[string]interface{}{}
	}

	// 如果查询不包含LIMIT和SKIP子句，添加它们
	if limit > 0 {
		if offset > 0 {
			query = fmt.Sprintf("%s SKIP %d LIMIT %d", query, offset, limit)
		} else {
			query = fmt.Sprintf("%s LIMIT %d", query, limit)
		}
	}

	result, err := session.Run(ctx, query, params)
	if err != nil {
		r.logger.Error("Failed to execute custom query", zap.Error(err), zap.String("query", query))
		return nil, fmt.Errorf("执行自定义查询失败: %w", err)
	}

	nodes := make([]map[string]interface{}, 0)
	for result.Next(ctx) {
		record := result.Record()
		recordMap := make(map[string]interface{})

		for _, key := range record.Keys {
			value, _ := record.Get(key)
			
			// 如果值是Neo4j节点，转换为Map
			if node, ok := value.(neo4j.Node); ok {
				recordMap[key] = mapNodeToMap(node)
			} else {
				recordMap[key] = value
			}
		}

		nodes = append(nodes, recordMap)
	}

	return nodes, nil
}

// CountNodesByCategory 统计指定分类的节点数
func (r *Neo4jNodeRepository) CountNodesByCategory(ctx context.Context, category string) (int64, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	query := `
		MATCH (n)
		WHERE n.category = $category
		RETURN count(n) as count
	`

	result, err := session.Run(ctx, query, map[string]interface{}{
		"category": category,
	})
	if err != nil {
		r.logger.Error("Failed to count nodes", zap.Error(err), zap.String("category", category))
		return 0, fmt.Errorf("统计节点失败: %w", err)
	}

	if result.Next(ctx) {
		record := result.Record()
		countValue, found := record.Get("count")
		if !found {
			return 0, fmt.Errorf("统计节点后未能获取计数")
		}

		count, ok := countValue.(int64)
		if !ok {
			return 0, fmt.Errorf("无法将节点计数转换为整数")
		}

		return count, nil
	}

	return 0, nil
}

// mapNodeToMap 将Neo4j节点转换为Map
func mapNodeToMap(node neo4j.Node) map[string]interface{} {
	result := make(map[string]interface{})
	
	// 添加ID
	result["id"] = node.ElementId
	
	// 添加所有属性
	for key, value := range node.Props {
		result[key] = value
	}
	
	// 添加标签
	labels := node.Labels
	if len(labels) > 0 {
		result["labels"] = labels
	}
	
	return result
} 