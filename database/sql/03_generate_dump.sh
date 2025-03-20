#!/bin/bash

DB_NAME="school_buses"
DB_USER="root"
DB_PASSWORD=""
DUMP_FILE="school_buses_dump_$(date +%Y%m%d_%H%M%S).sql"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting database dump...${NC}"

if [ -z "$DB_PASSWORD" ]; then
    mysqldump -u "$DB_USER" "$DB_NAME" > "$DUMP_FILE"
else
    mysqldump -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" > "$DUMP_FILE"
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database dump completed successfully!${NC}"
    echo -e "${GREEN}Dump file: $DUMP_FILE${NC}"
    
    gzip "$DUMP_FILE"
    echo -e "${GREEN}Dump file compressed: $DUMP_FILE.gz${NC}"
else
    echo -e "${RED}Error creating database dump${NC}"
    exit 1
fi 