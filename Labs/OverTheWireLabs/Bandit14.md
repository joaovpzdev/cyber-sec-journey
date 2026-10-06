# Bandit 14 → 15 — Serviço em porta TCP (texto puro)

## Objetivo

Enviar a senha do nível atual para um serviço que escuta numa porta TCP local e receber a senha do próximo nível.

## Conceitos

- **Porta TCP:** um "endereço" dentro da máquina onde um serviço aguarda conexões.
- **`localhost` / `127.0.0.1`:** a própria máquina.
- **Netcat (`nc`):** o "canivete suíço" das redes. Abre conexões TCP/UDP e envia ou recebe dados brutos.
- **Pipe (`|`):** encaminha a saída de um comando para a entrada de outro.

## Abordagem

1. Ler a senha atual, que fica no diretório de senhas do jogo.
2. Conectar no serviço e enviar a senha, de forma interativa:
   ```bash
   nc localhost <porta>
   ```
   ou numa linha só, com pipe:
   ```bash
   cat <arquivo_da_senha> | nc localhost <porta>
   ```
3. Encerrar a conexão com `Ctrl+C` quando necessário.

## A vulnerabilidade

**Transmissão de credenciais em texto puro (sem criptografia).**

Neste nível a comunicação é local, mas o protocolo usado **não protege os dados**. Numa rede real, qualquer pessoa posicionada no caminho (mesma rede Wi-Fi, switch comprometido, ARP spoofing) consegue ler a senha com um sniffer como o Wireshark ou o tcpdump.

## No mundo real

- Protocolos legados que trafegam credenciais em claro: **Telnet, FTP, HTTP, POP3, IMAP e SMTP sem TLS**.
- Serviços internos "porque é só rede interna", que viram alvo depois que um atacante entra na rede.

**CWE:** CWE-319 — Cleartext Transmission of Sensitive Information

## Como corrigir / detectar

- Substituir protocolos em claro pelas versões cifradas (SSH, SFTP, HTTPS, IMAPS…).
- Desabilitar serviços legados que não são necessários.
- Em monitoramento, alertar sobre tráfego de protocolos inseguros (por exemplo, regras de IDS para Telnet ou FTP).