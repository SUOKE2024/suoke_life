import 'package:meta/meta.dart';

/// 预约状态枚举
enum AppointmentStatus {
  /// 待确认
  pending,
  
  /// 已确认
  confirmed,
  
  /// 已完成
  completed,
  
  /// 已取消
  cancelled,
  
  /// 已过期
  expired,
}

/// 预约实体类
@immutable
class Appointment {
  /// 预约ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 服务ID
  final String serviceId;
  
  /// 服务提供者ID
  final String providerId;
  
  /// 预约日期
  final DateTime appointmentDate;
  
  /// 开始时间
  final DateTime startTime;
  
  /// 结束时间
  final DateTime endTime;
  
  /// 预约状态
  final AppointmentStatus status;
  
  /// 备注信息
  final String? notes;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 更新时间
  final DateTime updatedAt;
  
  /// 预约服务名称
  final String serviceName;
  
  /// 服务提供者名称
  final String providerName;
  
  /// 价格
  final double price;
  
  /// 是否评价
  final bool hasReviewed;

  const Appointment({
    required this.id,
    required this.userId,
    required this.serviceId,
    required this.providerId,
    required this.appointmentDate,
    required this.startTime,
    required this.endTime,
    required this.status,
    this.notes,
    required this.createdAt,
    required this.updatedAt,
    required this.serviceName,
    required this.providerName,
    required this.price,
    this.hasReviewed = false,
  });
  
  /// 创建副本
  Appointment copyWith({
    String? id,
    String? userId,
    String? serviceId,
    String? providerId,
    DateTime? appointmentDate,
    DateTime? startTime,
    DateTime? endTime,
    AppointmentStatus? status,
    String? notes,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? serviceName,
    String? providerName,
    double? price,
    bool? hasReviewed,
  }) {
    return Appointment(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      serviceId: serviceId ?? this.serviceId,
      providerId: providerId ?? this.providerId,
      appointmentDate: appointmentDate ?? this.appointmentDate,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
      status: status ?? this.status,
      notes: notes ?? this.notes,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      serviceName: serviceName ?? this.serviceName,
      providerName: providerName ?? this.providerName,
      price: price ?? this.price,
      hasReviewed: hasReviewed ?? this.hasReviewed,
    );
  }
  
  /// 计算预约时长（分钟）
  int get durationMinutes {
    return endTime.difference(startTime).inMinutes;
  }
  
  /// 判断预约是否可取消
  bool get canCancel {
    return status == AppointmentStatus.pending || 
           status == AppointmentStatus.confirmed;
  }
  
  /// 判断预约是否可评价
  bool get canReview {
    return status == AppointmentStatus.completed && !hasReviewed;
  }
  
  /// 判断预约是否即将开始（24小时内）
  bool get isUpcoming {
    final now = DateTime.now();
    final difference = startTime.difference(now);
    return difference.inHours <= 24 && difference.isNegative == false;
  }
  
  /// 判断预约是否已过期
  bool get isExpired {
    return DateTime.now().isAfter(endTime) && 
           status != AppointmentStatus.completed && 
           status != AppointmentStatus.cancelled;
  }
  
  /// 获取预约状态文本
  String get statusText {
    switch (status) {
      case AppointmentStatus.pending:
        return '待确认';
      case AppointmentStatus.confirmed:
        return '已确认';
      case AppointmentStatus.completed:
        return '已完成';
      case AppointmentStatus.cancelled:
        return '已取消';
      case AppointmentStatus.expired:
        return '已过期';
    }
  }
  
  /// 获取状态颜色代码
  String get statusColorHex {
    switch (status) {
      case AppointmentStatus.pending:
        return '#FFA500'; // 橙色
      case AppointmentStatus.confirmed:
        return '#4CAF50'; // 绿色
      case AppointmentStatus.completed:
        return '#2196F3'; // 蓝色
      case AppointmentStatus.cancelled:
        return '#F44336'; // 红色
      case AppointmentStatus.expired:
        return '#9E9E9E'; // 灰色
    }
  }
} 