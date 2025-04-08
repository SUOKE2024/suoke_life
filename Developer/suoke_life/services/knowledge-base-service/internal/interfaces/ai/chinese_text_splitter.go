package ai

import (
	"fmt"
	"github.com/google/uuid"
	"strings"
	"time"

	"knowledge-base-service/internal/domain/entity"
)

// ChineseTextSplitter 中文文本分割器
type ChineseTextSplitter struct {
	ChunkSize    int // 块大小（字符数）
	ChunkOverlap int // 块重叠（字符数）
}

// Split 将中文文本分割成块
func (s *ChineseTextSplitter) Split(text string, metadata map[string]interface{}) ([]entity.Chunk, error) {
	if s.ChunkSize <= 0 {
		return nil, fmt.Errorf("块大小必须大于0")
	}

	// 文本长度
	textLen := len([]rune(text))

	// 如果文本为空，返回空块
	if textLen == 0 {
		return []entity.Chunk{}, nil
	}

	// 如果重叠大于或等于块大小，将其调整为块大小的一半
	if s.ChunkOverlap >= s.ChunkSize {
		s.ChunkOverlap = s.ChunkSize / 2
	}

	// 将文本转换为rune切片以正确处理中文字符
	textRunes := []rune(text)

	// 计算步长
	step := s.ChunkSize - s.ChunkOverlap

	// 如果文本长度小于块大小，直接返回一个块
	if textLen <= s.ChunkSize {
		return []entity.Chunk{
			{
				ID:         uuid.New(),
				Content:    text,
				Metadata:   convertToMetadataFields(metadata),
				TokenCount: estimateTokenCount(text),
				Offset:     0,
				Length:     textLen,
				CreatedAt:  time.Now(),
			},
		}, nil
	}

	// 分割文本
	var chunks []entity.Chunk

	for i := 0; i < textLen; i += step {
		// 计算当前块的结束位置
		end := i + s.ChunkSize
		if end > textLen {
			end = textLen
		}

		// 提取当前块的文本
		chunkText := string(textRunes[i:end])

		// 创建块
		chunk := entity.Chunk{
			ID:         uuid.New(),
			Content:    chunkText,
			Metadata:   convertToMetadataFields(metadata),
			TokenCount: estimateTokenCount(chunkText),
			Offset:     i,
			Length:     end - i,
			CreatedAt:  time.Now(),
		}

		chunks = append(chunks, chunk)

		// 如果已经处理到文本末尾，退出循环
		if end == textLen {
			break
		}
	}

	return chunks, nil
}

// 将map[string]interface{}转换为[]entity.MetadataField
func convertToMetadataFields(metadata map[string]interface{}) []entity.MetadataField {
	fields := make([]entity.MetadataField, 0, len(metadata))

	for key, value := range metadata {
		fields = append(fields, entity.MetadataField{
			Name:  key,
			Value: value,
		})
	}

	return fields
}

// 估算文本的token数量（简单实现，实际应用中应该使用分词器）
func estimateTokenCount(text string) int {
	// 对于中文，我们可以粗略地认为每个字符是一个token
	// 对于英文，我们可以按空格分割来估算

	// 计算中文字符数
	chineseCount := 0
	for _, r := range text {
		if r >= 0x4e00 && r <= 0x9fff {
			chineseCount++
		}
	}

	// 计算英文单词数
	englishWords := len(strings.Fields(text))

	// 返回估算的token数量
	return chineseCount + englishWords
}
