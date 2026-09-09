# Google Hacking (Google Dorking)

## O que é

Google Hacking, também chamado de Google Dorking, é a técnica de usar operadores de busca avançados do Google para encontrar informações que não estão facilmente visíveis através de uma pesquisa comum. Não é uma falha do Google em si, mas sim o uso do motor de busca como ferramenta de reconhecimento (recon), explorando o fato de que o Google indexa páginas, arquivos e configurações que, muitas vezes, deveriam ter sido protegidas pelo administrador do sistema.

É amplamente usada na fase de **reconhecimento passivo** de um teste de intrusão, já que permite coletar informações sobre um alvo sem interagir diretamente com a infraestrutura dele — toda a consulta é feita contra o índice do Google.

## Como funciona

O Google indexa praticamente tudo que encontra publicamente na web, incluindo páginas de login, painéis administrativos, arquivos de configuração, backups e documentos que foram publicados sem controle de acesso adequado. Usando operadores específicos, é possível filtrar esse índice por tipo de arquivo, domínio, texto no título, texto na URL, entre outros critérios — reduzindo drasticamente o tempo necessário para localizar esse tipo de exposição.

## Operadores principais

| Operador | Função | Exemplo |
|---|---|---|
| `site:` | Restringe a busca a um domínio específico | `site:exemplo.com` |
| `filetype:` | Busca por tipo de arquivo | `filetype:pdf` |
| `intitle:` | Busca por termo no título da página | `intitle:"index of"` |
| `inurl:` | Busca por termo na URL | `inurl:admin` |
| `intext:` | Busca por termo no corpo da página | `intext:"senha"` |
| `ext:` | Sinônimo de `filetype:` | `ext:sql` |
| `cache:` | Exibe a versão em cache de uma página | `cache:exemplo.com` |
| `-` (negação) | Exclui termos dos resultados | `site:exemplo.com -inurl:blog` |
| `"..."` | Busca por frase exata | `"confidencial"` |
| `OR` / `\|` | Combina múltiplos termos | `filetype:pdf OR filetype:doc` |

Os operadores podem ser combinados para refinar a busca, formando o que se chama de "dork". Exemplo combinando múltiplos operadores:

```
site:exemplo.com filetype:pdf intext:"confidencial"
```

Esse dork busca, dentro do domínio `exemplo.com`, apenas arquivos PDF que contenham a palavra "confidencial" no conteúdo — um exemplo didático do tipo de refinamento possível.

## Categorias comuns de exposição encontradas

- **Diretórios abertos**: `intitle:"index of"` combinado com nomes de pastas sensíveis (ex: `/backup`, `/config`)
- **Painéis de administração expostos**: `inurl:admin` combinado com `intitle:login`
- **Arquivos de configuração e credenciais**: buscas por extensões como `.env`, `.log`, `.sql`, `.bak`, que às vezes acabam publicados por engano
- **Documentos internos**: PDFs, planilhas ou apresentações indexados publicamente que não deveriam estar acessíveis
- **Mensagens de erro reveladoras**: erros de aplicação ou banco de dados que expõem informações sobre a stack tecnológica
- **Dispositivos e câmeras conectados à internet**: interfaces de administração de equipamentos IoT mal configurados

## Google Hacking Database (GHDB)

A **Google Hacking Database**, mantida pela Exploit-DB (Offensive Security), é um catálogo público de dorks organizados por categoria (arquivos sensíveis, páginas de login vulneráveis, mensagens de erro, dispositivos expostos, entre outras). É a referência mais usada para consulta de dorks já catalogados pela comunidade.

## Impacto

- Exposição não intencional de credenciais, chaves de API e tokens
- Vazamento de documentos internos e dados pessoais
- Descoberta de painéis administrativos sem autenticação adequada
- Mapeamento da superfície de ataque de uma organização sem necessidade de contato direto com seus sistemas

## Como se proteger

**Controle de indexação**
Usar `robots.txt` e a meta tag `noindex` para impedir que mecanismos de busca indexem diretórios e páginas sensíveis. Importante notar que `robots.txt` é uma orientação, não uma barreira de segurança — não substitui controle de acesso real.

**Controle de acesso adequado**
Garantir autenticação em painéis administrativos e diretórios sensíveis, em vez de depender apenas de URLs "escondidas" (segurança por obscuridade não é suficiente).

**Auditoria periódica com dorks**
Rodar consultas do próprio domínio periodicamente (`site:seudominio.com filetype:sql`, por exemplo) para identificar exposições antes que sejam encontradas por terceiros.

**Remoção do cache do Google**
Utilizar a ferramenta *Removals* do Google Search Console para solicitar a remoção de conteúdo sensível já indexado.

**Gestão correta de arquivos publicados**
Nunca versionar ou publicar arquivos de configuração, backups ou logs em diretórios acessíveis publicamente pelo servidor web.

## Ferramentas relacionadas

- **Google Hacking Database (GHDB)**: catálogo de dorks mantido pela Exploit-DB
- **Google Search Console**: usado do lado defensivo, para monitorar indexação do próprio domínio
- **theHarvester**: ferramenta de reconhecimento que também utiliza motores de busca para coletar informações públicas sobre um alvo

## Considerações éticas e legais

Google Dorking em si não é ilegal — é apenas o uso de operadores de busca públicos. O problema legal surge no que é feito com a informação encontrada: acessar sistemas sem autorização, mesmo que a URL tenha sido localizada via Google, pode configurar acesso indevido dependendo da legislação local. Em testes de segurança, essa técnica só deve ser aplicada contra domínios próprios ou com autorização explícita (escopo definido em um teste de pentest).

## Para praticar

- **Google Hacking Database (GHDB)**: consultar dorks já catalogados para entender padrões
- **TryHackMe**: possui salas específicas sobre OSINT e Google Dorking
- Praticar contra o próprio domínio ou ambientes de laboratório próprios, nunca contra terceiros sem autorização

## Referências

- Exploit-DB — Google Hacking Database (GHDB)
- OWASP — Testing for Search Engine Discovery