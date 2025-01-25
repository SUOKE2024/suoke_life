import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'notification_service.dart';

class ConsultationService extends GetxService {
  final StorageService _storageService = Get.find();
  final NotificationService _notificationService = Get.find();

  // 预约咨询
  Future<void> bookConsultation({
    required String doctorId,
    required DateTime time,
    required String type,
    String? description,
  }) async {
    try {
      final appointment = {
        'id': DateTime.now().toString(),
        'doctor_id': doctorId,
        'time': time.toIso8601String(),
        'type': type,
        'description': description,
        'status': 'pending',
        'created_at': DateTime.now().toIso8601String(),
      };

      // 保存预约信息
      await _saveAppointment(appointment);
      
      // 发送通知
      await _notificationService.showNotification(
        title: '预约成功',
        body: '您已成功预约${time.toString()}的咨询',
        payload: '/consultation/detail/${appointment['id']}',
      );
    } catch (e) {
      rethrow;
    }
  }

  // 取消预约
  Future<void> cancelConsultation(String appointmentId) async {
    try {
      final appointments = await _getAppointments();
      final index = appointments.indexWhere((a) => a['id'] == appointmentId);
      
      if (index != -1) {
        appointments[index]['status'] = 'cancelled';
        await _storageService.saveLocal('appointments', appointments);
        
        await _notificationService.showNotification(
          title: '预约已取消',
          body: '您的咨询预约已取消',
        );
      }
    } catch (e) {
      rethrow;
    }
  }

  // 获取预约列表
  Future<List<Map<String, dynamic>>> getAppointments({String? status}) async {
    try {
      final appointments = await _getAppointments();
      if (status != null) {
        return appointments.where((a) => a['status'] == status).toList();
      }
      return appointments;
    } catch (e) {
      return [];
    }
  }

  Future<void> _saveAppointment(Map<String, dynamic> appointment) async {
    try {
      final appointments = await _getAppointments();
      appointments.add(appointment);
      await _storageService.saveLocal('appointments', appointments);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getAppointments() async {
    try {
      final data = await _storageService.getLocal('appointments');
      return data != null ? List<Map<String, dynamic>>.from(data) : [];
    } catch (e) {
      return [];
    }
  }
} 