import 'dart:async';
import 'package:flutter/foundation.dart';
import '../core/di/service_locator.dart';
import '../core/storage/services/file_storage_service.dart';

class CartService extends GetxController {
  final FileStorageService _storage = serviceLocator<FileStorageService>();
  final List<CartItem> _items = [];
  final _cartController = StreamController<List<CartItem>>.broadcast();

  Stream<List<CartItem>> get cartStream => _cartController.stream;
  List<CartItem> get items => List.unmodifiable(_items);
  
  int get itemCount => _items.length;
  
  double get totalPrice => _items.fold(
        0,
        (sum, item) => sum + item.price * item.quantity,
      );

  Future<void> init() async {
    try {
      final cartData = await _storage.read('cart_data');
      if (cartData != null) {
        final List<dynamic> items = cartData;
        _items.addAll(
          items.map((item) => CartItem.fromJson(item)).toList(),
        );
        _update();
      }
    } catch (e) {
      debugPrint('Failed to load cart data: $e');
    }
  }

  Future<void> addItem(CartItem item) async {
    final existingIndex = _items.indexWhere((i) => 
      i.id == item.id && i.specification == item.specification);
    
    if (existingIndex != -1) {
      _items[existingIndex] = _items[existingIndex].copyWith(
        quantity: _items[existingIndex].quantity + item.quantity,
      );
    } else {
      _items.add(item);
    }
    
    await _saveCart();
    _update();
  }

  Future<void> updateItemQuantity(String itemId, int quantity) async {
    final index = _items.indexWhere((item) => item.id == itemId);
    if (index != -1) {
      _items[index] = _items[index].copyWith(quantity: quantity);
      await _saveCart();
      _update();
    }
  }

  Future<void> removeItem(String itemId) async {
    _items.removeWhere((item) => item.id == itemId);
    await _saveCart();
    _update();
  }

  Future<void> clearCart() async {
    _items.clear();
    await _saveCart();
    _update();
  }

  Future<void> _saveCart() async {
    try {
      await _storage.write(
        'cart_data',
        _items.map((item) => item.toJson()).toList(),
      );
    } catch (e) {
      debugPrint('Failed to save cart data: $e');
    }
  }

  void _update() {
    update();
    _cartController.add(_items);
  }

  @override
  void dispose() {
    _cartController.close();
    super.dispose();
  }
}

class CartItem {
  final String id;
  final String name;
  final String specification;
  final double price;
  final int quantity;
  final String imageUrl;
  final String? description;

  const CartItem({
    required this.id,
    required this.name,
    required this.specification,
    required this.price,
    required this.quantity,
    required this.imageUrl,
    this.description,
  });

  CartItem copyWith({
    String? id,
    String? name,
    String? specification,
    double? price,
    int? quantity,
    String? imageUrl,
    String? description,
  }) {
    return CartItem(
      id: id ?? this.id,
      name: name ?? this.name,
      specification: specification ?? this.specification,
      price: price ?? this.price,
      quantity: quantity ?? this.quantity,
      imageUrl: imageUrl ?? this.imageUrl,
      description: description ?? this.description,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'specification': specification,
      'price': price,
      'quantity': quantity,
      'imageUrl': imageUrl,
      'description': description,
    };
  }

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      id: json['id'] as String,
      name: json['name'] as String,
      specification: json['specification'] as String,
      price: json['price'] as double,
      quantity: json['quantity'] as int,
      imageUrl: json['imageUrl'] as String,
      description: json['description'] as String?,
    );
  }
} 