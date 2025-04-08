/**
 * 基础节点类
 * 作为所有知识图谱节点的基类
 */

export interface BaseNode {
  id: string;
  name: string;
  description?: string;
  category: string;
  createdAt: Date;
  updatedAt: Date;
  vector?: number[];
  source?: string;
  confidence?: number;
  tags?: string[];
  aliases?: string[];
  relatedTerms?: string[];
  status: 'active' | 'inactive' | 'deprecated';
  metadata?: Record<string, any>;
}

export interface BaseNodeProperties {
  name: string;
  description?: string;
  category: string;
  source?: string;
  confidence?: number;
  tags?: string[];
  aliases?: string[];
  relatedTerms?: string[];
  status?: 'active' | 'inactive' | 'deprecated';
  metadata?: Record<string, any>;
}

export class BaseNodeImpl implements BaseNode {
  id: string;
  name: string;
  description?: string;
  category: string;
  createdAt: Date;
  updatedAt: Date;
  vector?: number[];
  source?: string;
  confidence?: number;
  tags?: string[];
  aliases?: string[];
  relatedTerms?: string[];
  status: 'active' | 'inactive' | 'deprecated';
  metadata?: Record<string, any>;

  constructor(props: BaseNodeProperties) {
    this.id = generateUUID();
    this.name = props.name;
    this.description = props.description;
    this.category = props.category;
    this.createdAt = new Date();
    this.updatedAt = new Date();
    this.source = props.source;
    this.confidence = props.confidence;
    this.tags = props.tags || [];
    this.aliases = props.aliases || [];
    this.relatedTerms = props.relatedTerms || [];
    this.status = props.status || 'active';
    this.metadata = props.metadata || {};
  }

  update(props: Partial<BaseNodeProperties>): void {
    if (props.name) this.name = props.name;
    if (props.description) this.description = props.description;
    if (props.category) this.category = props.category;
    if (props.source) this.source = props.source;
    if (props.confidence) this.confidence = props.confidence;
    if (props.tags) this.tags = props.tags;
    if (props.aliases) this.aliases = props.aliases;
    if (props.relatedTerms) this.relatedTerms = props.relatedTerms;
    if (props.status) this.status = props.status;
    if (props.metadata) this.metadata = {...this.metadata, ...props.metadata};
    this.updatedAt = new Date();
  }

  toJSON(): Record<string, any> {
    return {
      id: this.id,
      name: this.name,
      description: this.description,
      category: this.category,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt,
      source: this.source,
      confidence: this.confidence,
      tags: this.tags,
      aliases: this.aliases,
      relatedTerms: this.relatedTerms,
      status: this.status,
      metadata: this.metadata
    };
  }
}

// 生成UUID的辅助函数
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
} 