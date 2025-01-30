import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'notification_service.dart';

class MembershipService extends GetxService {
  final StorageService _storageService = Get.find();
  final NotificationService _notificationService = Get.find();

  final membershipLevel = RxString('free');
  final points = 0.obs;
  final benefits = <String>[].obs;

  @override
  void onInit() {
    super.onInit();
    _loadMembershipData();
  }

  Future<void> _loadMembershipData() async {
    try {
      final data = await _storageService.getLocal('membership_data');
      if (data != null) {
        membershipLevel.value = data['level'] ?? 'free';
        points.value = data['points'] ?? 0;
        benefits.value = List<String>.from(data['benefits'] ?? []);
      }
    } catch (e) {
      // 处理错误
    }
  }

  // 升级会员
  Future<void> upgradeMembership(String level) async {
    try {
      membershipLevel.value = level;
      benefits.value = await _getBenefits(level);
      
      await _saveMembershipData();
      
      await _notificationService.showNotification(
        title: '会员升级成功',
        body: '恭喜您升级到$level会员',
      );
    } catch (e) {
      rethrow;
    }
  }

  // 添加积分
  Future<void> addPoints(int amount) async {
    try {
      points.value += amount;
      await _saveMembershipData();
      
      if (_shouldUpgrade(points.value)) {
        final newLevel = _calculateNewLevel(points.value);
        await upgradeMembership(newLevel);
      }
    } catch (e) {
      rethrow;
    }
  }

  // 使用积分
  Future<void> usePoints(int amount) async {
    if (points.value < amount) {
      throw Exception('积分不足');
    }

    try {
      points.value -= amount;
      await _saveMembershipData();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveMembershipData() async {
    try {
      await _storageService.saveLocal('membership_data', {
        'level': membershipLevel.value,
        'points': points.value,
        'benefits': benefits,
        'updated_at': DateTime.now().toIso8601String(),
      });
    } catch (e) {
      rethrow;
    }
  }

  Future<List<String>> _getBenefits(String level) async {
    print('Retrieving benefits for level: $level');
    // 示例：根据会员等级返回权益列表
    // 实际实现中需要根据具体业务逻辑返回权益
    switch (level) {
      case 'gold':
        return ['Free shipping', 'Priority support', 'Exclusive discounts'];
      case 'silver':
        return ['Free shipping', 'Priority support'];
      default:
        return ['Standard support'];
    }
  }

  bool _shouldUpgrade(int points) {
    print('Checking if upgrade is needed for points: $points');
    // 示例：判断是否应该升级
    // 实际实现中需要根据具体业务逻辑判断
    return points >= 1000;
  }

  String _calculateNewLevel(int points) {
    print('Calculating new level for points: $points');
    // 示例：计算新的会员等级
    // 实际实现中需要根据具体业务逻辑计算
    if (points >= 2000) {
      return 'gold';
    } else if (points >= 1000) {
      return 'silver';
    } else {
      return 'free';
    }
  }
} 