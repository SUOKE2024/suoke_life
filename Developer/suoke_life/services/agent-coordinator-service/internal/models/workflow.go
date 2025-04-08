package models

import (
	"time"
)

// Workflow 工作流模型
type Workflow struct {
	ID          string                 `json:"id"`
	Name        string                 `json:"name"`
	Description string                 `json:"description,omitempty"`
	Status      string                 `json:"status"` // PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
	Steps       []WorkflowStep         `json:"steps"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
	CreatedAt   time.Time              `json:"createdAt"`
	UpdatedAt   time.Time              `json:"updatedAt"`
	CompletedAt *time.Time             `json:"completedAt,omitempty"`
}

// WorkflowStep 工作流步骤模型
type WorkflowStep struct {
	ID          string                 `json:"id"`
	WorkflowID  string                 `json:"workflowId"`
	Name        string                 `json:"name"`
	Type        string                 `json:"type"`
	AgentID     string                 `json:"agentId,omitempty"`
	Status      string                 `json:"status"` // PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
	DependsOn   []string               `json:"dependsOn,omitempty"`
	Config      map[string]interface{} `json:"config,omitempty"`
	InputData   map[string]interface{} `json:"inputData,omitempty"`
	OutputData  map[string]interface{} `json:"outputData,omitempty"`
	CreatedAt   time.Time              `json:"createdAt"`
	UpdatedAt   time.Time              `json:"updatedAt"`
	StartedAt   *time.Time             `json:"startedAt,omitempty"`
	CompletedAt *time.Time             `json:"completedAt,omitempty"`
}

// Task 任务模型
type Task struct {
	ID          string                 `json:"id"`
	WorkflowID  string                 `json:"workflowId,omitempty"`
	AgentID     string                 `json:"agentId"`
	Title       string                 `json:"title"`
	Description string                 `json:"description,omitempty"`
	Type        string                 `json:"type"`
	Status      string                 `json:"status"` // PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED
	Priority    int                    `json:"priority"`
	Deadline    *time.Time             `json:"deadline,omitempty"`
	InputData   map[string]interface{} `json:"inputData,omitempty"`
	OutputData  map[string]interface{} `json:"outputData,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
	CreatedAt   time.Time              `json:"createdAt"`
	UpdatedAt   time.Time              `json:"updatedAt"`
	StartedAt   *time.Time             `json:"startedAt,omitempty"`
	CompletedAt *time.Time             `json:"completedAt,omitempty"`
}

// CreateWorkflowRequest 创建工作流请求
type CreateWorkflowRequest struct {
	Name        string                 `json:"name" binding:"required"`
	Description string                 `json:"description,omitempty"`
	Steps       []WorkflowStepRequest  `json:"steps" binding:"required"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

// WorkflowStepRequest 工作流步骤请求
type WorkflowStepRequest struct {
	Name      string                 `json:"name" binding:"required"`
	Type      string                 `json:"type" binding:"required"`
	AgentID   string                 `json:"agentId,omitempty"`
	DependsOn []string               `json:"dependsOn,omitempty"`
	Config    map[string]interface{} `json:"config,omitempty"`
	InputData map[string]interface{} `json:"inputData,omitempty"`
}

// CreateTaskRequest 创建任务请求
type CreateTaskRequest struct {
	WorkflowID  string                 `json:"workflowId,omitempty"`
	AgentID     string                 `json:"agentId" binding:"required"`
	Title       string                 `json:"title" binding:"required"`
	Description string                 `json:"description,omitempty"`
	Type        string                 `json:"type" binding:"required"`
	Priority    int                    `json:"priority"`
	Deadline    *time.Time             `json:"deadline,omitempty"`
	InputData   map[string]interface{} `json:"inputData,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

// UpdateTaskRequest 更新任务请求
type UpdateTaskRequest struct {
	Status     string                 `json:"status,omitempty"`
	Priority   *int                   `json:"priority,omitempty"`
	Deadline   *time.Time             `json:"deadline,omitempty"`
	OutputData map[string]interface{} `json:"outputData,omitempty"`
	Metadata   map[string]interface{} `json:"metadata,omitempty"`
} 