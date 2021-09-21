from sqlmodel import create_engine, Session, SQLModel, select
from .models import * # REQUIRED IMPORT
from typing import List
from sqlalchemy.orm.exc import NoResultFound

class Database:
    """
    Class for all interactions with the database.
    """

    # TODO

    def __init__(self):
        self.db_uri = "sqlite:///data/moderation.db"

    @property
    def engine(self):
        return create_engine(self.db_uri, echo=True)

    @property
    def session(self) -> Session:
        return Session(self.engine)

    @property
    def modutils(self):
        return ModUtility()

    def create_tables(self):
        SQLModel.metadata.create_all(self.engine)

        

class ModUtility(Database):

    """Functions associated with mod stuff"""

    # Inserting a new mod action
    def modaction_insert(self, value: ModAction) -> None:
        with self.session as session:
            session.add(value)
            session.commit()
    
    # Deleting an existing mod action (using action id)
    def modaction_delete(self, case_id: int) -> None:
        with self.session as session:
            try:
                data = session.exec(select(ModAction).where(ModAction.case_id == case_id)).one()
                session.delete(data)
                session.commit()
            except NoResultFound:
                return None

    # List all existing mod actions
    def modaction_list_all(self) -> List[ModAction]:
        with self.session as session:
            try:
                data = session.exec(select(ModAction)).all()
                return data
            except NoResultFound:
                return None

    # List mod actions associated with a particular user (Helpful for checking if user has previous infractions)
    def modaction_list_user(self, user_id: int) -> List[ModAction]:
        with self.session as session:
            try:
                data = session.exec(select(ModAction).where(ModAction.user_id == user_id)).all()
                return data
            except NoResultFound:
                return None

    # List mod actions associated with a particular mod (Helpful while staff checks)
    def modaction_list_mod(self, mod_id: int) -> List[ModAction]:
        with self.session as session:
            try:
                data = session.exec(select(ModAction).where(ModAction.user_id == mod_id)).all()
                return data
            except NoResultFound:
                return None

    def modaction_fetch(self, case_id: int):
        with self.session as session:
            try:
                data = session.exec(select(ModAction).where(ModAction.case_id == case_id)).one()
                return data
            except NoResultFound:
                return None

if __name__ == "__main__":
    # Run this file to create the tables
    db = Database()
    db.create_tables()




