import os
import subprocess

APIURL_UNBOUND = "https://api.anablock.net.br/domains/all?output=unbound"
CONF_UNBOUND = "/usr/local/etc/unbound/anablock.conf"
CONF_UNBOUND_T = "/usr/local/etc/unbound/anablock_t.conf"
APIURL_VERSION = "https://api.anablock.net.br/api/version"
VERSION_F = "/usr/local/etc/unbound/version_api.conf"
CPU = subprocess.check_output(["technodns", "system", "threads"]).decode().strip()
MEMORY = subprocess.check_output(["technodns", "system", "memory", "--total"]).decode().strip()

status_output = subprocess.check_output(["unbound-control", "status"]).decode()

for line in status_output.split('\n'):
    if "is running" in line:
        pass
    else:
        print("Servidor com Broken Pipe.")
        exit(1)

def verificar_cpu():
    global CPU
    CPU = int(CPU)
    if CPU >= 16:
        CPU = 12

def processar_custom_v():
    global custom_v_string
    linhas_custom_v = []
    with open("/usr/local/etc/unbound/unbound.conf", 'r') as unbound_conf:
        flag = False
        for linha in unbound_conf:
            if "# Custom configuration" in linha:
                flag = True
                continue
            elif "# Parameters:" in linha:
                flag = False
            if flag:
                linha_sem_espacos = linha.strip()
                if linha_sem_espacos:
                    linha_com_substituicao = linha_sem_espacos.replace(" ", "+")
                    linhas_custom_v.append(linha_com_substituicao + "%0D%0A")

    if "include:+/usr/local/etc/unbound/anablock.conf%0D%0A" not in linhas_custom_v:
        linhas_custom_v.append("include:+/usr/local/etc/unbound/anablock.conf%0D%0A")

    custom_v_string = ''.join(linhas_custom_v)

processar_custom_v()
verificar_cpu()

VERSION = subprocess.check_output(["/usr/local/bin/curl", "-k", "-s", APIURL_VERSION]).decode().strip()
if os.path.isfile(VERSION_F) and os.path.getsize(VERSION_F) > 0:
    with open(VERSION_F, 'r') as f:
        if VERSION == f.read().strip():
            print("Tabela sem alterações.")
            exit(0)
else:
    with open(VERSION_F, 'w') as f:
        f.write(VERSION)

subprocess.run(["/usr/local/bin/curl", "-k", "-s", APIURL_UNBOUND, "-o", CONF_UNBOUND_T])
if os.path.isfile(CONF_UNBOUND_T) and os.path.getsize(CONF_UNBOUND_T) > 0:
    with open("/usr/local/etc/unbound/unbound.conf", 'r') as f:
        unbound_conf = f.read()
    with open(CONF_UNBOUND_T, 'r') as f:
        conf_unbound_t = f.read()
    with open("/tmp/unbound-test.conf", 'w') as f:
        f.write(unbound_conf + "server:\n" + conf_unbound_t)
    os.replace(CONF_UNBOUND_T, CONF_UNBOUND)
else:
    print("API não retornou dados.")
    exit(1)

CHECKFILE = "/usr/local/sbin/unbound-checkconf /tmp/unbound-test.conf"
result = subprocess.run(CHECKFILE, shell=True, stdout=subprocess.PIPE, text=True)
if "no errors" in result.stdout.lower():
    MEMORY = int(MEMORY)
    if MEMORY >= 1536:
        MEMORY -= 1024
    else:
        MEMORY //= 2
else:
    print("Arquivo de configuração Unbound contém erros.")
    exit(1)

MSG = MEMORY // 6
RRSET = MEMORY // 3

subprocess.run(["/usr/local/bin/curl", "-s", "-X", "POST", "http://localhost/dns/tuning/", "-H", "Content-Type: application/x-www-form-urlencoded", "--data-raw", f"num_threads={CPU}&msg_cache_size={MSG}m&rrset_cache_size={RRSET}m&prefetch=yes&minimal_responses=yes&qname_minimisation=yes&do_udp=yes&do_ip4=yes&do_ip6=yes&custom_config={custom_v_string}&action=save"], stdout=subprocess.DEVNULL)

try:
    subprocess.run(["/usr/local/bin/technodns/technodns", "recursive", "rewrite"], check=True, stdout=subprocess.DEVNULL)
except subprocess.CalledProcessError as e:
    print("Erro ao executar o comando:", e)

try:
    subprocess.run(["/usr/local/sbin/unbound-control", "reload"], check=True, stdout=subprocess.DEVNULL)
except subprocess.CalledProcessError as e:
    print("Erro ao executar o comando:", e)
