#!/bin/bash

# Update database if needed.
HAS_COL=$(sqlite3 rn_irl/irl.sdb "select show_valuations from 'system settings';")

if [[ $HAS_COL == "0" ]] || [[ $HAS_COL == "1" ]]; then
        echo "RN IRL Database System Settings up to date, moving on..."
else
        echo "RN IRL Database System Settings table not up to date, adding column show_valuations."
        sqlite3 /var/lib/rn_irl/irl.sdb 'ALTER TABLE "System Settings" ADD COLUMN show_valuations INTEGER(1);'
        sqlite3 /var/lib/rn_irl/irl.sdb 'UPDATE "System Settings" SET show_valuations = 0;'
fi
