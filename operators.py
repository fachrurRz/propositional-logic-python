class Operator(object):
    def __init__(self, kind):
        self.kind = kind

    def __repr__(self):
        return "Operator({})".format(self.kind)

    def __str__(self):
        return self.kind


class UnaryOperator(Operator):
    def __init__(self, kind):
        super().__init__(kind)
        self.operand = None

    def infix(self):
        return "{}{}".format(self.kind, self.operand.infix())


class NegationOperator(UnaryOperator):
    def __init__(self):
        super().__init__("~")

    def precedence(self):
        return 0

    def evaluate(self):
        return not self.operand.evaluate()


class BinaryOperator(Operator):
    def __init__(self, kind):
        super().__init__(kind)
        self.left = None
        self.right = None

    def infix(self):
        return "({} {} {})".format(self.left.infix(), self.kind, self.right.infix())


class ConjunctionOperator(BinaryOperator):
    def __init__(self):
        super().__init__("&")

    def precedence(self):
        return 1

    def evaluate(self):
        return self.left.evaluate() and self.right.evaluate()


class DisjunctionOperator(BinaryOperator):
    def __init__(self):
        super().__init__("|")

    def precedence(self):
        return 1

    def evaluate(self):
        return self.left.evaluate() or self.right.evaluate()


class ImplicationOperator(BinaryOperator):
    def __init__(self):
        super().__init__("->")

    def precedence(self):
        return 2

    def evaluate(self):
        return not self.left.evaluate() or self.right.evaluate()

    def infix(self):
        return "({} {} {} {})".format('~', self.left.infix(), '|', self.right.infix())

class BiimplicationOperator(BinaryOperator):
    def __init__(self):
        super().__init__("<->")

    def precedence(self):
        return 2

    def evaluate(self):
        left = self.left.evaluate() and self.right.evaluate()
        right = not self.left.evaluate() and not self.right.evaluate()
        return left or right

    def infix(self):
        return "({} {} {} {} {} {} {} {} {} {} {} {} {})".\
            format('(', '~', self.left.infix(), '|', self.right.infix(), ')', '&',
                   '(', '~', self.right.infix(), '|', self.left.infix(), ')')

class EquivalenceOperator(BinaryOperator):
    def __init__(self):
        super().__init__("=")

    def precedence(self):
        return 3

    def evaluate(self):
        return self.left.evaluate() == self.right.evaluate()


class LeftParen:
    def __repr__(self):
        return "("


class RightParen:
    def __repr__(self):
        return ")"
