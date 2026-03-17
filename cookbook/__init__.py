import pymysql
import os
import sys

# Проверяем, где мы работаем
ON_HOSTING = 'WEBSITE_HOSTNAME' in os.environ or 'DATABASE_URL' in os.environ

if ON_HOSTING:
    # Только на хостинге используем pymysql
    print("✅ pymysql настроен для хостинга")
    pymysql.version_info = (2, 2, 1, "final", 0)
    pymysql.install_as_MySQLdb()
else:
    print("💻 Локальная разработка - используем SQLite")