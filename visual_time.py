#!/usr/bin/env python3
"""
visual-time: sky-gradient timezone ruler in your terminal.

Usage:
  python visual_time.py
  python visual_time.py --cities "Tokyo, Berlin, Chicago"
  python visual_time.py -c "London, New York" --watch
  python visual_time.py --list
"""

import argparse
import sys
import time
import shutil
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    try:
        from backports.zoneinfo import ZoneInfo
    except ImportError:
        print("Error: requires Python 3.9+ or 'pip install backports.zoneinfo'", file=sys.stderr)
        sys.exit(1)

# ── Sky gradient (one RGB tuple per integer hour 0–23) ───────────────────────
SKY = [
    ( 10,  14,  39),  #  0 midnight deep navy
    (  9,  12,  36),  #  1
    (  7,  16,  43),  #  2
    (  6,  17,  46),  #  3 darkest
    ( 12,  28,  78),  #  4
    ( 30,  48, 112),  #  5 pre-dawn indigo
    (120, 136, 192),  #  6 dawn twilight blue-purple
    (232, 160,  96),  #  7 golden sunrise
    (135, 206, 235),  #  8 morning sky
    (106, 192, 234),  #  9
    ( 85, 184, 240),  # 10
    ( 72, 180, 240),  # 11
    ( 66, 176, 240),  # 12 noon vivid blue
    ( 72, 180, 240),  # 13
    ( 88, 184, 240),  # 14
    (112, 188, 236),  # 15
    (232, 184, 112),  # 16 golden hour
    (224, 112,  56),  # 17 sunset orange
    (176,  56,  32),  # 18 deep sunset red
    (107,  32, 117),  # 19 dusk purple
    ( 52,  22,  82),  # 20 early night
    ( 26,  14,  56),  # 21
    ( 14,  13,  46),  # 22
    ( 10,  14,  39),  # 23
]

# ── City database ─────────────────────────────────────────────────────────────
CITY_DB = [
    ('Abu Dhabi',        'Asia/Dubai'),
    ('Accra',            'Africa/Accra'),
    ('Addis Ababa',      'Africa/Addis_Ababa'),
    ('Adelaide',         'Australia/Adelaide'),
    ('Almaty',           'Asia/Almaty'),
    ('Amsterdam',        'Europe/Amsterdam'),
    ('Anchorage',        'America/Anchorage'),
    ('Ankara',           'Europe/Istanbul'),
    ('Athens',           'Europe/Athens'),
    ('Atlanta',          'America/New_York'),
    ('Auckland',         'Pacific/Auckland'),
    ('Baghdad',          'Asia/Baghdad'),
    ('Bahrain',          'Asia/Bahrain'),
    ('Bangkok',          'Asia/Bangkok'),
    ('Barcelona',        'Europe/Madrid'),
    ('Beijing',          'Asia/Shanghai'),
    ('Beirut',           'Asia/Beirut'),
    ('Belgrade',         'Europe/Belgrade'),
    ('Berlin',           'Europe/Berlin'),
    ('Bogota',           'America/Bogota'),
    ('Boston',           'America/New_York'),
    ('Brisbane',         'Australia/Brisbane'),
    ('Brussels',         'Europe/Brussels'),
    ('Bucharest',        'Europe/Bucharest'),
    ('Budapest',         'Europe/Budapest'),
    ('Buenos Aires',     'America/Argentina/Buenos_Aires'),
    ('Cairo',            'Africa/Cairo'),
    ('Calgary',          'America/Edmonton'),
    ('Cape Town',        'Africa/Johannesburg'),
    ('Casablanca',       'Africa/Casablanca'),
    ('Chicago',          'America/Chicago'),
    ('Colombo',          'Asia/Colombo'),
    ('Copenhagen',       'Europe/Copenhagen'),
    ('Dallas',           'America/Chicago'),
    ('Dar es Salaam',    'Africa/Dar_es_Salaam'),
    ('Delhi',            'Asia/Kolkata'),
    ('Denver',           'America/Denver'),
    ('Detroit',          'America/Detroit'),
    ('Dhaka',            'Asia/Dhaka'),
    ('Doha',             'Asia/Qatar'),
    ('Dubai',            'Asia/Dubai'),
    ('Dublin',           'Europe/Dublin'),
    ('Edinburgh',        'Europe/London'),
    ('Frankfurt',        'Europe/Berlin'),
    ('Guadalajara',      'America/Mexico_City'),
    ('Hanoi',            'Asia/Bangkok'),
    ('Havana',           'America/Havana'),
    ('Helsinki',         'Europe/Helsinki'),
    ('Ho Chi Minh City', 'Asia/Ho_Chi_Minh'),
    ('Hong Kong',        'Asia/Hong_Kong'),
    ('Honolulu',         'Pacific/Honolulu'),
    ('Houston',          'America/Chicago'),
    ('Islamabad',        'Asia/Karachi'),
    ('Istanbul',         'Europe/Istanbul'),
    ('Jakarta',          'Asia/Jakarta'),
    ('Jerusalem',        'Asia/Jerusalem'),
    ('Johannesburg',     'Africa/Johannesburg'),
    ('Kabul',            'Asia/Kabul'),
    ('Karachi',          'Asia/Karachi'),
    ('Kathmandu',        'Asia/Kathmandu'),
    ('Kolkata',          'Asia/Kolkata'),
    ('Kuala Lumpur',     'Asia/Kuala_Lumpur'),
    ('Kuwait City',      'Asia/Kuwait'),
    ('Kyiv',             'Europe/Kyiv'),
    ('Lagos',            'Africa/Lagos'),
    ('Lahore',           'Asia/Karachi'),
    ('Las Vegas',        'America/Los_Angeles'),
    ('Lima',             'America/Lima'),
    ('Lisbon',           'Europe/Lisbon'),
    ('London',           'Europe/London'),
    ('Los Angeles',      'America/Los_Angeles'),
    ('Madrid',           'Europe/Madrid'),
    ('Manila',           'Asia/Manila'),
    ('Melbourne',        'Australia/Melbourne'),
    ('Mexico City',      'America/Mexico_City'),
    ('Miami',            'America/New_York'),
    ('Milan',            'Europe/Rome'),
    ('Minneapolis',      'America/Chicago'),
    ('Minsk',            'Europe/Minsk'),
    ('Montreal',         'America/Toronto'),
    ('Moscow',           'Europe/Moscow'),
    ('Mumbai',           'Asia/Kolkata'),
    ('Muscat',           'Asia/Muscat'),
    ('Nairobi',          'Africa/Nairobi'),
    ('Nashville',        'America/Chicago'),
    ('New York',         'America/New_York'),
    ('Oslo',             'Europe/Oslo'),
    ('Ottawa',           'America/Toronto'),
    ('Panama City',      'America/Panama'),
    ('Paris',            'Europe/Paris'),
    ('Perth',            'Australia/Perth'),
    ('Philadelphia',     'America/New_York'),
    ('Phoenix',          'America/Phoenix'),
    ('Phnom Penh',       'Asia/Phnom_Penh'),
    ('Portland',         'America/Los_Angeles'),
    ('Prague',           'Europe/Prague'),
    ('Riyadh',           'Asia/Riyadh'),
    ('Rio de Janeiro',   'America/Sao_Paulo'),
    ('Rome',             'Europe/Rome'),
    ('San Francisco',    'America/Los_Angeles'),
    ('Santiago',         'America/Santiago'),
    ('Sao Paulo',        'America/Sao_Paulo'),
    ('Seattle',          'America/Los_Angeles'),
    ('Seoul',            'Asia/Seoul'),
    ('Shanghai',         'Asia/Shanghai'),
    ('Singapore',        'Asia/Singapore'),
    ('Sofia',            'Europe/Sofia'),
    ('Stockholm',        'Europe/Stockholm'),
    ('Sydney',           'Australia/Sydney'),
    ('Taipei',           'Asia/Taipei'),
    ('Tashkent',         'Asia/Tashkent'),
    ('Tehran',           'Asia/Tehran'),
    ('Tel Aviv',         'Asia/Jerusalem'),
    ('Tokyo',            'Asia/Tokyo'),
    ('Toronto',          'America/Toronto'),
    ('Tunis',            'Africa/Tunis'),
    ('Ulaanbaatar',      'Asia/Ulaanbaatar'),
    ('Vancouver',        'America/Vancouver'),
    ('Vienna',           'Europe/Vienna'),
    ('Warsaw',           'Europe/Warsaw'),
    ('Washington DC',    'America/New_York'),
    ('Wellington',       'Pacific/Auckland'),
    ('Yangon',           'Asia/Yangon'),
    ('Zurich',           'Europe/Zurich'),
]

DEFAULTS = [
    ('New York',  'America/New_York'),
    ('London',    'Europe/London'),
    ('Dubai',     'Asia/Dubai'),
    ('Singapore', 'Asia/Singapore'),
]

# Longest city name in the DB, used for column alignment
_MAX_NAME = max(len(name) for name, _ in CITY_DB)

RESET = '\x1b[0m'
DIM   = '\x1b[2m'


def _supports_color():
    return sys.stdout.isatty()


def _bg(r, g, b):
    return f'\x1b[48;2;{r};{g};{b}m'

def _fg(r, g, b):
    return f'\x1b[38;2;{r};{g};{b}m'


def lerp_color(hour):
    """Interpolated sky RGB for a fractional hour (wraps at 24)."""
    h  = hour % 24
    h0 = int(h)
    h1 = (h0 + 1) % 24
    t  = h - h0
    return tuple(int(SKY[h0][i] + (SKY[h1][i] - SKY[h0][i]) * t) for i in range(3))


def find_city(query):
    """Case-insensitive lookup: exact match first, then prefix."""
    q = query.strip().lower()
    for name, tz in CITY_DB:
        if name.lower() == q:
            return name, tz
    for name, tz in CITY_DB:
        if name.lower().startswith(q):
            return name, tz
    return None, None


def get_time_info(tz):
    """Return (fractional_hour, 'HH:MM') for the given IANA timezone."""
    now = datetime.now(ZoneInfo(tz))
    start = now.hour + now.minute / 60 + now.second / 3600
    return start, now.strftime('%H:%M')


def render_row(name, tz, ruler_width, window_hours, color):
    """
    Return (ruler_line, labels_line) for one city row.

    ruler_line  — city name + clock + colour-gradient bar with tick marks
    labels_line — blank label padding + hour labels at 3-hour intervals
    """
    start_hour, time_str = get_time_info(tz)
    end_hour = start_hour + window_hours

    # ── Pre-compute tick / midnight columns ──────────────────────────────────
    ticks     = {}   # col_index -> 'tall' | 'short'
    midnights = {}   # col_index -> True

    first_h = int(start_hour) + 1
    for h in range(first_h, int(end_hour) + 2):
        if h > end_hour + 1e-9:
            break
        col = (h - start_hour) / window_hours * ruler_width
        col_i = round(col)
        if 0 < col_i < ruler_width:
            if h % 24 == 0:
                midnights[col_i] = True
            elif h % 3 == 0:
                ticks[col_i] = 'tall'
            else:
                ticks[col_i] = 'short'

    # ── Build the gradient ruler ─────────────────────────────────────────────
    label      = f'{name.upper():<{_MAX_NAME}}  {time_str}  '
    label_width = len(label)

    if color:
        ruler_parts = []
        for i in range(ruler_width):
            hour = start_hour + (i / ruler_width) * window_hours
            r, g, b = lerp_color(hour)
            cell_bg = _bg(r, g, b)

            if i in midnights:
                char     = '│'
                cell_fg  = _fg(255, 255, 255)
            elif i in ticks:
                char     = '│' if ticks[i] == 'tall' else '╷'
                # approximate mix-blend-mode: difference
                cell_fg  = _fg(255 - r, 255 - g, 255 - b)
            else:
                char     = ' '
                cell_fg  = ''

            ruler_parts.append(cell_bg + cell_fg + char + RESET)

        ruler_str = ''.join(ruler_parts)
    else:
        # Plain ASCII ruler: dashes with pipe ticks
        chars = ['-'] * ruler_width
        for col_i in midnights:
            chars[col_i] = '|'
        for col_i, kind in ticks.items():
            chars[col_i] = '|' if kind == 'tall' else '+'
        ruler_str = ''.join(chars)

    # ── Build the hour-label line ────────────────────────────────────────────
    label_chars = [' '] * ruler_width
    for h in range(first_h, int(end_hour) + 1):
        if h % 3 == 0:
            col_f = (h - start_hour) / window_hours * ruler_width
            col_i = round(col_f)
            s     = f'{h % 24:02d}:00'
            start_c = col_i - len(s) // 2
            for j, c in enumerate(s):
                idx = start_c + j
                if 0 <= idx < ruler_width:
                    label_chars[idx] = c

    pad        = ' ' * label_width
    labels_str = (DIM if color else '') + ''.join(label_chars) + (RESET if color else '')

    return label + ruler_str, pad + labels_str


def render_all(locations, ruler_width, window_hours, color):
    lines = []
    for name, tz in locations:
        l1, l2 = render_row(name, tz, ruler_width, window_hours, color)
        lines.append(l1)
        lines.append(l2)
    return lines


def parse_cities(cities_str):
    """Parse a comma-delimited city string into (name, tz) pairs."""
    results = []
    for raw in cities_str.split(','):
        query = raw.strip()
        if not query:
            continue
        name, tz = find_city(query)
        if name is None:
            print(f"Warning: city not found: '{query}'", file=sys.stderr)
        else:
            results.append((name, tz))
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Visual Time — sky-gradient timezone ruler in your terminal.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  %(prog)s
  %(prog)s --cities "Tokyo, Berlin, Chicago"
  %(prog)s -c "Sydney, Los Angeles" --watch
  %(prog)s --list
        """,
    )
    parser.add_argument(
        '-c', '--cities',
        metavar='CITIES',
        help='Comma-separated list of cities (default: New York, London, Dubai, Singapore)',
    )
    parser.add_argument(
        '-w', '--watch',
        action='store_true',
        help='Refresh every second (live clock mode)',
    )
    parser.add_argument(
        '--window',
        type=int,
        default=24,
        metavar='HOURS',
        help='Hours shown in the ruler (default: 24)',
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable ANSI colour output',
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available cities and exit',
    )
    args = parser.parse_args()

    if args.list:
        try:
            for name, tz in CITY_DB:
                print(f'{name:<20}  {tz}')
        except BrokenPipeError:
            pass
        return

    color = _supports_color() and not args.no_color

    if args.cities:
        locations = parse_cities(args.cities)
        if not locations:
            print('Error: no valid cities found.', file=sys.stderr)
            sys.exit(1)
    else:
        locations = DEFAULTS

    term_width  = shutil.get_terminal_size((80, 24)).columns
    label_width = _MAX_NAME + 2 + 5 + 2   # name + "  " + "HH:MM" + "  "
    ruler_width = max(20, term_width - label_width)

    header      = f'VISUAL TIME  ·  {args.window}-hour window'

    if args.watch:
        num_content_lines = len(locations) * 2
        first = True
        try:
            while True:
                lines = render_all(locations, ruler_width, args.window, color)
                if not first:
                    # Move cursor back up to overwrite
                    sys.stdout.write(f'\x1b[{num_content_lines + 2}A')
                # Print header
                sys.stdout.write(f'\x1b[2K{DIM if color else ""}{header}{RESET if color else ""}\n')
                sys.stdout.write('\x1b[2K\n')
                for line in lines:
                    sys.stdout.write(f'\x1b[2K{line}\n')
                sys.stdout.flush()
                first = False
                time.sleep(1)
        except KeyboardInterrupt:
            print()
    else:
        if color:
            print(f'{DIM}{header}{RESET}')
        else:
            print(header)
        print()
        for line in render_all(locations, ruler_width, args.window, color):
            print(line)


if __name__ == '__main__':
    main()
