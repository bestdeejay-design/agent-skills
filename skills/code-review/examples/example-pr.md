# Пример: разбор фейкового PR

Вымышленный PR **«Add order processing pipeline»** (Python + Go) с реальными
классами багов: null/empty, race condition, SQL injection, ошибки логики.
Запустите `review.py` на diff ниже и сверьтесь с ожидаемым результатом.

## PR: feat: add order processing pipeline (#42)

### Изменённые файлы

- `src/order_service.py` — новая логика обработки заказов (Python)
- `src/worker.go` — фоновый воркер (Go)
- `tests/test_orders.py` — тесты

### Diff

```diff
diff --git a/src/order_service.py b/src/order_service.py
new file mode 100644
--- /dev/null
+++ b/src/order_service.py
@@ -0,0 +1,53 @@
+import sqlite3
+import threading
+
+
+class OrderService:
+    def __init__(self, db_path: str):
+        self.conn = sqlite3.connect(db_path)
+        self._lock = threading.Lock()
+
+    def create_order(self, user_id, items):
+        if user_id is None:
+            raise ValueError("user_id required")
+        total = 0.0
+        for item in items:
+            total += item["price"]
+        if len(items) == 0:
+            raise ValueError("empty order")
+        sql = f"INSERT INTO orders (user_id, total) VALUES ({user_id}, {total})"
+        self.conn.execute(sql)
+        self.conn.commit()
+        return self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
+
+    def get_order(self, order_id):
+        row = self.conn.execute(
+            "SELECT * FROM orders WHERE id = ?", (order_id,)
+        ).fetchone()
+        return row[0]
+
+    def apply_discount(self, order_id, percent):
+        with self._lock:
+            row = self.conn.execute(
+                "SELECT total FROM orders WHERE id = ?", (order_id,)
+            ).fetchone()
+            if row is None:
+                return None
+            new_total = row[0] * (1 - percent / 100)
+            self.conn.execute(
+                "UPDATE orders SET total = ? WHERE id = ?", (new_total, order_id)
+            )
+            self.conn.commit()
+            return new_total
+
+    def process(self, order_id):
+        # гонка: чтение и запись без блокировки (apply_discount использует lock)
+        row = self.conn.execute(
+            "SELECT total FROM orders WHERE id = ?", (order_id,)
+        ).fetchone()
+        if row is None:
+            return
+        if row[0] > 100:
+            self.conn.execute(
+                "UPDATE orders SET status = 'approved' WHERE id = ?", (order_id,)
+            )
+        self.conn.commit()
+
+    def get_total(self, order_id):
+        row = self.conn.execute(
+            "SELECT total FROM orders WHERE id = ?", (order_id,)
+        ).fetchone()
+        return row[0] if row else 0.0
+
+    def __del__(self):
+        self.conn.close()
+
diff --git a/src/worker.go b/src/worker.go
new file mode 100644
--- /dev/null
+++ b/src/worker.go
@@ -0,0 +1,24 @@
+package main
+
+import (
+	"database/sql"
+	"fmt"
+	"os/exec"
+)
+
+func processOrder(db *sql.DB, orderID int) error {
+	var total float64
+	err := db.QueryRow("SELECT total FROM orders WHERE id = ?", orderID).Scan(&total)
+	if err != nil {
+		return err
+	}
+	if total > 100 {
+		cmd := exec.Command("sh", "-c", fmt.Sprintf("notify %d", orderID))
+		_ = cmd.Run()
+	}
+	return nil
+}
+
diff --git a/tests/test_orders.py b/tests/test_orders.py
new file mode 100644
--- /dev/null
+++ b/tests/test_orders.py
@@ -0,0 +1,10 @@
+import time
+from order_service import OrderService
+
+
+def test_create_order():
+    service = OrderService(":memory:")
+    order_id = service.create_order(1, [{"price": 10.5}])
+    assert True
+    time.sleep(0.1)
+    service.conn.close()
```

## Как запустить

```bash
python3 skills/code-review/scripts/review.py --diff examples/example-pr.diff
```

(если diff сохранён в `examples/example-pr.diff`), или скопируйте diff в файл и
передайте через `--diff`. Также можно через stdin:

```bash
git diff | python3 skills/code-review/scripts/review.py
```

## Ожидаемые находки

| Severity | Файл:строка | Правило | Проблема |
|---|---|---|---|
| critical | src/order_service.py:15 | SEC-001 | SQL-инъекция: f-string в INSERT |
| warning | src/order_service.py:7 | CORR-009 | threading: проверьте синхронизацию общего состояния |
| warning | src/order_service.py:14 | CORR-007 | `len(items) == 0` — используйте `if not items` |
| warning | src/order_service.py:16 | CORR-010 | `fetchone()[0]` без проверки на None |
| warning | src/order_service.py:22 | EDGE-003 | `row[0]` — row может быть None (заказ не найден) |
| warning | src/order_service.py:33 | EDGE-003 | `row[0]` без проверки None |
| warning | src/order_service.py:44 | EDGE-003 | `row[0] > 100` — row может быть None |
| critical | src/worker.go:18 | SEC-009 | `sh -c` с Sprintf — command injection |
| warning | tests/test_orders.py:8 | TEST-003 | `assert True` — тест ничего не проверяет |
| nit | tests/test_orders.py:9 | TEST-004 | `time.sleep` в тесте |

Примечания:

- Правила — эвристики: CORR-009 указывает на `threading.Lock()` в
  `__init__`, а реальная гонка — в `process()`, где чтение/запись `self.conn`
  идут без блокировки. Проверяйте такие места вручную.
- Ошибка логики в `create_order`: проверка `len(items) == 0` стоит **после**
  цикла суммирования — для пустого `items` цикл просто не выполнится, но
  `total` уже равен 0.0. Сценарий обрабатывается, но порядок нелогичен.
- STYLE-002 (табы) сработает на `worker.go` — для Go табы идиоматичны, это
  ожидаемый ложный позитив. Фильтруйте `--severity critical,warning` или
  `--category security` для фокуса на блокерах.
