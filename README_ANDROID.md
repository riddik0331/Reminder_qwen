# 📱 Events Reminder - Android Version

Це Android-версія програми Events Reminder.

## ⚠️ Важливо

Ця гілка (`android`) призначена **тільки для збірки APK** на Android. Windows-версія знаходиться в гілці `master`.

## 🔄 Відмінності від desktop версії

### Видалено:
- ❌ Системний трей (pystray) - не існує на Android
- ❌ tray.py - не потрібен
- ❌ Обробник закриття вікна

### Додано:
- ✅ Android permissions (VIBRATE, FOREGROUND_SERVICE, etc.)
- ✅ Native Android notifications через plyer
- ✅ Оптимізація для мобільних екранів

---

## 📦 Збірка APK

### Спосіб 1: GitHub Actions (Рекомендовано)

1. **Створіть тег версії:**
```bash
git checkout android
git tag v1.0.0
git push origin v1.0.0
```

2. **GitHub Actions автоматично запустить збірку**
   - Відкрийте: https://github.com/riddik0331/Reminder_qwen/actions
   - Зачекайте 20-30 хвилин
   - Завантажте APK з артефактів

### Спосіб 2: Локальна збірка (Linux)

```bash
# Встановіть Buildozer
pip install buildozer

# Перейдіть в директорию проекту
cd my-python-app

# Зберіть APK
buildozer -v android debug

# APK буде в папці bin/
```

---

## 📲 Встановлення на телефон

1. **Увімкніть невідомі джерела** в налаштуваннях телефону
2. **Завантажте APK** з GitHub Actions artifacts
3. **Відкрийте APK** на телефоні
4. **Дозвольте встановлення**

---

## 🔔 Сповіщення

Програма використовує **Android native notifications** через plyer:

- ✅ При запуску - перевірка подій сьогодні
- ✅ Щодня о 9:00 - автоматична перевірка
- ✅ Спливаючі повідомлення Android
- ✅ Налаштування в settings.json

### Налаштування сповіщень:

Файл `settings.json` (створюється автоматично):
```json
{
  "enabled": true,
  "notify_days_before": 1,
  "notify_time": "09:00",
  "notify_today": true,
  "notify_tomorrow": true
}
```

---

## 📁 Структура проекту

```
my-python-app/ (android branch)
├── main.py                 # Головна (без tray)
├── notifications.py        # Сповіщення (plyer)
├── models.py               # Моделі даних
├── screens/                # Екрани
├── widgets/                # Віджети
├── theme.py                # Теми
├── utils.py                # Утиліти
├── buildozer.spec          # Конфіг збірки
├── requirements.txt        # Залежності
└── data/
    └── events.json         # Події
```

---

## 🛠️ Вимоги для збірки

### GitHub Actions:
- GitHub акаунт
- Git встановлений

### Локальна збірка:
- Linux (Ubuntu/Debian)
- Python 3.8+
- Buildozer
- Android SDK (встановлюється автоматично)

---

## 📊 Характеристики APK

- **Розмір**: ~15-25 MB (debug)
- **Архітектури**: arm64-v8a, armeabi-v7a
- **Android API**: 24+ (Android 7.0+)
- **Орієнтація**: Portrait

---

## 🐛 Вирішення проблем

### Помилка: "Aidl not found"
Використовуйте GitHub Actions або Docker образ `kivy/buildozer:latest`

### Помилка: "SDK not found"
Buildozer завантажить SDK автоматично при першій збірці

### Збірка зависає
```bash
buildozer android clean
buildozer -v android debug
```

---

## 📞 Контакти

- **Desktop версія**: гілка `master`
- **Android версія**: гілка `android`
- **Issues**: https://github.com/riddik0331/Reminder_qwen/issues

---

## 📝 Примітки

- Windows-сповіщення (pystray) **не працюють** на Android
- Використовується **plyer.notification** для Android
- Tray icon **відсутній** на Android
- Закриття програми стандартне (кнопка Back)
