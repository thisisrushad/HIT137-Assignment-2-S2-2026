"""
HIT137 Assignment 2 - Question 2
File: evaluator.py

Function-based recursive-descent expression evaluator.
No classes are used.
"""

import os


def format_number(value: float) -> str:
    """Format numbers for tree/result output."""
    if float(value).is_integer():
        return str(int(value))

    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return text


def tokenise(expression: str):
    """
    Convert an expression string into a list of tokens.

    Each token is a dictionary with:
      type: NUM, OP, LPAREN, RPAREN, END
      value: token text (END has an empty value)
    """
    tokens = []
    i = 0

    while i < len(expression):
        ch = expression[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit():
            start = i
            while i < len(expression) and expression[i].isdigit():
                i += 1

            if i < len(expression) and expression[i] == ".":
                i += 1
                decimal_start = i

                while i < len(expression) and expression[i].isdigit():
                    i += 1

                # A decimal point must be followed by at least one digit.
                if decimal_start == i:
                    raise ValueError("Invalid number")

            tokens.append({
                "type": "NUM",
                "value": expression[start:i]
            })
            continue

        if ch in "+-*/%^":
            tokens.append({
                "type": "OP",
                "value": ch
            })
            i += 1
            continue

        if ch == "(":
            tokens.append({
                "type": "LPAREN",
                "value": ch
            })
            i += 1
            continue

        if ch == ")":
            tokens.append({
                "type": "RPAREN",
                "value": ch
            })
            i += 1
            continue

        raise ValueError("Invalid character")

    tokens.append({"type": "END", "value": ""})
    return tokens


def token_string(tokens) -> str:
    """Return the token list in the assignment's required display format."""
    parts = []

    for token in tokens:
        if token["type"] == "END":
            parts.append("[END]")
        else:
            parts.append(f'[{token["type"]}:{token["value"]}]')

    return " ".join(parts)


def current_token(tokens, position):
    """Safely return the token at position."""
    if position >= len(tokens):
        return {"type": "END", "value": ""}
    return tokens[position]


def parse_expression(tokens, position):
    """Level 1: + and - (left associative)."""
    left, position = parse_term(tokens, position)

    while True:
        token = current_token(tokens, position)

        if token["type"] == "OP" and token["value"] in ("+", "-"):
            operator = token["value"]
            right, position = parse_term(tokens, position + 1)
            left = {
                "kind": "binary",
                "op": operator,
                "left": left,
                "right": right
            }
        else:
            break

    return left, position


def starts_implicit_factor(token, left_node):
    """
    Decide whether the next token starts implicit multiplication.

    Valid examples include:
      2(3+4)
      (2+3)(4+5)
      (2+3)4

    Two adjacent number literals such as "2 3" are deliberately invalid.
    """
    if token["type"] == "LPAREN":
        return True

    if token["type"] == "NUM" and left_node.get("_ends_parenthesis", False):
        return True

    return False


def parse_term(tokens, position):
    """Level 2: *, /, %, and implicit multiplication (left associative)."""
    left, position = parse_unary(tokens, position)

    while True:
        token = current_token(tokens, position)

        if token["type"] == "OP" and token["value"] in ("*", "/", "%"):
            operator = token["value"]
            right, position = parse_unary(tokens, position + 1)

            left = {
                "kind": "binary",
                "op": operator,
                "left": left,
                "right": right,
                "_ends_parenthesis": right.get("_ends_parenthesis", False)
            }
            continue

        if starts_implicit_factor(token, left):
            right, position = parse_unary(tokens, position)

            left = {
                "kind": "binary",
                "op": "*",
                "left": left,
                "right": right,
                "_ends_parenthesis": right.get("_ends_parenthesis", False)
            }
            continue

        break

    return left, position


def parse_unary(tokens, position):
    """Level 3: unary negation."""
    token = current_token(tokens, position)

    if token["type"] == "OP" and token["value"] == "-":
        operand, new_position = parse_unary(tokens, position + 1)

        return {
            "kind": "unary",
            "op": "neg",
            "operand": operand,
            "_ends_parenthesis": operand.get("_ends_parenthesis", False)
        }, new_position

    if token["type"] == "OP" and token["value"] == "+":
        raise ValueError("Unary plus is not supported")

    return parse_power(tokens, position)


def parse_power(tokens, position):
    """Level 4: exponentiation, right associative."""
    left, position = parse_primary(tokens, position)
    token = current_token(tokens, position)

    if token["type"] == "OP" and token["value"] == "^":
        # Parse through unary on the right so 2^-3 is valid while chained
        # exponentiation remains right-associative.
        right, position = parse_unary(tokens, position + 1)

        return {
            "kind": "binary",
            "op": "^",
            "left": left,
            "right": right,
            "_ends_parenthesis": right.get("_ends_parenthesis", False)
        }, position

    return left, position


def parse_primary(tokens, position):
    """Parse a number or a parenthesised sub-expression."""
    token = current_token(tokens, position)

    if token["type"] == "NUM":
        return {
            "kind": "number",
            "value": float(token["value"]),
            "_ends_parenthesis": False
        }, position + 1

    if token["type"] == "LPAREN":
        node, position = parse_expression(tokens, position + 1)

        if current_token(tokens, position)["type"] != "RPAREN":
            raise ValueError("Missing closing parenthesis")

        # Mark that this completed factor ended with ')'. This allows forms
        # such as (2+3)4 without treating 2 3 as implicit multiplication.
        node = dict(node)
        node["_ends_parenthesis"] = True
        return node, position + 1

    raise ValueError("Expected a number or '('")


def parse(tokens):
    """Parse a complete token list into an expression tree."""
    tree, position = parse_expression(tokens, 0)

    if current_token(tokens, position)["type"] != "END":
        raise ValueError("Unexpected token")

    return tree


def tree_to_string(node) -> str:
    """Convert the internal tree to the assignment's required prefix form."""
    if node["kind"] == "number":
        return format_number(node["value"])

    if node["kind"] == "unary":
        return f'(neg {tree_to_string(node["operand"])})'

    if node["kind"] == "binary":
        left = tree_to_string(node["left"])
        right = tree_to_string(node["right"])
        return f'({node["op"]} {left} {right})'

    raise ValueError("Invalid tree node")


def evaluate_tree(node) -> float:
    """Recursively evaluate a parsed expression tree."""
    if node["kind"] == "number":
        return node["value"]

    if node["kind"] == "unary":
        return -evaluate_tree(node["operand"])

    left = evaluate_tree(node["left"])
    right = evaluate_tree(node["right"])
    operator = node["op"]

    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise ZeroDivisionError("division by zero")
        return left / right
    if operator == "%":
        if right == 0:
            raise ZeroDivisionError("modulo by zero")
        return left % right
    if operator == "^":
        result = left ** right
        if isinstance(result, complex):
            raise ValueError("Complex results are not supported")
        return float(result)

    raise ValueError("Unknown operator")


def process_expression(expression: str) -> dict:
    """
    Tokenise, parse, and evaluate one expression.

    Tokenisation/parsing errors make tree, tokens, and result all ERROR.
    Evaluation-only errors (for example division by zero) preserve the valid
    tree and token output, matching the supplied sample.
    """
    try:
        tokens = tokenise(expression)
        tokens_text = token_string(tokens)
        tree = parse(tokens)
        tree_text = tree_to_string(tree)
    except (ValueError, OverflowError):
        return {
            "input": expression,
            "tree": "ERROR",
            "tokens": "ERROR",
            "result": "ERROR"
        }

    try:
        result = evaluate_tree(tree)

        if not isinstance(result, (int, float)):
            raise ValueError("Invalid result")

        return {
            "input": expression,
            "tree": tree_text,
            "tokens": tokens_text,
            "result": float(result)
        }
    except (ValueError, ZeroDivisionError, OverflowError):
        return {
            "input": expression,
            "tree": tree_text,
            "tokens": tokens_text,
            "result": "ERROR"
        }


def result_to_output_text(result) -> str:
    """Format a result value for output.txt."""
    if result == "ERROR":
        return "ERROR"
    return format_number(result)


def evaluate_file(input_path: str) -> list[dict]:
    """
    Read one expression per line from input_path, write output.txt in the same
    directory, and return one dictionary per expression.
    """
    with open(input_path, "r", encoding="utf-8") as infile:
        # splitlines() removes newline characters but preserves all other text.
        expressions = infile.read().splitlines()

    results = [process_expression(expression) for expression in expressions]

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(input_path)),
        "output.txt"
    )

    with open(output_path, "w", encoding="utf-8") as outfile:
        for index, item in enumerate(results):
            outfile.write(f'Input: {item["input"]}\n')
            outfile.write(f'Tree: {item["tree"]}\n')
            outfile.write(f'Tokens: {item["tokens"]}\n')
            outfile.write(
                f'Result: {result_to_output_text(item["result"])}\n'
            )

            if index != len(results) - 1:
                outfile.write("\n")

    return results


def main() -> None:
    """Allow the module to be run directly using input.txt."""
    evaluate_file("input.txt")


if __name__ == "__main__":
    main()
