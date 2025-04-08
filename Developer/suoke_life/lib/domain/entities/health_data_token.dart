import 'package:equatable/equatable.dart';

class HealthDataToken extends Equatable {
  final String address;
  final String symbol;
  final String name;
  final BigInt totalSupply;
  final BigInt balance;

  const HealthDataToken({
    required this.address,
    required this.symbol,
    required this.name,
    required this.totalSupply,
    required this.balance,
  });

  @override
  List<Object?> get props => [address, symbol, name, totalSupply, balance];

  HealthDataToken copyWith({
    String? address,
    String? symbol,
    String? name,
    BigInt? totalSupply,
    BigInt? balance,
  }) {
    return HealthDataToken(
      address: address ?? this.address,
      symbol: symbol ?? this.symbol,
      name: name ?? this.name,
      totalSupply: totalSupply ?? this.totalSupply,
      balance: balance ?? this.balance,
    );
  }
} 