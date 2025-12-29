from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from qgis_manager.core import (
    clean_artifacts,
    compile_qt_resources,
    deploy_plugin,
    get_qgis_plugin_dir,
    init_plugin_project,
)


def test_get_qgis_plugin_dir_linux(mocker: MockerFixture):
    mocker.patch("sys.platform", "linux")
    expected = Path.home() / ".local/share/QGIS/QGIS3/profiles/default/python/plugins"
    assert get_qgis_plugin_dir() == expected


def test_get_qgis_plugin_dir_linux_custom_profile(mocker: MockerFixture):
    mocker.patch("sys.platform", "linux")
    expected = Path.home() / ".local/share/QGIS/QGIS3/profiles/prod/python/plugins"
    assert get_qgis_plugin_dir(profile="prod") == expected


def test_get_qgis_plugin_dir_darwin(mocker: MockerFixture):
    mocker.patch("sys.platform", "darwin")
    expected = (
        Path.home()
        / "Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins"
    )
    assert get_qgis_plugin_dir() == expected


def test_get_qgis_plugin_dir_win32(mocker: MockerFixture):
    mocker.patch("sys.platform", "win32")
    mocker.patch("os.environ", {"APPDATA": "/appdata"})
    expected = Path("/appdata") / "QGIS/QGIS3/profiles/default/python/plugins"
    assert get_qgis_plugin_dir() == expected


def test_get_qgis_plugin_dir_win32_custom(mocker: MockerFixture):
    mocker.patch("sys.platform", "win32")
    mocker.patch("os.environ", {"APPDATA": "/appdata"})
    expected = Path("/appdata") / "QGIS/QGIS3/profiles/test/python/plugins"
    assert get_qgis_plugin_dir(profile="test") == expected


def test_get_qgis_plugin_dir_unsupported(mocker: MockerFixture):
    mocker.patch("sys.platform", "unknown")
    with pytest.raises(OSError, match="Unsupported platform"):
        get_qgis_plugin_dir()


def test_deploy_plugin(mocker: MockerFixture, tmp_path: Path):
    # Mocks
    mock_metadata = {"name": "Test Plugin", "slug": "test_plugin"}
    mocker.patch("qgis_manager.core.get_plugin_metadata", return_value=mock_metadata)

    mock_source_file = MagicMock(spec=Path)
    mock_source_file.name = "source.py"
    mock_source_file.is_dir.return_value = False

    mocker.patch("qgis_manager.core.get_source_files", return_value=[mock_source_file])

    mock_copy2 = mocker.patch("shutil.copy2")
    mocker.patch("shutil.rmtree")

    dest_dir = tmp_path / "plugins"
    dest_dir.mkdir()

    # Execute
    deploy_plugin(tmp_path, dest_dir=dest_dir)

    # Verify
    target_path = dest_dir / "test_plugin"
    assert target_path.exists()
    mock_copy2.assert_called()


def test_deploy_plugin_with_backup(mocker: MockerFixture, tmp_path: Path):
    # Mocks
    mock_metadata = {"name": "Test Plugin", "slug": "test_plugin"}
    mocker.patch("qgis_manager.core.get_plugin_metadata", return_value=mock_metadata)
    mocker.patch("qgis_manager.core.get_source_files", return_value=[])

    mock_copytree = mocker.patch("shutil.copytree")
    mock_datetime = mocker.patch("qgis_manager.core.datetime")
    mock_datetime.now.return_value.strftime.return_value = "20230101"

    dest_dir = tmp_path / "plugins"
    dest_dir.mkdir()
    (dest_dir / "test_plugin").mkdir()  # simulate existing

    # Execute
    deploy_plugin(tmp_path, dest_dir=dest_dir)

    # Verify backup was created
    mock_copytree.assert_called()


def test_compile_qt_resources(mocker: MockerFixture, tmp_path: Path):
    # Setup
    qrc_file = tmp_path / "resources.qrc"
    qrc_file.touch()

    mock_run = mocker.patch("subprocess.run")

    # Execute
    compile_qt_resources(tmp_path, res_type="resources")

    # Verify
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args[0] == "pyrcc5"
    assert args[-1] == str(qrc_file)


def test_clean_artifacts(mocker: MockerFixture, tmp_path: Path):
    # Setup
    pycache = tmp_path / "__pycache__"
    pycache.mkdir()
    pyc_file = tmp_path / "file.pyc"
    pyc_file.touch()

    # Execute
    clean_artifacts(tmp_path)

    # Verify
    assert not pycache.exists()
    assert not pyc_file.exists()


def test_init_plugin_project(tmp_path: Path):
    # Setup
    plugin_name = "My New Plugin"
    author = "John Doe"
    email = "john@example.com"
    description = "Cool description"

    # Execute
    init_plugin_project(tmp_path, plugin_name, author, email, description)

    # Verify directory
    plugin_dir = tmp_path / "my_new_plugin"
    assert plugin_dir.exists()
    assert plugin_dir.is_dir()

    # Verify metadata.txt
    metadata_file = plugin_dir / "metadata.txt"
    assert metadata_file.exists()
    content = metadata_file.read_text()
    assert "name=My New Plugin" in content
    assert "author=John Doe" in content
    assert "email=john@example.com" in content
    assert "description=Cool description" in content

    # Verify __init__.py
    init_py = plugin_dir / "__init__.py"
    assert init_py.exists()
    assert "def classFactory(iface):" in init_py.read_text()

    # Verify main plugin file
    main_py = plugin_dir / "my_new_plugin.py"
    assert main_py.exists()
    assert "class MyNewPlugin:" in main_py.read_text()

    # Verify resources.qrc
    qrc = plugin_dir / "resources.qrc"
    assert qrc.exists()
    assert 'prefix="/plugins/my_new_plugin"' in qrc.read_text()


def test_deploy_plugin_with_callback(mocker: MockerFixture, tmp_path: Path):
    # Mocks
    mock_metadata = {"name": "Test Plugin", "slug": "test_plugin"}
    mocker.patch("qgis_manager.core.get_plugin_metadata", return_value=mock_metadata)

    def mock_gen(_):
        file1 = MagicMock(spec=Path)
        file1.name = "f1.py"
        file1.is_dir.return_value = False
        yield file1

    mocker.patch("qgis_manager.core.get_source_files", side_effect=mock_gen)
    mocker.patch("shutil.copy2")
    mocker.patch("shutil.rmtree")

    dest_dir = tmp_path / "plugins"
    dest_dir.mkdir()

    callback_calls = []

    def callback(n):
        callback_calls.append(n)

    # Execute
    deploy_plugin(tmp_path, dest_dir=dest_dir, callback=callback)

    # Verify
    # Initial call with total length (1), then 1 per file (1)
    assert callback_calls == [1, 1]
