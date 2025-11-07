from django.contrib import admin
from .models import Assembly, Component, Rule, RuleVersion, Inconsistency, Configurator


@admin.register(Assembly)
class AssemblyAdmin(admin.ModelAdmin):
    list_display = ['name', 'inventor_file_path', 'created_by', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'description', 'inventor_file_path']


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ['name', 'assembly', 'component_type', 'inventor_instance_name']
    list_filter = ['assembly', 'component_type', 'created_at']
    search_fields = ['name', 'inventor_instance_name', 'description']


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ['rule_name', 'component', 'rule_type', 'created_by', 'created_at']
    list_filter = ['rule_type', 'created_at', 'created_by']
    search_fields = ['rule_name', 'rule_code', 'component__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RuleVersion)
class RuleVersionAdmin(admin.ModelAdmin):
    list_display = ['rule', 'version_number', 'created_by', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['rule__rule_name', 'change_notes']


@admin.register(Inconsistency)
class InconsistencyAdmin(admin.ModelAdmin):
    list_display = ['inconsistency_type', 'severity', 'status', 'rule', 'found_at']
    list_filter = ['severity', 'status', 'inconsistency_type', 'found_at']
    search_fields = ['description', 'suggested_fix', 'code_location']
    readonly_fields = ['found_at']


@admin.register(Configurator)
class ConfiguratorAdmin(admin.ModelAdmin):
    list_display = ['name', 'assembly', 'created_by', 'created_at']
    list_filter = ['assembly', 'created_at', 'created_by']
    search_fields = ['name', 'description']
