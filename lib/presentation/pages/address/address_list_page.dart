import 'package:flutter/material.dart';
import '../../../services/address_service.dart';
import '../../../core/di/service_locator.dart';
import 'address_edit_page.dart';

class AddressListPage extends StatefulWidget {
  final bool selectable;

  const AddressListPage({
    super.key,
    this.selectable = false,
  });

  @override
  State<AddressListPage> createState() => _AddressListPageState();
}

class _AddressListPageState extends State<AddressListPage> {
  final _addressService = serviceLocator<AddressService>();

  @override
  void initState() {
    super.initState();
    _addressService.init();
  }

  Future<void> _addAddress() async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => const AddressEditPage(),
      ),
    );

    if (result == true) {
      setState(() {});
    }
  }

  Future<void> _editAddress(Address address) async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) => AddressEditPage(address: address),
      ),
    );

    if (result == true) {
      setState(() {});
    }
  }

  Future<void> _deleteAddress(Address address) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('删除地址'),
        content: const Text('确定要删除这个地址吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text(
              '删除',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await _addressService.deleteAddress(address.id);
      setState(() {});
    }
  }

  Future<void> _setDefaultAddress(Address address) async {
    await _addressService.setDefaultAddress(address.id);
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('收货地址'),
        centerTitle: true,
      ),
      body: ListenableBuilder(
        listenable: _addressService,
        builder: (context, child) {
          final addresses = _addressService.addresses;
          if (addresses.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.location_off,
                    size: 64,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '暂无收货地址',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 24),
                  FilledButton.icon(
                    onPressed: _addAddress,
                    icon: const Icon(Icons.add),
                    label: const Text('新增地址'),
                  ),
                ],
              ),
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: addresses.length,
            separatorBuilder: (context, index) => const SizedBox(height: 16),
            itemBuilder: (context, index) {
              final address = addresses[index];
              return AddressCard(
                address: address,
                selectable: widget.selectable,
                onEdit: () => _editAddress(address),
                onDelete: () => _deleteAddress(address),
                onSetDefault: () => _setDefaultAddress(address),
                onSelect: widget.selectable
                    ? () => Navigator.pop(context, address)
                    : null,
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _addAddress,
        child: const Icon(Icons.add),
      ),
    );
  }
}

class AddressCard extends StatelessWidget {
  final Address address;
  final bool selectable;
  final VoidCallback onEdit;
  final VoidCallback onDelete;
  final VoidCallback onSetDefault;
  final VoidCallback? onSelect;

  const AddressCard({
    super.key,
    required this.address,
    this.selectable = false,
    required this.onEdit,
    required this.onDelete,
    required this.onSetDefault,
    this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onSelect,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    address.name,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Text(address.phone),
                  if (address.tag != null) ...[
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: Theme.of(context).primaryColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        address.tag!,
                        style: TextStyle(
                          fontSize: 12,
                          color: Theme.of(context).primaryColor,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 8),
              Text(
                address.fullAddress,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  if (address.isDefault)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text(
                        '默认地址',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.red,
                        ),
                      ),
                    )
                  else
                    TextButton(
                      onPressed: onSetDefault,
                      child: const Text('设为默认'),
                    ),
                  const Spacer(),
                  TextButton.icon(
                    onPressed: onEdit,
                    icon: const Icon(Icons.edit, size: 18),
                    label: const Text('编辑'),
                  ),
                  TextButton.icon(
                    onPressed: onDelete,
                    icon: const Icon(Icons.delete, size: 18),
                    label: const Text('删除'),
                    style: TextButton.styleFrom(
                      foregroundColor: Colors.red,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
} 