package nlp

import (
	"strings"
	"time"

	"github.com/google/uuid"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/interfaces/ai"
)

// RecursiveCharacterTextSplitter 递归字符文本分割器
// 按照分隔符列表递归地分割文本，优先使用大分隔符
type RecursiveCharacterTextSplitter struct {
	chunkSize     int
	chunkOverlap  int
	separators    []string
	keepSeparator bool
}

// 确保 RecursiveCharacterTextSplitter 实现了 TextSplitter 接口
var _ ai.TextSplitter = (*RecursiveCharacterTextSplitter)(nil)

// NewRecursiveCharacterTextSplitter 创建新的递归字符文本分割器
func NewRecursiveCharacterTextSplitter(chunkSize, chunkOverlap int) *RecursiveCharacterTextSplitter {
	if chunkSize <= 0 {
		chunkSize = 1000
	}

	if chunkOverlap < 0 {
		chunkOverlap = 0
	} else if chunkOverlap >= chunkSize {
		chunkOverlap = chunkSize / 2
	}

	// 默认分隔符，从大到小排序
	separators := []string{
		"\n\n", // 段落
		"\n",   // 换行
		". ",   // 句号
		"! ",   // 感叹号
		"? ",   // 问号
		"；",    // 中文分号
		"，",    // 中文逗号
		"。",    // 中文句号
		": ",   // 冒号
		"; ",   // 分号
		", ",   // 逗号
		" ",    // 空格
		"",     // 无分隔符，逐字分割
	}

	return &RecursiveCharacterTextSplitter{
		chunkSize:     chunkSize,
		chunkOverlap:  chunkOverlap,
		separators:    separators,
		keepSeparator: true,
	}
}

// Split 将文本分割成块
func (s *RecursiveCharacterTextSplitter) Split(text string, metadata map[string]interface{}) ([]entity.Chunk, error) {
	if text == "" {
		return nil, nil
	}

	// 开始递归分割
	splits := s.splitText(text, s.separators)

	// 将分割结果按照 chunkSize 和 chunkOverlap 合并为最终的块
	var chunks []entity.Chunk
	var currentChunk strings.Builder
	var currentSize int

	for _, split := range splits {
		splitSize := len(split)

		// 如果单个分割太大，进一步分割
		if splitSize > s.chunkSize {
			// 如果当前块非空，先保存
			if currentSize > 0 {
				chunks = append(chunks, s.createChunk(currentChunk.String(), metadata))
				currentChunk.Reset()
				currentSize = 0
			}

			// 进一步分割大块
			subSplits := s.splitTextBySize(split, s.chunkSize, s.chunkOverlap)
			for _, subSplit := range subSplits {
				chunks = append(chunks, s.createChunk(subSplit, metadata))
			}
			continue
		}

		// 如果添加当前分割后超过块大小，创建新块
		if currentSize+splitSize > s.chunkSize {
			if currentSize > 0 {
				chunks = append(chunks, s.createChunk(currentChunk.String(), metadata))

				// 重置或保留重叠部分
				if s.chunkOverlap > 0 && currentSize > s.chunkOverlap {
					content := currentChunk.String()
					overlapContent := content[len(content)-s.chunkOverlap:]
					currentChunk.Reset()
					currentChunk.WriteString(overlapContent)
					currentSize = s.chunkOverlap
				} else {
					currentChunk.Reset()
					currentSize = 0
				}
			}
		}

		// 添加当前分割
		currentChunk.WriteString(split)
		currentSize += splitSize
	}

	// 处理最后一个块
	if currentSize > 0 {
		chunks = append(chunks, s.createChunk(currentChunk.String(), metadata))
	}

	return chunks, nil
}

// splitText 递归分割文本
func (s *RecursiveCharacterTextSplitter) splitText(text string, separators []string) []string {
	// 如果没有更多分隔符，返回整个文本
	if len(separators) == 0 {
		return []string{text}
	}

	// 当前分隔符
	separator := separators[0]

	// 如果分隔符为空，返回逐字符分割
	if separator == "" {
		result := make([]string, len(text))
		for i, r := range text {
			result[i] = string(r)
		}
		return result
	}

	// 使用当前分隔符分割
	splits := strings.Split(text, separator)

	// 如果只有一个元素且没有更多分隔符，返回整个文本
	if len(splits) == 1 {
		return s.splitText(text, separators[1:])
	}

	// 重新组合分割结果，保留分隔符
	var result []string
	for i, split := range splits {
		if split == "" {
			continue
		}

		// 对每个分割再递归使用剩余分隔符
		subSplits := s.splitText(split, separators[1:])

		for _, subSplit := range subSplits {
			if s.keepSeparator && i > 0 {
				result = append(result, separator+subSplit)
			} else {
				result = append(result, subSplit)
			}
		}
	}

	return result
}

// splitTextBySize 按大小分割文本，确保每个块不超过指定大小
func (s *RecursiveCharacterTextSplitter) splitTextBySize(text string, size, overlap int) []string {
	if len(text) <= size {
		return []string{text}
	}

	var result []string
	start := 0

	for start < len(text) {
		end := start + size
		if end > len(text) {
			end = len(text)
		}

		result = append(result, text[start:end])
		start = end - overlap
	}

	return result
}

// createChunk 创建文档块
func (s *RecursiveCharacterTextSplitter) createChunk(content string, metadata map[string]interface{}) entity.Chunk {
	// 估计token数量（简单实现，每4个字符算1个token）
	tokenCount := len(content) / 4
	if tokenCount < 1 {
		tokenCount = 1
	}

	// 创建元数据字段
	metadataFields := make([]entity.MetadataField, 0, len(metadata))
	for k, v := range metadata {
		metadataFields = append(metadataFields, entity.MetadataField{
			Name:  k,
			Value: v,
		})
	}

	return entity.Chunk{
		ID:         uuid.New(),
		Content:    content,
		TokenCount: tokenCount,
		Offset:     0, // 简化实现，不计算具体偏移量
		Length:     len(content),
		Metadata:   metadataFields,
		CreatedAt:  time.Now(),
	}
}
