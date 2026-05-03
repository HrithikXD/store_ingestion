import re
import datetime
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import (
    Store, User, PermanentJourneyPlan,
    StoreBrand, StoreType, City, State, Country, Region
)

# Convert to lowercase before lookup
def normalize(val):
    if not val or not isinstance(val, str):
        return ''
    return val.strip().lower()

def parse_bool(val):
    return str(val).strip().lower() in ('true', '1', 'yes')

EMAIL_RE = re.compile(r'^[\w.+-]+@[\w-]+\.[\w.]+$')
VALID_USER_TYPES = {1, 2, 3, 7}

LOOKUP_MAP = {
    'store_brand': StoreBrand,
    'store_type':  StoreType,
    'city':        City,
    'state':       State,
    'country':     Country,
    'region':      Region,
}

class UploadStoresView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)
        
        df = pd.read_csv(file, dtype=str, keep_default_na=False)

        errors = []
        valid_stores = []
        seen_ids = set()  

        for idx, row in df.iterrows():
            row_num  = idx + 2 
            store_id = row.get('store_id', '').strip()
            name     = row.get('name', '').strip()
            title    = row.get('title', '').strip()

            if not store_id:
                errors.append({'row': row_num, 'column': 'store_id', 'reason': 'Required field missing'})
                continue
            if store_id in seen_ids:
                errors.append({'row': row_num, 'column': 'store_id', 'reason': 'Duplicate in file'})
                continue
            if Store.objects.filter(store_id=store_id).exists():
                errors.append({'row': row_num, 'column': 'store_id', 'reason': 'Already exists in DB'})
                continue
            if not name:
                errors.append({'row': row_num, 'column': 'name', 'reason': 'Required field missing'})
                continue
            if not title:
                errors.append({'row': row_num, 'column': 'title', 'reason': 'Required field missing'})
                continue
            try:
                lat = float(row.get('latitude', 0) or 0)
            except ValueError:
                errors.append({'row': row_num, 'column': 'latitude', 'reason': 'Must be a number'})
                continue
            try:
                lng = float(row.get('longitude', 0) or 0)
            except ValueError:
                errors.append({'row': row_num, 'column': 'longitude', 'reason': 'Must be a number'})
                continue

            seen_ids.add(store_id)

            fk_ids = {}
            for field, Model in LOOKUP_MAP.items():
                raw = row.get(field, '').strip()
                if raw:
                    obj, _ = Model.objects.get_or_create(name=normalize(raw))
                    fk_ids[f'{field}_id'] = obj.id

            valid_stores.append(Store(
                store_id=store_id,
                store_external_id=row.get('store_external_id', '').strip(),
                name=name,
                title=title,
                latitude=lat,
                longitude=lng,
                is_active=parse_bool(row.get('is_active', 'true')),
                **fk_ids
            ))

        Store.objects.bulk_create(valid_stores)

        return Response({
            'success_count': len(valid_stores),
            'error_count':   len(errors),
            'errors':        errors,
        }, status=200 if not errors else 207)


# ── Upload Users ──────────────────────────────────────────────────────────────

class UploadUsersView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)

        df = pd.read_csv(file, dtype=str, keep_default_na=False)

        errors = []
        valid_users = []
        seen_usernames = set()

        for idx, row in df.iterrows():
            row_num  = idx + 2
            username = row.get('username', '').strip()
            email    = row.get('email', '').strip()

            if not username:
                errors.append({'row': row_num, 'column': 'username', 'reason': 'Required field missing'})
                continue
            if len(username) > 150:
                errors.append({'row': row_num, 'column': 'username', 'reason': 'Exceeds 150 chars'})
                continue
            if username in seen_usernames:
                errors.append({'row': row_num, 'column': 'username', 'reason': 'Duplicate in file'})
                continue
            if User.objects.filter(username=username).exists():
                errors.append({'row': row_num, 'column': 'username', 'reason': 'Already exists in DB'})
                continue
            if not email or not EMAIL_RE.match(email):
                errors.append({'row': row_num, 'column': 'email', 'reason': 'Invalid or missing email'})
                continue
            try:
                user_type = int(row.get('user_type', 1) or 1)
                if user_type not in VALID_USER_TYPES:
                    raise ValueError
            except ValueError:
                errors.append({'row': row_num, 'column': 'user_type', 'reason': 'Must be 1, 2, 3, or 7'})
                continue

            seen_usernames.add(username)

            supervisor_username = row.get('supervisor', '').strip()
            supervisor = User.objects.filter(username=supervisor_username).first() if supervisor_username else None

            valid_users.append(User(
                username=username,
                first_name=row.get('first_name', '').strip(),
                last_name=row.get('last_name', '').strip(),
                email=email,
                user_type=user_type,
                phone_number=row.get('phone_number', '').strip(),
                supervisor=supervisor,
                is_active=parse_bool(row.get('is_active', 'true')),
            ))

        User.objects.bulk_create(valid_users)

        return Response({
            'success_count': len(valid_users),
            'error_count':   len(errors),
            'errors':        errors,
        }, status=200 if not errors else 207)


class UploadMappingView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)

        df = pd.read_csv(file, dtype=str, keep_default_na=False)

        valid_store_ids = set(Store.objects.values_list('store_id', flat=True))
        valid_usernames = set(User.objects.values_list('username', flat=True))

        errors = []
        valid_mappings = []
        seen_pairs = set()

        for idx, row in df.iterrows():
            row_num  = idx + 2
            store_id = row.get('store_id', '').strip()
            username = row.get('username', '').strip()
            date_str = row.get('date', '').strip()

            if store_id not in valid_store_ids:
                errors.append({'row': row_num, 'column': 'store_id', 'reason': f'Store not found: {store_id}'})
                continue
            if username not in valid_usernames:
                errors.append({'row': row_num, 'column': 'username', 'reason': f'User not found: {username}'})
                continue

            date_val = None
            if date_str:
                try:
                    date_val = datetime.date.fromisoformat(date_str)
                except ValueError:
                    errors.append({'row': row_num, 'column': 'date', 'reason': 'Invalid date, use YYYY-MM-DD'})
                    continue

            pair = (store_id, username, date_str)
            if pair in seen_pairs:
                errors.append({'row': row_num, 'column': 'store_id,username,date', 'reason': 'Duplicate mapping'})
                continue
            seen_pairs.add(pair)

            store = Store.objects.get(store_id=store_id)
            user  = User.objects.get(username=username)

            valid_mappings.append(PermanentJourneyPlan(
                store=store,
                user=user,
                date=date_val,
                is_active=parse_bool(row.get('is_active', 'true')),
            ))

        PermanentJourneyPlan.objects.bulk_create(valid_mappings, ignore_conflicts=True)

        return Response({
            'success_count': len(valid_mappings),
            'error_count':   len(errors),
            'errors':        errors,
        }, status=200 if not errors else 207)