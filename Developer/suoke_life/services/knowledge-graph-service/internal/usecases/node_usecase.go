package usecases

import (
	"context"
	"errors"
	"fmt"
	
	"go.uber.org/zap"
	
	"knowledge-graph-service/internal/domain/repositories"
)

// NodeUseCase 节点用例
type NodeUseCase struct {
	nodeRepo repositories.NodeRepository
	logger   *zap.Logger
}

// NewNodeUseCase 创建节点用例
func NewNodeUseCase(nodeRepo repositories.NodeRepository, logger *zap.Logger) *NodeUseCase {
	return &NodeUseCase{
		nodeRepo: nodeRepo,
		logger:   logger,
	}
}

// GetNode 获取节点
func (uc *NodeUseCase) GetNode(ctx context.Context, id string) (map[string]interface{}, error) {
	if id == "" {
		return nil, errors.New("节点ID不能为空")
	}
	
	node, err := uc.nodeRepo.GetNode(ctx, id)
	if err != nil {
		uc.logger.Error("获取节点失败", zap.Error(err), zap.String("id", id))
		return nil, fmt.Errorf("获取节点失败: %w", err)
	}
	
	return node, nil
}

// GetNodes 获取多个节点
func (uc *NodeUseCase) GetNodes(ctx context.Context, ids []string) ([]map[string]interface{}, error) {
	if len(ids) == 0 {
		return []map[string]interface{}{}, nil
	}
	
	nodes, err := uc.nodeRepo.GetNodes(ctx, ids)
	if err != nil {
		uc.logger.Error("获取多个节点失败", zap.Error(err), zap.Strings("ids", ids))
		return nil, fmt.Errorf("获取多个节点失败: %w", err)
	}
	
	return nodes, nil
}

// GetNodesByCategory 按分类获取节点
func (uc *NodeUseCase) GetNodesByCategory(ctx context.Context, category string, page, pageSize int) ([]map[string]interface{}, int64, error) {
	if category == "" {
		return nil, 0, errors.New("分类不能为空")
	}
	
	// 计算偏移量
	offset := (page - 1) * pageSize
	if offset < 0 {
		offset = 0
	}
	
	// 获取节点
	nodes, err := uc.nodeRepo.GetNodesByCategory(ctx, category, pageSize, offset)
	if err != nil {
		uc.logger.Error("按分类获取节点失败", 
			zap.Error(err), 
			zap.String("category", category),
			zap.Int("page", page),
			zap.Int("pageSize", pageSize))
		return nil, 0, fmt.Errorf("按分类获取节点失败: %w", err)
	}
	
	// 获取总数
	total, err := uc.nodeRepo.CountNodesByCategory(ctx, category)
	if err != nil {
		uc.logger.Error("统计节点数量失败", zap.Error(err), zap.String("category", category))
		// 继续处理，不因统计失败而中断流程
	}
	
	return nodes, total, nil
}

// GetNodesByProperty 按属性获取节点
func (uc *NodeUseCase) GetNodesByProperty(ctx context.Context, property string, value interface{}) ([]map[string]interface{}, error) {
	if property == "" {
		return nil, errors.New("属性名不能为空")
	}
	
	nodes, err := uc.nodeRepo.GetNodesByProperty(ctx, property, value)
	if err != nil {
		uc.logger.Error("按属性获取节点失败", 
			zap.Error(err), 
			zap.String("property", property), 
			zap.Any("value", value))
		return nil, fmt.Errorf("按属性获取节点失败: %w", err)
	}
	
	return nodes, nil
}

// CreateNode 创建节点
func (uc *NodeUseCase) CreateNode(ctx context.Context, nodeData map[string]interface{}) (string, error) {
	if len(nodeData) == 0 {
		return "", errors.New("节点数据不能为空")
	}
	
	// 添加创建时间
	if _, ok := nodeData["created_at"]; !ok {
		nodeData["created_at"] = currentTimeISO()
	}
	
	// 添加更新时间
	nodeData["updated_at"] = currentTimeISO()
	
	id, err := uc.nodeRepo.CreateNode(ctx, nodeData)
	if err != nil {
		uc.logger.Error("创建节点失败", zap.Error(err), zap.Any("nodeData", nodeData))
		return "", fmt.Errorf("创建节点失败: %w", err)
	}
	
	return id, nil
}

// BatchCreateNodes 批量创建节点
func (uc *NodeUseCase) BatchCreateNodes(ctx context.Context, nodesData []map[string]interface{}) ([]string, error) {
	if len(nodesData) == 0 {
		return []string{}, nil
	}
	
	// 为每个节点添加时间戳
	now := currentTimeISO()
	for i := range nodesData {
		if _, ok := nodesData[i]["created_at"]; !ok {
			nodesData[i]["created_at"] = now
		}
		nodesData[i]["updated_at"] = now
	}
	
	ids, err := uc.nodeRepo.BatchCreateNodes(ctx, nodesData)
	if err != nil {
		uc.logger.Error("批量创建节点失败", zap.Error(err), zap.Int("count", len(nodesData)))
		return nil, fmt.Errorf("批量创建节点失败: %w", err)
	}
	
	return ids, nil
}

// UpdateNode 更新节点
func (uc *NodeUseCase) UpdateNode(ctx context.Context, id string, nodeData map[string]interface{}) error {
	if id == "" {
		return errors.New("节点ID不能为空")
	}
	
	if len(nodeData) == 0 {
		return errors.New("更新数据不能为空")
	}
	
	// 添加更新时间
	nodeData["updated_at"] = currentTimeISO()
	
	err := uc.nodeRepo.UpdateNode(ctx, id, nodeData)
	if err != nil {
		uc.logger.Error("更新节点失败", zap.Error(err), zap.String("id", id), zap.Any("nodeData", nodeData))
		return fmt.Errorf("更新节点失败: %w", err)
	}
	
	return nil
}

// DeleteNode 删除节点
func (uc *NodeUseCase) DeleteNode(ctx context.Context, id string) error {
	if id == "" {
		return errors.New("节点ID不能为空")
	}
	
	err := uc.nodeRepo.DeleteNode(ctx, id)
	if err != nil {
		uc.logger.Error("删除节点失败", zap.Error(err), zap.String("id", id))
		return fmt.Errorf("删除节点失败: %w", err)
	}
	
	return nil
}

// SearchNodes 搜索节点
func (uc *NodeUseCase) SearchNodes(ctx context.Context, query string, params map[string]interface{}, page, pageSize int) ([]map[string]interface{}, error) {
	if query == "" {
		return nil, errors.New("查询语句不能为空")
	}
	
	// 计算偏移量
	offset := (page - 1) * pageSize
	if offset < 0 {
		offset = 0
	}
	
	nodes, err := uc.nodeRepo.QueryNodes(ctx, query, params, pageSize, offset)
	if err != nil {
		uc.logger.Error("搜索节点失败", 
			zap.Error(err), 
			zap.String("query", query),
			zap.Any("params", params),
			zap.Int("page", page),
			zap.Int("pageSize", pageSize))
		return nil, fmt.Errorf("搜索节点失败: %w", err)
	}
	
	return nodes, nil
} 