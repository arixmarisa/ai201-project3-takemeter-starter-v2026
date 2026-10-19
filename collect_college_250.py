#!/usr/bin/env python3
"""TakeMeter r/college collection: preserve 20 independent labels; review 180 + minority 50.

Run: python collect_college_250.py
Then review college_candidates.csv (fill final_label and review_status=APPROVED).
Run: python collect_college_250.py --build-initial
Then review 50 BONUS candidates for the minority label; fill final_label, review_status.
Run: python collect_college_250.py --build-final

No dependencies, uses Arctic Shift public archive. Does not rewrite existing labels.csv.
"""
import argparse
import csv
import html
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
API = 'https://arctic-shift.photon-reddit.com'
LABELS = ('academic_advice', 'college_experience', 'campus_life', 'financial_concerns')
FIRST = ROOT / 'college_first_20_human_labels.csv'
INITIAL = ROOT / 'college_first_20_with_text.csv'
POOL = ROOT / 'college_candidates.csv'
BONUS = ROOT / 'college_bonus_review.csv'
BASE = ROOT / 'college_initial_200.csv'
FINAL = ROOT / 'college_labels_250.csv'
HEADERS = {'User-Agent': 'TakeMeter-College-Research/1.0', 'Accept': 'application/json'}
COLS = ['post_id','url','title','text','created_utc','suggested_label','final_label','review_status','note']


def fetch(endpoint, args):
    url = API + endpoint + '?' + urlencode(args)
    for attempt in range(4):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=45) as response:
                raw = json.load(response)
            return raw.get('data', []) if isinstance(raw, dict) else raw
        except (HTTPError, URLError, ValueError, TimeoutError) as exc:
            if attempt == 3:
                raise RuntimeError(f'Archive request failed: {exc}; URL={url}') from exc
            time.sleep(2 * (attempt + 1))


def clean(p, min_body=20):
    if not isinstance(p, dict) or str(p.get('subreddit', '')).casefold() != 'college':
        return None
    if p.get('over_18') or p.get('removed_by_category'):
        return None
    title = html.unescape(str(p.get('title') or '')).strip()
    body = html.unescape(str(p.get('selftext') or '')).strip()
    if not title or not body or body.lower() in ('[removed]', '[deleted]') or len(body.split()) < min_body:
        return None
    if re.search(r'\b(megathread|weekly thread|monthly thread|mod post)\b', title, re.I):
        return None
    ident = str(p.get('id') or '').removeprefix('t3_').strip()
    if not ident:
        return None
    url = f'https://www.reddit.com/r/college/comments/{ident}/'
    return {'post_id': ident, 'url': url, 'title': title,
            'text': title + '\n\n' + body, 'created_utc': p.get('created_utc', ''),
            'suggested_label': '', 'final_label': '', 'review_status': 'NEEDS REVIEW',
            'note': 'Original r/college submission text; label must be reviewed'}


def read_csv(path):
    if not path.exists():
        return []
    with path.open(newline='', encoding='utf-8-sig') as file:
        return list(csv.DictReader(file))


def write_csv(path, rows, cols=COLS):
    with path.open('w', newline='', encoding='utf-8') as file:
        w = csv.DictWriter(file, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)


def key(text):
    return ' '.join(text.casefold().split())


def suggest(text):
    """Weak prioritization hint only. Human must review. Never use as final_label."""
    s = text.casefold()
    if re.search(r'\b(financial aid|fafsa|scholarship|tuition|student loan|student debt|grant|bursar|payment plan)\b', s):
        return 'financial_concerns'
    if re.search(r'\b(roommate|dorm|residence hall|campus housing|friendship|club|fraternity|sorority|campus life)\b', s):
        return 'campus_life'
    if re.search(r'\b(study|studying|professor|grade|gpa|exam|class|course|credits|finals|major|drop a class)\b', s) and re.search(r'\b(help|advice|should i|how do|what do|tips|recommend|question)\b', s):
        return 'academic_advice'
    return 'college_experience'


def get_first_20():
    original = read_csv(FIRST)
    if len(original) != 20 or len({r.get('post_id') for r in original}) != 20:
        raise SystemExit('Expected exactly 20 unique post_id entries in college_first_20_human_labels.csv')
    ids = [r['post_id'].strip() for r in original]
    results = fetch('/api/posts/ids', {'ids': ','.join(ids)})
    by_id = {}
    for p in results:
        item = clean(p, min_body=1)
        if item:
            by_id[item['post_id']] = item
    rows, unresolved = [], []
    for r in original:
        ident = r['post_id'].strip()
        label = (r.get('label') or '').strip()
        if label not in LABELS:
            raise SystemExit(f'Invalid first-20 label for post {ident}: {label}')
        if ident in by_id:
            d = by_id[ident]
            d.update(final_label=label, suggested_label='', review_status='HUMAN LABELED',
                     note='One of first 20: labeled independently before AI assistance; source=' + d['url'])
        else:
            d = {'post_id':ident, 'url':r.get('post_url') or r.get('url') or '',
                 'title':'', 'text':'', 'created_utc':'', 'suggested_label':'',
                 'final_label':label, 'review_status':'TEXT NOT FOUND',
                 'note':'Human label preserved; archive returned no usable original body'}
            unresolved.append(ident)
        rows.append(d)
    write_csv(INITIAL, rows)
    print(f'First 20: {20-len(unresolved)} full texts recovered; {len(unresolved)} require manual source text lookup.')
    if unresolved:
        print('Missing original text for IDs:', ', '.join(unresolved))
    return rows


def collect():
    first = get_first_20()
    existing = {r['post_id'] for r in first}
    seen_text = {key(r['text']) for r in first if r.get('text')}
    found = []
    before = None
    print('Collecting additional, unique r/college posts. Target: 400 review candidates.')
    for page in range(130):
        args = {'subreddit':'college', 'sort':'desc', 'limit':100}
        if before:
            args['before'] = before
        batch = fetch('/api/posts/search', args)
        if not batch:
            break
        timestamps = []
        for p in batch:
            if isinstance(p, dict) and isinstance(p.get('created_utc'), (int, float)):
                timestamps.append(p['created_utc'])
            item = clean(p)
            if not item or item['post_id'] in existing or key(item['text']) in seen_text:
                continue
            existing.add(item['post_id'])
            seen_text.add(key(item['text']))
            item['suggested_label'] = suggest(item['text'])
            found.append(item)
        print(f'Page {page+1}: {len(found)} unique candidates')
        if len(found) >= 400 or not timestamps:
            break
        cutoff = min(timestamps) - 1
        next_before = datetime.fromtimestamp(max(0, cutoff), timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
        if before == next_before:
            break
        before = next_before
        time.sleep(0.5)
    write_csv(POOL, found)
    print(f'Wrote {len(found)} real text candidates: {POOL.name}')
    print('Review candidates: final_label must be one of the four labels, and review_status=APPROVED.')
    print('After 180 accepted candidates, run: python collect_college_250.py --build-initial')
    if len(found) < 230:
        print('WARNING: fewer than 230 additional candidates; collect more or loosen filtering.')


def reviewed(r):
    return r.get('review_status','').strip().upper() == 'APPROVED' and r.get('final_label','').strip() in LABELS and bool(r.get('text','').strip())


def build_initial():
    first = read_csv(INITIAL)
    missing = [r['post_id'] for r in first if not r.get('text','').strip()]
    if len(first) != 20 or missing:
        raise SystemExit(f'Initial 20 need original text. Missing: {missing}; do not discard original human labels.')
    pool = read_csv(POOL)
    accepted = [r for r in pool if reviewed(r)]
    if len(accepted) < 180:
        raise SystemExit(f'Only {len(accepted)} approved candidates. Review at least 180 in {POOL.name} first.')
    used_ids = {r['post_id'] for r in first}
    used_text = {key(r['text']) for r in first}
    base = list(first)
    for r in accepted:
        if r['post_id'] not in used_ids and key(r['text']) not in used_text:
            base.append(r)
            used_ids.add(r['post_id'])
            used_text.add(key(r['text']))
            if len(base) == 200:
                break
    if len(base) < 200:
        raise SystemExit('Too few unique approved texts to reach 200.')
    write_csv(BASE, base)
    counts = Counter(r['final_label'] for r in base)
    minority = min(LABELS, key=lambda x: (counts[x], LABELS.index(x)))
    print('INITIAL 200 verified count:', dict(counts))
    print('MINORITY LABEL for +50:', minority)
    # Keep all remaining candidates visible, prioritizing tentative minority matches.
    extra = [r for r in pool if r['post_id'] not in used_ids and key(r['text']) not in used_text]
    extra.sort(key=lambda r: (r.get('suggested_label') != minority, r['post_id']))
    write_csv(BONUS, extra)
    print(f'Wrote {BONUS.name} ({len(extra)} potential extras). Check each one, and approve 50 REAL {minority} posts.')
    return minority, base


def build_final():
    first200 = read_csv(BASE)
    if len(first200) != 200:
        raise SystemExit('First create the 200-row checkpoint with --build-initial.')
    counts = Counter(r['final_label'] for r in first200)
    minority = min(LABELS, key=lambda x: (counts[x], LABELS.index(x)))
    approved = [r for r in read_csv(BONUS) if reviewed(r) and r['final_label'] == minority]
    used_ids = {r['post_id'] for r in first200}
    used_text = {key(r['text']) for r in first200}
    final = list(first200)
    for r in approved:
        if r['post_id'] in used_ids or key(r['text']) in used_text:
            continue
        final.append(r)
        used_ids.add(r['post_id'])
        used_text.add(key(r['text']))
        if len(final) == 250:
            break
    if len(final) != 250:
        raise SystemExit(f'Need 50 approved unique {minority} posts; only found {len(final)-200}. No final CSV written.')
    out = [{'text':r['text'],'label':r['final_label'],
            'note':f"source={r['url']}; {r.get('note', '')}; reviewed_by=student"} for r in final]
    write_csv(FINAL, out, ['text','label','note'])
    end_counts = Counter(r['label'] for r in out)
    print('Final dataset:', FINAL.name, 'rows:', len(out))
    print('Before extra 50:', dict(counts), 'Minority:', minority)
    print('After extra 50:', dict(end_counts))
    if max(end_counts.values()) > .4 * len(out):
        print('WARNING: A category is over 40% after the minority bonus. Document this, do not falsify labels.')
    print('Back up existing labels.csv; then copy college_labels_250.csv to labels.csv to train.')


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--build-initial', action='store_true')
    mode.add_argument('--build-final', action='store_true')
    args = parser.parse_args()
    if args.build_final:
        build_final()
    elif args.build_initial:
        build_initial()
    else:
        collect()

if __name__ == '__main__':
    main()
