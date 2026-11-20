{#
  Par défaut, dbt nomme les schémas "<schéma cible>_<schéma du modèle>" (ex. main_staging).
  On utilise directement le nom de la couche : staging, intermediate, marts.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
