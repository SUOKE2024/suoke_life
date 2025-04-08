import { KnowledgeNode, Relation } from '../../domain/entities/KnowledgeGraph';
import logger from '../logger';

export interface Node3D {
  id: string;
  position: Vector3;
  color: string;
  size: number;
  label: string;
  type: string;
  metadata: any;
}

export interface Edge3D {
  id: string;
  source: string;
  target: string;
  type: string;
  color: string;
  width: number;
  metadata: any;
}

export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export interface LayoutConfig {
  type: '3d' | 'vr' | 'ar';
  algorithm: 'force-directed' | 'hierarchical' | 'radial';
  dimensions: {
    width: number;
    height: number;
    depth: number;
  };
  physics: {
    gravity: number;
    springLength: number;
    springStrength: number;
    repulsion: number;
  };
}

export interface InteractionConfig {
  enableZoom: boolean;
  enableRotation: boolean;
  enableDrag: boolean;
  highlightNeighbors: boolean;
  showLabels: boolean;
  labelSize: number;
  minZoom: number;
  maxZoom: number;
}

export interface StyleConfig {
  nodeColors: Record<string, string>;
  edgeColors: Record<string, string>;
  nodeSizes: Record<string, number>;
  edgeWidths: Record<string, number>;
  defaultNodeColor: string;
  defaultEdgeColor: string;
  highlightColor: string;
  backgroundColor: string;
}

export class VisualizationManager {
  private static instance: VisualizationManager;
  private nodes: Map<string, Node3D>;
  private edges: Map<string, Edge3D>;
  private layout: LayoutConfig;
  private interaction: InteractionConfig;
  private style: StyleConfig;

  private constructor() {
    this.nodes = new Map();
    this.edges = new Map();
    this.initializeConfigs();
  }

  public static getInstance(): VisualizationManager {
    if (!VisualizationManager.instance) {
      VisualizationManager.instance = new VisualizationManager();
    }
    return VisualizationManager.instance;
  }

  private initializeConfigs(): void {
    this.layout = {
      type: '3d',
      algorithm: 'force-directed',
      dimensions: {
        width: 1000,
        height: 1000,
        depth: 1000
      },
      physics: {
        gravity: -1.2,
        springLength: 100,
        springStrength: 0.08,
        repulsion: 120
      }
    };

    this.interaction = {
      enableZoom: true,
      enableRotation: true,
      enableDrag: true,
      highlightNeighbors: true,
      showLabels: true,
      labelSize: 12,
      minZoom: 0.1,
      maxZoom: 10
    };

    this.style = {
      nodeColors: {
        'TCM_THEORY': '#FF6B6B',
        'SYMPTOM': '#4ECDC4',
        'TREATMENT': '#45B7D1',
        'HERB': '#96CEB4',
        'PRESCRIPTION': '#FFEEAD'
      },
      edgeColors: {
        'CAUSES': '#FF6B6B',
        'TREATS': '#4ECDC4',
        'CONTAINS': '#45B7D1',
        'RELATES_TO': '#96CEB4'
      },
      nodeSizes: {
        'TCM_THEORY': 20,
        'SYMPTOM': 15,
        'TREATMENT': 18,
        'HERB': 12,
        'PRESCRIPTION': 16
      },
      edgeWidths: {
        'CAUSES': 2,
        'TREATS': 3,
        'CONTAINS': 1,
        'RELATES_TO': 1
      },
      defaultNodeColor: '#666666',
      defaultEdgeColor: '#999999',
      highlightColor: '#FFA500',
      backgroundColor: '#FFFFFF'
    };
  }

  /**
   * 将知识图谱节点转换为3D节点
   */
  public convertToNode3D(node: KnowledgeNode): Node3D {
    return {
      id: node.id,
      position: this.calculateInitialPosition(),
      color: this.style.nodeColors[node.type] || this.style.defaultNodeColor,
      size: this.style.nodeSizes[node.type] || 10,
      label: node.content.substring(0, 30),
      type: node.type,
      metadata: node.metadata
    };
  }

  /**
   * 将关系转换为3D边
   */
  public convertToEdge3D(relation: Relation): Edge3D {
    return {
      id: relation.id,
      source: relation.fromId,
      target: relation.toId,
      type: relation.type,
      color: this.style.edgeColors[relation.type] || this.style.defaultEdgeColor,
      width: this.style.edgeWidths[relation.type] || 1,
      metadata: relation.metadata
    };
  }

  /**
   * 添加节点到可视化
   */
  public addNode(node: KnowledgeNode): void {
    const node3D = this.convertToNode3D(node);
    this.nodes.set(node.id, node3D);
    this.updateLayout();
  }

  /**
   * 添加边到可视化
   */
  public addEdge(relation: Relation): void {
    const edge3D = this.convertToEdge3D(relation);
    this.edges.set(relation.id, edge3D);
    this.updateLayout();
  }

  /**
   * 更新布局
   */
  private updateLayout(): void {
    switch (this.layout.algorithm) {
      case 'force-directed':
        this.applyForceDirectedLayout();
        break;
      case 'hierarchical':
        this.applyHierarchicalLayout();
        break;
      case 'radial':
        this.applyRadialLayout();
        break;
    }
  }

  /**
   * 应用力导向布局
   */
  private applyForceDirectedLayout(): void {
    // 实现力导向布局算法
    const nodes = Array.from(this.nodes.values());
    const edges = Array.from(this.edges.values());
    
    // 迭代计算节点位置
    for (let i = 0; i < 100; i++) {
      // 计算节点间的斥力
      this.calculateRepulsion(nodes);
      
      // 计算边的弹力
      this.calculateSpringForces(nodes, edges);
      
      // 更新节点位置
      this.updateNodePositions(nodes);
    }
  }

  /**
   * 计算节点间斥力
   */
  private calculateRepulsion(nodes: Node3D[]): void {
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const node1 = nodes[i];
        const node2 = nodes[j];
        
        // 计算节点间距离
        const dx = node2.position.x - node1.position.x;
        const dy = node2.position.y - node1.position.y;
        const dz = node2.position.z - node1.position.z;
        const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
        
        // 计算斥力
        const force = this.layout.physics.repulsion / (distance * distance);
        
        // 应用斥力
        const fx = (dx / distance) * force;
        const fy = (dy / distance) * force;
        const fz = (dz / distance) * force;
        
        node1.position.x -= fx;
        node1.position.y -= fy;
        node1.position.z -= fz;
        node2.position.x += fx;
        node2.position.y += fy;
        node2.position.z += fz;
      }
    }
  }

  /**
   * 计算边的弹力
   */
  private calculateSpringForces(nodes: Node3D[], edges: Edge3D[]): void {
    for (const edge of edges) {
      const source = nodes.find(n => n.id === edge.source);
      const target = nodes.find(n => n.id === edge.target);
      
      if (!source || !target) continue;
      
      // 计算边的长度
      const dx = target.position.x - source.position.x;
      const dy = target.position.y - source.position.y;
      const dz = target.position.z - source.position.z;
      const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
      
      // 计算弹力
      const force = (distance - this.layout.physics.springLength) * 
                   this.layout.physics.springStrength;
      
      // 应用弹力
      const fx = (dx / distance) * force;
      const fy = (dy / distance) * force;
      const fz = (dz / distance) * force;
      
      source.position.x += fx;
      source.position.y += fy;
      source.position.z += fz;
      target.position.x -= fx;
      target.position.y -= fy;
      target.position.z -= fz;
    }
  }

  /**
   * 更新节点位置
   */
  private updateNodePositions(nodes: Node3D[]): void {
    for (const node of nodes) {
      // 限制节点在可视范围内
      node.position.x = Math.max(-this.layout.dimensions.width/2,
        Math.min(this.layout.dimensions.width/2, node.position.x));
      node.position.y = Math.max(-this.layout.dimensions.height/2,
        Math.min(this.layout.dimensions.height/2, node.position.y));
      node.position.z = Math.max(-this.layout.dimensions.depth/2,
        Math.min(this.layout.dimensions.depth/2, node.position.z));
    }
  }

  /**
   * 计算初始位置
   */
  private calculateInitialPosition(): Vector3 {
    return {
      x: (Math.random() - 0.5) * this.layout.dimensions.width,
      y: (Math.random() - 0.5) * this.layout.dimensions.height,
      z: (Math.random() - 0.5) * this.layout.dimensions.depth
    };
  }

  /**
   * 获取可视化数据
   */
  public getVisualizationData(): {
    nodes: Node3D[];
    edges: Edge3D[];
    config: {
      layout: LayoutConfig;
      interaction: InteractionConfig;
      style: StyleConfig;
    };
  } {
    return {
      nodes: Array.from(this.nodes.values()),
      edges: Array.from(this.edges.values()),
      config: {
        layout: this.layout,
        interaction: this.interaction,
        style: this.style
      }
    };
  }

  /**
   * 更新配置
   */
  public updateConfig(config: {
    layout?: Partial<LayoutConfig>;
    interaction?: Partial<InteractionConfig>;
    style?: Partial<StyleConfig>;
  }): void {
    if (config.layout) {
      this.layout = { ...this.layout, ...config.layout };
    }
    if (config.interaction) {
      this.interaction = { ...this.interaction, ...config.interaction };
    }
    if (config.style) {
      this.style = { ...this.style, ...config.style };
    }
    this.updateLayout();
  }

  /**
   * 清除可视化数据
   */
  public clear(): void {
    this.nodes.clear();
    this.edges.clear();
  }
}