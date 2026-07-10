#!/bin/bash
# Скрипт для упаковки InstallKits как standalone приложения для Linux

# Создаем директорию для приложения
APP_DIR="InstallKits_linux"
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/data"

# Копируем основные файлы
cp main.py "$APP_DIR/"
cp settings.json "$APP_DIR/"
cp -r data/db.json "$APP_DIR/data/"

# Копируем все модули
cp -r ui "$APP_DIR/"
cp -r data/*.py "$APP_DIR/data/"

# Создаем стартовый скрипт
cat > "$APP_DIR/run.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 main.py
EOF

chmod +x "$APP_DIR/run.sh"

# Создаем архив
tar -czvf InstallKits_linux.tar.gz "$APP_DIR"

echo "Архив создан: InstallKits_linux.tar.gz"
echo "Размер: $(du -h InstallKits_linux.tar.gz | cut -f1)"
