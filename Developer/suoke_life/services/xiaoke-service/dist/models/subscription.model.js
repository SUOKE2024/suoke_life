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
exports.SubscriptionModel = exports.ServiceType = exports.BillingCycle = exports.SubscriptionStatus = void 0;
const mongoose_1 = __importStar(require("mongoose"));
// 订阅状态枚举
var SubscriptionStatus;
(function (SubscriptionStatus) {
    SubscriptionStatus["ACTIVE"] = "active";
    SubscriptionStatus["PENDING"] = "pending";
    SubscriptionStatus["CANCELED"] = "canceled";
    SubscriptionStatus["EXPIRED"] = "expired";
    SubscriptionStatus["SUSPENDED"] = "suspended";
    SubscriptionStatus["TRIAL"] = "trial";
})(SubscriptionStatus || (exports.SubscriptionStatus = SubscriptionStatus = {}));
// 计费周期枚举
var BillingCycle;
(function (BillingCycle) {
    BillingCycle["MONTHLY"] = "monthly";
    BillingCycle["QUARTERLY"] = "quarterly";
    BillingCycle["SEMI_ANNUALLY"] = "semi-annually";
    BillingCycle["ANNUALLY"] = "annually";
    BillingCycle["ONE_TIME"] = "one-time";
})(BillingCycle || (exports.BillingCycle = BillingCycle = {}));
// 服务类型枚举
var ServiceType;
(function (ServiceType) {
    ServiceType["PREMIUM"] = "premium";
    ServiceType["BASIC"] = "basic";
    ServiceType["STANDARD"] = "standard";
    ServiceType["PROFESSIONAL"] = "professional";
    ServiceType["ENTERPRISE"] = "enterprise";
    ServiceType["FARM_ACTIVITY"] = "farm-activity";
    ServiceType["FOOD_DELIVERY"] = "food-delivery";
    ServiceType["HEALTH_CONSULTATION"] = "health-consultation";
})(ServiceType || (exports.ServiceType = ServiceType = {}));
// 订阅模式
const subscriptionSchema = new mongoose_1.Schema({
    userId: { type: String, required: true, index: true },
    serviceName: { type: String, required: true },
    serviceType: {
        type: String,
        required: true,
        enum: Object.values(ServiceType)
    },
    status: {
        type: String,
        required: true,
        enum: Object.values(SubscriptionStatus),
        default: SubscriptionStatus.PENDING
    },
    startDate: { type: String, required: true },
    endDate: { type: String, required: true },
    price: { type: Number, required: true },
    billingCycle: {
        type: String,
        required: true,
        enum: Object.values(BillingCycle)
    },
    autoRenew: { type: Boolean, default: false },
    details: { type: mongoose_1.Schema.Types.Mixed, required: true },
    metadata: { type: mongoose_1.Schema.Types.Mixed }
}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});
// 索引
subscriptionSchema.index({ userId: 1, status: 1 });
subscriptionSchema.index({ serviceType: 1 });
subscriptionSchema.index({ endDate: 1, status: 1, autoRenew: 1 });
// 虚拟字段
subscriptionSchema.virtual('isActive').get(function () {
    return this.status === SubscriptionStatus.ACTIVE;
});
subscriptionSchema.virtual('daysLeft').get(function () {
    const endDate = new Date(this.endDate);
    const now = new Date();
    const diffTime = endDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
});
subscriptionSchema.virtual('formattedPrice').get(function () {
    return `¥${this.price.toFixed(2)}`;
});
// 创建模型
exports.SubscriptionModel = mongoose_1.default.model('Subscription', subscriptionSchema);
exports.default = exports.SubscriptionModel;
