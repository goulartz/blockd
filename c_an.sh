#!/bin/sh

# Verificar se o parâmetro "rj" foi fornecido
if [ "$1" = "rj" ]; then
    /usr/local/bin/curl -s -k -LJo /usr/home/admin/bloqueio-rj-27.py https://github.com/goulartz/blockd/raw/main/bloqueio-rj-27.py
    /usr/local/bin/python2.7 /usr/home/admin/bloqueio-rj-27.py
else
    # Verificar a versão do sistema operacional
    if uname -a | grep -q "13."; then
        /usr/local/bin/curl -s -k -LJo /usr/home/admin/anablock.py https://github.com/goulartz/blockd/raw/main/anablock.py
        /usr/local/bin/python3.8 /usr/home/admin/anablock.py
    else
        /usr/local/bin/curl -s -k -LJo /usr/home/admin/anablock27.py https://github.com/goulartz/blockd/raw/main/anablock27.py
        /usr/local/bin/python2.7 /usr/home/admin/anablock27.py
    fi
fi
