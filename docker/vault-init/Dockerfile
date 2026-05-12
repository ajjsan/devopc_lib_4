# ЛР3: образ одноразовой инициализации Vault.
# На этапе сборки в образ попадают только скрипты (без секретов); сами значения
# передаются в контейнер переменными окружения при docker compose up.
FROM hashicorp/vault:1.15

COPY docker/vault-init/entrypoint.sh /usr/local/bin/vault-init-entrypoint.sh
# Windows CRLF в шебанге даёт "no such file or directory" в Linux — убираем \r при сборке.
RUN sed -i 's/\r$//' /usr/local/bin/vault-init-entrypoint.sh && chmod +x /usr/local/bin/vault-init-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/vault-init-entrypoint.sh"]
