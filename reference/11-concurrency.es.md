+++
title = "11. Concurrencia (Async/Await)"
weight = 11
+++


# 11. Concurrencia (Async/Await)

Zen C utiliza un modelo de **corrutina sin pila** para async/await -- sin pool de hilos, sin dependencia de pthread.
Esto significa que las funciones asíncronas se transforman en tiempo de compilación en máquinas de estado, no en hilos.

#### Sintaxis

Declara una función asíncrona con `async fn` y espera su resultado con la palabra clave `await`:

```zc
async fn fetch_data() -> string {
    return "Datos";
}

fn main() {
    let result = await fetch_data();
}
```

{% alert(type="note") %}
A diferencia de los modelos basados en hilos, `await` en Zen C es un **bucle de sondeo bloqueante** que ejecuta
toda la función asíncrona hasta completarse. Esto es intencional -- hace que el flujo de control sea
predecible y elimina la necesidad de un ejecutor o pool de hilos.
{% end %}

#### Cómo funciona

Una `async fn` es transformada por el compilador en una **máquina de estados**. Cada
punto `await` se convierte en una transición de estado. El `Future` resultante
contiene el estado, los parámetros y los sub-futures para las llamadas awaitadas.

#### Patrón secuencial

```zc
async fn task(n: int) -> int {
    return n * 2;
}

fn main() {
    let a = await task(5);
    let b = await task(a);
}
```