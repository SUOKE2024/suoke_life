import '../../domain/entities/appointment.dart';

/// 预约数据模型
class AppointmentModel {
  final String id;
  final String userId;
  final String serviceId;
  final String providerId;
  final DateTime appointmentDate;
  final DateTime startTime;
  final DateTime endTime;
  final AppointmentStatus status;
  final String? notes;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String serviceName;
  final String providerName;
  final double price;
  final bool hasReviewed;

  AppointmentModel({
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

  /// 从实体转换为模型
  factory AppointmentModel.fromEntity(Appointment appointment) {
    return AppointmentModel(
      id: appointment.id,
      userId: appointment.userId,
      serviceId: appointment.serviceId,
      providerId: appointment.providerId,
      appointmentDate: appointment.appointmentDate,
      startTime: appointment.startTime,
      endTime: appointment.endTime,
      status: appointment.status,
      notes: appointment.notes,
      createdAt: appointment.createdAt,
      updatedAt: appointment.updatedAt,
      serviceName: appointment.serviceName,
      providerName: appointment.providerName,
      price: appointment.price,
      hasReviewed: appointment.hasReviewed,
    );
  }

  /// 从JSON转换为模型
  factory AppointmentModel.fromJson(Map<String, dynamic> json) {
    return AppointmentModel(
      id: json['id'],
      userId: json['userId'],
      serviceId: json['serviceId'],
      providerId: json['providerId'],
      appointmentDate: DateTime.parse(json['appointmentDate']),
      startTime: DateTime.parse(json['startTime']),
      endTime: DateTime.parse(json['endTime']),
      status: _parseStatus(json['status']),
      notes: json['notes'],
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: DateTime.parse(json['updatedAt']),
      serviceName: json['serviceName'],
      providerName: json['providerName'],
      price: json['price'].toDouble(),
      hasReviewed: json['hasReviewed'] ?? false,
    );
  }

  /// 解析预约状态
  static AppointmentStatus _parseStatus(String status) {
    switch (status) {
      case 'pending':
        return AppointmentStatus.pending;
      case 'confirmed':
        return AppointmentStatus.confirmed;
      case 'completed':
        return AppointmentStatus.completed;
      case 'cancelled':
        return AppointmentStatus.cancelled;
      case 'expired':
        return AppointmentStatus.expired;
      default:
        return AppointmentStatus.pending;
    }
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'serviceId': serviceId,
      'providerId': providerId,
      'appointmentDate': appointmentDate.toIso8601String(),
      'startTime': startTime.toIso8601String(),
      'endTime': endTime.toIso8601String(),
      'status': status.toString().split('.').last,
      'notes': notes,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'serviceName': serviceName,
      'providerName': providerName,
      'price': price,
      'hasReviewed': hasReviewed,
    };
  }

  /// 转换为实体
  Appointment toEntity() {
    return Appointment(
      id: id,
      userId: userId,
      serviceId: serviceId,
      providerId: providerId,
      appointmentDate: appointmentDate,
      startTime: startTime,
      endTime: endTime,
      status: status,
      notes: notes,
      createdAt: createdAt,
      updatedAt: updatedAt,
      serviceName: serviceName,
      providerName: providerName,
      price: price,
      hasReviewed: hasReviewed,
    );
  }

  /// 创建副本
  AppointmentModel copyWith({
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
    return AppointmentModel(
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
}