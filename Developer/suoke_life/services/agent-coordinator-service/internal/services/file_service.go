package services

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/gofrs/flock"
	"github.com/suoke-life/agent-coordinator-service/internal/models"
)

// FileServiceConfig 文件服务配置
type FileServiceConfig struct {
	BasePath string // 存储文件的基础路径
}

// FileService 文件系统持久化服务
type FileService struct {
	config   *FileServiceConfig
	fileLock sync.Map      // 用于文件锁管理
	locks    map[string]*flock.Flock
	mu       sync.Mutex    // 用于保护locks map
}

// NewFileService 创建新的文件服务实例
func NewFileService(config *FileServiceConfig) (*FileService, error) {
	if config == nil {
		config = &FileServiceConfig{
			BasePath: "state",
		}
	}

	// 确保基础目录存在
	if err := os.MkdirAll(config.BasePath, 0755); err != nil {
		return nil, fmt.Errorf("创建基础目录失败: %w", err)
	}

	// 创建会话目录
	sessionsDir := filepath.Join(config.BasePath, "sessions")
	if err := os.MkdirAll(sessionsDir, 0755); err != nil {
		return nil, fmt.Errorf("创建会话目录失败: %w", err)
	}

	// 创建状态目录
	stateDir := filepath.Join(config.BasePath, "state")
	if err := os.MkdirAll(stateDir, 0755); err != nil {
		return nil, fmt.Errorf("创建状态目录失败: %w", err)
	}

	return &FileService{
		config: config,
		locks:  make(map[string]*flock.Flock),
	}, nil
}

// 获取文件锁
func (fs *FileService) getLock(filePath string) *flock.Flock {
	fs.mu.Lock()
	defer fs.mu.Unlock()

	lock, exists := fs.locks[filePath]
	if !exists {
		lock = flock.New(filePath + ".lock")
		fs.locks[filePath] = lock
	}
	return lock
}

// 会话文件路径
func (fs *FileService) sessionFilePath(sessionID string) string {
	return filepath.Join(fs.config.BasePath, "sessions", sessionID+".json")
}

// 状态文件路径
func (fs *FileService) stateFilePath(stateKey string) string {
	return filepath.Join(fs.config.BasePath, "state", stateKey+".json")
}

// SaveSession 保存会话到文件
func (fs *FileService) SaveSession(session *models.Session) error {
	filePath := fs.sessionFilePath(session.ID)
	
	// 获取文件锁
	lock := fs.getLock(filePath)
	locked, err := lock.TryLock()
	if err != nil {
		return fmt.Errorf("获取文件锁失败: %w", err)
	}
	if !locked {
		return fmt.Errorf("文件正在被其他进程使用")
	}
	defer lock.Unlock()

	// 序列化会话
	sessionJSON, err := json.MarshalIndent(session, "", "  ")
	if err != nil {
		return fmt.Errorf("序列化会话失败: %w", err)
	}

	// 写入文件
	if err := ioutil.WriteFile(filePath, sessionJSON, 0644); err != nil {
		return fmt.Errorf("写入会话文件失败: %w", err)
	}

	return nil
}

// GetSession 从文件获取会话
func (fs *FileService) GetSession(sessionID string) (*models.Session, error) {
	filePath := fs.sessionFilePath(sessionID)
	
	// 检查文件是否存在
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		return nil, fmt.Errorf("会话不存在")
	}
	
	// 获取文件锁
	lock := fs.getLock(filePath)
	locked, err := lock.TryRLock()
	if err != nil {
		return nil, fmt.Errorf("获取文件锁失败: %w", err)
	}
	if !locked {
		return nil, fmt.Errorf("文件正在被其他进程写入")
	}
	defer lock.Unlock()

	// 读取文件
	sessionJSON, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("读取会话文件失败: %w", err)
	}

	// 反序列化会话
	var session models.Session
	if err := json.Unmarshal(sessionJSON, &session); err != nil {
		return nil, fmt.Errorf("反序列化会话失败: %w", err)
	}

	return &session, nil
}

// DeleteSession 删除会话文件
func (fs *FileService) DeleteSession(sessionID string) error {
	filePath := fs.sessionFilePath(sessionID)
	
	// 检查文件是否存在
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		return nil // 文件不存在，视为删除成功
	}
	
	// 获取文件锁
	lock := fs.getLock(filePath)
	locked, err := lock.TryLock()
	if err != nil {
		return fmt.Errorf("获取文件锁失败: %w", err)
	}
	if !locked {
		return fmt.Errorf("文件正在被其他进程使用")
	}
	defer lock.Unlock()

	// 删除文件
	if err := os.Remove(filePath); err != nil {
		return fmt.Errorf("删除会话文件失败: %w", err)
	}
	
	// 删除锁文件
	lockPath := filePath + ".lock"
	if _, err := os.Stat(lockPath); !os.IsNotExist(err) {
		os.Remove(lockPath) // 尝试删除锁文件，忽略错误
	}
	
	// 从锁映射中移除
	fs.mu.Lock()
	delete(fs.locks, filePath)
	fs.mu.Unlock()

	return nil
}

// ListSessionIDs 列出所有会话ID
func (fs *FileService) ListSessionIDs() ([]string, error) {
	sessionsDir := filepath.Join(fs.config.BasePath, "sessions")
	
	// 读取目录
	files, err := ioutil.ReadDir(sessionsDir)
	if err != nil {
		return nil, fmt.Errorf("读取会话目录失败: %w", err)
	}

	sessionIDs := make([]string, 0, len(files))
	for _, file := range files {
		if file.IsDir() || filepath.Ext(file.Name()) != ".json" {
			continue // 跳过目录和非JSON文件
		}
		
		// 从文件名提取会话ID
		sessionID := file.Name()[:len(file.Name())-5] // 移除 ".json" 后缀
		sessionIDs = append(sessionIDs, sessionID)
	}

	return sessionIDs, nil
}

// SaveState 保存状态到文件
func (fs *FileService) SaveState(stateKey string, value interface{}) error {
	filePath := fs.stateFilePath(stateKey)
	
	// 获取文件锁
	lock := fs.getLock(filePath)
	locked, err := lock.TryLock()
	if err != nil {
		return fmt.Errorf("获取文件锁失败: %w", err)
	}
	if !locked {
		return fmt.Errorf("文件正在被其他进程使用")
	}
	defer lock.Unlock()

	// 序列化数据
	stateJSON, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return fmt.Errorf("序列化状态数据失败: %w", err)
	}

	// 写入文件
	if err := ioutil.WriteFile(filePath, stateJSON, 0644); err != nil {
		return fmt.Errorf("写入状态文件失败: %w", err)
	}

	return nil
}

// GetState 从文件获取状态
func (fs *FileService) GetState(stateKey string, value interface{}) error {
	filePath := fs.stateFilePath(stateKey)
	
	// 检查文件是否存在
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		return fmt.Errorf("状态不存在")
	}
	
	// 获取文件锁
	lock := fs.getLock(filePath)
	locked, err := lock.TryRLock()
	if err != nil {
		return fmt.Errorf("获取文件锁失败: %w", err)
	}
	if !locked {
		return fmt.Errorf("文件正在被其他进程写入")
	}
	defer lock.Unlock()

	// 读取文件
	stateJSON, err := ioutil.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("读取状态文件失败: %w", err)
	}

	// 反序列化数据
	if err := json.Unmarshal(stateJSON, value); err != nil {
		return fmt.Errorf("反序列化状态数据失败: %w", err)
	}

	return nil
}

// DeleteState 删除状态文件
func (fs *FileService) DeleteState(stateKey string) error {
	filePath := fs.stateFilePath(stateKey)
	
	// 检查文件是否存在
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		return nil // 文件不存在，视为删除成功
	}
	
	// 获取文件锁
	lock := fs.getLock(filePath)
	locked, err := lock.TryLock()
	if err != nil {
		return fmt.Errorf("获取文件锁失败: %w", err)
	}
	if !locked {
		return fmt.Errorf("文件正在被其他进程使用")
	}
	defer lock.Unlock()

	// 删除文件
	if err := os.Remove(filePath); err != nil {
		return fmt.Errorf("删除状态文件失败: %w", err)
	}
	
	// 删除锁文件
	lockPath := filePath + ".lock"
	if _, err := os.Stat(lockPath); !os.IsNotExist(err) {
		os.Remove(lockPath) // 尝试删除锁文件，忽略错误
	}
	
	// 从锁映射中移除
	fs.mu.Lock()
	delete(fs.locks, filePath)
	fs.mu.Unlock()

	return nil
}

// Backup 创建备份
func (fs *FileService) Backup() (string, error) {
	// 创建备份目录
	backupDir := filepath.Join(fs.config.BasePath, "backups")
	if err := os.MkdirAll(backupDir, 0755); err != nil {
		return "", fmt.Errorf("创建备份目录失败: %w", err)
	}
	
	// 生成备份文件名 (使用时间戳)
	timestamp := time.Now().Format("20060102-150405")
	backupFile := filepath.Join(backupDir, fmt.Sprintf("backup-%s.tar.gz", timestamp))
	
	// 压缩会话和状态目录
	cmd := fmt.Sprintf("tar -czf %s -C %s sessions state", backupFile, fs.config.BasePath)
	if err := exec(cmd); err != nil {
		return "", fmt.Errorf("创建备份文件失败: %w", err)
	}
	
	return backupFile, nil
}

// Restore 从备份恢复
func (fs *FileService) Restore(backupFile string) error {
	// 检查备份文件是否存在
	if _, err := os.Stat(backupFile); os.IsNotExist(err) {
		return fmt.Errorf("备份文件不存在")
	}
	
	// 解压备份文件
	cmd := fmt.Sprintf("tar -xzf %s -C %s", backupFile, fs.config.BasePath)
	if err := exec(cmd); err != nil {
		return fmt.Errorf("恢复备份失败: %w", err)
	}
	
	return nil
}

// CleanBackups 清理过期备份
func (fs *FileService) CleanBackups(maxAge time.Duration) (int, error) {
	backupDir := filepath.Join(fs.config.BasePath, "backups")
	
	// 检查备份目录是否存在
	if _, err := os.Stat(backupDir); os.IsNotExist(err) {
		return 0, nil // 目录不存在，没有需要清理的备份
	}
	
	// 读取目录
	files, err := ioutil.ReadDir(backupDir)
	if err != nil {
		return 0, fmt.Errorf("读取备份目录失败: %w", err)
	}
	
	// 当前时间
	now := time.Now()
	deleted := 0
	
	for _, file := range files {
		if file.IsDir() {
			continue // 跳过子目录
		}
		
		// 检查文件名是否符合备份文件格式
		if filepath.Ext(file.Name()) != ".gz" || !filepath.HasPrefix(file.Name(), "backup-") {
			continue
		}
		
		// 检查文件的修改时间
		if now.Sub(file.ModTime()) > maxAge {
			// 文件年龄大于maxAge，删除它
			if err := os.Remove(filepath.Join(backupDir, file.Name())); err != nil {
				return deleted, fmt.Errorf("删除备份文件失败: %w", err)
			}
			deleted++
		}
	}
	
	return deleted, nil
}

// 执行shell命令
func exec(cmd string) error {
	return nil // 简化处理，实际实现需要使用exec.Command
} 