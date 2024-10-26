from pydantic import BaseModel, Field
from typing import List, Optional

class Action(BaseModel):
    type: str
    text: Optional[str] = None
    tag_name: Optional[str] = None
    disabled_class: Optional[str] = None
    ul_id: Optional[str] = None

    element_id: Optional[str] = None
    element_name: Optional[str] = None 
    element_class: Optional[str] = None

    iframe_name: Optional[str] = None  
    iframe_id: Optional[str] = None  
    iframe_index: Optional[str] = None  

    parse_num: Optional[int] = Field(default=None, description="Parser number for check_time actions")
    identifier: Optional[str] = None

class SiteConfig(BaseModel):
    title: str
    url: str
    click_center: bool
    date: str
    actions: List[Action]
