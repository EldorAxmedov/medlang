# TASKS — Loyiha vazifalari va yo'l xaritasi

Bu fayl Django + PostgreSQL asosidagi backend loyihasidagi barcha bajarilishi kerak bo'lgan ishlarni bosqichma-bosqich (har bir feature uchun) bayon qiladi.

## Qisqacha maqsad
- Production-ready, kengaytiriladigan backend: modular arxitektura (core, users, api, services, repositories).
- SOLID, DRY, KISS va Clean Architecture tamoyillari bo‘yicha ishlash.

## Hozirgi holat
- Loyihaning bosh skeleti yaratilgan: `manage.py`, `medlang/settings.py`, `api/urls.py`.
- `users` app: `User` modeli (UUID PK), repository, service, serializers, viewset va permission mavjud.
- JWT auth (SimpleJWT) integratsiyasi uchun sozlamalar qo‘yilgan.

---

## Umumiy ishlar (prioritet bilan)
1. Tests (unit + integration) — yuqori
2. CI pipeline (migrations, lint, tests) — yuqori
3. Production konfiguratsiyalari va security hardening — yuqori
4. Monitoring, logging, metrics (Sentry, Prometheus) — o'rta
5. Qo'shimcha domain modellari va ularni service/repository orqali implementatsiya — o'rta

---

## Har bir yangi Feature uchun ishlash tartibi (majburiy 7 bosqich)

1) Talabni tahlil qil
- Nima qilinadi? (feature maqsadi)
- Entitylar (model nomi, asosiy maydonlar)
- Bog‘lanishlar (FK, M2M)

2) Model (DB design)
- Django model yozish (`UUIDField` primary key)
- Indexlar va `unique` cheklovlar qo‘yish

3) Repository layer
- `core.repositories.base.BaseRepository` dan voris qilib repository yozish
- Barcha DB bilan bog‘liq CRUD shu qatorda bo‘lsin

4) Service layer
- Barcha biznes qoidalar shu qatorda yozilsin
- Repository orqali maʼlumot oling va validatsiya, transactionlarni shu yerda boshqaring

5) API layer
- `serializers` orqali kirish va chiqish validatsiyasi
- DRF `ViewSet` yoki CBV, view ichida biznes qoidalar yo‘q

6) Permission va xavfsizlik
- Role-based access (RBAC) qo‘llash
- Token/ACL cheklovlari, rate-limiting kerak bo‘lsa qo‘shish

7) Test yozish
- Service unit testlari (business logic)
- API integration testlar (registration, login, permissions)

---

## Maxsus vazifalar (tarkibiy ro'yxat)

- User Auth & RBAC
  - Talab: JWT login/refresh, rolelar (admin/user), access control.
  - Bosqichlar: (yuqoridagi 7 bosqichni amal qil)
  - Hozirgi status: Model + Service + ViewSet + JWT mavjud; testlar yozilishi kerak.

- Tests
  - Unit tests: `users.services.UserService` va `core.repositories` uchun.
  - API tests: registration (`POST /api/users/`), login (`POST /api/users/login/`), token refresh.
  - Tavsiya: `pytest` + `pytest-django`. Yozish tartibi: service unit test → api test.

- CI / Pipeline
  - Yozish: `.github/workflows/ci.yml` yoki GitLab CI.
  - Qadamlar: install deps → run linters (flake8/isort) → run `pytest` → makemigrations check → run migrate (optional).

- Deployment (systemd + gunicorn)
  - `/etc/systemd/system/medlang.service` — tayyor
  - Port: `8090` (boshqa loyihalar bilan to'qnashmaydi)
  - PostgreSQL: serverda mavjud `medlang_db` bazasi (localhost:5432)
  - Virtual env: `/var/www/medlang/venv/`

- Security & Production
  - `SECRET_KEY` muhofazasi (`.env` fayli orqali)
  - `DEBUG=False`, `ALLOWED_HOSTS` sozlash
  - HTTPS, HSTS, security middlewares
  - DB connection pooling va param konfiguratsiyalari

- Observability
  - Sentry (error tracking) integratsiyasi
  - Request/response logging: `/var/log/medlang/`

---

## Qo'llanma: testlarni boshlash uchun tez yo‘l
1. Virtual env yaratish va dependencies o‘rnatish:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-django
```
2. `.env` faylini to'ldiring (`.env.example` asosida — tayyor).
3. Migrationsni yaratib, DB ga tatbiq qiling:
```bash
python manage.py makemigrations
python manage.py migrate
```
4. Testsni ishga tushirish:
```bash
pytest -q
```

---

## Qisqa checklist (har feature uchun)
- [ ] Talab tahlili tugadi
- [ ] Model yaratildi + migrations
- [ ] Repository yozildi
- [ ] Service yozildi + unit testlar
- [ ] Serializer va View/URL qo‘shildi
- [ ] Permissionlar qo‘shildi
- [ ] API testlar yozildi va muvaffaqiyatli

---

Agar xohlasangiz, men hozir test fayllarini (`tests/test_users_service.py`, `tests/test_users_api.py`) va `.github/workflows/ci.yml` faylini avtomatik yaratib qo‘yaman. Qaysi ishni birinchi bajarishimni xohlaysiz?

---

## Medical English Platform — modul ro'yxati va talablar

Quyidagi bo'limlar tibbiyot talabalari uchun ingliz tilini o'rganish platformasining backend qismini tashkil etadi. Faqat backend (model, service, admin) yoziladi — API yoki frontend yozilmaydi.

### Umumiy cheklovlar
- API yozilmaydi
- Frontend yo'q
- Test yozilmaydi (agar keyinchalik xohlasangiz, service va model testlarini qo'shamiz)
- Faqat backend (model + service + admin)

### Texnologiya
- Django
- PostgreSQL

### Modullar (har biri uchun 1-5 bosqich talab qilinadi)

1) Users
- CustomUser (admin, teacher, student)
- Profile
- Specialty

2) Vocabulary
- Word, Translation, Definition, Example, Category

3) Tests
- Test, Question, Answer, UserResult

4) Grammar Check
- UserText, CorrectedText, Errors, Score

5) Patient Simulation
- Scenario, PatientProfile, Session, Message, Feedback

6) Chat Module
- ChatRoom (name, type, created_at)
- ChatParticipant (user, chat_room, role)
- ChatMessage (chat_room, sender, message, created_at, is_read)
- ChatRoomType: GROUP, PRIVATE, SIMULATION

7) Progress
- Level, UserProgress, total_score, completed_tests, completed_sessions

8) Statistics
- user activity, test results, writing results, chat activity, simulation results

### Biznes talablar (chat ga oid)
- Talaba group chatga qo'shiladi
- Talaba o'qituvchiga yozishi mumkin
- Har bir chat room alohida bo'ladi
- Message lar real vaqt uchun tayyor (websocket keyinchalik qo'shiladi)
- Simulation chat Session bilan bog'lanadi

### Ishlash bosqichlari (har modul uchun takrorlanadi)
1. Tahlil (entity va bog'lanishlar)
2. Model (UUID PK, relationlar)
3. Repository (CRUD)
4. Service (business logic: chat yaratish, message yuborish, session boshqarish, progress hisoblash)
5. Admin (filter, search, inline)

### Papka struktura taklifi
project/
├── users/
├── vocabulary/
├── tests/
├── simulation/
├── chat/
├── progress/
├── statistics/
├── services/
├── repositories/

### Natija (har modul uchun)
1. Tahlil
2. Model
3. Repository
4. Service
5. Admin

### Boshlash tartibi
- Avval: `Users`
- Keyin: `Vocabulary` → `Tests` → `Simulation` → `Chat` → `Progress` → `Statistics`

---

`TASKS.md` yangilandi: endi loyiha tibbiyot ingliz tili platformasi uchun zarur modullar va ishlash tartiblari yozildi.
