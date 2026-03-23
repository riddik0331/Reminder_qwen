# 📱 Збірка APK для Android

Цей документ описує процес створення APK файлу для встановлення на Android телефон.

## 📋 Вимоги

### Варіант 1: Локальна збірка (Linux/Mac)
- Ubuntu/Debian/MacOS
- Python 3.8+
- Buildozer
- Android SDK

### Варіант 2: GitHub Actions (Будь-яка ОС)
- GitHub акаунт
- Браузер

---

## 🔧 Варіант 1: Локальна збірка на Linux

### Крок 1: Встановлення залежностей

```bash
# Оновлення системи
sudo apt update && sudo apt upgrade -y

# Встановлення залежностей
sudo apt install -y \
    build-essential \
    git \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libswscale-dev \
    libavcodec-dev \
    libavformat-dev \
    libz-dev \
    libjpeg-dev \
    libffi-dev \
    cmake \
    autoconf \
    automake \
    pkg-config \
    openjdk-17-jdk \
    autoconf-archive \
    python3-pip

# Встановлення Python залежностей
pip3 install --user buildozer cython
```

### Крок 2: Збірка APK

```bash
# Перейдіть в директорію проекту
cd my-python-app

# Ініціалізація (якщо потрібно)
buildozer init

# Збірка APK
buildozer -v android debug

# Або для release версії (потребує підпису)
buildozer -v android release
```

### Крок 3: Отримання APK

Після збірки APK файл буде в папці:
```
bin/EventsReminder-1.0.0-debug.apk
```

---

## ☁️ Варіант 2: Збірка через GitHub Actions (Рекомендовано для Windows)

### Крок 1: Створіть тег версії

```bash
# В терміналі проекту
git tag v1.0.0
git push origin v1.0.0
```

### Крок 2: Запустіть GitHub Actions

1. Відкрийте https://github.com/riddik0331/Reminder_qwen/actions
2. Оберіть workflow **"Build Android APK"**
3. Натисніть **"Run workflow"**
4. Оберіть гілку `master`
5. Натисніть **"Run workflow"**

### Крок 3: Завантажте APK

Після завершення збірки (15-30 хвилин):
1. Перейдіть на вкладку **Actions**
2. Оберіть останній запуск
3. У секції **Artifacts** знайдіть `app-debug`
4. Завантажте APK файл

---

## 📲 Встановлення на телефон

### Спосіб 1: Через USB
1. Увімкніть **Невідомі джерела** в налаштуваннях телефону
2. Під'єднайте телефон до ПК
3. Скопіюйте APK файл на телефон
4. Відкрийте APK на телефоні та встановіть

### Спосіб 2: Через Google Drive
1. Завантажте APK на Google Drive
2. Відкрийте Drive на телефоні
3. Натисніть на APK файл
4. Дозвольте встановлення

---

## ⚙️ Налаштування в buildozer.spec

### Змінити назву додатку:
```ini
title = Ваша Назва
```

### Змінити package name:
```ini
package.name = вашдодаток
package.domain = com.вашеім'я
```

### Змінити версію:
```ini
version = 1.0.1
```

### Додати іконку:
1. Створіть папку `data/`
2. Додайте файл `icon.png` (512x512 px)
3. Розкоментуйте рядок в buildozer.spec:
```ini
icon.filename = %(source.dir)s/data/icon.png
```

---

## 🐛 Вирішення проблем

### Помилка: "No module named 'kivy'"
```bash
pip install --upgrade kivy
```

### Помилка: "SDK not found"
```bash
# Buildozer завантажить SDK автоматично при першій збірці
# Просто запустіть buildozer ще раз
```

### Помилка: "Java not found"
```bash
sudo apt install openjdk-17-jdk
```

### Збірка зависає
```bash
# Очистіть кеш і спробуйте ще раз
buildozer android clean
buildozer -v android debug
```

---

## 📦 Release версія (для публікації)

Для створення підписаної release версії:

1. Створіть keystore:
```bash
keytool -genkey -v -keystore my-release-key.keystore -alias alias_name -keyalg RSA -keysize 2048 -validity 10000
```

2. В buildozer.spec додайте:
```ini
android.release_artifact = apk
android.signing.release_keystore_path = /path/to/my-release-key.keystore
android.signing.release_keyalias = alias_name
```

3. Зберіть:
```bash
buildozer -v android release
```

---

## 📊 Розмір APK

- **Debug APK**: ~15-25 MB
- **Release APK**: ~10-15 MB (після оптимізації)

Для зменшення розміру:
- Видаліть зайві файли з проекту
- Використовуйте ProGuard
- Оптимізуйте зображення

---

## ✅ Перевірка перед збіркою

Перед збіркою переконайтесь:
- [ ] Всі файли проекту в репозиторії
- [ ] requirements.txt оновлений
- [ ] buildozer.spec налаштований
- [ ] Тестування на емуляторі пройшло

---

## 📞 Контакти

Якщо виникли проблеми - створіть Issue на GitHub або зверніться до документації:
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)
