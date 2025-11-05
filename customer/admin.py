from django.contrib import admin
from .models import KOMForm, KOMLineItem, KOMEquipmentRequired


class KOMLineItemInline(admin.TabularInline):
    model = KOMLineItem
    extra = 0


class KOMEquipmentRequiredInline(admin.TabularInline):
    model = KOMEquipmentRequired
    extra = 0


@admin.register(KOMForm)
class KOMFormAdmin(admin.ModelAdmin):
    list_display = ['proposal_number', 'proposal_date', 'project_name', 'sales_rep', 'bill_to_company', 'created_at']
    list_filter = ['proposal_date', 'created_at', 'industry']
    search_fields = ['proposal_number', 'project_name', 'bill_to_company', 'sales_rep']
    date_hierarchy = 'proposal_date'
    inlines = [KOMLineItemInline, KOMEquipmentRequiredInline]
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'source_file']


@admin.register(KOMLineItem)
class KOMLineItemAdmin(admin.ModelAdmin):
    list_display = ['kom_form', 'item_number', 'description', 'value_1', 'value_2', 'value_3']
    list_filter = ['kom_form']
    search_fields = ['item_number', 'description']


@admin.register(KOMEquipmentRequired)
class KOMEquipmentRequiredAdmin(admin.ModelAdmin):
    list_display = ['kom_form', 'equipment_type', 'qty', 'kn_number', 'description']
    list_filter = ['equipment_type', 'kom_form']
    search_fields = ['equipment_type', 'kn_number', 'description']
