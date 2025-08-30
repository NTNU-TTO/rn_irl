#!/bin/bash

# Update database if needed.
ERROR="no such column"
IRL_REV="Version F released 2025"
IRL_PROD_DB="/var/lib/rn_irl/irl.sdb"
IRL_GIT_DB="/etc/rn_irl_staging/bin/rn_irl/irl.sdb"
HAS_COL=$(sqlite3 "$IRL_PROD_DB" "SELECT show_valuations FROM 'System Settings';" 2>&1)

if [[ "$HAS_COL" == *"$ERROR"* ]]; then
        echo "RN IRL Database System Settings table not up to date, adding column show_valuations."
        sqlite3 "$IRL_PROD_DB" 'ALTER TABLE "System Settings" ADD COLUMN show_valuations INTEGER(1);'
        sqlite3 "$IRL_PROD_DB" 'UPDATE "System Settings" SET show_valuations = 0;'
else
        echo "RN IRL Database System Settings up to date, moving on..."
fi

HAS_COL=$(sqlite3 /var/lib/rn_irl/irl.sdb "SELECT noreply_address FROM 'System Settings';" 2>&1)

if [[ "$HAS_COL" == *"$ERROR"* ]]; then
        echo "RN IRL Database System Settings table not up to date, adding column noreply_address."
        sqlite3 "$IRL_PROD_DB" 'ALTER TABLE "System Settings" ADD COLUMN noreply_address TEXT;'
        sqlite3 "$IRL_PROD_DB" 'UPDATE "System Settings" SET noreply_address = "noreply@rn-irl.tto.ntnu.no";'
else
        echo "RN IRL Database System Settings up to date, moving on..."
fi

HAS_COL=$(sqlite3 "$IRL_PROD_DB" "SELECT noreply_body FROM 'System Settings';" 2>&1)

if [[ "$HAS_COL" == *"$ERROR"* ]]; then
        echo "RN IRL Database System Settings table not up to date, adding column noreply_body."
        sqlite3 "$IRL_PROD_DB" 'ALTER TABLE "System Settings" ADD COLUMN noreply_body TEXT;'
        sqlite3 "$IRL_PROD_DB" 'UPDATE "System Settings" SET noreply_body = "Welcome to Really Nice IRL!\n\nWe have generated a login password for you: %s\n\nWe suggest you change this upon your first login.\nGood luck with your innovation project going forward!\n\nBest regards,\nThe Really Nice IRL Team";'
else
        echo "RN IRL Database System Settings up to date, moving on..."        
fi

HAS_COL=$(sqlite3 "$IRL_PROD_DB" "SELECT irl_revision FROM 'System Settings';" 2>&1)
NEW_IRL=false

if [[ "$HAS_COL" == *"$ERROR"* ]]; then
        echo "RN IRL Database System Settings table not up to date, adding column irl_revision."
        sqlite3 "$IRL_PROD_DB" 'ALTER TABLE "System Settings" ADD COLUMN irl_revision TEXT;'
        sqlite3 "$IRL_PROD_DB" 'UPDATE "System Settings" SET irl_revision = "Version F released 2025";'
        NEW_IRL=true
fi

REV=$(sqlite3 "$IRL_PROD_DB" 'SELECT irl_revision FROM "System Settings"')

if [[ "$REV" != "$IRL_REV" || "$NEW_IRL" == "true" ]]; then

    echo "Updating IRL definitions to latest revision..."
            sqlite3 /var/lib/rn_irl/irl.sdb <<EOF
ATTACH DATABASE '$IRL_GIT_DB' AS newdb;
DROP TABLE IF EXISTS IRL;
CREATE TABLE IRL AS SELECT * FROM newdb.IRL;
DETACH DATABASE newdb;
EOF
    echo "IRL table updated successfully."
else
    echo "RN IRL Database System Settings up to date, moving on..."
fi


HAS_COL=$(sqlite3 "$IRL_PROD_DB" "SELECT project_description FROM 'IRL Data';" 2>&1)

if [[ "$HAS_COL" == *"$ERROR"* ]]; then
        echo "RN IRL Database IRL Data table not up to date, adding column project_description."
        sqlite3 "$IRL_PROD_DB" 'ALTER TABLE "IRL Data" ADD COLUMN project_description TEXT;'
else
        echo "RN IRL Database IRL Data table up to date, moving on..."
fi

HAS_COL=$(sqlite3 "$IRL_PROD_DB" "SELECT project_notes FROM 'IRL Data';" 2>&1)

if [[ "$HAS_COL" == *"$ERROR"* ]]; then
        echo "RN IRL Database IRL Data table not up to date, adding column project_notes."
        sqlite3 "$IRL_PROD_DB" 'ALTER TABLE "IRL Data" ADD COLUMN project_notes TEXT;'
else
        echo "RN IRL Database IRL Data table up to date, moving on..."
fi