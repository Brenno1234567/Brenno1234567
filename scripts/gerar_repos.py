"""Gera um card SVG neon para cada repositório público e atualiza o README."""
import json, os, re, textwrap, urllib.request
from html import escape
from pathlib import Path

USER = os.environ.get("GH_USER", "Brenno1234567")
MAXIMO = 8  # quantos repositórios aparecem
INICIO, FIM = "<!-- REPOS:INICIO -->", "<!-- REPOS:FIM -->"
CORES = {"GDScript": "#478cbf", "Python": "#3572A5", "JavaScript": "#f1e05a",
         "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#663399",
         "C#": "#178600", "Java": "#b07219", "PHP": "#4F5D95", "C++": "#f34b7d"}


def buscar():
    repos, pagina = [], 1
    while True:
        url = f"https://api.github.com/users/{USER}/repos?per_page=100&page={pagina}&sort=pushed"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        if os.environ.get("GITHUB_TOKEN"):
            req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
        with urllib.request.urlopen(req, timeout=30) as r:
            lote = json.load(r)
        repos += lote
        if len(lote) < 100:
            return repos
        pagina += 1


def cortar(texto, n):
    return texto if len(texto) <= n else texto[:n - 1] + "…"


def card(repo, i):
    linhas = textwrap.wrap(repo.get("description") or "Projeto sem descrição... ainda", 48)
    if len(linhas) > 2:
        linhas = [linhas[0], cortar(linhas[1] + "…", 48)]
    desc = "".join(f'<text x="22" y="{72 + n * 19}" class="d">{escape(l)}</text>'
                   for n, l in enumerate(linhas))
    lang = repo.get("language") or "Outros"
    data = "/".join(reversed(repo["pushed_at"][:10].split("-")))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="140" viewBox="0 0 420 140">
<style>
text{{font-family:'Fira Code',Consolas,monospace}}
.t{{fill:#e0aaff;font-size:17px;font-weight:700}}
.d{{fill:#c8b6e2;font-size:12px}}
.r{{fill:#9d8abf;font-size:11px}}
.b{{stroke-dasharray:140 960;animation:g 5s linear {-i * 0.7:.1f}s infinite}}
@keyframes g{{to{{stroke-dashoffset:-1100}}}}
@media (prefers-reduced-motion:reduce){{.b{{animation:none}}}}
</style>
<defs><linearGradient id="f" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#10002b"/><stop offset="1" stop-color="#240046"/></linearGradient></defs>
<rect x="2" y="2" width="416" height="136" rx="12" fill="url(#f)" stroke="#5a189a" stroke-width="2"/>
<rect class="b" x="2" y="2" width="416" height="136" rx="12" fill="none" stroke="#c77dff" stroke-width="2.5"/>
<text x="22" y="38" class="t">▶ {escape(cortar(repo["name"], 34))}</text>
{desc}
<circle cx="27" cy="115" r="5" fill="{CORES.get(lang, "#9d4edd")}"/>
<text x="39" y="119" class="r">{escape(lang)}</text>
<text x="190" y="119" class="r">★ {repo["stargazers_count"]}</text>
<text x="398" y="119" class="r" text-anchor="end">push {data}</text>
</svg>'''


def main(repos):
    escolhidos = [r for r in repos
                  if not r["fork"] and not r.get("private") and r["name"].lower() != USER.lower()]
    escolhidos.sort(key=lambda r: r["pushed_at"], reverse=True)
    pasta = Path("assets/repos")
    pasta.mkdir(parents=True, exist_ok=True)
    for antigo in pasta.glob("*.svg"):
        antigo.unlink()
    itens = []
    for i, r in enumerate(escolhidos[:MAXIMO]):
        arq = pasta / f"{r['name']}.svg"
        arq.write_text(card(r, i), encoding="utf-8")
        itens.append(f'<a href="{r["html_url"]}"><img src="./{arq.as_posix()}" '
                     f'width="49%" alt="{escape(r["name"])}"/></a>')
    bloco = "\n".join(itens) or "<i>Novas quests em breve...</i>"
    readme = Path("README.md")
    texto = readme.read_text(encoding="utf-8")
    if INICIO not in texto or FIM not in texto:
        raise SystemExit("Marcadores REPOS não encontrados no README.md")
    novo = re.sub(f"{INICIO}.*?{FIM}", lambda _: f"{INICIO}\n{bloco}\n{FIM}", texto, flags=re.S)
    readme.write_text(novo, encoding="utf-8")


if __name__ == "__main__":
    main(buscar())
         
