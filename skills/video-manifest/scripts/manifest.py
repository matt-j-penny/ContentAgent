#!/usr/bin/env python3
"""Video manifest helper.

  manifest.py init   <dir> [--name NAME]   create manifest.json + starter template bank
  manifest.py render <dir>                 write templates/_brand.css and manifest.html
  manifest.py gaps   <dir> [--profile P]   list fields still empty (what to ask about)
  manifest.py lock   <dir> <path>...       mark fields as user-set so analysis never overwrites them
  manifest.py resolve <dir> --profile P   print the base with the selected profile merged in
"""
import json, shutil, sys, datetime
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
STARTERS = ASSETS / "starter-templates"


def blank(v):
    if isinstance(v, dict):
        return {k: blank(x) for k, x in v.items()}
    return [] if isinstance(v, list) else None


def load(d):
    return json.loads((Path(d) / "manifest.json").read_text())


def save(d, m):
    (Path(d) / "manifest.json").write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")


def init(d, name=None):
    d = Path(d)
    if (d / "manifest.json").exists():
        sys.exit(f"{d}/manifest.json already exists - update it instead of re-initialising")
    if (d / "templates").exists() and any((d / "templates").iterdir()):
        sys.exit(f"{d}/templates already contains files - choose another directory")
    ex = json.loads((ASSETS / "manifest.example.json").read_text())
    today = datetime.date.today().isoformat()
    m = {
        "meta": {"name": name, "version": 1, "updated": today, "sources": []},
        "base": blank(ex["base"]),
        "profiles": {},
        "templates": json.loads((STARTERS / "templates.json").read_text()),
        "evidence": {"stats": [], "frames": []},
        "_sources": {},
        "_locked": [],
    }
    (d / "sources").mkdir(parents=True, exist_ok=True)
    shutil.copytree(STARTERS, d / "templates", dirs_exist_ok=True, ignore=shutil.ignore_patterns("templates.json"))
    save(d, m)
    print(f"created {d}/manifest.json with {len(m['templates'])} starter templates")


def brand_css(m):
    b = (m.get("base") or {}).get("brand") or {}
    c = b.get("colors") or {}
    t = b.get("typography") or {}
    mo = ((m.get("base") or {}).get("motionGraphics") or {}).get("motion") or {}
    fams, urls = {}, []
    for f in t.values():
        if isinstance(f, dict) and f.get("cssUrl"):
            urls.append(f["cssUrl"])  # non-Google fonts (Fontshare, self-hosted)
        elif isinstance(f, dict) and f.get("family"):
            fams.setdefault(f["family"], {400}).add(int(f.get("weight") or 400))
    imp = "".join(f"@import url('{u}');\n" for u in dict.fromkeys(urls)) + "".join(
        f"@import url('https://fonts.googleapis.com/css2?family={f.replace(' ', '+')}:wght@{';'.join(map(str, sorted(w)))}&display=swap');\n"
        for f, w in sorted(fams.items()))
    var = lambda k, v: f"  --{k}: {v};\n" if v not in (None, "") else ""
    fam = lambda r: f"'{t[r]['family']}', system-ui, sans-serif" if isinstance(t.get(r), dict) and t[r].get("family") else None
    radius = (b.get("shapes") or {}).get("radius")
    return imp + ":root {\n" + "".join([
        var("c-primary", c.get("primary")), var("c-secondary", c.get("secondary")),
        var("c-accent", c.get("accent")), var("c-bg", c.get("background")),
        var("c-text", c.get("text")), var("c-muted", c.get("muted")),
        var("font-heading", fam("heading")), var("font-body", fam("body")),
        var("font-caption", fam("caption")), var("font-numeric", fam("numeric")),
        var("radius", f"{radius}px" if isinstance(radius, (int, float)) else None),
        var("ease", mo.get("easing")),
        var("dur-in", f"{mo['inMs']}ms" if mo.get("inMs") else None),
        var("dur-out", f"{mo['outMs']}ms" if mo.get("outMs") else None),
        var("stagger", f"{mo['staggerMs']}ms" if mo.get("staggerMs") else None),
    ]) + "}\n"


def render(d):
    d = Path(d)
    m = load(d)
    (d / "templates").mkdir(exist_ok=True)
    (d / "templates" / "_brand.css").write_text(brand_css(m))
    data = json.dumps(m, ensure_ascii=False).replace("</", "<\\/")
    html = (ASSETS / "manifest.template.html").read_text().replace("/*MANIFEST*/", data)
    (d / "manifest.html").write_text(html)
    print(f"wrote {d}/manifest.html")


def empty(v):
    return v is None or v == "" or v == [] or v == {}


def walk(v, p=""):
    if isinstance(v, dict) and v:
        for k, x in v.items():
            yield from walk(x, f"{p}.{k}" if p else k)
    else:
        yield p, v


def merge(a, b):
    if not (isinstance(a, dict) and isinstance(b, dict)):
        return a if b is None else b
    return {**a, **{k: merge(a.get(k), v) for k, v in b.items()}}


def resolve(d, profile):
    m = load(d)
    if not profile or profile not in m.get("profiles", {}):
        sys.exit(f"Unknown profile: {profile!r}; choose one of: {', '.join(m.get('profiles', {})) or 'none'}")
    print(json.dumps(merge(m.get("base") or {}, m["profiles"][profile]), indent=2, ensure_ascii=False))


def gaps(d, profile=None):
    m = load(d)
    data = m["base"]
    if profile:
        data = merge(data, m["profiles"].get(profile) or {})
    missing = [p for p, v in walk(data) if empty(v)]
    if not m["profiles"]:
        missing.insert(0, "profiles (none defined)")
    print("\n".join(missing) or "no gaps")
    print(f"\n{len(missing)} empty field(s)", file=sys.stderr)


def lock(d, paths):
    m = load(d)
    m["_locked"] = sorted(set(m.get("_locked", [])) | set(paths))
    save(d, m)
    print(f"locked: {', '.join(paths)}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    cmd, d = a[0], a[1]
    opt = lambda f: a[a.index(f) + 1] if f in a else None
    if cmd == "init":
        init(d, opt("--name"))
    elif cmd == "render":
        render(d)
    elif cmd == "gaps":
        gaps(d, opt("--profile"))
    elif cmd == "resolve":
        resolve(d, opt("--profile"))
    elif cmd == "lock":
        lock(d, a[2:])
    else:
        sys.exit(__doc__)
