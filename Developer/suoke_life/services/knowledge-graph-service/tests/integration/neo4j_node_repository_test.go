// +build integration

package integration

import (
	"context"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"knowledge-graph-service/internal/domain/entities"
	"knowledge-graph-service/internal/infrastructure/database"
	"knowledge-graph-service/internal/infrastructure/repositories"
)

// 设置测试节点仓库
func setupTestNodeRepository(t *testing.T) repositories.Neo4jNodeRepository {
	// 获取Neo4j连接
	conn, err := database.GetNeo4jConnection()
	require.NoError(t, err, "连接Neo4j数据库失败")
	require.NotNil(t, conn, "Neo4j连接不应为空")

	// 创建Neo4j节点仓库
	repo := repositories.NewNeo4jNodeRepository(conn)
	require.NotNil(t, repo, "Neo4j节点仓库不应为空")

	// 清理测试数据
	cleanTestData(t, conn)

	return repo
}

// 清理测试数据
func cleanTestData(t *testing.T, conn *database.Neo4jConnection) {
	ctx := context.Background()
	session, err := conn.GetSession(ctx, true)
	require.NoError(t, err, "获取Neo4j会话失败")
	defer session.Close(ctx)

	_, err = session.Run(ctx, "MATCH (n) DETACH DELETE n", nil)
	require.NoError(t, err, "清理测试数据失败")
}

// 创建测试节点
func createTestNode(t *testing.T) entities.BaseNode {
	id := uuid.New().String()
	name := "测试节点-" + id[:8]
	category := "Test"
	
	return entities.NewBaseNodeImpl(id, name, category)
}

// 创建测试TCM节点
func createTestTCMNode(t *testing.T) entities.TCMNode {
	id := uuid.New().String()
	name := "测试中药-" + id[:8]
	category := "TCM"
	
	baseNode := entities.NewBaseNodeImpl(id, name, category)
	tcmNode := entities.NewTCMNodeImpl(baseNode, entities.HerbType)
	
	tcmProps := entities.TCMProperties{
		SubType:       entities.HerbType,
		Classification: "测试分类",
		Nature:        "温",
		Taste:         "甘",
		ChannelTropism: []string{"脾", "肺"},
		Functions:     []string{"测试功能1", "测试功能2"},
		Applications:  []string{"测试适应症1", "测试适应症2"},
	}
	tcmNode.SetTCMProperties(tcmProps)
	
	return tcmNode
}

// 测试创建节点
func TestCreateNode(t *testing.T) {
	// 设置
	repo := setupTestNodeRepository(t)
	ctx := context.Background()
	
	// 创建测试节点
	node := createTestNode(t)
	
	// 测试创建节点
	err := repo.Create(ctx, node)
	assert.NoError(t, err, "创建节点应该成功")
	
	// 获取节点验证
	retrievedNode, err := repo.GetByID(ctx, node.GetID())
	assert.NoError(t, err, "获取节点应该成功")
	assert.NotNil(t, retrievedNode, "获取的节点不应为空")
	assert.Equal(t, node.GetID(), retrievedNode.GetID(), "节点ID不匹配")
	assert.Equal(t, node.GetName(), retrievedNode.GetName(), "节点名称不匹配")
	assert.Equal(t, node.GetCategory(), retrievedNode.GetCategory(), "节点类别不匹配")
}

// 测试获取节点
func TestGetNode(t *testing.T) {
	// 设置
	repo := setupTestNodeRepository(t)
	ctx := context.Background()
	
	// 创建测试节点
	node := createTestNode(t)
	
	// 先创建节点
	err := repo.Create(ctx, node)
	require.NoError(t, err, "创建节点失败")
	
	// 测试通过ID获取节点
	byID, err := repo.GetByID(ctx, node.GetID())
	assert.NoError(t, err, "通过ID获取节点应该成功")
	assert.NotNil(t, byID, "通过ID获取的节点不应为空")
	assert.Equal(t, node.GetID(), byID.GetID(), "节点ID不匹配")
	
	// 测试通过名称获取节点
	byName, err := repo.GetByName(ctx, node.GetName())
	assert.NoError(t, err, "通过名称获取节点应该成功")
	assert.NotNil(t, byName, "通过名称获取的节点不应为空")
	assert.Equal(t, node.GetName(), byName.GetName(), "节点名称不匹配")
	
	// 测试通过类别获取节点
	byCategory, err := repo.GetByCategory(ctx, node.GetCategory(), 0, 10)
	assert.NoError(t, err, "通过类别获取节点应该成功")
	assert.NotEmpty(t, byCategory, "通过类别获取的节点不应为空")
	assert.Equal(t, 1, len(byCategory), "应该只有一个节点")
	assert.Equal(t, node.GetCategory(), byCategory[0].GetCategory(), "节点类别不匹配")
}

// 测试更新节点
func TestUpdateNode(t *testing.T) {
	// 设置
	repo := setupTestNodeRepository(t)
	ctx := context.Background()
	
	// 创建测试节点
	node := createTestNode(t)
	
	// 先创建节点
	err := repo.Create(ctx, node)
	require.NoError(t, err, "创建节点失败")
	
	// 更新节点属性
	node.SetProperty("test_prop", "测试值")
	node.SetProperty("test_number", 123)
	node.SetProperty("test_array", []string{"值1", "值2"})
	
	// 测试更新节点
	err = repo.Update(ctx, node)
	assert.NoError(t, err, "更新节点应该成功")
	
	// 获取节点验证更新
	updated, err := repo.GetByID(ctx, node.GetID())
	assert.NoError(t, err, "获取更新后的节点应该成功")
	assert.NotNil(t, updated, "更新后的节点不应为空")
	assert.Equal(t, "测试值", updated.GetProperty("test_prop"), "字符串属性不匹配")
	assert.Equal(t, 123, updated.GetProperty("test_number"), "数值属性不匹配")
	
	// 验证数组属性
	arrayProp, ok := updated.GetProperty("test_array").([]string)
	assert.True(t, ok, "数组属性类型不匹配")
	assert.Equal(t, []string{"值1", "值2"}, arrayProp, "数组属性值不匹配")
}

// 测试删除节点
func TestDeleteNode(t *testing.T) {
	// 设置
	repo := setupTestNodeRepository(t)
	ctx := context.Background()
	
	// 创建测试节点
	node := createTestNode(t)
	
	// 先创建节点
	err := repo.Create(ctx, node)
	require.NoError(t, err, "创建节点失败")
	
	// 测试删除节点
	err = repo.Delete(ctx, node.GetID())
	assert.NoError(t, err, "删除节点应该成功")
	
	// 尝试获取已删除的节点
	deleted, err := repo.GetByID(ctx, node.GetID())
	assert.Error(t, err, "获取已删除的节点应该失败")
	assert.Nil(t, deleted, "已删除的节点应为空")
}

// 测试批量操作
func TestBatchOperations(t *testing.T) {
	// 设置
	repo := setupTestNodeRepository(t)
	ctx := context.Background()
	
	// 创建多个测试节点
	nodes := make([]entities.BaseNode, 5)
	for i := 0; i < 5; i++ {
		nodes[i] = createTestNode(t)
	}
	
	// 测试批量创建
	err := repo.BatchCreate(ctx, nodes)
	assert.NoError(t, err, "批量创建节点应该成功")
	
	// 验证创建成功
	count, err := repo.Count(ctx, "", nil)
	assert.NoError(t, err, "计数应该成功")
	assert.Equal(t, 5, count, "应该有5个节点")
	
	// 更新所有节点
	for i := range nodes {
		nodes[i].SetProperty("batch_updated", true)
		nodes[i].SetProperty("timestamp", time.Now().Unix())
	}
	
	// 测试批量更新
	err = repo.BatchUpdate(ctx, nodes)
	assert.NoError(t, err, "批量更新节点应该成功")
	
	// 验证更新成功
	for _, node := range nodes {
		updated, err := repo.GetByID(ctx, node.GetID())
		assert.NoError(t, err, "获取更新后的节点应该成功")
		assert.Equal(t, true, updated.GetProperty("batch_updated"), "批量更新属性不匹配")
	}
	
	// 收集节点ID用于批量删除
	ids := make([]string, len(nodes))
	for i, node := range nodes {
		ids[i] = node.GetID()
	}
	
	// 测试批量删除
	err = repo.BatchDelete(ctx, ids)
	assert.NoError(t, err, "批量删除节点应该成功")
	
	// 验证删除成功
	count, err = repo.Count(ctx, "", nil)
	assert.NoError(t, err, "计数应该成功")
	assert.Equal(t, 0, count, "应该没有节点")
}

// 测试查询节点
func TestQueryNodes(t *testing.T) {
	// 设置
	repo := setupTestNodeRepository(t)
	ctx := context.Background()
	
	// 创建多个不同类别的测试节点
	categories := []string{"Category1", "Category2", "Category3"}
	for _, cat := range categories {
		for i := 0; i < 3; i++ {
			node := createTestNode(t)
			node.SetCategory(cat)
			node.SetProperty("index", i)
			node.SetProperty("created_at", time.Now().Unix())
			
			err := repo.Create(ctx, node)
			require.NoError(t, err, "创建节点失败")
		}
	}
	
	// 测试简单查询
	params := map[string]interface{}{
		"category": "Category1",
	}
	results, err := repo.Query(ctx, "n.category = $category", params, 0, 10)
	assert.NoError(t, err, "查询节点应该成功")
	assert.Equal(t, 3, len(results), "应该有3个Category1节点")
	for _, node := range results {
		assert.Equal(t, "Category1", node.GetCategory(), "节点类别不匹配")
	}
	
	// 测试复杂查询
	params = map[string]interface{}{
		"category": "Category2",
		"index": 1,
	}
	results, err = repo.Query(ctx, "n.category = $category AND n.index = $index", params, 0, 10)
	assert.NoError(t, err, "复杂查询节点应该成功")
	assert.Equal(t, 1, len(results), "应该有1个匹配节点")
	assert.Equal(t, "Category2", results[0].GetCategory(), "节点类别不匹配")
	assert.Equal(t, 1, results[0].GetProperty("index"), "节点索引不匹配")
	
	// 测试获取所有类别
	categories, err = repo.GetAllCategories(ctx)
	assert.NoError(t, err, "获取所有类别应该成功")
	assert.Equal(t, 3, len(categories), "应该有3个类别")
	assert.Contains(t, categories, "Category1", "应该包含Category1")
	assert.Contains(t, categories, "Category2", "应该包含Category2")
	assert.Contains(t, categories, "Category3", "应该包含Category3")
}

// 测试TCM节点特定功能
func TestTCMNodeOperations(t *testing.T) {
	// 设置
	repo := setupTestNodeRepository(t)
	ctx := context.Background()
	
	// 创建测试TCM节点
	tcmNode := createTestTCMNode(t)
	
	// 测试创建TCM节点
	err := repo.Create(ctx, tcmNode)
	assert.NoError(t, err, "创建TCM节点应该成功")
	
	// 获取TCM节点验证
	retrievedNode, err := repo.GetByID(ctx, tcmNode.GetID())
	assert.NoError(t, err, "获取TCM节点应该成功")
	
	// 转换为TCM节点
	tcmRetrieved, ok := retrievedNode.(entities.TCMNode)
	assert.True(t, ok, "应该能够转换为TCM节点")
	assert.NotNil(t, tcmRetrieved, "TCM节点不应为空")
	
	// 验证TCM属性
	props := tcmRetrieved.GetTCMProperties()
	assert.Equal(t, entities.HerbType, props.SubType, "子类型不匹配")
	assert.Equal(t, "测试分类", props.Classification, "分类不匹配")
	assert.Equal(t, "温", props.Nature, "性质不匹配")
	assert.Equal(t, "甘", props.Taste, "味道不匹配")
	assert.Equal(t, []string{"脾", "肺"}, props.ChannelTropism, "归经不匹配")
	assert.Equal(t, []string{"测试功能1", "测试功能2"}, props.Functions, "功效不匹配")
	assert.Equal(t, []string{"测试适应症1", "测试适应症2"}, props.Applications, "主治不匹配")
} 