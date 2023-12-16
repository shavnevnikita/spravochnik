from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import date

Base = declarative_base()


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), default="")
    description = Column(String, default="")
    budget = Column(Numeric(scale=2), default=0)
    professors = relationship("Professor", back_populates="department")

    def __getitem__(self, arg):
        return eval(f"self.{self.__table__.columns.keys()[arg]}")

    def __setitem__(self, arg, arg1):
        exec(f"self.{self.__table__.columns.keys()[arg]} = arg1")


class Professor(Base):
    __tablename__ = "professors"
    id = Column(Integer, primary_key=True)
    fio = Column(String(60), default="")
    birth_date = Column(Date, default=date.fromisoformat("2002-12-27"))
    social_rating = Column(Integer, default=0)
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="professors")

    def __getitem__(self, arg):
        return eval(f"self.{self.__table__.columns.keys()[arg]}")

    def __setitem__(self, arg, arg1):
        exec(f"self.{self.__table__.columns.keys()[arg]} = arg1")


if __name__ == "__main__":
    engine = create_engine("sqlite:///spravochnik.db")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(
        Department(
            name="Кафедра компьютерных технологий и систем",
            description="Лучшая кафедра на свете (лене)",
            budget=100.10,
        )
    )
    session.add(
        Professor(
            fio="Дайняк Виктор Владимирович",
            birth_date=date.fromisoformat("2007-08-08"),
            social_rating=99,
            department_id=1,
        )
    )
    session.commit()
