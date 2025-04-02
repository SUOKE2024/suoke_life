"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ActivityRegistrationModel = exports.ActivityModel = exports.RegistrationStatus = exports.ActivityStatus = exports.ActivityCategory = void 0;
const mongoose_1 = __importStar(require("mongoose"));
/**
 * 活动类别枚举
 */
var ActivityCategory;
(function (ActivityCategory) {
    ActivityCategory["PLANTING"] = "planting";
    ActivityCategory["HARVESTING"] = "harvesting";
    ActivityCategory["WORKSHOP"] = "workshop";
    ActivityCategory["TOUR"] = "tour";
    ActivityCategory["WELLNESS"] = "wellness";
    ActivityCategory["SEASONAL"] = "seasonal";
    ActivityCategory["CHILDREN"] = "children";
    ActivityCategory["OTHER"] = "other"; // 其他
})(ActivityCategory || (exports.ActivityCategory = ActivityCategory = {}));
/**
 * 活动状态枚举
 */
var ActivityStatus;
(function (ActivityStatus) {
    ActivityStatus["UPCOMING"] = "upcoming";
    ActivityStatus["ONGOING"] = "ongoing";
    ActivityStatus["COMPLETED"] = "completed";
    ActivityStatus["CANCELLED"] = "cancelled"; // 已取消
})(ActivityStatus || (exports.ActivityStatus = ActivityStatus = {}));
/**
 * 预约状态枚举
 */
var RegistrationStatus;
(function (RegistrationStatus) {
    RegistrationStatus["PENDING"] = "pending";
    RegistrationStatus["CONFIRMED"] = "confirmed";
    RegistrationStatus["CANCELLED"] = "cancelled";
    RegistrationStatus["COMPLETED"] = "completed";
    RegistrationStatus["NO_SHOW"] = "no_show"; // 未出席
})(RegistrationStatus || (exports.RegistrationStatus = RegistrationStatus = {}));
// 活动评价子文档Schema
const reviewSchema = new mongoose_1.Schema({
    userId: { type: String, required: true },
    rating: { type: Number, required: true, min: 1, max: 5 },
    comment: { type: String, required: true },
    date: { type: String, required: true }, // ISO格式日期字符串
    photoUrls: [String]
}, { _id: false });
// 活动Schema
const activitySchema = new mongoose_1.Schema({
    name: {
        type: String,
        required: true,
        trim: true,
        index: true
    },
    description: {
        type: String,
        required: true
    },
    location: {
        type: String,
        required: true,
        index: true
    },
    startDate: {
        type: String,
        required: true,
        index: true
    },
    endDate: {
        type: String,
        required: true
    },
    status: {
        type: String,
        enum: Object.values(ActivityStatus),
        default: ActivityStatus.UPCOMING,
        index: true
    },
    capacity: {
        type: Number,
        required: true,
        min: 1
    },
    currentRegistrations: {
        type: Number,
        default: 0
    },
    price: {
        type: Number,
        required: true,
        min: 0
    },
    category: {
        type: String,
        enum: Object.values(ActivityCategory),
        required: true,
        index: true
    },
    organizer: {
        type: String,
        required: true
    },
    contactInfo: {
        type: String,
        required: true
    },
    images: [{
            type: String
        }],
    requirements: {
        type: String
    },
    included: {
        type: String
    },
    reviews: [reviewSchema],
    metadata: {
        type: mongoose_1.Schema.Types.Mixed
    }
}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});
// 虚拟字段：剩余容量
activitySchema.virtual('remainingCapacity').get(function () {
    return this.capacity - this.currentRegistrations;
});
// 虚拟字段：当前状态自动更新
activitySchema.pre('save', function (next) {
    const now = new Date().toISOString();
    if (now < this.startDate) {
        this.status = ActivityStatus.UPCOMING;
    }
    else if (now >= this.startDate && now <= this.endDate) {
        this.status = ActivityStatus.ONGOING;
    }
    else if (now > this.endDate) {
        this.status = ActivityStatus.COMPLETED;
    }
    next();
});
// 活动注册Schema
const activityRegistrationSchema = new mongoose_1.Schema({
    activityId: {
        type: String,
        required: true,
        index: true
    },
    userId: {
        type: String,
        required: true,
        index: true
    },
    participants: {
        type: Number,
        required: true,
        min: 1
    },
    registrationDate: {
        type: String,
        required: true
    },
    status: {
        type: String,
        enum: Object.values(RegistrationStatus),
        default: RegistrationStatus.PENDING,
        index: true
    },
    paymentId: {
        type: String
    },
    notes: {
        type: String
    },
    metadata: {
        type: mongoose_1.Schema.Types.Mixed
    }
}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});
// 创建复合索引
activityRegistrationSchema.index({ userId: 1, activityId: 1 }, { unique: true });
// 创建模型
exports.ActivityModel = mongoose_1.default.model('Activity', activitySchema);
exports.ActivityRegistrationModel = mongoose_1.default.model('ActivityRegistration', activityRegistrationSchema);
