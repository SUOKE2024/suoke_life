"""
数据库管理命令
Database Management Commands

提供数据库初始化、迁移、备份等功能
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

import click
import structlog
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from sqlalchemy import text

from ...core.config import settings
from ...core.database import get_engine, init_database, close_database

logger = structlog.get_logger(__name__)
console = Console()


@click.group()
def db():
    """数据库管理命令"""
    pass


@db.command()
@click.option(
    "--force",
    is_flag=True,
    help="强制重新初始化（删除现有数据）"
)
def init(force: bool):
    """初始化数据库"""
    console.print("[bold blue]初始化数据库...[/bold blue]")
    
    async def run_init():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("正在初始化数据库...", total=None)
                
                # 初始化数据库
                await init_database()
                
                progress.update(task, description="数据库初始化完成")
                
            console.print("[green]✅ 数据库初始化成功[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ 数据库初始化失败: {e}[/red]")
            sys.exit(1)
        finally:
            await close_database()
    
    try:
        asyncio.run(run_init())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1)


@db.command()
def status():
    """检查数据库状态"""
    console.print("[bold blue]检查数据库状态...[/bold blue]")
    
    async def check_status():
        try:
            async with get_engine().begin() as conn:
                # 检查数据库连接
                result = await conn.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    console.print("[green]✅ 数据库连接正常[/green]")
                
                # 检查表是否存在
                tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
                """
                result = await conn.execute(text(tables_query))
                tables = [row[0] for row in result.fetchall()]
                
                if tables:
                    console.print(f"[green]✅ 发现 {len(tables)} 个表[/green]")
                    for table in tables:
                        console.print(f"  - {table}")
                else:
                    console.print("[yellow]⚠️ 未发现任何表，可能需要初始化[/yellow]")
                
        except Exception as e:
            console.print(f"[red]❌ 数据库连接失败: {e}[/red]")
            sys.exit(1)
    
    try:
        asyncio.run(check_status())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1)


@db.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="备份文件路径"
)
def backup(output: str):
    """备份数据库"""
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"backup_{timestamp}.sql"
    
    console.print(f"[bold blue]备份数据库到 {output}...[/bold blue]")
    
    # 这里应该实现实际的备份逻辑
    # 由于这需要依赖具体的数据库类型，这里只是示例
    console.print("[yellow]⚠️ 备份功能需要根据具体数据库类型实现[/yellow]")


@db.command()
@click.argument("backup_file", type=click.Path(exists=True))
@click.option(
    "--force",
    is_flag=True,
    help="强制恢复（覆盖现有数据）"
)
def restore(backup_file: str, force: bool):
    """从备份文件恢复数据库"""
    console.print(f"[bold blue]从 {backup_file} 恢复数据库...[/bold blue]")
    
    if not force:
        if not click.confirm("这将覆盖现有数据，确定要继续吗？"):
            console.print("[yellow]操作已取消[/yellow]")
            return
    
    # 这里应该实现实际的恢复逻辑
    console.print("[yellow]⚠️ 恢复功能需要根据具体数据库类型实现[/yellow]")


@db.command()
def migrate():
    """执行数据库迁移"""
    console.print("[bold blue]执行数据库迁移...[/bold blue]")
    
    # 这里应该集成Alembic或其他迁移工具
    console.print("[yellow]⚠️ 迁移功能需要集成Alembic实现[/yellow]")


@db.command()
@click.option(
    "--table",
    help="指定表名（可选）"
)
def reset(table: str):
    """重置数据库或指定表"""
    if table:
        console.print(f"[bold blue]重置表 {table}...[/bold blue]")
        if not click.confirm(f"确定要清空表 {table} 的所有数据吗？"):
            console.print("[yellow]操作已取消[/yellow]")
            return
    else:
        console.print("[bold blue]重置整个数据库...[/bold blue]")
        if not click.confirm("确定要删除所有数据并重新初始化数据库吗？"):
            console.print("[yellow]操作已取消[/yellow]")
            return
    
    async def run_reset():
        try:
            if table:
                # 清空指定表
                async with get_engine().begin() as conn:
                    await conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                console.print(f"[green]✅ 表 {table} 已重置[/green]")
            else:
                # 重置整个数据库
                await init_database()
                console.print("[green]✅ 数据库已重置[/green]")
                
        except Exception as e:
            console.print(f"[red]❌ 重置失败: {e}[/red]")
            sys.exit(1)
        finally:
            await close_database()
    
    try:
        asyncio.run(run_reset())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1)


@db.command()
def seed():
    """填充测试数据"""
    console.print("[bold blue]填充测试数据...[/bold blue]")
    
    async def run_seed():
        try:
            from ...core.service import HumanReviewService
            from ...core.models import ReviewerCreate, ReviewType
            from ...core.database import get_session
            
            async with get_session() as session:
                service = HumanReviewService(session)
                
                # 创建测试审核员
                test_reviewers = [
                    ReviewerCreate(
                        name="张医生",
                        email="zhang@example.com",
                        specialties=["中医诊断", "方剂学"],
                        max_concurrent_tasks=5
                    ),
                    ReviewerCreate(
                        name="李医生", 
                        email="li@example.com",
                        specialties=["西医诊断", "内科"],
                        max_concurrent_tasks=3
                    ),
                    ReviewerCreate(
                        name="王医生",
                        email="wang@example.com", 
                        specialties=["营养学", "健康管理"],
                        max_concurrent_tasks=8
                    )
                ]
                
                created_count = 0
                for reviewer_data in test_reviewers:
                    try:
                        reviewer = await service.create_reviewer(reviewer_data)
                        created_count += 1
                        console.print(f"  ✅ 创建审核员: {reviewer.name}")
                    except Exception as e:
                        console.print(f"  ⚠️ 跳过审核员 {reviewer_data.name}: {e}")
                
                console.print(f"[green]✅ 成功创建 {created_count} 个测试审核员[/green]")
                
        except Exception as e:
            console.print(f"[red]❌ 填充测试数据失败: {e}[/red]")
            sys.exit(1)
    
    try:
        asyncio.run(run_seed())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1) 