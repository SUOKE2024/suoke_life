package vecutil

import (
	"math"
)

// valIdx 用于存储值和索引对
type valIdx struct {
	val float64
	idx int
}

// CosineSimilarity 计算余弦相似度
func CosineSimilarity(a, b []float32) float64 {
	if len(a) != len(b) {
		return 0.0
	}

	var dot, magA, magB float64
	for i := 0; i < len(a); i++ {
		dot += float64(a[i] * b[i])
		magA += float64(a[i] * a[i])
		magB += float64(b[i] * b[i])
	}

	// 避免除零
	if magA == 0 || magB == 0 {
		return 0.0
	}

	return dot / (math.Sqrt(magA) * math.Sqrt(magB))
}

// EuclideanDistance 计算欧氏距离
func EuclideanDistance(a, b []float32) float64 {
	if len(a) != len(b) {
		return math.MaxFloat64
	}

	var sum float64
	for i := 0; i < len(a); i++ {
		d := float64(a[i] - b[i])
		sum += d * d
	}

	return math.Sqrt(sum)
}

// DotProduct 计算点积
func DotProduct(a, b []float32) float64 {
	if len(a) != len(b) {
		return 0.0
	}

	var dot float64
	for i := 0; i < len(a); i++ {
		dot += float64(a[i] * b[i])
	}

	return dot
}

// NormalizeVector 归一化向量
func NormalizeVector(vector []float32) []float32 {
	norm := float64(0)
	for _, v := range vector {
		norm += float64(v * v)
	}
	norm = math.Sqrt(norm)

	// 避免除零
	if norm == 0 {
		return vector
	}

	result := make([]float32, len(vector))
	for i, v := range vector {
		result[i] = float32(float64(v) / norm)
	}

	return result
}

// AverageVectors 计算向量平均值
func AverageVectors(vectors [][]float32) ([]float32, error) {
	if len(vectors) == 0 {
		return nil, nil
	}

	dim := len(vectors[0])
	result := make([]float32, dim)

	for _, vec := range vectors {
		if len(vec) != dim {
			continue // 跳过不匹配维度的向量
		}

		for i, v := range vec {
			result[i] += v
		}
	}

	// 计算平均值
	for i := range result {
		result[i] /= float32(len(vectors))
	}

	return result, nil
}

// TopKIndices 返回数组中最大的K个元素的索引
func TopKIndices(values []float64, k int) []int {
	if k <= 0 {
		return []int{}
	}

	if k >= len(values) {
		// 如果请求的k大于等于数组长度，返回所有索引
		indices := make([]int, len(values))
		for i := range values {
			indices[i] = i
		}
		return indices
	}

	// 创建(值, 索引)对
	pairs := make([]valIdx, len(values))
	for i, val := range values {
		pairs[i] = valIdx{val, i}
	}

	// 快速选择算法 - 复杂度O(n)，但通常比排序快
	left, right := 0, len(values)-1
	for left < right {
		pivotIndex := partition(pairs, left, right)
		if pivotIndex == k-1 {
			break
		} else if pivotIndex > k-1 {
			right = pivotIndex - 1
		} else {
			left = pivotIndex + 1
		}
	}

	// 提取前k个索引
	result := make([]int, k)
	for i := 0; i < k; i++ {
		result[i] = pairs[i].idx
	}

	return result
}

// partition helper for quickselect
func partition(pairs []valIdx, left, right int) int {
	pivot := pairs[right].val
	i := left
	for j := left; j < right; j++ {
		if pairs[j].val >= pivot { // 降序排序
			pairs[i], pairs[j] = pairs[j], pairs[i]
			i++
		}
	}
	pairs[i], pairs[right] = pairs[right], pairs[i]
	return i
}

// AddVectors 向量加法
func AddVectors(a, b []float32) []float32 {
	if len(a) != len(b) {
		return nil
	}

	result := make([]float32, len(a))
	for i := 0; i < len(a); i++ {
		result[i] = a[i] + b[i]
	}

	return result
}

// SubtractVectors 向量减法
func SubtractVectors(a, b []float32) []float32 {
	if len(a) != len(b) {
		return nil
	}

	result := make([]float32, len(a))
	for i := 0; i < len(a); i++ {
		result[i] = a[i] - b[i]
	}

	return result
}

// MultiplyByScalar 向量乘以标量
func MultiplyByScalar(vector []float32, scalar float32) []float32 {
	result := make([]float32, len(vector))
	for i, v := range vector {
		result[i] = v * scalar
	}

	return result
}

// MinVector 获取向量的最小值
func MinVector(vector []float32) float32 {
	if len(vector) == 0 {
		return 0
	}

	min := vector[0]
	for _, v := range vector {
		if v < min {
			min = v
		}
	}

	return min
}

// MaxVector 获取向量的最大值
func MaxVector(vector []float32) float32 {
	if len(vector) == 0 {
		return 0
	}

	max := vector[0]
	for _, v := range vector {
		if v > max {
			max = v
		}
	}

	return max
}

// SumVector 计算向量的所有元素之和
func SumVector(vector []float32) float32 {
	var sum float32
	for _, v := range vector {
		sum += v
	}

	return sum
}

// MeanVector 计算向量的平均值
func MeanVector(vector []float32) float32 {
	if len(vector) == 0 {
		return 0
	}

	return SumVector(vector) / float32(len(vector))
}

// StandardDeviation 计算向量的标准差
func StandardDeviation(vector []float32) float32 {
	if len(vector) == 0 {
		return 0
	}

	mean := MeanVector(vector)
	var sum float32

	for _, v := range vector {
		diff := v - mean
		sum += diff * diff
	}

	variance := sum / float32(len(vector))
	return float32(math.Sqrt(float64(variance)))
} 