package llm

import "errors"

// LLM服务相关错误定义
var (
	// ErrUnsupportedModel 表示不支持的模型类型
	ErrUnsupportedModel = errors.New("不支持的语言模型类型")
	
	// ErrAPIKeyMissing 表示缺少API密钥
	ErrAPIKeyMissing = errors.New("缺少API密钥")
	
	// ErrInvalidEndpoint 表示无效的API端点
	ErrInvalidEndpoint = errors.New("无效的API端点")
	
	// ErrLocalModelNotFound 表示本地模型文件不存在
	ErrLocalModelNotFound = errors.New("本地模型文件未找到")
	
	// ErrAPIRequestFailed 表示API请求失败
	ErrAPIRequestFailed = errors.New("API请求失败")
	
	// ErrContextExceeded 表示上下文超出限制
	ErrContextExceeded = errors.New("上下文窗口超出限制")
	
	// ErrStreamingFailed 表示流式处理失败
	ErrStreamingFailed = errors.New("流式处理失败")
	
	// ErrTokenLimitExceeded 表示Token限制超出
	ErrTokenLimitExceeded = errors.New("Token数量超出模型限制")
) 