# Repository Guidelines

## Project Structure & Module Organization
`myproject/` holds Django settings, URL routing, and ASGI/WSGI entrypoints; the app logic sits in `core/` (models, views, admin, migrations, seeds for tests). Electron bootstrap code lives in `main.js` with the splash screen in `loading.html`. Helper scripts (`run.sh`, `run_django.sh`, `start_django.sh`) wrap Conda activation and server start-up, while dependency manifests (`package.json`, `environment.yml`, `requirements.txt`) stay at the repo root.

## Build, Test, and Development Commands
- `conda env create -f environment.yml` then `conda activate django-electron` to bootstrap the recommended toolchain.
- `npm install` fetches Electron runtime dependencies into `node_modules/`.
- `npm start` launches Electron and the Django backend (uses `DISPLAY=:0`; adjust for headless environments).
- `npm run django` or `./start_django.sh` starts only the Django dev server at http://127.0.0.1:8000.
- `npm run build` invokes `electron-builder` to package the desktop app into `dist/`.

## Coding Style & Naming Conventions
Python code follows PEP 8 with 4-space indentation; keep modules in `snake_case.py` and use `PascalCase` for classes (e.g., `DashboardView`). Favor `camelCase` for JavaScript variables and `PascalCase` for Electron classes/functions. If you add formatters (`black`, `isort`, `prettier`) document them in the PR and run them before review.

## Testing Guidelines
Add Django unit tests under `core/tests.py` or new `tests/` packages using `TestCase` subclasses. Name tests after the behavior under test (e.g., `test_dashboard_renders_for_authenticated_user`) and group helpers with the feature they cover. Run suites with `python manage.py test`; add `--verbosity 2` when diagnosing failures and mention any skipped areas in the PR.

## Commit & Pull Request Guidelines
Adopt the Conventional Commits style observed in history (e.g., `feat: add onboarding window`). Keep commits focused, keep the summary under 72 characters, and note breaking changes in the body. PRs should describe scope, link issues, list manual verification steps (commands run, platforms tested), and include screenshots or screencasts for UI updates. Always attach migrations when models change and flag any follow-up tasks.

## Security & Configuration Tips
Keep secrets (API keys, Django `SECRET_KEY`) in environment variables or ignored `.env` files—never commit them. Exclude or reset `db.sqlite3` before distribution builds unless you are shipping seed data. When editing `myproject/settings.py`, confirm debug flags and allowed hosts are appropriate for the target environment.
