"""AppTest smoke test for the Increment 1A Sales Analytics Workbench shell.

Genuine Streamlit AppTest smoke test (not a lint test). It verifies:
1. Main app launches without exceptions.
2. All five page scripts run headlessly.
3. Navigation registry order matches the approved order.
4. Empty state renders when no dataset is loaded.
5. Theme CSS is injected.
6. AST-based architecture test: no non-presentation module imports Streamlit.
"""

import ast
import logging
from pathlib import Path

import pytest

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    pytest.skip("streamlit-testing not available", allow_module_level=True)

logger = logging.getLogger("tests")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"
MAIN_SCRIPT = APP_ROOT / "main.py"

EXPECTED_PAGES = [
    "Data Immersion & Wrangling",
    "EDA & BI",
    "SQL Analysis",
    "Power BI Showcase",
    "Statistical Validation",
]

PAGE_SCRIPTS = [
    "pages/01_data_immersion.py",
    "pages/02_eda_bi.py",
    "pages/03_sql_analysis.py",
    "pages/04_power_bi.py",
    "pages/05_statistical_validation.py",
]


def test_main_app_runs_without_exception() -> None:
    """1. Main app launches without exceptions."""
    logging.getLogger("streamlit").setLevel(logging.ERROR)
    app = AppTest.from_file(str(MAIN_SCRIPT))
    app.run(timeout=10)
    assert not app.exception, f"App raised: {[e.value for e in app.exception]}"


def test_pages_run_headlessly() -> None:
    """2. All five page scripts run headlessly without exceptions."""
    for script in PAGE_SCRIPTS:
        page = AppTest.from_file(str(APP_ROOT / script))
        page.session_state["raw_df"] = None
        page.session_state["active_df"] = None
        page.session_state["cleaning_history"] = []
        page.session_state["db_conn"] = None
        page.run(timeout=10)
        assert not page.exception, f"Page {script} raised: {page.exception}"


def test_navigation_registry_order() -> None:
    """3. Navigation registry has exactly five entries in the approved order."""
    tree = ast.parse(MAIN_SCRIPT.read_text(encoding="utf-8"))
    titles = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (isinstance(node.func, ast.Attribute) and node.func.attr == "Page"):
            continue
        for kw in node.keywords:
            if kw.arg == "title" and isinstance(kw.value, ast.Constant):
                titles.append(kw.value.value)
    assert titles == EXPECTED_PAGES


def test_empty_state_and_theme() -> None:
    """4 and 5. Empty states render and the theme CSS is injected."""
    app = AppTest.from_file(str(MAIN_SCRIPT))
    app.run(timeout=10)
    # Theme CSS injection: main() renders a markdown element containing the
    # dark navy background color token.
    has_theme = any("#0B132B" in m.value for m in app.markdown)
    assert has_theme, "Theme CSS not injected as HTML"
    # Landing content: title element contains "Sales Analytics Workbench".
    assert app.title, "Expected title element"
    assert "Sales Analytics Workbench" in app.title[0].value
    # Module 1 empty state.
    assert app.info, "Expected an info element for empty state"
    has_empty_msg = any("No dataset loaded" in i.value for i in app.info)
    assert has_empty_msg, "Empty state message not rendered"


def test_no_streamlit_import_in_non_presentation_modules() -> None:
    """6. AST-based architecture test: services/models/database are Streamlit-free."""
    banned_packages = ("services", "database", "models")
    offenders = []
    for path in sorted(APP_ROOT.rglob("*.py")):
        rel = path.relative_to(APP_ROOT)
        parts = rel.parts
        if not parts or parts[0] not in banned_packages:
            continue
        if path.name == "__init__.py" and len(parts) <= 2:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "streamlit" or alias.name.startswith("streamlit."):
                        offenders.append((str(rel), alias.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "streamlit" or module.startswith("streamlit."):
                    offenders.append((str(rel), module))
    assert not offenders, f"Streamlit imported outside presentation: {offenders}"


def test_approved_paths_exist() -> None:
    """Supporting check: all five page scripts and main exist on disk."""
    assert MAIN_SCRIPT.is_file()
    for script in PAGE_SCRIPTS:
        assert (APP_ROOT / script).is_file(), f"Missing approved path: {script}"
