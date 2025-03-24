### **1. Создание Docker-образа**
Создадим `Dockerfile` для упаковки Flask-приложения в контейнер

### **2. Сборка и загрузка образа**
Собираем Docker-образ:

```sh
docker build -t myflaskapp .
yc container registry create --name myregistry
yc iam create-token | docker login --username oauth --password-stdin cr.yandex
docker tag myflaskapp cr.yandex/myregistry/myflaskapp:v1
docker push cr.yandex/myregistry/myflaskapp:v1
```

---

### **3. Создание Kubernetes-манифестов**

#### **3.1 Deployment**
Создадим `deployment.yaml`

#### **3.2 Service**
Создадим `service.yaml` для доступа к приложению внутри кластера

#### **3.3 Ingress**
Создадим `ingress.yaml` для доступа извне

---

### **4. Деплой в Kubernetes**
Применяем манифесты:

```sh
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
```

---

### **5. Проверка развертывания**
Проверяем, что поды работают:

```sh
kubectl get pods
```

Проверяем, что сервис доступен:

```sh
kubectl get svc
```

Проверяем, что Ingress настроен:

```sh
kubectl get ingress
```

---

### **6. Доступ к приложению**
Если у вас настроен `Ingress Controller`, добавьте в `/etc/hosts`:

```
127.0.0.1 flask.local
```

Теперь приложение доступно по адресу:

```
http://flask.local
```