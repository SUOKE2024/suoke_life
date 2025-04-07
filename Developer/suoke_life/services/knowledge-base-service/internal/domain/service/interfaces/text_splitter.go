package interfaces

import (
	"knowledge-base-service/internal/domain/entity"
)

// TextSplitter 文本分割器接口
type TextSplitter interface {
	// Split 将文本分割成块
	Split(text string, metadata map[string]interface{}) ([]entity.Chunk, error)
} 