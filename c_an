#!/bin/sh

# Verificar a versão do sistema operacional
if uname -a | grep -q "13."; then
    curl -s -LJO https://github.com/goulartz/anablock_technodns/raw/main/anablock.py | python3.8 anablock.py
else
    curl -s -LJO https://github.com/goulartz/anablock_technodns/raw/main/anablock27.py | python2.7 anablock27.py
fi

