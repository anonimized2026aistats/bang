import itertools
import re


LOGICAL_REPLACEMENTS = {
    "~": " not ",
    "&": " and ",
    "|": " or ",
}

KEYWORDS = {"and", "or", "not", "true", "false", "True", "False"}
TOKEN_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _clean_name(token):
    token = token.strip()
    if token.endswith(":"):
        token = token[:-1]
    return token


def _translate_expression(expression):
    translated = expression.strip().rstrip(";")
    for old, new in LOGICAL_REPLACEMENTS.items():
        translated = translated.replace(old, new)
    translated = re.sub(r"\btrue\b", "True", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\bfalse\b", "False", translated, flags=re.IGNORECASE)
    return translated


def _expression_variables(expression, names_dict):
    variables = []
    for token in TOKEN_PATTERN.findall(expression):
        if token in KEYWORDS:
            continue
        if token not in names_dict:
            raise ValueError(f"Unknown ISPL variable: {token}")
        if token not in variables:
            variables.append(token)
    return variables


def _truth_table(expression, variable_names, names_dict):
    translated = _translate_expression(expression)
    variables = sorted(_expression_variables(translated, names_dict), key=names_dict.get)
    variable_indices = [names_dict[name] for name in variables]
    table = []

    for values in itertools.product([False, True], repeat=len(variables)):
        context = dict(zip(variables, values))
        table.append(bool(eval(translated, {}, context)))

    return table, variable_indices


def _parse_true_rule(line):
    statement, condition = line.strip().rstrip(";").split(" if ", 1)
    target_name, target_value = [part.strip() for part in statement.split("=", 1)]

    if target_value.lower() != "true":
        return None

    expression, expected_value = [part.strip() for part in condition.rsplit("=", 1)]
    if expected_value.lower() != "true":
        raise ValueError("Unsupported ISPL rule shape")

    return target_name, expression


def load_ispl(path):
    with open(path, "r") as file:
        lines = [line.strip() for line in file if line.strip()]

    names = []
    functions_by_name = {}
    i = 0

    while i < len(lines):
        if lines[i] == "Vars:":
            i += 1
            while i < len(lines) and not lines[i].startswith("end"):
                names.append(_clean_name(lines[i].split()[0]))
                i += 1
            continue

        if lines[i] == "Evolution:":
            i += 1
            while i < len(lines) and not lines[i].startswith("end"):
                parsed = _parse_true_rule(lines[i])
                if parsed is not None:
                    target_name, expression = parsed
                    functions_by_name[target_name] = expression
                i += 1
            continue

        i += 1

    if not names:
        raise ValueError("Invalid ISPL file: missing Vars section")
    if len(functions_by_name) != len(names):
        missing = [name for name in names if name not in functions_by_name]
        raise ValueError(f"Invalid ISPL file: missing update rules for {missing}")

    names_dict = {name: index for index, name in enumerate(names)}
    n = len(names)
    nf = [1 for _ in names]
    nv = []
    functions = []
    parent_variable_indices = []
    function_probabilities = [[1.0] for _ in names]

    for name in names:
        table, variables = _truth_table(functions_by_name[name], names, names_dict)
        functions.append(table)
        parent_variable_indices.append(variables)
        nv.append(len(variables))

    perturbation = 0.0
    non_perturbed_nodes = []
    return n, nf, nv, functions, parent_variable_indices, function_probabilities, perturbation, non_perturbed_nodes
