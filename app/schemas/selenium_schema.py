from pydantic import BaseModel


class SeleniumScript(BaseModel):
    test_case_id: str
    file_name: str
    code: str


class SeleniumScriptList(BaseModel):
    scripts: list[SeleniumScript]