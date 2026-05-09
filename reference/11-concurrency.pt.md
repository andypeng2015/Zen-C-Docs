+++
title = "11. Concorrência (Async/Await)"
weight = 11
+++


# 11. Concorrência (Async/Await)

Zen C usa um modelo de **corrotina sem pilha** para async/await -- sem pool de threads, sem dependência de pthread.
Isso significa que funções assíncronas são transformadas em tempo de compilação em máquinas de estado, não em threads.

#### Sintaxe

Declare uma função assíncrona com `async fn` e aguarde seu resultado com a palavra-chave `await`:

```zc
async fn fetch_data() -> string {
    return "Dados";
}

fn main() {
    let result = await fetch_data();
}
```

{% alert(type="note") %}
Ao contrário de modelos baseados em threads, o `await` do Zen C é um **loop de polling bloqueante** que executa
toda a função assíncrona até a conclusão. Isso é intencional -- torna o fluxo de controle
previsível e elimina a necessidade de um executor ou pool de threads.
{% end %}

#### Como funciona

Uma `async fn` é transformada pelo compilador em uma **máquina de estados**. Cada
ponto `await` torna-se uma transição de estado. O `Future` resultante
contém o estado, os parâmetros e os sub-futures para chamadas aguardadas.

#### Padrão sequencial

```zc
async fn task(n: int) -> int {
    return n * 2;
}

fn main() {
    let a = await task(5);
    let b = await task(a);
}
```