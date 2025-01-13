#!/bin/bash

# Update database if needed.
HAS_COL=$(sqlite3 /var/lib/rn_irl/irl.sdb "select show_valuations from 'System Settings';")

if [[ $HAS_COL == "0" ]] || [[ $HAS_COL == "1" ]]; then
        echo "RN IRL Database System Settings up to date, moving on..."
else
        echo "RN IRL Database System Settings table not up to date, adding column show_valuations."
        sqlite3 /var/lib/rn_irl/irl.sdb 'ALTER TABLE "System Settings" ADD COLUMN show_valuations INTEGER(1);'
        sqlite3 /var/lib/rn_irl/irl.sdb 'UPDATE "System Settings" SET show_valuations = 0;'
fi

HAS_COL=$(sqlite3 /var/lib/rn_irl/irl.sdb "select noreply_address from 'System Settings';")

if [[ $HAS_COL == "0" ]] || [[ $HAS_COL == "1" ]]; then
        echo "RN IRL Database System Settings up to date, moving on..."
else
        echo "RN IRL Database System Settings table not up to date, adding column noreply_address."
        sqlite3 /var/lib/rn_irl/irl.sdb 'ALTER TABLE "System Settings" ADD COLUMN noreply_address TEXT();'
        sqlite3 /var/lib/rn_irl/irl.sdb 'UPDATE "System Settings" SET noreply_address = "noreply@rn-irl.tto.ntnu.no";'
fi

HAS_COL=$(sqlite3 /var/lib/rn_irl/irl.sdb "select noreply_body from 'System Settings';")

if [[ $HAS_COL == "0" ]] || [[ $HAS_COL == "1" ]]; then
        echo "RN IRL Database System Settings up to date, moving on..."
else
        echo "RN IRL Database System Settings table not up to date, adding column noreply_body."
        sqlite3 /var/lib/rn_irl/irl.sdb 'ALTER TABLE "System Settings" ADD COLUMN noreply_body TEXT();'
        sqlite3 /var/lib/rn_irl/irl.sdb 'UPDATE "System Settings" SET noreply_body = "Welcome to Really Nice IRL!\n\nWe have generated a login password for you: %s\n\nWe suggest you change this upon your first login.\nGood luck with your innovation project going forward!\n\nBest regards,\nThe Really Nice IRL Team";'
fi
