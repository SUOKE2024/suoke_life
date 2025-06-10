"""
数据库服务测试
测试数据库服务的各项功能
"""

import pytest
import asyncio
import datetime
from unittest.mock import AsyncMock, patch

from unified_health_data_service.health_data_service.core.database import DatabaseService


class TestDatabaseService:
    """数据库服务测试类"""
    
    @pytest.fixture
    async def database_service(self):
        """创建数据库服务实例"""
        service = DatabaseService()
        # 模拟初始化
        service.connected = True
        service.pg_pool = AsyncMock()
        service.redis_client = AsyncMock()
        service.mongo_client = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_initialize(self):
        """测试数据库初始化"""
        service = DatabaseService()
        
        with patch('asyncpg.create_pool') as mock_pg_pool, \
             patch('aioredis.from_url') as mock_redis, \
             patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_mongo:
            
            mock_pg_pool.return_value = AsyncMock()
            mock_redis.return_value = AsyncMock()
            mock_mongo.return_value = AsyncMock()
            
            await service.initialize()
            
            assert service.connected is True
            mock_pg_pool.assert_called_once()
            mock_redis.assert_called_once()
            mock_mongo.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_data(self, database_service):
        """测试数据存储"""
        # 模拟数据库连接
        mock_connection = AsyncMock()
        mock_connection.fetchval.return_value = "test_id_123"
        database_service.pg_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        # 测试数据
        test_data = {
            'user_id': 'user123',
            'data_type': 'vital_signs',
            'heart_rate': 75
        }
        
        result = await database_service.store_data('health_data', test_data)
        
        assert result == "test_id_123"
        mock_connection.fetchval.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_data(self, database_service):
        """测试数据查询"""
        # 模拟查询结果
        mock_records = [
            {'id': 1, 'user_id': 'user123', 'data_type': 'vital_signs'},
            {'id': 2, 'user_id': 'user123', 'data_type': 'diagnostic'}
        ]
        
        mock_connection = AsyncMock()
        mock_connection.fetch.return_value = mock_records
        database_service.pg_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        conditions = {'user_id': 'user123'}
        results = await database_service.query_data('health_data', conditions)
        
        assert len(results) == 2
        assert results[0]['user_id'] == 'user123'
        mock_connection.fetch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_data(self, database_service):
        """测试数据更新"""
        mock_connection = AsyncMock()
        mock_connection.execute.return_value = "UPDATE 1"
        database_service.pg_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        update_data = {'heart_rate': 80}
        conditions = {'id': 1}
        
        result = await database_service.update_data('health_data', update_data, conditions)
        
        assert result == 1
        mock_connection.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_data(self, database_service):
        """测试数据删除"""
        mock_connection = AsyncMock()
        mock_connection.execute.return_value = "DELETE 1"
        database_service.pg_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        conditions = {'id': 1}
        
        result = await database_service.delete_data('health_data', conditions)
        
        assert result == 1
        mock_connection.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_operations(self, database_service):
        """测试缓存操作"""
        # 测试设置缓存
        await database_service.cache_set('test_key', 'test_value', 3600)
        database_service.redis_client.setex.assert_called_once_with('test_key', 3600, '"test_value"')
        
        # 测试获取缓存
        database_service.redis_client.get.return_value = '"test_value"'
        result = await database_service.cache_get('test_key')
        assert result == 'test_value'
        
        # 测试删除缓存
        await database_service.cache_delete('test_key')
        database_service.redis_client.delete.assert_called_once_with('test_key')
    
    @pytest.mark.asyncio
    async def test_mongo_operations(self, database_service):
        """测试MongoDB操作"""
        # 模拟MongoDB集合
        mock_collection = AsyncMock()
        database_service.mongo_client.__getitem__.return_value.__getitem__.return_value = mock_collection
        
        # 测试插入
        mock_collection.insert_one.return_value.inserted_id = "mongo_id_123"
        result = await database_service.mongo_insert('test_collection', {'test': 'data'})
        assert result == "mongo_id_123"
        
        # 测试查询
        mock_collection.find.return_value.to_list.return_value = [{'_id': 'id1', 'data': 'test'}]
        results = await database_service.mongo_find('test_collection', {'test': 'data'})
        assert len(results) == 1
        
        # 测试更新
        mock_collection.update_many.return_value.modified_count = 1
        result = await database_service.mongo_update('test_collection', {'test': 'data'}, {'$set': {'updated': True}})
        assert result.modified_count == 1
        
        # 测试删除
        mock_collection.delete_many.return_value.deleted_count = 1
        result = await database_service.mongo_delete('test_collection', {'test': 'data'})
        assert result.deleted_count == 1
    
    @pytest.mark.asyncio
    async def test_transaction_management(self, database_service):
        """测试事务管理"""
        # 模拟事务
        mock_transaction = AsyncMock()
        mock_connection = AsyncMock()
        mock_connection.transaction.return_value = mock_transaction
        database_service.pg_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        # 测试开始事务
        transaction_id = await database_service.begin_transaction()
        assert transaction_id is not None
        
        # 测试提交事务
        await database_service.commit_transaction(transaction_id)
        
        # 测试回滚事务
        await database_service.rollback_transaction(transaction_id)
    
    @pytest.mark.asyncio
    async def test_health_check(self, database_service):
        """测试健康检查"""
        # 模拟健康检查
        mock_connection = AsyncMock()
        mock_connection.fetchval.return_value = 1
        database_service.pg_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        database_service.redis_client.ping.return_value = True
        database_service.mongo_client.admin.command.return_value = {'ok': 1}
        
        health_status = await database_service.health_check()
        
        assert health_status['postgresql'] is True
        assert health_status['redis'] is True
        assert health_status['mongodb'] is True
        assert health_status['overall'] is True
    
    @pytest.mark.asyncio
    async def test_get_status(self, database_service):
        """测试获取状态"""
        status = await database_service.get_status()
        
        assert 'connected' in status
        assert 'databases' in status
        assert 'uptime' in status
        assert status['connected'] is True
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, database_service):
        """测试获取指标"""
        # 模拟指标数据
        mock_connection = AsyncMock()
        mock_connection.fetch.return_value = [
            {'table_name': 'health_data', 'row_count': 1000},
            {'table_name': 'vital_signs', 'row_count': 500}
        ]
        database_service.pg_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        database_service.redis_client.info.return_value = {'used_memory': 1024000}
        
        metrics = await database_service.get_metrics()
        
        assert 'postgresql' in metrics
        assert 'redis' in metrics
        assert 'mongodb' in metrics
    
    @pytest.mark.asyncio
    async def test_error_handling(self, database_service):
        """测试错误处理"""
        # 模拟数据库错误
        mock_connection = AsyncMock()
        mock_connection.fetchval.side_effect = Exception("Database error")
        database_service.pg_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        with pytest.raises(Exception):
            await database_service.store_data('health_data', {'test': 'data'})
    
    @pytest.mark.asyncio
    async def test_connection_pool_management(self, database_service):
        """测试连接池管理"""
        # 测试连接池状态
        assert database_service.connected is True
        
        # 测试关闭连接
        await database_service.close()
        
        # 验证连接池关闭
        database_service.pg_pool.close.assert_called_once()
        database_service.redis_client.close.assert_called_once()
        database_service.mongo_client.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_data_migration(self, database_service):
        """测试数据迁移"""
        # 模拟迁移执行
        mock_connection = AsyncMock()
        database_service.pg_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        result = await database_service.run_migration('test_migration')
        
        assert 'migration_name' in result
        assert 'status' in result
        assert result['migration_name'] == 'test_migration'
    
    @pytest.mark.asyncio
    async def test_query_optimization(self, database_service):
        """测试查询优化"""
        # 测试带索引的查询
        mock_connection = AsyncMock()
        mock_connection.fetch.return_value = []
        database_service.pg_pool.acquire.return_value.__aenter__.return_value = mock_connection
        
        conditions = {'user_id': 'user123', 'created_at': datetime.utcnow()}
        await database_service.query_data('health_data', conditions, limit=100)
        
        # 验证查询被调用
        mock_connection.fetch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, database_service):
        """测试并发操作"""
        # 模拟并发数据操作
        tasks = []
        for i in range(10):
            task = database_service.store_data('health_data', {'test': f'data_{i}'})
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证所有操作都被执行
        assert len(results) == 10


class TestDatabaseServiceIntegration:
    """数据库服务集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_data_lifecycle(self):
        """测试完整的数据生命周期"""
        service = DatabaseService()
        
        # 模拟服务初始化
        with patch.multiple(service,
                          pg_pool=AsyncMock(),
                          redis_client=AsyncMock(),
                          mongo_client=AsyncMock(),
                          connected=True):
            
            # 1. 存储数据
            test_data = {
                'user_id': 'user123',
                'data_type': 'vital_signs',
                'heart_rate': 75,
                'created_at': datetime.utcnow()
            }
            
            service.pg_pool.acquire.return_value.__aenter__.return_value.fetchval.return_value = "data_id_123"
            data_id = await service.store_data('health_data', test_data)
            assert data_id == "data_id_123"
            
            # 2. 查询数据
            service.pg_pool.acquire.return_value.__aenter__.return_value.fetch.return_value = [test_data]
            results = await service.query_data('health_data', {'user_id': 'user123'})
            assert len(results) == 1
            
            # 3. 更新数据
            service.pg_pool.acquire.return_value.__aenter__.return_value.execute.return_value = "UPDATE 1"
            updated_rows = await service.update_data('health_data', {'heart_rate': 80}, {'id': data_id})
            assert updated_rows == 1
            
            # 4. 缓存数据
            await service.cache_set(f'health_data:{data_id}', test_data)
            service.redis_client.get.return_value = '{"user_id": "user123"}'
            cached_data = await service.cache_get(f'health_data:{data_id}')
            assert cached_data is not None
            
            # 5. 删除数据
            service.pg_pool.acquire.return_value.__aenter__.return_value.execute.return_value = "DELETE 1"
            deleted_rows = await service.delete_data('health_data', {'id': data_id})
            assert deleted_rows == 1
    
    @pytest.mark.asyncio
    async def test_multi_database_coordination(self):
        """测试多数据库协调"""
        service = DatabaseService()
        
        with patch.multiple(service,
                          pg_pool=AsyncMock(),
                          redis_client=AsyncMock(),
                          mongo_client=AsyncMock(),
                          connected=True):
            
            # 模拟MongoDB集合
            mock_collection = AsyncMock()
            service.mongo_client.__getitem__.return_value.__getitem__.return_value = mock_collection
            
            # 1. PostgreSQL存储主数据
            service.pg_pool.acquire.return_value.__aenter__.return_value.fetchval.return_value = "pg_id_123"
            pg_id = await service.store_data('health_data', {'user_id': 'user123'})
            
            # 2. MongoDB存储详细数据
            mock_collection.insert_one.return_value.inserted_id = "mongo_id_123"
            mongo_id = await service.mongo_insert('health_details', {'pg_id': pg_id, 'details': {}})
            
            # 3. Redis缓存关联
            await service.cache_set(f'relation:{pg_id}', mongo_id)
            
            # 验证数据关联
            assert pg_id == "pg_id_123"
            assert mongo_id == "mongo_id_123"


if __name__ == '__main__':
    pytest.main([__file__])