+++
title = "16. MISRA Rules"
weight = 16
+++

# 16. MISRA Rules

Zen C includes a **MISRA C:2012 compliance mode** activated with the `--misra` flag.
In addition to standard MISRA checks, the compiler enforces several **Zen-specific rules**
that promote safer, more maintainable code.

#### Enabling MISRA mode

```bash
zc build app.zc --misra
```

Violations are reported as compiler errors at compile time:

```text
error: MISRA Rule Zen 2.2: tuple with 3 or more fields shall be replaced
       with a named struct (use 'struct' instead of positional tuple)
  --> app.zc:5:1
   |
 5 | fn get_stats() -> (int, int, int) { ... }
```

{% alert(type="note") %}
The MISRA standard text is copyright MISRA Consortium Ltd. Zen C's implementation
checks conformance but does not reproduce the standard. For the official rule
definitions, refer to the [MISRA C:2012](https://www.misra.org.uk/) documentation.
{% end %}

#### Zen-Specific Rules

These rules are unique to Zen C. Each rule is checked when `--misra` is active.

#### Zen 1.1 -- No raw blocks

Forbids `raw { }` blocks that bypass the transpiler.

```zc
// ❌ Violation:
fn main() {
    raw { int x = 10; }
}

// ✅ Fix: use native Zen C constructs
fn main() {
    let x = 10;
}
```

#### Zen 1.2 -- No plugin blocks

Forbids `plugin ... end` blocks, which execute arbitrary build-time code.

```zc
// ❌ Violation:
plugin my_plugin

// ✅ Fix: implement functionality as a regular function or import a library
import "std/some_module.zc"
```

#### Zen 1.3 -- Exhaustive enum match

Forbids the `_` wildcard in `match` on enum types -- all variants must be handled explicitly.

```zc
enum Color { Red; Green; Blue; }

// ❌ Violation:
fn describe(c: Color) {
    match c {
        Color::Red => { println "red"; }
        Color::Green => { println "green"; }
        // Missing Blue -- Zen 1.3
    }
}

// ✅ Fix: handle all variants
fn describe(c: Color) {
    match c {
        Color::Red => { println "red"; }
        Color::Green => { println "green"; }
        Color::Blue => { println "blue"; }
    }
}
```

#### Zen 1.4 -- No preprocessor directives

Forbids C preprocessor directives (`#define`, `#include`, `#if`, etc.).
Use Zen's `import` and `def` instead.

```zc
// ❌ Violation:
#define BUFFER_SIZE 256
#include <stdio.h>

// ✅ Fix:
def BUFFER_SIZE = 256;
import "std/io.zc"
```

#### Zen 1.5 -- No `var` / `const` for declarations

The `var` and `const` keywords are deprecated for variable/constant declarations.
Use `let` for variables and `def` for compile-time constants.

```zc
// ❌ Violation:
var x = 10;
const MAX = 100;

// ✅ Fix:
let x = 10;
def MAX = 100;
```

> The `const` keyword remains valid as a **type qualifier** for C interop
> (e.g., `const int` means "pointer to const int" in FFI declarations).

#### Zen 1.8 -- No identifier shadowing

Forbids declaring a name that hides one from an outer scope.

```zc
// ❌ Violation:
let x = 10;
if true {
    let x = 20;  // shadows outer x
}

// ✅ Fix: use a distinct name
let x = 10;
if true {
    let inner_x = 20;
}
```

#### Zen 2.1 -- No reserved identifiers

Forbids identifiers starting with `__`, `_[A-Z]`, or `_z_`, which are reserved
for the compiler and C implementation.

```zc
// ❌ Violation:
let __my_var = 10;
let _Reserved = 20;
let _z_internal = 30;

// ✅ Fix: use non-reserved names
let my_var = 10;
let reserved = 20;
let internal = 30;
```

#### Zen 2.2 -- Tuple size limit

Tuples with **3 or more fields** shall not be used as function return types or
parameters. Use a named struct instead. 2-tuples are exempt.

```zc
// ❌ Violation:
fn get_stats() -> (int, int, int) { ... }

// ❌ Violation:
fn process(p: (int, string, bool)) { ... }

// ✅ OK:
struct Stats { sum: int; avg: int; max: int; }
fn get_stats() -> Stats { ... }

// ✅ OK (2-tuples exempt):
fn get_pair() -> (int, int) { ... }
```

#### Zen 2.3 -- String comparison

`string == string` shall not be used. Use `strcmp()` instead.

```zc
// ❌ Violation:
if a == b { ... }  // when a, b are string

// ✅ Fix:
if strcmp(a, b) == 0 { ... }

// ✅ OK (non-string types):
if x == y { ... }   // int, bool, pointer comparisons are safe
```

## Standard MISRA C:2012 Coverage

The compiler checks the following standard MISRA C:2012 rules.
Click on a chapter to expand the rule list.

{% misra_table() %}

For the complete rule text, refer to the official
[MISRA C:2012](https://www.misra.org.uk/) documentation.
