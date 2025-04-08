package database

import (
	"fmt"
	"io/ioutil"
	"path/filepath"
	"strings"
	"time"

	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq" // postgres驱动
	"github.com/suoke-life/shared/pkg/logger"
	"github.com/suoke-life/user-service/internal/config"
)

// Manager 数据库管理器
type Manager struct {
	DB     *sqlx.DB
	Config *config.DatabaseConfig
	Logger logger.Logger
}

// NewManager 创建新的数据库管理器
func NewManager(cfg *config.DatabaseConfig, log logger.Logger) (*Manager, error) {
	log = log.With("component", "database")
	log.Info("初始化数据库连接", "host", cfg.Host, "db", cfg.DBName)

	dsn := cfg.GetDatabaseDSN()
	db, err := sqlx.Connect("postgres", dsn)
	if err != nil {
		log.Error("连接数据库失败", "error", err)
		return nil, fmt.Errorf("连接数据库失败: %w", err)
	}

	// 配置连接池
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(5 * time.Minute)

	return &Manager{
		DB:     db,
		Config: cfg,
		Logger: log,
	}, nil
}

// Close 关闭数据库连接
func (m *Manager) Close() error {
	m.Logger.Info("关闭数据库连接")
	return m.DB.Close()
}

// Ping 检查数据库连接
func (m *Manager) Ping() error {
	m.Logger.Debug("Ping数据库")
	return m.DB.Ping()
}

// RunMigrations 运行数据库迁移
func (m *Manager) RunMigrations() error {
	m.Logger.Info("运行数据库迁移")
	
	// 创建迁移表（如果不存在）
	err := m.createMigrationsTable()
	if err != nil {
		return fmt.Errorf("创建迁移表失败: %w", err)
	}
	
	// 获取已执行的迁移
	appliedMigrations, err := m.getAppliedMigrations()
	if err != nil {
		return fmt.Errorf("获取已执行迁移失败: %w", err)
	}
	
	// 迁移文件目录
	migrationsDir := "./internal/database/migrations"
	
	// 读取迁移文件
	files, err := ioutil.ReadDir(migrationsDir)
	if err != nil {
		return fmt.Errorf("读取迁移目录失败: %w", err)
	}
	
	// 按文件名排序
	var migrationFiles []string
	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".sql") {
			migrationFiles = append(migrationFiles, file.Name())
		}
	}
	
	// 执行未应用的迁移
	for _, filename := range migrationFiles {
		if !contains(appliedMigrations, filename) {
			m.Logger.Info("应用迁移", "file", filename)
			
			// 读取迁移文件内容
			content, err := ioutil.ReadFile(filepath.Join(migrationsDir, filename))
			if err != nil {
				return fmt.Errorf("读取迁移文件失败 %s: %w", filename, err)
			}
			
			// 分割Up和Down部分
			parts := strings.Split(string(content), "-- +migrate Down")
			upSQL := parts[0]
			
			// 执行迁移
			tx, err := m.DB.Beginx()
			if err != nil {
				return fmt.Errorf("开始事务失败: %w", err)
			}
			
			_, err = tx.Exec(upSQL)
			if err != nil {
				tx.Rollback()
				return fmt.Errorf("执行迁移失败 %s: %w", filename, err)
			}
			
			// 记录迁移
			_, err = tx.Exec("INSERT INTO schema_migrations (version, applied_at) VALUES ($1, $2)",
				filename, time.Now())
			if err != nil {
				tx.Rollback()
				return fmt.Errorf("记录迁移失败 %s: %w", filename, err)
			}
			
			if err := tx.Commit(); err != nil {
				return fmt.Errorf("提交事务失败: %w", err)
			}
			
			m.Logger.Info("迁移成功应用", "file", filename)
		}
	}
	
	return nil
}

// createMigrationsTable 创建迁移表
func (m *Manager) createMigrationsTable() error {
	query := `
	CREATE TABLE IF NOT EXISTS schema_migrations (
		version VARCHAR(255) PRIMARY KEY,
		applied_at TIMESTAMP WITH TIME ZONE NOT NULL
	)`
	
	_, err := m.DB.Exec(query)
	return err
}

// getAppliedMigrations 获取已应用的迁移
func (m *Manager) getAppliedMigrations() ([]string, error) {
	var migrations []string
	
	err := m.DB.Select(&migrations, "SELECT version FROM schema_migrations ORDER BY version ASC")
	if err != nil {
		return nil, err
	}
	
	return migrations, nil
}

// contains 检查数组是否包含特定值
func contains(arr []string, str string) bool {
	for _, a := range arr {
		if a == str {
			return true
		}
	}
	return false
}

// GetDB 获取数据库连接
func (m *Manager) GetDB() *sqlx.DB {
	return m.DB
} 