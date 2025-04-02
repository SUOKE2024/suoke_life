import mongoose, { Document, Schema } from 'mongoose';

// 订单状态枚举
export enum OrderStatus {
  PENDING = 'pending',
  PAID = 'paid',
  PROCESSING = 'processing',
  SHIPPED = 'shipped',
  DELIVERED = 'delivered',
  CANCELED = 'canceled',
  REFUNDED = 'refunded'
}

// 支付方式枚举
export enum PaymentMethod {
  WECHAT = 'wechat',
  ALIPAY = 'alipay',
  CREDIT_CARD = 'credit_card',
  BANK_TRANSFER = 'bank_transfer',
  CASH = 'cash'
}

// 订单项接口
interface OrderItem {
  productId: string;
  productName: string;
  quantity: number;
  price: number;
  totalPrice: number;
  metadata?: any;
}

// 收货地址接口
interface ShippingAddress {
  name: string;
  phone: string;
  province: string;
  city: string;
  district: string;
  address: string;
  zipCode?: string;
}

// 订单文档类型
export interface OrderDocument extends Document {
  orderNumber: string;
  userId: string;
  items: OrderItem[];
  totalAmount: number;
  status: string;
  paymentMethod: string;
  paymentStatus: string;
  paymentTime?: Date;
  shippingAddress: ShippingAddress;
  trackingNumber?: string;
  shippingMethod?: string;
  shippingCost: number;
  discount?: number;
  tax?: number;
  notes?: string;
  metadata?: any;
  createdAt: Date;
  updatedAt: Date;
}

// 订单项模式
const orderItemSchema = new Schema({
  productId: { type: String, required: true },
  productName: { type: String, required: true },
  quantity: { type: Number, required: true, min: 1 },
  price: { type: Number, required: true },
  totalPrice: { type: Number, required: true },
  metadata: { type: Schema.Types.Mixed }
});

// 收货地址模式
const shippingAddressSchema = new Schema({
  name: { type: String, required: true },
  phone: { type: String, required: true },
  province: { type: String, required: true },
  city: { type: String, required: true },
  district: { type: String, required: true },
  address: { type: String, required: true },
  zipCode: { type: String }
});

// 订单模式
const orderSchema = new Schema({
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
  metadata: { type: Schema.Types.Mixed }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// 生成唯一订单号
orderSchema.pre('save', async function(next) {
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
export const OrderModel = mongoose.model<OrderDocument>('Order', orderSchema);

export default OrderModel; 