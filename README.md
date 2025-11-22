# TON_mining_BOT

Bot de Telegram diseñado para simular minería de TON, gestionar usuarios, recompensas, tareas y sistema de referidos. Implementado en Python y desplegado en Render.

## 🚀 Características
- Sistema de minería automática simulada
- Recompensas por tiempo de actividad
- Sistema de referidos con bonificaciones
- Panel para administrador
- Comandos personalizados
- Envío de notificaciones automáticas

## 📦 Tecnologías utilizadas
- Python 3.11
- Librería `pyTelegramBotAPI` (telebot)
- Render (Deploy en web service)
- GitHub (Control de versiones)

## 🔧 Instalación local:
- Pedir repositorio.
# Añadir .env al .gitignore
echo ".env" >> .gitignore

# eliminar .env del historial de Git
git rm --cached .env

# reescribir todo el historial y borrar rastros
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# hacer commit
git commit -m "Eliminar .env del repositorio y del historial"

# subir los cambios a GitHub (forzando actualización del historial)
git push origin --force
