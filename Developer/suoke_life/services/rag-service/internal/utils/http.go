package utils

import (
	"encoding/json"
	"net/http"
)

// ResponseWriterWrapper HTTP响应写入器包装
type ResponseWriterWrapper struct {
	http.ResponseWriter
	StatusCode int
}

// NewResponseWriterWrapper 创建响应写入器包装
func NewResponseWriterWrapper(w http.ResponseWriter) *ResponseWriterWrapper {
	return &ResponseWriterWrapper{
		ResponseWriter: w,
		StatusCode:     http.StatusOK,
	}
}

// WriteHeader 覆盖WriteHeader以捕获状态码
func (w *ResponseWriterWrapper) WriteHeader(code int) {
	w.StatusCode = code
	w.ResponseWriter.WriteHeader(code)
}

// WriteJSONResponse 写入JSON响应
func WriteJSONResponse(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	
	if err := json.NewEncoder(w).Encode(data); err != nil {
		http.Error(w, "JSON编码错误", http.StatusInternalServerError)
	}
}

// WriteErrorResponse 写入错误响应
func WriteErrorResponse(w http.ResponseWriter, status int, message string, details interface{}) {
	response := map[string]interface{}{
		"error": map[string]interface{}{
			"message": message,
		},
	}
	
	if details != nil {
		response["error"].(map[string]interface{})["details"] = details
	}
	
	WriteJSONResponse(w, status, response)
}

// ReadJSONRequest 读取JSON请求
func ReadJSONRequest(r *http.Request, v interface{}) error {
	return json.NewDecoder(r.Body).Decode(v)
}