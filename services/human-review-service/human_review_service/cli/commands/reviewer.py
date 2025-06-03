"""
审核员管理命令
Reviewer Management Commands

提供审核员的创建、查询、更新等管理功能
"""

import asyncio
import sys

import click
import structlog
from rich.console import Console
from rich.table import Table

from ...core.database import get_session
from ...core.models import ReviewerCreate, ReviewerStatus, ReviewerUpdate
from ...core.service import HumanReviewService

logger = structlog.get_logger(__name__)
console = Console()

@click.group()
def reviewer():
    """审核员管理命令"""
    pass

@reviewer.command()
@click.option("--name", required=True, help="审核员姓名")
@click.option("--email", required=True, help="审核员邮箱")
@click.option("--specialties", help="专业领域（逗号分隔）")
@click.option("--max-tasks", default=5, type=int, help="最大并发任务数")
def create(name: str, email: str, specialties: str, max_tasks: int):
    """创建新的审核员"""
    console.print(f"[bold blue]创建审核员 {name}...[/bold blue]")

    # 处理专业领域
    specialty_list = []
    if specialties:
        specialty_list = [s.strip() for s in specialties.split(",")]

    async def run_create():
        try:
            async with get_session() as session:
                service = HumanReviewService(session)

                reviewer_data = ReviewerCreate(
                    name=name,
                    email=email,
                    specialties=specialty_list,
                    max_concurrent_tasks=max_tasks,
                )

                reviewer = await service.create_reviewer(reviewer_data)

                console.print(f"[green]✅ 审核员创建成功[/green]")
                console.print(f"ID: {reviewer.reviewer_id}")
                console.print(f"姓名: {reviewer.name}")
                console.print(f"邮箱: {reviewer.email}")
                console.print(f"专业领域: {', '.join(reviewer.specialties)}")
                console.print(f"最大并发任务: {reviewer.max_concurrent_tasks}")

        except Exception as e:
            console.print(f"[red]❌ 创建审核员失败: {e}[/red]")
            sys.exit(1)

    try:
        asyncio.run(run_create())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1)

@reviewer.command()
@click.argument("reviewer_id")
def show(reviewer_id: str):
    """显示审核员详细信息"""
    console.print(f"[bold blue]查看审核员 {reviewer_id}...[/bold blue]")

    async def run_show():
        try:
            async with get_session() as session:
                service = HumanReviewService(session)
                reviewer = await service.get_reviewer(reviewer_id)

                if not reviewer:
                    console.print(f"[red]❌ 审核员 {reviewer_id} 不存在[/red]")
                    sys.exit(1)

                # 创建详细信息表格
                table = Table(title=f"审核员信息 - {reviewer.name}")
                table.add_column("属性", style="cyan")
                table.add_column("值", style="green")

                table.add_row("ID", reviewer.reviewer_id)
                table.add_row("姓名", reviewer.name)
                table.add_row("邮箱", reviewer.email)
                table.add_row("状态", reviewer.status.value)
                table.add_row("专业领域", ", ".join(reviewer.specialties))
                table.add_row("最大并发任务", str(reviewer.max_concurrent_tasks))
                table.add_row("当前任务数", str(reviewer.current_task_count))
                table.add_row("是否可用", "是" if reviewer.is_available else "否")
                table.add_row(
                    "创建时间", reviewer.created_at.strftime("%Y-%m-%d %H:%M:%S")
                )
                table.add_row(
                    "更新时间", reviewer.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                )

                console.print(table)

                # 获取工作负载信息
                workload = await service.get_reviewer_workload(reviewer_id)
                if workload:
                    console.print(f"\n[bold]工作负载统计:[/bold]")
                    console.print(f"待处理任务: {workload.get('pending_tasks', 0)}")
                    console.print(f"进行中任务: {workload.get('in_progress_tasks', 0)}")
                    console.print(f"已完成任务: {workload.get('completed_tasks', 0)}")

        except Exception as e:
            console.print(f"[red]❌ 查看审核员失败: {e}[/red]")
            sys.exit(1)

    try:
        asyncio.run(run_show())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1)

@reviewer.command()
@click.option(
    "--status",
    type=click.Choice(["active", "inactive", "suspended"]),
    help="按状态过滤",
)
@click.option("--specialty", help="按专业领域过滤")
@click.option("--available", is_flag=True, help="仅显示可用的审核员")
@click.option("--limit", default=20, type=int, help="显示数量限制")
def list(status: str, specialty: str, available: bool, limit: int):
    """列出审核员"""
    console.print("[bold blue]审核员列表[/bold blue]")

    async def run_list():
        try:
            async with get_session() as session:
                service = HumanReviewService(session)

                filters = {}
                if status:
                    filters["status"] = ReviewerStatus(status)
                if specialty:
                    filters["specialty"] = specialty
                if available:
                    filters["is_available"] = True

                reviewers = await service.list_reviewers(
                    filters=filters, limit=limit, offset=0
                )

                if not reviewers:
                    console.print("[yellow]未找到符合条件的审核员[/yellow]")
                    return

                # 创建审核员列表表格
                table = Table()
                table.add_column("ID", style="cyan")
                table.add_column("姓名", style="green")
                table.add_column("邮箱", style="blue")
                table.add_column("状态", style="yellow")
                table.add_column("专业领域", style="magenta")
                table.add_column("任务数", style="red")
                table.add_column("可用", style="white")

                for reviewer in reviewers:
                    table.add_row(
                        reviewer.reviewer_id[:8] + "...",
                        reviewer.name,
                        reviewer.email,
                        reviewer.status.value,
                        ", ".join(reviewer.specialties[:2])
                        + ("..." if len(reviewer.specialties) > 2 else ""),
                        f"{reviewer.current_task_count}/{reviewer.max_concurrent_tasks}",
                        "✅" if reviewer.is_available else "❌",
                    )

                console.print(table)
                console.print(f"\n共找到 {len(reviewers)} 个审核员")

        except Exception as e:
            console.print(f"[red]❌ 获取审核员列表失败: {e}[/red]")
            sys.exit(1)

    try:
        asyncio.run(run_list())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1)

@reviewer.command()
@click.argument("reviewer_id")
@click.option("--name", help="更新姓名")
@click.option("--email", help="更新邮箱")
@click.option("--specialties", help="更新专业领域（逗号分隔）")
@click.option("--max-tasks", type=int, help="更新最大并发任务数")
def update(reviewer_id: str, name: str, email: str, specialties: str, max_tasks: int):
    """更新审核员信息"""
    console.print(f"[bold blue]更新审核员 {reviewer_id}...[/bold blue]")

    async def run_update():
        try:
            async with get_session() as session:
                service = HumanReviewService(session)

                # 构建更新数据
                update_data = ReviewerUpdate()
                if name:
                    update_data.name = name
                if email:
                    update_data.email = email
                if specialties:
                    update_data.specialties = [
                        s.strip() for s in specialties.split(",")
                    ]
                if max_tasks is not None:
                    update_data.max_concurrent_tasks = max_tasks

                reviewer = await service.update_reviewer(reviewer_id, update_data)

                if not reviewer:
                    console.print(f"[red]❌ 审核员 {reviewer_id} 不存在[/red]")
                    sys.exit(1)

                console.print(f"[green]✅ 审核员更新成功[/green]")
                console.print(f"姓名: {reviewer.name}")
                console.print(f"邮箱: {reviewer.email}")
                console.print(f"专业领域: {', '.join(reviewer.specialties)}")
                console.print(f"最大并发任务: {reviewer.max_concurrent_tasks}")

        except Exception as e:
            console.print(f"[red]❌ 更新审核员失败: {e}[/red]")
            sys.exit(1)

    try:
        asyncio.run(run_update())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1)

@reviewer.command()
@click.argument("reviewer_id")
def activate(reviewer_id: str):
    """激活审核员"""
    console.print(f"[bold blue]激活审核员 {reviewer_id}...[/bold blue]")

    async def run_activate():
        try:
            async with get_session() as session:
                service = HumanReviewService(session)
                reviewer = await service.activate_reviewer(reviewer_id)

                if not reviewer:
                    console.print(f"[red]❌ 审核员 {reviewer_id} 不存在[/red]")
                    sys.exit(1)

                console.print(f"[green]✅ 审核员 {reviewer.name} 已激活[/green]")

        except Exception as e:
            console.print(f"[red]❌ 激活审核员失败: {e}[/red]")
            sys.exit(1)

    try:
        asyncio.run(run_activate())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1)

@reviewer.command()
@click.argument("reviewer_id")
def deactivate(reviewer_id: str):
    """停用审核员"""
    console.print(f"[bold blue]停用审核员 {reviewer_id}...[/bold blue]")

    async def run_deactivate():
        try:
            async with get_session() as session:
                service = HumanReviewService(session)
                reviewer = await service.deactivate_reviewer(reviewer_id)

                if not reviewer:
                    console.print(f"[red]❌ 审核员 {reviewer_id} 不存在[/red]")
                    sys.exit(1)

                console.print(f"[green]✅ 审核员 {reviewer.name} 已停用[/green]")

        except Exception as e:
            console.print(f"[red]❌ 停用审核员失败: {e}[/red]")
            sys.exit(1)

    try:
        asyncio.run(run_deactivate())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1)

@reviewer.command()
@click.argument("reviewer_id")
@click.option("--days", default=30, type=int, help="统计天数")
def performance(reviewer_id: str, days: int):
    """查看审核员绩效统计"""
    console.print(
        f"[bold blue]审核员 {reviewer_id} 绩效统计（最近{days}天）[/bold blue]"
    )

    async def run_performance():
        try:
            async with get_session() as session:
                service = HumanReviewService(session)
                performance = await service.get_reviewer_performance(reviewer_id, days)

                if performance is None:
                    console.print(f"[red]❌ 审核员 {reviewer_id} 不存在[/red]")
                    sys.exit(1)

                # 创建绩效统计表格
                table = Table(title=f"绩效统计（最近{days}天）")
                table.add_column("指标", style="cyan")
                table.add_column("值", style="green")

                table.add_row("总任务数", str(performance.get("total_tasks", 0)))
                table.add_row("已完成任务", str(performance.get("completed_tasks", 0)))
                table.add_row(
                    "平均处理时间",
                    f"{performance.get('avg_processing_time', 0):.2f} 小时",
                )
                table.add_row("质量评分", f"{performance.get('quality_score', 0):.2f}")
                table.add_row("准确率", f"{performance.get('accuracy_rate', 0):.2%}")
                table.add_row("及时完成率", f"{performance.get('on_time_rate', 0):.2%}")

                console.print(table)

        except Exception as e:
            console.print(f"[red]❌ 获取绩效统计失败: {e}[/red]")
            sys.exit(1)

    try:
        asyncio.run(run_performance())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1)

@reviewer.command()
@click.argument("reviewer_id")
@click.option("--force", is_flag=True, help="强制删除（跳过确认）")
def delete(reviewer_id: str, force: bool):
    """删除审核员"""
    console.print(f"[bold blue]删除审核员 {reviewer_id}...[/bold blue]")

    if not force:
        if not click.confirm("确定要删除这个审核员吗？此操作不可撤销。"):
            console.print("[yellow]操作已取消[/yellow]")
            return

    async def run_delete():
        try:
            async with get_session() as session:
                service = HumanReviewService(session)
                success = await service.delete_reviewer(reviewer_id)

                if not success:
                    console.print(f"[red]❌ 审核员 {reviewer_id} 不存在[/red]")
                    sys.exit(1)

                console.print(f"[green]✅ 审核员已删除[/green]")

        except Exception as e:
            console.print(f"[red]❌ 删除审核员失败: {e}[/red]")
            sys.exit(1)

    try:
        asyncio.run(run_delete())
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        sys.exit(1)
