package repositories

import (
	"context"
)

// NodeRepository 定义了节点操作的接口
type NodeRepository interface {
	// 获取节点
	GetNode(ctx context.Context, id string) (map[string]interface{}, error)
	GetNodes(ctx context.Context, ids []string) ([]map[string]interface{}, error)
	GetNodesByProperty(ctx context.Context, property string, value interface{}) ([]map[string]interface{}, error)
	GetNodesByCategory(ctx context.Context, category string, limit, offset int) ([]map[string]interface{}, error)
	
	// 创建节点
	CreateNode(ctx context.Context, nodeData map[string]interface{}) (string, error)
	BatchCreateNodes(ctx context.Context, nodes []map[string]interface{}) ([]string, error)
	
	// 更新节点
	UpdateNode(ctx context.Context, id string, nodeData map[string]interface{}) error
	
	// 删除节点
	DeleteNode(ctx context.Context, id string) error
	
	// 查询节点
	QueryNodes(ctx context.Context, query string, params map[string]interface{}, limit, offset int) ([]map[string]interface{}, error)
	
	// 统计节点
	CountNodesByCategory(ctx context.Context, category string) (int64, error)
} 