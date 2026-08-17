from perceptual import write_atomic
from editor import syntax, surfaces, audit
from studio import config_dir
from palette import contrast, lum, enforce
import glob, json, os
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))

# Retargets the palette to Android Studio (IntelliJ .icls editor schemes), the
# same way neovim.py retargets it to Neovim. The attribute key set is taken
# from a scheme the IDE itself accepts plus the ANSI console keys from the
# platform's ConsoleHighlighter; unlisted attributes inherit from the parent
# scheme (Darcula / Default).
P = json.load(open(_os.path.join(_HERE, "palette.json")))


ANSI = ("BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "GRAY",
        "DARKGRAY", "RED_BRIGHT", "GREEN_BRIGHT", "YELLOW_BRIGHT",
        "BLUE_BRIGHT", "MAGENTA_BRIGHT", "CYAN_BRIGHT", "WHITE")

def colors(V, S):
    c3, c8 = V["3"], V["8"]
    return {"CARET_COLOR": V["cursor"], "CARET_ROW_COLOR": S["line"],
            "CONSOLE_BACKGROUND_KEY": V["background"], "GUTTER_BACKGROUND": V["background"],
            "INDENT_GUIDE": S["ghost"], "LINE_NUMBERS_COLOR": S["linenr"],
            "LINE_NUMBER_ON_CARET_ROW_COLOR": c3, "NOTIFICATION_BACKGROUND": S["panel"],
            "RIGHT_MARGIN_COLOR": S["line"], "SELECTED_INDENT_GUIDE": c8,
            "SELECTION_BACKGROUND": V["selection"], "SELECTION_FOREGROUND": V["foreground"],
            "SOFT_WRAP_SIGN_COLOR": S["ghost"], "TEARLINE_COLOR": S["line"],
            "VISUAL_INDENT_GUIDE": S["line"], "WHITESPACES": S["ghost"]}

# Roles come from editor.py, so chroma is level across keywords, functions,
# types, strings and literals rather than inheriting the terminal's chrome
# weighting. Static-ness is carried by font style, as IDE convention expects.
def attributes(V, S):
    fg, bg, sel, cur = V["foreground"], V["background"], V["selection"], V["cursor"]
    c = {i: V[str(i)] for i in range(16)}
    X = syntax(V)
    mut = c[7] if lum(bg) < 0.18 else c[8]  # muted text; light's slot 7 is a surface
    A = {}
    def put(keys, **v):
        for k in keys.split(): A[k] = v
    put("TEXT", FOREGROUND=fg, BACKGROUND=bg)
    put("DEFAULT_LINE_COMMENT DEFAULT_BLOCK_COMMENT DEFAULT_DOC_COMMENT "
        "JAVA_LINE_COMMENT JAVA_BLOCK_COMMENT JAVA_DOC_COMMENT",
        FOREGROUND=c[8], FONT_TYPE=2)
    put("DEFAULT_DOC_COMMENT_TAG JAVA_DOC_TAG", FOREGROUND=c[8], FONT_TYPE=3)
    put("DEFAULT_DOC_COMMENT_TAG_VALUE JAVA_DOC_TAG_VALUE", FOREGROUND=mut)
    put("DEFAULT_DOC_MARKUP JAVA_DOC_MARKUP", FOREGROUND=c[8])
    put("DEFAULT_KEYWORD JAVA_KEYWORD GROOVY_KEYWORD JSON.KEYWORD", FOREGROUND=X["keyword"])
    put("DEFAULT_STRING JAVA_STRING GROOVY_STRING JSON.STRING "
        "XML_ATTRIBUTE_VALUE HTML_ATTRIBUTE_VALUE YAML_SCALAR_VALUE "
        "ANNOTATION_ATTRIBUTE_VALUE", FOREGROUND=X["string"])
    put("DEFAULT_VALID_STRING_ESCAPE JAVA_VALID_STRING_ESCAPE", FOREGROUND=X["escape"])
    put("DEFAULT_INVALID_STRING_ESCAPE JAVA_INVALID_STRING_ESCAPE",
        FOREGROUND=c[9], EFFECT_COLOR=c[9], EFFECT_TYPE=2)
    put("DEFAULT_NUMBER JAVA_NUMBER GROOVY_NUMBER JSON.NUMBER", FOREGROUND=X["number"])
    put("DEFAULT_CONSTANT KOTLIN_ENUM_ENTRY", FOREGROUND=X["constant"])
    put("STATIC_FINAL_FIELD_ATTRIBUTES", FOREGROUND=X["constant"], FONT_TYPE=2)
    put("DEFAULT_CLASS_NAME DEFAULT_CLASS_REFERENCE DEFAULT_INTERFACE_NAME "
        "CLASS_NAME_ATTRIBUTES INTERFACE_NAME_ATTRIBUTES ENUM_NAME_ATTRIBUTES "
        "ANONYMOUS_CLASS_NAME_ATTRIBUTES KOTLIN_OBJECT "
        "CONSTRUCTOR_CALL_ATTRIBUTES CONSTRUCTOR_DECLARATION_ATTRIBUTES",
        FOREGROUND=X["type"])
    put("ABSTRACT_CLASS_NAME_ATTRIBUTES", FOREGROUND=X["type"], FONT_TYPE=2)
    put("KOTLIN_TYPE_PARAMETER TYPE_PARAMETER_NAME_ATTRIBUTES", FOREGROUND=c[14])
    put("DEFAULT_FUNCTION_DECLARATION DEFAULT_FUNCTION_CALL "
        "METHOD_DECLARATION_ATTRIBUTES METHOD_CALL_ATTRIBUTES "
        "INHERITED_METHOD_ATTRIBUTES KOTLIN_PACKAGE_FUNCTION_CALL", FOREGROUND=X["function"])
    put("ABSTRACT_METHOD_ATTRIBUTES DEFAULT_STATIC_METHOD STATIC_METHOD_ATTRIBUTES "
        "KOTLIN_DYNAMIC_FUNCTION_CALL", FOREGROUND=X["function"], FONT_TYPE=2)
    put("KOTLIN_SUSPEND_FUNCTION_CALL", FOREGROUND=X["function"], EFFECT_COLOR=c[8], EFFECT_TYPE=1)
    put("DEFAULT_IDENTIFIER DEFAULT_LOCAL_VARIABLE LOCAL_VARIABLE_ATTRIBUTES "
        "XML_TAG_DATA JSON.PROPERTY_KEY YAML_SCALAR_KEY", FOREGROUND=fg)
    put("DEFAULT_PARAMETER PARAMETER_ATTRIBUTES LAMBDA_PARAMETER_ATTRIBUTES",
        FOREGROUND=X["param"])
    put("DEFAULT_INSTANCE_FIELD INSTANCE_FIELD_ATTRIBUTES", FOREGROUND=X["member"])
    put("DEFAULT_STATIC_FIELD STATIC_FIELD_ATTRIBUTES DEFAULT_GLOBAL_VARIABLE "
        "KOTLIN_EXTENSION_PROPERTY KOTLIN_PACKAGE_PROPERTY "
        "KOTLIN_DYNAMIC_PROPERTY_CALL IMPLICIT_ANONYMOUS_CLASS_PARAMETER_ATTRIBUTES",
        FOREGROUND=fg, FONT_TYPE=2)
    put("KOTLIN_BACKING_FIELD_ACCESS", FOREGROUND=fg, FONT_TYPE=1)
    put("REASSIGNED_LOCAL_VARIABLE_ATTRIBUTES REASSIGNED_PARAMETER_ATTRIBUTES "
        "KOTLIN_MUTABLE_VARIABLE", FOREGROUND=fg, EFFECT_COLOR=c[8], EFFECT_TYPE=1)
    put("DEFAULT_BRACES DEFAULT_BRACKETS DEFAULT_PARENTHS DEFAULT_DOT "
        "DEFAULT_COMMA DEFAULT_SEMICOLON DEFAULT_OPERATION_SIGN "
        "JAVA_BRACES JAVA_BRACKETS JAVA_PARENTH JAVA_DOT JAVA_COMMA "
        "JAVA_SEMICOLON JAVA_OPERATION_SIGN XML_TAG HTML_TAG", FOREGROUND=X["punct"])
    put("DEFAULT_LABEL KOTLIN_LABEL KOTLIN_NAMED_ARGUMENT XML_NS_PREFIX", FOREGROUND=X["param"])
    put("DEFAULT_PREDEFINED_SYMBOL", FOREGROUND=c[12])
    put("ANNOTATION_NAME_ATTRIBUTES ANNOTATION_ATTRIBUTE_NAME_ATTRIBUTES "
        "DEFAULT_METADATA KOTLIN_ANNOTATION XML_ATTRIBUTE_NAME "
        "HTML_ATTRIBUTE_NAME", FOREGROUND=X["constant"])
    put("KOTLIN_SMART_CAST_RECEIVER KOTLIN_SMART_CAST_VALUE KOTLIN_SMART_CONSTANT",
        BACKGROUND=S["add"])
    put("XML_TAG_NAME HTML_TAG_NAME", FOREGROUND=X["keyword"])
    put("XML_ENTITY_REFERENCE HTML_ENTITY_REFERENCE YAML_ANCHOR", FOREGROUND=c[14])
    put("XML_PROLOGUE", FOREGROUND=c[8])
    put("CONSOLE_NORMAL_OUTPUT", FOREGROUND=fg)
    put("CONSOLE_ERROR_OUTPUT", FOREGROUND=c[1])
    put("CONSOLE_SYSTEM_OUTPUT", FOREGROUND=c[8])
    put("CONSOLE_USER_INPUT", FOREGROUND=c[2])
    for i, name in enumerate(ANSI):
        put(f"CONSOLE_{name}_OUTPUT", FOREGROUND=c[i])
    put("LOG_VERBOSE_OUTPUT", FOREGROUND=c[8])
    put("LOG_DEBUG_OUTPUT", FOREGROUND=c[4])
    put("LOG_INFO_OUTPUT", FOREGROUND=c[2])
    put("LOG_WARNING_OUTPUT", FOREGROUND=c[3])
    put("LOG_ERROR_OUTPUT", FOREGROUND=c[1])
    put("ERRORS_ATTRIBUTES", EFFECT_COLOR=c[1], ERROR_STRIPE_COLOR=c[1], EFFECT_TYPE=2)
    put("WARNING_ATTRIBUTES", EFFECT_COLOR=c[3], ERROR_STRIPE_COLOR=c[3], EFFECT_TYPE=2)
    put("INFO_ATTRIBUTES", EFFECT_COLOR=c[4], EFFECT_TYPE=2)
    put("DEPRECATED_ATTRIBUTES", EFFECT_COLOR=c[8], EFFECT_TYPE=3)
    put("NOT_USED_ELEMENT_ATTRIBUTES", FOREGROUND=c[8])
    put("WRONG_REFERENCES_ATTRIBUTES", FOREGROUND=c[9])
    put("MATCHED_BRACE_ATTRIBUTES", BACKGROUND=sel, FONT_TYPE=1)
    put("UNMATCHED_BRACE_ATTRIBUTES", FOREGROUND=bg, BACKGROUND=c[1])
    put("SEARCH_RESULT_ATTRIBUTES TEXT_SEARCH_RESULT_ATTRIBUTES",
        BACKGROUND=S["search"], ERROR_STRIPE_COLOR=cur)
    put("WRITE_SEARCH_RESULT_ATTRIBUTES",
        BACKGROUND=S["search"], EFFECT_COLOR=c[9], ERROR_STRIPE_COLOR=c[9], EFFECT_TYPE=1)
    put("TODO_DEFAULT_ATTRIBUTES", FOREGROUND=c[11], FONT_TYPE=3, ERROR_STRIPE_COLOR=c[3])
    put("BOOKMARKS_ATTRIBUTES", ERROR_STRIPE_COLOR=cur)
    put("HYPERLINK_ATTRIBUTES", FOREGROUND=c[4], EFFECT_COLOR=c[4], EFFECT_TYPE=1)
    put("FOLLOWED_HYPERLINK_ATTRIBUTES", FOREGROUND=c[13], EFFECT_COLOR=c[13], EFFECT_TYPE=1)
    put("DIFF_INSERTED", BACKGROUND=S["add"], ERROR_STRIPE_COLOR=c[2])
    put("DIFF_MODIFIED", BACKGROUND=S["change"], ERROR_STRIPE_COLOR=c[3])
    put("DIFF_DELETED", BACKGROUND=S["delete"], ERROR_STRIPE_COLOR=c[1])
    put("DIFF_CONFLICT", BACKGROUND=S["text"], ERROR_STRIPE_COLOR=c[9])
    put("INJECTED_LANGUAGE_FRAGMENT DEFAULT_TEMPLATE_LANGUAGE_COLOR", BACKGROUND=S["line"])
    put("MARKDOWN_HEADER", FOREGROUND=c[3], FONT_TYPE=1)
    put("MARKDOWN_BOLD", FONT_TYPE=1)
    put("MARKDOWN_ITALIC", FONT_TYPE=2)
    put("MARKDOWN_CODE_SPAN MARKDOWN_CODE_BLOCK", FOREGROUND=c[6], BACKGROUND=S["line"])
    put("MARKDOWN_CODE_FENCE", FOREGROUND=c[8])
    put("MARKDOWN_LINK_TEXT", FOREGROUND=c[4], EFFECT_COLOR=c[4], EFFECT_TYPE=1)
    put("MARKDOWN_LINK_DESTINATION", FOREGROUND=mut)
    return A

def hx(v): return v.lstrip("#")

ORDER = ("FOREGROUND", "BACKGROUND", "FONT_TYPE", "EFFECT_COLOR",
         "ERROR_STRIPE_COLOR", "EFFECT_TYPE")

def render(name, parent, V, S):
    out = [f'<scheme name="{name}" version="142" parent_scheme="{parent}">',
           "  <metaInfo>",
           '    <property name="created">2026-08-15</property>',
           '    <property name="ide">AndroidStudio</property>',
           '    <property name="ideVersion">2026.1</property>',
           f'    <property name="originalScheme">{name}</property>',
           "  </metaInfo>",
           "  <colors>"]
    for k, v in sorted(colors(V, S).items()):
        out.append(f'    <option name="{k}" value="{hx(v)}" />')
    out.append("  </colors>")
    out.append("  <attributes>")
    for k, opts in sorted(attributes(V, S).items()):
        out.append(f'    <option name="{k}">')
        out.append("      <value>")
        for o in ORDER:
            if o in opts:
                v = opts[o]
                out.append(f'        <option name="{o}" value="{v if isinstance(v, int) else hx(v)}" />')
        out.append("      </value>")
        out.append("    </option>")
    out += ["  </attributes>", "</scheme>"]
    return "\n".join(out) + "\n"

VARIANTS = (("Umber", "Darcula", P["dark"]), ("Umber Night", "Darcula", P["night"]),
            ("Umber Light", "Default", P["light"]))
FLOOR = {"Umber": 4.5, "Umber Night": 3.3, "Umber Light": 4.5}

# Audit first, write only if every floor holds — never ship a bad ramp into the
# live config.
failures = []
built = []
for name, parent, V in VARIANTS:
    S = surfaces(V)
    built.append((name, parent, V, S))
    f = FLOOR[name]; fg, bg = V["foreground"], V["background"]
    checks = [(s, contrast(fg, S[s]), f) for s in ("line", "panel", "add", "change", "delete", "text", "search")]
    checks += [("comment/panel", contrast(V["8"], S["panel"]), f * 0.66),
               ("linenr", contrast(S["linenr"], bg), 1.7)]
    bad = [n for n, x, floor in checks if x < floor]
    bad += [f"syntax:{k}" for k, _ in audit(V, syntax(V), f)]
    print(f"{name:<12} " + " ".join(f"{n} {x:4.2f}" for n, x, _ in checks))
    print(f"             floor {f}  {'PASS' if not bad else 'BELOW: ' + str(bad)}")
    failures += [f"{name}:{n}" for n in bad]
enforce(failures)

OUT = os.path.join(config_dir(), "colors")
os.makedirs(OUT, exist_ok=True)
for name, parent, V, S in built:
    write_atomic(os.path.join(OUT, f"{name}.icls"), render(name, parent, V, S))
print(f"wrote 3 schemes -> {OUT}")
