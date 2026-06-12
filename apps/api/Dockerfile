FROM python:3.12-slim

# packages/shared 상대 경로 의존을 위해 모노레포 구조를 유지한다
WORKDIR /workspace

COPY apps/api/pyproject.toml apps/api/alembic.ini ./apps/api/
COPY apps/api/app ./apps/api/app
COPY apps/api/alembic ./apps/api/alembic
COPY apps/api/scripts ./apps/api/scripts
COPY packages/shared ./packages/shared

WORKDIR /workspace/apps/api
RUN pip install --no-cache-dir -e .

COPY apps/api/docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
