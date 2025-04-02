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
exports.OrderModel = exports.PaymentMethod = exports.OrderStatus = void 0;
const mongoose_1 = __importStar(require("mongoose"));
// 订单状态枚举
var OrderStatus;
(function (OrderStatus) {
    OrderStatus["PENDING"] = "pending";
    OrderStatus["PAID"] = "paid";
    OrderStatus["PROCESSING"] = "processing";
    OrderStatus["SHIPPED"] = "shipped";
    OrderStatus["DELIVERED"] = "delivered";
    OrderStatus["CANCELED"] = "canceled";
    OrderStatus["REFUNDED"] = "refunded";
})(OrderStatus || (exports.OrderStatus = OrderStatus = {}));
// 支付方式枚举
var PaymentMethod;
(function (PaymentMethod) {
    PaymentMethod["WECHAT"] = "wechat";
    PaymentMethod["ALIPAY"] = "alipay";
    PaymentMethod["CREDIT_CARD"] = "credit_card";
    PaymentMethod["BANK_TRANSFER"] = "bank_transfer";
    PaymentMethod["CASH"] = "cash";
})(PaymentMethod || (exports.PaymentMethod = PaymentMethod = {}));
// 订单项模式
const orderItemSchema = new mongoose_1.Schema({
    productId: { type: String, required: true },
    productName: { type: String, required: true },
    quantity: { type: Number, required: true, min: 1 },
    price: { type: Number, required: true },
    totalPrice: { type: Number, required: true },
    metadata: { type: mongoose_1.Schema.Types.Mixed }
});
// 收货地址模式
const shippingAddressSchema = new mongoose_1.Schema({
    name: { type: String, required: true },
    phone: { type: String, required: true },
    province: { type: String, required: true },
    city: { type: String, required: true },
    district: { type: String, required: true },
    address: { type: String, required: true },
    zipCode: { type: String }
});
// 订单模式
const orderSchema = new mongoose_1.Schema({
    orderNumber: {
        type: String,
        required: true,
        unique: true,
        index: true
    },
    userId: {
        type: String,
        required: true,
        index: true
    },
    items: [{ type: orderItemSchema, required: true }],
    totalAmount: { type: Number, required: true },
    status: {
        type: String,
        required: true,
        enum: Object.values(OrderStatus),
        default: OrderStatus.PENDING,
        index: true
    },
    paymentMethod: {
        type: String,
        required: true,
        enum: Object.values(PaymentMethod)
    },
    paymentStatus: {
        type: String,
        required: true,
        enum: ['pending', 'paid', 'failed', 'refunded'],
        default: 'pending'
    },
    paymentTime: { type: Date },
    shippingAddress: {
        type: shippingAddressSchema,
        required: true
    },
    trackingNumber: { type: String },
    shippingMethod: { type: String },
    shippingCost: { type: Number, default: 0 },
    discount: { type: Number, default: 0 },
    tax: { type: Number, default: 0 },
    notes: { type: String },
    metadata: { type: mongoose_1.Schema.Types.Mixed }
}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});
// 生成唯一订单号
orderSchema.pre('save', async function (next) {
    if (this.isNew) {
        const date = new Date();
        const timestamp = date.getTime().toString().slice(-8);
        const randomPart = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
        this.orderNumber = `XK${date.getFullYear()}${(date.getMonth() + 1).toString().padStart(2, '0')}${date.getDate().toString().padStart(2, '0')}${timestamp}${randomPart}`;
    }
    next();
});
// 索引
orderSchema.index({ createdAt: -1 });
orderSchema.index({ 'items.productId': 1 });
// 创建模型
exports.OrderModel = mongoose_1.default.model('Order', orderSchema);
exports.default = exports.OrderModel;
