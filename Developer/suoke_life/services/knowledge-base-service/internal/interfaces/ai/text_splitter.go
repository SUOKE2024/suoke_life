package ai

import (
	"knowledge-base-service/internal/domain/entity"
)

// TextSplitter 文本分割器接口
// 负责将长文本分割成适合处理的更小块
type TextSplitter interface {
	// Split 将文本分割成多个块
	// text: 要分割的文本内容
	// metadata: 附加到每个块的元数据
	// 返回分割后的块列表和可能的错误
	Split(text string, metadata map[string]interface{}) ([]entity.Chunk, error)
}
