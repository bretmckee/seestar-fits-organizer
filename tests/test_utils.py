"""Unit tests for filesystem utilities."""

import os
import pytest

from core.utils import extended_path, safe_copy


class TestExtendedPath:
    """The Windows long-path normalization helper."""

    @pytest.mark.skipif(os.name != 'nt', reason="Windows-only behavior")
    def test_adds_prefix_on_windows(self, temp_dir):
        result = extended_path(temp_dir / "file.fit")
        assert result.startswith('\\\\?\\')

    @pytest.mark.skipif(os.name != 'nt', reason="Windows-only behavior")
    def test_does_not_double_prefix(self):
        already = '\\\\?\\C:\\some\\path.fit'
        assert extended_path(already) == already

    @pytest.mark.skipif(os.name == 'nt', reason="POSIX-only behavior")
    def test_no_prefix_on_posix(self, temp_dir):
        result = extended_path(temp_dir / "file.fit")
        assert not result.startswith('\\\\?\\')


class TestSafeCopy:
    """safe_copy should copy content and preserve size."""

    def test_copies_file(self, temp_dir):
        src = temp_dir / "src.fit"
        dst = temp_dir / "sub" / "dst.fit"
        dst.parent.mkdir()
        src.write_bytes(b"hello fits" * 100)

        safe_copy(src, dst)

        assert dst.exists()
        assert dst.read_bytes() == src.read_bytes()

    def test_raises_on_missing_source(self, temp_dir):
        with pytest.raises(Exception):
            safe_copy(temp_dir / "nope.fit", temp_dir / "out.fit")


class TestGetStoragePath:
    """Where settings files are stored."""

    def test_script_mode_uses_core_dir(self, monkeypatch):
        import sys
        import core.utils as utils
        monkeypatch.delattr(sys, 'frozen', raising=False)
        path = utils.get_storage_path("app_settings.json")
        assert path.parent == utils.Path(utils.__file__).parent

    def test_frozen_mac_uses_application_support(self, monkeypatch, temp_dir):
        import sys
        import core.utils as utils
        monkeypatch.setattr(sys, 'frozen', True, raising=False)
        monkeypatch.setattr(sys, 'platform', 'darwin')
        monkeypatch.setattr(utils.Path, 'home', classmethod(lambda cls: temp_dir))
        path = utils.get_storage_path("app_settings.json")
        expected = temp_dir / "Library" / "Application Support" / utils.APP_NAME
        assert path == expected / "app_settings.json"
        assert expected.is_dir()

    def test_frozen_windows_uses_exe_dir(self, monkeypatch, temp_dir):
        import sys
        import core.utils as utils
        monkeypatch.setattr(sys, 'frozen', True, raising=False)
        monkeypatch.setattr(sys, 'platform', 'win32')
        monkeypatch.setattr(sys, 'executable', str(temp_dir / "app.exe"))
        path = utils.get_storage_path("app_settings.json")
        assert path == temp_dir / "app_settings.json"
