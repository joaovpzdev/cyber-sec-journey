# Troubleshooting — Conexão SSH fechada (rate limiting)

Anotações de um problema real enfrentado durante o OverTheWire Bandit: o servidor passou a **fechar as conexões SSH** sem pedir senha. Documentado aqui como referência de troubleshooting.

## Sintoma

Ao tentar conectar, a conexão caía imediatamente:

```
Connection closed by <IP> port 2220
```

Em alguns casos o servidor nem chegava a pedir a senha.

## Como diagnosticar

O modo verboso do SSH mostra **em que ponto** a conexão morre:

```bash
ssh -v usuario@host -p 2220
```

Quanto mais `-v`, mais detalhe (`-v`, `-vv`, `-vvv`).

**Leitura do resultado:**

| Onde a conexão para | Causa provável |
|---|---|
| Logo após `Local version string ...`, **antes** de pedir senha | O servidor recusou a conexão (rate limiting / bloqueio temporário) |
| Depois de digitar a senha, com `Permission denied` | Senha errada ou com caractere perdido na colagem |
| `Too many authentication failures` | Muitas tentativas de login seguidas |
| Antes de `Connection established` | Rede, firewall ou host/porta errados |

No caso registrado, a conexão parava **antes de pedir senha**, logo depois da linha `Local version string`. Isso aponta para **recusa do lado do servidor**, não senha errada.

## Causa

**Rate limiting por IP.** O servidor do OverTheWire limita quantas conexões um mesmo IP pode abrir num curto intervalo, para evitar abuso. O bloqueio foi disparado por um acúmulo de conexões em pouco tempo:

- reconexões seguidas depois de fechar abas;
- uma sessão `nc` deixada aberta;
- várias tentativas de `ssh` em sequência.

É um bloqueio **temporário**, não um banimento.

## Solução

1. **Parar de tentar.** Cada nova tentativa durante o bloqueio costuma reiniciar a contagem do tempo.
2. **Esperar de 2 a 5 minutos** sem abrir nada.
3. Reconectar normalmente:
   ```bash
   ssh usuario@host -p 2220
   ```

## Como evitar

- Não abrir várias conexões SSH em paralelo para o mesmo servidor.
- Encerrar sessões `nc`/`openssl` com `Ctrl+C` quando terminar, em vez de deixá-las penduradas.
- Em desafios que envolvem muitas tentativas (ex.: força bruta de PIN), mandar **todas as tentativas numa única conexão**, em vez de abrir uma conexão por tentativa. Abrir uma conexão por tentativa é o que dispara o rate limiting.

## Por que isso é relevante em segurança

**Rate limiting é um controle de segurança**, não um defeito. Ele é a primeira linha de defesa contra ataques de força bruta e de negação de serviço.

- **Red Team:** ao automatizar tentativas, é preciso respeitar o limite do alvo (reusar uma conexão, inserir atrasos), senão o ataque é bloqueado antes de terminar e ainda gera ruído nos logs.
- **Blue Team:** um pico de conexões recusadas por rate limit é exatamente o tipo de evento que deve gerar alerta. Pode indicar uma tentativa de brute force em andamento.

Controles relacionados em ambientes reais: `fail2ban`, limites no `sshd_config` (`MaxStartups`, `MaxAuthTries`) e regras de firewall por taxa de conexão.
