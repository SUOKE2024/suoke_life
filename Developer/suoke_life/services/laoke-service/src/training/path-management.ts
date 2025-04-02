/**
 * 学习路径管理服务
 * 负责学习路径的创建、更新、查询和管理
 */
import {
  LearningPath,
  LearningNode,
  LearningResource,
  LearningPathType,
  LearningMode,
  LearningResourceType,
  CompletionRequirement,
  CertificationType,
  Badge
} from './types';
import { 
  KnowledgeDomain, 
  DifficultyLevel, 
  ContentStatus 
} from '../knowledge/types';
import { logger } from '../utils/logger';

class PathManagement {
  // 模拟数据存储
  private pathsStore: Map<string, LearningPath> = new Map();
  private badgesStore: Map<string, Badge> = new Map();
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('学习路径管理服务初始化');
  }
  
  /**
   * 创建学习路径
   * @param path 学习路径
   * @returns 创建的路径ID
   */
  public async createPath(
    path: Omit<LearningPath, 'id' | 'createdAt' | 'updatedAt' | 'enrollmentCount' | 'completionCount' | 'rating' | 'ratingCount'>
  ): Promise<string> {
    const id = `path-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const now = new Date();
    
    const newPath: LearningPath = {
      ...path,
      id,
      createdAt: now,
      updatedAt: now,
      enrollmentCount: 0,
      completionCount: 0,
      rating: 0,
      ratingCount: 0
    };
    
    this.pathsStore.set(id, newPath);
    
    logger.info(`创建学习路径: ${id}`, {
      title: path.title,
      domain: path.domain,
      difficulty: path.difficulty
    });
    
    return id;
  }
  
  /**
   * 更新学习路径
   * @param id 路径ID
   * @param updates 更新内容
   * @returns 是否更新成功
   */
  public async updatePath(
    id: string,
    updates: Partial<Omit<LearningPath, 'id' | 'createdAt' | 'updatedAt' | 'enrollmentCount' | 'completionCount' | 'rating' | 'ratingCount'>>
  ): Promise<boolean> {
    if (!this.pathsStore.has(id)) {
      logger.warn(`更新失败，学习路径不存在: ${id}`);
      return false;
    }
    
    const path = this.pathsStore.get(id)!;
    
    const updatedPath: LearningPath = {
      ...path,
      ...updates,
      updatedAt: new Date()
    };
    
    this.pathsStore.set(id, updatedPath);
    
    logger.info(`更新学习路径: ${id}`);
    
    return true;
  }
  
  /**
   * 获取学习路径
   * @param id 路径ID
   * @returns 学习路径或null
   */
  public async getPath(id: string): Promise<LearningPath | null> {
    if (!this.pathsStore.has(id)) {
      logger.warn(`获取失败，学习路径不存在: ${id}`);
      return null;
    }
    
    logger.info(`获取学习路径: ${id}`);
    
    return this.pathsStore.get(id)!;
  }
  
  /**
   * 删除学习路径
   * @param id 路径ID
   * @returns 是否删除成功
   */
  public async deletePath(id: string): Promise<boolean> {
    if (!this.pathsStore.has(id)) {
      logger.warn(`删除失败，学习路径不存在: ${id}`);
      return false;
    }
    
    this.pathsStore.delete(id);
    
    logger.info(`删除学习路径: ${id}`);
    
    return true;
  }
  
  /**
   * 发布学习路径
   * @param id 路径ID
   * @returns 是否发布成功
   */
  public async publishPath(id: string): Promise<boolean> {
    if (!this.pathsStore.has(id)) {
      logger.warn(`发布失败，学习路径不存在: ${id}`);
      return false;
    }
    
    return this.updatePath(id, { status: ContentStatus.PUBLISHED });
  }
  
  /**
   * 归档学习路径
   * @param id 路径ID
   * @returns 是否归档成功
   */
  public async archivePath(id: string): Promise<boolean> {
    if (!this.pathsStore.has(id)) {
      logger.warn(`归档失败，学习路径不存在: ${id}`);
      return false;
    }
    
    return this.updatePath(id, { status: ContentStatus.ARCHIVED });
  }
  
  /**
   * 添加学习节点
   * @param pathId 路径ID
   * @param node 学习节点
   * @returns 创建的节点ID
   */
  public async addNode(
    pathId: string,
    node: Omit<LearningNode, 'id'>
  ): Promise<string> {
    if (!this.pathsStore.has(pathId)) {
      throw new Error(`学习路径不存在: ${pathId}`);
    }
    
    const path = this.pathsStore.get(pathId)!;
    
    const nodeId = `node-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    
    const newNode: LearningNode = {
      ...node,
      id: nodeId
    };
    
    // 添加节点
    const updatedNodes = [...path.nodes, newNode];
    
    // 按序号排序
    updatedNodes.sort((a, b) => a.order - b.order);
    
    // 更新路径
    await this.updatePath(pathId, { nodes: updatedNodes });
    
    logger.info(`添加学习节点: ${nodeId}`, {
      pathId,
      title: node.title,
      order: node.order
    });
    
    return nodeId;
  }
  
  /**
   * 更新学习节点
   * @param pathId 路径ID
   * @param nodeId 节点ID
   * @param updates 更新内容
   * @returns 是否更新成功
   */
  public async updateNode(
    pathId: string,
    nodeId: string,
    updates: Partial<Omit<LearningNode, 'id'>>
  ): Promise<boolean> {
    if (!this.pathsStore.has(pathId)) {
      logger.warn(`更新失败，学习路径不存在: ${pathId}`);
      return false;
    }
    
    const path = this.pathsStore.get(pathId)!;
    
    // 查找节点
    const nodeIndex = path.nodes.findIndex(node => node.id === nodeId);
    if (nodeIndex === -1) {
      logger.warn(`更新失败，学习节点不存在: ${nodeId}`);
      return false;
    }
    
    // 更新节点
    const updatedNodes = [...path.nodes];
    updatedNodes[nodeIndex] = {
      ...updatedNodes[nodeIndex],
      ...updates
    };
    
    // 按序号排序
    if (updates.order !== undefined) {
      updatedNodes.sort((a, b) => a.order - b.order);
    }
    
    // 更新路径
    await this.updatePath(pathId, { nodes: updatedNodes });
    
    logger.info(`更新学习节点: ${nodeId}`, {
      pathId
    });
    
    return true;
  }
  
  /**
   * 删除学习节点
   * @param pathId 路径ID
   * @param nodeId 节点ID
   * @returns 是否删除成功
   */
  public async deleteNode(
    pathId: string,
    nodeId: string
  ): Promise<boolean> {
    if (!this.pathsStore.has(pathId)) {
      logger.warn(`删除失败，学习路径不存在: ${pathId}`);
      return false;
    }
    
    const path = this.pathsStore.get(pathId)!;
    
    // 查找节点
    const nodeIndex = path.nodes.findIndex(node => node.id === nodeId);
    if (nodeIndex === -1) {
      logger.warn(`删除失败，学习节点不存在: ${nodeId}`);
      return false;
    }
    
    // 删除节点
    const updatedNodes = path.nodes.filter(node => node.id !== nodeId);
    
    // 更新路径
    await this.updatePath(pathId, { nodes: updatedNodes });
    
    logger.info(`删除学习节点: ${nodeId}`, {
      pathId
    });
    
    return true;
  }
  
  /**
   * 添加学习资源
   * @param pathId 路径ID
   * @param nodeId 节点ID
   * @param resource 学习资源
   * @returns 创建的资源ID
   */
  public async addResource(
    pathId: string,
    nodeId: string,
    resource: Omit<LearningResource, 'id'>
  ): Promise<string> {
    if (!this.pathsStore.has(pathId)) {
      throw new Error(`学习路径不存在: ${pathId}`);
    }
    
    const path = this.pathsStore.get(pathId)!;
    
    // 查找节点
    const nodeIndex = path.nodes.findIndex(node => node.id === nodeId);
    if (nodeIndex === -1) {
      throw new Error(`学习节点不存在: ${nodeId}`);
    }
    
    const resourceId = `resource-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    
    const newResource: LearningResource = {
      ...resource,
      id: resourceId
    };
    
    // 添加资源
    const updatedNode = { ...path.nodes[nodeIndex] };
    updatedNode.resources = [...updatedNode.resources, newResource];
    
    // 按序号排序
    updatedNode.resources.sort((a, b) => a.order - b.order);
    
    // 更新节点
    const updatedNodes = [...path.nodes];
    updatedNodes[nodeIndex] = updatedNode;
    
    // 更新路径
    await this.updatePath(pathId, { nodes: updatedNodes });
    
    logger.info(`添加学习资源: ${resourceId}`, {
      pathId,
      nodeId,
      title: resource.title,
      type: resource.type
    });
    
    return resourceId;
  }
  
  /**
   * 更新学习资源
   * @param pathId 路径ID
   * @param nodeId 节点ID
   * @param resourceId 资源ID
   * @param updates 更新内容
   * @returns 是否更新成功
   */
  public async updateResource(
    pathId: string,
    nodeId: string,
    resourceId: string,
    updates: Partial<Omit<LearningResource, 'id'>>
  ): Promise<boolean> {
    if (!this.pathsStore.has(pathId)) {
      logger.warn(`更新失败，学习路径不存在: ${pathId}`);
      return false;
    }
    
    const path = this.pathsStore.get(pathId)!;
    
    // 查找节点
    const nodeIndex = path.nodes.findIndex(node => node.id === nodeId);
    if (nodeIndex === -1) {
      logger.warn(`更新失败，学习节点不存在: ${nodeId}`);
      return false;
    }
    
    // 查找资源
    const node = path.nodes[nodeIndex];
    const resourceIndex = node.resources.findIndex(res => res.id === resourceId);
    if (resourceIndex === -1) {
      logger.warn(`更新失败，学习资源不存在: ${resourceId}`);
      return false;
    }
    
    // 更新资源
    const updatedResources = [...node.resources];
    updatedResources[resourceIndex] = {
      ...updatedResources[resourceIndex],
      ...updates
    };
    
    // 按序号排序
    if (updates.order !== undefined) {
      updatedResources.sort((a, b) => a.order - b.order);
    }
    
    // 更新节点
    const updatedNode = { ...node, resources: updatedResources };
    
    // 更新路径
    const updatedNodes = [...path.nodes];
    updatedNodes[nodeIndex] = updatedNode;
    
    await this.updatePath(pathId, { nodes: updatedNodes });
    
    logger.info(`更新学习资源: ${resourceId}`, {
      pathId,
      nodeId
    });
    
    return true;
  }
  
  /**
   * 删除学习资源
   * @param pathId 路径ID
   * @param nodeId 节点ID
   * @param resourceId 资源ID
   * @returns 是否删除成功
   */
  public async deleteResource(
    pathId: string,
    nodeId: string,
    resourceId: string
  ): Promise<boolean> {
    if (!this.pathsStore.has(pathId)) {
      logger.warn(`删除失败，学习路径不存在: ${pathId}`);
      return false;
    }
    
    const path = this.pathsStore.get(pathId)!;
    
    // 查找节点
    const nodeIndex = path.nodes.findIndex(node => node.id === nodeId);
    if (nodeIndex === -1) {
      logger.warn(`删除失败，学习节点不存在: ${nodeId}`);
      return false;
    }
    
    // 查找资源
    const node = path.nodes[nodeIndex];
    const resourceIndex = node.resources.findIndex(res => res.id === resourceId);
    if (resourceIndex === -1) {
      logger.warn(`删除失败，学习资源不存在: ${resourceId}`);
      return false;
    }
    
    // 删除资源
    const updatedResources = node.resources.filter(res => res.id !== resourceId);
    
    // 更新节点
    const updatedNode = { ...node, resources: updatedResources };
    
    // 更新路径
    const updatedNodes = [...path.nodes];
    updatedNodes[nodeIndex] = updatedNode;
    
    await this.updatePath(pathId, { nodes: updatedNodes });
    
    logger.info(`删除学习资源: ${resourceId}`, {
      pathId,
      nodeId
    });
    
    return true;
  }
  
  /**
   * 获取学习路径列表
   * @param domain 知识领域过滤
   * @param difficulty 难度级别过滤
   * @param type 路径类型过滤
   * @param status 状态过滤
   * @returns 学习路径列表
   */
  public async getPaths(
    domain?: KnowledgeDomain,
    difficulty?: DifficultyLevel,
    type?: LearningPathType,
    status: ContentStatus = ContentStatus.PUBLISHED
  ): Promise<LearningPath[]> {
    let paths = Array.from(this.pathsStore.values());
    
    // 按状态过滤
    paths = paths.filter(path => path.status === status);
    
    // 按领域过滤
    if (domain) {
      paths = paths.filter(path => path.domain === domain);
    }
    
    // 按难度过滤
    if (difficulty) {
      paths = paths.filter(path => path.difficulty === difficulty);
    }
    
    // 按类型过滤
    if (type) {
      paths = paths.filter(path => path.type === type);
    }
    
    logger.info(`获取学习路径列表`, {
      count: paths.length,
      domain,
      difficulty,
      type,
      status
    });
    
    return paths;
  }
  
  /**
   * 创建徽章
   * @param badge 徽章
   * @returns 创建的徽章ID
   */
  public async createBadge(
    badge: Omit<Badge, 'id' | 'createdAt' | 'earnedCount'>
  ): Promise<string> {
    const id = `badge-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    
    const newBadge: Badge = {
      ...badge,
      id,
      createdAt: new Date(),
      earnedCount: 0
    };
    
    this.badgesStore.set(id, newBadge);
    
    logger.info(`创建徽章: ${id}`, {
      name: badge.name,
      level: badge.level,
      category: badge.category
    });
    
    return id;
  }
  
  /**
   * 更新徽章
   * @param id 徽章ID
   * @param updates 更新内容
   * @returns 是否更新成功
   */
  public async updateBadge(
    id: string,
    updates: Partial<Omit<Badge, 'id' | 'createdAt' | 'earnedCount'>>
  ): Promise<boolean> {
    if (!this.badgesStore.has(id)) {
      logger.warn(`更新失败，徽章不存在: ${id}`);
      return false;
    }
    
    const badge = this.badgesStore.get(id)!;
    
    const updatedBadge: Badge = {
      ...badge,
      ...updates
    };
    
    this.badgesStore.set(id, updatedBadge);
    
    logger.info(`更新徽章: ${id}`);
    
    return true;
  }
  
  /**
   * 获取徽章
   * @param id 徽章ID
   * @returns 徽章或null
   */
  public async getBadge(id: string): Promise<Badge | null> {
    if (!this.badgesStore.has(id)) {
      logger.warn(`获取失败，徽章不存在: ${id}`);
      return null;
    }
    
    logger.info(`获取徽章: ${id}`);
    
    return this.badgesStore.get(id)!;
  }
  
  /**
   * 删除徽章
   * @param id 徽章ID
   * @returns 是否删除成功
   */
  public async deleteBadge(id: string): Promise<boolean> {
    if (!this.badgesStore.has(id)) {
      logger.warn(`删除失败，徽章不存在: ${id}`);
      return false;
    }
    
    this.badgesStore.delete(id);
    
    logger.info(`删除徽章: ${id}`);
    
    return true;
  }
  
  /**
   * 获取路径徽章
   * @param pathId 路径ID
   * @returns 徽章列表
   */
  public async getPathBadges(pathId: string): Promise<Badge[]> {
    const badges = Array.from(this.badgesStore.values())
      .filter(badge => 
        badge.criteria.includes(pathId) || 
        badge.category.includes('path')
      );
    
    logger.info(`获取路径徽章`, {
      pathId,
      count: badges.length
    });
    
    return badges;
  }
  
  /**
   * 复制学习路径
   * @param sourceId 源路径ID
   * @param title 新路径标题
   * @param creatorId 创建者ID
   * @returns 新路径ID
   */
  public async clonePath(
    sourceId: string,
    title: string,
    creatorId: string
  ): Promise<string> {
    if (!this.pathsStore.has(sourceId)) {
      throw new Error(`源学习路径不存在: ${sourceId}`);
    }
    
    const sourcePath = this.pathsStore.get(sourceId)!;
    
    // 创建新路径
    const newPathId = await this.createPath({
      ...sourcePath,
      title,
      creatorId,
      status: ContentStatus.DRAFT
    });
    
    logger.info(`复制学习路径: ${sourceId} -> ${newPathId}`, {
      title,
      creatorId
    });
    
    return newPathId;
  }
  
  /**
   * 获取热门学习路径
   * @param limit 限制数量
   * @param domain 知识领域
   * @returns 热门路径列表
   */
  public async getHotPaths(limit: number = 10, domain?: KnowledgeDomain): Promise<LearningPath[]> {
    let paths = Array.from(this.pathsStore.values())
      .filter(path => path.status === ContentStatus.PUBLISHED);
    
    // 按领域过滤
    if (domain) {
      paths = paths.filter(path => path.domain === domain);
    }
    
    // 按热度排序(根据学习人数、完成人数和评分)
    paths.sort((a, b) => {
      const scoreA = a.enrollmentCount * 1 + a.completionCount * 3 + a.rating * 5;
      const scoreB = b.enrollmentCount * 1 + b.completionCount * 3 + b.rating * 5;
      return scoreB - scoreA;
    });
    
    logger.info(`获取热门学习路径`, {
      limit,
      domain,
      total: paths.length
    });
    
    return paths.slice(0, limit);
  }
}

export default new PathManagement();