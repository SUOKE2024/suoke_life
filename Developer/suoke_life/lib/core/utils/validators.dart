/// 表单验证工具类
class Validators {
  // 私有构造器，防止实例化
  Validators._();

  /// 验证用户名
  /// 规则：3-20个字符，只能包含字母、数字、下划线
  static String? validateUsername(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入用户名';
    }
    
    if (value.length < 3) {
      return '用户名至少需要3个字符';
    }
    
    if (value.length > 20) {
      return '用户名最多20个字符';
    }
    
    if (!RegExp(r'^[a-zA-Z0-9_]+$').hasMatch(value)) {
      return '用户名只能包含字母、数字和下划线';
    }
    
    return null;
  }

  /// 验证邮箱
  /// 规则：符合标准邮箱格式
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入邮箱';
    }
    
    final emailRegex = RegExp(
      r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$',
    );
    
    if (!emailRegex.hasMatch(value)) {
      return '请输入有效的邮箱地址';
    }
    
    return null;
  }

  /// 验证手机号
  /// 规则：中国大陆手机号，11位数字，以1开头
  static String? validatePhoneNumber(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入手机号';
    }
    
    if (!RegExp(r'^1[3-9]\d{9}$').hasMatch(value)) {
      return '请输入有效的手机号';
    }
    
    return null;
  }

  /// 验证密码
  /// 规则：至少8个字符，至少包含1个大写字母，1个小写字母和1个数字
  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入密码';
    }
    
    if (value.length < 8) {
      return '密码至少需要8个字符';
    }
    
    if (!RegExp(r'(?=.*[a-z])').hasMatch(value)) {
      return '密码必须包含至少一个小写字母';
    }
    
    if (!RegExp(r'(?=.*[A-Z])').hasMatch(value)) {
      return '密码必须包含至少一个大写字母';
    }
    
    if (!RegExp(r'(?=.*\d)').hasMatch(value)) {
      return '密码必须包含至少一个数字';
    }
    
    return null;
  }

  /// 验证确认密码
  /// 规则：必须与原密码相同
  static String? validateConfirmPassword(String? value, String password) {
    if (value == null || value.isEmpty) {
      return '请确认密码';
    }
    
    if (value != password) {
      return '两次输入的密码不一致';
    }
    
    return null;
  }

  /// 验证验证码
  /// 规则：6位数字
  static String? validateVerificationCode(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入验证码';
    }
    
    if (!RegExp(r'^\d{6}$').hasMatch(value)) {
      return '验证码为6位数字';
    }
    
    return null;
  }

  /// 验证姓名
  /// 规则：2-30个字符，允许中文、英文字母、空格和点号
  static String? validateName(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入姓名';
    }
    
    if (value.length < 2 || value.length > 30) {
      return '姓名长度应在2-30个字符之间';
    }
    
    if (!RegExp(r'^[\u4e00-\u9fa5a-zA-Z\s.]+$').hasMatch(value)) {
      return '姓名格式不正确';
    }
    
    return null;
  }

  /// 验证年龄
  /// 规则：1-120之间的整数
  static String? validateAge(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入年龄';
    }
    
    final age = int.tryParse(value);
    if (age == null) {
      return '请输入有效的年龄';
    }
    
    if (age < 1 || age > 120) {
      return '年龄应在1-120岁之间';
    }
    
    return null;
  }

  /// 验证身高
  /// 规则：50-250之间的数字（cm）
  static String? validateHeight(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入身高';
    }
    
    final height = double.tryParse(value);
    if (height == null) {
      return '请输入有效的身高';
    }
    
    if (height < 50 || height > 250) {
      return '身高应在50-250厘米之间';
    }
    
    return null;
  }

  /// 验证体重
  /// 规则：2-300之间的数字（kg）
  static String? validateWeight(String? value) {
    if (value == null || value.isEmpty) {
      return '请输入体重';
    }
    
    final weight = double.tryParse(value);
    if (weight == null) {
      return '请输入有效的体重';
    }
    
    if (weight < 2 || weight > 300) {
      return '体重应在2-300千克之间';
    }
    
    return null;
  }

  /// 验证非空
  /// 规则：不能为空
  static String? validateRequired(String? value, String fieldName) {
    if (value == null || value.trim().isEmpty) {
      return '请输入$fieldName';
    }
    
    return null;
  }
} 