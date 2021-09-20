from sqlmodel import SQLModel, Field
from typing import Optional
import datetime

class ModAction(SQLModel, table=True):
    """
    ModAction
    --------
    Fields:
        id: Unique warn id (will be used for handling cases)
        user_id: ID of the user
        mod_id: ID of the moderator responsible
        action: Type of action (warn/mute/kick/ban)
        reason: Reason of the action
        date: Date of the action issued
        duration: Duration of the action (in seconds)
    --------
    """

    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int
    mod_id: int
    action: str
    reason: str = Field(default="No reason given.")
    date: datetime.datetime = Field(default=datetime.datetime.now())
    duration: int
    


