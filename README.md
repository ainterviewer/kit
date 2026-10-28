# AInterviewer self-host kit

Run your own [AInterviewer](https://ainterviewer.dk) on a single Linux machine
with Docker. It is meant for researchers and reviewers who want to try the
platform without depending on the hosted instance.

The stack is three containers:

| Service    | Image                            | Role                                      |
| ---------- | -------------------------------- | ----------------------------------------- |
| `caddy`    | `caddy`                          | HTTPS, and routing `/api` and `/ws` to the backend |
| `frontend` | `ghcr.io/ainterviewer/frontend`  | The web app ([source](https://github.com/ainterviewer/frontend)) |
| `backend`  | `ghcr.io/ainterviewer/backend`   | API and interview engine ([source](https://github.com/ainterviewer/backend)) |

Data is kept in a SQLite database under `./storage`.

## Requirements

- A Linux machine with Docker Engine and the Compose plugin. 2 vCPU and 4 GB RAM
  is plenty, because the language models run at the provider and not on the machine.
- An API key for at least one model provider. [OpenRouter](https://openrouter.ai)
  is the simplest, since one key covers many models.
- For a public install, a domain whose DNS points at the machine, with ports 80
  and 443 open. You don't need one to try it out on `localhost`.

## Quick start

```bash
git clone https://github.com/ainterviewer/kit.git ainterviewer
cd ainterviewer

cp .env.example .env
cp config.example.toml config.toml
```

Edit `.env`:

1. Set `DOMAIN` (keep `localhost` for a local trial).
2. Set `CONTACT_EMAIL`. Interview participants are shown it as the address
   for questions about their interview.
3. Fill both `APP_SECRET__*` keys with the output of `openssl rand -hex 32`.
4. Add your `OPENROUTER_API_KEY`.

Then start the stack and create the first admin account. The backend creates
the database on first start.

```bash
docker compose up -d
docker compose exec backend python /opt/kit/create_admin.py you@example.org YourName
```

Open `https://<DOMAIN>` and log in. As an admin you can invite further users
from the dashboard.

## Configuration

- **`.env`**: secrets and the domain. `.env.example` documents every variable.
- **`config.toml`**: everything else: available models, registration, email,
  speech. `config.example.toml` documents the common settings. Any setting can
  also be given as an environment variable in `.env`, with `__` between section
  and key, e.g. `APP__REGISTRATION_REQUIRES_TOKEN=false`.

Apply changes with `docker compose up -d --force-recreate backend`.

### Email

Without email, the platform runs fine for accounts created with
`create_admin.py`, but self sign-up, password resets, two-factor codes and
emailing participants are unavailable. To enable them, fill in
`[services.email]` in `config.toml` and the matching passwords in `.env`.

### Guide assistant

The dashboard's assistant helps write interview guides. It uses the model in
`[services.assistance]` (`openrouter:` or `openai:` models with tool calling),
OpenRouter's `gpt-oss-120b` in the example config.

### Speech

Spoken interviews use OpenAI's speech models. To enable them, uncomment
`[services.speech]` in `config.toml` and set `OPENAI_API_KEY`.

## Upgrading

Set `BACKEND_VERSION` and `FRONTEND_VERSION` in `.env` to a newer
[backend](https://github.com/ainterviewer/backend/releases) and
[frontend](https://github.com/ainterviewer/frontend/releases) release, then:

```bash
docker compose pull && docker compose up -d
```

The backend applies database migrations on start. Back up first (see below).

## Backups

Everything that matters is in `./storage`, together with your `.env` and
`config.toml`. To take a consistent copy of the database while it runs:

```bash
docker compose exec backend python -c \
  "import sqlite3; sqlite3.connect('storage/db.sqlite').backup(sqlite3.connect('storage/backup.sqlite'))"
```

## Citation

If you use AInterviewer in your research, please cite:

> Gårdhus, T., Vitsakis, N., Frederiksen, F. L., Rogers, A., & Carlsen, H. B. (2026).
> AInterviewer: A Platform for Designing and Conducting AI-led Qualitative Interviews.
> _Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics
> (Volume 3: System Demonstrations)_, 119–127. https://doi.org/10.18653/v1/2026.acl-demo.12

<details>
<summary>BibTeX</summary>

```bibtex
@inproceedings{gardhus-etal-2026-ainterviewer,
    title = "{AI}nterviewer: A Platform for Designing and Conducting {AI}-led Qualitative Interviews",
    author = "G{\r{a}}rdhus, Tobias and Vitsakis, Nikolas and Frederiksen, Fie Lejre and Rogers, Anna and Carlsen, Hjalmar Bang",
    booktitle = "Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations)",
    month = jul,
    year = "2026",
    address = "San Diego, California, United States",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2026.acl-demo.12/",
    doi = "10.18653/v1/2026.acl-demo.12",
    pages = "119--127",
    ISBN = "979-8-89176-392-0"
}
```

</details>

### Paper versions

The component versions each publication describes. The full release history is
on the [documentation site](https://docs.ainterviewer.dk/releases/).

| Publication                                                                         | Venue                 | Platform release | lib                                                           | backend                                                           | frontend                                                           |
| ----------------------------------------------------------------------------------- | --------------------- | ---------------- | ------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------ |
| AInterviewer: A Platform for Designing and Conducting AI-led Qualitative Interviews | ACL 2026 Systems Demo | `2026.07.3` †    | [`v0.2.16`](https://github.com/ainterviewer/lib/tree/v0.2.16) | [`v0.4.10`](https://github.com/ainterviewer/backend/tree/v0.4.10) | [`v0.2.56`](https://github.com/ainterviewer/frontend/tree/v0.2.56) |

† Predates this kit: those versions are listed to show which code the paper
describes, and cannot be run with it. To try the platform, use the kit as it
stands.

## License

[AGPL-3.0](LICENSE)
