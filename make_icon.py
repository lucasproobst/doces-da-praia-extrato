# -*- coding: utf-8 -*-
"""
Gera o ícone do aplicativo (assets/icon.ico).

O ícone é um "doce de praia" estilizado: um pirulito sobre um fundo turquesa
(o mar) com areia embaixo. Rode uma vez antes de compilar:

    python make_icon.py

Requer Pillow (já incluído no requirements.txt).
"""

import math
import os

from PIL import Image, ImageDraw


def _arredondar(draw, caixa, raio, cor):
    draw.rounded_rectangle(caixa, radius=raio, fill=cor)


def gerar_icone(caminho="assets/icon.ico", tamanho=256):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    # Trabalhamos em alta resolução e reduzimos no final (bordas mais suaves).
    escala = 4
    lado = tamanho * escala
    img = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    margem = int(lado * 0.06)
    raio = int(lado * 0.22)

    # Fundo turquesa (o mar)
    _arredondar(d, [margem, margem, lado - margem, lado - margem], raio, (14, 165, 164, 255))

    # Faixa de areia na parte de baixo
    areia = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    da = ImageDraw.Draw(areia)
    da.rectangle([0, int(lado * 0.72), lado, lado], fill=(253, 224, 178, 255))
    mascara = Image.new("L", (lado, lado), 0)
    dm = ImageDraw.Draw(mascara)
    dm.rounded_rectangle([margem, margem, lado - margem, lado - margem], radius=raio, fill=255)
    img.paste(areia, (0, 0), Image.composite(areia.split()[3], Image.new("L", (lado, lado), 0), mascara))

    # Palito do pirulito
    centro_x = lado // 2
    topo_y = int(lado * 0.26)
    raio_doce = int(lado * 0.20)
    base_palito = int(lado * 0.80)
    d.line(
        [centro_x, topo_y + raio_doce, centro_x, base_palito],
        fill=(255, 255, 255, 255),
        width=int(lado * 0.05),
    )

    # Cabeça do pirulito (círculo coral)
    d.ellipse(
        [centro_x - raio_doce, topo_y - raio_doce + raio_doce,
         centro_x + raio_doce, topo_y + raio_doce + raio_doce],
        fill=(251, 113, 133, 255),
    )

    # Espiral branca do doce
    centro_y = topo_y + raio_doce
    pontos = []
    voltas = 3.0
    passos = 240
    for i in range(passos):
        t = i / passos
        ang = t * voltas * 2 * math.pi
        r = t * (raio_doce * 0.82)
        pontos.append((centro_x + r * math.cos(ang), centro_y + r * math.sin(ang)))
    d.line(pontos, fill=(255, 255, 255, 230), width=int(lado * 0.022), joint="curve")

    # Reduz para o tamanho final e salva em vários tamanhos dentro do .ico
    img = img.resize((tamanho, tamanho), Image.LANCZOS)
    tamanhos = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(caminho, format="ICO", sizes=tamanhos)
    print(f"Ícone gerado em: {caminho}")


if __name__ == "__main__":
    gerar_icone()
