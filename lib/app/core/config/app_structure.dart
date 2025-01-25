class AppStructure {
  static const Map<String, dynamic> pageStructure = {
    'home': {
      'path': '/home',
      'children': {
        'chat': '/chat/:id',
        'settings': '/chat/settings'
      }
    },
    'suoke': {
      'path': '/suoke',
      'children': {
        'service': '/service/:id',
        'health': '/health',
        'agri': '/agri'
      }
    },
    'explore': {
      'path': '/explore',
      'children': {
        'knowledge': '/knowledge',
        'graph': '/knowledge-graph'
      }
    },
    'life': {
      'path': '/life',
      'children': {
        'record': '/record',
        'health': '/health-advice',
        'analysis': '/analysis'
      }
    },
    'profile': {
      'path': '/profile',
      'children': {
        'settings': '/settings',
        'devices': '/devices',
        'admin': '/admin'
      }
    }
  };
} 