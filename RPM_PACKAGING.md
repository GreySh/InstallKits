# Инструкция по созданию .rpm пакета для InstallKits

## Предварительные требования

Для создания .rpm пакета вам понадобится система на базе RHEL/CentOS/Fedora (или RedOS).

## Шаг 1: Установите необходимые инструменты

```bash
# Установите PyInstaller и зависимости
pip install pyinstaller customtkinter tinydb openpyxl

# Установите инструменты для сборки RPM пакетов
sudo dnf install rpm-build rpmdevtools redhat-rpm-config
```

## Шаг 2: Подготовьте структуру сборки

```bash
# Создайте структуру директорий для RPM сборки
mkdir -p ~/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

# Установите переменную окружения
export TOPDIR=$HOME/rpmbuild
```

## Шаг 3: Соберите исполняемый файл

```bash
# Перейдите в папку с проектом
cd /path/to/InstallKits

# Соберите .exe файл
pyinstaller --onefile --windowed --name InstallKits main.py

# Файл будет в папке dist/
```

## Шаг 4: Создайте SPEC файл

Создайте файл `InstallKits.spec` в папке `SPECS`:

```bash
mkdir -p ~/rpmbuild/SPECS
nano ~/rpmbuild/SPECS/InstallKits.spec
```

Содержимое `InstallKits.spec`:

```spec
Name:           installkits
Version:        0.1.0
Release:        1%{?dist}
Summary:        InstallKits - Application for managing installation kits

License:        MIT
URL:            https://github.com/yourusername/InstallKits
Source0:        %{name}-%{version}.tar.gz
BuildArch:      x86_64

BuildRequires:  python3-devel
Requires:       python3
Requires:       python3-tkinter
Requires:       python3-customtkinter
Requires:       python3-tinydb
Requires:       python3-openpyxl

%description
InstallKits - Application for managing installation kits consisting of discs and boxes.

%prep
%setup -q

%build
# Пробuild stage (если нужна компиляция)

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/%{name}/data

cp -r * %{buildroot}%{_datadir}/%{name}/

# Создайте launcher скрипт
cat > %{buildroot}%{_bindir}/%{name} << 'LAUNCHER'
#!/bin/bash
cd %{_datadir}/%{name}
python3 main.py
LAUNCHER

chmod +x %{buildroot}%{_bindir}/%{name}

%files
%{_bindir}/%{name}
%{_datadir}/%{name}/
%doc %{_datadir}/%{name}/README.md

%changelog
* Wed Jul 09 2026 GreySh <sergei_shchitov@mail.ru> - 0.1.0-1
- Initial package
```

## Шаг 5: Создайте архив с исходниками

```bash
# Создайте архив с приложением (включая settings.json и db.json)
tar -czvf ~/rpmbuild/SOURCES/InstallKits-0.1.0.tar.gz \
    --exclude='__pycache__' \
    --exclude='.venv' \
    --exclude='*.spec' \
    --exclude='build' \
    --exclude='dist' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    main.py settings.json data/ ui/

# Скопируйте архив в SOURCES
cp ~/rpmbuild/SOURCES/InstallKits-0.1.0.tar.gz ~/rpmbuild/SOURCES/
```

## Шаг 6: Соберите RPM пакет

```bash
# Соберите пакет
rpmbuild -ba ~/rpmbuild/SPECS/InstallKits.spec

# Готовый пакет будет в:
# ~/rpmbuild/RPMS/x86_64/InstallKits-0.1.0-1.x86_64.rpm
```

## Шаг 7: Установка и тестирование

```bash
# Установите пакет
sudo dnf install ~/rpmbuild/RPMS/x86_64/InstallKits-0.1.0-1.x86_64.rpm

# Запустите приложение
installkits

# Или
/usr/bin/installkits
```

## Альтернативный метод: Использование PyInstaller напрямую (проще)

Если вам не нужен полноценный .rpm пакет, а просто standalone приложение:

### Создайте скрипт запуска

Создайте файл `installkits.sh`:

```bash
#!/bin/bash
# InstallKits launcher for Linux

# Получите путь к скрипту
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Запустите приложение
cd "$SCRIPT_DIR"
python3 main.py
```

### Упаковка для распространения

```bash
# Создайте архив с приложением
tar -czvf InstallKits_linux.tar.gz \
    main.py \
    settings.json \
    data/ \
    ui/ \
    installkits.sh

# Или создайте self-contained версию
pyinstaller --onefile --windowed --name InstallKits main.py

# Скопируйте settings.json в папку с .exe
cp settings.json dist/

# Упакуйте всё вместе
tar -czvf InstallKits_linux.tar.gz dist/
```

### Установка на RedOS

```bash
# Распакуйте архив
tar -xzvf InstallKits_linux.tar.gz

# Сделайте скрипт исполняемым
chmod +x installkits.sh

# Запустите
./installkits.sh

# Или запустите .exe файл
chmod +x dist/InstallKits
./dist/InstallKits
```

## Примечания

1. **Зависимости:** Убедитесь, что установлены все зависимости:
   ```bash
   sudo dnf install python3 python3-tkinter python3-pip
   pip3 install customtkinter tinydb openpyxl
   ```

2. **GUI на Linux:** CustomTkinter использует Tcl/Tk, убедитесь что он установлен:
   ```bash
   sudo dnf install tk tk-devel
   ```

3. **Сетевые пути:** Если используется сетевой путь к базе данных, убедитесь что он доступен:
   ```bash
   # Проверьте доступность сервера
   ping yyyserver.red-soft.ru
   ```

## Troubleshooting

### Ошибка: "No module named _tkinter"
```bash
sudo dnf install python3-tkinter
```

### Ошибка: "No display name and no $DISPLAY environment variable"
Запустите с X11 forwarding или используйте VNC:
```bash
ssh -X user@hostname
```

### Ошибка: "Can't find a default font"
```bash
sudo dnf install fontconfig
fc-cache -fv
```
