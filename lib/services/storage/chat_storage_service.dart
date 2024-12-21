import '../../models/message.dart';

abstract class ChatStorageService {
  Future<List<Message>> getMessages();
  Future<void> saveMessage(Message message);
  Future<String> uploadVoice(String path);
  Future<String> uploadImage(String path);
  Future<String> uploadVideo(String path);
  Future<String> generateThumbnail(String videoPath);
} 