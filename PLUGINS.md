# Zen C Plugin System Guide

Zen C offers a powerful, low-overhead plugin system that allows you to extend the language syntax and transpilation process. Plugins act as compile-time hooks that can parse arbitrary text blocks and generate standard C code.

## Quick Start

### Using a Plugin

To use a plugin, import it using the `import plugin` syntax. Zen C supports both native Zen C plugins (`.zc`) and legacy C plugins (`.so`).

```zc
import plugin "plugins/lisp" as lisp

fn main() {
    lisp! {
        (defun square (x) (* x x))
        (print (square 10))
    }
}
```

The syntax `alias! { ... }` invokes the plugin. The content inside the braces is passed as a raw string to the plugin's transpiler function.

---

## Creating a Plugin

Modern Zen C plugins are written natively in Zen C (`.zc`). This allows you to use high-level features like string interpolation and multiline blocks to generate C code cleanly.

### API Reference (`std/plugin.zc`)

The core API consists of a few structured types that provide context and output streams.

```zc
struct ZApi {
    api_version: u32,
    filename: char*,
    current_line: int,
    out: void*,         // Primary output stream (injects code at call site)
    hoist_out: void*,   // Hoisted output stream (injects code at top level)
    
    // Diagnostic reporting
    error: fn*(ZApi*, char*, ...),
    warn: fn*(ZApi*, char*, ...),
    note: fn*(ZApi*, char*, ...),

    config: ZConfig,
    user_data: void*
}

struct ZPlugin {
    name: char[256],
    handler: fn*(char*, ZApi*),
    hover_handler: fn*(char*, int, int) -> char*
}
```

### Implementing a Brainfuck Plugin

Let's implement a plugin that compiles Brainfuck code directly into optimized C logic.

#### 1. Define the Transpiler

A native Zen C plugin uses `f-strings` or `triple-quotes` to emit code.

```zc
import "std/plugin.zc"

fn bf_transpile(input_body: char*, api: ZApi*) {
    let out = api.out;
    " { "; // Shorthand println to 'out'
    " static unsigned char tape[30000] = {0}; ";
    " unsigned char *ptr = tape; ";

    let c = input_body;
    while c[0] != 0 {
        match c[0] {
            '>' => " ++ptr; ",
            '<' => " --ptr; ",
            '+' => " ++*ptr; ",
            '-' => " --*ptr; ",
            '.' => " putchar(*ptr); ",
            ',' => " *ptr = getchar(); ",
            '[' => " while (*ptr) { ",
            ']' => " } ",
            _   => {}
        }
        c = &c[1];
    }
    " } ";
}
```

#### 2. LSP Hover Provider (Optional)

You can provide a `hover_handler` to display markdown tooltips when a user hovers over syntax inside the plugin block. The handler receives the raw text body and the 0-indexed line/column relative to the start of the block.

```zc
fn bf_hover(body: char*, line: int, col: int) -> char* {
    let p = body;
    let r = 0; let c = 0;
    while p[0] != 0 {
        if r == line && c == col {
            match (int)p[0] {
                '>' => return "**:ptr++**: Increment the data pointer.",
                '<' => return "**:ptr--**: Decrement the data pointer.",
                // ...
                _   => return NULL
            }
        }
        if p[0] == 10 { r++; c = 0; } else { c++; }
        p = &p[1];
    }
    return NULL;
}
```

#### 3. Register and Export

Every plugin must export a `z_plugin_init` function.

```zc
let bf_plugin = ZPlugin {
    name: "brainfuck",
    handler: bf_transpile,
    hover_handler: bf_hover
};

@export
fn z_plugin_init() -> ZPlugin* {
    return &bf_plugin;
}
```

---

## Best Practices: Clang and TCC Compatibility

> [!IMPORTANT]
> **Hoisting Function Definitions**
>
> If your plugin generates C function definitions (like a Lisp `defun`), you **MUST** write them to `api.hoist_out`. 
>
> Writing a function definition to `api.out` inside a Zen C block will result in a "nested function," which is a GCC extension not supported by standard C compilers like Clang or TCC.

### Correct Hoisting Pattern:

```zc
fn lisp_transpile(body: char*, api: ZApi*) {
    if (is_defun(body)) {
        // Emit implementation to the top-level hoist buffer
        fputs("static LVal my_func() { ... }", api.hoist_out);
        
        // Return a reference or identifier to the call site
        fputs("my_func", api.out);
    }
}
```

---

## Building and Testing

### Building
Zen C automatically detects and compiles `.zc` plugins when imported. However, you can manually build them with the `-shared` flag:

```bash
zc build my_plugin.zc -shared -o my_plugin.so
```

### Unified Testing
Maintain a clean test suite using the `make test-plugins` target in the core repository, or by creating a dedicated verification file:

```bash
# Run the unified plugin suite
make test-plugins CC=clang
```

### Multiline Emission Example
Use triple-quoted strings for large blocks of boilerplate:

```zc
fputs(f"""
    /* Custom Runtime for {api.filename} */
    typedef struct {{ ... }} Runtime;
    static void init() {{ ... }}
""", api.hoist_out);
```
