"""计算器工具 - 执行数学运算"""

import math
import ast
import operator
from typing import Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    """计算器输入"""
    expression: str = Field(description="数学表达式，如 '2 + 3 * 4' 或 'sqrt(16) + sin(pi/2)'")


SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

SAFE_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "max": max,
    "min": min,
    "sum": sum,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "pi": math.pi,
    "e": math.e,
    "floor": math.floor,
    "ceil": math.ceil,
}

SAFE_CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}


def _safe_eval(expr: str) -> float:
    tree = ast.parse(expr.strip(), mode="eval")

    def _eval_node(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _eval_node(node.body)
        elif isinstance(node, ast.Constant):
            return float(node.value)
        elif isinstance(node, ast.Name):
            name = node.id
            if name in SAFE_CONSTANTS:
                return SAFE_CONSTANTS[name]
            raise NameError(f"未知变量: {name}")
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise NotImplementedError(f"不支持的运算符: {op_type.__name__}")
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            return SAFE_OPERATORS[op_type](left, right)
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise NotImplementedError(f"不支持的运算符: {op_type.__name__}")
            return SAFE_OPERATORS[op_type](_eval_node(node.operand))
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name and func_name in SAFE_FUNCTIONS:
                args = [_eval_node(a) for a in node.args]
                return SAFE_FUNCTIONS[func_name](*args)
            raise NameError(f"未知函数: {func_name}")
        else:
            raise NotImplementedError(f"不支持的语法: {type(node).__name__}")

    return _eval_node(tree)


class CalculatorTool(BaseTool):
    """执行数学计算的安全计算器"""

    name: str = "calculator"
    description: str = """执行数学计算，支持四则运算、幂、三角函数等。
输入一个数学表达式，如 '2 + 3 * 4' 或 'sqrt(16) + sin(pi/2)'。
支持: +, -, *, /, //, %, **, sqrt, sin, cos, tan, log, exp, abs, round"""
    args_schema: Type[BaseModel] = CalculatorInput

    def _run(self, expression: str) -> str:
        try:
            result = _safe_eval(expression)
            return str(result)
        except Exception as e:
            return f"计算错误: {e!s}"


calculator_tool = CalculatorTool()
