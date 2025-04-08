package utils

import (
	"context"
	"time"
)

// FeedbackStorage 用户反馈存储接口
type FeedbackStorage interface {
	// SaveFeedback 保存用户反馈
	SaveFeedback(ctx context.Context, feedback interface{}) error
	
	// GetFeedback 根据ID获取用户反馈
	GetFeedback(ctx context.Context, feedbackID string) (interface{}, error)
	
	// GetFeedbackByQuery 获取与特定查询相关的反馈
	GetFeedbackByQuery(ctx context.Context, query string, limit int) ([]interface{}, error)
	
	// GetFeedbackByUser 获取特定用户的反馈
	GetFeedbackByUser(ctx context.Context, userID string, limit int) ([]interface{}, error)
	
	// GetFeedbackCount 获取某时间后的反馈数量
	GetFeedbackCount(ctx context.Context, since time.Time) (int, error)
	
	// GetTotalFeedbackCount 获取总反馈数量
	GetTotalFeedbackCount(ctx context.Context) (int, error)
	
	// GetFeedbackCountByType 获取各类型反馈数量
	GetFeedbackCountByType(ctx context.Context) (map[string]int, error)
	
	// SaveParameters 保存学习参数
	SaveParameters(ctx context.Context, parameters map[string]interface{}) error
	
	// LoadParameters 加载学习参数
	LoadParameters(ctx context.Context) (map[string]interface{}, error)
	
	// GetFeedbackStats 获取反馈统计数据
	GetFeedbackStats(ctx context.Context, period string) (map[string]interface{}, error)
}

// SQLiteFeedbackStorage SQLite实现的反馈存储
type SQLiteFeedbackStorage struct {
	// 数据库连接
	db *SQLiteDB
	
	// 日志器
	logger Logger
	
	// 表名
	feedbackTableName string
	
	// 参数表名
	parametersTableName string
}

// NewSQLiteFeedbackStorage 创建基于SQLite的反馈存储
func NewSQLiteFeedbackStorage(db *SQLiteDB, logger Logger) *SQLiteFeedbackStorage {
	if logger == nil {
		logger = NewNoopLogger()
	}
	
	return &SQLiteFeedbackStorage{
		db:                 db,
		logger:             logger,
		feedbackTableName:  "user_feedback",
		parametersTableName: "learning_parameters",
	}
}

// Initialize 初始化存储
func (s *SQLiteFeedbackStorage) Initialize(ctx context.Context) error {
	// 创建反馈表
	feedbackTableSQL := `
	CREATE TABLE IF NOT EXISTS ` + s.feedbackTableName + ` (
		id TEXT PRIMARY KEY,
		user_id TEXT,
		session_id TEXT,
		query TEXT NOT NULL,
		answer TEXT NOT NULL,
		feedback_type TEXT NOT NULL,
		feedback_content TEXT,
		correct_answer TEXT,
		relevance_score INTEGER,
		timestamp DATETIME NOT NULL,
		metadata TEXT,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);
	CREATE INDEX IF NOT EXISTS idx_` + s.feedbackTableName + `_user_id ON ` + s.feedbackTableName + ` (user_id);
	CREATE INDEX IF NOT EXISTS idx_` + s.feedbackTableName + `_query ON ` + s.feedbackTableName + ` (query);
	CREATE INDEX IF NOT EXISTS idx_` + s.feedbackTableName + `_feedback_type ON ` + s.feedbackTableName + ` (feedback_type);
	CREATE INDEX IF NOT EXISTS idx_` + s.feedbackTableName + `_timestamp ON ` + s.feedbackTableName + ` (timestamp);
	`
	
	// 创建参数表
	parametersTableSQL := `
	CREATE TABLE IF NOT EXISTS ` + s.parametersTableName + ` (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		parameters TEXT NOT NULL,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);
	`
	
	// 执行SQL
	if err := s.db.Exec(ctx, feedbackTableSQL); err != nil {
		return err
	}
	
	if err := s.db.Exec(ctx, parametersTableSQL); err != nil {
		return err
	}
	
	s.logger.Info("反馈存储初始化完成")
	return nil
}

// SaveFeedback 保存用户反馈
func (s *SQLiteFeedbackStorage) SaveFeedback(ctx context.Context, feedback interface{}) error {
	// 转换为JSON
	feedbackJSON, err := JSONMarshal(feedback)
	if err != nil {
		return err
	}
	
	// 解析反馈属性
	var feedbackMap map[string]interface{}
	if err := JSONUnmarshal(feedbackJSON, &feedbackMap); err != nil {
		return err
	}
	
	// 获取必要字段
	id, _ := feedbackMap["id"].(string)
	userID, _ := feedbackMap["user_id"].(string)
	sessionID, _ := feedbackMap["session_id"].(string)
	query, _ := feedbackMap["query"].(string)
	answer, _ := feedbackMap["answer"].(string)
	feedbackType, _ := feedbackMap["feedback_type"].(string)
	feedbackContent, _ := feedbackMap["feedback_content"].(string)
	correctAnswer, _ := feedbackMap["correct_answer"].(string)
	
	// 处理relevance_score
	var relevanceScore int = 0
	if score, ok := feedbackMap["relevance_score"].(float64); ok {
		relevanceScore = int(score)
	}
	
	// 处理timestamp
	var timestamp time.Time
	if ts, ok := feedbackMap["timestamp"].(string); ok {
		timestamp, err = time.Parse(time.RFC3339, ts)
		if err != nil {
			timestamp = time.Now()
		}
	} else {
		timestamp = time.Now()
	}
	
	// 处理metadata
	var metadataJSON string = "{}"
	if metadata, ok := feedbackMap["metadata"].(map[string]interface{}); ok && len(metadata) > 0 {
		metadataBytes, err := JSONMarshal(metadata)
		if err == nil {
			metadataJSON = string(metadataBytes)
		}
	}
	
	// 插入数据
	sql := `
	INSERT INTO ` + s.feedbackTableName + `
	(id, user_id, session_id, query, answer, feedback_type, feedback_content, correct_answer, relevance_score, timestamp, metadata)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	ON CONFLICT (id) DO UPDATE SET
	feedback_type = excluded.feedback_type,
	feedback_content = excluded.feedback_content,
	correct_answer = excluded.correct_answer,
	relevance_score = excluded.relevance_score,
	metadata = excluded.metadata
	`
	
	if err := s.db.Exec(ctx, sql, id, userID, sessionID, query, answer, feedbackType, feedbackContent, correctAnswer, relevanceScore, timestamp, metadataJSON); err != nil {
		return err
	}
	
	return nil
}

// GetFeedback 根据ID获取用户反馈
func (s *SQLiteFeedbackStorage) GetFeedback(ctx context.Context, feedbackID string) (interface{}, error) {
	sql := `
	SELECT id, user_id, session_id, query, answer, feedback_type, feedback_content, correct_answer, relevance_score, timestamp, metadata
	FROM ` + s.feedbackTableName + `
	WHERE id = ?
	`
	
	rows, err := s.db.Query(ctx, sql, feedbackID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	if !rows.Next() {
		return nil, ErrNotFound
	}
	
	var (
		id, userID, sessionID, query, answer, feedbackType, feedbackContent, correctAnswer string
		relevanceScore                                                                     int
		timestamp                                                                          time.Time
		metadataJSON                                                                      string
	)
	
	if err := rows.Scan(&id, &userID, &sessionID, &query, &answer, &feedbackType, &feedbackContent, &correctAnswer, &relevanceScore, &timestamp, &metadataJSON); err != nil {
		return nil, err
	}
	
	// 解析metadata
	var metadata map[string]interface{}
	if err := JSONUnmarshal([]byte(metadataJSON), &metadata); err != nil {
		metadata = make(map[string]interface{})
	}
	
	// 构建反馈对象
	feedback := map[string]interface{}{
		"id":               id,
		"user_id":          userID,
		"session_id":       sessionID,
		"query":            query,
		"answer":           answer,
		"feedback_type":    feedbackType,
		"feedback_content": feedbackContent,
		"correct_answer":   correctAnswer,
		"relevance_score":  relevanceScore,
		"timestamp":        timestamp,
		"metadata":         metadata,
	}
	
	return feedback, nil
}

// GetFeedbackByQuery 获取与特定查询相关的反馈
func (s *SQLiteFeedbackStorage) GetFeedbackByQuery(ctx context.Context, query string, limit int) ([]interface{}, error) {
	sql := `
	SELECT id, user_id, session_id, query, answer, feedback_type, feedback_content, correct_answer, relevance_score, timestamp, metadata
	FROM ` + s.feedbackTableName + `
	WHERE query LIKE ?
	ORDER BY timestamp DESC
	LIMIT ?
	`
	
	// 使用模糊匹配
	queryPattern := "%" + query + "%"
	
	if limit <= 0 {
		limit = 100 // 默认限制
	}
	
	rows, err := s.db.Query(ctx, sql, queryPattern, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	var result []interface{}
	
	for rows.Next() {
		var (
			id, userID, sessionID, query, answer, feedbackType, feedbackContent, correctAnswer string
			relevanceScore                                                                     int
			timestamp                                                                          time.Time
			metadataJSON                                                                      string
		)
		
		if err := rows.Scan(&id, &userID, &sessionID, &query, &answer, &feedbackType, &feedbackContent, &correctAnswer, &relevanceScore, &timestamp, &metadataJSON); err != nil {
			return nil, err
		}
		
		// 解析metadata
		var metadata map[string]interface{}
		if err := JSONUnmarshal([]byte(metadataJSON), &metadata); err != nil {
			metadata = make(map[string]interface{})
		}
		
		// 构建反馈对象
		feedback := map[string]interface{}{
			"id":               id,
			"user_id":          userID,
			"session_id":       sessionID,
			"query":            query,
			"answer":           answer,
			"feedback_type":    feedbackType,
			"feedback_content": feedbackContent,
			"correct_answer":   correctAnswer,
			"relevance_score":  relevanceScore,
			"timestamp":        timestamp,
			"metadata":         metadata,
		}
		
		result = append(result, feedback)
	}
	
	return result, nil
}

// GetFeedbackByUser 获取特定用户的反馈
func (s *SQLiteFeedbackStorage) GetFeedbackByUser(ctx context.Context, userID string, limit int) ([]interface{}, error) {
	sql := `
	SELECT id, user_id, session_id, query, answer, feedback_type, feedback_content, correct_answer, relevance_score, timestamp, metadata
	FROM ` + s.feedbackTableName + `
	WHERE user_id = ?
	ORDER BY timestamp DESC
	LIMIT ?
	`
	
	if limit <= 0 {
		limit = 100 // 默认限制
	}
	
	rows, err := s.db.Query(ctx, sql, userID, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	var result []interface{}
	
	for rows.Next() {
		var (
			id, userID, sessionID, query, answer, feedbackType, feedbackContent, correctAnswer string
			relevanceScore                                                                     int
			timestamp                                                                          time.Time
			metadataJSON                                                                      string
		)
		
		if err := rows.Scan(&id, &userID, &sessionID, &query, &answer, &feedbackType, &feedbackContent, &correctAnswer, &relevanceScore, &timestamp, &metadataJSON); err != nil {
			return nil, err
		}
		
		// 解析metadata
		var metadata map[string]interface{}
		if err := JSONUnmarshal([]byte(metadataJSON), &metadata); err != nil {
			metadata = make(map[string]interface{})
		}
		
		// 构建反馈对象
		feedback := map[string]interface{}{
			"id":               id,
			"user_id":          userID,
			"session_id":       sessionID,
			"query":            query,
			"answer":           answer,
			"feedback_type":    feedbackType,
			"feedback_content": feedbackContent,
			"correct_answer":   correctAnswer,
			"relevance_score":  relevanceScore,
			"timestamp":        timestamp,
			"metadata":         metadata,
		}
		
		result = append(result, feedback)
	}
	
	return result, nil
}

// GetFeedbackCount 获取某时间后的反馈数量
func (s *SQLiteFeedbackStorage) GetFeedbackCount(ctx context.Context, since time.Time) (int, error) {
	sql := `
	SELECT COUNT(*)
	FROM ` + s.feedbackTableName + `
	WHERE timestamp >= ?
	`
	
	var count int
	err := s.db.QueryRow(ctx, sql, since, &count)
	if err != nil {
		return 0, err
	}
	
	return count, nil
}

// GetTotalFeedbackCount 获取总反馈数量
func (s *SQLiteFeedbackStorage) GetTotalFeedbackCount(ctx context.Context) (int, error) {
	sql := `
	SELECT COUNT(*)
	FROM ` + s.feedbackTableName
	
	var count int
	err := s.db.QueryRow(ctx, sql, &count)
	if err != nil {
		return 0, err
	}
	
	return count, nil
}

// GetFeedbackCountByType 获取各类型反馈数量
func (s *SQLiteFeedbackStorage) GetFeedbackCountByType(ctx context.Context) (map[string]int, error) {
	sql := `
	SELECT feedback_type, COUNT(*)
	FROM ` + s.feedbackTableName + `
	GROUP BY feedback_type
	`
	
	rows, err := s.db.Query(ctx, sql)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	result := make(map[string]int)
	
	for rows.Next() {
		var feedbackType string
		var count int
		
		if err := rows.Scan(&feedbackType, &count); err != nil {
			return nil, err
		}
		
		result[feedbackType] = count
	}
	
	return result, nil
}

// SaveParameters 保存学习参数
func (s *SQLiteFeedbackStorage) SaveParameters(ctx context.Context, parameters map[string]interface{}) error {
	// 转换为JSON
	parametersJSON, err := JSONMarshal(parameters)
	if err != nil {
		return err
	}
	
	// 插入或更新数据
	sql := `
	INSERT INTO ` + s.parametersTableName + ` (parameters, updated_at)
	VALUES (?, CURRENT_TIMESTAMP)
	`
	
	if err := s.db.Exec(ctx, sql, string(parametersJSON)); err != nil {
		return err
	}
	
	// 保留最新的10条记录
	cleanupSQL := `
	DELETE FROM ` + s.parametersTableName + `
	WHERE id NOT IN (
		SELECT id FROM ` + s.parametersTableName + `
		ORDER BY updated_at DESC
		LIMIT 10
	)
	`
	
	if err := s.db.Exec(ctx, cleanupSQL); err != nil {
		s.logger.Warn("清理旧参数记录失败", "error", err)
	}
	
	return nil
}

// LoadParameters 加载学习参数
func (s *SQLiteFeedbackStorage) LoadParameters(ctx context.Context) (map[string]interface{}, error) {
	sql := `
	SELECT parameters
	FROM ` + s.parametersTableName + `
	ORDER BY updated_at DESC
	LIMIT 1
	`
	
	var parametersJSON string
	err := s.db.QueryRow(ctx, sql, &parametersJSON)
	if err != nil {
		if err == ErrNotFound {
			// 没有参数记录，返回空map
			return make(map[string]interface{}), nil
		}
		return nil, err
	}
	
	// 解析参数
	var parameters map[string]interface{}
	if err := JSONUnmarshal([]byte(parametersJSON), &parameters); err != nil {
		return nil, err
	}
	
	return parameters, nil
}

// GetFeedbackStats 获取反馈统计数据
func (s *SQLiteFeedbackStorage) GetFeedbackStats(ctx context.Context, period string) (map[string]interface{}, error) {
	result := make(map[string]interface{})
	
	// 确定时间范围
	var since time.Time
	now := time.Now()
	
	switch period {
	case "day":
		since = now.AddDate(0, 0, -1)
	case "week":
		since = now.AddDate(0, 0, -7)
	case "month":
		since = now.AddDate(0, -1, 0)
	case "year":
		since = now.AddDate(-1, 0, 0)
	default:
		// 默认为所有时间
		since = time.Time{}
	}
	
	// 总反馈数
	totalSQL := `
	SELECT COUNT(*)
	FROM ` + s.feedbackTableName
	
	var totalCount int
	if err := s.db.QueryRow(ctx, totalSQL, &totalCount); err != nil {
		return nil, err
	}
	result["total_count"] = totalCount
	
	// 时间段内反馈数
	if !since.IsZero() {
		periodSQL := `
		SELECT COUNT(*)
		FROM ` + s.feedbackTableName + `
		WHERE timestamp >= ?
		`
		
		var periodCount int
		if err := s.db.QueryRow(ctx, periodSQL, since, &periodCount); err != nil {
			return nil, err
		}
		result["period_count"] = periodCount
	}
	
	// 各类型反馈数
	typeSQL := `
	SELECT feedback_type, COUNT(*)
	FROM ` + s.feedbackTableName + `
	GROUP BY feedback_type
	`
	
	rows, err := s.db.Query(ctx, typeSQL)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	typeCounts := make(map[string]int)
	for rows.Next() {
		var feedbackType string
		var count int
		
		if err := rows.Scan(&feedbackType, &count); err != nil {
			return nil, err
		}
		
		typeCounts[feedbackType] = count
	}
	result["type_counts"] = typeCounts
	
	// 平均评分
	scoreSQL := `
	SELECT AVG(relevance_score)
	FROM ` + s.feedbackTableName + `
	WHERE relevance_score > 0
	`
	
	var avgScore float64
	if err := s.db.QueryRow(ctx, scoreSQL, &avgScore); err != nil && err != ErrNotFound {
		return nil, err
	}
	result["average_score"] = avgScore
	
	// 最近反馈趋势
	trendSQL := `
	SELECT 
		CAST(strftime('%Y-%m-%d', timestamp) as TEXT) as date,
		COUNT(*) as count
	FROM ` + s.feedbackTableName + `
	WHERE timestamp >= datetime('now', '-30 day')
	GROUP BY date
	ORDER BY date
	`
	
	rows, err = s.db.Query(ctx, trendSQL)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	trends := make(map[string]int)
	for rows.Next() {
		var date string
		var count int
		
		if err := rows.Scan(&date, &count); err != nil {
			return nil, err
		}
		
		trends[date] = count
	}
	result["daily_trends"] = trends
	
	return result, nil
} 