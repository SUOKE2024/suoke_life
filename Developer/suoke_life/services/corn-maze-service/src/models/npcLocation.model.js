/**
 * NPC位置模型
 * 用于管理NPC的位置信息
 */
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const npcLocationSchema = new Schema({
  // NPC ID
  npcId: {
    type: String,
    required: true,
    index: true,
    default: 'laoke'
  },
  
  // 位置名称
  name: {
    type: String,
    required: true
  },
  
  // 位置描述
  description: {
    type: String
  },
  
  // 地理位置
  location: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point'
    },
    coordinates: {
      type: [Number], // [longitude, latitude]
      required: true
    },
    altitude: {
      type: Number,
      default: 0
    }
  },
  
  // 所在迷宫ID
  mazeId: {
    type: Schema.Types.ObjectId,
    ref: 'Maze',
    index: true
  },
  
  // 影响范围（米）
  radius: {
    type: Number,
    default: 50
  },
  
  // 是否活跃
  isActive: {
    type: Boolean,
    default: true,
    index: true
  },
  
  // 开始时间
  startTime: {
    type: Date,
    default: Date.now
  },
  
  // 结束时间（如果有）
  endTime: {
    type: Date
  },
  
  // 移动路径（如果NPC是移动的）
  movementPath: [{
    coordinates: {
      type: [Number], // [longitude, latitude]
      required: true
    },
    stayDuration: {
      type: Number, // 停留时间（分钟）
      default: 60
    },
    arrivalTime: Date
  }],
  
  // 互动条件
  interactionConditions: {
    timeRestricted: {
      type: Boolean,
      default: false
    },
    timeWindows: [{
      dayOfWeek: {
        type: Number, // 0-6 表示周日到周六
        required: true
      },
      startHour: {
        type: Number, // 0-23
        required: true
      },
      endHour: {
        type: Number, // 0-23
        required: true
      }
    }],
    weatherDependent: {
      type: Boolean,
      default: false
    },
    allowedWeather: [{
      type: String,
      enum: ['sunny', 'cloudy', 'rainy', 'snowy', 'windy', 'foggy']
    }],
    requiresQuest: {
      type: Boolean,
      default: false
    },
    questId: {
      type: Schema.Types.ObjectId,
      ref: 'Quest'
    }
  },
  
  // 特殊属性
  properties: {
    hasCornKnowledge: {
      type: Boolean,
      default: true
    },
    offersQuests: {
      type: Boolean,
      default: true
    },
    sharesSecrets: {
      type: Boolean,
      default: false
    },
    sellsItems: {
      type: Boolean,
      default: false
    }
  },
  
  // 自定义头像和标记
  visuals: {
    avatarUrl: String,
    markerUrl: String,
    markerColor: {
      type: String,
      default: '#35BB78' // 索克绿
    },
    scaleSize: {
      type: Number,
      default: 1.0
    }
  },
  
  // 元数据
  metadata: Schema.Types.Mixed
}, {
  timestamps: true
});

// 索引优化
npcLocationSchema.index({ 'location.coordinates': '2dsphere' });
npcLocationSchema.index({ npcId: 1, isActive: 1 });
npcLocationSchema.index({ mazeId: 1, isActive: 1 });
npcLocationSchema.index({ startTime: 1, endTime: 1 });

// 方法：检查是否在范围内
npcLocationSchema.methods.isInRange = function(longitude, latitude) {
  // 使用MongoDB的$geoNear查询
  return mongoose.models.NPCLocation.findOne({
    _id: this._id,
    isActive: true,
    'location.coordinates': {
      $nearSphere: {
        $geometry: {
          type: 'Point',
          coordinates: [parseFloat(longitude), parseFloat(latitude)]
        },
        $maxDistance: this.radius
      }
    }
  }).lean();
};

// 方法：检查是否在活动时间内
npcLocationSchema.methods.isAvailableNow = function() {
  const now = new Date();
  
  // 检查开始和结束时间
  if (this.endTime && now > this.endTime) {
    return false;
  }
  
  if (now < this.startTime) {
    return false;
  }
  
  // 检查时间窗口限制
  if (this.interactionConditions.timeRestricted) {
    const dayOfWeek = now.getDay();
    const currentHour = now.getHours();
    
    const inTimeWindow = this.interactionConditions.timeWindows.some(window => {
      return window.dayOfWeek === dayOfWeek && 
             currentHour >= window.startHour && 
             currentHour < window.endHour;
    });
    
    if (!inTimeWindow) {
      return false;
    }
  }
  
  return true;
};

// 方法：获取当前位置
npcLocationSchema.methods.getCurrentPosition = function() {
  // 如果NPC不移动，则返回固定位置
  if (!this.movementPath || this.movementPath.length === 0) {
    return this.location.coordinates;
  }
  
  const now = new Date();
  
  // 找到当前或最近的路径点
  let currentPosition = this.location.coordinates; // 默认位置
  
  // 按照到达时间排序
  const sortedPath = [...this.movementPath].sort((a, b) => 
    a.arrivalTime && b.arrivalTime ? a.arrivalTime - b.arrivalTime : 0
  );
  
  for (let i = 0; i < sortedPath.length; i++) {
    const point = sortedPath[i];
    
    if (!point.arrivalTime) continue;
    
    // 如果点的到达时间在未来，继续使用上一个位置
    if (point.arrivalTime > now) {
      break;
    }
    
    // 如果在当前停留时间内
    const stayUntil = new Date(point.arrivalTime);
    stayUntil.setMinutes(stayUntil.getMinutes() + (point.stayDuration || 0));
    
    if (now <= stayUntil) {
      currentPosition = point.coordinates;
      break;
    }
    
    // 如果这是最后一个点或已经超过停留时间
    if (i === sortedPath.length - 1 || now > stayUntil) {
      currentPosition = point.coordinates;
    }
  }
  
  return currentPosition;
};

// 静态方法：查找附近的NPC
npcLocationSchema.statics.findNearby = function(coordinates, maxDistance = 100) {
  return this.find({
    isActive: true,
    'location.coordinates': {
      $nearSphere: {
        $geometry: {
          type: 'Point',
          coordinates
        },
        $maxDistance: maxDistance
      }
    }
  }).lean();
};

// 静态方法：查找迷宫中的所有NPC
npcLocationSchema.statics.findInMaze = function(mazeId) {
  return this.find({
    mazeId,
    isActive: true
  }).lean();
};

// 创建模型
const NPCLocation = mongoose.model('NPCLocation', npcLocationSchema);

module.exports = NPCLocation; 