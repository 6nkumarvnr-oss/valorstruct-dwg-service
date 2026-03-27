# Local setup without GitHub (offline-friendly)

If GitHub has issues, you can still build everything locally.

## 1) Recommended folder structure on your system
Create one workspace folder:

```text
exam-ai-workspace/
  backend-exam-engine/      # this repository code (FastAPI)
  mobile-flutter-app/       # your Flutter app
  shared-assets/            # PDFs, sample data, docs
```

## 2) Get backend code without GitHub clone
Use any one method:

### Method A: Download ZIP from browser (when website works)
1. Open repo page.
2. Click `Code` → `Download ZIP`.
3. Extract into `backend-exam-engine/`.

### Method B: Copy project via USB/drive from another machine
1. Zip the repo on working machine.
2. Transfer ZIP.
3. Extract into `backend-exam-engine/`.

### Method C: Create a git bundle once, reuse everywhere
On machine with repo access:
```bash
git bundle create exam-engine.bundle --all
```
Transfer `exam-engine.bundle`, then on local machine:
```bash
git clone exam-engine.bundle backend-exam-engine
```

## 3) Open backend in VS Code
```bash
cd exam-ai-workspace/backend-exam-engine
code .
```

Then follow beginner setup docs:
- `docs/beginner_step_by_step_manual.md`
- `docs/beginner_manual_part2_api_examples.md`
- `docs/beginner_manual_part3_one_day_demo_plan.md`

## 4) Create Flutter project locally
```bash
cd ../
flutter create mobile-flutter-app
cd mobile-flutter-app
code .
```

## 5) Connect Flutter app to local backend
In Flutter, set base URL:
- Android emulator: `http://10.0.2.2:8001`
- iOS simulator: `http://127.0.0.1:8001`
- Real device: `http://<your-laptop-ip>:8001`

## 6) Run both projects locally

### Terminal 1 (backend)
```bash
cd exam-ai-workspace/backend-exam-engine
source .venv/bin/activate
uvicorn tet_engine.app.main:app --reload --port 8001
```

### Terminal 2 (flutter)
```bash
cd exam-ai-workspace/mobile-flutter-app
flutter pub get
flutter run
```

## 7) Suggested division: VS Code backend vs Flutter frontend
- **VS Code backend folders**:
  - `tet_engine/`
  - `alembic/`
  - `docs/`
  - `.github/`
  - `tests/`

- **Flutter app folders**:
  - `lib/`
  - `android/`
  - `ios/`
  - `test/`

## 8) No-GitHub collaboration option
If team cannot use GitHub temporarily:
1. Exchange `.zip` or `.bundle` daily.
2. Keep a version file, e.g. `build_version.txt`.
3. Merge changes later when GitHub returns.

## 9) Best local-first plan
1. Stabilize backend APIs locally.
2. Build admin web/mobile UI against local API.
3. Run one-day demo plan locally.
4. Move to cloud only after local flow is stable.
