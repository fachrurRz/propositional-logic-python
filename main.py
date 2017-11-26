from formula import *
from operators import *


def tree(node, arr):
    if isinstance(node, Variable):
        arr.append(node)
    if isinstance(node, BinaryOperator):
        arr.append(node.infix())
        if node.left is not None:
            tree(node.left, arr)
        if node.right is not None:
            tree(node.right, arr)
    elif isinstance(node, UnaryOperator):
        if isinstance(node, Variable):
            arr.append(node)
        if node.operand is not None:
            arr.append(node.infix())
            tree(node.operand, arr)


def get_subformula(formula):
    formula2 = LogicFormula(formula.infix())
    root = formula2.get_tree()
    sub_formulas = []

    tree(root, sub_formulas)

    for f in sub_formulas:
        print(f)


# main

if __name__ == "__main__":
    string_formula = '((( P2 -> P1 ) | ~ P2 ) <-> P2 )'
    formula = LogicFormula(string_formula)

    # sub formula
    get_subformula(formula)
    formula.generate_evaluation_table()