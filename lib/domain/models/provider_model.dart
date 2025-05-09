import 'package:suoke_life/domain/models/chat_contact_model.dart';

/// 供应商模型
class Provider {
  /// 供应商ID
  final String id;
  
  /// 供应商名称
  final String name;
  
  /// 供应商Logo URL
  final String logoUrl;
  
  /// 供应商类型
  final ProviderType type;
  
  /// 供应商简介
  final String description;
  
  /// 联系电话
  final String phoneNumber;
  
  /// 电子邮箱
  final String email;
  
  /// 地址
  final String address;
  
  /// 营业执照号
  final String licenseNumber;
  
  /// 认证状态
  final VerificationStatus verificationStatus;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 最后更新时间
  final DateTime updatedAt;
  
  /// 供应商提供的服务列表
  final List<ProviderService> services;
  
  /// 供应商提供的产品列表
  final List<ProviderProduct> products;
  
  /// 附加数据
  final Map<String, dynamic>? extraData;

  /// 构造函数
  Provider({
    required this.id,
    required this.name,
    required this.logoUrl,
    required this.type,
    required this.description,
    required this.phoneNumber,
    required this.email,
    required this.address,
    required this.licenseNumber,
    this.verificationStatus = VerificationStatus.pending,
    required this.createdAt,
    required this.updatedAt,
    this.services = const [],
    this.products = const [],
    this.extraData,
  });
  
  /// 复制并修改
  Provider copyWith({
    String? id,
    String? name,
    String? logoUrl,
    ProviderType? type,
    String? description,
    String? phoneNumber,
    String? email,
    String? address,
    String? licenseNumber,
    VerificationStatus? verificationStatus,
    DateTime? createdAt,
    DateTime? updatedAt,
    List<ProviderService>? services,
    List<ProviderProduct>? products,
    Map<String, dynamic>? extraData,
  }) {
    return Provider(
      id: id ?? this.id,
      name: name ?? this.name,
      logoUrl: logoUrl ?? this.logoUrl,
      type: type ?? this.type,
      description: description ?? this.description,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      email: email ?? this.email,
      address: address ?? this.address,
      licenseNumber: licenseNumber ?? this.licenseNumber,
      verificationStatus: verificationStatus ?? this.verificationStatus,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      services: services ?? this.services,
      products: products ?? this.products,
      extraData: extraData ?? this.extraData,
    );
  }
  
  /// 转换为聊天联系人
  ChatContact toChatContact() {
    return ChatContact(
      id: id,
      name: name,
      type: ChatContactType.provider,
      avatarUrl: logoUrl,
      description: description,
      lastActiveTime: updatedAt,
      verificationStatus: verificationStatus,
      extraData: {
        'providerType': type.toString(),
      },
    );
  }
}

/// 供应商类型
enum ProviderType {
  /// 诊所
  clinic,
  
  /// 医院
  hospital,
  
  /// 药店
  pharmacy,
  
  /// 健康产品商
  healthProductVendor,
  
  /// 健康服务商
  healthServiceProvider,
}

/// 供应商服务模型
class ProviderService {
  /// 服务ID
  final String id;
  
  /// 服务名称
  final String name;
  
  /// 服务描述
  final String description;
  
  /// 服务图标
  final String iconUrl;
  
  /// 服务价格
  final double price;
  
  /// 服务类型
  final ServiceType type;
  
  /// 服务时长（分钟）
  final int duration;
  
  /// 是否上线
  final bool isActive;
  
  /// 供应商ID
  final String providerId;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 最后更新时间
  final DateTime updatedAt;
  
  /// 附加数据
  final Map<String, dynamic>? extraData;

  /// 构造函数
  ProviderService({
    required this.id,
    required this.name,
    required this.description,
    required this.iconUrl,
    required this.price,
    required this.type,
    required this.duration,
    this.isActive = true,
    required this.providerId,
    required this.createdAt,
    required this.updatedAt,
    this.extraData,
  });
}

/// 服务类型
enum ServiceType {
  /// 中医体质检测
  constitutionAssessment,
  
  /// 针灸
  acupuncture,
  
  /// 推拿
  massage,
  
  /// 处方
  prescription,
  
  /// 健康咨询
  consultation,
  
  /// 其他
  other,
}

/// 供应商产品模型
class ProviderProduct {
  /// 产品ID
  final String id;
  
  /// 产品名称
  final String name;
  
  /// 产品描述
  final String description;
  
  /// 产品图片URL
  final String imageUrl;
  
  /// 产品价格
  final double price;
  
  /// 产品类型
  final ProductType type;
  
  /// 库存数量
  final int stockQuantity;
  
  /// 是否上线
  final bool isActive;
  
  /// 供应商ID
  final String providerId;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 最后更新时间
  final DateTime updatedAt;
  
  /// 附加数据
  final Map<String, dynamic>? extraData;

  /// 构造函数
  ProviderProduct({
    required this.id,
    required this.name,
    required this.description,
    required this.imageUrl,
    required this.price,
    required this.type,
    required this.stockQuantity,
    this.isActive = true,
    required this.providerId,
    required this.createdAt,
    required this.updatedAt,
    this.extraData,
  });
}

/// 产品类型
enum ProductType {
  /// 中药
  herbalMedicine,
  
  /// 保健品
  healthProduct,
  
  /// 医疗器械
  medicalDevice,
  
  /// 健康设备
  healthDevice,
  
  /// 其他
  other,
} 