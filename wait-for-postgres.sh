#!/bin/sh
# wait-for-postgres.sh

set -e

host=$POSTGRES_HOST
shift
cmd="$@"

echo $POSTGRES_USER
echo $POSTGRES_PASSWORD

until PGPASSWORD=$POSTGRES_PASSWORD  psql $POSTGRES_DB -U $POSTGRES_USER -h "$host"  -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
>&2 echo "waiting 5 seconds to start..."
sleep 5
echo $cmd
exec $cmd
