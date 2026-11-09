# SOC700 - Fase 7 (Domain compromise) - Playbook de hunting

Rodar manualmente no Kibana (Discover = KQL, ou ES|QL). Time range amplo (ex.: ultimo ano / absoluto). Respostas em texto puro (sem CTF{}); Flag 1 em minusculas. Trocar NOME.exe, HOST, ENTITY_ID, PID, IP_C2, USUARIO pelos valores achados.

## Step 0 - Indices, hosts e schema

Conta eventos por indice (descobre se e winlogbeat/Sysmon ou Elastic Defend).
```esql
FROM logs-*,winlogbeat-*,.ds-* METADATA _index | STATS count() BY _index
```

Lista hosts e tipo de SO (candidatos a Flag 1).
```esql
FROM logs-*,winlogbeat-*,.ds-* | STATS count() BY host.hostname, host.os.type
```

Mostra dataset/provider para saber o schema de cada fonte.
```esql
FROM logs-*,winlogbeat-*,.ds-* METADATA _index | STATS count() BY _index, event.module, event.dataset, event.provider
```

KQL rapido: so eventos Windows.
```kql
host.os.type : "windows" or winlog.channel : *
```

## Flags 1-5 - Binario malicioso (host, arquivo, diretorio, usuario, timestamp)

Sysmon EID 1 de binarios em pastas suspeitas (Flags 1-4).
```kql
winlog.event_id : 1 and winlog.event_data.Image : (*\\Users\\* or *\\Temp\\* or *\\Downloads\\* or *\\ProgramData\\* or *\\Public\\*) and not winlog.event_data.Image : *\\AppData\\Local\\Microsoft\\*
```

Mesmo em Elastic Defend.
```kql
event.category : "process" and event.type : "start" and process.executable : (*\\Users\\* or *\\Temp\\* or *\\Downloads\\* or *\\ProgramData\\* or *\\Public\\*)
```

Executaveis raros por host/usuario, Sysmon (poucos eventos = suspeito).
```esql
FROM winlogbeat-*,logs-* | WHERE winlog.event_id == "1" | STATS n = count(), first = MIN(@timestamp) BY host.hostname, winlog.event_data.Image, winlog.event_data.User | SORT n ASC | LIMIT 100
```

Mesmo em Elastic Defend.
```esql
FROM logs-endpoint.events.process-* | WHERE event.type == "start" | STATS n = count(), first = MIN(@timestamp) BY host.hostname, process.executable, user.name, user.domain | SORT n ASC | LIMIT 100
```

Pivo no binario achado: host (F1), Image (F2/F3), User (F4), UtcTime/@timestamp (F5), ProcessGuid/entity_id.
```kql
(winlog.event_id : 1 and winlog.event_data.Image : *\\NOME.exe) or (process.name : "NOME.exe" and event.type : "start")
```

Criacao/download do arquivo (confirma diretorio e origem), Sysmon 11 / Defend file.
```kql
(winlog.event_id : 11 and winlog.event_data.TargetFilename : *NOME.exe) or (event.category : "file" and file.name : "NOME.exe")
```

Flag 5: anotar @timestamp exato em UTC e o winlog.event_data.UtcTime cru (aba JSON do doc); formato exigido e desconhecido, so decidir apos ver o exemplo da plataforma.

## Flags 6-7 - C2 (IP e porta)

Conexoes do processo, Sysmon EID 3.
```kql
winlog.event_id : 3 and winlog.event_data.Image : *\\NOME.exe
```

Conexoes do processo, Elastic Defend (pivo por entity_id).
```kql
event.category : "network" and process.entity_id : "ENTITY_ID"
```

Destinos agregados, Sysmon (F6 = IP, F7 = porta).
```esql
FROM winlogbeat-*,logs-* | WHERE winlog.event_id == "3" AND winlog.event_data.Image LIKE "*NOME.exe" | STATS n = count() BY winlog.event_data.DestinationIp, winlog.event_data.DestinationPort
```

Destinos agregados, Elastic Defend.
```esql
FROM logs-endpoint.events.network-* | WHERE process.name == "NOME.exe" | STATS n = count() BY destination.ip, destination.port
```

Cruza o IP com tudo (IOCs da fase Linux podem repetir).
```kql
"IP_C2"
```

## Flags 8 e 11 - Ferramenta de credenciais e command line

Filhos do binario malicioso (Defend por parent.entity_id; Sysmon por ParentImage).
```kql
process.parent.entity_id : "ENTITY_ID" or winlog.event_data.ParentImage : *\\NOME.exe
```

Pivo por pid quando nao ha entity_id (host + parent pid).
```kql
host.hostname : "HOST" and (process.parent.pid : PID or winlog.event_data.ParentProcessId : PID) and (event.type : "start" or winlog.event_id : 1)
```

Keywords de mimikatz/Rubeus na command line (pega ferramenta renomeada).
```kql
process.command_line : (*sekurlsa* or *kerberos\:\:* or *lsadump* or *tgtdeleg* or *asktgt* or *kerberoast* or *dump* or *\/ptt* or *\/service*) or winlog.event_data.CommandLine : (*sekurlsa* or *kerberos\:\:* or *lsadump* or *tgtdeleg* or *asktgt* or *kerberoast* or *dump* or *\/ptt* or *\/service*)
```

Timeline do host com OriginalFileName/Description/Hashes (F8 mesmo se renomeada) e CommandLine completa (F11).
```esql
FROM winlogbeat-*,logs-* | WHERE host.hostname == "HOST" | KEEP @timestamp, winlog.event_data.Image, winlog.event_data.OriginalFileName, winlog.event_data.Description, winlog.event_data.Hashes, winlog.event_data.CommandLine, process.executable, process.pe.original_file_name, process.command_line | SORT @timestamp ASC
```

Acesso ao LSASS (Sysmon EID 10): SourceImage = ferramenta de dump.
```kql
winlog.event_id : 10 and winlog.event_data.TargetImage : *\\lsass.exe
```

## Flags 9-10 - Tickets

Arquivos .kirbi criados (F9 = quantidade/nomes; F10 = @timestamp).
```kql
(winlog.event_id : 11 and winlog.event_data.TargetFilename : *.kirbi) or (event.category : "file" and file.extension : "kirbi")
```

Lista ordenada dos tickets com hora.
```esql
FROM winlogbeat-*,logs-* | WHERE winlog.event_data.TargetFilename LIKE "*.kirbi" OR file.extension == "kirbi" | KEEP @timestamp, host.hostname, winlog.event_data.TargetFilename, file.path, winlog.event_data.Image, process.name | SORT @timestamp ASC
```

Sem .kirbi (ticket em memoria/base64): checar logons/tickets Kerberos do usuario.
```kql
event.code : (4768 or 4769 or 4624 or 4672) and winlog.event_data.TargetUserName : "USUARIO"
```

Nota: "Ticket Timestamp" pode ser a criacao do arquivo ou do comando; anotar ambos em UTC antes de escolher.
