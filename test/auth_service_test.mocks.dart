// Mocks generated by Mockito 5.4.5 from annotations
// in suoke_life/test/auth_service_test.dart.
// Do not manually edit this file.

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'dart:async' as _i4;

import 'package:core/core.dart' as _i5;
import 'package:core/network/network_service.dart' as _i3;
import 'package:dio/dio.dart' as _i2;
import 'package:mockito/mockito.dart' as _i1;

// ignore_for_file: type=lint
// ignore_for_file: avoid_redundant_argument_values
// ignore_for_file: avoid_setters_without_getters
// ignore_for_file: comment_references
// ignore_for_file: deprecated_member_use
// ignore_for_file: deprecated_member_use_from_same_package
// ignore_for_file: implementation_imports
// ignore_for_file: invalid_use_of_visible_for_testing_member
// ignore_for_file: must_be_immutable
// ignore_for_file: prefer_const_constructors
// ignore_for_file: unnecessary_parenthesis
// ignore_for_file: camel_case_types
// ignore_for_file: subtype_of_sealed_class

class _FakeResponse_0<T> extends _i1.SmartFake implements _i2.Response<T> {
  _FakeResponse_0(
    Object parent,
    Invocation parentInvocation,
  ) : super(
          parent,
          parentInvocation,
        );
}

/// A class which mocks [NetworkService].
///
/// See the documentation for Mockito's code generation for more information.
class MockNetworkService extends _i1.Mock implements _i3.NetworkService {
  @override
  _i4.Future<_i2.Response<dynamic>> get(
    String? url, {
    Map<String, dynamic>? queryParameters,
    _i2.Options? options,
  }) =>
      (super.noSuchMethod(
        Invocation.method(
          #get,
          [url],
          {
            #queryParameters: queryParameters,
            #options: options,
          },
        ),
        returnValue:
            _i4.Future<_i2.Response<dynamic>>.value(_FakeResponse_0<dynamic>(
          this,
          Invocation.method(
            #get,
            [url],
            {
              #queryParameters: queryParameters,
              #options: options,
            },
          ),
        )),
        returnValueForMissingStub:
            _i4.Future<_i2.Response<dynamic>>.value(_FakeResponse_0<dynamic>(
          this,
          Invocation.method(
            #get,
            [url],
            {
              #queryParameters: queryParameters,
              #options: options,
            },
          ),
        )),
      ) as _i4.Future<_i2.Response<dynamic>>);

  @override
  _i4.Future<_i2.Response<dynamic>> post(
    String? url, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    _i2.Options? options,
  }) =>
      (super.noSuchMethod(
        Invocation.method(
          #post,
          [url],
          {
            #data: data,
            #queryParameters: queryParameters,
            #options: options,
          },
        ),
        returnValue:
            _i4.Future<_i2.Response<dynamic>>.value(_FakeResponse_0<dynamic>(
          this,
          Invocation.method(
            #post,
            [url],
            {
              #data: data,
              #queryParameters: queryParameters,
              #options: options,
            },
          ),
        )),
        returnValueForMissingStub:
            _i4.Future<_i2.Response<dynamic>>.value(_FakeResponse_0<dynamic>(
          this,
          Invocation.method(
            #post,
            [url],
            {
              #data: data,
              #queryParameters: queryParameters,
              #options: options,
            },
          ),
        )),
      ) as _i4.Future<_i2.Response<dynamic>>);

  @override
  _i4.Future<_i2.Response<dynamic>> put(
    String? url, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    _i2.Options? options,
  }) =>
      (super.noSuchMethod(
        Invocation.method(
          #put,
          [url],
          {
            #data: data,
            #queryParameters: queryParameters,
            #options: options,
          },
        ),
        returnValue:
            _i4.Future<_i2.Response<dynamic>>.value(_FakeResponse_0<dynamic>(
          this,
          Invocation.method(
            #put,
            [url],
            {
              #data: data,
              #queryParameters: queryParameters,
              #options: options,
            },
          ),
        )),
        returnValueForMissingStub:
            _i4.Future<_i2.Response<dynamic>>.value(_FakeResponse_0<dynamic>(
          this,
          Invocation.method(
            #put,
            [url],
            {
              #data: data,
              #queryParameters: queryParameters,
              #options: options,
            },
          ),
        )),
      ) as _i4.Future<_i2.Response<dynamic>>);

  @override
  _i4.Future<_i2.Response<dynamic>> delete(
    String? url, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    _i2.Options? options,
  }) =>
      (super.noSuchMethod(
        Invocation.method(
          #delete,
          [url],
          {
            #data: data,
            #queryParameters: queryParameters,
            #options: options,
          },
        ),
        returnValue:
            _i4.Future<_i2.Response<dynamic>>.value(_FakeResponse_0<dynamic>(
          this,
          Invocation.method(
            #delete,
            [url],
            {
              #data: data,
              #queryParameters: queryParameters,
              #options: options,
            },
          ),
        )),
        returnValueForMissingStub:
            _i4.Future<_i2.Response<dynamic>>.value(_FakeResponse_0<dynamic>(
          this,
          Invocation.method(
            #delete,
            [url],
            {
              #data: data,
              #queryParameters: queryParameters,
              #options: options,
            },
          ),
        )),
      ) as _i4.Future<_i2.Response<dynamic>>);
}

/// A class which mocks [LocalStorageService].
///
/// See the documentation for Mockito's code generation for more information.
class MockLocalStorageService extends _i1.Mock
    implements _i5.LocalStorageService {
  @override
  _i4.Future<void> init() => (super.noSuchMethod(
        Invocation.method(
          #init,
          [],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<void> save(
    String? table,
    String? key,
    dynamic value,
  ) =>
      (super.noSuchMethod(
        Invocation.method(
          #save,
          [
            table,
            key,
            value,
          ],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<String?> get(String? key) => (super.noSuchMethod(
        Invocation.method(
          #get,
          [key],
        ),
        returnValue: _i4.Future<String?>.value(),
        returnValueForMissingStub: _i4.Future<String?>.value(),
      ) as _i4.Future<String?>);

  @override
  _i4.Future<void> delete(
    String? table, {
    String? where,
    List<dynamic>? whereArgs,
  }) =>
      (super.noSuchMethod(
        Invocation.method(
          #delete,
          [table],
          {
            #where: where,
            #whereArgs: whereArgs,
          },
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<List<Map<String, dynamic>>> query(
    String? table, {
    bool? distinct,
    List<String>? columns,
    String? where,
    List<dynamic>? whereArgs,
    String? groupBy,
    String? having,
    String? orderBy,
    int? limit,
    int? offset,
  }) =>
      (super.noSuchMethod(
        Invocation.method(
          #query,
          [table],
          {
            #distinct: distinct,
            #columns: columns,
            #where: where,
            #whereArgs: whereArgs,
            #groupBy: groupBy,
            #having: having,
            #orderBy: orderBy,
            #limit: limit,
            #offset: offset,
          },
        ),
        returnValue: _i4.Future<List<Map<String, dynamic>>>.value(
            <Map<String, dynamic>>[]),
        returnValueForMissingStub: _i4.Future<List<Map<String, dynamic>>>.value(
            <Map<String, dynamic>>[]),
      ) as _i4.Future<List<Map<String, dynamic>>>);

  @override
  _i4.Future<void> saveData(
    String? key,
    Map<String, dynamic>? data,
  ) =>
      (super.noSuchMethod(
        Invocation.method(
          #saveData,
          [
            key,
            data,
          ],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<Map<String, dynamic>?> getData(String? key) => (super.noSuchMethod(
        Invocation.method(
          #getData,
          [key],
        ),
        returnValue: _i4.Future<Map<String, dynamic>?>.value(),
        returnValueForMissingStub: _i4.Future<Map<String, dynamic>?>.value(),
      ) as _i4.Future<Map<String, dynamic>?>);

  @override
  _i4.Future<void> deleteData(String? key) => (super.noSuchMethod(
        Invocation.method(
          #deleteData,
          [key],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<List<Map<String, dynamic>>> getAll(String? table) =>
      (super.noSuchMethod(
        Invocation.method(
          #getAll,
          [table],
        ),
        returnValue: _i4.Future<List<Map<String, dynamic>>>.value(
            <Map<String, dynamic>>[]),
        returnValueForMissingStub: _i4.Future<List<Map<String, dynamic>>>.value(
            <Map<String, dynamic>>[]),
      ) as _i4.Future<List<Map<String, dynamic>>>);

  @override
  _i4.Future<void> saveList(
    String? key,
    String? itemId,
    Map<String, dynamic>? item,
  ) =>
      (super.noSuchMethod(
        Invocation.method(
          #saveList,
          [
            key,
            itemId,
            item,
          ],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<List<Map<String, dynamic>>> getList(String? key) =>
      (super.noSuchMethod(
        Invocation.method(
          #getList,
          [key],
        ),
        returnValue: _i4.Future<List<Map<String, dynamic>>>.value(
            <Map<String, dynamic>>[]),
        returnValueForMissingStub: _i4.Future<List<Map<String, dynamic>>>.value(
            <Map<String, dynamic>>[]),
      ) as _i4.Future<List<Map<String, dynamic>>>);

  @override
  _i4.Future<void> saveItem(
    String? key,
    dynamic value,
  ) =>
      (super.noSuchMethod(
        Invocation.method(
          #saveItem,
          [
            key,
            value,
          ],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<dynamic> getItem(String? key) => (super.noSuchMethod(
        Invocation.method(
          #getItem,
          [key],
        ),
        returnValue: _i4.Future<dynamic>.value(),
        returnValueForMissingStub: _i4.Future<dynamic>.value(),
      ) as _i4.Future<dynamic>);

  @override
  _i4.Future<void> removeItem(String? key) => (super.noSuchMethod(
        Invocation.method(
          #removeItem,
          [key],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<void> clear() => (super.noSuchMethod(
        Invocation.method(
          #clear,
          [],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<List<dynamic>> getItems(String? key) => (super.noSuchMethod(
        Invocation.method(
          #getItems,
          [key],
        ),
        returnValue: _i4.Future<List<dynamic>>.value(<dynamic>[]),
        returnValueForMissingStub: _i4.Future<List<dynamic>>.value(<dynamic>[]),
      ) as _i4.Future<List<dynamic>>);

  @override
  _i4.Future<void> set(
    String? key,
    String? value,
  ) =>
      (super.noSuchMethod(
        Invocation.method(
          #set,
          [
            key,
            value,
          ],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<void> remove(String? key) => (super.noSuchMethod(
        Invocation.method(
          #remove,
          [key],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<bool> containsKey(String? key) => (super.noSuchMethod(
        Invocation.method(
          #containsKey,
          [key],
        ),
        returnValue: _i4.Future<bool>.value(false),
        returnValueForMissingStub: _i4.Future<bool>.value(false),
      ) as _i4.Future<bool>);

  @override
  _i4.Future<void> setBool(
    String? key,
    bool? value,
  ) =>
      (super.noSuchMethod(
        Invocation.method(
          #setBool,
          [
            key,
            value,
          ],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<bool?> getBool(String? key) => (super.noSuchMethod(
        Invocation.method(
          #getBool,
          [key],
        ),
        returnValue: _i4.Future<bool?>.value(),
        returnValueForMissingStub: _i4.Future<bool?>.value(),
      ) as _i4.Future<bool?>);

  @override
  _i4.Future<void> setInt(
    String? key,
    int? value,
  ) =>
      (super.noSuchMethod(
        Invocation.method(
          #setInt,
          [
            key,
            value,
          ],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<int?> getInt(String? key) => (super.noSuchMethod(
        Invocation.method(
          #getInt,
          [key],
        ),
        returnValue: _i4.Future<int?>.value(),
        returnValueForMissingStub: _i4.Future<int?>.value(),
      ) as _i4.Future<int?>);

  @override
  _i4.Future<void> setDouble(
    String? key,
    double? value,
  ) =>
      (super.noSuchMethod(
        Invocation.method(
          #setDouble,
          [
            key,
            value,
          ],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<double?> getDouble(String? key) => (super.noSuchMethod(
        Invocation.method(
          #getDouble,
          [key],
        ),
        returnValue: _i4.Future<double?>.value(),
        returnValueForMissingStub: _i4.Future<double?>.value(),
      ) as _i4.Future<double?>);

  @override
  _i4.Future<void> setStringList(
    String? key,
    List<String>? value,
  ) =>
      (super.noSuchMethod(
        Invocation.method(
          #setStringList,
          [
            key,
            value,
          ],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<List<String>?> getStringList(String? key) => (super.noSuchMethod(
        Invocation.method(
          #getStringList,
          [key],
        ),
        returnValue: _i4.Future<List<String>?>.value(),
        returnValueForMissingStub: _i4.Future<List<String>?>.value(),
      ) as _i4.Future<List<String>?>);

  @override
  _i4.Future<void> setMap(
    String? key,
    Map<String, dynamic>? value,
  ) =>
      (super.noSuchMethod(
        Invocation.method(
          #setMap,
          [
            key,
            value,
          ],
        ),
        returnValue: _i4.Future<void>.value(),
        returnValueForMissingStub: _i4.Future<void>.value(),
      ) as _i4.Future<void>);

  @override
  _i4.Future<Map<String, dynamic>?> getMap(String? key) => (super.noSuchMethod(
        Invocation.method(
          #getMap,
          [key],
        ),
        returnValue: _i4.Future<Map<String, dynamic>?>.value(),
        returnValueForMissingStub: _i4.Future<Map<String, dynamic>?>.value(),
      ) as _i4.Future<Map<String, dynamic>?>);

  @override
  _i4.Future<List<dynamic>> getAllItems() => (super.noSuchMethod(
        Invocation.method(
          #getAllItems,
          [],
        ),
        returnValue: _i4.Future<List<dynamic>>.value(<dynamic>[]),
        returnValueForMissingStub: _i4.Future<List<dynamic>>.value(<dynamic>[]),
      ) as _i4.Future<List<dynamic>>);
}
