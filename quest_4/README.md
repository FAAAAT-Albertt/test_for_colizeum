## **Диагностика SQL-запроса в PostgreSQL**

### **1. Проверка активных запросов**

Для начала необходимо проверить, какие запросы выполняются в базе данных, а также есть ли блокировки. Выполните следующий запрос:

```sql
SELECT pid, age(clock_timestamp(), query_start) AS duration, state, wait_event, query
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY query_start;
```

_Этот запрос покажет все выполняющиеся запросы, их длительность и возможные блокировки. Обратите внимание на колонку `wait_event`, если ваш запрос, например, `ALTER TABLE`, выполняется долго._

### **2. Проверка блокировок в таблице**

Если ваш запрос заблокирован, нужно выяснить, кто держит блокировку. Используйте следующий запрос:

```sql
SELECT blockingl.pid AS blocking_pid, blockedl.pid AS blocked_pid, blocked_activity.query AS blocked_query
FROM pg_locks blockedl
JOIN pg_stat_activity blocked_activity ON blockedl.pid = blocked_activity.pid
JOIN pg_locks blockingl ON blockedl.locktype = blockingl.locktype 
    AND blockedl.database IS NOT DISTINCT FROM blockingl.database
    AND blockedl.relation IS NOT DISTINCT FROM blockingl.relation
    AND blockedl.page IS NOT DISTINCT FROM blockingl.page
    AND blockedl.tuple IS NOT DISTINCT FROM blockingl.tuple
    AND blockedl.transactionid IS NOT DISTINCT FROM blockingl.transactionid
    AND blockedl.classid IS NOT DISTINCT FROM blockingl.classid
    AND blockedl.objid IS NOT DISTINCT FROM blockingl.objid
    AND blockedl.objsubid IS NOT DISTINCT FROM blockingl.objsubid
    AND blockedl.pid <> blockingl.pid
JOIN pg_stat_activity blocking_activity ON blockingl.pid = blocking_activity.pid;
```

_Этот запрос покажет, какой процесс блокирует ваш запрос, например, `ALTER TABLE`._

### **3. Проверка размера таблицы и индексов**

Если таблица очень большая, изменение её структуры может занять значительное время. Для проверки размера таблицы выполните:

```sql
SELECT pg_size_pretty(pg_total_relation_size('my_table'));
```

_Этот запрос покажет общий размер таблицы, включая данные, индексы и дополнительные объекты._

### **4. Проверка активных транзакций**

Если перед `ALTER TABLE` запущена длительная транзакция, она может блокировать выполнение изменений. Проверьте активные транзакции с помощью следующего запроса:

```sql
SELECT * FROM pg_stat_activity 
WHERE state = 'active' 
  AND backend_xid IS NOT NULL;
```

_Этот запрос отобразит все активные транзакции в базе данных._

### **5. Проверка доступности индексов**

Если в таблице много индексов, PostgreSQL может долго перестраивать их при изменении структуры. Для проверки индексов таблицы используйте следующий запрос:

```sql
SELECT indexname, pg_size_pretty(pg_relation_size(indexrelid)) 
FROM pg_stat_user_indexes 
WHERE relname = 'my_table';
```

_Этот запрос покажет информацию о всех индексах в таблице и их размерах._

### **6. Решение проблем**

**1. Если есть блокировки**:
   - Завершите процесс, который блокирует ваш запрос `ALTER TABLE`:
   ```sql
   SELECT pg_terminate_backend(<blocking_pid>);
   ```

**2. Если таблица слишком большая**:
   - Добавьте колонку без ограничения `NOT NULL`:
   ```sql
   ALTER TABLE my_table ADD COLUMN status INTEGER NULL;
   ```
   - Заполните её партиями (например, по 10,000 строк):
   ```sql
   UPDATE my_table SET status = 1 WHERE status IS NULL LIMIT 10000;
   ```
   - Затем, после того как данные будут обновлены, установите ограничение `NOT NULL`:
   ```sql
   ALTER TABLE my_table ALTER COLUMN status SET NOT NULL;
   ```

**3. Если запрос выполняется слишком долго**:
   - Проверьте, когда в последний раз выполнялся `VACUUM ANALYZE`, чтобы очистить таблицу и обновить статистику:
   ```sql
   VACUUM ANALYZE my_table;
   ```
   - Попробуйте использовать команду с `CONCURRENTLY` (если применимо, например, для индексов), чтобы избежать блокировки:

   Для создания индекса без блокировки:
   ```sql
   CREATE INDEX CONCURRENTLY my_index ON my_table (column_name);
   ```

---

Эти шаги помогут вам диагностировать и устранить возможные проблемы с блокировками или длительными запросами в PostgreSQL.