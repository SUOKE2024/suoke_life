package utils

import (
	"container/list"
	"sync"
)

// LRUCache 简单的线程安全LRU缓存实现
type LRUCache struct {
	// 最大容量
	capacity int
	
	// 缓存项
	cache map[string]*list.Element
	
	// 使用顺序链表
	list *list.List
	
	// 互斥锁
	mutex sync.RWMutex
}

// cacheItem 缓存项
type cacheItem struct {
	key   string
	value interface{}
}

// NewLRUCache 创建新的LRU缓存
func NewLRUCache(capacity int) *LRUCache {
	if capacity <= 0 {
		capacity = 1000 // 默认容量
	}
	
	return &LRUCache{
		capacity: capacity,
		cache:    make(map[string]*list.Element),
		list:     list.New(),
	}
}

// Get 获取缓存值
func (c *LRUCache) Get(key string) (interface{}, bool) {
	c.mutex.RLock()
	element, exists := c.cache[key]
	c.mutex.RUnlock()
	
	if !exists {
		return nil, false
	}
	
	// 更新访问顺序
	c.mutex.Lock()
	c.list.MoveToFront(element)
	c.mutex.Unlock()
	
	return element.Value.(*cacheItem).value, true
}

// Set 设置缓存值
func (c *LRUCache) Set(key string, value interface{}) {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	
	// 检查键是否已存在
	if element, exists := c.cache[key]; exists {
		// 更新现有条目
		c.list.MoveToFront(element)
		element.Value.(*cacheItem).value = value
		return
	}
	
	// 添加新条目
	element := c.list.PushFront(&cacheItem{key: key, value: value})
	c.cache[key] = element
	
	// 检查是否超出容量
	if c.list.Len() > c.capacity {
		c.removeOldest()
	}
}

// Delete 删除缓存项
func (c *LRUCache) Delete(key string) {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	
	if element, exists := c.cache[key]; exists {
		c.list.Remove(element)
		delete(c.cache, key)
	}
}

// Clear 清空缓存
func (c *LRUCache) Clear() {
	c.mutex.Lock()
	defer c.mutex.Unlock()
	
	c.list = list.New()
	c.cache = make(map[string]*list.Element)
}

// Len 返回缓存项数量
func (c *LRUCache) Len() int {
	c.mutex.RLock()
	defer c.mutex.RUnlock()
	
	return c.list.Len()
}

// Keys 返回所有缓存键
func (c *LRUCache) Keys() []string {
	c.mutex.RLock()
	defer c.mutex.RUnlock()
	
	keys := make([]string, 0, len(c.cache))
	for key := range c.cache {
		keys = append(keys, key)
	}
	
	return keys
}

// 移除最老的缓存项
func (c *LRUCache) removeOldest() {
	element := c.list.Back()
	if element != nil {
		c.list.Remove(element)
		item := element.Value.(*cacheItem)
		delete(c.cache, item.key)
	}
} 