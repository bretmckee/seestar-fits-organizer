#!/bin/bash

# Bash strict mode (exit on error, unset variables, pipe failures)
set -euo pipefail

cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "Installing/updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
# Build-time only: PyInstaller's astropy hook imports every astropy submodule, and
# astropy.visualization.wcsaxes calls pytest.importorskip("matplotlib"), which
# aborts the build when pytest is installed but matplotlib is not.
pip install "matplotlib>=3.7"

# Run PyInstaller build
echo "Building Seestar FITS Organizer..."
pyinstaller --noconfirm --clean --onedir --windowed \
    --name "Seestar FITS Organizer" \
    --icon icon.icns \
    --add-data "TERMS_OF_SERVICE.md:." \
    --add-data "DISCLAIMER.md:." \
    main.py

# Package the app into a drag-to-Applications disk image
echo "Creating disk image..."
STAGING="build/dmg-staging"
rm -rf "$STAGING"
mkdir -p "$STAGING"
cp -R "dist/Seestar FITS Organizer.app" "$STAGING/"
ln -s /Applications "$STAGING/Applications"
hdiutil create -volname "Seestar FITS Organizer" -srcfolder "$STAGING" \
    -ov -format ULFO "dist/Seestar FITS Organizer.dmg"
rm -rf "$STAGING"

echo "Build complete!"
echo "  App: dist/Seestar FITS Organizer.app"
echo "  DMG: dist/Seestar FITS Organizer.dmg"
