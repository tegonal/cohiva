#!/bin/bash
# Update translations while preserving Unfold Admin Theme translations
# Usage: ./update-translations.sh

set -e  # Exit on error

LOCALE_DIR="locale/de/LC_MESSAGES"
PO_FILE="$LOCALE_DIR/django.po"
UNFOLD_BACKUP="/tmp/unfold-translations-backup.txt"

# Extract Unfold section (everything after the Unfold marker)
echo "📦 Backing up Unfold translations..."
sed -n '/^# =====.*Unfold Admin Theme/,$p' "$PO_FILE" > "$UNFOLD_BACKUP"

if [ ! -s "$UNFOLD_BACKUP" ]; then
    echo "⚠️  Warning: No Unfold translations found to backup"
    echo "   This is normal if it's the first run"
fi

# Run makemessages
echo "🔄 Running makemessages..."
~/.venv/cohiva-dev/bin/python manage.py makemessages -l de --no-obsolete

# Restore Unfold section
if [ -s "$UNFOLD_BACKUP" ]; then
    echo "✅ Restoring Unfold translations..."
    cat "$UNFOLD_BACKUP" >> "$PO_FILE"
else
    echo "ℹ️  No Unfold translations to restore"
fi

# Compile messages
echo "⚙️  Compiling messages..."
~/.venv/cohiva-dev/bin/python manage.py compilemessages -l de

echo "✨ Translation update complete!"
echo ""
echo "Next steps:"
echo "1. Review $PO_FILE for any new untranslated strings"
echo "2. Add German translations for empty msgstr entries"
echo "3. Run: ./update-translations.sh  (to recompile)"
