import { KnowledgeNode, KnowledgeRelation } from '../entities/KnowledgeNode';

export interface SearchOptions {
  limit?: number;
  offset?: number;
  domain?: string;
  type?: string;
  minRelevance?: number;
}

export interface IKnowledgeGraphRepository {
  // 节点操作
  createNode(node: Omit<KnowledgeNode, 'id' | 'createdAt' | 'updatedAt'>): Promise<KnowledgeNode>;
  updateNode(id: string, node: Partial<KnowledgeNode>): Promise<KnowledgeNode>;
  deleteNode(id: string): Promise<boolean>;
  getNodeById(id: string): Promise<KnowledgeNode | null>;
  searchNodes(query: string, options?: SearchOptions): Promise<KnowledgeNode[]>;
  
  // 关系操作
  createRelation(relation: Omit<KnowledgeRelation, 'id' | 'createdAt' | 'updatedAt'>): Promise<KnowledgeRelation>;
  updateRelation(id: string, relation: Partial<KnowledgeRelation>): Promise<KnowledgeRelation>;
  deleteRelation(id: string): Promise<boolean>;
  getRelationById(id: string): Promise<KnowledgeRelation | null>;
  
  // 向量操作
  updateNodeVector(id: string, vector: number[]): Promise<boolean>;
  searchSimilarNodes(vector: number[], options?: SearchOptions): Promise<KnowledgeNode[]>;
  
  // 图遍历
  getRelatedNodes(nodeId: string, relationTypes?: string[], maxDepth?: number): Promise<KnowledgeNode[]>;
  getShortestPath(fromNodeId: string, toNodeId: string, relationTypes?: string[]): Promise<KnowledgeRelation[]>;
  
  // 批量操作
  batchCreateNodes(nodes: Array<Omit<KnowledgeNode, 'id' | 'createdAt' | 'updatedAt'>>): Promise<KnowledgeNode[]>;
  batchCreateRelations(relations: Array<Omit<KnowledgeRelation, 'id' | 'createdAt' | 'updatedAt'>>): Promise<KnowledgeRelation[]>;
}