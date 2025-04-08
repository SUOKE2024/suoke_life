package repository

import (
	"context"

	"github.com/google/uuid"

	"knowledge-base-service/internal/domain/entity/models"
)

// KnowledgeRepository 知识存储库接口
// 提供对不同类型知识模型的访问能力
type KnowledgeRepository interface {
	// 基础CRUD操作
	FindKnowledgeByID(ctx context.Context, id uuid.UUID, knowledgeType string) (interface{}, error)
	SaveKnowledge(ctx context.Context, knowledge interface{}) error
	UpdateKnowledge(ctx context.Context, knowledge interface{}) error
	DeleteKnowledge(ctx context.Context, id uuid.UUID, knowledgeType string) error

	// 高级查询
	FindByCategory(ctx context.Context, categoryID uuid.UUID, knowledgeType string, limit, offset int) ([]interface{}, int, error)
	FindByTags(ctx context.Context, tags []string, knowledgeType string, limit, offset int) ([]interface{}, int, error)
	Search(ctx context.Context, query string, knowledgeType string, limit, offset int) ([]interface{}, int, error)
	SemanticSearch(ctx context.Context, query string, knowledgeType string, limit int) ([]interface{}, error)

	// 中医知识相关
	FindByMeridian(ctx context.Context, meridian string, limit, offset int) ([]models.TraditionalChineseMedicineKnowledge, int, error)
	FindByHerbalMedicine(ctx context.Context, herb string, limit, offset int) ([]models.TraditionalChineseMedicineKnowledge, int, error)
	FindByConstitutionType(ctx context.Context, constitutionType string, limit, offset int) ([]models.TraditionalChineseMedicineKnowledge, int, error)

	// 现代医学知识相关
	FindByDiagnosticMethod(ctx context.Context, method string, limit, offset int) ([]models.ModernMedicineKnowledge, int, error)
	FindByTreatmentOption(ctx context.Context, treatment string, limit, offset int) ([]models.ModernMedicineKnowledge, int, error)

	// 多模态健康数据相关
	FindByDataType(ctx context.Context, dataType string, limit, offset int) ([]models.MultimodalHealthData, int, error)

	// 健康教育相关
	FindByTargetAudience(ctx context.Context, audience string, limit, offset int) ([]models.HealthEducationKnowledge, int, error)

	// 统计方法
	CountByKnowledgeType(ctx context.Context, knowledgeType string) (int, error)
	CountByCategory(ctx context.Context, categoryID uuid.UUID, knowledgeType string) (int, error)
}
