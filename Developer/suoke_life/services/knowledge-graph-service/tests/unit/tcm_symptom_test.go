package unit

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"knowledge-graph-service/internal/domain/entities"
)

func TestSymptomNodeCreation(t *testing.T) {
	// 准备测试数据
	name := "胁肋胀痛"

	// 创建TCM节点
	tcmNode := entities.NewTCMNode(name, entities.TCMNodeSymptom,
		entities.WithDescription("肝气郁结的常见症状"),
		entities.WithSource("中医诊断学"),
	)

	// 创建TCM属性
	tcmProps := &entities.TCMProperties{
		SubType:        entities.TCMNodeSymptom,
		Classification: "气滞症状",
		Etiology:       []string{"情志不畅", "肝气郁结", "肝胆湿热"},
		Pathogenesis:   []string{"肝气郁滞", "气机不畅", "疏泄失职"},
		Manifestation:  []string{"胁肋疼痛", "痛处固定", "胀痛连及乳房", "情志变化痛势加重"},
		DiagnosisMethod: []string{"问诊", "舌象", "脉象"},
		TreatmentPrinciple: []string{"疏肝理气", "行气止痛"},
	}

	// 设置TCM属性
	tcmNode.SetTCMProperties(tcmProps)

	// 验证基本属性
	assert.NotNil(t, tcmNode)
	assert.Equal(t, "胁肋胀痛", tcmNode.GetName())
	assert.Equal(t, "tcm", tcmNode.GetCategory())
	assert.Equal(t, "肝气郁结的常见症状", tcmNode.GetDescription())
	assert.Equal(t, "中医诊断学", tcmNode.GetSource())

	// 验证TCM属性
	props := tcmNode.GetTCMProperties()
	assert.Equal(t, entities.TCMNodeSymptom, props.SubType)
	assert.Equal(t, "气滞症状", props.Classification)
	assert.ElementsMatch(t, []string{"情志不畅", "肝气郁结", "肝胆湿热"}, props.Etiology)
	assert.ElementsMatch(t, []string{"肝气郁滞", "气机不畅", "疏泄失职"}, props.Pathogenesis)
	assert.ElementsMatch(t, []string{"胁肋疼痛", "痛处固定", "胀痛连及乳房", "情志变化痛势加重"}, props.Manifestation)
	assert.ElementsMatch(t, []string{"问诊", "舌象", "脉象"}, props.DiagnosisMethod)
	assert.ElementsMatch(t, []string{"疏肝理气", "行气止痛"}, props.TreatmentPrinciple)
}