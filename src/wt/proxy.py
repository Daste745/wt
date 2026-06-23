from collections import defaultdict
from dataclasses import dataclass
from typing import final

from jinja2 import Template

from wt.util import strip_indented_string


@final
@dataclass(frozen=True)
class ProxyHost:
    config_id: str
    project_id: str
    worktree_name: str
    port: int

    @property
    def hostname(self) -> str:
        return get_proxy_hostname(self.worktree_name, self.project_id, self.config_id)


def get_proxy_hostname(
    worktree_name: str,
    project_id: str,
    config_id: str,
) -> str:
    return f"{worktree_name}.{project_id}.{config_id}.localhost"


def get_proxy_host_config(
    host: ProxyHost,
) -> str:
    return strip_indented_string(f"""
        {host.hostname}:80 {{
            reverse_proxy localhost:{host.port}
        }}
    """).strip()


# TODO)) Remove this ugly whitespace
# Indentation is used to match the heredoc `<<HTML` and `HTML 200` in the Caddyfile,
# because having the wrong indentation levels breaks the syntax.
PROXY_LISTING_TEMPLATE = Template(
    """<html>
            <head>
                <title>Available services</title>
            </head>
            <body>
            {% for (config_id, project_id), proxy_hosts in sections.items() %}
                <section>
                    <h2>{{ config_id }} {{ project_id }}</h2>
                    <ul>
                    {% for host in proxy_hosts %}
                        <li>
                            <a href="http://{{ host.hostname }}">{{ host.hostname }}</a>
                            <span>({{ host.port }})</span>
                        </li>
                    {% endfor %}
                    </ul>
                </section>
            {% endfor %}
            </body>
        </html>
    """,
)


def get_proxy_listing_html(hosts: list[ProxyHost]) -> str:
    sections: dict[tuple[str, str], list[ProxyHost]] = defaultdict(list)
    for host in hosts:
        sections[(host.config_id, host.project_id)].append(host)

    return PROXY_LISTING_TEMPLATE.render(sections=sections)


def get_proxy_listing_config(hosts: list[ProxyHost]) -> str:
    return strip_indented_string(f"""
    localhost:80 {{
        header Content-Type text/html
        respond <<HTML
        {get_proxy_listing_html(hosts).strip()}
        HTML 200
    }}
    """).strip()
