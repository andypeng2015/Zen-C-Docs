+++
title = "11. 並發 (Async/Await)"
weight = 11
+++


# 11. 並發 (Async/Await)

Zen C 使用**無棧協程**模型實現 async/await -- 無需執行緒池，無需 pthread 依賴。
這意味著非同步函數在編譯時被轉換為狀態機，而不是執行緒。

#### 語法

使用 `async fn` 宣告非同步函數，並使用 `await` 關鍵字等待其結果：

```zc
async fn fetch_data() -> string {
    return "資料";
}

fn main() {
    let result = await fetch_data();
}
```

{% alert(type="note") %}
與基於執行緒的模型不同，Zen C 的 `await` 是一個**阻塞輪詢循環**，會執行
整個非同步函數直到完成。這是有意為之 -- 它使控制流可預測
並消除了對執行時執行器或執行緒池的需求。
{% end %}

#### 工作原理

`async fn` 會被編譯器轉換為一個**狀態機**。每個
`await` 點成為一個狀態轉換。生成的 `Future` 結構體
包含狀態、參數以及被等待呼叫的子 Future。

#### 順序模式

```zc
async fn task(n: int) -> int {
    return n * 2;
}

fn main() {
    let a = await task(5);
    let b = await task(a);
}
```