+++
title = "11. 并发 (Async/Await)"
weight = 11
+++


# 11. 并发 (Async/Await)

Zen C 使用**无栈协程**模型实现 async/await -- 无需线程池，无需 pthread 依赖。
这意味着异步函数在编译时被转换为状态机，而不是线程。

#### 语法

使用 `async fn` 声明异步函数，并使用 `await` 关键字等待其结果：

```zc
async fn fetch_data() -> string {
    return "数据";
}

fn main() {
    let result = await fetch_data();
}
```

{% alert(type="note") %}
与基于线程的模型不同，Zen C 的 `await` 是一个**阻塞轮询循环**，会执行
整个异步函数直到完成。这是有意为之 -- 它使控制流可预测
并消除了对运行时执行器或线程池的需求。
{% end %}

#### 工作原理

`async fn` 会被编译器转换为一个**状态机**。每个
`await` 点成为一个状态转换。生成的 `Future` 结构体
包含状态、参数以及被等待调用的子 Future。

#### 顺序模式

```zc
async fn task(n: int) -> int {
    return n * 2;
}

fn main() {
    let a = await task(5);
    let b = await task(a);
}
```