# Diagram sources

Mermaid sources for the pre-rendered SVGs in `assets/diagrams/`. To re-render:

    npx -y @mermaid-js/mermaid-cli -i loop.mmd -o ../assets/diagrams/loop.svg -c mermaid-config.json -b white
    npx -y @mermaid-js/mermaid-cli -i board.mmd -o ../assets/diagrams/board.svg -c mermaid-config.json -b white
