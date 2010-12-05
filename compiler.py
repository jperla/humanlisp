#!/usr/bin/env python
import os
import re

def line_tokenize(s):
    """Accepts string.
        Returns list of lines.
    """
    return s.split('\n')

def leading_whitespace(line):
    """Accepts line string.
        Returns number of spaces of leading whitespace.
        One tab counts as one space.
        A line with only whitespace returns -1.
    """
    if re.match('^\s*$', line):
        return -1
    else:
        return len(re.search('^(\s*)', line).group(1))

def group_hexpressions(lines):
    """Accepts list of lines.
        Returns groups of h-expressions
    """
    all_lines = [(leading_whitespace(l), l) for l in lines]
    lines_no_blank = [wl for wl in all_lines if wl[0] >= 0]
    groups = group_when(lines_no_blank, lambda wl: wl[0] == 0)
    return [[line for _,line in group] for group in groups]

def indented_ast(group):
    """Accepts a list of line strings.
        Returns a list of 2-tuples.  
        First element is number of spaces indenting line.
        Second element is list of whitespace-delimited tokens in line.
    """
    #import pdb; pdb.set_trace()
    def tokenize(line):
        """Accepts line string.
            Whitespace tokenizes the line.
        """
        return [w for w in re.split('\s+', line) if w]
    return [(leading_whitespace(g), tokenize(g)) for g in group]
    

def group_when(iterable, when):
    """Accepts iterable.
        Returns list of lists.
        Starts list at first item.  
        Creates new list whenever when func is true.
    """
    output = []
    this = []
    for i in iterable:
        this.append(i)
        if when(i):
            output.append(this)
            this = []
    if this:
        output.append(this)
    return output

def shrink_indented_ast(iast):
    """Accepts indented ast: list of 2-tuples, (int, list of str).
        Returns a smaller one, using H-expression
            replacement. Unless already just 1 expression.
    """
    if len(iast) > 1:
        return iast
    else:
        return iast

def replace_line(ast_lines, target_ast_line, hdelimiter=':'):
    """Accepts list of lines, a line is a list of token strings.
        Also accepts a target line.
        Also accepts delimiter, defaults to ':'
       Returns one ast line after first lines inserted into target.
    """
    def calculate_replacement_dict(ast_lines, hdelimiter):
        """Accepts lines of list of str tokens, and hdelimiter str.
            Returns dict of first token in line (minus delimiter)
                with value the rest of the line of list of token str.
                [['bla:', 'foo', 'bar'], ...] => {'bla': ['foo', 'bar'], ...}
        """
        d = {}
        for line in ast_lines:
            first, rest = line[0], line[1:]
            assert first.endswith(hdelimiter), 'First item in indented must be replacement: %s' % line
            key = first[:-len(hdelimiter)]
            assert key not in d, "More than one token with same name: %s" % key
            d[key] = rest
        return d
    replacement_dict = calculate_replacement_dict(ast_lines, hdelimiter)
    # strip ( and ) to deal with nested s-expressions
    return [replacement_dict.get(token.lstrip('(').rstrip(')'), token) for token in target_ast_line]

def max_indentation_line_number(indented_ast):
    """Accepts indented ast.
        Returns offset int of line that has maximum indentation.
    """
    return -max([(line[0], -i) for i,line in enumerate(indented_ast)])[1]

def max_indentation_range(indented_ast):
    """Accepts indented ast.
        Returns 2-tuples of offsets ints of lines that contiguously have maximum indentation.
    """
    first = max_indentation_line_number(indented_ast)
    i = first
    while indented_ast[i][0] == indented_ast[first][0]:
        i += 1
    last = i-1
    return (first, last)

def shrink_one(indented_ast):
    """Accepts indented ast.
    Returns new ast after one H-expression replacement.
    """
    first, last = max_indentation_range(indented_ast)
    into_index = last + 1

    from_lines = [l[1] for l in indented_ast[first:into_index]]
    indentation, into_line = indented_ast[into_index]
    new_line = replace_line(from_lines, into_line)

    beginning,end = indented_ast[:first], indented_ast[(into_index+1):]
    new_ast = beginning + [(indentation, new_line),] + end
    return new_ast

def calculate_s_expression(indented_ast):
    """Accepts indented ast.
        Returns s-expressions (recursive list of lists of tokens).
    """
    ia = indented_ast
    while len(ia) > 1:
        ia = shrink_one(ia)
    only = ia[0]
    indentation, s_expression = only
    return s_expression

def format_s_expression(s_expression, level=0):
    """Accepts s-expression and current indentation level.
        Recursively returns string version of s-expression at that indentation level.
    """
    def format_token(token):
        if isinstance(token, basestring):
            return token
        else:
            return '\n' + format_s_expression(token, level+1)
    inner = ' '.join([format_token(t) for t in s_expression])
    return ('  ' * level) + '(' + inner + ')'

def compile_file(filename):
    """Accepts filename.
        Writes new file with same name.
        Returns nothing.
    """
    hdelimiter = ':'
    target = 'clj'

    name, extension = os.path.splitext(filename)
    assert extension.endswith('hlisp')
    target_filename = name + '.' + target

    code = open('example.hlisp', 'r').read()
    lines = line_tokenize(code)
    groups = group_hexpressions(lines)
    indented_asts = [indented_ast(g) for g in groups]
    asts = [calculate_s_expression(ia) for ia in indented_asts]

    new_file = '\n\n'.join(format_s_expression(a) for a in asts)
    open(target_filename, 'w').write(new_file)

try:
    compile_file('example.hlisp')

    code = open('example.hlisp', 'r').read()
    lines = line_tokenize(code)
    groups = group_hexpressions(lines)
    print groups
    indented_asts = [indented_ast(g) for g in groups]
    print indented_asts
    indented_ast = indented_asts[2]
    ast = calculate_s_expression(indented_ast)
    print ast
    print format_s_expression(ast)
except Exception, e:
    print e
    import pdb; pdb.post_mortem()

#TODO: jperla: line continuations with parens
#TODO: jperla: remove comments

