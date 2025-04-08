package benchmark

import (
	"testing"

	_ "knowledge-base-service/internal/test/benchmark/real" // 导入实际测试包
)

// 跳过实际的存储库测试，因为它们需要真实的数据库连接
// 使用real包中的实现来运行实际测试
func TestSkipRepositoryTests(t *testing.T) {
	t.Skip("跳过存储库测试，需要实际数据库连接，请使用real包中的实现")
}

// BenchmarkRepositorySkipped 跳过存储库基准测试
// 如果需要运行真实数据库基准测试，请执行:
// go test -bench=. ./internal/test/benchmark/real/
func BenchmarkRepositorySkipped(b *testing.B) {
	b.Skip("存储库基准测试已跳过 - 需要实际数据库连接，请使用 real 包中的实现")
}
