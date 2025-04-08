package unit

import (
	"testing"
	
	"github.com/stretchr/testify/assert"
	"suoke.life/services/knowledge-graph-service/internal/domain/entities"
)

func TestHerbNodeCreation(t *testing.T) {
	// 准备测试数据
	name := "人参"
	
	// 创建基础节点和TCM节点
	baseNode := entities.NewBaseNode(name, "tcm", 
		entities.WithDescription("性味甘、微温"),
		entities.WithSource("中国药典2020版"),
	)
	
	// 创建TCM属性
	tcmProps := &entities.TCMProperties{
		SubType:        entities.TCMNodeHerb,
		Classification: "补气药",
		Nature:         []string{"微温"},
		Flavor:         []string{"甘", "微苦"},
		ChannelTropism: []string{"脾", "肺"},
		Functions:      []string{"大补元气", "复脉固脱", "补脾益肺", "生津", "安神"},
		Applications:   []string{"气虚体弱", "脾肺气虚", "气不摄血"},
		Dosage:         "3-9g",
	}
	
	// 创建TCM节点
	tcmNode := entities.NewTCMNode(baseNode, tcmProps)
	
	// 验证基本属性
	assert.NotNil(t, tcmNode)
	assert.Equal(t, "人参", tcmNode.GetName())
	assert.Equal(t, "tcm", tcmNode.GetCategory())
	assert.Equal(t, "性味甘、微温", tcmNode.GetDescription())
	assert.Equal(t, "中国药典2020版", tcmNode.GetSource())
	
	// 验证TCM属性
	props := tcmNode.GetTCMProperties()
	assert.Equal(t, entities.TCMNodeHerb, props.SubType)
	assert.Equal(t, "补气药", props.Classification)
	assert.ElementsMatch(t, []string{"微温"}, props.Nature)
	assert.ElementsMatch(t, []string{"甘", "微苦"}, props.Flavor)
	assert.ElementsMatch(t, []string{"脾", "肺"}, props.ChannelTropism)
	assert.ElementsMatch(t, []string{"大补元气", "复脉固脱", "补脾益肺", "生津", "安神"}, props.Functions)
	assert.ElementsMatch(t, []string{"气虚体弱", "脾肺气虚", "气不摄血"}, props.Applications)
	assert.Equal(t, "3-9g", props.Dosage)
} 