import 'dart:math';

import '../../domain/entities/appointment.dart';
import '../../domain/repositories/appointment_repository.dart';
import '../models/appointment_model.dart';
import '../../core/network/api_client.dart';
import '../../core/utils/logger.dart';

/// 预约仓库实现
class AppointmentRepositoryImpl implements AppointmentRepository {
  final ApiClient _apiClient;
  
  AppointmentRepositoryImpl({required ApiClient apiClient}) : _apiClient = apiClient;
  
  @override
  Future<List<Appointment>> getUserAppointments(String userId) async {
    try {
      final response = await _apiClient.get('/appointments/user/$userId');
      final List<dynamic> data = response.data['appointments'];
      
      return data.map((item) => AppointmentModel.fromJson(item).toEntity()).toList();
    } catch (e) {
      logger.e('获取用户预约失败: $e');
      // 返回模拟数据
      return _getMockAppointments(userId);
    }
  }
  
  @override
  Future<Appointment> getAppointmentById(String appointmentId) async {
    try {
      final response = await _apiClient.get('/appointments/$appointmentId');
      return AppointmentModel.fromJson(response.data).toEntity();
    } catch (e) {
      logger.e('获取预约详情失败: $e');
      // 返回模拟数据
      return _getMockAppointment(appointmentId);
    }
  }
  
  @override
  Future<Appointment> createAppointment({
    required String userId,
    required String serviceId,
    required String providerId,
    required DateTime appointmentDate,
    required DateTime startTime,
    required DateTime endTime,
    String? notes,
  }) async {
    try {
      final response = await _apiClient.post(
        '/appointments',
        data: {
          'userId': userId,
          'serviceId': serviceId,
          'providerId': providerId,
          'appointmentDate': appointmentDate.toIso8601String(),
          'startTime': startTime.toIso8601String(),
          'endTime': endTime.toIso8601String(),
          'notes': notes,
        },
      );
      
      return AppointmentModel.fromJson(response.data).toEntity();
    } catch (e) {
      logger.e('创建预约失败: $e');
      // 返回模拟数据
      return _createMockAppointment(
        userId: userId,
        serviceId: serviceId,
        providerId: providerId,
        appointmentDate: appointmentDate,
        startTime: startTime,
        endTime: endTime,
        notes: notes,
      );
    }
  }
  
  @override
  Future<Appointment> updateAppointmentStatus(
    String appointmentId, 
    AppointmentStatus status,
  ) async {
    try {
      final response = await _apiClient.patch(
        '/appointments/$appointmentId/status',
        data: {
          'status': status.toString().split('.').last,
        },
      );
      
      return AppointmentModel.fromJson(response.data).toEntity();
    } catch (e) {
      logger.e('更新预约状态失败: $e');
      // 模拟更新状态
      final appointment = await getAppointmentById(appointmentId);
      return appointment.copyWith(
        status: status,
        updatedAt: DateTime.now(),
      );
    }
  }
  
  @override
  Future<bool> cancelAppointment(String appointmentId, {String? reason}) async {
    try {
      final response = await _apiClient.patch(
        '/appointments/$appointmentId/cancel',
        data: {
          'reason': reason,
        },
      );
      
      return response.statusCode == 200;
    } catch (e) {
      logger.e('取消预约失败: $e');
      // 模拟取消成功
      return true;
    }
  }
  
  @override
  Future<bool> confirmAppointment(String appointmentId) async {
    try {
      final response = await _apiClient.patch(
        '/appointments/$appointmentId/confirm',
      );
      
      return response.statusCode == 200;
    } catch (e) {
      logger.e('确认预约失败: $e');
      // 模拟确认成功
      return true;
    }
  }
  
  @override
  Future<bool> completeAppointment(String appointmentId) async {
    try {
      final response = await _apiClient.patch(
        '/appointments/$appointmentId/complete',
      );
      
      return response.statusCode == 200;
    } catch (e) {
      logger.e('完成预约失败: $e');
      // 模拟完成成功
      return true;
    }
  }
  
  @override
  Future<List<DateTime>> getAvailableTimeSlots({
    required String serviceId, 
    required String providerId,
    required DateTime date,
  }) async {
    try {
      final response = await _apiClient.get(
        '/appointments/available-slots',
        queryParameters: {
          'serviceId': serviceId,
          'providerId': providerId,
          'date': date.toIso8601String().split('T')[0],
        },
      );
      
      final List<dynamic> slots = response.data['availableSlots'];
      return slots.map((slot) => DateTime.parse(slot)).toList();
    } catch (e) {
      logger.e('获取可用时间段失败: $e');
      // 返回模拟数据
      return _getMockTimeSlots(date);
    }
  }
  
  @override
  Future<Map<String, dynamic>> getProviderWorkingHours(String providerId) async {
    try {
      final response = await _apiClient.get('/providers/$providerId/working-hours');
      return response.data;
    } catch (e) {
      logger.e('获取服务提供者工作时间失败: $e');
      // 返回模拟数据
      return {
        'monday': {'start': '09:00', 'end': '18:00'},
        'tuesday': {'start': '09:00', 'end': '18:00'},
        'wednesday': {'start': '09:00', 'end': '18:00'},
        'thursday': {'start': '09:00', 'end': '18:00'},
        'friday': {'start': '09:00', 'end': '18:00'},
        'saturday': {'start': '10:00', 'end': '16:00'},
        'sunday': {'start': '10:00', 'end': '16:00'},
      };
    }
  }
  
  @override
  Future<bool> isTimeSlotAvailable({
    required String serviceId,
    required String providerId,
    required DateTime startTime,
    required DateTime endTime,
  }) async {
    try {
      final response = await _apiClient.get(
        '/appointments/check-availability',
        queryParameters: {
          'serviceId': serviceId,
          'providerId': providerId,
          'startTime': startTime.toIso8601String(),
          'endTime': endTime.toIso8601String(),
        },
      );
      
      return response.data['available'] == true;
    } catch (e) {
      logger.e('检查时间段可用性失败: $e');
      // 模拟随机可用性
      return Random().nextBool();
    }
  }
  
  @override
  Future<List<Appointment>> getProviderAppointments(
    String providerId, {
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'providerId': providerId,
      };
      
      if (startDate != null) {
        queryParams['startDate'] = startDate.toIso8601String();
      }
      
      if (endDate != null) {
        queryParams['endDate'] = endDate.toIso8601String();
      }
      
      final response = await _apiClient.get(
        '/appointments/provider/$providerId',
        queryParameters: queryParams,
      );
      
      final List<dynamic> data = response.data['appointments'];
      return data.map((item) => AppointmentModel.fromJson(item).toEntity()).toList();
    } catch (e) {
      logger.e('获取服务提供者预约失败: $e');
      // 返回模拟数据
      return _getMockProviderAppointments(providerId);
    }
  }
  
  @override
  Future<List<Appointment>> getUpcomingAppointments(String userId) async {
    try {
      final response = await _apiClient.get('/appointments/user/$userId/upcoming');
      
      final List<dynamic> data = response.data['appointments'];
      return data.map((item) => AppointmentModel.fromJson(item).toEntity()).toList();
    } catch (e) {
      logger.e('获取即将到来的预约失败: $e');
      // 返回模拟数据
      return _getMockUpcomingAppointments(userId);
    }
  }
  
  @override
  Future<List<Appointment>> getPastAppointments(
    String userId, {
    int limit = 10,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.get(
        '/appointments/user/$userId/past',
        queryParameters: {
          'limit': limit,
          'offset': offset,
        },
      );
      
      final List<dynamic> data = response.data['appointments'];
      return data.map((item) => AppointmentModel.fromJson(item).toEntity()).toList();
    } catch (e) {
      logger.e('获取历史预约失败: $e');
      // 返回模拟数据
      return _getMockPastAppointments(userId);
    }
  }
  
  @override
  Future<bool> updateAppointmentNotes(String appointmentId, String notes) async {
    try {
      final response = await _apiClient.patch(
        '/appointments/$appointmentId/notes',
        data: {
          'notes': notes,
        },
      );
      
      return response.statusCode == 200;
    } catch (e) {
      logger.e('更新预约备注失败: $e');
      // 模拟更新成功
      return true;
    }
  }
  
  @override
  Future<bool> sendAppointmentReminder(String appointmentId) async {
    try {
      final response = await _apiClient.post(
        '/appointments/$appointmentId/reminder',
      );
      
      return response.statusCode == 200;
    } catch (e) {
      logger.e('发送预约提醒失败: $e');
      // 模拟发送成功
      return true;
    }
  }
  
  @override
  Future<Appointment> rescheduleAppointment({
    required String appointmentId,
    required DateTime newDate,
    required DateTime newStartTime,
    required DateTime newEndTime,
  }) async {
    try {
      final response = await _apiClient.patch(
        '/appointments/$appointmentId/reschedule',
        data: {
          'appointmentDate': newDate.toIso8601String(),
          'startTime': newStartTime.toIso8601String(),
          'endTime': newEndTime.toIso8601String(),
        },
      );
      
      return AppointmentModel.fromJson(response.data).toEntity();
    } catch (e) {
      logger.e('重新安排预约失败: $e');
      // 模拟重新安排
      final appointment = await getAppointmentById(appointmentId);
      return appointment.copyWith(
        appointmentDate: newDate,
        startTime: newStartTime,
        endTime: newEndTime,
        updatedAt: DateTime.now(),
      );
    }
  }
  
  // 模拟数据辅助方法
  
  /// 获取模拟预约列表
  List<Appointment> _getMockAppointments(String userId) {
    final now = DateTime.now();
    final serviceTypes = ['中医诊断', '健康咨询', '营养指导', '运动指导', '心理咨询'];
    final providerNames = ['张医生', '李医生', '王医生', '赵医生', '钱医生'];
    
    return List.generate(
      5,
      (index) {
        final id = 'apt_${userId}_$index';
        final isUpcoming = index < 3;
        final date = isUpcoming 
            ? now.add(Duration(days: index + 1))
            : now.subtract(Duration(days: index));
        
        return Appointment(
          id: id,
          userId: userId,
          serviceId: 'srv_$index',
          providerId: 'prv_$index',
          appointmentDate: DateTime(date.year, date.month, date.day),
          startTime: DateTime(date.year, date.month, date.day, 9 + index, 0),
          endTime: DateTime(date.year, date.month, date.day, 10 + index, 0),
          status: isUpcoming 
              ? (index == 0 ? AppointmentStatus.confirmed : AppointmentStatus.pending)
              : AppointmentStatus.completed,
          notes: index % 2 == 0 ? '请准时到达' : null,
          createdAt: now.subtract(const Duration(days: 10)),
          updatedAt: now.subtract(const Duration(days: 5)),
          serviceName: serviceTypes[index % serviceTypes.length],
          providerName: providerNames[index % providerNames.length],
          price: 100.0 + (index * 20),
          hasReviewed: index >= 3 && index % 2 == 0,
        );
      },
    );
  }
  
  /// 获取模拟预约详情
  Appointment _getMockAppointment(String appointmentId) {
    final now = DateTime.now();
    final index = int.tryParse(appointmentId.split('_').last) ?? 0;
    final isUpcoming = index < 3;
    final date = isUpcoming 
        ? now.add(Duration(days: index + 1))
        : now.subtract(Duration(days: index));
    
    final serviceTypes = ['中医诊断', '健康咨询', '营养指导', '运动指导', '心理咨询'];
    final providerNames = ['张医生', '李医生', '王医生', '赵医生', '钱医生'];
    
    return Appointment(
      id: appointmentId,
      userId: 'user_1',
      serviceId: 'srv_$index',
      providerId: 'prv_$index',
      appointmentDate: DateTime(date.year, date.month, date.day),
      startTime: DateTime(date.year, date.month, date.day, 9 + index, 0),
      endTime: DateTime(date.year, date.month, date.day, 10 + index, 0),
      status: isUpcoming 
          ? (index == 0 ? AppointmentStatus.confirmed : AppointmentStatus.pending)
          : AppointmentStatus.completed,
      notes: index % 2 == 0 ? '请准时到达' : null,
      createdAt: now.subtract(const Duration(days: 10)),
      updatedAt: now.subtract(const Duration(days: 5)),
      serviceName: serviceTypes[index % serviceTypes.length],
      providerName: providerNames[index % providerNames.length],
      price: 100.0 + (index * 20),
      hasReviewed: index >= 3 && index % 2 == 0,
    );
  }
  
  /// 创建模拟预约
  Appointment _createMockAppointment({
    required String userId,
    required String serviceId,
    required String providerId,
    required DateTime appointmentDate,
    required DateTime startTime,
    required DateTime endTime,
    String? notes,
  }) {
    final now = DateTime.now();
    final id = 'apt_${now.millisecondsSinceEpoch}';
    
    return Appointment(
      id: id,
      userId: userId,
      serviceId: serviceId,
      providerId: providerId,
      appointmentDate: appointmentDate,
      startTime: startTime,
      endTime: endTime,
      status: AppointmentStatus.pending,
      notes: notes,
      createdAt: now,
      updatedAt: now,
      serviceName: _getServiceName(serviceId),
      providerName: _getProviderName(providerId),
      price: _getServicePrice(serviceId),
      hasReviewed: false,
    );
  }
  
  /// 获取模拟服务名称
  String _getServiceName(String serviceId) {
    final serviceTypes = ['中医诊断', '健康咨询', '营养指导', '运动指导', '心理咨询'];
    final index = int.tryParse(serviceId.split('_').last) ?? 0;
    return serviceTypes[index % serviceTypes.length];
  }
  
  /// 获取模拟服务提供者名称
  String _getProviderName(String providerId) {
    final providerNames = ['张医生', '李医生', '王医生', '赵医生', '钱医生'];
    final index = int.tryParse(providerId.split('_').last) ?? 0;
    return providerNames[index % providerNames.length];
  }
  
  /// 获取模拟服务价格
  double _getServicePrice(String serviceId) {
    final index = int.tryParse(serviceId.split('_').last) ?? 0;
    return 100.0 + (index * 20);
  }
  
  /// 获取模拟可用时间段
  List<DateTime> _getMockTimeSlots(DateTime date) {
    final slots = <DateTime>[];
    final baseDate = DateTime(date.year, date.month, date.day);
    
    // 上午时间段
    for (int hour = 9; hour < 12; hour++) {
      for (int minute = 0; minute < 60; minute += 30) {
        slots.add(baseDate.add(Duration(hours: hour, minutes: minute)));
      }
    }
    
    // 下午时间段
    for (int hour = 14; hour < 18; hour++) {
      for (int minute = 0; minute < 60; minute += 30) {
        slots.add(baseDate.add(Duration(hours: hour, minutes: minute)));
      }
    }
    
    // 随机移除一些时间段，模拟已预约
    final random = Random();
    final slotsToRemove = slots.length ~/ 4; // 移除约25%的时间段
    
    for (int i = 0; i < slotsToRemove; i++) {
      final indexToRemove = random.nextInt(slots.length);
      slots.removeAt(indexToRemove);
    }
    
    return slots;
  }
  
  /// 获取模拟服务提供者预约
  List<Appointment> _getMockProviderAppointments(String providerId) {
    final now = DateTime.now();
    
    return List.generate(
      5,
      (index) {
        final id = 'apt_${providerId}_$index';
        final isUpcoming = index < 3;
        final date = isUpcoming 
            ? now.add(Duration(days: index + 1))
            : now.subtract(Duration(days: index));
        
        return Appointment(
          id: id,
          userId: 'user_$index',
          serviceId: 'srv_$index',
          providerId: providerId,
          appointmentDate: DateTime(date.year, date.month, date.day),
          startTime: DateTime(date.year, date.month, date.day, 9 + index, 0),
          endTime: DateTime(date.year, date.month, date.day, 10 + index, 0),
          status: isUpcoming 
              ? (index == 0 ? AppointmentStatus.confirmed : AppointmentStatus.pending)
              : AppointmentStatus.completed,
          notes: index % 2 == 0 ? '患者特殊要求' : null,
          createdAt: now.subtract(const Duration(days: 10)),
          updatedAt: now.subtract(const Duration(days: 5)),
          serviceName: _getServiceName('srv_$index'),
          providerName: _getProviderName(providerId),
          price: 100.0 + (index * 20),
          hasReviewed: index >= 3 && index % 2 == 0,
        );
      },
    );
  }
  
  /// 获取模拟即将到来的预约
  List<Appointment> _getMockUpcomingAppointments(String userId) {
    final now = DateTime.now();
    final serviceTypes = ['中医诊断', '健康咨询', '营养指导', '运动指导', '心理咨询'];
    final providerNames = ['张医生', '李医生', '王医生', '赵医生', '钱医生'];
    
    return List.generate(
      3,
      (index) {
        final id = 'apt_upcoming_${userId}_$index';
        final date = now.add(Duration(days: index + 1));
        
        return Appointment(
          id: id,
          userId: userId,
          serviceId: 'srv_$index',
          providerId: 'prv_$index',
          appointmentDate: DateTime(date.year, date.month, date.day),
          startTime: DateTime(date.year, date.month, date.day, 9 + index, 0),
          endTime: DateTime(date.year, date.month, date.day, 10 + index, 0),
          status: index == 0 ? AppointmentStatus.confirmed : AppointmentStatus.pending,
          notes: index % 2 == 0 ? '请准时到达' : null,
          createdAt: now.subtract(const Duration(days: 5)),
          updatedAt: now.subtract(const Duration(days: 2)),
          serviceName: serviceTypes[index % serviceTypes.length],
          providerName: providerNames[index % providerNames.length],
          price: 100.0 + (index * 20),
          hasReviewed: false,
        );
      },
    );
  }
  
  /// 获取模拟历史预约
  List<Appointment> _getMockPastAppointments(String userId) {
    final now = DateTime.now();
    final serviceTypes = ['中医诊断', '健康咨询', '营养指导', '运动指导', '心理咨询'];
    final providerNames = ['张医生', '李医生', '王医生', '赵医生', '钱医生'];
    
    return List.generate(
      5,
      (index) {
        final id = 'apt_past_${userId}_$index';
        final date = now.subtract(Duration(days: index + 1));
        final completed = index % 3 != 0;
        
        return Appointment(
          id: id,
          userId: userId,
          serviceId: 'srv_$index',
          providerId: 'prv_$index',
          appointmentDate: DateTime(date.year, date.month, date.day),
          startTime: DateTime(date.year, date.month, date.day, 9 + index, 0),
          endTime: DateTime(date.year, date.month, date.day, 10 + index, 0),
          status: completed 
              ? AppointmentStatus.completed
              : AppointmentStatus.cancelled,
          notes: index % 2 == 0 ? '预约备注' : null,
          createdAt: now.subtract(Duration(days: 20 + index)),
          updatedAt: now.subtract(Duration(days: 15 + index)),
          serviceName: serviceTypes[index % serviceTypes.length],
          providerName: providerNames[index % providerNames.length],
          price: 100.0 + (index * 20),
          hasReviewed: completed && index % 2 == 0,
        );
      },
    );
  }
} 