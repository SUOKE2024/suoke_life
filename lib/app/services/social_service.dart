import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class SocialService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final friends = <String, Map<String, dynamic>>{}.obs;
  final messages = <String, List<Map<String, dynamic>>>{}.obs;
  final activities = <Map<String, dynamic>>[].obs;
  final groups = <String, Map<String, dynamic>>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initSocial();
  }

  Future<void> _initSocial() async {
    try {
      await Future.wait([
        _loadFriends(),
        _loadMessages(),
        _loadActivities(),
        _loadGroups(),
      ]);
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize social', data: {'error': e.toString()});
    }
  }

  // 好友管理
  Future<void> addFriend(String userId, Map<String, dynamic> friendInfo) async {
    try {
      friends[userId] = {
        ...friendInfo,
        'added_at': DateTime.now().toIso8601String(),
      };
      await _saveFriends();
    } catch (e) {
      await _loggingService.log('error', 'Failed to add friend', data: {'user_id': userId, 'error': e.toString()});
      rethrow;
    }
  }

  Future<void> removeFriend(String userId) async {
    try {
      friends.remove(userId);
      await _saveFriends();
    } catch (e) {
      await _loggingService.log('error', 'Failed to remove friend', data: {'user_id': userId, 'error': e.toString()});
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
    } catch (e) {
      await _loggingService.log('error', 'Failed to send message', data: {'to_user_id': toUserId, 'error': e.toString()});
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getMessages(String userId) async {
    try {
      return messages[userId] ?? [];
    } catch (e) {
      await _loggingService.log('error', 'Failed to get messages', data: {'user_id': userId, 'error': e.toString()});
      return [];
    }
  }

  // 活动管理
  Future<void> createActivity(Map<String, dynamic> activity) async {
    try {
      final newActivity = {
        ...activity,
        'created_at': DateTime.now().toIso8601String(),
        'status': 'active',
      };

      activities.insert(0, newActivity);
      await _saveActivities();
    } catch (e) {
      await _loggingService.log('error', 'Failed to create activity', data: {'error': e.toString()});
      rethrow;
    }
  }

  Future<void> joinActivity(String activityId, String userId) async {
    try {
      final index = activities.indexWhere((a) => a['id'] == activityId);
      if (index == -1) {
        throw Exception('Activity not found');
      }

      final participants = List<String>.from(activities[index]['participants'] ?? []);
      if (!participants.contains(userId)) {
        participants.add(userId);
        activities[index] = {
          ...activities[index],
          'participants': participants,
        };
        await _saveActivities();
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
        'members': [],
      };
      await _saveGroups();
    } catch (e) {
      await _loggingService.log('error', 'Failed to create group', data: {'group_id': groupId, 'error': e.toString()});
      rethrow;
    }
  }

  Future<void> joinGroup(String groupId, String userId) async {
    try {
      if (!groups.containsKey(groupId)) {
        throw Exception('Group not found');
      }

      final members = List<String>.from(groups[groupId]!['members']);
      if (!members.contains(userId)) {
        members.add(userId);
        groups[groupId] = {
          ...groups[groupId]!,
          'members': members,
        };
        await _saveGroups();
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to join group', data: {'group_id': groupId, 'error': e.toString()});
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

  Future<void> _saveFriends() async {
    try {
      await _storageService.saveLocal('friends', friends.value);
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

  Future<void> _saveActivities() async {
    try {
      await _storageService.saveLocal('activities', activities.value);
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
} 