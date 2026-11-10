"""Unit tests for UI filedialog starting directories."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from ui.main_window import SeestarApp
from ui.settings_window import SettingsWindow
from ui.analysis_window import AnalysisWindow


SINGLE_DIR_METHODS = [
    ("select_seestar_dir", "seestar_dir", "seestar_path_label"),
    ("select_raw_dir", "raw_dir", "raw_path_label"),
    ("select_projects_dir", "projects_dir", "projects_path_label"),
    ("select_ps_source_dir", "ps_source_dir", "ps_source_path_label"),
    ("select_ps_target_dir", "ps_target_dir", "ps_target_path_label"),
]


def _app_mock(**attrs):
    """A stand-in for SeestarApp with the real _initial_dir helper."""
    self_mock = MagicMock(spec=SeestarApp)
    self_mock._initial_dir = SeestarApp._initial_dir
    self_mock.settings = MagicMock()
    for name, value in attrs.items():
        setattr(self_mock, name, value)
    return self_mock


def _initialdir(mock_dialog):
    mock_dialog.assert_called_once()
    return mock_dialog.call_args.kwargs["initialdir"]


class TestMainWindowDialogs:
    """Directory pickers in the main window."""

    @pytest.mark.parametrize("method_name, dir_attr, label_attr", SINGLE_DIR_METHODS)
    def test_defaults_to_home(self, method_name, dir_attr, label_attr):
        self_mock = _app_mock(**{dir_attr: None, label_attr: MagicMock()})
        with patch("ui.main_window.filedialog.askdirectory", return_value="") as dlg:
            getattr(SeestarApp, method_name)(self_mock)
        assert _initialdir(dlg) == str(Path.home())

    @pytest.mark.parametrize("method_name, dir_attr, label_attr", SINGLE_DIR_METHODS)
    def test_uses_existing_dir(self, temp_dir, method_name, dir_attr, label_attr):
        self_mock = _app_mock(**{dir_attr: temp_dir, label_attr: MagicMock()})
        with patch("ui.main_window.filedialog.askdirectory", return_value="") as dlg:
            getattr(SeestarApp, method_name)(self_mock)
        assert _initialdir(dlg) == str(temp_dir)

    @pytest.mark.parametrize("method_name, dir_attr, label_attr", SINGLE_DIR_METHODS)
    def test_missing_dir_falls_back_to_home(self, temp_dir, method_name, dir_attr, label_attr):
        self_mock = _app_mock(**{dir_attr: temp_dir / "gone", label_attr: MagicMock()})
        with patch("ui.main_window.filedialog.askdirectory", return_value="") as dlg:
            getattr(SeestarApp, method_name)(self_mock)
        assert _initialdir(dlg) == str(Path.home())

    def test_analyze_dirs_default_to_home(self):
        self_mock = _app_mock(analyze_projects_dirs=[])
        with patch("ui.main_window.filedialog.askdirectory", return_value="") as dlg:
            SeestarApp.select_analyze_projects_dir(self_mock)
        assert _initialdir(dlg) == str(Path.home())

    def test_analyze_dirs_start_at_last_added(self, temp_dir):
        first, last = temp_dir / "a", temp_dir / "b"
        first.mkdir(); last.mkdir()
        self_mock = _app_mock(analyze_projects_dirs=[first, last])
        with patch("ui.main_window.filedialog.askdirectory", return_value="") as dlg:
            SeestarApp.select_analyze_projects_dir(self_mock)
        assert _initialdir(dlg) == str(last)

    def test_browse_fits_defaults_to_home(self):
        self_mock = _app_mock(current_fits_directory=None)
        with patch("ui.main_window.filedialog.askdirectory", return_value="") as dlg:
            SeestarApp.browse_fits_directory(self_mock)
        assert _initialdir(dlg) == str(Path.home())

    def test_browse_fits_uses_current_dir(self, temp_dir):
        self_mock = _app_mock(current_fits_directory=str(temp_dir))
        with patch("ui.main_window.filedialog.askdirectory", return_value="") as dlg:
            SeestarApp.browse_fits_directory(self_mock)
        assert _initialdir(dlg) == str(temp_dir)


class TestOtherWindowDialogs:
    """File dialogs in the settings and analysis windows start in the home folder."""

    def test_settings_import_tags(self):
        self_mock = MagicMock(spec=SettingsWindow)
        with patch("ui.settings_window.filedialog.askopenfilename", return_value="") as dlg:
            SettingsWindow.import_tags(self_mock)
        assert _initialdir(dlg) == str(Path.home())

    def test_settings_export_tags(self):
        self_mock = MagicMock(spec=SettingsWindow)
        with patch("ui.settings_window.filedialog.asksaveasfilename", return_value="") as dlg:
            SettingsWindow.export_tags(self_mock)
        assert _initialdir(dlg) == str(Path.home())

    def test_analysis_export_to_csv(self):
        self_mock = MagicMock(spec=AnalysisWindow)
        with patch("ui.analysis_window.filedialog.asksaveasfilename", return_value="") as dlg:
            AnalysisWindow.export_to_csv(self_mock)
        assert _initialdir(dlg) == str(Path.home())
