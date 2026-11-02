#!/usr/bin/env python3
import hashlib,json,pathlib,subprocess,time,urllib.request,urllib.parse,signal,sys
base=pathlib.Path.home()/'.config/eww'
cache=pathlib.Path.home()/'.cache/eww-gruvbox';cache.mkdir(parents=True,exist_ok=True)
fallback=str(base/'assets/music.svg')
last_art=None;cover=fallback

def query(*args):
    try:
        r=subprocess.run(['playerctl',*args],capture_output=True,text=True,timeout=2)
        return r.stdout.strip() if r.returncode==0 else ''
    except (FileNotFoundError,subprocess.TimeoutExpired):return ''

def number(value):
    try:return float(value)
    except (ValueError,TypeError):return 0

def clock(value):
    value=max(0,int(value));return f'{value//60}:{value%60:02}'

def artwork(url):
    if not url:return fallback
    parsed=urllib.parse.urlparse(url)
    if parsed.scheme=='file':
        p=pathlib.Path(urllib.parse.unquote(parsed.path));return str(p) if p.is_file() else fallback
    if parsed.scheme not in ('http','https'):return fallback
    target=cache/(hashlib.sha256(url.encode()).hexdigest()+'.img')
    if target.exists():return str(target)
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Eww-local-music-widget/1.0'})
        with urllib.request.urlopen(req,timeout=3) as response:
            if not response.headers.get('Content-Type','').startswith('image/'):return fallback
            data=response.read(4*1024*1024+1)
        if len(data)>4*1024*1024:return fallback
        target.write_bytes(data);return str(target)
    except Exception:return fallback

try:
    while True:
        status=query('status')
        if status:
            title=query('metadata','title') or 'Untitled track'
            artist=query('metadata','artist') or 'Unknown artist'
            duration=number(query('metadata','mpris:length'))/1000000
            position=number(query('position'))
            art=query('metadata','mpris:artUrl')
        else:
            title='No media playing';artist='Open an MPRIS-compatible player'
            duration=position=0;art=''
        if art!=last_art:
            cover=artwork(art);last_art=art
        cover_style='background-image: linear-gradient(to right, rgba(0,2,0,0.70), rgba(0,2,0,0.18)), url("'+pathlib.Path(cover).as_uri()+'");'
        print(json.dumps({'title':title,'artist':artist,'playing':status=='Playing',
            'progress':max(0,min(100,100*position/duration)) if duration else 0,
            'elapsed':clock(position),'duration':clock(duration),'cover':cover,'cover_style':cover_style}),flush=True)
        time.sleep(1)
except (BrokenPipeError,KeyboardInterrupt):sys.exit(0)
