# Kasa

A personal budget tracker for three currencies: Serbian dinar (RSD), euro and Russian ruble. It ships as an Android APK and the same page runs in a browser. The UI is in Russian.

- Wallets per currency, total in any currency, daily official rates with trend arrows.
- Expenses, income and currency exchanges (shows the loss vs. the official rate).
- Recurring payments with a first due date and an optional share (e.g. half of the rent), recurring income (salary that can be split into two dates), debts.
- Monthly spending limit warnings and a reminder to exchange money before dinars run out.
- First-run setup screen, light and dark themes, a sleeping cat on the tab bar.

**Privacy:** all records live in one file in the app's private storage (`allowBackup=false`). The only network request is the daily rate fetch, made by native code; the WebView page itself is blocked from the network by CSP (`connect-src 'none'`).

**Build** (no Android SDK required, needs JDK 17+, Maven, Node.js/npm, Python 3):

```bash
KASA_KEYSTORE=/path/to/key.p12 KASA_KEY_PASSWORD='...' ./build.sh   # -> build/Kasa.apk
```

The pipeline compiles `MainActivity.java` against Android 4.1 stubs, converts it with `dalvik-dx`, writes the binary manifest and `resources.arsc` with `tools/mkres.py` (no aapt), packages with 4-byte alignment and signs with APK Signature Scheme v2 via `apksig`. `tools/mkhtml.py` turns `web/kasa.html` into the offline APK page: local file storage through a JS bridge, bundled fonts and the native rate fetch. Bump `versionCode` in `tools/mkres.py` for every release. The signing key is not part of this repository.

No license is granted: all rights reserved. Ask the author before reusing the code.

---

# Каса

Личный трекер бюджета в трёх валютах: сербские динары, евро и рубли. Это приложение для Android (APK) и та же страница для браузера.

## Что умеет

- Кошельки RSD, EUR и RUB и общий баланс в выбранной валюте.
- Курсы с пометкой роста или падения. В APK курс запрашивается один раз в сутки.
- Траты, доходы и обмены валют. При обмене видно, сколько теряешь относительно официального курса.
- Повторяющиеся платежи (например, аренда и коммуналка), можно платить свою долю, с датой первой оплаты.
- Доход: зарплата, которую можно разбить на две даты с отдельными суммами.
- Долги, месячный лимит с предупреждениями, напоминание поменять валюту, когда кончаются динары.
- Экран первого запуска, дневная и ночная темы, котик на нижней панели.

## Приватность (APK)

- Все записи хранятся в одном файле в личной папке приложения на телефоне. Облачный бэкап Android выключен (`allowBackup=false`).
- В интернет приложение ходит только за официальным курсом: open.er-api.com, при ошибке зеркала currency-api. Запрос делает нативный код. Странице внутри приложения выход в сеть закрыт политикой CSP (`connect-src 'none'`).
- Резервная копия делается вручную: «Настройки», затем «Сохранить копию».

## Устройство

| Путь | Что это |
|---|---|
| `web/kasa.html` | Исходник интерфейса, единый для браузерной версии и APK |
| `tools/mkhtml.py` | Превращает `web/kasa.html` в офлайн-версию для APK: локальное хранилище, встроенные шрифты, мост к нативному коду |
| `android/src/app/kasa/MainActivity.java` | WebView, хранение в файле, запрос курса, системные панели, кнопка «Назад» |
| `tools/mkres.py` | Пишет бинарный `AndroidManifest.xml` и `resources.arsc` без aapt |
| `tools/mkzip.py`, `tools/Sign.java` | Упаковка с выравниванием и подпись схемой v2 (apksig) |
| `tests/cat_overlap.test.js` | Проверка в Playwright, что котик не перекрывает контент ни на одной вкладке |

## Сборка

Нужны JDK 17+, Maven, Node.js с npm и Python 3. Android SDK не нужен.

```bash
KASA_KEYSTORE=/путь/к/kasa-signing-key.p12 KASA_KEY_PASSWORD='...' ./build.sh
# результат: build/Kasa.apk
```

Версия задаётся в `tools/mkres.py` (`versionCode` и `versionName`). Для каждого обновления увеличивай `versionCode`.

**Ключ подписи в репозиторий не кладётся.** Обновления нужно подписывать тем же ключом, иначе Android не поставит их поверх установленной версии. Храни ключ и пароль отдельно, в надёжном месте.

## Лицензия

Лицензия не выдаётся, все права защищены. Чтобы использовать код, спросите автора.
