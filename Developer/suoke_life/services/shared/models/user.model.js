/**
 * 用户模型
 * 定义用户数据结构和验证规则
 */
const mongoose = require('mongoose');
const { Schema } = mongoose;
const bcrypt = require('bcrypt');

/**
 * 用户模式定义
 */
const userSchema = new Schema({
  // 基本信息
  username: {
    type: String,
    required: [true, '用户名是必填项'],
    unique: true,
    trim: true,
    minlength: [3, '用户名至少需要3个字符'],
    maxlength: [30, '用户名不能超过30个字符']
  },
  email: {
    type: String,
    required: [true, '邮箱是必填项'],
    unique: true,
    trim: true,
    lowercase: true,
    match: [/^\S+@\S+\.\S+$/, '请提供有效的邮箱地址']
  },
  password: {
    type: String,
    required: [true, '密码是必填项'],
    minlength: [8, '密码至少需要8个字符'],
    select: false // 默认查询不返回密码
  },
  phone: {
    type: String,
    trim: true,
    match: [/^1[3-9]\d{9}$/, '请提供有效的手机号码'],
    sparse: true // 允许为null，但如果存在则必须唯一
  },
  
  // 账户状态
  active: {
    type: Boolean,
    default: true
  },
  verified: {
    type: Boolean,
    default: false
  },
  lastLogin: {
    type: Date,
    default: null
  },
  
  // 角色和权限
  role: {
    type: String,
    enum: ['user', 'admin', 'system'],
    default: 'user'
  },
  permissions: [{
    type: String,
    enum: [
      'read:profile', 'write:profile',
      'read:health', 'write:health',
      'read:nutrition', 'write:nutrition',
      'manage:users', 'manage:content',
      'manage:system'
    ]
  }],
  
  // 安全相关
  passwordChangedAt: Date,
  passwordResetToken: String,
  passwordResetExpires: Date,
  loginAttempts: {
    type: Number,
    default: 0
  },
  lockUntil: Date,
  
  // 元数据
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  // 模式选项
  timestamps: true, // 自动管理createdAt和updatedAt
  toJSON: { virtuals: true }, // 在JSON中包含虚拟属性
  toObject: { virtuals: true } // 在对象中包含虚拟属性
});

/**
 * 添加索引
 */
userSchema.index({ email: 1 });
userSchema.index({ username: 1 });
userSchema.index({ phone: 1 }, { sparse: true });

/**
 * 虚拟属性 - 个人资料关联
 */
userSchema.virtual('profile', {
  ref: 'Profile',
  localField: '_id',
  foreignField: 'userId',
  justOne: true
});

/**
 * 中间件 - 保存前密码哈希
 */
userSchema.pre('save', async function(next) {
  // 如果密码没有修改，则跳过
  if (!this.isModified('password')) return next();
  
  try {
    // 生成盐并哈希密码
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
    
    // 如果是修改密码，更新密码修改时间
    if (this.isModified('password') && !this.isNew) {
      this.passwordChangedAt = Date.now() - 1000; // 减去1秒，确保JWT在密码更改后生成
    }
    
    next();
  } catch (error) {
    next(error);
  }
});

/**
 * 实例方法 - 验证密码
 * @param {string} candidatePassword - 待验证的密码
 * @returns {Promise<boolean>} 验证结果
 */
userSchema.methods.verifyPassword = async function(candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

/**
 * 实例方法 - 检查密码是否在指定时间后更改
 * @param {number} JWTTimestamp - JWT的发布时间戳
 * @returns {boolean} 如果密码在JWT发布后更改，则返回true
 */
userSchema.methods.changedPasswordAfter = function(JWTTimestamp) {
  if (this.passwordChangedAt) {
    const changedTimestamp = parseInt(this.passwordChangedAt.getTime() / 1000, 10);
    return JWTTimestamp < changedTimestamp;
  }
  return false;
};

/**
 * 实例方法 - 创建密码重置令牌
 * @returns {string} 密码重置令牌
 */
userSchema.methods.createPasswordResetToken = function() {
  const resetToken = crypto.randomBytes(32).toString('hex');
  
  // 存储加密的重置令牌
  this.passwordResetToken = crypto
    .createHash('sha256')
    .update(resetToken)
    .digest('hex');
    
  // 设置令牌过期时间（1小时）
  this.passwordResetExpires = Date.now() + 3600000;
  
  return resetToken;
};

/**
 * 实例方法 - 检查账户是否被锁定
 * @returns {boolean} 如果账户被锁定，则返回true
 */
userSchema.methods.isLocked = function() {
  return !!(this.lockUntil && this.lockUntil > Date.now());
};

/**
 * 实例方法 - 增加登录尝试次数并在必要时锁定账户
 * @returns {Promise<void>}
 */
userSchema.methods.incrementLoginAttempts = async function() {
  // 如果锁定已过期，重置尝试次数和锁定
  if (this.lockUntil && this.lockUntil < Date.now()) {
    return this.updateOne({
      $set: { loginAttempts: 1 },
      $unset: { lockUntil: 1 }
    });
  }
  
  // 增加尝试次数
  const updates = { $inc: { loginAttempts: 1 } };
  
  // 锁定账户（超过5次失败尝试）
  if (this.loginAttempts + 1 >= 5 && !this.isLocked()) {
    updates.$set = { lockUntil: Date.now() + 3600000 }; // 锁定1小时
  }
  
  return this.updateOne(updates);
};

/**
 * 实例方法 - 重置登录尝试计数器
 * @returns {Promise<void>}
 */
userSchema.methods.resetLoginAttempts = function() {
  return this.updateOne({
    $set: { loginAttempts: 0 },
    $unset: { lockUntil: 1 }
  });
};

/**
 * 静态方法 - 按邮箱查找用户
 * @param {string} email - 用户邮箱
 * @returns {Promise<User>} 用户文档
 */
userSchema.statics.findByEmail = function(email) {
  return this.findOne({ email });
};

/**
 * 创建模型
 */
const User = mongoose.model('User', userSchema);

module.exports = User; 