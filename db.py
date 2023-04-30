import datetime
from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.sqlite import JSON

Base = declarative_base()

engine = create_engine("sqlite+pysqlite:///./mydb.sqlite", echo=True)
Session = sessionmaker(bind=engine)

class WorkOrderTmp(Base):
    __tablename__ = 'work_order_tmp'
    id = Column(String(50), primary_key=True, nullable=False)
    status = Column(String(100), nullable=False)
    products_sku = Column(JSON, nullable=False)
    wo_date = Column(DateTime, nullable=False)


class WorkOrder(Base):
    __tablename__ = 'work_order'
    id = Column(String(50), primary_key=True, nullable=False)
    products_sku = Column(JSON, nullable=False)
    status = Column(String(100), nullable=False)
    attached_planes = Column(String(100), nullable=False)
    error = Column(JSON, nullable=True)
    wo_date = Column(DateTime, nullable=False)
    created_at = Column(
        DateTime, 
        nullable=False, 
        default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, 
        nullable=False,
        default=datetime.datetime.utcnow, 
        onupdate=datetime.datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "attached_planes": self.attached_planes,
            "products_sku": self.products_sku,
            "status": self.status,
            "error": self.error,
            "wo_date": self.wo_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


