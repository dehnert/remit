#!/bin/sh

set -euf

settings=$(dirname "$0")
base="$settings/.."

echo Creating config files...
secret=$(python -c "import random; print(''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789@#%&-_=+') for i in range(50)]))")
secret_re="s/^#SECRET_KEY = something$/SECRET_KEY = '$secret'/"
sed -e "$secret_re" < "$settings/local.dev-template.py" > "$settings/local.py"
touch "$settings/local_after.py"

echo
echo Creating database and doing basic sync...
$base/manage.py syncdb && $base/manage.py migrate

echo
echo Creating accounts...
$base/util/setup.py
$base/util/add_accounts Accounts.Assets <<EOF
Officers	1234567
Officers.President
Officers.President.Gifts
Officers.Treasurer
Officers.Treasurer.Stamps
Officers.Publicity
Officers.Publicity.Copying
Committees	1234567
Committees.Art
Committees.Art.Software
Committees.Logistics
Committees.Logistics.Food
Committees.Logistics.Rooms
EOF

echo
echo Creating budget term...
$base/manage.py shell <<EOF
from finance_core.models import BudgetTerm
import datetime
today = datetime.date.today()
year = today.year
term, created = BudgetTerm.objects.get_or_create(name=year, defaults=dict(
    slug=year,
    start_date=datetime.date(year, 1, 1),
    end_date=datetime.date(year, 12, 31),
    submit_deadline=datetime.date(year+1, 4, 15),
))
if created:
    term.save()
EOF

echo; echo
echo Done!
echo 'Run the server with "./manage.py runserver 8006" or similar.'
