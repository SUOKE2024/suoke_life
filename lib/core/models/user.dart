class User {
  final int? id;
  final String name;
  final String email;
  final String? avatarUrl;
  final String? bio;
  final String? phoneNumber;
  final String? address;
  final int? age;
  final String? gender;

  User({
    this.id,
    required this.name,
    required this.email,
    this.avatarUrl,
    this.bio,
    this.phoneNumber,
    this.address,
    this.age,
    this.gender,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'avatarUrl': avatarUrl,
      'bio': bio,
      'phone_number': phoneNumber,
      'address': address,
      'age': age,
      'gender': gender,
    };
  }

  factory User.fromMap(Map<String, dynamic> map) {
    return User(
      id: map['id'],
      name: map['name'],
      email: map['email'],
      avatarUrl: map['avatarUrl'],
      bio: map['bio'],
      phoneNumber: map['phone_number'],
      address: map['address'],
      age: map['age'],
      gender: map['gender'],
    );
  }

  User copyWith({
    int? id,
    String? name,
    String? email,
    String? avatarUrl,
    String? bio,
    String? phoneNumber,
    String? address,
    int? age,
    String? gender,
  }) {
    return User(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      bio: bio ?? this.bio,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      address: address ?? this.address,
      age: age ?? this.age,
      gender: gender ?? this.gender,
    );
  }

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
      avatarUrl: json['avatarUrl'],
      bio: json['bio'],
      phoneNumber: json['phone_number'],
      address: json['address'],
      age: json['age'],
      gender: json['gender'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'avatarUrl': avatarUrl,
      'bio': bio,
      'phone_number': phoneNumber,
      'address': address,
      'age': age,
      'gender': gender,
    };
  }
} 