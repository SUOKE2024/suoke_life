import 'package:timeago/timeago.dart' as timeago;

class TimeagoUtils {
  static void init() {
    timeago.setLocaleMessages('zh', timeago.ZhMessages());
    timeago.setLocaleMessages('en', timeago.EnMessages());
  }
} 