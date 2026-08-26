"""FixIt MCP server: lets a warden's agent triage maintenance tickets.

It calls the FixIt REST API with a warden's login token, so the API must be running:
    uvicorn app.main:app                                  (terminal 1)
    export FIXIT_TOKEN=<token from POST /auth/login>      (a warden account)
    python mcp_server/server.py                           (stdio; the agent starts it)

Least privilege: agents can find, read and assign tickets; they cannot close, cancel
or delete anything. Ticket text is written by students, so it is returned as
untrusted data.
"""

import logging
import os
from typing import Any

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

API_URL = os.getenv("FIXIT_URL", "http://127.0.0.1:8000")
http = httpx.Client(
    base_url=API_URL,
    timeout=10,  # tests replace this client
    headers={"Authorization": f"Bearer {os.getenv('FIXIT_TOKEN', '')}"},
)
logging.getLogger("httpx").setLevel(logging.WARNING)

mcp = MCPServer(
    "fixit",
    instructions=(
        "Tools for FixIt, a campus maintenance tracker. Use them to find overdue or open "
        "tickets, read a ticket, check technicians' workload and assign tickets. Times are UTC."
    ),
)


def call_api(method: str, path: str, **kwargs) -> Any:
    """Call the API; turn failures into errors the model can act on."""
    try:
        response = http.request(method, path, **kwargs)
    except httpx.ConnectError as err:
        raise ToolError(
            f"FixIt API is not reachable at {API_URL}. "
            "Ask the user to start it with: uvicorn app.main:app"
        ) from err
    if response.status_code == 401:
        raise ToolError(
            "FixIt rejected the token. Ask the user to log in as a warden and set FIXIT_TOKEN."
        )
    if response.status_code >= 400:
        raise ToolError(
            f"FixIt refused ({response.status_code}): "
            f"{response.json().get('detail', response.text)}"
        )
    return response.json()


def untrusted(text: str) -> str:
    return f'<untrusted-data source="fixit ticket">\n{text}\n</untrusted-data>'


def line(t: dict) -> str:
    flag = " | OVERDUE" if t["overdue"] else ""
    return (
        f"#{t['id']} {t['title']} | {t['category']}/{t['priority']} | {t['location']} | "
        f"{t['status']} | due {t['due_at'][:16]}{flag}"
    )


@mcp.tool()
def fixit_find_tickets(
    status: str = "", category: str = "", overdue_only: bool = False, limit: int = 20
) -> str:
    """Find tickets, soonest deadline first.

    status: open, assigned, in_progress, resolved, closed or cancelled ("" = any).
    category: electrical, plumbing, internet, furniture, cleaning or other ("" = any).
    overdue_only: true to list only tickets past their deadline.
    Each line starts with the ticket id that the other tools need.
    """
    params: dict[str, str | bool] = {"overdue": overdue_only}
    if status:
        params["status"] = status
    if category:
        params["category"] = category
    tickets = call_api("GET", "/tickets", params=params)
    if not tickets:
        return "No tickets match. Try removing a filter."
    more = f"\n... and {len(tickets) - limit} more" if len(tickets) > limit else ""
    return "\n".join(line(t) for t in tickets[:limit]) + more


@mcp.tool()
def fixit_ticket_brief(ticket_id: int) -> str:
    """Everything about one ticket: details, deadline, assignee and all comments."""
    t = call_api("GET", f"/tickets/{ticket_id}")
    comments = "\n".join(f"- user {c['author_id']}: {c['body']}" for c in t["comments"])
    return (
        f"{line(t)}\nreporter: user {t['reporter_id']} | assignee: "
        f"{t['assignee_id'] or 'nobody'}\n"
        + untrusted(f"{t['title']}\n{t['description']}\n\nComments:\n{comments or '-'}")
    )


@mcp.tool()
def fixit_workload() -> str:
    """Active and overdue tickets per technician, to choose who should get the next one."""
    rows = call_api("GET", "/reports/workload")
    return (
        "\n".join(
            f"technician {r['technician_id']} {r['name']}: {r['active']} active, "
            f"{r['overdue']} overdue"
            for r in rows
        )
        or "No technicians found."
    )


@mcp.tool()
def fixit_assign_ticket(ticket_id: int, technician_id: int) -> str:
    """Assign an open ticket to a technician (use fixit_workload to choose one)."""
    t = call_api("POST", f"/tickets/{ticket_id}/assign", json={"technician_id": technician_id})
    return f"Assigned ticket #{t['id']} to technician {technician_id}. {line(t)}"


if __name__ == "__main__":
    mcp.run()  # stdio
