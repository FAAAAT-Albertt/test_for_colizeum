# Добавление нового поля в высоконагруженную таблицу Django

## Описание
Этот документ описывает процесс безопасного добавления нового поля (`status`) в модель Django, связанной с активно используемой таблицей (~1 млн записей). Методика минимизирует блокировки базы данных и предотвращает простой приложения.

## Шаги внедрения

### 1. Добавление поля без значений по умолчанию

Редактируем модель Django, добавляя новое поле с `null=True`:

```python
from django.db import models

class MyModel(models.Model):
    # Добавляем поле, но временно разрешаем null
    status = models.IntegerField(null=True)
```

Создаём и применяем миграцию:

```bash
python manage.py makemigrations
python manage.py migrate
```

На данном этапе поле появится в БД, но будет пустым (`NULL`). Это изменение происходит быстро и без блокировки.

---

### 2. Постепенное заполнение нового поля

Чтобы избежать нагрузки на базу данных, обновляем данные партиями:

```python
from django.db import transaction
from myapp.models import MyModel

BATCH_SIZE = 10000  # Размер партии

while True:
    with transaction.atomic():
        updated_rows = MyModel.objects.filter(status__isnull=True)[:BATCH_SIZE].update(status=1)
    if updated_rows == 0:
        break  # Выход, если больше нечего обновлять
```

Этот скрипт можно запустить как Django management command или выполнить в консоли.

Таким образом, данные обновляются постепенно, не перегружая базу.

---

### 3. Убираем `null=True` и добавляем `default=1`

После завершения обновления данных обновляем модель:

```python
class MyModel(models.Model):
    status = models.IntegerField(default=1)
```

Создаём и применяем новую миграцию:

```bash
python manage.py makemigrations
python manage.py migrate
```

Теперь все новые записи будут автоматически получать `status=1`, а существующие уже обновлены.

---

### 4. Устанавливаем `NOT NULL` в базе данных (опционально)

Для гарантии целостности данных можно выполнить SQL-запрос:

```sql
ALTER TABLE myapp_mymodel ALTER COLUMN status SET NOT NULL;
```

Этот шаг можно выполнить отдельно после проверки, что все записи заполнены.

---

### 5. Очистка кода

После успешного обновления:
- Удаляем временные скрипты по заполнению данных.
- Проверяем, что приложение корректно работает с новым полем.
