# Binwalk — análise e extração de firmware

## O que é

Binwalk é uma ferramenta de análise de imagens binárias, focada principalmente em firmware, mas aplicável a qualquer blob binário. Ela varre um arquivo em busca de arquivos, sistemas de arquivos e código embutido — identificando, por assinatura, coisas como sistemas de arquivos comprimidos (SquashFS, CramFS, JFFS2, UBIFS), dados comprimidos (gzip, LZMA, zlib, XZ), cabeçalhos de bootloader (U-Boot/uImage), kernels Linux, imagens de dispositivo (device tree blobs) e muito mais, tudo embutido dentro de uma única imagem de firmware.

A varredura é baseada em assinaturas, usando a mesma lógica da biblioteca `libmagic` (a que dá suporte ao comando `file` do Linux), complementada por um conjunto próprio de assinaturas afinadas especificamente para o que costuma aparecer em firmware de dispositivos embarcados e IoT.

### Duas versões no Kali

O Kali Linux disponibiliza dois pacotes:

- **`binwalk`** — a versão clássica, escrita em Python, hoje mantida majoritariamente como biblioteca de assinaturas de apoio.
- **`binwalk3`** — reescrita mais recente em Rust, focada em velocidade e precisão, e que hoje é o binário efetivamente usado ao rodar a ferramenta no Kali atual.

A sintaxe das opções mais usadas (`-e`, `-M`, `-E`) permanece praticamente a mesma entre as duas versões, o que mantém a maior parte dos tutoriais e exemplos antigos ainda válida. Este arquivo cobre o `binwalk3`, indicando pontuais diferenças quando relevante.

## Instalação

```bash
sudo apt install binwalk3
```

Já vem pré-instalado no Kali Linux.

## Nível básico

### Sintaxe geral

```
binwalk3 [opções] arquivo
```

### Scan de assinaturas (comportamento padrão)

```bash
binwalk3 firmware.bin
```

Sem nenhuma flag adicional, o binwalk3 varre o arquivo por assinaturas conhecidas e lista cada uma com seu deslocamento (offset) dentro do arquivo. Uma saída típica se parece com:

```
DECIMAL     HEXADECIMAL   DESCRIPTION
--------------------------------------------------------------------------------
0           0x0           uImage header, OS: Linux, CPU: ARM, compression: none
92          0x5C          Linux kernel ARM boot executable zImage
2460        0x99C         Device tree image (dtb)
3145756     0x30001C      Squashfs filesystem, little endian, version 4.0
```

Cada linha indica onde, dentro do binário, começa algo reconhecível — informação essencial antes de decidir como extrair ou analisar cada parte.

### Extração automática

```bash
binwalk3 -e firmware.bin
```

`-e` extrai automaticamente os arquivos e sistemas de arquivo identificados na varredura, salvando o resultado (por padrão) em uma pasta `extractions` no diretório atual.

## Nível intermediário

### Extração recursiva (Matryoshka)

```bash
binwalk3 -Me firmware.bin
```

`-M` (Matryoshka, em referência às bonecas russas que se encaixam umas dentro das outras) faz o binwalk3 escanear recursivamente também os arquivos que acabou de extrair — bastante comum em firmware real, onde um cabeçalho contém um kernel comprimido, que contém um sistema de arquivos, que por sua vez contém dezenas de arquivos de configuração e binários individuais.

### Diretório de extração customizado

```bash
binwalk3 -e -C saida_firmware/ firmware.bin
```

`-C` define um diretório de destino próprio para a extração, em vez do padrão `extractions` — útil para organizar análises de múltiplas imagens de firmware em pastas separadas.

### Análise de entropia

```bash
binwalk3 -E firmware.bin
```

A análise de entropia mede o nível de aleatoriedade dos dados ao longo do arquivo e gera um gráfico. Regiões com entropia próxima do máximo geralmente indicam dados comprimidos ou criptografados — o que é especialmente útil quando o scan de assinaturas não encontra nada reconhecível em determinado trecho: a entropia revela que ali existe algo "denso" (possivelmente cifrado ou usando uma compressão proprietária), mesmo sem conseguir identificar exatamente o quê.

### Varredura exaustiva

```bash
binwalk3 -a firmware.bin
```

`-a` (search-all) força a checagem de todas as assinaturas conhecidas em todos os offsets possíveis, em vez da varredura otimizada padrão — significativamente mais lenta, mas útil quando se suspeita que o scan padrão deixou passar algo por causa de um alinhamento incomum dos dados.

### Filtrando assinaturas

```bash
binwalk3 -x squashfs firmware.bin    # exclui um tipo específico do scan
binwalk3 -y elf firmware.bin         # restringe o scan a apenas um tipo
```

`-x` remove tipos específicos do escopo da varredura (útil para reduzir ruído de resultados muito comuns, mas pouco relevantes para a análise atual). `-y` faz o inverso: restringe a varredura só ao(s) tipo(s) informado(s), útil quando já se sabe exatamente o que está procurando.

## Nível avançado

### Listando assinaturas e extratores suportados

```bash
binwalk3 -L
```

`-L` lista todas as assinaturas e extratores que a instalação atual do binwalk3 é capaz de reconhecer e processar — boa referência na hora de decidir o que incluir ou excluir com `-x`/`-y`.

### Log estruturado em JSON

```bash
binwalk3 -l resultado.json firmware.bin
```

`-l` exporta os resultados da varredura em formato JSON estruturado, em vez de (ou além de) exibir a tabela no terminal — útil para alimentar outras ferramentas ou scripts como parte de um pipeline automatizado de análise de firmware.

### Controle de threads

```bash
binwalk3 -t 8 firmware.bin
```

`-t` define manualmente o número de threads usadas na varredura — relevante para ajustar desempenho em imagens de firmware muito grandes ou em hardware com recursos limitados.

### Verbosidade em extrações recursivas

```bash
binwalk3 -E -v firmware.bin
```

`-v`, combinado com extração recursiva, exibe todos os resultados encontrados durante o processo, em vez de um resumo filtrado — útil em investigações manuais mais profundas sobre um firmware grande ou incomum.

### Extração manual (carving com dd)

Quando um sistema de arquivos identificado pelo scan não é extraído automaticamente (formato não suportado, corrompido, ou incomum o suficiente para o extrator padrão falhar), é possível isolar manualmente aquele trecho usando o offset e tamanho reportados pelo binwalk3, com uma ferramenta como `dd`:

```bash
dd if=firmware.bin of=squashfs_isolado.img bs=1 skip=3145756 count=1866000
```

Esse tipo de extração manual — chamada de "carving" — é um recurso importante para quando a extração automática não é suficiente, e o offset preciso reportado pelo binwalk já resolve metade do problema.

### Fluxo típico de análise de firmware

1. Varredura inicial de assinaturas, para ter uma visão geral do conteúdo (`binwalk3 firmware.bin`)
2. Extração recursiva automática dos arquivos e sistemas de arquivo identificados (`binwalk3 -Me firmware.bin`)
3. Inspeção manual do sistema de arquivos extraído — montar o SquashFS, procurar por arquivos de configuração, chaves privadas e credenciais hardcoded (essa parte já é trabalho de outras ferramentas, como `strings`, `grep` e um explorador de arquivos comum; o binwalk termina seu papel ao identificar e extrair)
4. Análise de entropia sobre qualquer trecho que a varredura de assinatura não conseguiu identificar, para descartar (ou confirmar) a presença de dados cifrados ou comprimidos com algoritmo proprietário

## Por que isso importa em segurança

Análise de firmware é uma etapa central em pesquisa de segurança de dispositivos IoT e embarcados: muitas vezes é a única forma prática de examinar o funcionamento interno de um dispositivo sem acesso físico a uma interface de debug (JTAG/UART). É comum encontrar, dentro de sistemas de arquivo extraídos dessa forma, credenciais fixas no código, chaves privadas SSH/TLS reaproveitadas entre milhares de dispositivos do mesmo modelo, ou scripts de inicialização que revelam serviços expostos e não documentados — todos achados típicos de pesquisas de segurança em firmware.

## Considerações éticas e legais

Analisar firmware de dispositivos próprios, ou no contexto de um teste de segurança autorizado, é uma prática legítima e amplamente aceita em pesquisa de segurança. Vale lembrar, porém, que a extração e engenharia reversa de firmware de terceiros pode esbarrar em termos de licença e restrições contratuais do fabricante, dependendo da legislação local e do contexto — algo a se considerar especialmente ao analisar firmware comercial fora do escopo de um pentest ou pesquisa autorizada.

## Referências

- Repositório oficial — ReFirmLabs/binwalk (versão clássica em Python)
- Binwalk Wiki — Quick Start Guide e Usage
- Kali Linux Tools — binwalk / binwalk3