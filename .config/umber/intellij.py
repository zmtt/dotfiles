from perceptual import write_atomic, hex_lr, lch, solve
from editor import syntax, surfaces, audit
from model import EMBER
from studio import config_dir
from palette import contrast, lum, enforce
import glob, json, os
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))

# Retargets the palette to Android Studio (IntelliJ .icls editor schemes), the
# same way neovim.py retargets it to Neovim. The attribute key set is taken
# from a scheme the IDE itself accepts, the ANSI console keys from the
# platform's ConsoleHighlighter, and the keys the installed platform and its
# Android/Kotlin/Compose/Logcat plugins define with stock colours (mined from
# DefaultColorSchemesManager.xml and the plugins' additionalTextAttributes
# scheme XMLs), so no daily surface falls back to Darcula's cool palette.
# Unlisted attributes inherit from the parent scheme (Darcula / Default).
P = json.load(open(_os.path.join(_HERE, "palette.json")))


ANSI = ("BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "GRAY",
        "DARKGRAY", "RED_BRIGHT", "GREEN_BRIGHT", "YELLOW_BRIGHT",
        "BLUE_BRIGHT", "MAGENTA_BRIGHT", "CYAN_BRIGHT", "WHITE")

# Umber-side derivations for surfaces the stock scheme paints in its own cool
# palette. Everything is solved against the live palette, so both variants
# derive for free and a model change reaches every one of these.
def extras(V, S):
    bg, fg = V["background"], V["foreground"]
    dark = lum(bg) < 0.18
    bglr, nh = lch(bg)[0], lch(fg)[2]
    d = 1 if dark else -1
    hue = {k: lch(V[s])[2] for k, s in
           (("red", "1"), ("green", "2"), ("yellow", "3"),
            ("blue", "4"), ("magenta", "5"))}
    wash = lambda off, C, h: hex_lr(bglr + d * off, C, h)[0]
    # Gutter change bars: chromatic enough to read as colour at two pixels
    # wide, dimmer than text so the gutter never competes with the code.
    bar = lambda h, t=3.0: solve(t, bg, 0.055, h)
    # File names in the project tree and on tabs render on the UI surface that
    # matches S["line"], so their floor is solved there, not on the editor bg.
    fs = lambda slot: solve(4.6, S["line"], lch(V[slot])[1], lch(V[slot])[2])
    return {
        # Chip text (inlays, folded code) on the line surface, and ghost text
        # (inline AI suggestions): readable, deliberately quieter than code.
        "quiet": solve(4.6, S["line"], 0.014, nh),
        "ghost_text": solve(3.6, bg, 0.014, nh),
        # The debugger keeps its platform-wide blue identity, in Umber's blue.
        "exec": wash(0.115, 0.045, hue["blue"]),
        "frame": wash(0.075, 0.030, hue["blue"]),
        "breakpoint": wash(0.070, 0.032, hue["red"]),
        "step_target": wash(0.075, 0.028, hue["magenta"]),
        "step_selection": wash(0.115, 0.038, hue["magenta"]),
        "bar_add": bar(hue["green"]), "bar_change": bar(hue["yellow"]),
        "bar_del": bar(hue["red"]), "bar_ws": bar(hue["yellow"], 2.4),
        "bar_add_dim": bar(hue["green"], 2.0), "bar_change_dim": bar(hue["yellow"], 2.0),
        "bar_del_dim": bar(hue["red"], 2.0),
        # Blame ages newest to oldest through the ember, fading toward ground.
        "blame": [wash(0.085 - 0.016 * i, 0.034 - 0.005 * i, EMBER) for i in range(5)],
        "fs": {slot: fs(slot) for slot in ("1", "2", "3", "5", "6", "8", "9")},
    }

def colors(V, S, E):
    c3, c8 = V["3"], V["8"]
    F = E["fs"]
    out = {"CARET_COLOR": V["cursor"], "CARET_ROW_COLOR": S["line"],
           "CONSOLE_BACKGROUND_KEY": V["background"], "GUTTER_BACKGROUND": V["background"],
           "INDENT_GUIDE": S["ghost"], "LINE_NUMBERS_COLOR": S["linenr"],
           "LINE_NUMBER_ON_CARET_ROW_COLOR": c3, "NOTIFICATION_BACKGROUND": S["panel"],
           "RIGHT_MARGIN_COLOR": S["line"], "SELECTED_INDENT_GUIDE": c8,
           "SELECTION_BACKGROUND": V["selection"], "SELECTION_FOREGROUND": V["foreground"],
           "SOFT_WRAP_SIGN_COLOR": S["ghost"], "TEARLINE_COLOR": S["line"],
           "VISUAL_INDENT_GUIDE": S["line"], "WHITESPACES": S["ghost"]}
    out.update({
        "ADDED_LINES_COLOR": E["bar_add"], "MODIFIED_LINES_COLOR": E["bar_change"],
        "DELETED_LINES_COLOR": E["bar_del"], "WHITESPACES_MODIFIED_LINES_COLOR": E["bar_ws"],
        "IGNORED_ADDED_LINES_BORDER_COLOR": E["bar_add_dim"],
        "IGNORED_MODIFIED_LINES_BORDER_COLOR": E["bar_change_dim"],
        "IGNORED_DELETED_LINES_BORDER_COLOR": E["bar_del_dim"],
        "ANNOTATIONS_COLOR": c8})
    out.update({f"VCS_ANNOTATIONS_COLOR_{i + 1}": E["blame"][i] for i in range(5)})
    # File status follows the terminal's git colours: green added, yellow
    # modified, red untracked, bright red conflicted.
    out.update({
        "FILESTATUS_ADDED": F["2"], "FILESTATUS_COPIED": F["2"],
        "FILESTATUS_addedOutside": F["2"],
        "FILESTATUS_MODIFIED": F["3"], "FILESTATUS_modifiedOutside": F["3"],
        "FILESTATUS_NOT_CHANGED_IMMEDIATE": F["3"], "FILESTATUS_NOT_CHANGED_RECURSIVE": F["3"],
        "FILESTATUS_DELETED": F["8"], "FILESTATUS_IDEA_FILESTATUS_DELETED_FROM_FILE_SYSTEM": F["8"],
        "FILESTATUS_UNKNOWN": F["1"], "FILESTATUS_IDEA_FILESTATUS_IGNORED": E["quiet"],
        "FILESTATUS_MERGED": F["5"], "FILESTATUS_RENAMED": F["6"],
        "FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_CONFLICTS": F["9"],
        "FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_BOTH_CONFLICTS": F["9"],
        "FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_PROPERTY_CONFLICTS": F["9"],
        "FILESTATUS_changelistConflict": F["9"],
        "MODIFIED_TAB_ICON": F["3"]})
    out.update({
        "LOOKUP_COLOR": S["over"], "DOCUMENTATION_COLOR": S["over"],
        "RECENT_LOCATIONS_SELECTION": V["selection"],
        "METHOD_SEPARATORS_COLOR": S["ghost"], "DIFF_SEPARATOR_WAVE": S["ghost"],
        "DOC_COMMENT_GUIDE": S["ghost"], "DOC_COMMENT_LINK": V["4"],
        "STRING_CONTENT_INDENT_GUIDE": S["ghost"],
        "FOLDED_TEXT_BORDER_COLOR": S["ghost"], "SELECTED_TEARLINE_COLOR": S["linenr"],
        "Bookmark.iconBackground": c3, "Bookmark.Mnemonic.iconBackground": S["panel"],
        "Bookmark.Mnemonic.iconBorderColor": c3,
        "Bookmark.Mnemonic.iconForeground": V["foreground"]})
    return out

# Roles come from editor.py, so chroma is level across keywords, functions,
# types, strings and literals rather than inheriting the terminal's chrome
# weighting. Static-ness is carried by font style, as IDE convention expects.
def attributes(V, S, E):
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
    # Chips: folded code and inlay hints are quiet text on the line surface,
    # never the stock cool-grey pills.
    put("FOLDED_TEXT_ATTRIBUTES INLAY_DEFAULT INLINE_PARAMETER_HINT",
        FOREGROUND=E["quiet"], BACKGROUND=S["line"])
    put("INLAY_TEXT_WITHOUT_BACKGROUND", FOREGROUND=E["quiet"])
    put("INLINE_PARAMETER_HINT_CURRENT", FOREGROUND=fg, BACKGROUND=S["over"])
    put("INLINE_PARAMETER_HINT_HIGHLIGHTED", FOREGROUND=fg, BACKGROUND=S["panel"])
    put("INLINE_SUGGESTION LOG_EXPIRED_ENTRY", FOREGROUND=E["ghost_text"])
    put("BREADCRUMBS_DEFAULT BREADCRUMBS_INACTIVE", FOREGROUND=mut)
    put("BREADCRUMBS_HOVERED", FOREGROUND=fg, BACKGROUND=S["line"])
    put("BREADCRUMBS_CURRENT", FOREGROUND=fg, BACKGROUND=S["panel"])
    put("CTRL_CLICKABLE", FOREGROUND=c[4], EFFECT_COLOR=c[4], EFFECT_TYPE=1)
    put("INACTIVE_HYPERLINK_ATTRIBUTES", EFFECT_COLOR=c[8], EFFECT_TYPE=1)
    put("DEFAULT_HIGHLIGHTED_REFERENCE DEFAULT_REASSIGNED_LOCAL_VARIABLE "
        "DEFAULT_REASSIGNED_PARAMETER", EFFECT_COLOR=c[8], EFFECT_TYPE=1)
    # Usage washes: read is a neutral lift, write borrows the modified yellow.
    put("IDENTIFIER_UNDER_CARET_ATTRIBUTES", BACKGROUND=S["panel"], ERROR_STRIPE_COLOR=c[6])
    put("WRITE_IDENTIFIER_UNDER_CARET_ATTRIBUTES", BACKGROUND=S["change"], ERROR_STRIPE_COLOR=c[3])
    put("EXECUTIONPOINT_ATTRIBUTES", BACKGROUND=E["exec"])
    put("NOT_TOP_FRAME_ATTRIBUTES", BACKGROUND=E["frame"])
    put("BREAKPOINT_ATTRIBUTES", BACKGROUND=E["breakpoint"], ERROR_STRIPE_COLOR=c[1])
    put("DEBUGGER_SMART_STEP_INTO_TARGET", BACKGROUND=E["step_target"])
    put("DEBUGGER_SMART_STEP_INTO_SELECTION", BACKGROUND=E["step_selection"])
    put("DEBUGGER_INLINED_VALUES", FOREGROUND=X["muted"], FONT_TYPE=2)
    put("DEBUGGER_INLINED_VALUES_EXECUTION_LINE", FOREGROUND=c[4], FONT_TYPE=2)
    put("DEBUGGER_INLINED_VALUES_MODIFIED", FOREGROUND=c[3], FONT_TYPE=2)
    put("INLINE_STACK_FRAMES", BACKGROUND=S["panel"])
    put("EVALUATED_EXPRESSION_ATTRIBUTES EVALUATED_EXPRESSION_EXECUTION_LINE_ATTRIBUTES",
        BACKGROUND=S["over"])
    put("LINE_FULL_COVERAGE", FOREGROUND=E["bar_add"], FONT_TYPE=1)
    put("LINE_PARTIAL_COVERAGE", FOREGROUND=E["bar_change"], FONT_TYPE=1)
    put("LINE_NONE_COVERAGE", FOREGROUND=E["bar_del"], FONT_TYPE=1)
    # Logcat follows the LOG_* law above; level chips invert it (accent ground,
    # editor-background text), so severity reads at a glance without glare.
    LEVELS = {"VERBOSE": c[8], "DEBUG": c[4], "INFO": c[2],
              "WARNING": c[3], "ERROR": c[1], "ASSERT": c[9]}
    for lvl, colour in LEVELS.items():
        put(f"LOGCAT_V2_LEVEL_{lvl}", FOREGROUND=bg, BACKGROUND=colour)
        put(f"LOGCAT_V2_MESSAGE_{lvl}", FOREGROUND=colour)
    put("LOGCAT_FILTER_KEY LOGCAT_FILTER_KVALUE LOGCAT_FILTER_REGEX_KVALUE "
        "LOGCAT_FILTER_STRING_KVALUE", FOREGROUND=fg, BACKGROUND=S["add"])
    # Composable calls read as type, exactly how SwiftUI constructors read in
    # the Umber Xcode theme: declarative UI is construction. Studio's own
    # Compose plugin and the JetBrains shared one register different keys.
    put("ComposableCallTextAttributes IntelliJComposableCallTextAttributes",
        FOREGROUND=X["type"])
    put("ComposeStateReadScopeHighlightingTextAttributes", BACKGROUND=S["panel"])
    # Darcula paints every backing-field property with a purple wash; that is
    # chronic, not exceptional, so Umber declares the key empty to suppress it.
    put("KOTLIN_PROPERTY_WITH_BACKING_FIELD")
    put("KOTLIN_FUNCTION_LITERAL_BRACES_AND_ARROW", FOREGROUND=X["punct"], FONT_TYPE=1)
    put("KOTLIN_CLOSURE_DEFAULT_PARAMETER", FOREGROUND=X["param"])
    put("KOTLIN_BACKING_FIELD_VARIABLE", FOREGROUND=fg, FONT_TYPE=1)
    put("BASH.EXTERNAL_COMMAND", FOREGROUND=X["function"])
    # The find/usages tool window ships pure-red prefixes.
    put("$INVALID_PREFIX $READ_ONLY_PREFIX $HAS_READ_ONLY_CHILD", FOREGROUND=c[1])
    put("$NUMBER_OF_USAGES", FOREGROUND=mut)
    put("$EXCLUDED_NODE", EFFECT_COLOR=c[8], EFFECT_TYPE=3)
    put("XML_CUSTOM_TAG_NAME HTML_CUSTOM_TAG_NAME", FOREGROUND=X["type"])
    put("TYPO", EFFECT_COLOR=c[2], EFFECT_TYPE=2)
    put("BAD_CHARACTER", EFFECT_COLOR=c[9], EFFECT_TYPE=2)
    put("MARKED_FOR_REMOVAL_ATTRIBUTES", EFFECT_COLOR=c[1], EFFECT_TYPE=3)
    put("RUNTIME_ERROR", EFFECT_COLOR=c[9], ERROR_STRIPE_COLOR=c[1], EFFECT_TYPE=5)
    put("LIVE_TEMPLATE_ATTRIBUTES", EFFECT_COLOR=cur, EFFECT_TYPE=0)
    put("LIVE_TEMPLATE_INACTIVE_SEGMENT", EFFECT_COLOR=c[8], EFFECT_TYPE=0)
    put("TEMPLATE_VARIABLE_ATTRIBUTES", FOREGROUND=c[13])
    put("DELETED_TEXT_ATTRIBUTES", BACKGROUND=S["delete"], EFFECT_COLOR=c[8], EFFECT_TYPE=3)
    put("PROPERTIES.KEY", FOREGROUND=fg)
    put("PROPERTIES.KEY_VALUE_SEPARATOR", FOREGROUND=X["punct"])
    put("PROPERTIES.INVALID_STRING_ESCAPE", FOREGROUND=c[9], EFFECT_COLOR=c[9], EFFECT_TYPE=2)
    # Regex roles mirror xcode.py: escape body, type char classes, punct operators.
    put("REGEXP.META REGEXP.ESC_CHARACTER REGEXP.QUOTE_CHARACTER", FOREGROUND=X["escape"])
    put("REGEXP.CHAR_CLASS", FOREGROUND=X["type"])
    put("REGEXP.BRACES REGEXP.BRACKETS REGEXP.PARENTHS", FOREGROUND=X["punct"])
    put("REGEXP.REDUNDANT_ESCAPE", FOREGROUND=X["muted"])
    put("REGEXP_MATCHED_GROUPS", BACKGROUND=S["panel"])
    return A

def hx(v): return v.lstrip("#")

ORDER = ("FOREGROUND", "BACKGROUND", "FONT_TYPE", "EFFECT_COLOR",
         "ERROR_STRIPE_COLOR", "EFFECT_TYPE")

def render(name, parent, V, S, E):
    out = [f'<scheme name="{name}" version="142" parent_scheme="{parent}">',
           "  <metaInfo>",
           '    <property name="created">2026-08-15</property>',
           '    <property name="ide">AndroidStudio</property>',
           '    <property name="ideVersion">2026.1</property>',
           f'    <property name="originalScheme">{name}</property>',
           "  </metaInfo>",
           "  <colors>"]
    for k, v in sorted(colors(V, S, E).items()):
        out.append(f'    <option name="{k}" value="{hx(v)}" />')
    out.append("  </colors>")
    out.append("  <attributes>")
    for k, opts in sorted(attributes(V, S, E).items()):
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

VARIANTS = (("Umber", "Darcula", P["dark"]), ("Umber Light", "Default", P["light"]))
FLOOR = {"Umber": 4.5, "Umber Light": 4.5}

# Audit first, write only if every floor holds — never ship a bad ramp into the
# live config.
failures = []
built = []
for name, parent, V in VARIANTS:
    S = surfaces(V)
    E = extras(V, S)
    built.append((name, parent, V, S, E))
    f = FLOOR[name]; fg, bg = V["foreground"], V["background"]
    checks = [(s, contrast(fg, S[s]), f) for s in ("line", "panel", "over", "add", "change", "delete", "text", "search")]
    checks += [(s, contrast(fg, E[s]), f) for s in ("exec", "frame", "breakpoint", "step_selection")]
    checks += [("comment/panel", contrast(V["8"], S["panel"]), f * 0.66),
               ("chip", min(contrast(V[s], bg) for s in ("1", "2", "3", "4", "8", "9")), f),
               ("blame", contrast(V["8"], E["blame"][0]), f * 0.66),
               ("linenr", contrast(S["linenr"], bg), 1.7)]
    bad = [n for n, x, floor in checks if x < floor]
    bad += [f"syntax:{k}" for k, _ in audit(V, syntax(V), f)]
    print(f"{name:<12} " + " ".join(f"{n} {x:4.2f}" for n, x, _ in checks))
    print(f"             floor {f}  {'PASS' if not bad else 'BELOW: ' + str(bad)}")
    failures += [f"{name}:{n}" for n in bad]
enforce(failures)

OUT = os.path.join(config_dir(), "colors")
os.makedirs(OUT, exist_ok=True)
for name, parent, V, S, E in built:
    write_atomic(os.path.join(OUT, f"{name}.icls"), render(name, parent, V, S, E))
print(f"wrote {len(built)} schemes -> {OUT}")
