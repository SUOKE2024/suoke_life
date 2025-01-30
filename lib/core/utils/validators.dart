class Validators {
  static String? username(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入用户名';
    }
    if (value.length < 3) {
      return '用户名至少3个字符';
    }
    if (value.length > 20) {
      return '用户名最多20个字符';
    }
    if (!RegExp(r'^[a-zA-Z0-9_]+$').hasMatch(value)) {
      return '用户名只能包含字母、数字和下划线';
    }
    return null;
  }

  static String? password(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入密码';
    }
    if (value.length < 6) {
      return '密码至少6个字符';
    }
    if (value.length > 20) {
      return '密码最多20个字符';
    }
    if (!RegExp(r'^[a-zA-Z0-9_@#$%^&*]+$').hasMatch(value)) {
      return '密码只能包含字母、数字和特殊字符';
    }
    return null;
  }

  static String? email(String? value) {
    if (value == null || value.isEmpty) {
      return null; // 邮箱可选
    }
    if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
      return '请输入有效的邮箱地址';
    }
    return null;
  }

  static String? confirmPassword(String? value, String password) {
    if (value == null || value.isEmpty) {
      return '请确认密码';
    }
    if (value != password) {
      return '两次输入的密码不一致';
    }
    return null;
  }
} 