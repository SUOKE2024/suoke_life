package models

import (
	"time"
)

// KnowledgeEntity 知识实体模型
type KnowledgeEntity struct {
	ID          string                 `json:"id"`
	Type        string                 `json:"type"`
	Name        string                 `json:"name"`
	Description string                 `json:"description,omitempty"`
	Properties  map[string]interface{} `json:"properties,omitempty"`
	Vector      []float64              `json:"vector,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
	CreatedAt   time.Time              `json:"createdAt"`
	UpdatedAt   time.Time              `json:"updatedAt"`
}

// KnowledgeRelation 知识关系模型
type KnowledgeRelation struct {
	ID         string                 `json:"id"`
	Type       string                 `json:"type"`
	SourceID   string                 `json:"sourceId"`
	TargetID   string                 `json:"targetId"`
	Properties map[string]interface{} `json:"properties,omitempty"`
	Weight     float64                `json:"weight,omitempty"`
	Metadata   map[string]interface{} `json:"metadata,omitempty"`
	CreatedAt  time.Time              `json:"createdAt"`
	UpdatedAt  time.Time              `json:"updatedAt"`
}

// KnowledgeResult 知识查询结果
type KnowledgeResult struct {
	Entity *KnowledgeEntity `json:"entity"`
	Score  float64          `json:"score"`
}

// KnowledgeIngestRequest 知识导入请求
type KnowledgeIngestRequest struct {
	Entities  []KnowledgeEntity  `json:"entities" binding:"required"`
	Relations []KnowledgeRelation `json:"relations,omitempty"`
}

// KnowledgeIngestResponse 知识导入响应
type KnowledgeIngestResponse struct {
	Success           bool     `json:"success"`
	EntitiesIngested  int      `json:"entitiesIngested"`
	RelationsIngested int      `json:"relationsIngested"`
	Errors            []string `json:"errors,omitempty"`
}

// KnowledgeQueryRequest 知识查询请求
type KnowledgeQueryRequest struct {
	Query         string   `json:"query" binding:"required"`
	QueryType     string   `json:"queryType,omitempty"` // exact, semantic, hybrid
	EntityTypes   []string `json:"entityTypes,omitempty"`
	Filters       map[string]interface{} `json:"filters,omitempty"`
	MaxResults    int      `json:"maxResults,omitempty"`
	IncludeVector bool     `json:"includeVector,omitempty"`
}

// KnowledgeQueryResponse 知识查询响应
type KnowledgeQueryResponse struct {
	Results     []KnowledgeResult `json:"results"`
	TotalCount  int               `json:"totalCount"`
	ProcessTime int64             `json:"processTimeMs"`
} 