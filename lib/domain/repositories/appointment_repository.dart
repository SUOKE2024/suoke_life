import '../entities/appointment.dart';

/// 预约仓库接口
abstract class AppointmentRepository {
  /// 获取用户所有预约
  Future<List<Appointment>> getUserAppointments(String userId);
  
  /// 获取预约详情
  Future<Appointment> getAppointmentById(String appointmentId);
  
  /// 创建新预约
  Future<Appointment> createAppointment({
    required String userId,
    required String serviceId,
    required String providerId,
    required DateTime appointmentDate,
    required DateTime startTime,
    required DateTime endTime,
    String? notes,
  });
  
  /// 更新预约状态
  Future<Appointment> updateAppointmentStatus(
    String appointmentId, 
    AppointmentStatus status,
  );
  
  /// 取消预约
  Future<bool> cancelAppointment(String appointmentId, {String? reason});
  
  /// 确认预约
  Future<bool> confirmAppointment(String appointmentId);
  
  /// 完成预约
  Future<bool> completeAppointment(String appointmentId);
  
  /// 获取可用的预约时间段
  Future<List<DateTime>> getAvailableTimeSlots({
    required String serviceId, 
    required String providerId,
    required DateTime date,
  });
  
  /// 获取服务提供者工作时间
  Future<Map<String, dynamic>> getProviderWorkingHours(String providerId);
  
  /// 检查时间段是否可用
  Future<bool> isTimeSlotAvailable({
    required String serviceId,
    required String providerId,
    required DateTime startTime,
    required DateTime endTime,
  });
  
  /// 获取服务提供者的预约
  Future<List<Appointment>> getProviderAppointments(
    String providerId, {
    DateTime? startDate,
    DateTime? endDate,
  });
  
  /// 获取用户即将到来的预约
  Future<List<Appointment>> getUpcomingAppointments(String userId);
  
  /// 获取历史预约
  Future<List<Appointment>> getPastAppointments(
    String userId, {
    int limit = 10,
    int offset = 0,
  });
  
  /// 更新预约备注
  Future<bool> updateAppointmentNotes(String appointmentId, String notes);
  
  /// 提醒用户预约（推送通知）
  Future<bool> sendAppointmentReminder(String appointmentId);
  
  /// 重新安排预约
  Future<Appointment> rescheduleAppointment({
    required String appointmentId,
    required DateTime newDate,
    required DateTime newStartTime,
    required DateTime newEndTime,
  });
} 