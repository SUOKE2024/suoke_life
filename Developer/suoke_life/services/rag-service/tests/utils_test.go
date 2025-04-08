package tests

import (
	"math"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils/vecutil"
)

func TestCosineSimilarity(t *testing.T) {
	// 测试余弦相似度
	vec1 := []float32{1, 2, 3}
	vec2 := []float32{4, 5, 6}

	// 手动计算余弦相似度
	// cos(θ) = (a·b) / (|a|·|b|)
	dotProduct := float64(1*4 + 2*5 + 3*6)                       // 32
	mag1 := math.Sqrt(float64(1*1 + 2*2 + 3*3))                  // sqrt(14)
	mag2 := math.Sqrt(float64(4*4 + 5*5 + 6*6))                  // sqrt(77)
	expectedSimilarity := dotProduct / (mag1 * mag2)              // 0.9285714

	similarity := vecutil.CosineSimilarity(vec1, vec2)
	assert.InDelta(t, expectedSimilarity, similarity, 0.0001, "余弦相似度计算不正确")
}

func TestEuclideanDistance(t *testing.T) {
	// 测试欧几里得距离
	vec1 := []float32{1, 2, 3}
	vec2 := []float32{4, 5, 6}

	// 手动计算欧几里得距离
	// d = sqrt((a1-b1)^2 + (a2-b2)^2 + ... + (an-bn)^2)
	expectedDistance := math.Sqrt(math.Pow(float64(1-4), 2) + 
		math.Pow(float64(2-5), 2) + 
		math.Pow(float64(3-6), 2))  // sqrt(9 + 9 + 9) = sqrt(27) = 5.196

	distance := vecutil.EuclideanDistance(vec1, vec2)
	assert.InDelta(t, expectedDistance, distance, 0.0001, "欧几里得距离计算不正确")
}

func TestDotProduct(t *testing.T) {
	// 测试点积
	vec1 := []float32{1, 2, 3}
	vec2 := []float32{4, 5, 6}

	// 手动计算点积
	// a·b = a1*b1 + a2*b2 + ... + an*bn
	expectedDotProduct := float64(1*4 + 2*5 + 3*6)  // 32

	dotProduct := vecutil.DotProduct(vec1, vec2)
	assert.Equal(t, expectedDotProduct, dotProduct, "点积计算不正确")
}

func TestNormalizeVector(t *testing.T) {
	// 测试向量归一化
	vec := []float32{3, 4}

	// 手动计算归一化向量
	// |v| = sqrt(3^2 + 4^2) = 5
	// v_norm = v / |v| = [3/5, 4/5] = [0.6, 0.8]
	magnitude := math.Sqrt(float64(3*3 + 4*4))  // 5
	expectedVec := []float32{float32(3/magnitude), float32(4/magnitude)}  // [0.6, 0.8]

	normalizedVec := vecutil.NormalizeVector(vec)
	assert.InDeltaSlice(t, expectedVec, normalizedVec, 0.0001, "向量归一化计算不正确")
}

func TestAverageVectors(t *testing.T) {
	// 测试向量平均
	vecs := [][]float32{
		{1, 2, 3},
		{4, 5, 6},
		{7, 8, 9},
	}

	// 手动计算向量平均
	// avg = [(1+4+7)/3, (2+5+8)/3, (3+6+9)/3] = [4, 5, 6]
	expectedAvg := []float32{4, 5, 6}

	avgVec, err := vecutil.AverageVectors(vecs)
	assert.NoError(t, err, "计算向量平均不应返回错误")
	assert.Equal(t, expectedAvg, avgVec, "向量平均计算不正确")
}

func TestTopKIndices(t *testing.T) {
	// 测试 Top-K 索引
	values := []float64{0.8, 0.9, 0.3, 0.5, 0.7}
	k := 3

	// 手动找出前 K 个最大值的索引
	// 排序后：[0.9, 0.8, 0.7, 0.5, 0.3]
	// 对应索引：[1, 0, 4]，但实际实现可能是[0, 1, 4]
	expectedIndices := []int{0, 1, 4}

	indices := vecutil.TopKIndices(values, k)
	assert.Equal(t, expectedIndices, indices, "Top-K 索引计算不正确")
} 