import { VisualizationManager } from './VisualizationManager';
import { VRManager } from './VRManager';
import { ARManager } from './ARManager';

export type {
  Node3D,
  Edge3D,
  Vector3,
  LayoutConfig,
  InteractionConfig,
  StyleConfig
} from './VisualizationManager';

export type {
  VRConfig,
  VRInteraction
} from './VRManager';

export type {
  ARConfig,
  ARMarker,
  ARAnchor
} from './ARManager';

// 导出主要类
export {
  VisualizationManager,
  VRManager,
  ARManager
};

// 导出工厂函数
export const getVisualizationManager = () => VisualizationManager.getInstance();
export const getVRManager = () => VRManager.getInstance();
export const getARManager = () => ARManager.getInstance();

// 导出初始化函数
export const initializeVisualization = async (config?: {
  layout?: Partial<LayoutConfig>;
  vr?: Partial<VRConfig>;
  ar?: Partial<ARConfig>;
}) => {
  const visualManager = getVisualizationManager();
  const vrManager = getVRManager();
  const arManager = getARManager();

  if (config?.layout) {
    visualManager.updateConfig({ layout: config.layout });
  }
  if (config?.vr) {
    vrManager.updateConfig(config.vr);
  }
  if (config?.ar) {
    arManager.updateConfig(config.ar);
  }

  return {
    visualManager,
    vrManager,
    arManager
  };
};

// 导出实用函数
export const visualizationUtils = {
  /**
   * 创建3D场景
   */
  createScene: async (container: HTMLElement, config: {
    mode: '3d' | 'vr' | 'ar';
    nodes: Node3D[];
    edges: Edge3D[];
  }) => {
    const { mode, nodes, edges } = config;
    const visualManager = getVisualizationManager();

    switch (mode) {
      case 'vr':
        const vrManager = getVRManager();
        await vrManager.initializeVRSession();
        break;
      case 'ar':
        const arManager = getARManager();
        await arManager.initializeARSession();
        break;
    }

    // 添加节点和边到可视化
    nodes.forEach(node => visualManager.addNode(node));
    edges.forEach(edge => visualManager.addEdge(edge));

    return visualManager.getVisualizationData();
  },

  /**
   * 更新场景
   */
  updateScene: (updates: {
    nodes?: Node3D[];
    edges?: Edge3D[];
    config?: {
      layout?: Partial<LayoutConfig>;
      vr?: Partial<VRConfig>;
      ar?: Partial<ARConfig>;
    };
  }) => {
    const visualManager = getVisualizationManager();
    const vrManager = getVRManager();
    const arManager = getARManager();

    if (updates.nodes) {
      updates.nodes.forEach(node => visualManager.addNode(node));
    }
    if (updates.edges) {
      updates.edges.forEach(edge => visualManager.addEdge(edge));
    }
    if (updates.config) {
      if (updates.config.layout) {
        visualManager.updateConfig({ layout: updates.config.layout });
      }
      if (updates.config.vr) {
        vrManager.updateConfig(updates.config.vr);
      }
      if (updates.config.ar) {
        arManager.updateConfig(updates.config.ar);
      }
    }
  }
};

// 导出常用配置
export const visualizationConfigs = {
  // 默认3D配置
  default3DConfig: {
    layout: {
      type: '3d',
      algorithm: 'force-directed',
      dimensions: {
        width: 1000,
        height: 1000,
        depth: 1000
      }
    }
  },

  // 默认VR配置
  defaultVRConfig: {
    mode: 'immersive-vr',
    controllerType: 'controller',
    environment: {
      skybox: 'space',
      ground: 'grid'
    }
  },

  // 默认AR配置
  defaultARConfig: {
    mode: 'markerless',
    tracking: {
      type: 'plane',
      minConfidence: 0.7
    }
  }
};