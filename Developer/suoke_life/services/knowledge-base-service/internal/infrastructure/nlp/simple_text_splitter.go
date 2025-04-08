package nlp

import (
	"strings"
	"time"

	"github.com/google/uuid"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/interfaces/ai"
)

// SimpleTextSplitter 简单文本分割器
// 按照固定大小分割文本，用于测试
type SimpleTextSplitter struct {
	chunkSize    int
	chunkOverlap int
}

// 确保 SimpleTextSplitter 实现了 TextSplitter 接口
var _ ai.TextSplitter = (*SimpleTextSplitter)(nil)

// NewSimpleTextSplitter 创建新的简单文本分割器
func NewSimpleTextSplitter(chunkSize, chunkOverlap int) *SimpleTextSplitter {
	if chunkSize <= 0 {
		chunkSize = 1000
	}

	if chunkOverlap < 0 {
		chunkOverlap = 0
	} else if chunkOverlap >= chunkSize {
		chunkOverlap = chunkSize / 2
	}

	return &SimpleTextSplitter{
		chunkSize:    chunkSize,
		chunkOverlap: chunkOverlap,
	}
}

// Split 将文本分割成块
func (s *SimpleTextSplitter) Split(text string, metadata map[string]interface{}) ([]entity.Chunk, error) {
	if text == "" {
		return nil, nil
	}

	// 简单按段落分割
	paragraphs := strings.Split(text, "\n\n")

	var chunks []entity.Chunk
	var currentChunk strings.Builder
	var currentSize int

	for _, paragraph := range paragraphs {
		trimmedParagraph := strings.TrimSpace(paragraph)
		if trimmedParagraph == "" {
			continue
		}

		paragraphSize := len(trimmedParagraph)

		// 如果段落太大，单独作为一个块
		if paragraphSize > s.chunkSize {
			if currentSize > 0 {
				chunks = append(chunks, s.createChunk(currentChunk.String(), metadata))
				currentChunk.Reset()
				currentSize = 0
			}

			chunks = append(chunks, s.createChunk(trimmedParagraph, metadata))
			continue
		}

		// 如果添加段落后超过块大小，创建新块
		if currentSize+paragraphSize > s.chunkSize {
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

		// 添加当前段落
		if currentSize > 0 {
			currentChunk.WriteString("\n\n")
			currentSize += 2
		}
		currentChunk.WriteString(trimmedParagraph)
		currentSize += paragraphSize
	}

	// 处理最后一个块
	if currentSize > 0 {
		chunks = append(chunks, s.createChunk(currentChunk.String(), metadata))
	}

	return chunks, nil
}

// createChunk 创建文档块
func (s *SimpleTextSplitter) createChunk(content string, metadata map[string]interface{}) entity.Chunk {
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
