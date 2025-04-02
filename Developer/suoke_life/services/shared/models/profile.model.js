/**
 * 用户个人资料模型
 * 定义用户个人资料数据结构和验证规则
 */
const mongoose = require('mongoose');
const { Schema } = mongoose;

/**
 * 个人资料模式定义
 */
const profileSchema = new Schema({
  // 与用户的关联
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, '用户ID是必填项'],
    unique: true
  },
  
  // 基本信息
  nickname: {
    type: String,
    trim: true,
    maxlength: [30, '昵称不能超过30个字符']
  },
  avatar: {
    type: String,
    default: '/assets/default-avatar.png'
  },
  gender: {
    type: String,
    enum: ['male', 'female', 'other', 'prefer_not_to_say'],
    default: 'prefer_not_to_say'
  },
  dateOfBirth: Date,
  bio: {
    type: String,
    maxlength: [500, '个人简介不能超过500个字符']
  },
  
  // 联系信息
  address: {
    province: String,
    city: String,
    district: String,
    detail: String
  },
  emergencyContact: {
    name: String,
    phone: String,
    relationship: String
  },
  
  // 偏好设置
  preferences: {
    theme: {
      type: String,
      enum: ['light', 'dark', 'system'],
      default: 'system'
    },
    language: {
      type: String,
      enum: ['zh_CN', 'en_US'],
      default: 'zh_CN'
    },
    notifications: {
      email: {
        type: Boolean,
        default: true
      },
      push: {
        type: Boolean,
        default: true
      },
      sms: {
        type: Boolean,
        default: false
      }
    },
    privacySettings: {
      shareHealthData: {
        type: Boolean,
        default: false
      },
      shareFitnessData: {
        type: Boolean,
        default: false
      },
      allowLocationTracking: {
        type: Boolean,
        default: false
      }
    }
  },
  
  // 健康信息
  healthInfo: {
    height: {
      type: Number, // 身高（厘米）
      min: [50, '身高不能小于50厘米'],
      max: [250, '身高不能大于250厘米']
    },
    weight: {
      type: Number, // 体重（千克）
      min: [20, '体重不能小于20千克'],
      max: [300, '体重不能大于300千克']
    },
    bloodType: {
      type: String,
      enum: ['A', 'B', 'AB', 'O', 'unknown'],
      default: 'unknown'
    },
    allergies: [{
      type: String,
      trim: true
    }],
    chronicDiseases: [{
      type: String,
      trim: true
    }],
    medications: [{
      name: String,
      dosage: String,
      frequency: String,
      startDate: Date,
      endDate: Date
    }]
  },
  
  // 中医体质信息
  tcmConstitution: {
    primaryType: {
      type: String,
      enum: [
        'balanced', // 平和质
        'qi_deficiency', // 气虚质
        'yang_deficiency', // 阳虚质
        'yin_deficiency', // 阴虚质
        'phlegm_dampness', // 痰湿质
        'damp_heat', // 湿热质
        'blood_stasis', // 血瘀质
        'qi_stagnation', // 气郁质
        'special', // 特禀质
        'unknown' // 未知
      ],
      default: 'unknown'
    },
    secondaryTypes: [{
      type: String,
      enum: [
        'qi_deficiency', // 气虚质
        'yang_deficiency', // 阳虚质
        'yin_deficiency', // 阴虚质
        'phlegm_dampness', // 痰湿质
        'damp_heat', // 湿热质
        'blood_stasis', // 血瘀质
        'qi_stagnation', // 气郁质
        'special' // 特禀质
      ]
    }],
    lastAssessmentDate: Date,
    assessmentScore: {
      balanced: Number, // 平和质得分
      qi_deficiency: Number, // 气虚质得分
      yang_deficiency: Number, // 阳虚质得分
      yin_deficiency: Number, // 阴虚质得分
      phlegm_dampness: Number, // 痰湿质得分
      damp_heat: Number, // 湿热质得分
      blood_stasis: Number, // 血瘀质得分
      qi_stagnation: Number, // 气郁质得分
      special: Number // 特禀质得分
    }
  },
  
  // 活动和成就
  activities: {
    steps: {
      type: Number,
      default: 0
    },
    totalDistance: {
      type: Number, // 总距离（米）
      default: 0
    },
    meditationMinutes: {
      type: Number,
      default: 0
    },
    sleepAverage: {
      type: Number, // 平均睡眠时间（小时）
      default: 0
    }
  },
  badges: [{
    id: String,
    name: String,
    description: String,
    imageUrl: String,
    earnedAt: Date
  }],
  
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
profileSchema.index({ userId: 1 }, { unique: true });
profileSchema.index({ 'tcmConstitution.primaryType': 1 });
profileSchema.index({ 'healthInfo.bloodType': 1 });

/**
 * 虚拟属性 - 用户年龄
 */
profileSchema.virtual('age').get(function() {
  if (!this.dateOfBirth) return null;
  
  const ageDifMs = Date.now() - this.dateOfBirth.getTime();
  const ageDate = new Date(ageDifMs);
  return Math.abs(ageDate.getUTCFullYear() - 1970);
});

/**
 * 虚拟属性 - BMI计算
 */
profileSchema.virtual('bmi').get(function() {
  const { height, weight } = this.healthInfo;
  
  if (!height || !weight) return null;
  
  // BMI = 体重(kg) / 身高(m)²
  const heightInMeters = height / 100;
  return (weight / (heightInMeters * heightInMeters)).toFixed(1);
});

/**
 * 虚拟属性 - BMI分类
 */
profileSchema.virtual('bmiCategory').get(function() {
  const bmi = this.bmi;
  
  if (!bmi) return null;
  
  if (bmi < 18.5) return 'underweight'; // 偏瘦
  if (bmi < 24) return 'normal'; // 正常
  if (bmi < 28) return 'overweight'; // 偏胖
  return 'obese'; // 肥胖
});

/**
 * 实例方法 - 获取体质评估结果
 * @returns {Object} 体质评估结果
 */
profileSchema.methods.getConstitutionAssessment = function() {
  const { primaryType, secondaryTypes, assessmentScore } = this.tcmConstitution;
  
  return {
    primaryType,
    secondaryTypes: secondaryTypes || [],
    scores: assessmentScore || {},
    lastAssessedAt: this.tcmConstitution.lastAssessmentDate
  };
};

/**
 * 实例方法 - 更新用户体质评估
 * @param {Object} assessment - 体质评估数据
 * @returns {Promise<Profile>} 更新后的档案
 */
profileSchema.methods.updateConstitutionAssessment = async function(assessment) {
  this.tcmConstitution = {
    ...this.tcmConstitution,
    ...assessment,
    lastAssessmentDate: new Date()
  };
  
  return this.save();
};

/**
 * 实例方法 - 添加徽章
 * @param {Object} badge - 徽章信息
 * @returns {Promise<Profile>} 更新后的档案
 */
profileSchema.methods.addBadge = async function(badge) {
  // 检查徽章是否已存在
  const badgeExists = this.badges.some(b => b.id === badge.id);
  
  if (!badgeExists) {
    this.badges.push({
      ...badge,
      earnedAt: new Date()
    });
    
    return this.save();
  }
  
  return this;
};

/**
 * 创建模型
 */
const Profile = mongoose.model('Profile', profileSchema);

module.exports = Profile; 