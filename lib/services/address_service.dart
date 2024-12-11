import 'package:flutter/foundation.dart';
import '../core/di/service_locator.dart';
import '../core/storage/services/file_storage_service.dart';

class AddressService extends GetxController {
  final FileStorageService _storage = serviceLocator<FileStorageService>();
  List<Address> _addresses = [];

  List<Address> get addresses => List.unmodifiable(_addresses);
  Address? get defaultAddress => _addresses.firstWhere(
        (addr) => addr.isDefault,
        orElse: () => _addresses.isEmpty ? null : _addresses.first,
      );

  Future<void> init() async {
    try {
      final addressData = await _storage.read('address_data');
      if (addressData != null) {
        final List<dynamic> items = addressData;
        _addresses = items.map((item) => Address.fromJson(item)).toList();
        update();
      }
    } catch (e) {
      debugPrint('Failed to load address data: $e');
    }
  }

  Future<void> addAddress(Address address) async {
    if (address.isDefault) {
      // 如果新地址是默认地址，取消其他地址的默认状态
      _addresses = _addresses.map((addr) => addr.copyWith(isDefault: false)).toList();
    } else if (_addresses.isEmpty) {
      // 如果是第一个地址，自动设为默认
      _addresses.add(address.copyWith(isDefault: true));
      await _saveAddresses();
      update();
      return;
    }
    _addresses.add(address);
    await _saveAddresses();
    update();
  }

  Future<void> updateAddress(Address address) async {
    final index = _addresses.indexWhere((addr) => addr.id == address.id);
    if (index != -1) {
      if (address.isDefault) {
        // 如果更新的地址设为默认，取消其他地址的默认状态
        _addresses = _addresses.map((addr) => 
          addr.id == address.id ? address : addr.copyWith(isDefault: false)
        ).toList();
      } else {
        _addresses[index] = address;
      }
      await _saveAddresses();
      update();
    }
  }

  Future<void> deleteAddress(String id) async {
    final wasDefault = _addresses.firstWhere((addr) => addr.id == id).isDefault;
    _addresses.removeWhere((addr) => addr.id == id);
    
    if (wasDefault && _addresses.isNotEmpty) {
      // 如果删除的是默认地址，将第一个地址设为默认
      _addresses[0] = _addresses[0].copyWith(isDefault: true);
    }
    
    await _saveAddresses();
    update();
  }

  Future<void> setDefaultAddress(String id) async {
    _addresses = _addresses.map((addr) => 
      addr.copyWith(isDefault: addr.id == id)
    ).toList();
    await _saveAddresses();
    update();
  }

  Future<void> _saveAddresses() async {
    try {
      await _storage.write(
        'address_data',
        _addresses.map((addr) => addr.toJson()).toList(),
      );
    } catch (e) {
      debugPrint('Failed to save address data: $e');
    }
  }
}

class Address {
  final String id;
  final String name;
  final String phone;
  final String province;
  final String city;
  final String district;
  final String street;
  final String detail;
  final bool isDefault;
  final String? tag; // 家、公司等标签

  const Address({
    required this.id,
    required this.name,
    required this.phone,
    required this.province,
    required this.city,
    required this.district,
    required this.street,
    required this.detail,
    this.isDefault = false,
    this.tag,
  });

  String get fullAddress => '$province$city$district$street$detail';

  Address copyWith({
    String? id,
    String? name,
    String? phone,
    String? province,
    String? city,
    String? district,
    String? street,
    String? detail,
    bool? isDefault,
    String? tag,
  }) {
    return Address(
      id: id ?? this.id,
      name: name ?? this.name,
      phone: phone ?? this.phone,
      province: province ?? this.province,
      city: city ?? this.city,
      district: district ?? this.district,
      street: street ?? this.street,
      detail: detail ?? this.detail,
      isDefault: isDefault ?? this.isDefault,
      tag: tag ?? this.tag,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'phone': phone,
      'province': province,
      'city': city,
      'district': district,
      'street': street,
      'detail': detail,
      'isDefault': isDefault,
      'tag': tag,
    };
  }

  factory Address.fromJson(Map<String, dynamic> json) {
    return Address(
      id: json['id'] as String,
      name: json['name'] as String,
      phone: json['phone'] as String,
      province: json['province'] as String,
      city: json['city'] as String,
      district: json['district'] as String,
      street: json['street'] as String,
      detail: json['detail'] as String,
      isDefault: json['isDefault'] as bool,
      tag: json['tag'] as String?,
    );
  }
} 