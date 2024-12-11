import 'package:flutter/material.dart';

class CartPage extends StatefulWidget {
  const CartPage({super.key});

  @override
  State<CartPage> createState() => _CartPageState();
}

class _CartPageState extends State<CartPage> {
  final List<CartItem> _cartItems = [
    CartItem(
      id: '1',
      name: '有机养生茶',
      specification: '500g/盒',
      price: 128.00,
      quantity: 1,
      imageUrl: 'assets/images/product1.jpg',
    ),
    CartItem(
      id: '2',
      name: '助眠香薰精油',
      specification: '30ml/瓶',
      price: 168.00,
      quantity: 1,
      imageUrl: 'assets/images/product2.jpg',
    ),
  ];

  Set<String> _selectedItems = {};
  bool _isAllSelected = false;

  double get _totalPrice {
    return _cartItems
        .where((item) => _selectedItems.contains(item.id))
        .fold(0, (sum, item) => sum + item.price * item.quantity);
  }

  void _updateAllSelected() {
    setState(() {
      _isAllSelected = _cartItems.length == _selectedItems.length;
    });
  }

  void _toggleSelectAll() {
    setState(() {
      if (_isAllSelected) {
        _selectedItems.clear();
      } else {
        _selectedItems = _cartItems.map((item) => item.id).toSet();
      }
      _isAllSelected = !_isAllSelected;
    });
  }

  void _updateItemQuantity(CartItem item, int newQuantity) {
    if (newQuantity < 1) return;
    setState(() {
      final index = _cartItems.indexOf(item);
      _cartItems[index] = item.copyWith(quantity: newQuantity);
    });
  }

  void _removeItem(CartItem item) {
    setState(() {
      _cartItems.remove(item);
      _selectedItems.remove(item.id);
      _updateAllSelected();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('购物车'),
        centerTitle: true,
      ),
      body: _cartItems.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.shopping_cart_outlined,
                    size: 64,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '购物车是空的',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: () {
                      Navigator.pop(context);
                    },
                    child: const Text('去逛逛'),
                  ),
                ],
              ),
            )
          : Stack(
              children: [
                ListView.separated(
                  padding: const EdgeInsets.only(bottom: 80),
                  itemCount: _cartItems.length,
                  separatorBuilder: (context, index) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final item = _cartItems[index];
                    return Dismissible(
                      key: Key(item.id),
                      direction: DismissDirection.endToStart,
                      background: Container(
                        alignment: Alignment.centerRight,
                        padding: const EdgeInsets.only(right: 16),
                        color: Colors.red,
                        child: const Icon(
                          Icons.delete,
                          color: Colors.white,
                        ),
                      ),
                      onDismissed: (direction) {
                        _removeItem(item);
                      },
                      child: CartItemTile(
                        item: item,
                        isSelected: _selectedItems.contains(item.id),
                        onToggleSelect: (selected) {
                          setState(() {
                            if (selected) {
                              _selectedItems.add(item.id);
                            } else {
                              _selectedItems.remove(item.id);
                            }
                            _updateAllSelected();
                          });
                        },
                        onUpdateQuantity: (quantity) {
                          _updateItemQuantity(item, quantity);
                        },
                        onRemove: () {
                          _removeItem(item);
                        },
                      ),
                    );
                  },
                ),
                Positioned(
                  left: 0,
                  right: 0,
                  bottom: 0,
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 8,
                          offset: const Offset(0, -2),
                        ),
                      ],
                    ),
                    child: SafeArea(
                      child: Row(
                        children: [
                          Row(
                            children: [
                              Checkbox(
                                value: _isAllSelected,
                                onChanged: (value) {
                                  _toggleSelectAll();
                                },
                              ),
                              const Text('全选'),
                            ],
                          ),
                          const Spacer(),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                '合计: ¥${_totalPrice.toStringAsFixed(2)}',
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.red,
                                ),
                              ),
                              Text(
                                '已选${_selectedItems.length}件商品',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(width: 16),
                          FilledButton(
                            onPressed: _selectedItems.isEmpty
                                ? null
                                : () {
                                    // TODO: 实现结算功能
                                  },
                            child: const Text('结算'),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
    );
  }
}

class CartItem {
  final String id;
  final String name;
  final String specification;
  final double price;
  final int quantity;
  final String imageUrl;

  const CartItem({
    required this.id,
    required this.name,
    required this.specification,
    required this.price,
    required this.quantity,
    required this.imageUrl,
  });

  CartItem copyWith({
    String? id,
    String? name,
    String? specification,
    double? price,
    int? quantity,
    String? imageUrl,
  }) {
    return CartItem(
      id: id ?? this.id,
      name: name ?? this.name,
      specification: specification ?? this.specification,
      price: price ?? this.price,
      quantity: quantity ?? this.quantity,
      imageUrl: imageUrl ?? this.imageUrl,
    );
  }
}

class CartItemTile extends StatelessWidget {
  final CartItem item;
  final bool isSelected;
  final ValueChanged<bool> onToggleSelect;
  final ValueChanged<int> onUpdateQuantity;
  final VoidCallback onRemove;

  const CartItemTile({
    super.key,
    required this.item,
    required this.isSelected,
    required this.onToggleSelect,
    required this.onUpdateQuantity,
    required this.onRemove,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Checkbox(
            value: isSelected,
            onChanged: (value) {
              onToggleSelect(value ?? false);
            },
          ),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.asset(
              item.imageUrl,
              width: 80,
              height: 80,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return Container(
                  width: 80,
                  height: 80,
                  color: Colors.grey[200],
                  child: const Icon(
                    Icons.image,
                    color: Colors.grey,
                  ),
                );
              },
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.name,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  item.specification,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Text(
                      '¥${item.price.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.red,
                      ),
                    ),
                    const Spacer(),
                    IconButton.filled(
                      icon: const Icon(Icons.remove, size: 18),
                      onPressed: item.quantity > 1
                          ? () {
                              onUpdateQuantity(item.quantity - 1);
                            }
                          : null,
                      style: IconButton.styleFrom(
                        minimumSize: const Size(32, 32),
                        padding: EdgeInsets.zero,
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                      child: Text(
                        item.quantity.toString(),
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    IconButton.filled(
                      icon: const Icon(Icons.add, size: 18),
                      onPressed: () {
                        onUpdateQuantity(item.quantity + 1);
                      },
                      style: IconButton.styleFrom(
                        minimumSize: const Size(32, 32),
                        padding: EdgeInsets.zero,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
} 