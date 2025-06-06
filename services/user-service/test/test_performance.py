"""
test_performance - 索克生活项目模块
"""

        import gc
        import psutil
        import random
from concurrent.futures import ThreadPoolExecutor
from internal.model.user import CreateUserRequest, UpdateUserRequest, BindDeviceRequest
from internal.repository.sqlite_user_repository import SQLiteUserRepository
from internal.service.user_service import UserService
from uuid import uuid4
import asyncio
import os
import pytest
import pytest_asyncio
import statistics
import tempfile
import time

"""
User-Service 性能和压力测试
"""



class TestUserServicePerformance:
    """User-Service 性能测试"""
    
    @pytest_asyncio.fixture
    async def repository(self):
        """创建测试repository"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        repo = SQLiteUserRepository(temp_db.name)
        await repo.initialize()
        
        yield repo
        
        # 清理
        try:
            os.unlink(temp_db.name)
        except:
            pass
    
    @pytest_asyncio.fixture
    async def user_service(self, repository):
        """创建用户服务实例"""
        return UserService(repository)
    
    @pytest.mark.asyncio
    async def test_bulk_user_creation_performance(self, user_service):
        """测试批量用户创建性能"""
        user_count = 100
        batch_size = 10
        
        print(f"\n开始批量创建 {user_count} 个用户测试...")
        
        start_time = time.time()
        created_users = []
        
        # 分批创建用户
        for batch_start in range(0, user_count, batch_size):
            batch_tasks = []
            
            for i in range(batch_start, min(batch_start + batch_size, user_count)):
                user_data = {
                    "username": f"perfuser{i:04d}",
                    "email": f"perf{i:04d}@suoke.life",
                    "password": "SecurePass123!",
                    "full_name": f"性能测试用户 {i}"
                }
                
                request = CreateUserRequest(**user_data)
                batch_tasks.append(user_service.create_user(request))
            
            batch_results = await asyncio.gather(*batch_tasks)
            created_users.extend(batch_results)
            
            print(f"完成批次 {batch_start//batch_size + 1}/{(user_count-1)//batch_size + 1}")
        
        total_time = time.time() - start_time
        
        # 性能指标
        avg_time_per_user = total_time / user_count * 1000  # 毫秒
        users_per_second = user_count / total_time
        
        print(f"✓ 批量创建性能测试结果:")
        print(f"  - 总用户数: {user_count}")
        print(f"  - 总耗时: {total_time:.2f}秒")
        print(f"  - 平均每用户: {avg_time_per_user:.2f}毫秒")
        print(f"  - 每秒创建: {users_per_second:.2f}用户/秒")
        
        # 性能断言
        assert avg_time_per_user < 100  # 每用户创建时间不超过100ms
        assert users_per_second > 5     # 每秒至少创建5个用户
        
        return created_users
    
    @pytest.mark.asyncio
    async def test_concurrent_read_performance(self, user_service):
        """测试并发读取性能"""
        # 先创建一些用户
        users = []
        for i in range(20):
            user_data = {
                "username": f"readuser{i:03d}",
                "email": f"read{i:03d}@suoke.life",
                "password": "SecurePass123!"
            }
            request = CreateUserRequest(**user_data)
            user = await user_service.create_user(request)
            users.append(user)
        
        print(f"\n开始并发读取性能测试...")
        
        # 测试不同并发级别
        concurrency_levels = [1, 5, 10, 20]
        results = {}
        
        for concurrency in concurrency_levels:
            read_times = []
            
            # 进行多轮测试
            for round_num in range(3):
                start_time = time.time()
                
                # 创建并发读取任务
                tasks = []
                for _ in range(concurrency):
                    user = users[_ % len(users)]
                    tasks.append(user_service.get_user(str(user.user_id)))
                
                await asyncio.gather(*tasks)
                
                round_time = time.time() - start_time
                read_times.append(round_time)
            
            avg_time = statistics.mean(read_times)
            min_time = min(read_times)
            max_time = max(read_times)
            
            results[concurrency] = {
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'requests_per_second': concurrency / avg_time
            }
        
        # 输出结果
        print(f"✓ 并发读取性能测试结果:")
        for concurrency, metrics in results.items():
            print(f"  - 并发数 {concurrency:2d}: "
                  f"平均 {metrics['avg_time']*1000:.1f}ms, "
                  f"最小 {metrics['min_time']*1000:.1f}ms, "
                  f"最大 {metrics['max_time']*1000:.1f}ms, "
                  f"{metrics['requests_per_second']:.1f} req/s")
        
        # 性能断言
        assert results[1]['avg_time'] < 0.1    # 单个请求不超过100ms
        assert results[10]['avg_time'] < 0.5   # 10并发不超过500ms
    
    @pytest.mark.asyncio
    async def test_mixed_workload_performance(self, user_service):
        """测试混合工作负载性能"""
        print(f"\n开始混合工作负载性能测试...")
        
        # 先创建一些基础用户
        base_users = []
        for i in range(10):
            user_data = {
                "username": f"mixuser{i:03d}",
                "email": f"mix{i:03d}@suoke.life",
                "password": "SecurePass123!"
            }
            request = CreateUserRequest(**user_data)
            user = await user_service.create_user(request)
            base_users.append(user)
        
        # 定义不同类型的操作
        async def create_operation(op_id):
            user_data = {
                "username": f"newuser{op_id}",
                "email": f"new{op_id}@suoke.life",
                "password": "SecurePass123!"
            }
            request = CreateUserRequest(**user_data)
            return await user_service.create_user(request)
        
        async def read_operation(op_id):
            user = base_users[op_id % len(base_users)]
            return await user_service.get_user(str(user.user_id))
        
        async def update_operation(op_id):
            user = base_users[op_id % len(base_users)]
            update_request = UpdateUserRequest(
                full_name=f"更新用户 {op_id}"
            )
            return await user_service.update_user(str(user.user_id), update_request)
        
        async def device_bind_operation(op_id):
            user = base_users[op_id % len(base_users)]
            device_request = BindDeviceRequest(
                device_id=f"device-{op_id}",
                device_type="smartphone",
                device_name=f"设备 {op_id}"
            )
            return await user_service.bind_device(str(user.user_id), device_request)
        
        # 混合工作负载：60%读取，20%创建，15%更新，5%设备绑定
        operations = []
        total_ops = 100
        
        for i in range(total_ops):
            if i < 60:  # 60% 读取
                operations.append(('read', read_operation, i))
            elif i < 80:  # 20% 创建
                operations.append(('create', create_operation, i))
            elif i < 95:  # 15% 更新
                operations.append(('update', update_operation, i))
            else:  # 5% 设备绑定
                operations.append(('device', device_bind_operation, i))
        
        # 随机打乱操作顺序
        random.shuffle(operations)
        
        # 执行混合工作负载
        start_time = time.time()
        
        tasks = []
        for op_type, op_func, op_id in operations:
            tasks.append(op_func(op_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # 统计结果
        successful_ops = sum(1 for r in results if not isinstance(r, Exception))
        failed_ops = len(results) - successful_ops
        
        print(f"✓ 混合工作负载性能测试结果:")
        print(f"  - 总操作数: {total_ops}")
        print(f"  - 成功操作: {successful_ops}")
        print(f"  - 失败操作: {failed_ops}")
        print(f"  - 总耗时: {total_time:.2f}秒")
        print(f"  - 平均每操作: {total_time/total_ops*1000:.2f}毫秒")
        print(f"  - 操作吞吐量: {total_ops/total_time:.2f} ops/秒")
        
        # 性能断言
        assert successful_ops >= total_ops * 0.95  # 至少95%成功率
        assert total_time < 30  # 总时间不超过30秒
        assert total_ops/total_time > 3  # 每秒至少3个操作
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, user_service):
        """测试负载下的内存使用情况"""
        
        print(f"\n开始内存使用测试...")
        
        # 获取初始内存使用
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"初始内存使用: {initial_memory:.2f} MB")
        
        # 创建大量用户
        users = []
        batch_size = 50
        total_users = 500
        
        for batch_start in range(0, total_users, batch_size):
            batch_tasks = []
            
            for i in range(batch_start, min(batch_start + batch_size, total_users)):
                user_data = {
                    "username": f"memuser{i:04d}",
                    "email": f"mem{i:04d}@suoke.life",
                    "password": "SecurePass123!",
                    "full_name": f"内存测试用户 {i}"
                }
                
                request = CreateUserRequest(**user_data)
                batch_tasks.append(user_service.create_user(request))
            
            batch_users = await asyncio.gather(*batch_tasks)
            users.extend(batch_users)
            
            # 检查内存使用
            current_memory = process.memory_info().rss / 1024 / 1024
            print(f"创建 {len(users)} 用户后内存使用: {current_memory:.2f} MB "
                  f"(增长: {current_memory - initial_memory:.2f} MB)")
        
        # 执行大量读取操作
        print("执行大量读取操作...")
        read_tasks = []
        for _ in range(1000):
            user = users[_ % len(users)]
            read_tasks.append(user_service.get_user(str(user.user_id)))
        
        await asyncio.gather(*read_tasks)
        
        after_reads_memory = process.memory_info().rss / 1024 / 1024
        print(f"大量读取后内存使用: {after_reads_memory:.2f} MB")
        
        # 强制垃圾回收
        gc.collect()
        
        after_gc_memory = process.memory_info().rss / 1024 / 1024
        print(f"垃圾回收后内存使用: {after_gc_memory:.2f} MB")
        
        # 内存使用断言
        memory_growth = after_gc_memory - initial_memory
        memory_per_user = memory_growth / total_users * 1024  # KB per user
        
        print(f"✓ 内存使用测试结果:")
        print(f"  - 总内存增长: {memory_growth:.2f} MB")
        print(f"  - 每用户内存: {memory_per_user:.2f} KB")
        
        # 内存使用不应该过高
        assert memory_growth < 100  # 总增长不超过100MB
        assert memory_per_user < 200  # 每用户不超过200KB
    
    @pytest.mark.asyncio
    async def test_database_connection_stress(self, user_service):
        """测试数据库连接压力"""
        print(f"\n开始数据库连接压力测试...")
        
        # 创建大量并发数据库操作
        concurrent_operations = 100
        operations_per_task = 10
        
        async def database_stress_task(task_id):
            """单个压力测试任务"""
            results = []
            
            for op_id in range(operations_per_task):
                try:
                    # 创建用户
                    user_data = {
                        "username": f"stress{task_id}_{op_id}",
                        "email": f"stress{task_id}_{op_id}@suoke.life",
                        "password": "SecurePass123!"
                    }
                    request = CreateUserRequest(**user_data)
                    user = await user_service.create_user(request)
                    
                    # 立即读取
                    retrieved_user = await user_service.get_user(str(user.user_id))
                    
                    # 更新用户
                    update_request = UpdateUserRequest(
                        full_name=f"压力测试用户 {task_id}_{op_id}"
                    )
                    updated_user = await user_service.update_user(str(user.user_id), update_request)
                    
                    results.append(True)
                    
                except Exception as e:
                    print(f"任务 {task_id} 操作 {op_id} 失败: {e}")
                    results.append(False)
            
            return results
        
        # 启动所有压力测试任务
        start_time = time.time()
        
        stress_tasks = []
        for task_id in range(concurrent_operations):
            stress_tasks.append(database_stress_task(task_id))
        
        all_results = await asyncio.gather(*stress_tasks)
        
        total_time = time.time() - start_time
        
        # 统计结果
        total_operations = concurrent_operations * operations_per_task
        successful_operations = sum(sum(task_results) for task_results in all_results)
        failed_operations = total_operations - successful_operations
        
        success_rate = successful_operations / total_operations * 100
        operations_per_second = total_operations / total_time
        
        print(f"✓ 数据库连接压力测试结果:")
        print(f"  - 并发任务数: {concurrent_operations}")
        print(f"  - 每任务操作数: {operations_per_task}")
        print(f"  - 总操作数: {total_operations}")
        print(f"  - 成功操作: {successful_operations}")
        print(f"  - 失败操作: {failed_operations}")
        print(f"  - 成功率: {success_rate:.2f}%")
        print(f"  - 总耗时: {total_time:.2f}秒")
        print(f"  - 操作吞吐量: {operations_per_second:.2f} ops/秒")
        
        # 压力测试断言
        assert success_rate >= 95  # 至少95%成功率
        assert operations_per_second > 50  # 每秒至少50个操作
        assert total_time < 60  # 总时间不超过60秒 