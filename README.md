# Radar Logístico

Dashboard didático em Streamlit para monitoramento de atrasos em entregas.

## Como executar

```powershell
cd outputs\dashboard_logistico
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

O app abre em `http://localhost:8501`.

No Windows, também é possível iniciar com dois cliques em `iniciar_dashboard.bat`.

## Recursos

- KPIs de atraso, prazo e criticidade;
- filtros por transportadora, região, status e prioridade;
- ranking de entregas problemáticas;
- comparação entre transportadoras;
- análise regional;
- tendência pela sequência operacional;
- upload opcional de arquivo CSV no mesmo formato da base;
- exportação dos dados filtrados.

## Colunas esperadas no CSV

`id_entrega`, `transportadora`, `regiao`, `prazo_dias`, `dias_reais`.
