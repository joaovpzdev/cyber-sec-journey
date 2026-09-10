# Guia de Estudo: Social-Engineer Toolkit (SET)

## Aviso Legal e Ética Aplicada ao Ethical Hacking

 **AVISO DE ISENÇÃO DE RESPONSABILIDADE E USO ÉTICO:**  
 O uso do **Social-Engineer Toolkit (SET)** ou de qualquer outra ferramenta de teste de penetração contra sistemas, redes ou indivíduos sem **autorização prévia, expressa e por escrito** é ilegal e constitui crime cibernético (conforme a Lei 12.737/2012 - Lei Carolina Dieckmann e o Art. 154-A do Código Penal Brasileiro, além de legislações internacionais equivalentes).

 **Pilares do Ethical Hacking (Hacking Ético):**

 - **Escopo e Consentimento:** Testes de simulação de engenharia social só devem ser realizados mediante contrato assinado (_Rules of Engagement_) definindo claramente limites, alvos e horários.
 - **Confidencialidade e Proteção de Dados:** Quaisquer dados capturados durante testes simulados (como credenciais de teste) devem ser imediatamente protegidos e destruídos após o relatório final, respeitando legislações de privacidade como a LGPD.
 - **Foco Construtivo e Educacional:** O objetivo central da engenharia social ética é educar os colaboradores e reforçar as defesas organizacionais, jamais expor, ridicularizar ou punir indivíduos.
 - **Ambiente de Testes Controlado:** O aprendizado técnico deve ser realizado estritamente em ambientes de laboratório locais e isolados (ex.: Máquinas Virtuais em rede interna fechada).

---

## 1. Visão Geral

O **Social-Engineer Toolkit (SET)**, conhecido pelo comando `setoolkit`, é uma framework de código aberto projetada para testar a vulnerabilidade humana por meio de simulações de engenharia social. Ele automatiza a criação de cenários de teste nos quais usuários são avaliados em relação à entrega inadvertida de senhas, execução de arquivos não autorizados ou concessão de acesso ao sistema.

---

## 2. Pré-requisitos e Instalação

O SET vem pré-instalado por padrão em distribuições voltadas para segurança, como o **Kali Linux**. Em outras distribuições Linux, a instalação pode ser realizada via repositório oficial do GitHub:

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/trustedsec/social-engineer-toolkit
   ```
2. **Navegar até a pasta e executar a instalação:**
   ```bash
   cd social-engineer-toolkit
   python setup.py install
   ```
3. **Iniciar a ferramenta com privilégios de administrador:**
   ```bash
   sudo setoolkit
   ```

---

## 3. Estrutura de Navegação (Menu Principal)

Ao iniciar, o SET exibe um menu numérico interativo com navegação hierárquica (Seleção de Categoria $\rightarrow$ Método de Ataque $\rightarrow$ Configuração de Parâmetros).

**Árvore Principal de Opções:**

1. **Social-Engineering Attacks:** Núcleo principal contendo módulos de phishing, clonagem de páginas e geração de payloads.
2. **Penetration Testing:** Ferramentas de apoio para testes de intrusão mais amplos.
3. **Third Party Modules:** Módulos e integrações desenvolvidos por terceiros.
4. **Update Options:** Atualização das assinaturas e do código do framework.

---

## 4. Passo a Passo: Simulação de Clonagem de Site (Website Attack)

Um dos módulos mais utilizados no SET é o _Credential Harvester_, empregado em auditorias para testar a suscetibilidade dos usuários a páginas de login clonadas.

### Sequência de Navegação no Menu:

- **Passo 1:** Selecione `1` $\rightarrow$ _Social-Engineering Attacks_
- **Passo 2:** Selecione `2` $\rightarrow$ _Website Attack Vectors_
- **Passo 3:** Selecione `3` $\rightarrow$ _Credential Harvester Attack Method_
- **Passo 4:** Selecione `2` $\rightarrow$ _Site Cloner_
- **Passo 5 (Configuração de IP):** Defina o endereço IP local (ex: `192.168.1.10`) para onde o tráfego e as requisições do servidor local serão direcionados.
- **Passo 6 (URL Alvo):** Digite o endereço da página que será clonada para teste (ex: `https://accounts.google.com`).

### Mecanismo de Funcionamento:

O SET levanta um serviço HTTP local que renderiza uma cópia da página solicitada. Em um teste simulado, quando o usuário submete os dados no formulário, a requisição é interceptada pelo servidor local e registrada em tempo real no terminal do auditor de segurança.

---

## 5. Outros Métodos Relevantes

### 5.1 Spear-Phishing (Ataques Direcionados)

No menu _Social-Engineering Attacks_ (opção `1`), o módulo de _Spear-Phishing_ permite a criação e envio de e-mails personalizados para alvos específicos. O auditor pode configurar um servidor SMTP autorizado para testar a eficácia dos filtros de e-mail e a capacidade de identificação de mensagens falsas por parte dos funcionários.

### 5.2 Payload Generation (Criação de Arquivos para Testes)

Integrado ao Metasploit Framework, o SET permite gerar arquivos (como documentos do Microsoft Office ou PDFs) que contêm vetores de teste. Quando executados em um ambiente de teste, esses arquivos estabelecem uma conexão remota (_Reverse Shell_) de volta para o ambiente de auditoria.

---

## 6. Limitações Concretas e Barreiras Modernas de Defesa

Embora seja uma ferramenta tradicional de testes, o SET enfrenta diversas limitações contra arquiteturas modernas de segurança:

- **HTTPS/SSL & Certificados:** A clonagem de sites não copia certificados SSL válidos. Navegadores modernos exibem alertas destacados de _"Sua conexão não é privada"_, alertando usuários conscientes.
- **Soluções Antivírus (AV) e EDR:** Payloads gerados nativamente pelo SET são amplamente conhecidos pelas assinaturas de mercado e bloqueados quase instantaneamente por mecanismos EDR/AV modernos sem técnicas avançadas de ofuscação.
- **Filtros e Gateways de E-mail (SEG):** Provedores corporativos e serviços como Google Workspace e Microsoft 365 utilizam checagens rigorosas de SPF, DKIM e DMARC, enviando e-mails não autenticados direto para o Spam ou descartando-os na entrada.
- **Resolução de Nomes e Roteamento DNS:** Para testes fora de redes locais isoladas, é necessária infraestrutura dedicada de apontamento DNS ou mecanismos de tunelamento seguro (como Ngrok) em cenários devidamente autorizados.

---

## 7. Tabela de Resumo de Comandos

| Objetivo de Teste                  | Caminho no Menu | Resultado Prático no Laboratório              |
| :--------------------------------- | :-------------- | :-------------------------------------------- |
| **Captura de Credenciais**         | `1 → 2 → 3 → 2` | Clone de site com escuta ativa de formulário  |
| **Simulação de Phishing**          | `1 → 1`         | Envio de e-mail de teste com anexo/link       |
| **Criação de Arquivo de Teste**    | `1 → 4`         | Documento com payload de conexão reversa      |
| **Teste de Mídia Removível (USB)** | `1 → 2 → 1`     | Configuração de autostart/payload em pendrive |
