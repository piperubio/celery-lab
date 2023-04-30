from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab
from db import (
    Session, 
    WorkOrder, 
    WorkOrderTmp
)

celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(30.0, sync_work_order.s())

@celery_app.task
def attach_drawings(wo_id: str):
    print(f"Attaching drawings to work order {wo_id}")
    session = Session()
    wo = session.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    wo.attached_planes = "attached_planes_ok"
    session.commit()
    notify.delay(wo_id)


@celery_app.task
def notify(wo_id: str):
    print(f"Notify work order {wo_id}")

def create_work_order(
        db: Session, 
        work_order_tmp: WorkOrderTmp
) -> WorkOrder:
    work_order_created = WorkOrder(
        id=work_order_tmp.id,
        attached_planes="attached_planes",
        products_sku=work_order_tmp.products_sku,
        status="status",
        error=None,
        wo_date=work_order_tmp.wo_date
    )

    db.add(work_order_created)
    db.commit()
    return work_order_created


def get_work_orders_tmp_records_not_in_work_order_table(
        db: Session
) -> list[WorkOrderTmp]:
    last_24_hours = datetime.now() - timedelta(hours=24)
    work_orders_in_last_24h: list[WorkOrderTmp] = db.query(WorkOrderTmp).filter(
        WorkOrderTmp.wo_date >= last_24_hours
    ).all()

    work_orders_not_int_work_order_table: list[WorkOrderTmp] = []
    for work_order_tmp in work_orders_in_last_24h:
        query_work_order = db.query(WorkOrder).filter(
            WorkOrder.id == work_order_tmp.id
        ).first()

        if query_work_order is None:
            work_orders_not_int_work_order_table.append(work_order_tmp)

    return work_orders_not_int_work_order_table

@celery_app.task
def sync_work_order():
    session = Session()
    work_orders_to_store = get_work_orders_tmp_records_not_in_work_order_table(
        session
    )
    print(f"Work orders to store: {len(work_orders_to_store)}")
    for work_order_tmp in work_orders_to_store:
        wo_result = create_work_order(session, work_order_tmp)
        attach_drawings_result =  attach_drawings.delay(wo_result.id)


