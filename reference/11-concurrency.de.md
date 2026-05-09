+++
title = "11. Nebenläufigkeit (Async/Await)"
weight = 11
+++


# 11. Nebenläufigkeit (Async/Await)

Zen C verwendet ein **stackless coroutine**-Modell für Async/Await -- kein Thread-Pool, keine pthread-Abhängigkeit.
Das bedeutet, dass asynchrone Funktionen zur Compile-Zeit in Zustandsmaschinen umgewandelt werden, nicht in Threads.

#### Syntax

Deklariere eine asynchrone Funktion mit `async fn` und erwarte ihr Ergebnis mit dem Schlüsselwort `await`:

```zc
async fn fetch_data() -> string {
    return "Daten";
}

fn main() {
    let result = await fetch_data();
}
```

{% alert(type="note") %}
Im Gegensatz zu thread-basierten Modellen ist Zen C's `await` eine **blockierende Poll-Schleife**, die die
gesamte asynchrone Funktion bis zum Ende ausführt. Dies ist beabsichtigt -- es macht den Kontrollfluss
vorhersagbar und eliminiert die Notwendigkeit einer Laufzeitumgebung oder eines Thread-Pools.
{% end %}

#### Wie es funktioniert

Eine `async fn` wird vom Compiler in eine **Zustandsmaschine** umgewandelt. Jeder
`await`-Punkt wird zu einem Zustandsübergang. Der resultierende `Future`-Struct
enthält den Zustand, die Parameter und die Sub-Futures für awaitierte Aufrufe.

#### Sequentielles Muster

```zc
async fn task(n: int) -> int {
    return n * 2;
}

fn main() {
    let a = await task(5);
    let b = await task(a);
}
```