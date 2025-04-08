package repositories

import (
	"context"
	"fmt"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"go.uber.org/zap"

	"knowledge-graph-service/internal/domain/repositories"
)

// Neo4jRelationshipRepository Neo4j关系仓库实现
type Neo4jRelationshipRepository struct {
	driver neo4j.DriverWithContext
	logger *zap.Logger
}

// NewNeo4jRelationshipRepository 创建Neo4j关系仓库
func NewNeo4jRelationshipRepository(driver neo4j.DriverWithContext, logger *zap.Logger) repositories.RelationshipRepository {
	return &Neo4jRelationshipRepository{
		driver: driver,
		logger: logger,
	}
}

// CreateRelationship 创建关系
func (r *Neo4jRelationshipRepository) CreateRelationship(ctx context.Context, sourceNodeId, targetNodeId string, relType repositories.RelationshipType, properties map[string]interface{}) (string, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

	if properties == nil {
		properties = map[string]interface{}{}
	}

	query := `
		MATCH (source), (target)
		WHERE (id(source) = $sourceId OR source.id = $sourceId) AND (id(target) = $targetId OR target.id = $targetId)
		CREATE (source)-[r:` + string(relType) + ` $props]->(target)
		RETURN r, id(r) as id
	`

	result, err := session.Run(ctx, query, map[string]interface{}{
		"sourceId": sourceNodeId,
		"targetId": targetNodeId,
		"props":    properties,
	})
	if err != nil {
		r.logger.Error("Failed to create relationship", 
			zap.Error(err), 
			zap.String("sourceNodeId", sourceNodeId), 
			zap.String("targetNodeId", targetNodeId), 
			zap.String("relType", string(relType)))
		return "", fmt.Errorf("创建关系失败: %w", err)
	}

	if result.Next(ctx) {
		record := result.Record()
		idValue, found := record.Get("id")
		if !found {
			return "", fmt.Errorf("创建关系后未能获取ID")
		}

		id, ok := idValue.(int64)
		if !ok {
			return "", fmt.Errorf("无法将关系ID转换为整数")
		}

		return fmt.Sprintf("%d", id), nil
	}

	return "", fmt.Errorf("创建关系失败，未能找到源节点或目标节点")
}

// CreateBidirectionalRelationship 创建双向关系
func (r *Neo4jRelationshipRepository) CreateBidirectionalRelationship(ctx context.Context, sourceNodeId, targetNodeId string, sourceToTargetType, targetToSourceType repositories.RelationshipType, properties map[string]interface{}) ([]string, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

	if properties == nil {
		properties = map[string]interface{}{}
	}

	// 创建从源到目标的关系
	sourceToTargetId, err := r.CreateRelationship(ctx, sourceNodeId, targetNodeId, sourceToTargetType, properties)
	if err != nil {
		return nil, err
	}

	// 创建从目标到源的关系
	targetToSourceId, err := r.CreateRelationship(ctx, targetNodeId, sourceNodeId, targetToSourceType, properties)
	if err != nil {
		// 如果创建反向关系失败，尝试删除已创建的正向关系
		_ = r.DeleteRelationship(ctx, sourceToTargetId)
		return nil, err
	}

	return []string{sourceToTargetId, targetToSourceId}, nil
}

// GetRelationship 获取关系
func (r *Neo4jRelationshipRepository) GetRelationship(ctx context.Context, id string) (map[string]interface{}, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	query := `
		MATCH ()-[r]->()
		WHERE id(r) = $id OR r.id = $id
		RETURN r, type(r) as type, id(r) as id, startNode(r) as source, endNode(r) as target
	`

	result, err := session.Run(ctx, query, map[string]interface{}{
		"id": id,
	})
	if err != nil {
		r.logger.Error("Failed to get relationship", zap.Error(err), zap.String("id", id))
		return nil, fmt.Errorf("获取关系失败: %w", err)
	}

	if result.Next(ctx) {
		record := result.Record()
		relMap := make(map[string]interface{})

		// 处理关系ID
		idValue, found := record.Get("id")
		if found {
			relMap["id"] = idValue
		}

		// 处理关系类型
		typeValue, found := record.Get("type")
		if found {
			relMap["type"] = typeValue
		}

		// 处理关系对象
		relValue, found := record.Get("r")
		if found {
			rel, ok := relValue.(neo4j.Relationship)
			if ok {
				// 添加所有属性
				for key, value := range rel.Props {
					relMap[key] = value
				}
				// 使用Type属性而不是Type()方法
				relMap["type"] = rel.Type
			}
		}

		// 处理源节点和目标节点
		sourceValue, sourceFound := record.Get("source")
		targetValue, targetFound := record.Get("target")
		
		if sourceFound {
			source, ok := sourceValue.(neo4j.Node)
			if ok {
				relMap["source"] = mapNodeToMap(source)
			}
		}
		
		if targetFound {
			target, ok := targetValue.(neo4j.Node)
			if ok {
				relMap["target"] = mapNodeToMap(target)
			}
		}

		return relMap, nil
	}

	return nil, fmt.Errorf("未找到ID为 %s 的关系", id)
}

// GetNodeRelationships 获取节点的所有关系
func (r *Neo4jRelationshipRepository) GetNodeRelationships(ctx context.Context, nodeId string, direction string, types []repositories.RelationshipType) ([]map[string]interface{}, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	var query string
	typesClause := ""
	
	// 处理关系类型过滤
	if len(types) > 0 {
		typesStrings := make([]string, len(types))
		for i, t := range types {
			typesStrings[i] = string(t)
		}
		typesClause = "WHERE type(r) IN $types"
	}

	// 根据方向构建查询
	switch direction {
	case "outgoing":
		query = `
			MATCH (n)-[r]->()
			WHERE id(n) = $nodeId OR n.id = $nodeId
			` + typesClause + `
			RETURN r, type(r) as type, id(r) as id, startNode(r) as source, endNode(r) as target
		`
	case "incoming":
		query = `
			MATCH (n)<-[r]-()
			WHERE id(n) = $nodeId OR n.id = $nodeId
			` + typesClause + `
			RETURN r, type(r) as type, id(r) as id, startNode(r) as source, endNode(r) as target
		`
	default: // both
		query = `
			MATCH (n)-[r]-()
			WHERE id(n) = $nodeId OR n.id = $nodeId
			` + typesClause + `
			RETURN r, type(r) as type, id(r) as id, startNode(r) as source, endNode(r) as target
		`
	}

	params := map[string]interface{}{
		"nodeId": nodeId,
	}
	
	if len(types) > 0 {
		typesStrings := make([]string, len(types))
		for i, t := range types {
			typesStrings[i] = string(t)
		}
		params["types"] = typesStrings
	}

	result, err := session.Run(ctx, query, params)
	if err != nil {
		r.logger.Error("Failed to get node relationships", 
			zap.Error(err), 
			zap.String("nodeId", nodeId), 
			zap.String("direction", direction))
		return nil, fmt.Errorf("获取节点关系失败: %w", err)
	}

	relationships := make([]map[string]interface{}, 0)
	for result.Next(ctx) {
		record := result.Record()
		relMap := make(map[string]interface{})

		// 处理关系ID
		idValue, found := record.Get("id")
		if found {
			relMap["id"] = idValue
		}

		// 处理关系类型
		typeValue, found := record.Get("type")
		if found {
			relMap["type"] = typeValue
		}

		// 处理关系对象
		relValue, found := record.Get("r")
		if found {
			rel, ok := relValue.(neo4j.Relationship)
			if ok {
				// 添加所有属性
				for key, value := range rel.Props {
					relMap[key] = value
				}
				// 使用Type属性而不是Type()方法
				relMap["type"] = rel.Type
			}
		}

		// 处理源节点和目标节点
		sourceValue, sourceFound := record.Get("source")
		targetValue, targetFound := record.Get("target")
		
		if sourceFound {
			source, ok := sourceValue.(neo4j.Node)
			if ok {
				relMap["source"] = mapNodeToMap(source)
			}
		}
		
		if targetFound {
			target, ok := targetValue.(neo4j.Node)
			if ok {
				relMap["target"] = mapNodeToMap(target)
			}
		}

		relationships = append(relationships, relMap)
	}

	return relationships, nil
}

// GetRelationshipsBetweenNodes 获取两个节点之间的关系
func (r *Neo4jRelationshipRepository) GetRelationshipsBetweenNodes(ctx context.Context, sourceNodeId, targetNodeId string, types []repositories.RelationshipType) ([]map[string]interface{}, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	typesClause := ""
	if len(types) > 0 {
		typesStrings := make([]string, len(types))
		for i, t := range types {
			typesStrings[i] = string(t)
		}
		typesClause = "WHERE type(r) IN $types"
	}

	query := `
		MATCH (source)-[r]->(target)
		WHERE (id(source) = $sourceId OR source.id = $sourceId) AND (id(target) = $targetId OR target.id = $targetId)
		` + typesClause + `
		RETURN r, type(r) as type, id(r) as id, source, target
	`

	params := map[string]interface{}{
		"sourceId": sourceNodeId,
		"targetId": targetNodeId,
	}
	
	if len(types) > 0 {
		typesStrings := make([]string, len(types))
		for i, t := range types {
			typesStrings[i] = string(t)
		}
		params["types"] = typesStrings
	}

	result, err := session.Run(ctx, query, params)
	if err != nil {
		r.logger.Error("Failed to get relationships between nodes", 
			zap.Error(err), 
			zap.String("sourceNodeId", sourceNodeId), 
			zap.String("targetNodeId", targetNodeId))
		return nil, fmt.Errorf("获取节点间关系失败: %w", err)
	}

	relationships := make([]map[string]interface{}, 0)
	for result.Next(ctx) {
		record := result.Record()
		relMap := make(map[string]interface{})

		// 处理关系ID
		idValue, found := record.Get("id")
		if found {
			relMap["id"] = idValue
		}

		// 处理关系类型
		typeValue, found := record.Get("type")
		if found {
			relMap["type"] = typeValue
		}

		// 处理关系对象
		relValue, found := record.Get("r")
		if found {
			rel, ok := relValue.(neo4j.Relationship)
			if ok {
				// 添加所有属性
				for key, value := range rel.Props {
					relMap[key] = value
				}
				// 使用Type属性而不是Type()方法
				relMap["type"] = rel.Type
			}
		}

		// 处理源节点和目标节点
		sourceValue, sourceFound := record.Get("source")
		targetValue, targetFound := record.Get("target")
		
		if sourceFound {
			source, ok := sourceValue.(neo4j.Node)
			if ok {
				relMap["source"] = mapNodeToMap(source)
			}
		}
		
		if targetFound {
			target, ok := targetValue.(neo4j.Node)
			if ok {
				relMap["target"] = mapNodeToMap(target)
			}
		}

		relationships = append(relationships, relMap)
	}

	return relationships, nil
}

// UpdateRelationship 更新关系属性
func (r *Neo4jRelationshipRepository) UpdateRelationship(ctx context.Context, id string, properties map[string]interface{}) error {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

	query := `
		MATCH ()-[r]->()
		WHERE id(r) = $id OR r.id = $id
		SET r += $props
		RETURN r
	`

	result, err := session.Run(ctx, query, map[string]interface{}{
		"id":    id,
		"props": properties,
	})
	if err != nil {
		r.logger.Error("Failed to update relationship", zap.Error(err), zap.String("id", id))
		return fmt.Errorf("更新关系失败: %w", err)
	}

	if !result.Next(ctx) {
		return fmt.Errorf("未找到ID为 %s 的关系", id)
	}

	return nil
}

// DeleteRelationship 删除关系
func (r *Neo4jRelationshipRepository) DeleteRelationship(ctx context.Context, id string) error {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

	query := `
		MATCH ()-[r]->()
		WHERE id(r) = $id OR r.id = $id
		DELETE r
		RETURN count(r) as count
	`

	result, err := session.Run(ctx, query, map[string]interface{}{
		"id": id,
	})
	if err != nil {
		r.logger.Error("Failed to delete relationship", zap.Error(err), zap.String("id", id))
		return fmt.Errorf("删除关系失败: %w", err)
	}

	if result.Next(ctx) {
		record := result.Record()
		countValue, found := record.Get("count")
		if !found {
			return fmt.Errorf("删除关系后未能获取计数")
		}

		count, ok := countValue.(int64)
		if !ok {
			return fmt.Errorf("无法将关系计数转换为整数")
		}

		if count == 0 {
			return fmt.Errorf("未找到ID为 %s 的关系", id)
		}
	}

	return nil
}

// DeleteRelationshipsBetweenNodes 删除两个节点之间的关系
func (r *Neo4jRelationshipRepository) DeleteRelationshipsBetweenNodes(ctx context.Context, sourceNodeId, targetNodeId string, types []repositories.RelationshipType) (int, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeWrite})
	defer session.Close(ctx)

	typesClause := ""
	if len(types) > 0 {
		typesStrings := make([]string, len(types))
		for i, t := range types {
			typesStrings[i] = string(t)
		}
		typesClause = "WHERE type(r) IN $types"
	}

	query := `
		MATCH (source)-[r]->(target)
		WHERE (id(source) = $sourceId OR source.id = $sourceId) AND (id(target) = $targetId OR target.id = $targetId)
		` + typesClause + `
		DELETE r
		RETURN count(r) as count
	`

	params := map[string]interface{}{
		"sourceId": sourceNodeId,
		"targetId": targetNodeId,
	}
	
	if len(types) > 0 {
		typesStrings := make([]string, len(types))
		for i, t := range types {
			typesStrings[i] = string(t)
		}
		params["types"] = typesStrings
	}

	result, err := session.Run(ctx, query, params)
	if err != nil {
		r.logger.Error("Failed to delete relationships between nodes", 
			zap.Error(err), 
			zap.String("sourceNodeId", sourceNodeId), 
			zap.String("targetNodeId", targetNodeId))
		return 0, fmt.Errorf("删除节点间关系失败: %w", err)
	}

	count := int64(0)
	if result.Next(ctx) {
		record := result.Record()
		countValue, found := record.Get("count")
		if found {
			if countInt, ok := countValue.(int64); ok {
				count = countInt
			}
		}
	}

	return int(count), nil
}

// FindPaths 查找两个节点之间的路径
func (r *Neo4jRelationshipRepository) FindPaths(ctx context.Context, startNodeId, endNodeId string, maxDepth int) ([]map[string]interface{}, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	if maxDepth <= 0 {
		maxDepth = 3 // 默认最大深度
	}

	query := `
		MATCH path = shortestPath((start)-[*1..` + fmt.Sprintf("%d", maxDepth) + `]-(end))
		WHERE (id(start) = $startId OR start.id = $startId) AND (id(end) = $endId OR end.id = $endId)
		RETURN path, length(path) as length
		ORDER BY length ASC
		LIMIT 5
	`

	result, err := session.Run(ctx, query, map[string]interface{}{
		"startId": startNodeId,
		"endId":   endNodeId,
	})
	if err != nil {
		r.logger.Error("Failed to find paths", 
			zap.Error(err), 
			zap.String("startNodeId", startNodeId), 
			zap.String("endNodeId", endNodeId), 
			zap.Int("maxDepth", maxDepth))
		return nil, fmt.Errorf("查找路径失败: %w", err)
	}

	paths := make([]map[string]interface{}, 0)
	for result.Next(ctx) {
		record := result.Record()
		pathMap := make(map[string]interface{})

		// 处理路径长度
		lengthValue, found := record.Get("length")
		if found {
			pathMap["length"] = lengthValue
		}

		// 处理路径
		pathValue, found := record.Get("path")
		if found {
			path, ok := pathValue.(neo4j.Path)
			if ok {
				// 获取路径中的节点
				nodes := make([]map[string]interface{}, 0)
				for _, node := range path.Nodes {
					nodes = append(nodes, mapNodeToMap(node))
				}
				pathMap["nodes"] = nodes

				// 获取路径中的关系
				relationships := make([]map[string]interface{}, 0)
				for _, rel := range path.Relationships {
					relMap := make(map[string]interface{})
					relMap["id"] = rel.ElementId
					relMap["type"] = rel.Type
					
					// 添加关系的所有属性
					for key, value := range rel.Props {
						relMap[key] = value
					}
					
					relationships = append(relationships, relMap)
				}
				pathMap["relationships"] = relationships
			}
		}

		paths = append(paths, pathMap)
	}

	return paths, nil
}

// FindCommunities 查找社区
func (r *Neo4jRelationshipRepository) FindCommunities(ctx context.Context, nodeIds []string, algorithm string) ([]map[string]interface{}, error) {
	session := r.driver.NewSession(ctx, neo4j.SessionConfig{AccessMode: neo4j.AccessModeRead})
	defer session.Close(ctx)

	if algorithm == "" {
		algorithm = "louvain" // 默认使用Louvain算法
	}

	// 构建节点过滤条件
	nodeCondition := ""
	params := map[string]interface{}{}
	
	if len(nodeIds) > 0 {
		nodeCondition = "WHERE n.id IN $nodeIds"
		params["nodeIds"] = nodeIds
	}

	// 根据算法选择查询
	var query string
	switch algorithm {
	case "louvain":
		query = `
			CALL gds.louvain.stream({
				nodeQuery: "MATCH (n) " + $nodeCondition + " RETURN id(n) as id",
				relationshipQuery: "MATCH (n1)-[r]-(n2) RETURN id(n1) as source, id(n2) as target, count(r) as weight",
				relationshipWeightProperty: "weight"
			})
			YIELD nodeId, communityId
			WITH nodeId, communityId
			MATCH (n) WHERE id(n) = nodeId
			RETURN communityId, collect(n) as nodes, count(n) as size
			ORDER BY size DESC
		`
	case "labelPropagation":
		query = `
			CALL gds.labelPropagation.stream({
				nodeQuery: "MATCH (n) " + $nodeCondition + " RETURN id(n) as id",
				relationshipQuery: "MATCH (n1)-[r]-(n2) RETURN id(n1) as source, id(n2) as target"
			})
			YIELD nodeId, communityId
			WITH nodeId, communityId
			MATCH (n) WHERE id(n) = nodeId
			RETURN communityId, collect(n) as nodes, count(n) as size
			ORDER BY size DESC
		`
	default:
		return nil, fmt.Errorf("不支持的社区检测算法: %s", algorithm)
	}

	params["nodeCondition"] = nodeCondition

	result, err := session.Run(ctx, query, params)
	if err != nil {
		r.logger.Error("Failed to find communities", 
			zap.Error(err), 
			zap.Strings("nodeIds", nodeIds), 
			zap.String("algorithm", algorithm))
		return nil, fmt.Errorf("查找社区失败: %w", err)
	}

	communities := make([]map[string]interface{}, 0)
	for result.Next(ctx) {
		record := result.Record()
		communityMap := make(map[string]interface{})

		// 处理社区ID
		communityIdValue, found := record.Get("communityId")
		if found {
			communityMap["communityId"] = communityIdValue
		}

		// 处理社区大小
		sizeValue, found := record.Get("size")
		if found {
			communityMap["size"] = sizeValue
		}

		// 处理社区节点
		nodesValue, found := record.Get("nodes")
		if found {
			if nodesList, ok := nodesValue.([]interface{}); ok {
				nodes := make([]map[string]interface{}, 0)
				for _, nodeValue := range nodesList {
					if node, ok := nodeValue.(neo4j.Node); ok {
						nodes = append(nodes, mapNodeToMap(node))
					}
				}
				communityMap["nodes"] = nodes
			}
		}

		communities = append(communities, communityMap)
	}

	return communities, nil
} 