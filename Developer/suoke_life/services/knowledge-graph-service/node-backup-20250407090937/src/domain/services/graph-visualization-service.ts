import { Logger } from '../../infrastructure/logger';
import { Neo4jKnowledgeGraphRepository } from '../../infrastructure/repositories/Neo4jKnowledgeGraphRepository';

/**
 * 知识图谱可视化服务 - 负责准备和转换知识图谱数据用于前端可视化
 */
export class GraphVisualizationService {
  private readonly logger = new Logger('GraphVisualizationService');

  constructor(
    private readonly graphRepository: Neo4jKnowledgeGraphRepository,
  ) {}

  /**
   * 获取图谱可视化数据
   * @param options 可视化选项
   * @returns 格式化的可视化数据
   */
  async getVisualizationData(options: VisualizationOptions): Promise<VisualizationData> {
    try {
      const { centralNode, depth, nodeTypes, relationshipTypes, limit } = options;
      
      // 从中心节点开始，获取子图
      const subgraph = await this.graphRepository.getSubgraph({
        startNodeId: centralNode,
        maxDepth: depth || 2,
        nodeTypes: nodeTypes || [],
        relationshipTypes: relationshipTypes || [],
        limit: limit || 100
      });

      // 转换为可视化格式
      return this.formatForVisualization(subgraph);
    } catch (error) {
      this.logger.error(`获取可视化数据失败: ${error.message}`);
      throw new Error(`获取可视化数据失败: ${error.message}`);
    }
  }

  /**
   * 获取3D图谱可视化数据
   * @param options 可视化选项
   * @returns 格式化的3D可视化数据
   */
  async get3DVisualizationData(options: Visualization3DOptions): Promise<Visualization3DData> {
    try {
      const { centralNode, depth, nodeTypes, relationshipTypes, limit, layout } = options;
      
      // 从中心节点开始，获取子图
      const subgraph = await this.graphRepository.getSubgraph({
        startNodeId: centralNode,
        maxDepth: depth || 3, // 3D视图默认增加深度
        nodeTypes: nodeTypes || [],
        relationshipTypes: relationshipTypes || [],
        limit: limit || 150 // 3D视图可支持更多节点
      });

      // 转换为3D可视化格式
      return this.formatFor3DVisualization(subgraph, layout || '3d-force');
    } catch (error) {
      this.logger.error(`获取3D可视化数据失败: ${error.message}`);
      throw new Error(`获取3D可视化数据失败: ${error.message}`);
    }
  }

  /**
   * 获取AR图谱可视化数据
   * @param options AR可视化选项
   * @returns 格式化的AR可视化数据
   */
  async getARVisualizationData(options: ARVisualizationOptions): Promise<ARVisualizationData> {
    try {
      const { centralNode, depth, nodeTypes, relationshipTypes, limit, arMarkers } = options;
      
      // 从中心节点开始，获取子图
      const subgraph = await this.graphRepository.getSubgraph({
        startNodeId: centralNode,
        maxDepth: depth || 2,
        nodeTypes: nodeTypes || [],
        relationshipTypes: relationshipTypes || [],
        limit: limit || 50 // AR视图需要适当限制节点数以避免视觉混乱
      });

      // 转换为AR可视化格式
      return this.formatForARVisualization(subgraph, arMarkers);
    } catch (error) {
      this.logger.error(`获取AR可视化数据失败: ${error.message}`);
      throw new Error(`获取AR可视化数据失败: ${error.message}`);
    }
  }

  /**
   * 获取VR图谱可视化数据
   * @param options VR可视化选项
   * @returns 格式化的VR可视化数据
   */
  async getVRVisualizationData(options: VRVisualizationOptions): Promise<VRVisualizationData> {
    try {
      const { centralNode, depth, nodeTypes, relationshipTypes, limit, immersiveMode } = options;
      
      // 从中心节点开始，获取子图
      const subgraph = await this.graphRepository.getSubgraph({
        startNodeId: centralNode,
        maxDepth: depth || 4, // VR视图可以支持更深的图谱探索
        nodeTypes: nodeTypes || [],
        relationshipTypes: relationshipTypes || [],
        limit: limit || 200 // VR空间可呈现更多节点
      });

      // 获取节点间的相似度，用于VR中的空间布局
      const nodeIds = subgraph.nodes.map(node => node.id);
      const similarities = await this.graphRepository.getNodeSimilarities(nodeIds);

      // 转换为VR可视化格式
      return this.formatForVRVisualization(subgraph, similarities, immersiveMode || 'full');
    } catch (error) {
      this.logger.error(`获取VR可视化数据失败: ${error.message}`);
      throw new Error(`获取VR可视化数据失败: ${error.message}`);
    }
  }

  /**
   * 获取领域知识的可视化数据
   * @param domain 领域名称
   * @param options 可视化选项
   * @returns 格式化的可视化数据
   */
  async getDomainVisualizationData(domain: string, options: DomainVisualizationOptions = {}): Promise<VisualizationData> {
    try {
      // 获取领域内的节点
      const domainNodes = await this.graphRepository.getDomainNodes(domain, {
        limit: options.limit || 50,
        nodeTypes: options.nodeTypes || []
      });

      if (domainNodes.length === 0) {
        return { nodes: [], links: [] };
      }

      // 获取节点间的关系
      const nodeIds = domainNodes.map(node => node.id);
      const relationships = await this.graphRepository.getRelationshipsBetweenNodes(nodeIds, {
        types: options.relationshipTypes || []
      });

      // 转换为可视化格式
      return this.formatForVisualization({
        nodes: domainNodes,
        relationships
      });
    } catch (error) {
      this.logger.error(`获取领域可视化数据失败: ${error.message}`);
      throw new Error(`获取领域可视化数据失败: ${error.message}`);
    }
  }

  /**
   * 获取领域知识的3D可视化数据
   * @param domain 领域名称
   * @param options 3D可视化选项
   * @returns 格式化的3D可视化数据
   */
  async getDomain3DVisualizationData(domain: string, options: Domain3DVisualizationOptions = {}): Promise<Visualization3DData> {
    try {
      // 获取领域内的节点
      const domainNodes = await this.graphRepository.getDomainNodes(domain, {
        limit: options.limit || 100, // 3D视图可支持更多节点
        nodeTypes: options.nodeTypes || []
      });

      if (domainNodes.length === 0) {
        return { nodes: [], links: [], layout: options.layout || '3d-force' };
      }

      // 获取节点间的关系
      const nodeIds = domainNodes.map(node => node.id);
      const relationships = await this.graphRepository.getRelationshipsBetweenNodes(nodeIds, {
        types: options.relationshipTypes || []
      });

      // 转换为3D可视化格式
      return this.formatFor3DVisualization({
        nodes: domainNodes,
        relationships
      }, options.layout || '3d-force');
    } catch (error) {
      this.logger.error(`获取领域3D可视化数据失败: ${error.message}`);
      throw new Error(`获取领域3D可视化数据失败: ${error.message}`);
    }
  }

  /**
   * 获取健康数据可视化
   * @param userId 用户ID
   * @param options 可视化选项
   * @returns 格式化的可视化数据
   */
  async getUserHealthVisualization(userId: string, options: HealthVisualizationOptions = {}): Promise<VisualizationData> {
    try {
      // 获取用户节点
      const userNode = await this.graphRepository.getNodeById(userId);
      
      if (!userNode) {
        throw new Error(`用户 ${userId} 不存在`);
      }

      // 获取用户健康相关节点
      const healthNodes = await this.graphRepository.getConnectedNodes(userId, {
        relationshipTypes: options.relationshipTypes || [
          'HAS_CONDITION',
          'HAS_SYMPTOM',
          'HAS_MEDICATION',
          'HAS_ALLERGY',
          'HAS_CONSTITUTION',
          'HAS_HEALTH_DATA',
          'HAS_GENOMIC_DATA'
        ],
        nodeTypes: options.nodeTypes || [
          'Condition', 
          'Symptom', 
          'Medication', 
          'Allergy',
          'Constitution',
          'HealthData',
          'GenomicData'
        ],
        limit: options.limit || 100
      });
      
      // 获取健康节点之间的关系
      const nodeIds = [...healthNodes.map(node => node.id), userId];
      const relationships = await this.graphRepository.getRelationshipsBetweenNodes(nodeIds);

      // 转换为可视化格式，使用特定配置
      return this.formatForVisualization({
        nodes: [userNode, ...healthNodes],
        relationships
      }, {
        userNodeColor: '#ff5722',
        nodeGroupColors: {
          'Condition': '#f44336',
          'Symptom': '#e91e63',
          'Medication': '#9c27b0',
          'Allergy': '#673ab7',
          'Constitution': '#3f51b5',
          'HealthData': '#2196f3',
          'GenomicData': '#00bcd4'
        }
      });
    } catch (error) {
      this.logger.error(`获取用户健康可视化失败: ${error.message}`);
      throw new Error(`获取用户健康可视化失败: ${error.message}`);
    }
  }

  /**
   * 获取健康数据的VR沉浸式可视化
   * @param userId 用户ID
   * @param options 可视化选项
   * @returns 格式化的VR可视化数据
   */
  async getUserHealthVRVisualization(userId: string, options: HealthVRVisualizationOptions = {}): Promise<VRVisualizationData> {
    try {
      // 获取用户节点
      const userNode = await this.graphRepository.getNodeById(userId);
      
      if (!userNode) {
        throw new Error(`用户 ${userId} 不存在`);
      }

      // 获取用户健康相关节点
      const healthNodes = await this.graphRepository.getConnectedNodes(userId, {
        relationshipTypes: options.relationshipTypes || [
          'HAS_CONDITION',
          'HAS_SYMPTOM',
          'HAS_MEDICATION',
          'HAS_ALLERGY',
          'HAS_CONSTITUTION',
          'HAS_HEALTH_DATA',
          'HAS_GENOMIC_DATA'
        ],
        nodeTypes: options.nodeTypes || [
          'Condition', 
          'Symptom', 
          'Medication', 
          'Allergy',
          'Constitution',
          'HealthData',
          'GenomicData'
        ],
        limit: options.limit || 150
      });
      
      // 获取健康节点之间的关系
      const nodeIds = [...healthNodes.map(node => node.id), userId];
      const relationships = await this.graphRepository.getRelationshipsBetweenNodes(nodeIds);
      
      // 获取节点间的相似度，用于VR中的空间布局
      const similarities = await this.graphRepository.getNodeSimilarities(nodeIds);

      // 转换为VR可视化格式
      return this.formatForVRVisualization({
        nodes: [userNode, ...healthNodes],
        relationships
      }, similarities, options.immersiveMode || 'body-centered');
    } catch (error) {
      this.logger.error(`获取用户健康VR可视化失败: ${error.message}`);
      throw new Error(`获取用户健康VR可视化失败: ${error.message}`);
    }
  }

  /**
   * 将图谱数据格式化为前端可视化格式
   * @param data 图谱数据
   * @param visualConfig 可视化配置
   * @returns 格式化后的可视化数据
   */
  private formatForVisualization(
    data: { nodes: any[], relationships: any[] },
    visualConfig: VisualConfig = {}
  ): VisualizationData {
    const { nodes, relationships } = data;
    
    // 设置默认配置
    const config = {
      defaultNodeColor: '#1976d2',
      defaultLinkColor: '#90caf9',
      nodeGroupColors: {
        'TCM': '#4caf50',
        'Herb': '#8bc34a',
        'Prescription': '#cddc39',
        'Symptom': '#ffeb3b',
        'Constitution': '#ffc107',
        'Acupoint': '#ff9800',
        'Diagnosis': '#ff5722',
        'Meridian': '#795548',
        'ModernMedicine': '#9e9e9e',
        'PrecisionMedicine': '#607d8b',
        'MultimodalHealth': '#3f51b5',
        'EnvironmentalHealth': '#2196f3',
        'MentalHealth': '#f44336',
        'IntegratedKnowledge': '#e91e63'
      },
      ...visualConfig
    };

    // 转换节点
    const visualNodes = nodes.map(node => ({
      id: node.id,
      label: node.name || node.id,
      title: node.description || node.name || '',
      group: node.labels[0] || 'Unknown',
      color: this.getNodeColor(node, config),
      value: node.importance || 1,
      properties: this.getNodeProperties(node)
    }));
    
    // 转换关系
    const visualLinks = relationships.map(rel => ({
      id: rel.id,
      from: rel.startNodeId,
      to: rel.endNodeId,
      label: rel.type,
      color: config.defaultLinkColor,
      arrows: 'to',
      title: rel.properties?.description || rel.type,
      width: rel.weight || 1
    }));

    return {
      nodes: visualNodes,
      links: visualLinks
    };
  }

  /**
   * 将图谱数据格式化为3D可视化格式
   * @param data 图谱数据
   * @param layout 3D布局类型
   * @returns 格式化后的3D可视化数据
   */
  private formatFor3DVisualization(
    data: { nodes: any[], relationships: any[] },
    layout: '3d-force' | '3d-hierarchical' | '3d-clustered' = '3d-force'
  ): Visualization3DData {
    const { nodes, relationships } = data;
    
    // 基础视觉配置
    const visualConfig = {
      defaultNodeColor: '#1976d2',
      defaultLinkColor: '#90caf9',
      nodeGroupColors: {
        'TCM': '#4caf50',
        'Herb': '#8bc34a',
        'Prescription': '#cddc39',
        'Symptom': '#ffeb3b',
        'Constitution': '#ffc107',
        'Acupoint': '#ff9800',
        'Diagnosis': '#ff5722',
        'Meridian': '#795548',
        'ModernMedicine': '#9e9e9e',
        'PrecisionMedicine': '#607d8b',
        'MultimodalHealth': '#3f51b5',
        'EnvironmentalHealth': '#2196f3',
        'MentalHealth': '#f44336',
        'IntegratedKnowledge': '#e91e63'
      }
    };

    // 转换节点为3D格式
    const visual3DNodes = nodes.map(node => {
      const nodeType = node.labels[0] || 'Unknown';
      // 根据节点类型决定3D形状
      const shape = this.get3DShapeForNodeType(nodeType);
      
      return {
        id: node.id,
        label: node.name || node.id,
        title: node.description || node.name || '',
        group: nodeType,
        color: visualConfig.nodeGroupColors[nodeType] || visualConfig.defaultNodeColor,
        value: node.importance || 1,
        shape: shape,
        geometry: shape.geometry,
        material: {
          color: visualConfig.nodeGroupColors[nodeType] || visualConfig.defaultNodeColor,
          transparent: true,
          opacity: 0.9
        },
        properties: this.getNodeProperties(node),
        // 初始无坐标，由前端布局算法计算
        x: undefined,
        y: undefined,
        z: undefined
      };
    });
    
    // 转换关系为3D格式
    const visual3DLinks = relationships.map(rel => ({
      id: rel.id,
      source: rel.startNodeId,
      target: rel.endNodeId,
      label: rel.type,
      color: visualConfig.defaultLinkColor,
      title: rel.properties?.description || rel.type,
      width: rel.weight || 1,
      material: {
        color: visualConfig.defaultLinkColor,
        transparent: true,
        opacity: 0.6,
        linewidth: (rel.weight || 1) * 2
      }
    }));

    return {
      nodes: visual3DNodes,
      links: visual3DLinks,
      layout: layout
    };
  }

  /**
   * 将图谱数据格式化为AR可视化格式
   * @param data 图谱数据
   * @param arMarkers AR标记配置
   * @returns 格式化后的AR可视化数据
   */
  private formatForARVisualization(
    data: { nodes: any[], relationships: any[] },
    arMarkers?: ARMarkers
  ): ARVisualizationData {
    const { nodes, relationships } = data;
    const baseVisualization = this.formatFor3DVisualization(data, '3d-force');
    
    // AR专用配置
    const arConfig = {
      scale: 0.5, // AR中的缩放比例
      position: { x: 0, y: 0, z: 0 }, // 相对于标记的位置
      interactive: true, // 是否可交互
      anchors: [] as ARNodeAnchor[], // 空间锚点
      markers: arMarkers || { type: 'qr', main: 'center' }
    };
    
    // 为每个节点添加AR特定属性
    const arNodes = baseVisualization.nodes.map((node, index) => ({
      ...node,
      ar: {
        scale: node.value * arConfig.scale,
        animation: {
          type: 'rotate',
          speed: 0.01,
          enabled: true
        },
        // 重要节点添加标签
        label: {
          visible: node.value > 1.5,
          scale: 0.8,
          offset: { x: 0, y: 1.2, z: 0 }
        }
      }
    }));

    return {
      nodes: arNodes,
      links: baseVisualization.links,
      ar: arConfig
    };
  }

  /**
   * 将图谱数据格式化为VR可视化格式
   * @param data 图谱数据
   * @param similarities 节点间的相似度矩阵
   * @param immersiveMode VR沉浸模式
   * @returns 格式化后的VR可视化数据
   */
  private formatForVRVisualization(
    data: { nodes: any[], relationships: any[] },
    similarities: { source: string, target: string, score: number }[],
    immersiveMode: 'full' | 'selective' | 'body-centered' = 'full'
  ): VRVisualizationData {
    const { nodes, relationships } = data;
    const baseVisualization = this.formatFor3DVisualization(data, '3d-force');
    
    // VR专用配置
    const vrConfig = {
      environment: 'space', // 环境背景：space, lab, nature
      scale: 15, // VR中的整体缩放比例
      position: { x: 0, y: 1.6, z: -3 }, // 相对于用户的初始位置
      gravity: 0.1, // 引力系数
      physics: true, // 是否启用物理引擎
      sound: true, // 是否启用空间音效
      immersiveMode: immersiveMode,
      interactions: {
        selection: true,
        navigation: true,
        manipulation: true
      },
      animations: {
        enabled: true,
        duration: 1000
      }
    };
    
    // 使用相似度信息优化VR布局
    const similarityEdges = [];
    if (similarities && similarities.length > 0) {
      for (const sim of similarities) {
        if (sim.score > 0.7) { // 只考虑高相似度的节点对
          similarityEdges.push({
            source: sim.source,
            target: sim.target,
            strength: sim.score
          });
        }
      }
    }
    
    // 为每个节点添加VR特定属性
    const vrNodes = baseVisualization.nodes.map(node => ({
      ...node,
      vr: {
        scale: node.value * 0.3, // VR中节点大小
        mass: node.value, // 物理引擎质量参数
        collider: true, // 是否有碰撞体积
        grabbable: true, // 是否可抓取
        sound: {
          onClick: `sounds/${node.group.toLowerCase()}.mp3`, // 点击音效
          onHover: `sounds/hover.mp3` // 悬停音效
        },
        detail: {
          model: node.group === 'User' ? '3d-models/user.glb' : null, // 自定义3D模型
          texture: `textures/${node.group.toLowerCase()}.png` // 贴图
        },
        tutorial: node.group === 'User' // 是否显示交互教程
      }
    }));

    return {
      nodes: vrNodes,
      links: baseVisualization.links,
      similarities: similarityEdges,
      vr: vrConfig
    };
  }

  /**
   * 获取节点颜色
   */
  private getNodeColor(node: any, config: VisualConfig): string {
    // 用户节点特殊处理
    if (node.labels.includes('User') && config.userNodeColor) {
      return config.userNodeColor;
    }
    
    // 基于节点类型获取颜色
    const nodeType = node.labels[0];
    return config.nodeGroupColors[nodeType] || config.defaultNodeColor;
  }

  /**
   * 提取节点属性
   */
  private getNodeProperties(node: any): Record<string, any> {
    // 排除不需要在可视化中显示的属性
    const excludedProps = ['id', 'labels', 'createdAt', 'updatedAt', 'vector'];
    const properties: Record<string, any> = {};
    
    Object.entries(node).forEach(([key, value]) => {
      if (!excludedProps.includes(key) && value !== null && value !== undefined) {
        properties[key] = value;
      }
    });
    
    return properties;
  }

  /**
   * 根据节点类型获取3D形状
   */
  private get3DShapeForNodeType(nodeType: string): Node3DShape {
    // 为不同节点类型配置不同的3D形状
    const shapes: Record<string, Node3DShape> = {
      'User': { type: 'sphere', geometry: { radius: 1 } },
      'TCM': { type: 'octahedron', geometry: { radius: 1 } },
      'Herb': { type: 'box', geometry: { width: 1, height: 1, depth: 1 } },
      'Prescription': { type: 'cylinder', geometry: { radius: 0.7, height: 1.4 } },
      'Symptom': { type: 'cone', geometry: { radius: 0.7, height: 1.2 } },
      'Constitution': { type: 'dodecahedron', geometry: { radius: 0.9 } },
      'Acupoint': { type: 'sphere', geometry: { radius: 0.6 } },
      'Diagnosis': { type: 'tetrahedron', geometry: { radius: 0.8 } },
      'Meridian': { type: 'tube', geometry: { radius: 0.5, height: 1.5 } },
      'ModernMedicine': { type: 'icosahedron', geometry: { radius: 0.8 } },
      'PrecisionMedicine': { type: 'sphere', geometry: { radius: 0.8 } },
      'MultimodalHealth': { type: 'torus', geometry: { radius: 0.7, tube: 0.2 } },
      'EnvironmentalHealth': { type: 'sphere', geometry: { radius: 0.7 } },
      'MentalHealth': { type: 'sphere', geometry: { radius: 0.7 } },
      'GenomicData': { type: 'helix', geometry: { radius: 0.6, height: 1.2, turns: 2 } }
    };
    
    return shapes[nodeType] || { type: 'sphere', geometry: { radius: 0.7 } };
  }
}

/**
 * 可视化选项接口
 */
export interface VisualizationOptions {
  centralNode: string;
  depth?: number;
  nodeTypes?: string[];
  relationshipTypes?: string[];
  limit?: number;
}

/**
 * 3D可视化选项接口
 */
export interface Visualization3DOptions extends VisualizationOptions {
  layout?: '3d-force' | '3d-hierarchical' | '3d-clustered';
}

/**
 * AR可视化选项接口
 */
export interface ARVisualizationOptions extends VisualizationOptions {
  arMarkers?: ARMarkers;
}

/**
 * VR可视化选项接口
 */
export interface VRVisualizationOptions extends VisualizationOptions {
  immersiveMode?: 'full' | 'selective' | 'body-centered';
}

/**
 * 领域可视化选项接口
 */
export interface DomainVisualizationOptions {
  nodeTypes?: string[];
  relationshipTypes?: string[];
  limit?: number;
}

/**
 * 领域3D可视化选项接口
 */
export interface Domain3DVisualizationOptions extends DomainVisualizationOptions {
  layout?: '3d-force' | '3d-hierarchical' | '3d-clustered';
}

/**
 * 健康可视化选项接口
 */
export interface HealthVisualizationOptions {
  nodeTypes?: string[];
  relationshipTypes?: string[];
  limit?: number;
}

/**
 * 健康VR可视化选项接口
 */
export interface HealthVRVisualizationOptions extends HealthVisualizationOptions {
  immersiveMode?: 'full' | 'selective' | 'body-centered';
}

/**
 * 可视化配置接口
 */
interface VisualConfig {
  defaultNodeColor?: string;
  defaultLinkColor?: string;
  userNodeColor?: string;
  nodeGroupColors?: Record<string, string>;
}

/**
 * AR标记配置接口
 */
export interface ARMarkers {
  type: 'qr' | 'image' | 'natural';
  main: string;
  auxiliary?: string[];
}

/**
 * AR节点锚点接口
 */
interface ARNodeAnchor {
  nodeId: string;
  position: { x: number, y: number, z: number };
  marker: string;
}

/**
 * 3D节点形状接口
 */
interface Node3DShape {
  type: '3d-model' | 'sphere' | 'box' | 'cylinder' | 'cone' | 'torus' | 
        'tetrahedron' | 'octahedron' | 'dodecahedron' | 'icosahedron' |
        'tube' | 'helix';
  geometry: any;
}

/**
 * 可视化数据接口
 */
export interface VisualizationData {
  nodes: Array<{
    id: string;
    label: string;
    title?: string;
    group?: string;
    color?: string;
    value?: number;
    properties?: Record<string, any>;
  }>;
  links: Array<{
    id: string;
    from: string;
    to: string;
    label?: string;
    color?: string;
    arrows?: string;
    title?: string;
    width?: number;
  }>;
}

/**
 * 3D可视化数据接口
 */
export interface Visualization3DData {
  nodes: Array<{
    id: string;
    label: string;
    title?: string;
    group?: string;
    color?: string;
    value?: number;
    shape?: Node3DShape;
    geometry?: any;
    material?: any;
    properties?: Record<string, any>;
    x?: number;
    y?: number;
    z?: number;
  }>;
  links: Array<{
    id: string;
    source: string;
    target: string;
    label?: string;
    color?: string;
    title?: string;
    width?: number;
    material?: any;
  }>;
  layout: '3d-force' | '3d-hierarchical' | '3d-clustered';
}

/**
 * AR可视化数据接口
 */
export interface ARVisualizationData {
  nodes: Array<{
    id: string;
    label: string;
    title?: string;
    group?: string;
    color?: string;
    value?: number;
    shape?: Node3DShape;
    geometry?: any;
    material?: any;
    properties?: Record<string, any>;
    ar?: {
      scale: number;
      animation?: {
        type: string;
        speed: number;
        enabled: boolean;
      };
      label?: {
        visible: boolean;
        scale: number;
        offset: { x: number, y: number, z: number };
      };
    };
  }>;
  links: Array<{
    id: string;
    source: string;
    target: string;
    label?: string;
    color?: string;
    title?: string;
    width?: number;
    material?: any;
  }>;
  ar: {
    scale: number;
    position: { x: number, y: number, z: number };
    interactive: boolean;
    anchors: ARNodeAnchor[];
    markers: ARMarkers;
  };
}

/**
 * VR可视化数据接口
 */
export interface VRVisualizationData {
  nodes: Array<{
    id: string;
    label: string;
    title?: string;
    group?: string;
    color?: string;
    value?: number;
    shape?: Node3DShape;
    geometry?: any;
    material?: any;
    properties?: Record<string, any>;
    vr?: {
      scale: number;
      mass: number;
      collider: boolean;
      grabbable: boolean;
      sound?: {
        onClick?: string;
        onHover?: string;
      };
      detail?: {
        model?: string;
        texture?: string;
      };
      tutorial?: boolean;
    };
  }>;
  links: Array<{
    id: string;
    source: string;
    target: string;
    label?: string;
    color?: string;
    title?: string;
    width?: number;
    material?: any;
  }>;
  similarities: Array<{
    source: string;
    target: string;
    strength: number;
  }>;
  vr: {
    environment: string;
    scale: number;
    position: { x: number, y: number, z: number };
    gravity: number;
    physics: boolean;
    sound: boolean;
    immersiveMode: string;
    interactions: {
      selection: boolean;
      navigation: boolean;
      manipulation: boolean;
    };
    animations: {
      enabled: boolean;
      duration: number;
    };
  };
} 