/**
 * 数据库表结构定义
 */

// ... existing code ...

// 用户会话表结构
const USER_SESSIONS_SCHEMA = `
CREATE TABLE IF NOT EXISTS user_sessions (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  token_id VARCHAR(36) NOT NULL,
  device_info TEXT NOT NULL,
  ip_address VARCHAR(45),
  user_agent TEXT,
  location TEXT,
  is_current BOOLEAN DEFAULT FALSE,
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_active_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token_id ON user_sessions(token_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_status ON user_sessions(status);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
`;

// 二因素认证恢复码表结构
const TWO_FACTOR_RECOVERY_CODES_SCHEMA = `
CREATE TABLE IF NOT EXISTS two_factor_recovery_codes (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  code_hash VARCHAR(255) NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  used_at TIMESTAMP NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_two_factor_recovery_codes_user_id ON two_factor_recovery_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_two_factor_recovery_codes_used ON two_factor_recovery_codes(used);
`;

// 用户安全设置表结构
const USER_SECURITY_SETTINGS_SCHEMA = `
CREATE TABLE IF NOT EXISTS user_security_settings (
  user_id VARCHAR(36) PRIMARY KEY,
  two_factor_enabled BOOLEAN DEFAULT FALSE,
  two_factor_secret VARCHAR(255),
  two_factor_backup_codes TEXT,
  password_last_changed TIMESTAMP,
  security_questions_answers TEXT,
  session_timeout_minutes INTEGER DEFAULT 30,
  max_sessions INTEGER DEFAULT 5,
  device_verification_required BOOLEAN DEFAULT FALSE,
  suspicious_activity_notifications_enabled BOOLEAN DEFAULT TRUE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
`;

// 用户设备表结构
const USER_DEVICES_SCHEMA = `
CREATE TABLE IF NOT EXISTS user_devices (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  device_type VARCHAR(20) NOT NULL,
  device_name VARCHAR(100) NOT NULL,
  os_name VARCHAR(50) NOT NULL,
  os_version VARCHAR(50) NOT NULL,
  browser_name VARCHAR(50) NOT NULL,
  browser_version VARCHAR(50) NOT NULL,
  device_fingerprint VARCHAR(64) NOT NULL,
  is_trusted BOOLEAN DEFAULT FALSE,
  last_used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_user_devices_user_id ON user_devices(user_id);
CREATE INDEX IF NOT EXISTS idx_user_devices_device_fingerprint ON user_devices(device_fingerprint);
CREATE INDEX IF NOT EXISTS idx_user_devices_is_trusted ON user_devices(is_trusted);
CREATE INDEX IF NOT EXISTS idx_user_devices_last_used_at ON user_devices(last_used_at);
`;

// ... existing code ...

module.exports = {
  // ... existing exports ...
  USER_SESSIONS_SCHEMA,
  TWO_FACTOR_RECOVERY_CODES_SCHEMA,
  USER_SECURITY_SETTINGS_SCHEMA,
  USER_DEVICES_SCHEMA,
  // ... existing exports ...
}; 