package simple

import (
	"testing"
)

// 测试基本功能
func TestSimple(t *testing.T) {
	// 一个不依赖任何项目内部包的简单测试
	t.Run("基本断言", func(t *testing.T) {
		if 1+1 != 2 {
			t.Error("基本数学运算失败")
		}
	})
}

// 测试字符串操作
func TestStrings(t *testing.T) {
	// 字符串测试
	t.Run("字符串连接", func(t *testing.T) {
		s1 := "知识"
		s2 := "图谱"
		if s1+s2 != "知识图谱" {
			t.Error("字符串连接失败")
		}
	})
}

// 基准测试
func BenchmarkSimpleOperation(b *testing.B) {
	for i := 0; i < b.N; i++ {
		_ = 1 + 1
	}
}
