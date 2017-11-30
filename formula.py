from operators import *
import sys
#
# sys.stdout.write('hi there')
# sys.stdout.write('Bob here.')

class Variable:
    def parse(input_string):
        name = ""
        consumed = 0
        for ch in input_string:
            if ch.isalnum():
                name += ch
                consumed += 1
            else:
                break
        if consumed == 0:
            raise Exception("Not a valid input string")
        return (Variable(name), input_string[consumed:])

    def __init__(self, name):
        self.name = name
        self.value = None

    def __repr__(self):
        return "Variable({})".format(self.name)

    def __str__(self):
        return self.name

    def evaluate(self):
        if self.value == None:
            raise Exception("Trying to evaulate a variable without any value")
        else:
            return self.value

    def infix(self):
        return self.name


class LogicFormula:
    def __init__(self, string):
        tokens = self._tokenize(string)
        self._parse(tokens)
        self.variables.sort(key=lambda v: v.name)

    def _tokenize(self, formula):
        position = 0
        symbol_map = {
            "~": NegationOperator,
            "&": ConjunctionOperator,
            "|": DisjunctionOperator,
            "->": ImplicationOperator,
            "<->": BiimplicationOperator,
            "=": EquivalenceOperator,
            "(": LeftParen,
            ")": RightParen
        }
        symbols = symbol_map.keys()
        tokens = []
        while len(formula) != 0:
            if formula[0].isalnum():
                token, formula = Variable.parse(formula)
                token.position = position
                position += len(token.name)
                tokens.append(token)
            elif formula[0] in symbols:
                token = symbol_map[formula[0]]()
                token.position = position
                tokens.append(token)
                position += 1
                formula = formula[1:]
            elif formula[0:2] in symbols:
                token = symbol_map[formula[0:2]]()
                token.position = position
                tokens.append(token)
                position += 1
                formula = formula[2:]
            elif formula[0:3] in symbols:
                token = symbol_map[formula[0:3]]()
                token.position = position
                tokens.append(token)
                position += 1
                formula = formula[3:]
            elif formula[0] == " ":
                formula = formula[1:]
                position += 1
            else:
                raise Exception("Unexpected symbol at position {}".format(position))
        return tokens

    def _parse(self, tokens):
        variables = {}
        out = []
        operators = []
        for token in tokens:
            if isinstance(token, Variable):
                if token.name in variables:
                    out.append(variables[token.name])
                else:
                    variables[token.name] = token
                    out.append(token)
            elif isinstance(token, Operator):
                while len(operators) > 0 and isinstance(operators[-1], Operator) and operators[-1].precedence() <= token.precedence():
                    self._add_operator(out, operators.pop(), False)
                operators.append(token)
            elif isinstance(token, LeftParen):
                operators.append(token)
            elif isinstance(token, RightParen):
                stack_token = operators.pop()
                while not isinstance(stack_token, LeftParen):
                    self._add_operator(out, stack_token, False)
                    stack_token = operators.pop()
            else:
                raise Exception("Unknown token")

        # print("Popping")
        for operator in operators[::-1]:
            if isinstance(operator, Operator):
                self._add_operator(out, operator, False)
            else:
                raise Exception("Mismatched parens")
                # print(out, operators)

        self.root = out.pop()
        if len(out) != 0:
            raise Exception("There are variables that are not consumed by any operator in the formula.")
        self.variables = list(variables.values())

    def evaluate(self):
        return self.root.evaluate()

    def _add_operator(self, stack, operator, reverse_operands):
        if isinstance(operator, BinaryOperator):
            if len(stack) < 2:
                raise Exception(
                    "Binary operator at position {} doesn't have enough arguments".format(operator.position))
            operator.right, operator.left = stack.pop(), stack.pop()
            if reverse_operands:
                operator.right, operator.left = operator.left, operator.right
        elif isinstance(operator, UnaryOperator):
            if len(stack) < 1:
                raise Exception("Unary operator at position {} doesn't have an argument".format(operator.position))
            operator.operand = stack.pop()
        else:
            raise Exception("Not a binary or unary operator")
        stack.append(operator)

    def digraph(self):
        output = ["digraph {"]
        output.extend(self._node_graph(self.root, 1))
        output.append("}\n")
        return "\n".join(output)

    def _node_graph(self, node, ident):
        output = []
        output.append("{} [label = \"{}\"]".format(ident, node))
        if isinstance(node, BinaryOperator):
            output.append("{} -> {}".format(ident, ident * 3))
            output.append("{} -> {}".format(ident, (ident + 1) * 3))
            output.extend(self._node_graph(node.left, ident * 3))
            output.extend(self._node_graph(node.right, (ident + 1) * 3))
        elif isinstance(node, UnaryOperator):
            output.append("{} -> {}".format(ident, ident * 3))
            output.extend(self._node_graph(node.operand, ident * 3))
        return output

    def generate_evaluation_table(self):
        formatString = "{{:0{}b}}: {{}}".format(len(self.variables))
        results = self.evaluate_all()
        # if all(results.values()):
        #     print("Formula is a tautology")
        # elif any(results.values()):
        #     print("Formula is satisfiable")
        # else:
        #     print("Formula is a contradiction")
        for x in self.variables:
            if isinstance(x, Variable):
                sys.stdout.write(str(x) + '   ')
        sys.stdout.write('F \n')

        for k, v in results.items():
            to_print = formatString.format(k, v)
            flag = False
            for c in to_print:
                if c.isalnum():
                    if flag:
                        if c == 'F':
                            sys.stdout.write('0')
                        else:
                            sys.stdout.write('1')
                        sys.stdout.write('\n')
                        break;
                    sys.stdout.write(c + '    ')
                else:
                    flag = True

    def evaluate_all(self):
        evaluation_results = {}
        for i in range(0, 2 ** len(self.variables)):
            evaluation_results[i] = self.evaluate_with_bitset(i)
        return evaluation_results

    def evaluate_with_bitset(self, bitset):
        values = []
        bitset += 2 ** len(self.variables)
        while bitset != 1:
            values.append(bitset % 2 == True)
            bitset //= 2
        values.reverse()
        return self.evaluate_with_values(values)

    def evaluate_with_values(self, values):
        if len(values) != len(self.variables):
            raise Exception("Incorrect variable value count when evaluating.")
        for (i, value) in enumerate(values):
            self.variables[i].value = value
        return self.evaluate()

    def infix(self):
        return "({})".format(self.root.infix())

    def get_tree(self):
        string_formula = self.infix()
        self.__init__(string_formula)
        return self.root