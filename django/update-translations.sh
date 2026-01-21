#!/bin/bash
# Update translations while preserving Unfold Admin Theme translations
# Usage: ./update-translations.sh

set -e  # Exit on error

LOCALE_DIR="locale/de/LC_MESSAGES"
PO_FILE="$LOCALE_DIR/django.po"
UNFOLD_BACKUP="/tmp/unfold-translations-backup.txt"
MANAGE_COMMAND=(./manage.py)
DEFAULT_VENV_PATH=~/.venv/cohiva-dev

if [ -z "$VIRTUAL_ENV" ]; then
    if [ -e $DEFAULT_VENV_PATH/bin/python ] ; then
        echo "ℹ️  No Python virtual environment is active. Using default at $DEFAULT_VENV_PATH"
        MANAGE_COMMAND=($DEFAULT_VENV_PATH/bin/python manage.py)
    else
        echo "⚠️  No Python virtual environment is active or found at the default location $DEFAULT_VENV_PATH."
        exit
    fi
fi

# Extract Unfold section (everything after the Unfold marker)
echo "📦 Backing up Unfold translations..."
sed -n '/^# =====.*Unfold Admin Theme/,$p' "$PO_FILE" > "$UNFOLD_BACKUP"

if [ ! -s "$UNFOLD_BACKUP" ]; then
    echo "⚠️  Warning: No Unfold translations found to backup"
    echo "   This is normal if it's the first run"
fi

# Run makemessages
echo "🔄 Running makemessages..."
${MANAGE_COMMAND[@]} makemessages -l de --no-obsolete --ignore='htmlcov/*' --ignore='*.bak'

# Restore Unfold section
if [ -s "$UNFOLD_BACKUP" ]; then
    echo "✅ Restoring Unfold translations..."
    cat "$UNFOLD_BACKUP" >> "$PO_FILE"
else
    echo "ℹ️  No Unfold translations to restore"
fi

# Compile messages
echo "⚙️  Compiling messages..."
${MANAGE_COMMAND[@]} compilemessages -l de

echo "✨ Translation update complete!"
echo ""
echo "Next steps:"
echo "1. Review $PO_FILE for any new untranslated strings"
echo "2. Add German translations for empty msgstr entries"
echo "3. Run: ./update-translations.sh  (to recompile)"
