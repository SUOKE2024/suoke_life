package usecases

import (
	"context"
	"errors"
	"fmt"
	
	"go.uber.org/zap"
	
	"knowledge-graph-service/internal/domain/repositories"
	"knowledge-graph-service/internal/domain/domain"
	"knowledge-graph-service/internal/logger"
)

// GraphUseCase 图用例
type GraphUseCase struct {
	nodeRepo         repositories.NodeRepository
	relationshipRepo repositories.RelationshipRepository
	logger           *logger.Logger
}

// NewGraphUseCase 创建图用例
func NewGraphUseCase(nodeRepo repositories.NodeRepository, relationshipRepo repositories.RelationshipRepository, logger *logger.Logger) *GraphUseCase {
	return &GraphUseCase{
		nodeRepo:         nodeRepo,
		relationshipRepo: relationshipRepo,
		logger:           logger,
	}
}

// NodeWithRelations 节点及其关系
type NodeWithRelations struct {
	Node         interface{}   `json:"node"`
	Relationships []interface{} `json:"relationships"`
	RelatedNodes  []interface{} `json:"relatedNodes"`
}

// GraphPath 图路径
type GraphPath struct {
	Nodes         []interface{} `json:"nodes"`
	Relationships []interface{} `json:"relationships"`
	Length        int           `json:"length"`
}

// GetAllRelationshipTypes 获取所有关系类型
func (uc *GraphUseCase) GetAllRelationshipTypes() ([]string, error) {
	uc.logger.Info("获取所有关系类型")
	return uc.relationshipRepo.GetAllTypes()
}

// GetNodeNeighborhood 获取节点周围的邻居
func (uc *GraphUseCase) GetNodeNeighborhood(nodeID string, depth int) (*NodeWithRelations, error) {
	uc.logger.Info(fmt.Sprintf("获取节点 %s 的邻居 (深度: %d)", nodeID, depth))
	
	// 获取节点
	node, err := uc.nodeRepo.GetByID(nodeID)
	if err != nil {
		return nil, err
	}
	
	// 获取关系
	relationships, err := uc.relationshipRepo.GetByNodeID(nodeID)
	if err != nil {
		return nil, err
	}
	
	// 获取相关节点
	relatedNodeIDs := make([]string, 0)
	for _, rel := range relationships {
		if rel.GetSourceID() == nodeID {
			relatedNodeIDs = append(relatedNodeIDs, rel.GetTargetID())
		} else {
			relatedNodeIDs = append(relatedNodeIDs, rel.GetSourceID())
		}
	}
	
	relatedNodes := make([]interface{}, 0)
	for _, id := range relatedNodeIDs {
		relNode, err := uc.nodeRepo.GetByID(id)
		if err != nil {
			uc.logger.Warn(fmt.Sprintf("获取相关节点 %s 失败: %v", id, err))
			continue
		}
		relatedNodes = append(relatedNodes, relNode)
	}
	
	return &NodeWithRelations{
		Node:          node,
		Relationships: interfaces(relationships),
		RelatedNodes:  relatedNodes,
	}, nil
}

// SearchGraph 搜索图
func (uc *GraphUseCase) SearchGraph(query string, nodeType string, limit int) ([]interface{}, error) {
	uc.logger.Info(fmt.Sprintf("搜索图 (查询: %s, 类型: %s, 限制: %d)", query, nodeType, limit))
	
	// 使用模糊匹配搜索节点
	nodes, err := uc.nodeRepo.Search(query, nodeType, limit)
	if err != nil {
		return nil, err
	}
	
	return interfaces(nodes), nil
}

// FindPaths 查找路径
func (uc *GraphUseCase) FindPaths(sourceID string, targetID string, maxDepth int) ([]GraphPath, error) {
	uc.logger.Info(fmt.Sprintf("查找从 %s 到 %s 的路径 (最大深度: %d)", sourceID, targetID, maxDepth))
	
	// 获取源节点和目标节点
	sourceNode, err := uc.nodeRepo.GetByID(sourceID)
	if err != nil {
		return nil, fmt.Errorf("获取源节点失败: %w", err)
	}
	
	targetNode, err := uc.nodeRepo.GetByID(targetID)
	if err != nil {
		return nil, fmt.Errorf("获取目标节点失败: %w", err)
	}
	
	// 实现路径查找算法
	// 这里使用简化版的BFS查找最短路径
	paths, err := uc.findPathsBFS(sourceNode, targetNode, maxDepth)
	if err != nil {
		return nil, err
	}
	
	return paths, nil
}

// GetZangFuRelations 获取脏腑关系
func (uc *GraphUseCase) GetZangFuRelations() ([]interface{}, error) {
	uc.logger.Info("获取脏腑关系")
	
	// 获取所有脏腑节点
	zangfuNodes, err := uc.nodeRepo.GetByType("ZangFu")
	if err != nil {
		return nil, err
	}
	
	// 获取脏腑之间的关系
	result := make([]interface{}, 0)
	for _, node := range zangfuNodes {
		nodeID := node.GetID()
		relations, err := uc.relationshipRepo.GetByNodeID(nodeID)
		if err != nil {
			uc.logger.Warn(fmt.Sprintf("获取节点 %s 的关系失败: %v", nodeID, err))
			continue
		}
		
		// 仅保留脏腑之间的关系
		for _, rel := range relations {
			sourceID := rel.GetSourceID()
			targetID := rel.GetTargetID()
			
			var otherNodeID string
			if sourceID == nodeID {
				otherNodeID = targetID
			} else {
				otherNodeID = sourceID
			}
			
			otherNode, err := uc.nodeRepo.GetByID(otherNodeID)
			if err != nil {
				uc.logger.Warn(fmt.Sprintf("获取节点 %s 失败: %v", otherNodeID, err))
				continue
			}
			
			if otherNode.GetType() == "ZangFu" {
				result = append(result, map[string]interface{}{
					"source": sourceID,
					"target": targetID,
					"type": rel.GetType(),
					"properties": rel.GetProperties(),
				})
			}
		}
	}
	
	return result, nil
}

// GetConstitutionZangFuRelations 获取体质与脏腑关系
func (uc *GraphUseCase) GetConstitutionZangFuRelations(constitutionType string) ([]interface{}, error) {
	uc.logger.Info(fmt.Sprintf("获取体质与脏腑关系 (体质类型: %s)", constitutionType))
	
	var constitutionNodes []domain.Node
	var err error
	
	// 如果未指定体质类型，获取所有体质节点
	if constitutionType == "" {
		constitutionNodes, err = uc.nodeRepo.GetByType("Constitution")
	} else {
		// 否则获取指定类型的体质节点
		constitutionNodes, err = uc.nodeRepo.Search(constitutionType, "Constitution", 10)
	}
	
	if err != nil {
		return nil, err
	}
	
	result := make([]interface{}, 0)
	for _, constNode := range constitutionNodes {
		constID := constNode.GetID()
		
		// 获取与该体质节点相关的关系
		relations, err := uc.relationshipRepo.GetByNodeID(constID)
		if err != nil {
			uc.logger.Warn(fmt.Sprintf("获取节点 %s 的关系失败: %v", constID, err))
			continue
		}
		
		// 筛选与脏腑相关的关系
		for _, rel := range relations {
			sourceID := rel.GetSourceID()
			targetID := rel.GetTargetID()
			
			var organtID string
			var direction string
			
			if sourceID == constID {
				organtID = targetID
				direction = "outgoing"
			} else {
				organtID = sourceID
				direction = "incoming"
			}
			
			organNode, err := uc.nodeRepo.GetByID(organtID)
			if err != nil {
				uc.logger.Warn(fmt.Sprintf("获取节点 %s 失败: %v", organtID, err))
				continue
			}
			
			// 检查节点是否为脏腑类型
			if organNode.GetType() == "ZangFu" {
				result = append(result, map[string]interface{}{
					"constitution": map[string]interface{}{
						"id": constID,
						"name": constNode.GetName(),
						"type": constNode.GetType(),
					},
					"organ": map[string]interface{}{
						"id": organtID,
						"name": organNode.GetName(),
						"type": organNode.GetType(),
					},
					"relationship": map[string]interface{}{
						"id": rel.GetID(),
						"type": rel.GetType(),
						"properties": rel.GetProperties(),
						"direction": direction,
					},
				})
			}
		}
	}
	
	return result, nil
}

// GetConstitutionSymptomRelations 获取体质与症状关系
func (uc *GraphUseCase) GetConstitutionSymptomRelations(constitutionType string) ([]interface{}, error) {
	uc.logger.Info(fmt.Sprintf("获取体质与症状关系 (体质类型: %s)", constitutionType))
	
	var constitutionNodes []domain.Node
	var err error
	
	// 如果未指定体质类型，获取所有体质节点
	if constitutionType == "" {
		constitutionNodes, err = uc.nodeRepo.GetByType("Constitution")
	} else {
		// 否则获取指定类型的体质节点
		constitutionNodes, err = uc.nodeRepo.Search(constitutionType, "Constitution", 10)
	}
	
	if err != nil {
		return nil, err
	}
	
	result := make([]interface{}, 0)
	for _, constNode := range constitutionNodes {
		constID := constNode.GetID()
		
		// 获取与该体质节点相关的关系
		relations, err := uc.relationshipRepo.GetByNodeID(constID)
		if err != nil {
			uc.logger.Warn(fmt.Sprintf("获取节点 %s 的关系失败: %v", constID, err))
			continue
		}
		
		// 筛选与症状相关的关系
		for _, rel := range relations {
			sourceID := rel.GetSourceID()
			targetID := rel.GetTargetID()
			
			var symptomID string
			var direction string
			
			if sourceID == constID {
				symptomID = targetID
				direction = "outgoing"
			} else {
				symptomID = sourceID
				direction = "incoming"
			}
			
			symptomNode, err := uc.nodeRepo.GetByID(symptomID)
			if err != nil {
				uc.logger.Warn(fmt.Sprintf("获取节点 %s 失败: %v", symptomID, err))
				continue
			}
			
			// 检查节点是否为症状类型
			if symptomNode.GetType() == "Symptom" {
				result = append(result, map[string]interface{}{
					"constitution": map[string]interface{}{
						"id": constID,
						"name": constNode.GetName(),
						"type": constNode.GetType(),
					},
					"symptom": map[string]interface{}{
						"id": symptomID,
						"name": symptomNode.GetName(),
						"type": symptomNode.GetType(),
					},
					"relationship": map[string]interface{}{
						"id": rel.GetID(),
						"type": rel.GetType(),
						"properties": rel.GetProperties(),
						"direction": direction,
					},
				})
			}
		}
	}
	
	return result, nil
}

// 辅助方法：将[]T转换为[]interface{}
func interfaces[T any](slice []T) []interface{} {
	result := make([]interface{}, len(slice))
	for i, v := range slice {
		result[i] = v
	}
	return result
}

// 辅助方法：使用BFS寻找路径
func (uc *GraphUseCase) findPathsBFS(source domain.Node, target domain.Node, maxDepth int) ([]GraphPath, error) {
	// 路径查找逻辑
	sourceID := source.GetID()
	targetID := target.GetID()
	
	if sourceID == targetID {
		return []GraphPath{
			{
				Nodes:         []interface{}{source},
				Relationships: []interface{}{},
				Length:        0,
			},
		}, nil
	}
	
	// 使用BFS寻找最短路径
	visited := make(map[string]bool)
	visited[sourceID] = true
	
	// 使用队列进行BFS
	type QueueItem struct {
		NodeID   string
		Path     []string
		RelPath  []string
	}
	
	queue := []QueueItem{{
		NodeID:   sourceID,
		Path:     []string{sourceID},
		RelPath:  []string{},
	}}
	
	var foundPaths []GraphPath
	
	for len(queue) > 0 && len(foundPaths) < 5 { // 限制最多返回5条路径
		current := queue[0]
		queue = queue[1:]
		
		// 如果达到最大深度，跳过
		if len(current.Path) > maxDepth + 1 {
			continue
		}
		
		// 获取当前节点的所有关系
		relations, err := uc.relationshipRepo.GetByNodeID(current.NodeID)
		if err != nil {
			return nil, fmt.Errorf("获取节点 %s 的关系失败: %w", current.NodeID, err)
		}
		
		for _, rel := range relations {
			relID := rel.GetID()
			var nextNodeID string
			
			if rel.GetSourceID() == current.NodeID {
				nextNodeID = rel.GetTargetID()
			} else {
				nextNodeID = rel.GetSourceID()
			}
			
			// 如果已访问过此节点，跳过
			if visited[nextNodeID] {
				continue
			}
			
			// 创建新路径
			newPath := append([]string{}, current.Path...)
			newPath = append(newPath, nextNodeID)
			
			newRelPath := append([]string{}, current.RelPath...)
			newRelPath = append(newRelPath, relID)
			
			// 如果找到目标节点
			if nextNodeID == targetID {
				// 构建返回路径
				pathNodes := make([]interface{}, 0)
				for _, nodeID := range newPath {
					node, err := uc.nodeRepo.GetByID(nodeID)
					if err != nil {
						return nil, fmt.Errorf("获取节点 %s 失败: %w", nodeID, err)
					}
					pathNodes = append(pathNodes, node)
				}
				
				pathRelationships := make([]interface{}, 0)
				for _, relID := range newRelPath {
					rel, err := uc.relationshipRepo.GetByID(relID)
					if err != nil {
						return nil, fmt.Errorf("获取关系 %s 失败: %w", relID, err)
					}
					pathRelationships = append(pathRelationships, rel)
				}
				
				foundPaths = append(foundPaths, GraphPath{
					Nodes:         pathNodes,
					Relationships: pathRelationships,
					Length:        len(newPath) - 1,
				})
				
				// 如果找到一条路径，就不再寻找其他从这个节点出发的路径
				break
			}
			
			// 标记为已访问
			visited[nextNodeID] = true
			
			// 将新路径添加到队列
			queue = append(queue, QueueItem{
				NodeID:   nextNodeID,
				Path:     newPath,
				RelPath:  newRelPath,
			})
		}
	}
	
	return foundPaths, nil
}

// GetNeighbors 获取节点的邻居
func (uc *GraphUseCase) GetNeighbors(ctx context.Context, nodeId string, depth int, direction string) (map[string]interface{}, error) {
	return uc.GetNeighborsWithRelTypes(ctx, nodeId, depth, nil, direction)
}

// GetNeighborsWithRelTypes 获取带指定关系类型过滤的节点邻居
func (uc *GraphUseCase) GetNeighborsWithRelTypes(ctx context.Context, nodeId string, depth int, relationshipTypes []repositories.RelationshipType, direction string) (map[string]interface{}, error) {
	if nodeId == "" {
		return nil, errors.New("节点ID不能为空")
	}
	
	if depth <= 0 {
		depth = 1
	}
	
	if depth > 3 {
		depth = 3 // 限制最大深度
	}
	
	// 默认为双向
	if direction != "outgoing" && direction != "incoming" && direction != "both" {
		direction = "both"
	}
	
	// 先获取中心节点
	centerNode, err := uc.nodeRepo.GetNode(ctx, nodeId)
	if err != nil {
		uc.logger.Error("获取中心节点失败", zap.Error(err), zap.String("nodeId", nodeId))
		return nil, fmt.Errorf("获取中心节点失败: %w", err)
	}
	
	result := map[string]interface{}{
		"center":    centerNode,
		"neighbors": []interface{}{},
		"links":     []interface{}{},
	}
	
	// 获取一阶邻居
	relationships, err := uc.relationshipRepo.GetNodeRelationships(ctx, nodeId, direction, relationshipTypes)
	if err != nil {
		uc.logger.Error("获取节点关系失败", zap.Error(err), zap.String("nodeId", nodeId))
		return nil, fmt.Errorf("获取节点关系失败: %w", err)
	}
	
	// 处理关系和邻居节点
	neighbors := make([]interface{}, 0)
	links := make([]interface{}, 0)
	
	processedNodes := make(map[string]bool)
	processedNodes[nodeId] = true
	
	// 处理关系
	for _, rel := range relationships {
		links = append(links, rel)
		
		// 处理源节点和目标节点
		sourceNode, sourceExists := rel["source"]
		targetNode, targetExists := rel["target"]
		
		if sourceExists {
			sourceNodeMap, ok := sourceNode.(map[string]interface{})
			if ok {
				sourceId, idExists := sourceNodeMap["id"]
				if idExists {
					sourceIdStr := fmt.Sprintf("%v", sourceId)
					if !processedNodes[sourceIdStr] {
						neighbors = append(neighbors, sourceNodeMap)
						processedNodes[sourceIdStr] = true
					}
				}
			}
		}
		
		if targetExists {
			targetNodeMap, ok := targetNode.(map[string]interface{})
			if ok {
				targetId, idExists := targetNodeMap["id"]
				if idExists {
					targetIdStr := fmt.Sprintf("%v", targetId)
					if !processedNodes[targetIdStr] {
						neighbors = append(neighbors, targetNodeMap)
						processedNodes[targetIdStr] = true
					}
				}
			}
		}
	}
	
	result["neighbors"] = neighbors
	result["links"] = links
	
	return result, nil
}

// GetSubgraph 获取子图
func (uc *GraphUseCase) GetSubgraph(ctx context.Context, nodeIds []string, includeRelationships bool) (map[string]interface{}, error) {
	if len(nodeIds) == 0 {
		return nil, errors.New("节点ID列表不能为空")
	}
	
	// 获取所有节点
	nodes, err := uc.nodeRepo.GetNodes(ctx, nodeIds)
	if err != nil {
		uc.logger.Error("获取节点失败", zap.Error(err), zap.Strings("nodeIds", nodeIds))
		return nil, fmt.Errorf("获取节点失败: %w", err)
	}
	
	result := map[string]interface{}{
		"nodes": nodes,
		"relationships": []interface{}{},
	}
	
	// 如果需要包含关系
	if includeRelationships && len(nodes) > 0 {
		allRelationships := make([]map[string]interface{}, 0)
		
		// 获取所有节点之间的关系
		for i := 0; i < len(nodeIds); i++ {
			for j := i + 1; j < len(nodeIds); j++ {
				rels, err := uc.relationshipRepo.GetRelationshipsBetweenNodes(ctx, nodeIds[i], nodeIds[j], nil)
				if err != nil {
					// 记录错误但继续处理
					uc.logger.Error("获取节点间关系失败", 
						zap.Error(err), 
						zap.String("sourceNodeId", nodeIds[i]), 
						zap.String("targetNodeId", nodeIds[j]))
					continue
				}
				
				// 添加到结果中
				allRelationships = append(allRelationships, rels...)
			}
		}
		
		result["relationships"] = allRelationships
	}
	
	return result, nil
}

// ExportGraph 导出图数据
func (uc *GraphUseCase) ExportGraph(ctx context.Context, nodeIds []string, format string) (map[string]interface{}, error) {
	if len(nodeIds) == 0 {
		return nil, errors.New("节点ID列表不能为空")
	}
	
	if format == "" {
		format = "json" // 默认为JSON格式
	}
	
	// 支持的格式类型
	supportedFormats := map[string]bool{
		"json":     true,
		"graphml":  true,
		"cypher":   true,
	}
	
	if !supportedFormats[format] {
		return nil, fmt.Errorf("不支持的导出格式: %s", format)
	}
	
	// 获取子图
	subgraph, err := uc.GetSubgraph(ctx, nodeIds, true)
	if err != nil {
		uc.logger.Error("获取子图失败", zap.Error(err), zap.Strings("nodeIds", nodeIds))
		return nil, fmt.Errorf("获取子图失败: %w", err)
	}
	
	// 添加导出元数据
	result := map[string]interface{}{
		"format":      format,
		"nodeCount":   len(subgraph["nodes"].([]map[string]interface{})),
		"relCount":    len(subgraph["relationships"].([]interface{})),
		"exportTime":  currentTimeISO(),
		"data":        subgraph,
	}
	
	return result, nil
} 