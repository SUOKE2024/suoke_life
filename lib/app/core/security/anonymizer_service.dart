class AnonymizerService {
  String anonymizePhoneNumber(String phone) {
    if (phone.length < 7) return phone;
    return '${phone.substring(0, 3)}****${phone.substring(7)}';
  }

  String anonymizeEmail(String email) {
    final parts = email.split('@');
    if (parts.length != 2) return email;
    final name = parts[0];
    if (name.length <= 2) return email;
    return '${name[0]}***${name[name.length-1]}@${parts[1]}';
  }

  Map<String, dynamic> anonymizeUserData(Map<String, dynamic> userData) {
    return {
      'id': userData['id'],
      'age_range': _getAgeRange(userData['age'] as int),
      'region': userData['province'],
      'gender': userData['gender'],
      // 移除敏感信息
      'name': null,
      'phone': null,
      'email': null,
      'address': null,
    };
  }

  String _getAgeRange(int age) {
    if (age < 18) return '<18';
    if (age < 25) return '18-24';
    if (age < 35) return '25-34';
    if (age < 45) return '35-44';
    if (age < 55) return '45-54';
    return '55+';
  }
} 