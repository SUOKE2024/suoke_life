class Expert {
  final String id;
  final String name;
  final String? avatar;
  final String specialty;
  final String description;
  final String? title;
  final String? organization;
  final List<String>? certificates;
  final String? status;
  final DateTime createdAt;

  Expert({
    required this.id,
    required this.name,
    this.avatar,
    required this.specialty,
    required this.description,
    this.title,
    this.organization,
    this.certificates,
    this.status,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory Expert.fromMap(Map<String, dynamic> map) {
    return Expert(
      id: map['id'] as String,
      name: map['name'] as String,
      avatar: map['avatar'] as String?,
      specialty: map['specialty'] as String,
      description: map['description'] as String,
      title: map['title'] as String?,
      organization: map['organization'] as String?,
      certificates: map['certificates'] != null 
          ? List<String>.from(map['certificates'] as List)
          : null,
      status: map['status'] as String?,
      createdAt: DateTime.fromMillisecondsSinceEpoch(map['created_at'] as int),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'avatar': avatar,
      'specialty': specialty,
      'description': description,
      'title': title,
      'organization': organization,
      'certificates': certificates,
      'status': status,
      'created_at': createdAt.millisecondsSinceEpoch,
    };
  }
} 