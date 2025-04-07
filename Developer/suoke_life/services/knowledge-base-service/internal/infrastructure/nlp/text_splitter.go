package nlp

import (
	"strings"
	"time"
	
	"github.com/google/uuid"
	
	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/interfaces/ai"
)

// 常量定义
const (
	// 默认块大小（字符数）
	DefaultChunkSize = 1000
	
	// 默认块重叠大小（字符数）
	DefaultChunkOverlap = 200
	
	// 最小块大小
	MinChunkSize = 100
	
	// 估计的每个汉字token数量（中文文本特有）
	EstimatedTokensPerChar = 1.5
)

// ChineseTextSplitter 中文文本分割器
// 针对中文文本的特点进行了优化
type ChineseTextSplitter struct {
	chunkSize       int
	chunkOverlap    int
	separators      []string
	useSmartBoundary bool
}

// 确保 ChineseTextSplitter 实现了 TextSplitter 接口
var _ ai.TextSplitter = (*ChineseTextSplitter)(nil)

// NewChineseTextSplitter 创建新的中文文本分割器
func NewChineseTextSplitter(chunkSize, chunkOverlap int, useSmartBoundary bool) *ChineseTextSplitter {
	if chunkSize <= 0 {
		chunkSize = DefaultChunkSize
	} else if chunkSize < MinChunkSize {
		chunkSize = MinChunkSize
	}
	
	if chunkOverlap < 0 {
		chunkOverlap = 0
	} else if chunkOverlap >= chunkSize {
		chunkOverlap = chunkSize / 2
	}
	
	// 分隔符按优先级排序，分段时优先使用列表前面的分隔符
	separators := []string{
		"\n\n", // 段落分隔
		"\n",   // 换行
		"。",    // 句号
		"！",    // 感叹号
		"？",    // 问号
		"；",    // 分号
		"，",    // 逗号
		"、",    // 顿号
		" ",    // 空格
		"",     // 无分隔符（按字符分割）
	}
	
	return &ChineseTextSplitter{
		chunkSize:       chunkSize,
		chunkOverlap:    chunkOverlap,
		separators:      separators,
		useSmartBoundary: useSmartBoundary,
	}
}

// Split 将文本分割成块
func (s *ChineseTextSplitter) Split(text string, metadata map[string]interface{}) ([]entity.Chunk, error) {
	if text == "" {
		return nil, nil
	}
	
	var chunks []entity.Chunk
	
	// 将文本按分隔符分割成段落
	paragraphs := s.splitByBestSeparator(text)
	
	// 合并段落成块
	var currentChunk strings.Builder
	var currentSize int
	var startOffset int
	
	for _, paragraph := range paragraphs {
		paragraphSize := len(paragraph)
		
		// 如果段落太大，需要进一步分割
		if paragraphSize > s.chunkSize {
			// 先处理当前累积的内容
			if currentSize > 0 {
				chunk := s.createChunk(currentChunk.String(), startOffset, currentSize, metadata)
				chunks = append(chunks, chunk)
				
				// 准备下一个块
				startOffset += currentSize - s.chunkOverlap
				
				// 如果使用重叠，保留一部分内容
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
			
			// 分割大段落
			subChunks := s.splitLargeParagraph(paragraph, startOffset, metadata)
			chunks = append(chunks, subChunks...)
			
			// 更新偏移量
			startOffset += paragraphSize
			continue
		}
		
		// 检查是否需要创建新块
		if currentSize+paragraphSize > s.chunkSize {
			// 当前块已满，创建新块
			chunk := s.createChunk(currentChunk.String(), startOffset, currentSize, metadata)
			chunks = append(chunks, chunk)
			
			// 准备下一个块
			startOffset += currentSize - s.chunkOverlap
			
			// 如果使用重叠，保留一部分内容
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
		
		// 添加段落到当前块
		currentChunk.WriteString(paragraph)
		currentSize += paragraphSize
	}
	
	// 处理最后一个块
	if currentSize > 0 {
		chunk := s.createChunk(currentChunk.String(), startOffset, currentSize, metadata)
		chunks = append(chunks, chunk)
	}
	
	return chunks, nil
}

// 创建文档块
func (s *ChineseTextSplitter) createChunk(content string, offset, length int, metadata map[string]interface{}) entity.Chunk {
	// 估计token数量
	tokenCount := int(float64(length) * EstimatedTokensPerChar)
	
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
		Offset:     offset,
		Length:     length,
		Metadata:   metadataFields,
		CreatedAt:  time.Now(),
	}
}

// 按最佳分隔符分割文本
func (s *ChineseTextSplitter) splitByBestSeparator(text string) []string {
	for _, sep := range s.separators {
		if sep == "" {
			// 最后的情况：按固定大小分割
			return s.splitBySize(text, s.chunkSize)
		}
		
		parts := strings.Split(text, sep)
		if len(parts) > 1 {
			var result []string
			for _, part := range parts {
				trimmed := strings.TrimSpace(part)
				if trimmed != "" {
					// 在每个部分后面添加分隔符（除了最后一个）
					if sep != "\n" && sep != "\n\n" && sep != " " {
						result = append(result, trimmed+sep)
					} else {
						result = append(result, trimmed)
					}
				}
			}
			return result
		}
	}
	
	// 无法分割，返回原文本
	return []string{text}
}

// 按固定大小分割文本
func (s *ChineseTextSplitter) splitBySize(text string, size int) []string {
	var result []string
	runes := []rune(text) // 使用rune以正确处理中文字符
	
	for i := 0; i < len(runes); i += size {
		end := i + size
		if end > len(runes) {
			end = len(runes)
		}
		result = append(result, string(runes[i:end]))
	}
	
	return result
}

// 分割大段落
func (s *ChineseTextSplitter) splitLargeParagraph(paragraph string, startOffset int, metadata map[string]interface{}) []entity.Chunk {
	var chunks []entity.Chunk
	var currentOffset = startOffset
	
	// 尝试使用更细粒度的分隔符
	fineSeparators := []string{"。", "！", "？", "；", "，", "、", " ", ""}
	
	for _, sep := range fineSeparators {
		if sep == "" {
			// 最后的情况：按字符分割
			parts := s.splitBySize(paragraph, s.chunkSize)
			
			for _, part := range parts {
				content := part
				length := len([]rune(content))
				
				if content != "" {
					chunk := s.createChunk(content, currentOffset, length, metadata)
					chunks = append(chunks, chunk)
					
					// 更新偏移量（考虑重叠）
					currentOffset += length
					if s.chunkOverlap > 0 && length > s.chunkOverlap {
						currentOffset -= s.chunkOverlap
					}
				}
			}
			
			return chunks
		}
		
		parts := strings.Split(paragraph, sep)
		if len(parts) > 1 {
			var currentChunk strings.Builder
			var currentSize int
			
			for _, part := range parts {
				trimmed := strings.TrimSpace(part)
				if trimmed == "" {
					continue
				}
				
				// 添加分隔符（除了最后一个部分）
				if sep != " " {
					trimmed += sep
				}
				
				partSize := len([]rune(trimmed))
				
				// 如果加上这部分会超出块大小，先创建一个块
				if currentSize > 0 && currentSize + partSize > s.chunkSize {
					content := currentChunk.String()
					chunk := s.createChunk(content, currentOffset, currentSize, metadata)
					chunks = append(chunks, chunk)
					
					// 更新偏移量（考虑重叠）
					currentOffset += currentSize
					if s.chunkOverlap > 0 && currentSize > s.chunkOverlap {
						// 保留重叠部分
						overlapRunes := []rune(content)
						if len(overlapRunes) > s.chunkOverlap {
							overlapContent := string(overlapRunes[len(overlapRunes)-s.chunkOverlap:])
							currentChunk.Reset()
							currentChunk.WriteString(overlapContent)
							currentSize = s.chunkOverlap
							currentOffset -= s.chunkOverlap
						}
					} else {
						currentChunk.Reset()
						currentSize = 0
					}
				}
				
				// 如果部分本身超过块大小，进一步分割
				if partSize > s.chunkSize {
					// 如果当前块有内容，先保存
					if currentSize > 0 {
						content := currentChunk.String()
						chunk := s.createChunk(content, currentOffset, currentSize, metadata)
						chunks = append(chunks, chunk)
						currentOffset += currentSize
						currentChunk.Reset()
						currentSize = 0
					}
					
					// 递归分割大部分
					subChunks := s.splitLargeParagraph(trimmed, currentOffset, metadata)
					chunks = append(chunks, subChunks...)
					
					// 更新偏移量
					lastChunk := subChunks[len(subChunks)-1]
					currentOffset = lastChunk.Offset + lastChunk.Length
				} else {
					// 添加到当前块
					currentChunk.WriteString(trimmed)
					currentSize += partSize
				}
			}
			
			// 处理最后一个块
			if currentSize > 0 {
				content := currentChunk.String()
				chunk := s.createChunk(content, currentOffset, currentSize, metadata)
				chunks = append(chunks, chunk)
			}
			
			return chunks
		}
	}
	
	// 无法分割，作为单个块返回
	content := paragraph
	length := len([]rune(content))
	chunk := s.createChunk(content, startOffset, length, metadata)
	return []entity.Chunk{chunk}
}

// 注意：RecursiveCharacterTextSplitter 已移至 recursive_text_splitter.go 文件