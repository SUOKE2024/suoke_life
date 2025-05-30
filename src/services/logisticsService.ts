import { apiClient } from "./apiClient";

/**
 * 物流系统对接服务
 * 索克生活APP - 多物流提供商集成管理
 */

// 物流提供商类型
export type LogisticsProvider =
  | "sf_express" // 顺丰速运
  | "ems" // 中国邮政EMS
  | "yto" // 圆通速递
  | "sto" // 申通快递
  | "zto" // 中通快递
  | "yunda" // 韵达速递
  | "jd_logistics" // 京东物流
  | "dhl" // DHL国际快递
  | "fedex" // FedEx联邦快递
  | "ups" // UPS快递
  | "tnt" // TNT快递
  | "dpd" // DPD快递
  | "gls" // GLS快递
  | "local_delivery" // 本地配送
  | "drone_delivery" // 无人机配送
  | "cold_chain"; // 冷链物流

// 配送类型
export type DeliveryType =
  | "standard" // 标准配送
  | "express" // 快速配送
  | "same_day" // 当日达
  | "next_day" // 次日达
  | "scheduled" // 预约配送
  | "pickup" // 自提
  | "cold_chain" // 冷链配送
  | "fragile" // 易碎品配送
  | "prescription" // 处方药配送
  | "medical_device"; // 医疗器械配送

// 包裹状态
export type PackageStatus =
  | "created" // 已创建
  | "picked_up" // 已揽收
  | "in_transit" // 运输中
  | "out_for_delivery" // 派送中
  | "delivered" // 已送达
  | "failed_delivery" // 配送失败
  | "returned" // 已退回
  | "cancelled" // 已取消
  | "lost" // 丢失
  | "damaged"; // 损坏

// 地址信息
export interface Address {
  id?: string;
  name: string;
  phone: string;
  country: string;
  province: string;
  city: string;
  district: string;
  street: string;
  postalCode: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  addressType?: "home" | "office" | "hospital" | "pharmacy" | "clinic";
  isDefault?: boolean;
  specialInstructions?: string;
}

// 包裹信息
export interface Package {
  id: string;
  trackingNumber: string;
  provider: LogisticsProvider;
  deliveryType: DeliveryType;
  status: PackageStatus;
  sender: Address;
  recipient: Address;
  items: PackageItem[];
  weight: number; // 克
  dimensions: {
    length: number; // 厘米
    width: number;
    height: number;
  };
  value: number; // 货物价值
  currency: string;
  shippingCost: number;
  insuranceValue?: number;
  createdAt: string;
  updatedAt: string;
  estimatedDelivery?: string;
  actualDelivery?: string;
  specialRequirements?: {
    temperatureControl?: { min: number; max: number };
    fragile?: boolean;
    prescriptionRequired?: boolean;
    signatureRequired?: boolean;
    ageVerificationRequired?: boolean;
  };
  metadata?: {
    orderId?: string;
    userId?: string;
    pharmacyId?: string;
    clinicId?: string;
    insuranceClaim?: boolean;
  };
}

// 包裹物品
export interface PackageItem {
  id: string;
  name: string;
  description: string;
  quantity: number;
  weight: number;
  value: number;
  category:
    | "medication"
    | "medical_device"
    | "health_supplement"
    | "medical_supply"
    | "other";
  sku?: string;
  batchNumber?: string;
  expiryDate?: string;
  requiresRefrigeration?: boolean;
  prescriptionRequired?: boolean;
  controlledSubstance?: boolean;
}

// 配送跟踪信息
export interface TrackingEvent {
  id: string;
  packageId: string;
  status: PackageStatus;
  timestamp: string;
  location: {
    name: string;
    address: string;
    coordinates?: {
      latitude: number;
      longitude: number;
    };
  };
  description: string;
  operatorName?: string;
  nextLocation?: string;
  estimatedArrival?: string;
  photos?: string[];
  signature?: {
    recipientName: string;
    signatureImage: string;
    timestamp: string;
  };
}

// 配送费用计算
export interface ShippingRate {
  provider: LogisticsProvider;
  deliveryType: DeliveryType;
  cost: number;
  currency: string;
  estimatedDays: number;
  guaranteedDelivery?: string;
  features: string[];
  restrictions?: string[];
}

// 物流配置
interface LogisticsConfig {
  provider: LogisticsProvider;
  apiKey: string;
  secretKey?: string;
  customerId: string;
  environment: "sandbox" | "production";
  webhookUrl: string;
  supportedServices: DeliveryType[];
  coverageAreas: string[];
  specialCapabilities: string[];
}

// 物流服务类
class LogisticsService {
  private configs: Map<LogisticsProvider, LogisticsConfig> = new Map();
  private activePackages: Map<string, Package> = new Map();

  constructor() {
    this.initializeConfigs();
  }

  /**
   * 初始化物流配置
   */
  private initializeConfigs(): void {
    // 顺丰速运配置
    this.configs.set("sf_express", {
      provider: "sf_express",
      apiKey: process.env.SF_EXPRESS_API_KEY || "",
      secretKey: process.env.SF_EXPRESS_SECRET_KEY || "",
      customerId: process.env.SF_EXPRESS_CUSTOMER_ID || "",
      environment: (process.env.NODE_ENV === "production"
        ? "production"
        : "sandbox") as "sandbox" | "production",
      webhookUrl: process.env.SF_EXPRESS_WEBHOOK_URL || "",
      supportedServices: [
        "standard",
        "express",
        "same_day",
        "next_day",
        "cold_chain",
      ],
      coverageAreas: ["CN", "HK", "TW", "SG", "MY"],
      specialCapabilities: ["cold_chain", "prescription", "medical_device"],
    });

    // 京东物流配置
    this.configs.set("jd_logistics", {
      provider: "jd_logistics",
      apiKey: process.env.JD_LOGISTICS_API_KEY || "",
      secretKey: process.env.JD_LOGISTICS_SECRET_KEY || "",
      customerId: process.env.JD_LOGISTICS_CUSTOMER_ID || "",
      environment: (process.env.NODE_ENV === "production"
        ? "production"
        : "sandbox") as "sandbox" | "production",
      webhookUrl: process.env.JD_LOGISTICS_WEBHOOK_URL || "",
      supportedServices: [
        "standard",
        "express",
        "same_day",
        "next_day",
        "scheduled",
      ],
      coverageAreas: ["CN"],
      specialCapabilities: [
        "cold_chain",
        "prescription",
        "medical_device",
        "fragile",
      ],
    });

    // DHL配置
    this.configs.set("dhl", {
      provider: "dhl",
      apiKey: process.env.DHL_API_KEY || "",
      secretKey: process.env.DHL_SECRET_KEY || "",
      customerId: process.env.DHL_CUSTOMER_ID || "",
      environment: (process.env.NODE_ENV === "production"
        ? "production"
        : "sandbox") as "sandbox" | "production",
      webhookUrl: process.env.DHL_WEBHOOK_URL || "",
      supportedServices: ["standard", "express", "next_day"],
      coverageAreas: ["GLOBAL"],
      specialCapabilities: ["cold_chain", "medical_device", "fragile"],
    });

    // FedEx配置
    this.configs.set("fedex", {
      provider: "fedex",
      apiKey: process.env.FEDEX_API_KEY || "",
      secretKey: process.env.FEDEX_SECRET_KEY || "",
      customerId: process.env.FEDEX_CUSTOMER_ID || "",
      environment: (process.env.NODE_ENV === "production"
        ? "production"
        : "sandbox") as "sandbox" | "production",
      webhookUrl: process.env.FEDEX_WEBHOOK_URL || "",
      supportedServices: ["standard", "express", "next_day", "same_day"],
      coverageAreas: ["GLOBAL"],
      specialCapabilities: ["cold_chain", "medical_device", "prescription"],
    });

    // 本地配送配置
    this.configs.set("local_delivery", {
      provider: "local_delivery",
      apiKey: process.env.LOCAL_DELIVERY_API_KEY || "",
      customerId: process.env.LOCAL_DELIVERY_CUSTOMER_ID || "",
      environment: (process.env.NODE_ENV === "production"
        ? "production"
        : "sandbox") as "sandbox" | "production",
      webhookUrl: process.env.LOCAL_DELIVERY_WEBHOOK_URL || "",
      supportedServices: ["same_day", "scheduled", "pickup"],
      coverageAreas: ["LOCAL"],
      specialCapabilities: ["prescription", "cold_chain", "medical_device"],
    });
  }

  /**
   * 计算配送费用
   */
  async calculateShippingRates(
    sender: Address,
    recipient: Address,
    items: PackageItem[],
    deliveryTypes?: DeliveryType[]
  ): Promise<ShippingRate[]> {
    try {
      const totalWeight = items.reduce(
        (sum, item) => sum + item.weight * item.quantity,
        0
      );
      const totalValue = items.reduce(
        (sum, item) => sum + item.value * item.quantity,
        0
      );

      const rates: ShippingRate[] = [];

      // 遍历所有配置的物流提供商
      for (const [provider, config] of this.configs) {
        try {
          const providerRates = await this.getProviderRates(
            provider,
            sender,
            recipient,
            totalWeight,
            totalValue,
            items,
            deliveryTypes
          );
          rates.push(...providerRates);
        } catch (error) {
          console.warn(`Failed to get rates from ${provider}:`, error);
        }
      }

      // 按价格排序
      return rates.sort((a, b) => a.cost - b.cost);
    } catch (error) {
      console.error("Failed to calculate shipping rates:", error);
      throw error;
    }
  }

  /**
   * 创建配送订单
   */
  async createShipment(shipmentData: {
    provider: LogisticsProvider;
    deliveryType: DeliveryType;
    sender: Address;
    recipient: Address;
    items: PackageItem[];
    specialRequirements?: Package["specialRequirements"];
    metadata?: Package["metadata"];
  }): Promise<Package> {
    try {
      const config = this.configs.get(shipmentData.provider);
      if (!config) {
        throw new Error(`Provider ${shipmentData.provider} not configured`);
      }

      const packageId = this.generatePackageId();
      const trackingNumber = await this.generateTrackingNumber(
        shipmentData.provider
      );

      const totalWeight = shipmentData.items.reduce(
        (sum, item) => sum + item.weight * item.quantity,
        0
      );
      const totalValue = shipmentData.items.reduce(
        (sum, item) => sum + item.value * item.quantity,
        0
      );

      const packageInfo: Package = {
        id: packageId,
        trackingNumber,
        provider: shipmentData.provider,
        deliveryType: shipmentData.deliveryType,
        status: "created",
        sender: shipmentData.sender,
        recipient: shipmentData.recipient,
        items: shipmentData.items,
        weight: totalWeight,
        dimensions: this.calculateDimensions(shipmentData.items),
        value: totalValue,
        currency: "CNY",
        shippingCost: 0, // 将在后续计算
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        specialRequirements: shipmentData.specialRequirements,
        metadata: shipmentData.metadata,
      };

      // 调用物流提供商API创建订单
      const providerResponse = await this.createProviderShipment(
        shipmentData.provider,
        packageInfo
      );

      // 更新包裹信息
      packageInfo.trackingNumber = providerResponse.trackingNumber;
      packageInfo.shippingCost = providerResponse.shippingCost;
      packageInfo.estimatedDelivery = providerResponse.estimatedDelivery;

      this.activePackages.set(packageId, packageInfo);

      // 保存到后端
      await apiClient.post("/api/v1/logistics/packages", packageInfo);

      return packageInfo;
    } catch (error) {
      console.error("Failed to create shipment:", error);
      throw error;
    }
  }

  /**
   * 跟踪包裹
   */
  async trackPackage(
    trackingNumber: string,
    provider?: LogisticsProvider
  ): Promise<{
    package: Package;
    events: TrackingEvent[];
    currentLocation?: {
      name: string;
      coordinates: { latitude: number; longitude: number };
    };
    estimatedDelivery?: string;
  }> {
    try {
      let packageInfo: Package | undefined;
      let trackingEvents: TrackingEvent[] = [];

      if (provider) {
        // 直接从指定提供商查询
        const result = await this.getProviderTracking(provider, trackingNumber);
        packageInfo = result.package;
        trackingEvents = result.events;
      } else {
        // 尝试从所有提供商查询
        for (const [providerKey, config] of this.configs) {
          try {
            const result = await this.getProviderTracking(
              providerKey,
              trackingNumber
            );
            packageInfo = result.package;
            trackingEvents = result.events;
            break;
          } catch (error) {
            // 继续尝试下一个提供商
          }
        }
      }

      if (!packageInfo) {
        throw new Error("Package not found");
      }

      // 获取当前位置
      const currentLocation =
        trackingEvents.length > 0
          ? trackingEvents[trackingEvents.length - 1].location
          : undefined;

      return {
        package: packageInfo,
        events: trackingEvents,
        currentLocation: currentLocation?.coordinates
          ? {
              name: currentLocation.name,
              coordinates: currentLocation.coordinates,
            }
          : undefined,
        estimatedDelivery: packageInfo.estimatedDelivery,
      };
    } catch (error) {
      console.error("Failed to track package:", error);
      throw error;
    }
  }

  /**
   * 获取配送历史
   */
  async getDeliveryHistory(
    userId: string,
    filters?: {
      status?: PackageStatus;
      provider?: LogisticsProvider;
      dateRange?: { start: string; end: string };
    }
  ): Promise<Package[]> {
    try {
      const params = new URLSearchParams();
      params.append("userId", userId);

      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value) {
            if (key === "dateRange") {
              params.append("startDate", (value as any).start);
              params.append("endDate", (value as any).end);
            } else {
              params.append(key, value.toString());
            }
          }
        });
      }

      const response = await apiClient.get(
        `/api/v1/logistics/history?${params.toString()}`
      );
      return response.data;
    } catch (error) {
      console.error("Failed to get delivery history:", error);
      throw error;
    }
  }

  /**
   * 预约配送时间
   */
  async scheduleDelivery(
    packageId: string,
    scheduledTime: string,
    specialInstructions?: string
  ): Promise<{
    success: boolean;
    scheduledTime: string;
    confirmationNumber?: string;
  }> {
    try {
      const packageInfo = this.activePackages.get(packageId);
      if (!packageInfo) {
        throw new Error("Package not found");
      }

      const response = await apiClient.post(
        `/api/v1/logistics/packages/${packageId}/schedule`,
        {
          scheduledTime,
          specialInstructions,
        }
      );

      return response.data;
    } catch (error) {
      console.error("Failed to schedule delivery:", error);
      throw error;
    }
  }

  /**
   * 处理配送异常
   */
  async handleDeliveryException(
    packageId: string,
    exceptionType: "failed_delivery" | "damaged" | "lost" | "wrong_address",
    description: string,
    resolution?: "retry" | "return" | "replace" | "refund"
  ): Promise<{
    success: boolean;
    caseNumber: string;
    resolution: string;
    estimatedResolutionTime?: string;
  }> {
    try {
      const response = await apiClient.post(
        `/api/v1/logistics/packages/${packageId}/exception`,
        {
          exceptionType,
          description,
          resolution,
        }
      );

      return response.data;
    } catch (error) {
      console.error("Failed to handle delivery exception:", error);
      throw error;
    }
  }

  /**
   * 获取配送区域覆盖
   */
  async getDeliveryCoverage(
    address: Partial<Address>,
    deliveryType?: DeliveryType
  ): Promise<
    {
      provider: LogisticsProvider;
      available: boolean;
      deliveryTypes: DeliveryType[];
      estimatedDays: number;
      restrictions?: string[];
    }[]
  > {
    const coverage: any[] = [];

    this.configs.forEach((config, provider) => {
      const isAvailable = this.checkCoverageArea(config, address);
      const availableTypes = deliveryType
        ? config.supportedServices.filter((service) => service === deliveryType)
        : config.supportedServices;

      coverage.push({
        provider,
        available: isAvailable,
        deliveryTypes: availableTypes,
        estimatedDays: this.getEstimatedDays(
          provider,
          deliveryType || "standard"
        ),
        restrictions: this.getDeliveryRestrictions(provider, address),
      });
    });

    return coverage;
  }

  /**
   * 处理配送回调
   */
  async handleDeliveryCallback(
    provider: LogisticsProvider,
    callbackData: any
  ): Promise<{
    packageId: string;
    status: PackageStatus;
    event: TrackingEvent;
  }> {
    try {
      switch (provider) {
        case "sf_express":
          return await this.handleSFExpressCallback(callbackData);
        case "jd_logistics":
          return await this.handleJDLogisticsCallback(callbackData);
        case "dhl":
          return await this.handleDHLCallback(callbackData);
        case "fedex":
          return await this.handleFedExCallback(callbackData);
        default:
          throw new Error(`Callback handler for ${provider} not implemented`);
      }
    } catch (error) {
      console.error("Failed to handle delivery callback:", error);
      throw error;
    }
  }

  /**
   * 私有方法实现
   */
  private async getProviderRates(
    provider: LogisticsProvider,
    sender: Address,
    recipient: Address,
    weight: number,
    value: number,
    items: PackageItem[],
    deliveryTypes?: DeliveryType[]
  ): Promise<ShippingRate[]> {
    const config = this.configs.get(provider);
    if (!config) return [];

    // 这里应该调用具体提供商的API
    // 模拟返回数据
    const rates: ShippingRate[] = [];
    const supportedTypes = deliveryTypes
      ? config.supportedServices.filter((service) =>
          deliveryTypes.includes(service)
        )
      : config.supportedServices;

    supportedTypes.forEach((deliveryType) => {
      rates.push({
        provider,
        deliveryType,
        cost: this.calculateBaseCost(provider, deliveryType, weight, value),
        currency: "CNY",
        estimatedDays: this.getEstimatedDays(provider, deliveryType),
        features: config.specialCapabilities,
        restrictions: this.getItemRestrictions(items),
      });
    });

    return rates;
  }

  private async createProviderShipment(
    provider: LogisticsProvider,
    packageInfo: Package
  ): Promise<{
    trackingNumber: string;
    shippingCost: number;
    estimatedDelivery: string;
  }> {
    // 这里应该调用具体提供商的API创建订单
    // 模拟返回数据
    return {
      trackingNumber: this.generateTrackingNumber(provider),
      shippingCost: this.calculateBaseCost(
        provider,
        packageInfo.deliveryType,
        packageInfo.weight,
        packageInfo.value
      ),
      estimatedDelivery: new Date(
        Date.now() +
          this.getEstimatedDays(provider, packageInfo.deliveryType) *
            24 *
            60 *
            60 *
            1000
      ).toISOString(),
    };
  }

  private async getProviderTracking(
    provider: LogisticsProvider,
    trackingNumber: string
  ): Promise<{
    package: Package;
    events: TrackingEvent[];
  }> {
    // 这里应该调用具体提供商的API查询跟踪信息
    // 模拟返回数据
    const packageInfo = this.activePackages.get(trackingNumber) || {
      id: trackingNumber,
      trackingNumber,
      provider,
      deliveryType: "standard" as DeliveryType,
      status: "in_transit" as PackageStatus,
      sender: {} as Address,
      recipient: {} as Address,
      items: [],
      weight: 0,
      dimensions: { length: 0, width: 0, height: 0 },
      value: 0,
      currency: "CNY",
      shippingCost: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    const events: TrackingEvent[] = [
      {
        id: "1",
        packageId: trackingNumber,
        status: "picked_up",
        timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        location: {
          name: "发货仓库",
          address: "北京市朝阳区",
        },
        description: "包裹已从发货仓库揽收",
      },
      {
        id: "2",
        packageId: trackingNumber,
        status: "in_transit",
        timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        location: {
          name: "中转站",
          address: "上海市浦东新区",
        },
        description: "包裹正在运输途中",
      },
    ];

    return { package: packageInfo, events };
  }

  private calculateBaseCost(
    provider: LogisticsProvider,
    deliveryType: DeliveryType,
    weight: number,
    value: number
  ): number {
    // 基础费用计算逻辑
    let baseCost = 10; // 基础费用

    // 重量费用
    baseCost += Math.ceil(weight / 1000) * 5;

    // 配送类型费用
    switch (deliveryType) {
      case "same_day":
        baseCost *= 3;
        break;
      case "next_day":
        baseCost *= 2;
        break;
      case "express":
        baseCost *= 1.5;
        break;
      case "cold_chain":
        baseCost *= 2.5;
        break;
    }

    // 提供商费用调整
    switch (provider) {
      case "sf_express":
        baseCost *= 1.2;
        break;
      case "dhl":
      case "fedex":
        baseCost *= 2;
        break;
    }

    return Math.round(baseCost * 100) / 100;
  }

  private getEstimatedDays(
    provider: LogisticsProvider,
    deliveryType: DeliveryType
  ): number {
    switch (deliveryType) {
      case "same_day":
        return 0;
      case "next_day":
        return 1;
      case "express":
        return 2;
      case "standard":
        return provider === "sf_express" ? 3 : 5;
      default:
        return 5;
    }
  }

  private checkCoverageArea(
    config: LogisticsConfig,
    address: Partial<Address>
  ): boolean {
    if (config.coverageAreas.includes("GLOBAL")) return true;
    if (config.coverageAreas.includes("LOCAL") && address.city) return true;
    return config.coverageAreas.includes(address.country || "");
  }

  private getDeliveryRestrictions(
    provider: LogisticsProvider,
    address: Partial<Address>
  ): string[] {
    const restrictions: string[] = [];

    if (provider === "local_delivery" && address.country !== "CN") {
      restrictions.push("仅限国内配送");
    }

    return restrictions;
  }

  private getItemRestrictions(items: PackageItem[]): string[] {
    const restrictions: string[] = [];

    if (items.some((item) => item.prescriptionRequired)) {
      restrictions.push("需要处方验证");
    }

    if (items.some((item) => item.requiresRefrigeration)) {
      restrictions.push("需要冷链运输");
    }

    if (items.some((item) => item.controlledSubstance)) {
      restrictions.push("管制物品，需要特殊许可");
    }

    return restrictions;
  }

  private calculateDimensions(items: PackageItem[]): {
    length: number;
    width: number;
    height: number;
  } {
    // 简化的尺寸计算
    const totalVolume = items.reduce(
      (sum, item) => sum + item.weight * item.quantity * 0.001,
      0
    );
    const side = Math.cbrt(totalVolume);

    return {
      length: Math.max(side, 10),
      width: Math.max(side, 10),
      height: Math.max(side, 5),
    };
  }

  private generatePackageId(): string {
    const timestamp = Date.now().toString();
    const random = Math.random().toString(36).substring(2, 8);
    return `PKG${timestamp}${random}`.toUpperCase();
  }

  private generateTrackingNumber(provider: LogisticsProvider): string {
    const timestamp = Date.now().toString();
    const random = Math.random().toString(36).substring(2, 10);

    switch (provider) {
      case "sf_express":
        return `SF${timestamp}${random}`.toUpperCase();
      case "jd_logistics":
        return `JD${timestamp}${random}`.toUpperCase();
      case "dhl":
        return `DHL${timestamp}${random}`.toUpperCase();
      case "fedex":
        return `FX${timestamp}${random}`.toUpperCase();
      default:
        return `TRK${timestamp}${random}`.toUpperCase();
    }
  }

  /**
   * 回调处理方法
   */
  private async handleSFExpressCallback(callbackData: any): Promise<{
    packageId: string;
    status: PackageStatus;
    event: TrackingEvent;
  }> {
    return {
      packageId: callbackData.waybillNo,
      status: this.mapSFStatus(callbackData.status),
      event: {
        id: Date.now().toString(),
        packageId: callbackData.waybillNo,
        status: this.mapSFStatus(callbackData.status),
        timestamp: callbackData.updateTime,
        location: {
          name: callbackData.location,
          address: callbackData.address,
        },
        description: callbackData.description,
      },
    };
  }

  private async handleJDLogisticsCallback(callbackData: any): Promise<{
    packageId: string;
    status: PackageStatus;
    event: TrackingEvent;
  }> {
    return {
      packageId: callbackData.trackingNumber,
      status: this.mapJDStatus(callbackData.status),
      event: {
        id: Date.now().toString(),
        packageId: callbackData.trackingNumber,
        status: this.mapJDStatus(callbackData.status),
        timestamp: callbackData.timestamp,
        location: {
          name: callbackData.location,
          address: callbackData.address,
        },
        description: callbackData.description,
      },
    };
  }

  private async handleDHLCallback(callbackData: any): Promise<{
    packageId: string;
    status: PackageStatus;
    event: TrackingEvent;
  }> {
    return {
      packageId: callbackData.trackingNumber,
      status: this.mapDHLStatus(callbackData.status),
      event: {
        id: Date.now().toString(),
        packageId: callbackData.trackingNumber,
        status: this.mapDHLStatus(callbackData.status),
        timestamp: callbackData.timestamp,
        location: {
          name: callbackData.location,
          address: callbackData.address,
        },
        description: callbackData.description,
      },
    };
  }

  private async handleFedExCallback(callbackData: any): Promise<{
    packageId: string;
    status: PackageStatus;
    event: TrackingEvent;
  }> {
    return {
      packageId: callbackData.trackingNumber,
      status: this.mapFedExStatus(callbackData.status),
      event: {
        id: Date.now().toString(),
        packageId: callbackData.trackingNumber,
        status: this.mapFedExStatus(callbackData.status),
        timestamp: callbackData.timestamp,
        location: {
          name: callbackData.location,
          address: callbackData.address,
        },
        description: callbackData.description,
      },
    };
  }

  /**
   * 状态映射方法
   */
  private mapSFStatus(status: string): PackageStatus {
    const statusMap: Record<string, PackageStatus> = {
      "1": "picked_up",
      "2": "in_transit",
      "3": "out_for_delivery",
      "4": "delivered",
      "5": "failed_delivery",
    };
    return statusMap[status] || "in_transit";
  }

  private mapJDStatus(status: string): PackageStatus {
    const statusMap: Record<string, PackageStatus> = {
      PICKED_UP: "picked_up",
      IN_TRANSIT: "in_transit",
      OUT_FOR_DELIVERY: "out_for_delivery",
      DELIVERED: "delivered",
      FAILED: "failed_delivery",
    };
    return statusMap[status] || "in_transit";
  }

  private mapDHLStatus(status: string): PackageStatus {
    const statusMap: Record<string, PackageStatus> = {
      PU: "picked_up",
      IT: "in_transit",
      WC: "out_for_delivery",
      OK: "delivered",
      DF: "failed_delivery",
    };
    return statusMap[status] || "in_transit";
  }

  private mapFedExStatus(status: string): PackageStatus {
    const statusMap: Record<string, PackageStatus> = {
      PU: "picked_up",
      IT: "in_transit",
      OD: "out_for_delivery",
      DL: "delivered",
      DE: "failed_delivery",
    };
    return statusMap[status] || "in_transit";
  }
}

// 导出服务实例
export const logisticsService = new LogisticsService();
export default logisticsService;
