import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:http/http.dart' as http;

class AudioProcessor {
  static Future<void> adjustVolume(AudioPlayer player, double volume) async {
    await player.setVolume(volume);
  }
  
  static Future<String?> saveAudioFile(String url, String filename) async {
    try {
      final dir = await getTemporaryDirectory();
      final file = File('${dir.path}/$filename');
      
      // 下载或复制音频文件
      if (url.startsWith('http')) {
        final response = await http.get(Uri.parse(url));
        await file.writeAsBytes(response.bodyBytes);
      } else {
        await File(url).copy(file.path);
      }
      
      return file.path;
    } catch (e) {
      print('Error saving audio file: $e');
      return null;
    }
  }
  
  static Future<Duration?> getAudioDuration(String path) async {
    try {
      final player = AudioPlayer();
      final duration = await player.setSource(
        path.startsWith('http') 
          ? UrlSource(path)
          : DeviceFileSource(path)
      );
      await player.dispose();
      return duration;
    } catch (e) {
      print('Error getting audio duration: $e');
      return null;
    }
  }
} 