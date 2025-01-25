class PluginManager {
  static final instance = PluginManager._();
  PluginManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  final _plugins = <String, Plugin>{};
  final _extensions = <String, List<Extension>>{};
  final _hooks = <String, List<Hook>>{};
  
  bool _isInitialized = false;

  Future<void> initialize() async {
    if (_isInitialized) return;

    // 加载插件配置
    await _loadPluginConfigs();
    
    // 初始化已安装的插件
    await _initializePlugins();
    
    _isInitialized = true;
  }

  Future<void> _loadPluginConfigs() async {
    final configs = await _storage.getObject<Map<String, dynamic>>(
      'plugin_configs',
      (json) => json,
    );

    if (configs != null) {
      for (final entry in configs.entries) {
        final plugin = Plugin.fromJson(entry.value);
        if (plugin.enabled) {
          _plugins[plugin.id] = plugin;
        }
      }
    }
  }

  Future<void> _initializePlugins() async {
    for (final plugin in _plugins.values) {
      await _initializePlugin(plugin);
    }
  }

  Future<void> _initializePlugin(Plugin plugin) async {
    try {
      // 注册扩展点
      for (final extension in plugin.extensions) {
        registerExtension(extension);
      }

      // 注册钩子
      for (final hook in plugin.hooks) {
        registerHook(hook);
      }

      // 初始化插件
      await plugin.initialize();
      
      _eventBus.fire(PluginInitializedEvent(plugin));
    } catch (e) {
      LoggerManager.instance.error('Failed to initialize plugin: ${plugin.id}', e);
      _eventBus.fire(PluginFailedEvent(plugin, e));
    }
  }

  void registerExtension(Extension extension) {
    _extensions.putIfAbsent(extension.point, () => []).add(extension);
  }

  void registerHook(Hook hook) {
    _hooks.putIfAbsent(hook.type, () => []).add(hook);
  }

  List<Extension> getExtensions(String point) {
    return List.unmodifiable(_extensions[point] ?? []);
  }

  Future<void> executeHooks(String type, dynamic context) async {
    final hooks = _hooks[type] ?? [];
    for (final hook in hooks) {
      try {
        await hook.execute(context);
      } catch (e) {
        LoggerManager.instance.error('Hook execution failed: ${hook.id}', e);
      }
    }
  }

  Future<void> installPlugin(String id, String source) async {
    // 下载插件
    final pluginPath = await _downloadPlugin(source);
    
    // 验证插件
    final manifest = await _validatePlugin(pluginPath);
    
    // 创建插件实例
    final plugin = Plugin.fromManifest(manifest);
    
    // 安装插件
    await _installPluginFiles(plugin, pluginPath);
    
    // 初始化插件
    await _initializePlugin(plugin);
    
    // 保存插件配置
    _plugins[plugin.id] = plugin;
    await _savePluginConfigs();
    
    _eventBus.fire(PluginInstalledEvent(plugin));
  }

  Future<void> uninstallPlugin(String id) async {
    final plugin = _plugins.remove(id);
    if (plugin == null) return;

    // 清理扩展点
    for (final extension in plugin.extensions) {
      _extensions[extension.point]?.removeWhere((e) => e.pluginId == id);
    }

    // 清理钩子
    for (final hook in plugin.hooks) {
      _hooks[hook.type]?.removeWhere((h) => h.pluginId == id);
    }

    // 清理插件文件
    await _cleanupPluginFiles(plugin);
    
    // 保存配置
    await _savePluginConfigs();
    
    _eventBus.fire(PluginUninstalledEvent(plugin));
  }

  Future<void> enablePlugin(String id) async {
    final plugin = _plugins[id];
    if (plugin == null || plugin.enabled) return;

    plugin.enabled = true;
    await _initializePlugin(plugin);
    await _savePluginConfigs();
    
    _eventBus.fire(PluginEnabledEvent(plugin));
  }

  Future<void> disablePlugin(String id) async {
    final plugin = _plugins[id];
    if (plugin == null || !plugin.enabled) return;

    plugin.enabled = false;
    
    // 清理扩展点和钩子
    for (final extension in plugin.extensions) {
      _extensions[extension.point]?.removeWhere((e) => e.pluginId == id);
    }
    for (final hook in plugin.hooks) {
      _hooks[hook.type]?.removeWhere((h) => h.pluginId == id);
    }

    await _savePluginConfigs();
    _eventBus.fire(PluginDisabledEvent(plugin));
  }

  Future<void> _savePluginConfigs() async {
    final configs = <String, dynamic>{};
    for (final entry in _plugins.entries) {
      configs[entry.key] = entry.value.toJson();
    }
    await _storage.setObject('plugin_configs', configs);
  }
}

class Plugin {
  final String id;
  final String name;
  final String version;
  final List<Extension> extensions;
  final List<Hook> hooks;
  bool enabled;

  Plugin({
    required this.id,
    required this.name,
    required this.version,
    this.extensions = const [],
    this.hooks = const [],
    this.enabled = true,
  });

  Future<void> initialize() async {
    // 插件初始化逻辑
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'version': version,
    'enabled': enabled,
    'extensions': extensions.map((e) => e.toJson()).toList(),
    'hooks': hooks.map((h) => h.toJson()).toList(),
  };

  factory Plugin.fromJson(Map<String, dynamic> json) => Plugin(
    id: json['id'],
    name: json['name'],
    version: json['version'],
    enabled: json['enabled'],
    extensions: (json['extensions'] as List)
        .map((e) => Extension.fromJson(e))
        .toList(),
    hooks: (json['hooks'] as List)
        .map((h) => Hook.fromJson(h))
        .toList(),
  );
}

class Extension {
  final String id;
  final String pluginId;
  final String point;
  final Map<String, dynamic> data;

  Extension({
    required this.id,
    required this.pluginId,
    required this.point,
    this.data = const {},
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'pluginId': pluginId,
    'point': point,
    'data': data,
  };

  factory Extension.fromJson(Map<String, dynamic> json) => Extension(
    id: json['id'],
    pluginId: json['pluginId'],
    point: json['point'],
    data: Map<String, dynamic>.from(json['data']),
  );
}

class Hook {
  final String id;
  final String pluginId;
  final String type;
  final Function(dynamic) execute;

  Hook({
    required this.id,
    required this.pluginId,
    required this.type,
    required this.execute,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'pluginId': pluginId,
    'type': type,
  };

  factory Hook.fromJson(Map<String, dynamic> json) => Hook(
    id: json['id'],
    pluginId: json['pluginId'],
    type: json['type'],
    execute: (context) async {}, // 需要实际的执行逻辑
  );
}

// 插件相关事件
class PluginEvent extends AppEvent {
  final Plugin plugin;
  PluginEvent(this.plugin);
}

class PluginInitializedEvent extends PluginEvent {
  PluginInitializedEvent(super.plugin);
}

class PluginFailedEvent extends PluginEvent {
  final dynamic error;
  PluginFailedEvent(super.plugin, this.error);
}

class PluginInstalledEvent extends PluginEvent {
  PluginInstalledEvent(super.plugin);
}

class PluginUninstalledEvent extends PluginEvent {
  PluginUninstalledEvent(super.plugin);
}

class PluginEnabledEvent extends PluginEvent {
  PluginEnabledEvent(super.plugin);
}

class PluginDisabledEvent extends PluginEvent {
  PluginDisabledEvent(super.plugin);
} 