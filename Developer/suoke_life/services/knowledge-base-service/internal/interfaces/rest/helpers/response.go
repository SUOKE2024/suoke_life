package helpers

import (
	"encoding/json"
	"io"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/render"
	"github.com/google/uuid"

	"knowledge-base-service/pkg/errors"
	"knowledge-base-service/pkg/logger"
)

// ErrorResponse 错误响应
type ErrorResponse struct {
	Error string `json:"error"`
}

// SuccessResponse 成功响应
type SuccessResponse struct {
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// ParseRequestBody 解析请求体到给定结构
func ParseRequestBody(r *http.Request, dst interface{}) error {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		return errors.BadRequest("无法读取请求体", err)
	}
	defer r.Body.Close()

	err = json.Unmarshal(body, dst)
	if err != nil {
		return errors.BadRequest("无法解析JSON", err)
	}

	return nil
}

// ParseUUID 解析URL参数为UUID
func ParseUUID(r *http.Request, paramName string) (uuid.UUID, error) {
	idStr := chi.URLParam(r, paramName)
	id, err := uuid.Parse(idStr)
	if err != nil {
		return uuid.Nil, errors.BadRequest("无效的UUID格式", err)
	}
	return id, nil
}

// RenderJSON 渲染JSON响应
func RenderJSON(w http.ResponseWriter, r *http.Request, status int, data interface{}) {
	render.Status(r, status)
	render.JSON(w, r, data)
}

// RenderError 渲染错误响应
func RenderError(w http.ResponseWriter, r *http.Request, err error) {
	log := logger.FromContext(r.Context())

	if appErr, ok := err.(*errors.AppError); ok {
		log.Errorw("处理请求时遇到错误",
			"error", appErr.Error(),
			"code", appErr.Code,
			"path", r.URL.Path,
			"method", r.Method,
		)

		render.Status(r, appErr.Code)
		render.JSON(w, r, ErrorResponse{Error: appErr.Message})
		return
	}

	log.Errorw("处理请求时遇到未知错误",
		"error", err.Error(),
		"path", r.URL.Path,
		"method", r.Method,
	)

	render.Status(r, http.StatusInternalServerError)
	render.JSON(w, r, ErrorResponse{Error: "服务器内部错误"})
}

// RenderSuccess 渲染成功响应
func RenderSuccess(w http.ResponseWriter, r *http.Request, status int, message string, data interface{}) {
	response := SuccessResponse{
		Message: message,
		Data:    data,
	}

	render.Status(r, status)
	render.JSON(w, r, response)
}

// ValidateRequired 验证必填字段
func ValidateRequired(fields map[string]string) error {
	for fieldName, fieldValue := range fields {
		if fieldValue == "" {
			return errors.BadRequest(fieldName+"为必填项", nil)
		}
	}
	return nil
}
