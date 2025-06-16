#!/bin/bash
# ==========================================
# KONGCHAT DEVELOPMENT ENVIRONMENT INSTALLER
# UPDATED: 2024-06-15 | v2.1.0
# ==========================================

# Global Variables
LOG_FILE="/tmp/install_kongchat.log"
BACKUP_DIR="$HOME/kongchat_backup_$(date +%s)"
SUPPORTED_OS=("Ubuntu 22.04" "Debian 11")

# ASCII Art
print_banner() {
  cat << "EOF"

  ██╗  ██╗ ██████╗ ███╗   ██╗ ██████╗  ██████╗ ██╗  ██╗╔█████╗ ███████║
  ██║ ██╔╝██╔═══██╗████╗  ██║██╔════╝ ██╔   ██║██║  ██║██║  ██║   ██║
  █████╔╝ ██║   ██║██╔██╗ ██║██║  ███╗██║      ███████║███████║   ██║
  ██╔═██╗ ██║   ██║██║╚██╗██║██║   ██║██║   ██║██╔══██║██╔══██║   ██║
  ██║  ██╗╚██████╔╝██║ ╚████║╚██████╔╝╚██████╔╝██║  ██║██║  ██║   ██║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝
  ============ DEVELOPMENT SUITE v2 =============
EOF
}

# Initial Checks
preflight_check() {
  echo "[+] Running pre-flight checks"
  
  # OS Compatibility
  current_os=$(lsb_release -d | awk -F"\t" '{print \$2}')
  supported=false
  for os in "${SUPPORTED_OS[@]}"; do
    if [[ "$current_os" == *"$os"* ]]; then
      supported=true
      break
    fi
  done
  
  if ! $supported; then
    echo -e "\n[!] ERROR: Unsupported OS: $current_os"
    echo "Supported versions:"
    printf ' - %s\n' "${SUPPORTED_OS[@]}"
    exit 1
  fi

  # Sudo Validation
  if [ "$EUID" -ne 0 ]; then
    echo -e "\n[!] Please run as root"
    exit 1
  fi
  
  # Internet Connection
  if ! ping -c 1 google.com &> /dev/null; then
    echo "[!] No internet connection"
    exit 1
  fi
}

# Backup Existing Configs
create_backup() {
  echo "[+] Creating backup at $BACKUP_DIR"
  mkdir -p "$BACKUP_DIR"
  
  important_files=(
    "/etc/nginx"
    "/etc/mysql"
    "/etc/redis"
    "$HOME/.bashrc"
    "$HOME/.zshrc"
    "$HOME/.config"
  )
  
  for item in "${important_files[@]}"; do
    if [ -e "$item" ]; then
      cp -rv "$item" "$BACKUP_DIR" >> "$LOG_FILE" 2>&1
    fi
  done
}

# Core System Setup
setup_system() {
  echo "[+] Updating system packages"
  apt update -y >> "$LOG_FILE" 2>&1
  apt upgrade -y >> "$LOG_FILE" 2>&1
  
  echo "[+] Installing core dependencies"
  apt install -y \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    curl \
    wget \
    git \
    gnupg2 \
    software-properties-common >> "$LOG_FILE" 2>&1
}

# Database Stack
install_databases() {
  echo "[+] Installing database stack"
  
  # PostgreSQL
  apt install -y postgresql postgresql-contrib >> "$LOG_FILE" 2>&1
  systemctl start postgresql >> "$LOG_FILE" 2>&1
  sudo -u postgres psql -c "CREATE DATABASE kongchat_dev;" >> "$LOG_FILE" 2>&1
  
  # Redis
  apt install -y redis-server >> "$LOG_FILE" 2>&1
  sed -i 's/supervised no/supervised systemd/' /etc/redis/redis.conf
  systemctl restart redis >> "$LOG_FILE" 2>&1
}

# Runtime Environments
install_runtimes() {
  echo "[+] Installing language runtimes"
  
  # Node.js (via NVM)
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash >> "$LOG_FILE" 2>&1
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  nvm install 20 >> "$LOG_FILE" 2>&1
  nvm use 20 >> "$LOG_FILE" 2>&1
  
  # Python (via Pyenv)
  git clone https://github.com/pyenv/pyenv.git ~/.pyenv >> "$LOG_FILE" 2>&1
  echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
  echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
  echo 'eval "$(pyenv init -)"' >> ~/.bashrc
  source ~/.bashrc
  pyenv install 3.12 >> "$LOG_FILE" 2>&1
  pyenv global 3.12 >> "$LOG_FILE" 2>&1
  
  # Java
  apt install -y openjdk-17-jdk >> "$LOG_FILE" 2>&1
}

# Containerization
install_container_tools() {
  echo "[+] Installing container tools"
  
  # Docker
  curl -fsSL https://get.docker.com | sh >> "$LOG_FILE" 2>&1
  usermod -aG docker $USER >> "$LOG_FILE" 2>&1
  
  # Docker Compose
  LATEST_COMPOSE=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
  curl -L "https://github.com/docker/compose/releases/download/${LATEST_COMPOSE}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose >> "$LOG_FILE" 2>&1
  chmod +x /usr/local/bin/docker-compose >> "$LOG_FILE" 2>&1
}

# Monitoring Tools
install_monitoring() {
  echo "[+] Installing monitoring"
  
  # Prometheus Stack
  docker run -d \
    -p 9090:9090 \
    -v /etc/prometheus:/etc/prometheus \
    --name prometheus \
    prom/prometheus >> "$LOG_FILE" 2>&1
    
  # Grafana
  docker run -d \
    -p 3000:3000 \
    --name=grafana \
    grafana/grafana-enterprise >> "$LOG_FILE" 2>&1
}

# Main Installation Flow
main() {
  clear
  print_banner
  echo "Starting installation... | Log: $LOG_FILE"
  
  # Execution Pipeline
  STEPS=(
    preflight_check
    create_backup
    setup_system
    install_databases
    install_runtimes
    install_container_tools
    install_monitoring
  )
  
  for step in "${STEPS[@]}"; do
    echo -e "\n[=== RUNNING: $step ===]"
    if $step; then
      echo "[OK] Completed successfully"
    else
      echo -e "\n[!] FAILED at step: $step"
      echo "Check log file: $LOG_FILE"
      exit 1
    fi
  done
  
  # Post-install Report
  echo -e "\n[SUCCESS] KongChat environment installed!"
  cat << EOF

  ██╗  ██╗ ██████╗ ███╗   ██╗ ██████╗  ██████╗ ██╗  ██╗╔█████╗ ███████║
  ██║ ██╔╝██╔═══██╗████╗  ██║██╔════╝ ██╔   ██║██║  ██║██║  ██║   ██║
  █████╔╝ ██║   ██║██╔██╗ ██║██║  ███╗██║      ███████║███████║   ██║
  ██╔═██╗ ██║   ██║██║╚██╗██║██║   ██║██║   ██║██╔══██║██╔══██║   ██║
  ██║  ██╗╚██████╔╝██║ ╚████║╚██████╔╝╚██████╔╝██║  ██║██║  ██║   ██║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝

  === INSTALLATION COMPLETE ===
  Access services:
  - PostgreSQL: psql -U postgres -d kongchat_dev
  - Redis:     redis-cli
  - Node.js:   node -v (v20+)
  - Python:    python --version (3.12)
  - Docker:    docker ps
  - Monitoring:
      Prometheus: http://localhost:9090
      Grafana:    http://localhost:3000 (admin/admin)

  Backup available at: $BACKUP_DIR
  Full log: $LOG_FILE
EOF
}

# Execute main function
main
