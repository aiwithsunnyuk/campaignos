# CampaignOS M11.4 — Career Path Finder

M11.4 turns M11.3 persona intelligence into a usable **Career Path Finder**.

**Workflow:** Profile → Persona → Career Path → Training Sequence → Next Action

### Added
- `src/training/career_paths.py`
- `app/pages/10_Career_Path_Finder.py`
- `tests/test_career_paths.py`
- `docs/m11_4_career_path_finder.md`
- updated `src/training/__init__.py`

This is an incremental overlay for an existing CampaignOS M11.3 checkout. Extract it at the repository root. It intentionally adds a new Streamlit page rather than replacing the M11.3 Training Growth Hub.

### Validation
```bash
python -m py_compile src/training/career_paths.py app/pages/10_Career_Path_Finder.py
python -m pytest tests/test_career_paths.py -q
python -m pytest -q
```
If the full suite regenerates tracked activity data, run `git restore data/synthetic/activities.csv` afterward.

### Git closeout
```bash
git status --short
git add src/training/career_paths.py src/training/__init__.py app/pages/10_Career_Path_Finder.py tests/test_career_paths.py docs/m11_4_career_path_finder.md M11_4_README.md
git commit -m "feat: add career path finder"
git push origin main
```
Only type commands into the terminal, not their output.
