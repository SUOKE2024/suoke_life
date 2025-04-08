package unit

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"knowledge-graph-service/internal/domain/entities"
)

func TestFormulaNodeCreation(t *testing.T) {
	// 准备测试数据
	name := "桂枝汤"

	// 创建TCM节点
	tcmNode := entities.NewTCMNode(name, entities.TCMNodePrescription,
		entities.WithDescription("发汗解表方剂"),
		entities.WithSource("伤寒论"),
	)

	// 创建TCM属性
	tcmProps := &entities.TCMProperties{
		SubType:        entities.TCMNodePrescription,
		Classification: "解表剂",
		Composition:    []string{"桂枝", "芍药", "生姜", "大枣", "甘草"},
		Formula:        "桂枝三两(9g)，芍药三两(9g)，生姜三两(9g)，大枣十二枚(6g)，甘草二两(6g)",
		PreparationMethod: "水煎服",
		AdministrationRoute: "口服",
		Treatment:      []string{"风寒感冒", "太阳中风证", "营卫不和"},
		Functions:      []string{"发汗解表", "调和营卫", "温通经脉"},
	}

	// 设置TCM属性
	tcmNode.SetTCMProperties(tcmProps)

	// 验证基本属性
	assert.NotNil(t, tcmNode)
	assert.Equal(t, "桂枝汤", tcmNode.GetName())
	assert.Equal(t, "tcm", tcmNode.GetCategory())
	assert.Equal(t, "发汗解表方剂", tcmNode.GetDescription())
	assert.Equal(t, "伤寒论", tcmNode.GetSource())

	// 验证TCM属性
	props := tcmNode.GetTCMProperties()
	assert.Equal(t, entities.TCMNodePrescription, props.SubType)
	assert.Equal(t, "解表剂", props.Classification)
	assert.ElementsMatch(t, []string{"桂枝", "芍药", "生姜", "大枣", "甘草"}, props.Composition)
	assert.Equal(t, "桂枝三两(9g)，芍药三两(9g)，生姜三两(9g)，大枣十二枚(6g)，甘草二两(6g)", props.Formula)
	assert.Equal(t, "水煎服", props.PreparationMethod)
	assert.Equal(t, "口服", props.AdministrationRoute)
	assert.ElementsMatch(t, []string{"风寒感冒", "太阳中风证", "营卫不和"}, props.Treatment)
	assert.ElementsMatch(t, []string{"发汗解表", "调和营卫", "温通经脉"}, props.Functions)
}