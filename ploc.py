#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Count lines of code
"""

# TODO - create docopt usage
# TODO - take gitignore files into accound (`walk`)
#   -> collect `.gitignore` files while walking
#   -> compile content into a regex using fnmatch.translate
#   -> check files/directories against this regex
# TODO - experiment with parallelization
# TODO - compile with cython
# TODO - pretty-print output
# TODO - write tests to make sure logic is correct

from collections import defaultdict
from enum import Enum, auto
import mimetypes
import os
import os.path
import sys


class Language(Enum):
    Cpp = auto()
    ActionScript = auto()
    Ada = auto()
    Agda = auto()
    Asp = auto()
    AspNet = auto()
    Assembly = auto()
    Autoconf = auto()
    Awk = auto()
    Batch = auto()
    BourneShell = auto()
    C = auto()
    CCppHeader = auto()
    CSharp = auto()
    CShell = auto()
    Clojure = auto()
    CoffeeScript = auto()
    ColdFusion = auto()
    ColdFusionScript = auto()
    Coq = auto()
    Css = auto()
    CUDA = auto()
    CUDAHeader = auto()
    D = auto()
    Dart = auto()
    DeviceTree = auto()
    Elixir = auto()
    Elm = auto()
    Erlang = auto()
    Forth = auto()
    FortranLegacy = auto()
    FortranModern = auto()
    FSharp = auto()
    Gherkin = auto()
    Glsl = auto()
    Go = auto()
    Groovy = auto()
    Handlebars = auto()
    Haskell = auto()
    Hex = auto()
    Html = auto()
    INI = auto()
    Idris = auto()
    IntelHex = auto()
    Isabelle = auto()
    Jai = auto()
    Java = auto()
    JavaScript = auto()
    Json = auto()
    Jsx = auto()
    Julia = auto()
    Kotlin = auto()
    Less = auto()
    LinkerScript = auto()
    Lean = auto()
    Lisp = auto()
    Lua = auto()
    Make = auto()
    Makefile = auto()
    Markdown = auto()
    Mustache = auto()
    Nim = auto()
    Nix = auto()
    OCaml = auto()
    ObjectiveC = auto()
    ObjectiveCpp = auto()
    Oz = auto()
    Pascal = auto()
    Perl = auto()
    Php = auto()
    Polly = auto()
    Prolog = auto()
    Protobuf = auto()
    PureScript = auto()
    Pyret = auto()
    Python = auto()
    Qcl = auto()
    Qml = auto()
    R = auto()
    Razor = auto()
    ReStructuredText = auto()
    Ruby = auto()
    RubyHtml = auto()
    Rust = auto()
    SaltStack = auto()
    Sass = auto()
    Scala = auto()
    Sml = auto()
    Sql = auto()
    Stylus = auto()
    Swift = auto()
    Tcl = auto()
    Terraform = auto()
    Tex = auto()
    Text = auto()
    Toml = auto()
    TypeScript = auto()
    Tsx = auto()
    UnrealScript = auto()
    VimScript = auto()
    Wolfram = auto()
    XML = auto()
    Yacc = auto()
    Yaml = auto()
    Zig = auto()
    Zsh = auto()
    Haxe = auto()


EXTS = {
    "4th": Language.Forth,
    "forth": Language.Forth,
    "fr": Language.Forth,
    "frt": Language.Forth,
    "fth": Language.Forth,
    "f83": Language.Forth,
    "fb": Language.Forth,
    "fpm": Language.Forth,
    "e4": Language.Forth,
    "rx": Language.Forth,
    "ft": Language.Forth,
    "ada": Language.Ada,
    "adb": Language.Ada,
    "ads": Language.Ada,
    "pad": Language.Ada,
    "agda": Language.Agda,
    "as": Language.ActionScript,
    "awk": Language.Awk,
    "bat": Language.Batch,
    "btm": Language.Batch,
    "cmd": Language.Batch,
    "c": Language.C,
    "ec": Language.C,
    "pgc": Language.C,
    "cc": Language.Cpp,
    "cpp": Language.Cpp,
    "cxx": Language.Cpp,
    "c++": Language.Cpp,
    "pcc": Language.Cpp,
    "cfc": Language.ColdFusionScript,
    "coffee": Language.CoffeeScript,
    "cs": Language.CSharp,
    "csh": Language.CShell,
    "css": Language.Css,
    "postcss": Language.Css,
    "cu": Language.CUDA,
    "cuh": Language.CUDAHeader,
    "d": Language.D,
    "dart": Language.Dart,
    "dts": Language.DeviceTree,
    "dtsi": Language.DeviceTree,
    "el": Language.Lisp,
    "lisp": Language.Lisp,
    "lsp": Language.Lisp,
    "scm": Language.Lisp,
    "ss": Language.Lisp,
    "rkt": Language.Lisp,
    "ex": Language.Elixir,
    "exs": Language.Elixir,
    "elm": Language.Elm,
    "erl": Language.Erlang,
    "hrl": Language.Erlang,
    "feature": Language.Gherkin,
    "fs": Language.FSharp,
    "fsx": Language.FSharp,
    "vert": Language.Glsl,
    "tesc": Language.Glsl,
    "tese": Language.Glsl,
    "geom": Language.Glsl,
    "frag": Language.Glsl,
    "comp": Language.Glsl,
    "go": Language.Go,
    "groovy": Language.Groovy,
    "h": Language.CCppHeader,
    "hh": Language.CCppHeader,
    "hpp": Language.CCppHeader,
    "hxx": Language.CCppHeader,
    "hbs": Language.Handlebars,
    "handlebars": Language.Handlebars,
    "hs": Language.Haskell,
    "html": Language.Html,
    "idr": Language.Idris,
    "lidr": Language.Idris,
    "ini": Language.INI,
    "jai": Language.Jai,
    "java": Language.Java,
    "jl": Language.Julia,
    "js": Language.JavaScript,
    "jsx": Language.Jsx,
    "kt": Language.Kotlin,
    "kts": Language.Kotlin,
    "lds": Language.LinkerScript,
    "lean": Language.Lean,
    "hlean": Language.Lean,
    "less": Language.Less,
    "lua": Language.Lua,
    "m": Language.ObjectiveC,
    "ml": Language.OCaml,
    "mli": Language.OCaml,
    "nb": Language.Wolfram,
    "wl": Language.Wolfram,
    "sh": Language.BourneShell,
    "asa": Language.Asp,
    "asp": Language.Asp,
    "asax": Language.AspNet,
    "ascx": Language.AspNet,
    "asmx": Language.AspNet,
    "aspx": Language.AspNet,
    "master": Language.AspNet,
    "sitemap": Language.AspNet,
    "webinfo": Language.AspNet,
    "in": Language.Autoconf,
    "clj": Language.Clojure,
    "cljs": Language.Clojure,
    "cljc": Language.Clojure,
    "f": Language.FortranLegacy,
    "for": Language.FortranLegacy,
    "ftn": Language.FortranLegacy,
    "f77": Language.FortranLegacy,
    "pfo": Language.FortranLegacy,
    "f03": Language.FortranModern,
    "f08": Language.FortranModern,
    "f90": Language.FortranModern,
    "f95": Language.FortranModern,
    "makefile": Language.Makefile,
    "mk": Language.Makefile,
    "Makefile": Language.Makefile,
    "mm": Language.ObjectiveCpp,
    "nim": Language.Nim,
    "nix": Language.Nix,
    "php": Language.Php,
    "pl": Language.Perl,
    "pm": Language.Perl,
    "qcl": Language.Qcl,
    "qml": Language.Qml,
    "cshtml": Language.Razor,
    "mustache": Language.Mustache,
    "oz": Language.Oz,
    "p": Language.Prolog,
    "pro": Language.Prolog,
    "pas": Language.Pascal,
    "hex": Language.Hex,
    "ihex": Language.IntelHex,
    "json": Language.Json,
    "markdown": Language.Markdown,
    "md": Language.Markdown,
    "rst": Language.ReStructuredText,
    "text": Language.Text,
    "txt": Language.Text,
    "polly": Language.Polly,
    "proto": Language.Protobuf,
    "purs": Language.PureScript,
    "arr": Language.Pyret,
    "py": Language.Python,
    "r": Language.R,
    "rake": Language.Ruby,
    "rb": Language.Ruby,
    "rhtml": Language.RubyHtml,
    "rs": Language.Rust,
    "s": Language.Assembly,
    "asm": Language.Assembly,
    "sass": Language.Sass,
    "scss": Language.Sass,
    "sc": Language.Scala,
    "scala": Language.Scala,
    "sls": Language.SaltStack,
    "sml": Language.Sml,
    "sql": Language.Sql,
    "styl": Language.Stylus,
    "swift": Language.Swift,
    "tcl": Language.Tcl,
    "tf": Language.Terraform,
    "tex": Language.Tex,
    "sty": Language.Tex,
    "toml": Language.Toml,
    "ts": Language.TypeScript,
    "tsx": Language.Tsx,
    "thy": Language.Isabelle,
    "uc": Language.UnrealScript,
    "uci": Language.UnrealScript,
    "upkg": Language.UnrealScript,
    "v": Language.Coq,
    "vim": Language.VimScript,
    "xml": Language.XML,
    "yaml": Language.Yaml,
    "yml": Language.Yaml,
    "y": Language.Yacc,
    "zig": Language.Zig,
    "zsh": Language.Zsh,
    "hx": Language.Haxe,
}


# TODO: Generalize quotes
CONFIGS = {
    Language.Ada: (b"--", None),
    Language.Batch: (b"REM", None),
    Language.Erlang: (b"%", None),
    Language.Tex: (b"%", None),
    Language.FortranModern: (b"!", None),
    Language.INI: (b";", None),
    Language.Protobuf: (b"//", None),
    Language.Zig: (b"//", None),
    Language.VimScript: (b'"', None),
    Language.Terraform: (b"#", (b"/*", b"*/")),
    Language.Nix: (b"#", (b"/*", b"*/")),
    Language.Assembly: (b"#", (b"/*", b"*/")),
    Language.CoffeeScript: (b"#", (b"###", b"###")),
    Language.D: (b"//", (b"/*", b"*/")),
    Language.Forth: (b"\\", (b"(b", b")")),
    Language.FSharp: (b"//", (b"(*", b"*)")),
    Language.Julia: (b"#", (b"#=", b"=#")),
    Language.Lisp: (b";", (b"#|", b"|#")),
    Language.Text: None,
    Language.Markdown: None,
    Language.Json: None,
    Language.IntelHex: None,
    Language.Hex: None,
    Language.ReStructuredText: None,
    Language.Lean: (b"--", (b"/-", b"-/")),
    Language.Lua: (b"--", (b"--[[", b"]]")),
    Language.Perl: (b"#", (b"=pod", b"=cut")),
    Language.Python: (b"#", (b'"""', b'"""')),  # TODO
    Language.Ruby: (b"#", (b"=begin", b"=end")),
    Language.Sql: (b"--", (b"/*", b"*/")),
    Language.Haskell: (b"--", (b"{-", b"-}")),
    Language.Idris: (b"--", (b"{-", b"-}")),
    Language.Agda: (b"--", (b"{-", b"-}")),
    Language.PureScript: (b"--", (b"{-", b"-}")),
    Language.Elm: (b"--", (b"{-", b"-}")),
    Language.Autoconf: (b"#", None),  # TODO
    Language.Clojure: (b"#", None),  # TODO
    Language.Php: (b"#", (b"/*", b"*/")),
    Language.Coq: (None, (b"(*", b"*)")),
    Language.Sml: (None, (b"(*", b"*)")),
    Language.Wolfram: (None, (b"(*", b"*)")),
    Language.OCaml: (None, (b"(*", b"*)")),
    # Html style
    Language.Html: (None, (b"<!--", b"-->")),
    Language.Polly: (None, (b"<!--", b"-->")),
    Language.RubyHtml: (None, (b"<!--", b"-->")),
    Language.XML: (None, (b"<!--", b"-->")),
    # Shell style
    Language.BourneShell: (b"#", None),
    Language.Awk: (b"#", None),
    Language.Awk: (b"#", None),
    Language.CShell: (b"#", None),
    Language.Makefile: (b"#", None),
    Language.Nim: (b"#", None),
    Language.R: (b"#", None),
    Language.SaltStack: (b"#", None),
    Language.Tcl: (b"#", None),
    Language.Toml: (b"#", None),
    Language.Yaml: (b"#", None),
    Language.Zsh: (b"#", None),
    Language.Elixir: (b"#", None),
    # C-style
    Language.C: (b"//", (b"/*", b"*/")),
    Language.CCppHeader: (b"//", (b"/*", b"*/")),
    Language.Rust: (b"//", (b"/*", b"*/")),
    Language.Yacc: (b"//", (b"/*", b"*/")),
    Language.ActionScript: (b"//", (b"/*", b"*/")),
    Language.Css: (b"//", (b"/*", b"*/")),
    Language.Cpp: (b"//", (b"/*", b"*/")),
    Language.CUDA: (b"//", (b"/*", b"*/")),
    Language.CUDAHeader: (b"//", (b"/*", b"*/")),
    Language.CSharp: (b"//", (b"/*", b"*/")),
    Language.Dart: (b"//", (b"/*", b"*/")),
    Language.Glsl: (b"//", (b"/*", b"*/")),
    Language.Go: (b"//", (b"/*", b"*/")),
    Language.Java: (b"//", (b"/*", b"*/")),
    Language.JavaScript: (b"//", (b"/*", b"*/")),
    Language.Jsx: (b"//", (b"/*", b"*/")),
    Language.Kotlin: (b"//", (b"/*", b"*/")),
    Language.Less: (b"//", (b"/*", b"*/")),
    Language.LinkerScript: (b"//", (b"/*", b"*/")),
    Language.ObjectiveC: (b"//", (b"/*", b"*/")),
    Language.ObjectiveCpp: (b"//", (b"/*", b"*/")),
    Language.Sass: (b"//", (b"/*", b"*/")),
    Language.Scala: (b"//", (b"/*", b"*/")),
    Language.Swift: (b"//", (b"/*", b"*/")),
    Language.TypeScript: (b"//", (b"/*", b"*/")),
    Language.Tsx: (b"//", (b"/*", b"*/")),
    Language.UnrealScript: (b"//", (b"/*", b"*/")),
    Language.Stylus: (b"//", (b"/*", b"*/")),
    Language.Qml: (b"//", (b"/*", b"*/")),
    Language.Haxe: (b"//", (b"/*", b"*/")),
    Language.Groovy: (b"//", (b"/*", b"*/")),
}


def walk(path="."):
    queue = [path]
    while len(queue) > 0:
        d = queue.pop()
        with os.scandir(d) as it:
            for entry in it:
                if entry.is_dir() and not entry.name.startswith("."):
                    queue.append(f"{d}/{entry.name}")
                else:
                    if entry.name == ".gitignore":
                        print(f"{d}/{entry.name}")
                    yield f"{d}/{entry.name}"


def process_file(filepath):
    blank = 0
    code = 0
    comments = 0
    lines = 0

    basename = os.path.basename(filepath)
    ext = basename.rsplit(".", 1)[-1]

    # Guess language of file
    language = None
    if ext in EXTS:
        language = EXTS[ext]
    elif basename in EXTS:
        language = EXTS[basename]
    elif "." not in basename:
        language = Language.Text

    if language is None:
        return ("Unknown", 0, 0, 0)

    # Get comments config
    config = CONFIGS.get(language)
    # print(basename, language, config)

    # Only count blank/full lines
    with open(filepath, mode="rb") as code_file:
        if config is None:
            for line in code_file:
                if len(line) == 0 or line.isspace():
                    blank += 1
                else:
                    code += 1
        else:
            short, long = config
            # Take care of short comments only
            if long is None and short is not None:
                for line in code_file:
                    if len(line) == 0 or line.isspace():
                        blank += 1
                    elif short in line:
                        # There is a comment symbol
                        comment_start = line.index(short)
                        if line[:comment_start].isspace():
                            comments += 1
                        else:
                            code += 1
                    else:
                        code += 1
            else:
                opening, closing = long
                in_comment = False
                for line in code_file:
                    # TODO - take care of closing/opening on same line. The current
                    # heuristics are too naive and won't handle some corner cases
                    if in_comment:
                        comments += 1
                        if closing in line:
                            in_comment = False
                    elif opening in line:
                        in_comment = True
                        # Check if this is only a comment
                        comment_start = line.index(opening)
                        if line[:comment_start].isspace():
                            comments += 1
                        else:
                            code += 1
                    elif len(line) == 0 or line.isspace():
                        blank += 1
                    elif short is not None and short in line:
                        # There is a comment symbol
                        comment_start = line.index(short)
                        if line[:comment_start].isspace():
                            comments += 1
                        else:
                            code += 1
                    else:
                        code += 1
    return (language, blank, comments, code)


def main():
    path = sys.argv[-1]
    cpp = 0
    comments = 0
    counts = defaultdict(lambda: [0, 0, 0, 0])
    print(len(list(walk(path=path))))
    return
    for filepath in walk(path=path):
        try:
            (language, blank, comments, code) = process_file(filepath)
            counter = counts[language]
            counter[0] += 1  # total files for this language
            counter[1] += blank
            counter[2] += comments
            counter[3] += code
        except FileNotFoundError:
            pass

    # Display results
    print(
        "--------------------------------------------------------------------------------"
    )
    print("Language\t\tFiles\t\tLines\t\tBlank\t\tComment\t\tCode")
    print(
        "--------------------------------------------------------------------------------"
    )
    total_blanks = 0
    total_comments = 0
    total_code = 0
    total_lines = 0
    total_files = 0
    entries = []
    for language, counter in counts.items():
        files, blanks, comments, code = counter
        lines = blanks + comments + code
        total_blanks += blank
        total_comments += comments
        total_code += code
        total_lines += lines
        total_files += files
        entries.append((language, files, lines, blanks, comments, code))
    entries.sort(reverse=True, key=lambda e: e[5])
    for language, files, lines, blanks, comments, code in entries:
        print(f"{language}\t\t{files}\t\t{lines}\t\t{blanks}\t\t{comments}\t\t{code}")

    print(
        "--------------------------------------------------------------------------------"
    )
    print(
        f"Total\t\t{total_files}\t\t{total_lines}\t\t{total_blanks}\t\t{total_comments}\t\t{total_code}"
    )
    print(
        "--------------------------------------------------------------------------------"
    )


if __name__ == "__main__":
    main()
