import 'package:get/get.dart';
import '../../../core/storage/storage_service.dart';
import '../../../services/logging_service.dart';

class SocialManagerService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  // 社交数据
  final friends = <String, Map<String, dynamic>>{}.obs;
  final messages = <String, List<Map<String, dynamic>>>{}.obs;
  final activities = <Map<String, dynamic>>[].obs;
  final groups = <String, Map<String, dynamic>>{}.obs;
  final interactions = <Map<String, dynamic>>[].obs;

  @override
  void onInit() {
    super.onInit();
    _initSocialManager();
  }

  Future<void> _initSocialManager() async {
    try {
      await Future.wait([
        _loadFriends(),
        _loadMessages(),
        _loadActivities(),
        _loadGroups(),
        _loadInteractions(),
      ]);
      _startInteractionMonitoring();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize social manager', data: {'error': e.toString()});
    }
  }

  // 好友管理
  Future<void> addFriend(String userId, Map<String, dynamic> friendInfo) async {
    try {
      friends[userId] = {
        ...friendInfo,
        'added_at': DateTime.now().toIso8601String(),
        'status': 'pending',
      };
      await _saveFriends();
      await _recordInteraction('add_friend', {'friend_id': userId});
    } catch (e) {
      await _loggingService.log('error', 'Failed to add friend', data: {'user_id': userId, 'error': e.toString()});
      rethrow;
    }
  }

  Future<void> acceptFriend(String userId) async {
    try {
      if (!friends.containsKey(userId)) {
        throw Exception('Friend request not found');
      }

      friends[userId] = {
        ...friends[userId]!,
        'status': 'accepted',
        'accepted_at': DateTime.now().toIso8601String(),
      };
      await _saveFriends();
      await _recordInteraction('accept_friend', {'friend_id': userId});
    } catch (e) {
      await _loggingService.log('error', 'Failed to accept friend', data: {'user_id': userId, 'error': e.toString()});
      rethrow;
    }
  }

  // 消息管理
  Future<void> sendMessage(String toUserId, Map<String, dynamic> message) async {
    try {
      final newMessage = {
        ...message,
        'to_user_id': toUserId,
        'sent_at': DateTime.now().toIso8601String(),
        'status': 'sent',
      };

      if (!messages.containsKey(toUserId)) {
        messages[toUserId] = [];
      }
      messages[toUserId]!.insert(0, newMessage);
      
      await _saveMessages();
      await _recordInteraction('send_message', {
        'to_user_id': toUserId,
        'message_id': newMessage['id'],
      });
    } catch (e) {
      await _loggingService.log('error', 'Failed to send message', data: {'to_user_id': toUserId, 'error': e.toString()});
      rethrow;
    }
  }

  // 活动管理
  Future<void> createActivity(Map<String, dynamic> activity) async {
    try {
      final newActivity = {
        ...activity,
        'created_at': DateTime.now().toIso8601String(),
        'status': 'active',
        'participants': [],
      };

      activities.insert(0, newActivity);
      await _saveActivities();
      await _recordInteraction('create_activity', {'activity_id': newActivity['id']});
    } catch (e) {
      await _loggingService.log('error', 'Failed to create activity', data: {'error': e.toString()});
      rethrow;
    }
  }

  Future<void> joinActivity(String activityId) async {
    try {
      final index = activities.indexWhere((a) => a['id'] == activityId);
      if (index == -1) {
        throw Exception('Activity not found');
      }

      final participants = List<String>.from(activities[index]['participants']);
      if (!participants.contains(Get.find<UserService>().currentUser.value?.id)) {
        participants.add(Get.find<UserService>().currentUser.value!.id);
        activities[index] = {
          ...activities[index],
          'participants': participants,
        };
        await _saveActivities();
        await _recordInteraction('join_activity', {'activity_id': activityId});
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to join activity', data: {'activity_id': activityId, 'error': e.toString()});
      rethrow;
    }
  }

  // 群组管理
  Future<void> createGroup(String groupId, Map<String, dynamic> groupInfo) async {
    try {
      groups[groupId] = {
        ...groupInfo,
        'created_at': DateTime.now().toIso8601String(),
        'members': [Get.find<UserService>().currentUser.value!.id],
      };
      await _saveGroups();
      await _recordInteraction('create_group', {'group_id': groupId});
    } catch (e) {
      await _loggingService.log('error', 'Failed to create group', data: {'group_id': groupId, 'error': e.toString()});
      rethrow;
    }
  }

  Future<void> joinGroup(String groupId) async {
    try {
      if (!groups.containsKey(groupId)) {
        throw Exception('Group not found');
      }

      final members = List<String>.from(groups[groupId]!['members']);
      if (!members.contains(Get.find<UserService>().currentUser.value?.id)) {
        members.add(Get.find<UserService>().currentUser.value!.id);
        groups[groupId] = {
          ...groups[groupId]!,
          'members': members,
        };
        await _saveGroups();
        await _recordInteraction('join_group', {'group_id': groupId});
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to join group', data: {'group_id': groupId, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取互动历史
  Future<List<Map<String, dynamic>>> getInteractionHistory({
    String? type,
    String? targetId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      var history = interactions.toList();

      if (type != null) {
        history = history.where((i) => i['type'] == type).toList();
      }

      if (targetId != null) {
        history = history.where((i) => 
          i['friend_id'] == targetId || 
          i['to_user_id'] == targetId ||
          i['activity_id'] == targetId ||
          i['group_id'] == targetId
        ).toList();
      }

      if (startDate != null || endDate != null) {
        history = history.where((i) {
          final timestamp = DateTime.parse(i['timestamp']);
          if (startDate != null && timestamp.isBefore(startDate)) return false;
          if (endDate != null && timestamp.isAfter(endDate)) return false;
          return true;
        }).toList();
      }

      return history;
    } catch (e) {
      await _loggingService.log('error', 'Failed to get interaction history', data: {'error': e.toString()});
      return [];
    }
  }

  void _startInteractionMonitoring() {
    // TODO: 实现互动监控逻辑
  }

  Future<void> _recordInteraction(
    String type,
    Map<String, dynamic> data,
  ) async {
    try {
      final interaction = {
        'type': type,
        'data': data,
        'user_id': Get.find<UserService>().currentUser.value?.id,
        'timestamp': DateTime.now().toIso8601String(),
      };

      interactions.insert(0, interaction);
      
      // 只保留最近1000条记录
      if (interactions.length > 1000) {
        interactions.removeRange(1000, interactions.length);
      }
      
      await _saveInteractions();
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadFriends() async {
    try {
      final saved = await _storageService.getLocal('friends');
      if (saved != null) {
        friends.value = Map<String, Map<String, dynamic>>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveFriends() async {
    try {
      await _storageService.saveLocal('friends', friends.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadMessages() async {
    try {
      final saved = await _storageService.getLocal('messages');
      if (saved != null) {
        messages.value = Map<String, List<Map<String, dynamic>>>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveMessages() async {
    try {
      await _storageService.saveLocal('messages', messages.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadActivities() async {
    try {
      final saved = await _storageService.getLocal('activities');
      if (saved != null) {
        activities.value = List<Map<String, dynamic>>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveActivities() async {
    try {
      await _storageService.saveLocal('activities', activities.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadGroups() async {
    try {
      final saved = await _storageService.getLocal('groups');
      if (saved != null) {
        groups.value = Map<String, Map<String, dynamic>>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveGroups() async {
    try {
      await _storageService.saveLocal('groups', groups.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadInteractions() async {
    try {
      final saved = await _storageService.getLocal('interactions');
      if (saved != null) {
        interactions.value = List<Map<String, dynamic>>.from(saved);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveInteractions() async {
    try {
      await _storageService.saveLocal('interactions', interactions.value);
    } catch (e) {
      rethrow;
    }
  }
} 