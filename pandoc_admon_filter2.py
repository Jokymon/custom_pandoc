#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandoc filter to process admonition blocks.
"""
import io
import fontawesome as fa
import json
import sys
import textwrap
from pandocfilters import walk, RawBlock, RawInline, Div


# Pandoc uses UTF-8 for both input and output; so must its filters.  This is
# handled differently depending on the python version.
if sys.version_info > (3,):
    # Py3 strings are unicode: https://docs.python.org/3.5/howto/unicode.html.
    # Character encoding/decoding is performed automatically at stream
    # interfaces: https://stackoverflow.com/questions/16549332/.
    # Set it to UTF-8 for all streams.
    STDIN = io.TextIOWrapper(sys.stdin.buffer, 'utf-8', 'strict')
    STDOUT = io.TextIOWrapper(sys.stdout.buffer, 'utf-8', 'strict')
    STDERR = io.TextIOWrapper(sys.stderr.buffer, 'utf-8', 'strict')
else:
    # Py2 strings are ASCII bytes.  Encoding/decoding is handled separately.
    # See: https://docs.python.org/2/howto/unicode.html.
    STDIN = sys.stdin
    STDOUT = sys.stdout
    STDERR = sys.stderr


styles = {
    "note": {
        "color": "d23a45",
        "icon": "hand-point-right",
        "icon_source": "free",
        "icon_style": "regular",
    },
    "tip": {
        "color": "f5bb2c",
        "icon": "lightbulb",
        "icon_source": "free",
        "icon_style": "regular",
    },
    "video": {
        "color": "11ac11",
        "icon": "film",
        "icon_source": "free",
        "icon_style": "solid",
    },
    "exercise": {
        "color": "f37726",
        "icon": "book-open",
        "icon_source": "free",
        "icon_style": "solid",
    },
    "python": {
        "color": "4482b4",
        "icon": "python",
        "icon_source": "brands",
        "icon_style": "solid",
    }
}


def rgb_string_to_css(s):
    colors = [s[i:i+2] for i in range(0, 6, 2)]
    colors = list(map(lambda x: str(int(x, 16)), colors))
    return f"rgb({','.join(colors)})"


def rgb_string_to_latex(s):
    colors = [s[i:i+2] for i in range(0, 6, 2)]
    colors = list(map(lambda x: str(int(x, 16)), colors))
    return f"{','.join(colors)}"


def admonition(key, value, format_, meta):
    result = None
    if key == 'Div':
        [[ident, classes, kvs], contents] = value
        for admonition_type in styles.keys():
            if admonition_type in classes:
                classes.remove(admonition_type)
                if format_ == 'html':
                    classes.append("admonition-box")
                    classes.append("admonition-box-"+admonition_type)
                    result = Div([ident, classes, kvs], contents)
                elif format_ == 'latex':
                    result = Div([ident, classes, kvs], [RawBlock('latex',
                                 f"\\admon{admonition_type}box{{")] +
                                 contents + [RawBlock('latex', "}")])
                break
    elif key == 'Str':
        if len(value) > 4 and value[:7] == '&admon:' and value[-1] == ';':
            symbol_name = value[7:-1]
            icon_name = styles[symbol_name]["icon"]
            icon_color = styles[symbol_name]["color"]
            icon_source = styles[symbol_name]["icon_source"]
            icon_style = styles[symbol_name]["icon_style"]

            if format_ == 'latex':
                latex_name = icon_name.replace("-", " ").title().replace(" ", "")
                return RawInline('latex', f"\\textcolor{{{symbol_name}color}}{{\\Huge\\fa{latex_name}}}")
            else:
                entity_code = repr(fa.icons[icon_name])[3:-1]
                css_color = rgb_string_to_css(icon_color)
                return RawInline('html',
                                 f'<span class="awesome_{icon_source}_{icon_style}_icon" style="color: {css_color}">&#x{entity_code};</span>')

    return result


def main(stdin=STDIN, stdout=STDOUT, stderr=STDERR):
    if len(sys.argv) > 1:
        fmt = sys.argv[1]
    else:
        fmt = ""
    doc = json.loads(stdin.read())

    if 'meta' in doc:
        meta = doc['meta']
    else:  # old API
        meta = doc[0]['unMeta']

    metablocks = None
    if fmt == 'latex':
        tex = """
            %%%% pandoc-admonitition: required package
            \\usepackage{awesomebox}
        """
        tex = textwrap.dedent(tex)
        for key, value in styles.items():
            tex += f"\\definecolor{{{key}color}}{{RGB}}{{{rgb_string_to_latex(value['color'])}}}\n"
            tex += f"\\newcommand{{\\admon{key}box}}[1]{{%\n"
            latex_icon_name = "fa"+value['icon'].replace("-", " ").title().replace(" ", "")
            tex += f"    \\awesomebox{{2pt}}{{\\{latex_icon_name}}}{{{key}color}}{{#1}}\n"
            tex += "}\n"
        rawblock = {'t': 'RawBlock', 'c': [fmt, tex]}
        metablocks = {'t': 'MetaBlocks', 'c': [rawblock]}
    elif fmt == 'html':
        html = """
            <link rel="stylesheet" href=
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.css">
            </link>
            <style>
            .awesome_free_normal_icon {
                font-family: 'Font Awesome 5 Free';
                font-size: xx-large;
                font-weight: 400;
            }
            .awesome_free_regular_icon {
                font-family: 'Font Awesome 5 Free';
                font-size: xx-large;
                font-weight: 400;
            }
            .awesome_free_solid_icon {
                font-family: 'Font Awesome 5 Free';
                font-size: xx-large;
                font-weight: 900;
            }
            .awesome_brands_normal_icon {
                font-family: 'Font Awesome 5 Brands';
                font-size: xx-large;
                font-weight: 400;
            }
            .awesome_brands_solid_icon {
                font-family: 'Font Awesome 5 Brands';
                font-size: xx-large;
                font-weight: 900;
            }

            .admonition-box {
                padding-left: 0.5em;
                margin-left: 12%;

                border-style: solid;
                border-width: 0 0 0 2pt;

                position: relative;
            }
            .admonition-box:before {
                font-size: xx-large !important;

                position: absolute;
                left: -12%;
            }
        """
        html = textwrap.dedent(html)
        for key, value in styles.items():
            html += f"\n.admonition-box-{key}:before {{\n"
            html += f"    font: var(--fa-font-{value['icon_style']});\n"
            html += f"    color: {rgb_string_to_css(value['color'])};\n"
            html += f"    content: '\\{repr(fa.icons[value['icon']])[3:]};\n;"
            html += "\n}\n"
        html += "</style>"
        rawblock = {'t': 'RawBlock', 'c': [fmt, html]}
        metablocks = {'t': 'MetaBlocks', 'c': [rawblock]}

    if metablocks is not None:
        if 'header-includes' not in meta:
            meta['header-includes'] = metablocks
        elif meta['header-includes']['t'] in ['MetaBlocks', 'MetaInlines']:
            meta['header-includes'] = \
                {'t': 'MetaList', 'c': [meta['header-includes'], metablocks]}
        elif meta['header-includes']['t'] == 'MetaList':
            meta['header-includes']['c'].append(metablocks)

    altered = doc
    altered = walk(altered, admonition, fmt, meta)

    json.dump(altered, stdout)
    stdout.flush()


if __name__ == "__main__":
    main()
