import ast


class CodeValidationService:

    @staticmethod
    def validate(code: str):

        try:
            ast.parse(code)

            return {
                "valid": True,
                "error": None
            }

        except SyntaxError as e:

            return {
                "valid": False,
                "error": str(e)
            }