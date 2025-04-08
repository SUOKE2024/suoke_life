/**
 * 知识图谱服务API响应接口定义
 */

// 基础分页查询参数
export interface PaginationQuery {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortDirection?: 'asc' | 'desc';
}

// 搜索查询参数
export interface SearchQuery {
  query?: string;
  fields?: string[];
  fuzzy?: boolean;
  threshold?: number;
}

// 基础成功响应格式
export interface SuccessResponse<T = any> {
  success: true;
  message: string;
  data: T;
  timestamp: string;
}

// 分页响应数据格式
export interface PaginatedData<T = any> {
  items: T[];
  pagination: {
    totalItems: number;
    totalPages: number;
    currentPage: number;
    itemsPerPage: number;
  };
}

// 分页响应格式
export interface PaginatedResponse<T = any> {
  success: true;
  message: string;
  data: PaginatedData<T>;
  timestamp: string;
}

// 错误响应格式
export interface ErrorResponse {
  success: false;
  message: string;
  error: string;
  statusCode: number;
  timestamp: string;
}

// 节点数据结构
export interface GraphNode {
  id: string;
  type: string;
  labels?: string[];
  properties: Record<string, any>;
  createdAt?: string;
  updatedAt?: string;
  createdBy?: string;
  updatedBy?: string;
}

// 关系数据结构
export interface GraphRelationship {
  id: string;
  type: string;
  startNodeId: string;
  endNodeId: string;
  properties: Record<string, any>;
  createdAt?: string;
  updatedAt?: string;
  createdBy?: string;
  updatedBy?: string;
}

// 带关系的节点数据
export interface NodeWithRelationships {
  node: GraphNode;
  relationships: GraphRelationship[];
}

// 知识图谱统计信息
export interface GraphStats {
  nodeCount: number;
  relationshipCount: number;
  nodeCountByType: Record<string, number>;
  relationshipCountByType: Record<string, number>;
  nodeCountByDomain?: Record<string, number>;
}

// 路径数据
export interface GraphPath {
  nodes: GraphNode[];
  relationships: GraphRelationship[];
  length: number;
}

// 路径查询结果
export interface PathsResult {
  paths: GraphPath[];
  count: number;
}

// 可视化选项
export interface VisualizationOptions {
  maxDepth?: number;
  maxNodes?: number;
  layout?: string;
  nodeTypes?: string[];
  relationshipTypes?: string[];
  domains?: string[];
  dimensions?: '2D' | '3D';
}

// 可视化节点
export interface VisualizationNode {
  id: string;
  label: string;
  type: string;
  attributes: Record<string, any>;
  x?: number;
  y?: number;
  z?: number;
  size?: number;
  color?: string;
  geometry?: '球体' | '立方体' | '圆柱体' | '圆锥体' | '自定义';
}

// 可视化边
export interface VisualizationEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  attributes: Record<string, any>;
  size?: number;
  color?: string;
  curve?: number;
}

// 二维图谱可视化数据
export interface GraphVisualization {
  nodes: VisualizationNode[];
  edges: VisualizationEdge[];
  meta: {
    nodeCount: number;
    edgeCount: number;
    layout: string;
  };
}

// 三维图谱可视化数据
export interface ThreeDVisualization {
  nodes: VisualizationNode[];
  edges: VisualizationEdge[];
  meta: {
    nodeCount: number;
    edgeCount: number;
    layout: string;
    dimensions: '2D' | '3D';
  };
}

// AR场景对象
export interface ARObject {
  id: string;
  nodeId: string;
  type: string;
  model: string;
  position: {
    x: number;
    y: number;
    z: number;
  };
  rotation: {
    x: number;
    y: number;
    z: number;
  };
  scale: {
    x: number;
    y: number;
    z: number;
  };
  interactive: boolean;
  animation?: string;
}

// AR场景连接
export interface ARConnection {
  id: string;
  source: string;
  target: string;
  type: string;
  visualType: '线条' | '箭头' | '粒子' | '自定义';
  color: string;
}

// AR场景
export interface ARScene {
  id: string;
  name: string;
  anchor: {
    type: '图像' | '平面' | '人脸' | '世界';
    value?: string;
  };
  objects: ARObject[];
  connections: ARConnection[];
}

// AR可视化数据
export interface ARVisualization {
  scenes: ARScene[];
  meta: {
    version: string;
    sceneCount: number;
    objectCount: number;
    connectionCount: number;
  };
}

// 可视化预设配置
export interface VisualizationPreset {
  id: string;
  name: string;
  description: string;
  type: string;
  format: '2d' | '3d' | 'ar' | 'vr';
  config: Record<string, any>;
}

// 可视化预设结果
export interface PresetVisualizationResult {
  preset: {
    id: string;
    name: string;
    description: string;
    type: string;
    format: string;
  };
  visualization: GraphVisualization | ThreeDVisualization | ARVisualization;
}