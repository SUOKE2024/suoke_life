package unit

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"knowledge-graph-service/internal/domain/entities"
	"knowledge-graph-service/internal/infrastructure/repositories"
)

func TestMockNodeRepository(t *testing.T) {
	// 创建Mock存储库
	repo := repositories.NewMockNodeRepository()
	ctx := context.Background()

	// 测试创建节点
	t.Run("Create Node", func(t *testing.T) {
		// 创建一个人参节点
		herbNode := entities.NewTCMNode("人参", entities.TCMNodeHerb,
			entities.WithDescription("补气名药"),
			entities.WithSource("中国药典"),
		)

		// 设置TCM属性
		herbNode.SetTCMProperties(&entities.TCMProperties{
			SubType:        entities.TCMNodeHerb,
			Classification: "补气药",
			Nature:         []string{"微温"},
			Flavor:         []string{"甘", "微苦"},
		})

		// 创建节点
		id, err := repo.Create(ctx, herbNode)
		
		// 验证
		assert.NoError(t, err)
		assert.NotEmpty(t, id)
		assert.Equal(t, herbNode.GetID(), id)
	})

	// 测试通过ID获取节点
	t.Run("Get Node By ID", func(t *testing.T) {
		// 创建一个桂枝汤节点
		formulaNode := entities.NewTCMNode("桂枝汤", entities.TCMNodePrescription,
			entities.WithDescription("经典方剂"),
		)
		
		// 设置TCM属性
		formulaNode.SetTCMProperties(&entities.TCMProperties{
			SubType:        entities.TCMNodePrescription,
			Classification: "解表剂",
		})

		// 创建节点
		id, _ := repo.Create(ctx, formulaNode)

		// 获取节点
		node, err := repo.GetByID(ctx, id)
		
		// 验证
		assert.NoError(t, err)
		assert.NotNil(t, node)
		assert.Equal(t, "桂枝汤", node.GetName())
		assert.Equal(t, "tcm", node.GetCategory())
		
		// 验证是否为TCM节点
		tcmNode, ok := node.(entities.TCMNode)
		assert.True(t, ok)
		assert.Equal(t, entities.TCMNodePrescription, tcmNode.GetTCMProperties().SubType)
	})

	// 测试通过类别获取节点
	t.Run("Get Nodes By Category", func(t *testing.T) {
		// 创建多个症状节点
		symptom1 := entities.NewTCMNode("胁肋胀痛", entities.TCMNodeSymptom)
		symptom2 := entities.NewTCMNode("口干", entities.TCMNodeSymptom)
		symptom3 := entities.NewTCMNode("头痛", entities.TCMNodeSymptom)
		
		// 创建节点
		repo.Create(ctx, symptom1)
		repo.Create(ctx, symptom2)
		repo.Create(ctx, symptom3)

		// 获取节点
		nodes, err := repo.GetByCategory(ctx, "tcm", 10, 0)
		
		// 验证
		assert.NoError(t, err)
		assert.GreaterOrEqual(t, len(nodes), 3) // 可能有之前测试创建的节点
	})

	// 测试通过名称获取节点
	t.Run("Get Nodes By Name", func(t *testing.T) {
		// 创建一个重复名称的节点
		herb1 := entities.NewTCMNode("黄芪", entities.TCMNodeHerb)
		herb2 := entities.NewTCMNode("黄芪", entities.TCMNodeHerb,
			entities.WithDescription("另一个黄芪记录"),
		)
		
		// 创建节点
		repo.Create(ctx, herb1)
		repo.Create(ctx, herb2)

		// 获取节点
		nodes, err := repo.GetByName(ctx, "黄芪")
		
		// 验证
		assert.NoError(t, err)
		assert.Equal(t, 2, len(nodes))
	})

	// 测试更新节点
	t.Run("Update Node", func(t *testing.T) {
		// 创建一个节点
		node := entities.NewTCMNode("当归", entities.TCMNodeHerb)
		id, _ := repo.Create(ctx, node)

		// 获取节点并进行修改
		retrievedNode, _ := repo.GetByID(ctx, id)
		tcmNode, _ := retrievedNode.(entities.TCMNode)
		
		// 设置TCM属性
		tcmNode.SetTCMProperties(&entities.TCMProperties{
			SubType:        entities.TCMNodeHerb,
			Classification: "活血药",
			Nature:         []string{"温"},
			Flavor:         []string{"甘", "辛"},
		})

		// 更新节点
		err := repo.Update(ctx, tcmNode)
		
		// 验证
		assert.NoError(t, err)
		
		// 再次获取节点验证更新
		updatedNode, _ := repo.GetByID(ctx, id)
		updatedTCMNode, _ := updatedNode.(entities.TCMNode)
		
		assert.Equal(t, "活血药", updatedTCMNode.GetTCMProperties().Classification)
		assert.ElementsMatch(t, []string{"温"}, updatedTCMNode.GetTCMProperties().Nature)
	})

	// 测试删除节点
	t.Run("Delete Node", func(t *testing.T) {
		// 创建一个节点
		node := entities.NewTCMNode("柴胡", entities.TCMNodeHerb)
		id, _ := repo.Create(ctx, node)

		// 删除节点
		err := repo.Delete(ctx, id)
		
		// 验证
		assert.NoError(t, err)
		
		// 尝试获取已删除的节点
		_, err = repo.GetByID(ctx, id)
		assert.Error(t, err)
	})

	// 测试查询节点
	t.Run("Query Nodes", func(t *testing.T) {
		// 创建查询
		query := map[string]interface{}{
			"category": "tcm",
		}

		// 查询节点
		nodes, err := repo.Query(ctx, query, 10, 0)
		
		// 验证
		assert.NoError(t, err)
		assert.NotEmpty(t, nodes)
		
		// 所有返回的节点都应该是tcm类别
		for _, node := range nodes {
			assert.Equal(t, "tcm", node.GetCategory())
		}
	})
}